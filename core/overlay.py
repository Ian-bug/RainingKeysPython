import sys
import time
from collections import deque
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QBrush, QColor, QFont
from .configuration import AppConfig

# Windows API for click-through
try:
    import win32gui
    import win32con
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
        self.settings_manager = settings_manager
        self.config: AppConfig = settings_manager.app_config
        
        # Connect to settings changed signal
        self.settings_manager.settings_changed.connect(self.on_settings_changed)
        
        self.pool = BarPool(self.config.MAX_BARS)
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
        self._init_key_counts()
        
        # Track active keys for visual feedback
        self.active_keys_visual = set() # {lane_index}
        
        # Cache for geometry
        self.cached_kv_geom = None

    def _init_key_counts(self):
        if self.config.lane_map:
             for idx in self.config.lane_map.values():
                 if idx not in self.key_counts:
                     self.key_counts[idx] = 0

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
        
        self.update_layout()

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
        self.move(self.config.position.x, self.config.position.y)
        self.update_layout() # Recalculate size if lanes changed
        self._init_key_counts()
        self.cached_kv_geom = None # Invalidate cache

    def update_layout(self):
        """Recalculates window size based on current lanes."""
        max_lane = 0
        if self.config.lane_map:
             max_lane = max(self.config.lane_map.values())
        else:
             max_lane = 0 # Fallback
        
        # LANE_START_X is not in config, defining logic here or use visual.lane_width as offset?
        # Original had LANE_START_X = 50. Let's keep it hardcoded or move to visual settings if needed.
        # For now, let's assume 50.
        lane_start_x = 50 
        
        # Width: Start Offset + (Max Lane Index + 1) * Lane Width + Extra Padding
        width = lane_start_x + ((max_lane + 1) * self.config.visual.lane_width) + 50
        
        # Get primary screen height
        screen = QApplication.primaryScreen()
        height = screen.size().height() if screen else 1080
        
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
        if self.cached_kv_geom and self.cached_kv_geom['screen_h'] == screen_h:
             return self.cached_kv_geom

        key_width = self.config.visual.lane_width
        key_height = self.config.key_viewer.height
        
        # Determine Base Y
        pos_mode = self.config.key_viewer.panel_position
        base_y = 0
        if pos_mode == 'above':
            base_y = 50 
        elif pos_mode == 'below':
            base_y = screen_h - key_height - 50 
        else: # auto
             base_y = screen_h - key_height - 50

        start_y = base_y + self.config.key_viewer.panel_offset_y
        
        # Determine Flow Direction based on Position
        is_top = (start_y + (key_height/2)) < (screen_h / 2)
        
        self.cached_kv_geom = {
            'y': start_y,
            'height': key_height,
            'width': key_width,
            'is_top': is_top,
            'screen_h': screen_h
        }
        return self.cached_kv_geom

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
            if kv_geom['is_top']:
                origin_y = kv_geom['y'] + kv_geom['height']
                direction = 1 # Down (Positive Y)
            else:
                origin_y = kv_geom['y']
                direction = -1 # Up (Negative Y)
                
            self._draw_active_bars(painter, current_time, screen_h, origin_y, direction)

            # Draw KeyViewer Panel
            if self.config.key_viewer.enabled:
                 self.draw_keyviewer(painter, kv_geom)

            # Draw Debug
            if self.config.DEBUG_MODE:
                self.draw_debug(painter, current_time)
                
        except Exception as e:
            print(f"Paint Error: {e}")
        finally:
            if painter.isActive():
                painter.end()

    def _draw_active_bars(self, painter, current_time, screen_h, origin_y, direction):
        speed = self.config.visual.scroll_speed
        to_recycle = []
        
        bar_width = self.config.visual.bar_width
        bar_height_min = self.config.visual.bar_height
        lane_start_x = 50
        lane_width = self.config.visual.lane_width
        kv_offset_x = self.config.key_viewer.panel_offset_x
        bar_color = self.config.visual.bar_color
        
        fade_start_y = self.config.FADE_START_Y
        fade_range = self.config.FADE_RANGE
        input_latency = self.config.INPUT_LATENCY_OFFSET

        # Bar Drawing Loop
        for bar in self.pool.active_bars:
            # 1. Physics
            delta_press = current_time - bar.press_time + input_latency
            dist_head = delta_press * speed
            
            if bar.release_time is None:
                dist_tail = input_latency * speed
            else:
                delta_release = current_time - bar.release_time + input_latency
                dist_tail = delta_release * speed

            # 2. Geometry
            height_bar = dist_head - dist_tail
            if height_bar < bar_height_min:
                    height_bar = bar_height_min
                    dist_tail = dist_head - height_bar
            
            # 3. Screen Position
            if direction == 1: # Moving Down
                rect_y = origin_y + dist_tail
            else: # Moving Up
                rect_y = origin_y - dist_head
            
            # 4. Recycle Check
            should_recycle = False
            if direction == 1:
                if rect_y > screen_h:
                    should_recycle = True
            else:
                    if (rect_y + height_bar) < 0:
                        should_recycle = True

            if should_recycle:
                to_recycle.append(bar)
                continue

            # 5. Fade Logic
            alpha = 1.0
            if dist_head > fade_start_y:
                dist_into_fade = dist_head - fade_start_y
                factor = 1.0 - (dist_into_fade / fade_range)
                alpha = max(0.0, min(1.0, factor))

            if alpha <= 0.0:
                continue # Not visible
                
            x = lane_start_x + (bar.lane_index * lane_width) + kv_offset_x
            
            # Color
            c = QColor(bar_color)
            final_alpha = alpha * (bar_color.alphaF()) 
            c.setAlphaF(final_alpha)
            
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.NoPen)
            painter.drawRect(QRectF(x, rect_y, bar_width, height_bar))

        # Recycle
        for bar in to_recycle:
            try:
                self.pool.active_bars.remove(bar)
                self.pool.recycle(bar)
            except ValueError:
                pass

    def draw_debug(self, painter, current_time):
        self.frame_count += 1
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time

        painter.setPen(QColor(0, 255, 0, 255))
        painter.setFont(QFont("Consolas", 10))
        
        active_count = len(self.pool.active_bars)
        pool_size = len(self.pool.inactive_bars) + active_count
        
        info = [
            f"FPS: {self.current_fps:.1f}",
            f"Active: {active_count}",
            f"Pool: {pool_size}",
            f"Speed: {self.config.visual.scroll_speed}",
            f"Pos: {self.x()},{self.y()}"
        ]
        
        for i, line in enumerate(info):
            painter.drawText(10, 20 + (i * 15), line)

    def draw_keyviewer(self, painter, geom):
        """Renders the KeyViewer panel."""
        if not self.config.lane_map:
            return

        key_width = geom['width']
        key_height = geom['height']
        start_y = geom['y']
        
        # Iterate keys
        ordered_keys = sorted(self.config.lane_map.items(), key=lambda item: item[1])
        
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        default_color = self.config.visual.bar_color
        
        lane_start_x = 50
        lane_width = self.config.visual.lane_width
        kv_offset_x = self.config.key_viewer.panel_offset_x
        
        for k_str, lane_idx in ordered_keys:
            kx = lane_start_x + (lane_idx * lane_width) + kv_offset_x
            ky = start_y
            
            # Context for rendering a single key
            ctx = {
                'painter': painter,
                'lane_idx': lane_idx,
                'k_str': k_str,
                'rect': QRectF(kx, ky, key_width, key_height),
                'base_color': default_color,
                'geom': geom
            }
            
            self._draw_key_button(ctx)

    def _draw_key_button(self, ctx):
        """Draws a single key (bg, text, count) using the provided context."""
        painter = ctx['painter']
        lane_idx = ctx['lane_idx']
        k_rect = ctx['rect']
        base_color = ctx['base_color']
        
        is_pressed = lane_idx in self.active_keys_visual
        
        # 1. Background
        bg_color = QColor(base_color) 
        if is_pressed:
                if bg_color.alpha() > 200:
                    bg_color = bg_color.lighter(120)
        else:
            current_alpha = bg_color.alpha()
            opacity_factor = self.config.key_viewer.opacity 
            new_alpha = int(current_alpha * opacity_factor)
            bg_color.setAlpha(new_alpha)
            
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRect(k_rect)

        # 2. Text
        display_text = ctx['k_str'].replace("'", "").upper()
        if "KEY." in display_text:
                display_text = display_text.replace("KEY.", "")
        
        painter.setPen(QColor("white"))
        painter.drawText(k_rect, Qt.AlignCenter, display_text)
        
        # 3. Count
        if self.config.key_viewer.show_counts:
            count_val = self.key_counts.get(lane_idx, 0)
            
            # Position counts based on flow (Always above for now based on logic)
            # x is k_rect.x(), y is k_rect.y() - 25, width/height same logic
            count_rect = QRectF(k_rect.x(), k_rect.y() - 25, k_rect.width(), 20)
            
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(count_rect, Qt.AlignCenter, str(count_val))
            painter.setFont(QFont("Arial", 12, QFont.Bold))
