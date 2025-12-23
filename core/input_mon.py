import time
from PySide6.QtCore import QObject, Signal, QThread
from pynput import keyboard
from .config import Config

class InputWorker(QObject):
    """
    Worker that runs the pynput listener in a separate thread.
    Emits (lane_index, timestamp) when a tracked key is pressed or released.
    """
    key_pressed = Signal(int, float)  # lane_index, timestamp
    key_released = Signal(int, float) # lane_index, timestamp
    raw_key_pressed = Signal(str)     # raw_key_string

    def __init__(self):
        super().__init__()
        self.listener = None
        self.running = False
        self.active_keys = set() # Track pressed keys to filter autorepeats

    def start_monitoring(self):
        self.running = True
        self.active_keys.clear()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        print("Input monitoring started.")

    def stop_monitoring(self):
        self.running = False
        if self.listener:
            self.listener.stop()
            self.listener = None
            print("Input monitoring stopped.")

    def _get_key_str(self, key):
        try:
            return f"'{key.char}'"
        except AttributeError:
            return str(key)

    def on_press(self, key):
        if not self.running:
            return
        
        k_str = self._get_key_str(key)
        
        # Filter autorepeat: If key is already in active_keys, ignore it
        if k_str in self.active_keys:
            return

        self.raw_key_pressed.emit(k_str)

        if k_str in Config.LANE_MAP:
            self.active_keys.add(k_str)
            timestamp = time.perf_counter()
            lane_idx = Config.LANE_MAP[k_str]
            self.key_pressed.emit(lane_idx, timestamp)

    def on_release(self, key):
        if not self.running:
            return

        k_str = self._get_key_str(key)
        
        if k_str in self.active_keys:
            self.active_keys.remove(k_str)

        if k_str in Config.LANE_MAP:
            timestamp = time.perf_counter()
            lane_idx = Config.LANE_MAP[k_str]
            self.key_released.emit(lane_idx, timestamp)

class InputMonitor(QThread):
    """
    Thread wrapper for the worker.
    """
    key_pressed = Signal(int, float)
    key_released = Signal(int, float)
    raw_key_pressed = Signal(str)

    def __init__(self):
        super().__init__()
        self.worker = InputWorker()
        self.worker.key_pressed.connect(self.key_pressed.emit)
        self.worker.key_released.connect(self.key_released.emit)
        self.worker.raw_key_pressed.connect(self.raw_key_pressed.emit)

    def run(self):
        self.worker.start_monitoring()
        self.exec()
        self.worker.stop_monitoring()
