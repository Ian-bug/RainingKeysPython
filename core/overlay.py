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

        # KeyViewer State
        self.key_counts = {} # {lane_index: count}
        # Initialize counts for mapped lanes
        if Config.LANE_MAP:
             for idx in Config.LANE_MAP.values():
                 self.key_counts[idx] = 0
        
        # Track active keys for visual feedback
        self.active_keys_visual = set() # {lane_index}

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

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
        self.update_layout()

        # Win32 Click-through

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
        self.update_layout() # Recalculate size if lanes changed

    def update_layout(self):
        """Recalculates window size based on current lanes."""
        max_lane = 0
        if Config.LANE_MAP:
             max_lane = max(Config.LANE_MAP.values())
        else:
             max_lane = 0 # Fallback
        
        # Width: Start Offset + (Max Lane Index + 1) * Lane Width + Extra Padding
        width = Config.LANE_START_X + ((max_lane + 1) * Config.LANE_WIDTH) + 50
        height = QApplication.primaryScreen().size().height()
        
        self.resize(width, height)

    def handle_input(self, lane_index, timestamp):
        """Slot called when input monitor detects a key press."""
        if lane_index in self.active_holds:
            pass
        else:
            bar = self.pool.spawn(lane_index, timestamp)
            self.active_holds[lane_index] = bar
            
            # KeyViewer Logic
            self.active_keys_visual.add(lane_index)
            if lane_index not in self.key_counts:
                self.key_counts[lane_index] = 0
            self.key_counts[lane_index] += 1

    def handle_release(self, lane_index, timestamp):
        """Slot called when input monitor detects a key release."""
        if lane_index in self.active_holds:
            bar = self.active_holds.pop(lane_index)
            bar.release_time = timestamp
        
        # KeyViewer Logic
        if lane_index in self.active_keys_visual:
            self.active_keys_visual.remove(lane_index)

    def update_canvas(self):
        self.update() # Triggers paintEvent

    def get_kv_geometry(self, screen_h):
        """Calculates KeyViewer position and dimensions."""
        key_width = Config.LANE_WIDTH 
        key_height = self.settings.kv_height
        
        # Determine Base Y
        pos_mode = self.settings.kv_position
        base_y = 0
        if pos_mode == 'above':
            base_y = 50 
        elif pos_mode == 'below':
            base_y = screen_h - key_height - 50 
        else: # auto
             base_y = screen_h - key_height - 50

        start_y = base_y + self.settings.kv_offset_y
        
        # Determine Flow Direction based on Position
        # If KV is at top half -> Flow Down
        # If KV is at bottom half -> Flow Up
        is_top = (start_y + (key_height/2)) < (screen_h / 2)
        
        return {
            'y': start_y,
            'height': key_height,
            'width': key_width,
            'is_top': is_top
        }

    def paintEvent(self, event):
        painter = QPainter()
        try:
            if not painter.begin(self):
                return
            
            painter.setRenderHint(QPainter.Antialiasing)

            current_time = time.perf_counter()
            screen_h = self.height()
            
            # Geometry
            kv_geom = self.get_kv_geometry(screen_h)       
            
            # Origin Y determines where bars start
            # If Top: Start at Bottom of KV (y + h)
            # If Bottom: Start at Top of KV (y)
            if kv_geom['is_top']:
                origin_y = kv_geom['y'] + kv_geom['height']
                direction = 1 # Down (Positive Y)
            else:
                origin_y = kv_geom['y']
                direction = -1 # Up (Negative Y)
                
            speed = self.settings.scroll_speed
            
            to_recycle = []

            # Bar Drawing Loop
            for bar in self.pool.active_bars:
                # 1. Physics
                delta_press = current_time - bar.press_time + Config.INPUT_LATENCY_OFFSET
                dist_head = delta_press * speed
                
                if bar.release_time is None:
                    dist_tail = Config.INPUT_LATENCY_OFFSET * speed
                else:
                    delta_release = current_time - bar.release_time + Config.INPUT_LATENCY_OFFSET
                    dist_tail = delta_release * speed

                # 2. Geometry
                height_bar = dist_head - dist_tail
                if height_bar < Config.BAR_HEIGHT:
                     height_bar = Config.BAR_HEIGHT
                     dist_tail = dist_head - height_bar
                
                # 3. Screen Position
                # Head is the "Furthest" point from origin
                # Tail is the "Closest" point to origin
                
                if direction == 1: # Moving Down
                    # Origin is Top. Head is below Tail.
                    # Top of Rect = Tail Y
                    # Tail Y = Origin + dist_tail
                    rect_y = origin_y + dist_tail
                else: # Moving Up
                    # Origin is Bottom. Head is above Tail.
                    # Top of Rect = Head Y
                    # Head Y = Origin - dist_head
                    rect_y = origin_y - dist_head
                
                # 4. Recycle Check
                if direction == 1:
                    if rect_y > screen_h:
                        to_recycle.append(bar)
                        continue
                else:
                     if (rect_y + height_bar) < 0:
                        to_recycle.append(bar)
                        continue

                # 5. Fade Logic
                alpha = 1.0
                if dist_head > Config.FADE_START_Y:
                    dist_into_fade = dist_head - Config.FADE_START_Y
                    factor = 1.0 - (dist_into_fade / Config.FADE_RANGE)
                    alpha = max(0.0, min(1.0, factor))

                if alpha <= 0.0:
                    continue
                    
                x = Config.LANE_START_X + (bar.lane_index * Config.LANE_WIDTH) + self.settings.kv_offset_x
                
                # Use Custom Color
                base_c = self.settings.bar_color
                c = QColor(base_c)
                # Apply fade alpha to the base alpha
                final_alpha = alpha * (base_c.alphaF()) 
                c.setAlphaF(final_alpha)
                
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
                
            # Draw KeyViewer Panel
            if self.settings.kv_enabled:
                 self.draw_keyviewer(painter, kv_geom)

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
            f"Pos: {self.x()},{self.y()}"
        ]
        
        for i, line in enumerate(info):
            painter.drawText(10, 20 + (i * 15), line)

    def draw_keyviewer(self, painter, geom):
        """Renders the KeyViewer panel."""
        if not Config.LANE_MAP:
            return

        key_width = geom['width']
        key_height = geom['height']
        start_y = geom['y']
        
        # Iterate keys
        ordered_keys = sorted(Config.LANE_MAP.items(), key=lambda item: item[1])
        
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        
        # Custom Color
        default_color = self.settings.bar_color
        
        for k_str, lane_idx in ordered_keys:
            kx = Config.LANE_START_X + (lane_idx * Config.LANE_WIDTH) + self.settings.kv_offset_x
            ky = start_y
            
            k_rect = QRectF(kx, ky, key_width, key_height)
            
            is_pressed = lane_idx in self.active_keys_visual
            
            # Draw Background
            bg_color = QColor(default_color) 
            if is_pressed:
                 # Active: Use full alpha (or slightly lighter)
                 if bg_color.alpha() > 200:
                    bg_color = bg_color.lighter(120)
            else:
                # Inactive: Scale alpha down based on settings
                current_alpha = bg_color.alpha()
                # Opacity is 0.0 to 1.0. If opacity is 0.2, we want 20% of current alpha.
                opacity_factor = self.settings.kv_opacity 
                new_alpha = int(current_alpha * opacity_factor)
                bg_color.setAlpha(new_alpha)
                
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(k_rect)

            # Text
            display_text = k_str.replace("'", "").upper()
            if "KEY." in display_text:
                 display_text = display_text.replace("KEY.", "")
            
            painter.setPen(QColor("white"))
            painter.drawText(k_rect, Qt.AlignCenter, display_text)
            
            # Count
            if self.settings.kv_show_counts:
                count_val = self.key_counts.get(lane_idx, 0)
                
                # Position counts based on flow
                if geom['is_top']:
                     # Flowing Down -> Counts Below? Or Above?
                     # If Top, Usually counts inside or above.
                     # Let's put counts OPPOSITE to flow?
                     # If flow down, bar is below top. 
                     # Image showed counts ABOVE bar.
                     # Let's just put counts ABOVE by default for now (y - 25)
                     count_rect = QRectF(kx, ky - 25, key_width, 20)
                else:
                     # Flowing Up (KV at Bottom)
                     # Counts Above
                     count_rect = QRectF(kx, ky - 25, key_width, 20)
                
                painter.setFont(QFont("Arial", 10, QFont.Bold))
                painter.drawText(count_rect, Qt.AlignCenter, str(count_val))
                painter.setFont(QFont("Arial", 12, QFont.Bold))

