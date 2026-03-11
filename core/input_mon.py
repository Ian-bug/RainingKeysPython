import time
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
        callbacks from that thread. The active_keys set is modified from these callbacks.

        While this is not thread-safe in the general Python sense, pynput guarantees that
        callbacks are invoked serially (not concurrently) from a single background thread.
        This means there's no actual race condition between the check-and-add operations.

        However, if other code were to access active_keys concurrently, issues could arise.
        For this application, the design is safe because:
        1. Only the pynput callback thread modifies active_keys
        2. All modifications happen through serial callback invocations
        3. No other thread reads or writes to active_keys
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

    def start_monitoring(self) -> None:
        """Start the keyboard listener in a separate thread."""
        self.running = True
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
            logger.debug("Input monitoring stopped.")

    def _get_key_str(self, key) -> str:
        """Convert pynput Key object to string representation."""
        try:
            return f"'{key.char}'"
        except AttributeError:
            return str(key)

    def on_press(self, key) -> None:
        """Handle key press events from pynput listener."""
        if not self.running:
            return

        k_str = self._get_key_str(key)

        # Filter autorepeat: If key is already in active_keys, ignore it
        if k_str in self.active_keys:
            return

        self.raw_key_pressed.emit(k_str)

        if k_str in self.config.lane_map:
            self.active_keys.add(k_str)
            timestamp = time.perf_counter()
            lane_idx = self.config.lane_map[k_str]
            self.key_pressed.emit(lane_idx, timestamp)

    def on_release(self, key) -> None:
        """Handle key release events from pynput listener."""
        if not self.running:
            return

        k_str = self._get_key_str(key)

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
