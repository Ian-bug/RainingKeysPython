import sys
import time
from collections import deque
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QBrush, QColor, QScreen, QFont
from .config import Config

# Windows API for click-through
try:
    import win32gui
    import win32con
    import win32api
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    print("Warning: pywin32 not found. Click-through might not work.")

class Bar:
    """Represents a falling visual bar."""
    __slots__ = ['lane_index', 'press_time', 'release_time', 'active']
    
    def __init__(self):
        self.lane_index = 0
        self.press_time = 0.0
        self.release_time = None # None means currently held
        self.active = False

class BarPool:
    """
    Manages a pool of Bar objects. Uses a soft limit approach.
    """
    def __init__(self, max_size):
        self.max_size = max_size
        self.active_bars = deque()
        self.inactive_bars = deque()
        
        # Pre-allocate some bars
        initial_alloc = min(max_size, 50)
        for _ in range(initial_alloc):
            self.inactive_bars.append(Bar())

    def spawn(self, lane_index, timestamp):
        """
        Activates a bar. If pool is empty/full, handles gracefully.
        """
        if self.inactive_bars:
            bar = self.inactive_bars.pop()
        else:
            # Pool exhausted.
            # Strategy: If below max_size, create new.
            # If at max_size, recycle the oldest active bar (soft limit).
            total_count = len(self.active_bars) + len(self.inactive_bars) # logic check
            # Actually total known count is just what we have tracked.
            # Let's track total instantiated count if strictly needed, 
            # but deque length is good enough.
            
            # Simple count check:
            if (len(self.active_bars) + len(self.inactive_bars)) < self.max_size:
                bar = Bar()
            elif self.active_bars:
                # Soft Limit hit: Recycle oldest
                bar = self.active_bars.popleft() # Oldest is usually at the left/start
                # Technically we are taking it out of active to re-add it as new active
            else:
                # Should effectively never happen unless max_size=0
                bar = Bar() 
        
        bar.active = True
        bar.lane_index = lane_index
        bar.press_time = timestamp
        bar.release_time = None
        self.active_bars.append(bar)
        return bar

    def recycle(self, bar):
        """Returns a bar to the inactive pool."""
        bar.active = False
        self.inactive_bars.append(bar)

class RainingKeysOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.pool = BarPool(Config.MAX_BARS)
        self.active_holds = {} # {lane_index: Bar} tracking currently held notes
        
        # High-res timer for rendering
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_canvas)
        self.timer.start(16) # ~60 FPS target trigger, but delta used for physics

        # Debug stats
        self.last_fps_time = time.perf_counter()
        self.frame_count = 0
        self.current_fps = 0.0

    def init_ui(self):
        # Window Flags
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool | # Tool prevents showing in alt-tab usually
            Qt.WindowTransparentForInput # Qt 5.10+ helper, acts as partial clickthrough
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Full screen
        screen_geo = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_geo)

        # Win32 Click-through + Always on Top enforcement
        if HAS_WIN32:
            hwnd = int(self.winId())
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)

    def handle_input(self, lane_index, timestamp):
        """Slot called when input monitor detects a key press."""
        if lane_index in self.active_holds:
            # Key already held? (Should be filtered by input_mon, but safety check)
            pass
        else:
            bar = self.pool.spawn(lane_index, timestamp)
            self.active_holds[lane_index] = bar

    def handle_release(self, lane_index, timestamp):
        """Slot called when input monitor detects a key release."""
        if lane_index in self.active_holds:
            bar = self.active_holds.pop(lane_index)
            bar.release_time = timestamp

    def update_canvas(self):
        self.update() # Triggers paintEvent

    def paintEvent(self, event):
        painter = QPainter()
        try:
            if not painter.begin(self):
                # Failed to start painting (device occupied?)
                return
            
            painter.setRenderHint(QPainter.Antialiasing)

            current_time = time.perf_counter()
            
            # Calculate Logic
            screen_h = self.height()
            to_recycle = []
            
            # Bar Drawing Loop
            for bar in self.pool.active_bars:
                # Calculate Y positions
                # Bottom of the note (Leading Edge)
                delta_press = current_time - bar.press_time + Config.INPUT_LATENCY_OFFSET
                y_bottom = delta_press * Config.SCROLL_SPEED
                
                # Top of the note (Trailing Edge)
                if bar.release_time is None:
                    # Still held: Top is at current time (0 offset from 'now')
                    delta_release = Config.INPUT_LATENCY_OFFSET # effectively 0 time passed since 'now'
                    y_top = delta_release * Config.SCROLL_SPEED
                else:
                    delta_release = current_time - bar.release_time + Config.INPUT_LATENCY_OFFSET
                    y_top = delta_release * Config.SCROLL_SPEED

                # Check bounds (Recycle if Top is off-screen)
                if y_top > screen_h:
                    to_recycle.append(bar)
                    continue
                
                # Render only if VISIBLE
                if y_bottom < 0:
                     continue

                # Fade Logic (based on leading edge / y_bottom)
                alpha = 1.0
                if y_bottom > Config.FADE_START_Y:
                    dist_into_fade = y_bottom - Config.FADE_START_Y
                    factor = 1.0 - (dist_into_fade / Config.FADE_RANGE)
                    alpha = max(0.0, min(1.0, factor))
                
                # Draw
                x = Config.LANE_START_X + (bar.lane_index * Config.LANE_WIDTH)
                
                # Height
                h = max(Config.BAR_HEIGHT, y_bottom - y_top)
                
                draw_y = y_bottom - h
                
                # Apply Color
                c = QColor(Config.COLOR_BAR)
                c.setAlphaF(alpha * (Config.COLOR_BAR.alphaF())) 
                
                painter.setBrush(QBrush(c))
                painter.setPen(Qt.NoPen)
                painter.drawRect(QRectF(x, draw_y, Config.BAR_WIDTH, h))

            # Recycle off-screen bars
            for bar in to_recycle:
                try:
                    self.pool.active_bars.remove(bar)
                    self.pool.recycle(bar)
                except ValueError:
                    pass
                
            # Draw Debug
            if Config.DEBUG_MODE:
                self.draw_debug(painter, current_time)
                
        except Exception as e:
            print(f"Paint Error: {e}")
        finally:
            if painter.isActive():
                painter.end()

    def draw_debug(self, painter, current_time):
        self.frame_count += 1
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time

        painter.setPen(Config.COLOR_DEBUG_TEXT)
        painter.setFont(QFont("Consolas", 10))
        
        active_count = len(self.pool.active_bars)
        pool_size = len(self.pool.inactive_bars) + active_count
        
        info = [
            f"FPS: {self.current_fps:.1f}",
            f"Active Bars: {active_count} / {Config.MAX_BARS}",
            f"Pool Size: {pool_size}",
            f"Speed: {Config.SCROLL_SPEED} px/s"
        ]
        
        for i, line in enumerate(info):
            painter.drawText(10, 20 + (i * 15), line)
