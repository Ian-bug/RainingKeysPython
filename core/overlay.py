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
            if (len(self.active_bars) + len(self.inactive_bars)) < self.max_size:
                bar = Bar()
            elif self.active_bars:
                bar = self.active_bars.popleft()
            else:
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
    def __init__(self, settings_manager):
        super().__init__()
        self.settings = settings_manager
        # Connect to settings changed signal
        self.settings.settings_changed.connect(self.on_settings_changed)
        
        self.pool = BarPool(Config.MAX_BARS)
        self.active_holds = {} # {lane_index: Bar} tracking currently held notes
        
        self.init_ui()
        
        # High-res timer for rendering
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_canvas)
        self.timer.start(16) # ~60 FPS target trigger

        # Debug stats
        self.last_fps_time = time.perf_counter()
        self.frame_count = 0
        self.current_fps = 0.0

    def init_ui(self):
        # Window Flags
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool | 
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Initial calculation for window size
        # We need enough width for all lanes
        max_lane = 0
        if Config.LANE_MAP:
             max_lane = max(Config.LANE_MAP.values())
        
        # Width: Start Offset + (Max Lane Index + 1) * Lane Width + Extra Padding
        width = Config.LANE_START_X + ((max_lane + 1) * Config.LANE_WIDTH) + 50
        height = QApplication.primaryScreen().size().height()
        
        self.resize(width, height)
        # Move to configured position
        self.move(self.settings.overlay_x, self.settings.overlay_y)

        # Win32 Click-through
        if HAS_WIN32:
            hwnd = int(self.winId())
            try:
                styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
            except Exception as e:
                print(f"Win32 Error: {e}")

    def on_settings_changed(self):
        # Move window live when settings change
        self.move(self.settings.overlay_x, self.settings.overlay_y)

    def handle_input(self, lane_index, timestamp):
        """Slot called when input monitor detects a key press."""
        if lane_index in self.active_holds:
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
                return
            
            painter.setRenderHint(QPainter.Antialiasing)

            current_time = time.perf_counter()
            screen_h = self.height()
            to_recycle = []
            
            # Get current settings
            speed = self.settings.scroll_speed
            falling_down = (self.settings.fall_direction == 'down')

            # Bar Drawing Loop
            for bar in self.pool.active_bars:
                # 1. Physics: Distance from Origin (Press Time)
                delta_press = current_time - bar.press_time + Config.INPUT_LATENCY_OFFSET
                dist_head = delta_press * speed
                
                if bar.release_time is None:
                    # Held
                    dist_tail = Config.INPUT_LATENCY_OFFSET * speed
                else:
                    # Released
                    delta_release = current_time - bar.release_time + Config.INPUT_LATENCY_OFFSET
                    dist_tail = delta_release * speed

                # 2. Geometry
                height_bar = dist_head - dist_tail
                # Clamp min height so short taps are visible
                if height_bar < Config.BAR_HEIGHT:
                     height_bar = Config.BAR_HEIGHT
                     dist_tail = dist_head - height_bar
                
                # Calculate Screen Y
                if falling_down:
                    # Spawn at 0 (Top)
                    # Tail is "above" Head (smaller Y value)
                    rect_y = dist_tail
                else:
                    # Spawn at ScreenHeight (Bottom)
                    # Head moves UP (smaller Y value)
                    # Tail moves UP (larger Y value than Head)
                    # Y = H - dist. 
                    # Head Y = H - dist_head.
                    # Tail Y = H - dist_tail.
                    # Rect Top = Head Y (Smallest Y)
                    rect_y = screen_h - dist_head
                
                # 3. Recycle Check
                if falling_down:
                    if rect_y > screen_h:
                        to_recycle.append(bar)
                        continue
                else:
                    # Moving Up. If the bottom of that rect (rect_y + height) is < 0, it is gone.
                    if (rect_y + height_bar) < 0:
                        to_recycle.append(bar)
                        continue
                
                # 4. Fade Logic (Distance Traveled based)
                # Use dist_head (leading edge travel distance)
                alpha = 1.0
                if dist_head > Config.FADE_START_Y:
                    dist_into_fade = dist_head - Config.FADE_START_Y
                    factor = 1.0 - (dist_into_fade / Config.FADE_RANGE)
                    alpha = max(0.0, min(1.0, factor))

                # 5. Draw
                # Optimization: Don't draw if transparent
                if alpha <= 0.0:
                    continue
                    
                x = Config.LANE_START_X + (bar.lane_index * Config.LANE_WIDTH)
                
                c = QColor(Config.COLOR_BAR)
                c.setAlphaF(alpha * (Config.COLOR_BAR.alphaF())) 
                
                painter.setBrush(QBrush(c))
                painter.setPen(Qt.NoPen)
                painter.drawRect(QRectF(x, rect_y, Config.BAR_WIDTH, height_bar))

            # Recycle
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
            f"Active: {active_count}",
            f"Pool: {pool_size}",
            f"Speed: {self.settings.scroll_speed}",
            f"Dir: {self.settings.fall_direction}",
            f"Pos: {self.x()},{self.y()}"
        ]
        
        for i, line in enumerate(info):
            painter.drawText(10, 20 + (i * 15), line)
