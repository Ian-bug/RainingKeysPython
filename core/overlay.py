import time
from collections import deque
from typing import Dict, Set, Optional
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QPainter, QBrush, QColor, QFont, QFontDatabase
from .configuration import AppConfig
from .settings_manager import SettingsManager
from .ui.theme import COLOR_TEXT_BRIGHT
from .logging_config import get_logger

logger = get_logger(__name__)

# Windows API for click-through
try:
    import win32gui
    import win32con
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False
    logger.warning("pywin32 not found. Click-through functionality may not work properly.")

class Bar:
    """Represents a falling visual bar."""
    __slots__ = ['lane_index', 'press_time', 'release_time', 'active', 'removed']

    def __init__(self) -> None:
        self.lane_index: int = 0
        self.press_time: float = 0.0
        self.release_time: Optional[float] = None  # None means currently held
        self.active: bool = False
        self.removed: bool = False  # Track if this bar was already removed from active_bars

class BarPool:
    """
    Manages a pool of Bar objects. Uses a soft limit approach.
    """
    def __init__(self, max_size: int) -> None:
        self.max_size = max_size
        self.active_bars: deque[Bar] = deque()
        self.inactive_bars: deque[Bar] = deque()

        # Pre-allocate some bars
        initial_alloc = min(max_size, 50)
        for _ in range(initial_alloc):
            self.inactive_bars.append(Bar())

    def spawn(self, lane_index: int, timestamp: float) -> Bar:
        """
        Activates a bar. If pool is empty/full, handles gracefully.

        Args:
            lane_index: Which lane this bar belongs to.
            timestamp: When the key was pressed.

        Returns:
            The activated Bar object.
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

    def recycle(self, bar: Bar) -> None:
        """Returns a bar to the inactive pool.

        Args:
            bar: The Bar object to recycle.

        Raises:
            ValueError: If the bar is still active.
        """
        if bar.active:
            # This shouldn't happen with proper lifecycle management, but handle gracefully
            logger.debug(f"Deactivating active bar in lane {bar.lane_index} before recycling")
            bar.active = False
        bar.removed = False  # Reset removed flag for reuse
        bar.press_time = 0.0
        bar.release_time = None
        self.inactive_bars.append(bar)

class RainingKeysOverlay(QWidget):
    def __init__(self, settings_manager: SettingsManager) -> None:
        super().__init__()
        self.settings_manager = settings_manager
        self.config: AppConfig = settings_manager.app_config

        # Connect to settings changed signal
        self.settings_manager.settings_changed.connect(self.on_settings_changed)

        self.pool = BarPool(self.config.MAX_BARS)
        self.active_holds: Dict[int, Bar] = {}  # {lane_index: Bar} tracking currently held notes

        self.init_ui()

        # High-res timer for rendering - use screen refresh rate
        screen = QApplication.primaryScreen()
        refresh_rate = screen.refreshRate() if screen else 60.0
        interval_ms = int(1000.0 / refresh_rate) if refresh_rate > 0 else 16
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_canvas)
        self.timer.start(interval_ms)

        # Debug stats - only initialized if debug mode is enabled
        self.last_fps_time: float = 0.0
        self.frame_count: int = 0
        self.current_fps: float = 0.0
        if self.config.DEBUG_MODE:
            self.last_fps_time = time.perf_counter()

        # KeyViewer State
        self.key_counts: Dict[int, int] = {}  # {lane_index: count}
        # Initialize counts for mapped lanes
        self._init_key_counts()

        # Track active keys for visual feedback
        self.active_keys_visual: Set[int] = set()  # {lane_index}

        # Cache for geometry
        self.cached_kv_geom: Optional[Dict] = None

        # Font cache for performance
        self._font_cache: Dict[str, QFont] = {}

        # Store last screen height for resize detection
        self._last_screen_height: int = 0

    def _init_key_counts(self) -> None:
        """Initialize key counters for all mapped lanes."""
        if self.config.lane_map:
            for idx in self.config.lane_map.values():
                if idx not in self.key_counts:
                    self.key_counts[idx] = 0

        # Clean up old lane indices that no longer exist
        current_indices = set(self.config.lane_map.values())
        to_remove = [idx for idx in self.key_counts if idx not in current_indices]
        for idx in to_remove:
            del self.key_counts[idx]

    def init_ui(self) -> None:
        """Initialize the UI window properties and layout."""
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
        self._update_win32_clickthrough()

    def _update_win32_clickthrough(self) -> None:
        """Update Win32 click-through window handle. Safe to call multiple times."""
        if not HAS_WIN32:
            return

        try:
            hwnd = int(self.winId())
            styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT)
        except Exception as e:
            logger.error(f"Failed to set Win32 click-through: {e}")

    def resizeEvent(self, event) -> None:
        """Handle window resize events to invalidate geometry cache."""
        screen_h = self.height()
        if screen_h != self._last_screen_height:
            self.cached_kv_geom = None
            self._last_screen_height = screen_h
        super().resizeEvent(event)

    def on_settings_changed(self) -> None:
        """Handle configuration changes by updating UI state."""
        # Move window live when settings change
        self.move(self.config.position.x, self.config.position.y)
        self.update_layout()  # Recalculate size if lanes changed
        self._init_key_counts()
        self._reset_key_counts()  # Reset counters when settings change
        self.cached_kv_geom = None  # Invalidate cache

        # Clear font cache to prevent stale cached fonts
        self._font_cache.clear()

        # Reinitialize pool if lane count changed significantly
        max_lanes = len(self.config.lane_map)
        required_pool_size = max(self.config.MAX_BARS, max_lanes * 20)
        if required_pool_size > self.pool.max_size:
            # Pool is too small for current lanes, recreate
            self.pool = BarPool(required_pool_size)
            self.active_holds.clear()
            logger.info(f"Recreated pool with size {self.pool.max_size} for {max_lanes} lanes")

    def _reset_key_counts(self) -> None:
        """Reset key counters to prevent unbounded growth."""
        self.key_counts.clear()
        self._init_key_counts()
        logger.debug("Key counters reset")

    def update_layout(self) -> None:
        """Recalculates window size based on current lanes."""
        max_lane = 0
        if self.config.lane_map:
            max_lane = max(self.config.lane_map.values())
        else:
            max_lane = 0  # Fallback

        # Use configuration constants instead of magic numbers
        lane_start_x = self.config.display.LANE_START_X

        # Width: Start Offset + (Max Lane Index + 1) * Lane Width + Extra Padding
        width = lane_start_x + ((max_lane + 1) * self.config.visual.lane_width) + self.config.display.EXTRA_PADDING

        # Get primary screen height
        screen = QApplication.primaryScreen()
        if screen:
            height = screen.size().height()
        else:
            height = self.config.display.FALLBACK_SCREEN_HEIGHT
            logger.warning(f"Could not detect screen size, using fallback height: {height}")

        self.resize(width, height)

    def handle_input(self, lane_index: int, timestamp: float) -> None:
        """Slot called when input monitor detects a key press."""
        if lane_index in self.active_holds:
            # Duplicate press - log for debugging but don't create new bar
            logger.debug(f"Ignoring duplicate press on lane {lane_index}")
        else:
            bar = self.pool.spawn(lane_index, timestamp)
            self.active_holds[lane_index] = bar

            # KeyViewer Logic
            self.active_keys_visual.add(lane_index)
            if lane_index not in self.key_counts:
                self.key_counts[lane_index] = 0
            self.key_counts[lane_index] += 1

    def handle_release(self, lane_index: int, timestamp: float) -> None:
        """Slot called when input monitor detects a key release."""
        if lane_index in self.active_holds:
            bar = self.active_holds.pop(lane_index)
            bar.release_time = timestamp
            bar.active = False  # Mark bar as inactive when key is released

        # KeyViewer Logic
        if lane_index in self.active_keys_visual:
            self.active_keys_visual.remove(lane_index)

    def update_canvas(self) -> None:
        """Trigger a canvas update."""
        self.update()  # Triggers paintEvent

    def get_kv_geometry(self, screen_h: int) -> dict:
        """Calculates KeyViewer position and dimensions.

        Args:
            screen_h: Current screen height in pixels.

        Returns:
            Dictionary containing KeyViewer geometry information.
        """
        if self.cached_kv_geom and self.cached_kv_geom['screen_h'] == screen_h:
            return self.cached_kv_geom

        key_width = self.config.visual.lane_width
        key_height = self.config.key_viewer.height

        # Determine Base Y using configuration constants
        pos_mode = self.config.key_viewer.panel_position
        base_y = 0
        if pos_mode == 'above':
            base_y = self.config.display.KEYVIEWER_OFFSET_Y_TOP
        elif pos_mode == 'below':
            base_y = screen_h - key_height - self.config.display.KEYVIEWER_OFFSET_Y_BOTTOM
        else:  # auto
            base_y = screen_h - key_height - self.config.display.KEYVIEWER_OFFSET_Y_BOTTOM

        start_y = base_y + self.config.key_viewer.panel_offset_y

        # Determine Flow Direction based on Position
        is_top = (start_y + (key_height / 2)) < (screen_h / 2)

        self.cached_kv_geom = {
            'y': start_y,
            'height': key_height,
            'width': key_width,
            'is_top': is_top,
            'screen_h': screen_h
        }
        return self.cached_kv_geom

    def paintEvent(self, event) -> None:
        """Main paint event handler - renders the overlay.

        Handles all rendering including:
        - Falling bars (active notes)
        - KeyViewer panel
        - Debug information (when DEBUG_MODE is enabled)

        Expected Failures:
            - QPainter.begin() may fail if widget is not ready
            - Windows API calls may fail if window handle is invalid
            - Font loading may fail for missing fonts

        All rendering errors are caught and logged without crashing.
        """
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
                direction = 1  # Down (Positive Y)
            else:
                origin_y = kv_geom['y']
                direction = -1  # Up (Negative Y)

            self._draw_active_bars(painter, current_time, screen_h, origin_y, direction)

            # Draw KeyViewer Panel
            if self.config.key_viewer.enabled:
                self.draw_keyviewer(painter, kv_geom)

            # Draw Debug
            if self.config.DEBUG_MODE:
                self.draw_debug(painter, current_time)

        except Exception as e:
            logger.error(f"Paint error: {e}", exc_info=True)
        finally:
            if painter.isActive():
                painter.end()

    def _draw_active_bars(
        self,
        painter: QPainter,
        current_time: float,
        screen_h: int,
        origin_y: float,
        direction: int
    ) -> None:
        speed = self.config.visual.scroll_speed
        to_recycle = []

        bar_width = self.config.visual.bar_width
        bar_height_min = self.config.visual.bar_height
        lane_start_x = self.config.display.LANE_START_X
        lane_width = self.config.visual.lane_width
        kv_offset_x = self.config.key_viewer.panel_offset_x
        bar_color = self.config.visual.bar_color

        fade_start_y = self.config.display.FADE_START_Y
        fade_range = self.config.display.FADE_RANGE
        input_latency = self.config.INPUT_LATENCY_OFFSET

        # Bar Drawing Loop
        for bar in self.pool.active_bars:
            # Skip bars that were already marked for removal
            if bar.removed:
                continue

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
                bar.removed = True  # Mark as removed before adding to to_recycle
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

        # Recycle - now safe to remove marked bars
        for bar in to_recycle:
            try:
                if bar in self.pool.active_bars:
                    self.pool.active_bars.remove(bar)
                self.pool.recycle(bar)
            except ValueError:
                # This should never happen now with the removed flag
                logger.warning("Attempted to remove a bar that was already removed")

    def draw_debug(self, painter: QPainter, current_time: float) -> None:
        """Draw debug information overlay.

        Args:
            painter: QPainter instance for rendering.
            current_time: Current time from perf_counter.
        """
        self.frame_count += 1
        if current_time - self.last_fps_time >= 1.0:
            self.current_fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time

        # Use system monospace font with fallback
        mono_font = self._get_mono_font(10)
        painter.setFont(mono_font)
        painter.setPen(QColor(0, 255, 0, 255))
        
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

    def draw_keyviewer(self, painter: QPainter, geom: dict) -> None:
        """Renders the KeyViewer panel.

        Args:
            painter: QPainter instance for rendering.
            geom: KeyViewer geometry dictionary from get_kv_geometry.
        """
        if not self.config.lane_map:
            return

        key_width = geom['width']
        key_height = geom['height']
        start_y = geom['y']

        # Iterate keys
        ordered_keys = sorted(self.config.lane_map.items(), key=lambda item: item[1])

        # Use system sans-serif font with fallback
        sans_font = self._get_sans_font(12, QFont.Bold)
        painter.setFont(sans_font)
        default_color = self.config.visual.bar_color

        lane_start_x = self.config.display.LANE_START_X
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

    def _draw_key_button(self, ctx: dict) -> None:
        """Draws a single key (bg, text, count) using the provided context.

        Args:
            ctx: Dictionary containing rendering context information.
        """
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

        painter.setPen(QColor(COLOR_TEXT_BRIGHT))
        painter.drawText(k_rect, Qt.AlignCenter, display_text)

        # 3. Count
        if self.config.key_viewer.show_counts:
            count_val = self.key_counts.get(lane_idx, 0)

            # Position counts based on flow (Always above for now based on logic)
            # x is k_rect.x(), y is k_rect.y() - 25, width/height same logic
            count_rect = QRectF(k_rect.x(), k_rect.y() - 25, k_rect.width(), 20)

            small_font = self._get_sans_font(10, QFont.Bold)
            painter.setFont(small_font)
            painter.drawText(count_rect, Qt.AlignCenter, str(count_val))
            painter.setFont(self._get_sans_font(12, QFont.Bold))

    def _get_mono_font(self, size: int) -> QFont:
        """Get a monospace font with cross-platform fallbacks and caching.

        Args:
            size: Font size in points.

        Returns:
            QFont instance with monospace font family.
        """
        # Validate size to prevent Qt errors
        if size <= 0:
            logger.warning(f"Invalid font size {size} requested, using minimum of 1")
            size = 1

        cache_key = f"mono_{size}"
        if cache_key in self._font_cache:
            cached_font = self._font_cache[cache_key]
            # Validate cached font is still valid
            if cached_font.pointSize() == size:
                return cached_font
            else:
                # Cache mismatch, remove and recreate
                del self._font_cache[cache_key]

        font = QFont()
        font.setStyleHint(QFont.TypeWriter)

        # Try common monospace fonts in order of preference
        font_db = QFontDatabase()
        mono_families = ["Consolas", "Courier New", "Monaco", "Liberation Mono", "monospace"]

        for family in mono_families:
            if family in font_db.families():
                font.setFamily(family)
                font.setPointSize(size)
                self._font_cache[cache_key] = font
                return font

        # Fallback to system default
        font.setFamily("monospace")
        font.setPointSize(size)
        self._font_cache[cache_key] = font
        return font

    def _get_sans_font(self, size: int, weight: QFont.Weight = QFont.Normal) -> QFont:
        """Get a sans-serif font with cross-platform fallbacks and caching.

        Args:
            size: Font size in points.
            weight: Font weight (Normal, Bold, etc.).

        Returns:
            QFont instance with sans-serif font family.
        """
        # Validate size to prevent Qt errors
        if size <= 0:
            logger.warning(f"Invalid font size {size} requested, using minimum of 1")
            size = 1

        cache_key = f"sans_{size}_{weight.value}"
        if cache_key in self._font_cache:
            cached_font = self._font_cache[cache_key]
            # Validate cached font is still valid
            if cached_font.pointSize() == size and cached_font.weight() == weight:
                return cached_font
            else:
                # Cache mismatch, remove and recreate
                del self._font_cache[cache_key]

        font = QFont()
        font.setStyleHint(QFont.SansSerif)
        font.setWeight(weight)

        # Try common sans-serif fonts in order of preference
        font_db = QFontDatabase()
        sans_families = ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans", "sans-serif"]

        for family in sans_families:
            if family in font_db.families():
                font.setFamily(family)
                font.setPointSize(size)
                self._font_cache[cache_key] = font
                return font

        # Fallback to system default
        font.setFamily("sans-serif")
        font.setPointSize(size)
        self._font_cache[cache_key] = font
        return font
