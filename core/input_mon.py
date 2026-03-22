import time
from threading import Lock
from PySide6.QtCore import QObject, Signal, QThread
from pynput import keyboard
from .configuration import AppConfig
from .logging_config import get_logger

logger = get_logger(__name__)

class InputWorker(QObject):
    """
    Worker that runs the pynput listener in a separate thread.
    Emits (lane_index, timestamp) when a tracked key is pressed or released.

    Thread Safety:
        The pynput keyboard listener runs in its own thread and calls on_press/on_release
        callbacks from that thread. The active_keys set is protected by a Lock to ensure
        thread-safe access, preventing race conditions if other code were to access it.
    """
    key_pressed = Signal(int, float)  # lane_index, timestamp
    key_released = Signal(int, float) # lane_index, timestamp
    raw_key_pressed = Signal(str)     # raw_key_string

    def __init__(self, app_config: AppConfig) -> None:
        super().__init__()
        self.config = app_config
        self.listener = None
        self.running = False
        self.active_keys: set[str] = set()  # Track pressed keys to filter autorepeats
        self._active_keys_lock = Lock()  # Protect active_keys for thread safety

    def start_monitoring(self) -> None:
        """Start the keyboard listener in a separate thread."""
        self.running = True
        with self._active_keys_lock:
            self.active_keys.clear()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        logger.debug("Input monitoring started.")

    def stop_monitoring(self) -> None:
        """Stop the keyboard listener."""
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
            with self._active_keys_lock:
                self.active_keys.clear()
            logger.debug("Input monitoring stopped.")

    def _get_key_str(self, key) -> str:
        """Convert pynput Key object to normalized string representation.

        Normalizes key strings to a consistent format:
        - Character keys: 'a', '1', etc.
        - Special keys: 'space', 'enter', 'shift', etc.
        - Function keys: 'f1', 'f2', etc.

        Args:
            key: pynput Key object.

        Returns:
            Normalized string representation of the key.
        """
        try:
            # Regular character key
            return f"'{key.char}'"
        except AttributeError:
            # Special key
            key_str = str(key)
            # Remove 'Key.' prefix for cleaner display
            if key_str.startswith('Key.'):
                return key_str.replace('Key.', '').lower()
            return key_str.lower()

    def on_press(self, key) -> None:
        """Handle key press events from pynput listener."""
        if not self.running:
            return

        k_str = self._get_key_str(key)

        # Filter autorepeat: If key is already in active_keys, ignore it
        with self._active_keys_lock:
            if k_str in self.active_keys:
                return

        self.raw_key_pressed.emit(k_str)

        if k_str in self.config.lane_map:
            with self._active_keys_lock:
                self.active_keys.add(k_str)
            timestamp = time.perf_counter()
            lane_idx = self.config.lane_map[k_str]
            self.key_pressed.emit(lane_idx, timestamp)

    def on_release(self, key) -> None:
        """Handle key release events from pynput listener."""
        if not self.running:
            return

        k_str = self._get_key_str(key)

        with self._active_keys_lock:
            if k_str in self.active_keys:
                self.active_keys.remove(k_str)

        if k_str in self.config.lane_map:
            timestamp = time.perf_counter()
            lane_idx = self.config.lane_map[k_str]
            self.key_released.emit(lane_idx, timestamp)

class InputMonitor(QThread):
    """
    Thread wrapper for the worker.
    """
    key_pressed = Signal(int, float)
    key_released = Signal(int, float)
    raw_key_pressed = Signal(str)

    def __init__(self, app_config: AppConfig) -> None:
        super().__init__()
        self.worker = InputWorker(app_config)
        self.worker.key_pressed.connect(self.key_pressed.emit)
        self.worker.key_released.connect(self.key_released.emit)
        self.worker.raw_key_pressed.connect(self.raw_key_pressed.emit)

    def run(self) -> None:
        """Run the input monitoring thread."""
        self.worker.start_monitoring()
        self.exec()
        self.worker.stop_monitoring()

    def stop(self) -> None:
        """Stop the input monitoring thread cleanly."""
        self.worker.stop_monitoring()
        self.quit()
        if not self.wait(1000):  # Wait up to 1 second for thread to finish
            logger.warning("InputMonitor thread did not stop gracefully, terminating...")
            self.terminate()
            self.wait()
