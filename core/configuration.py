from dataclasses import dataclass, field
from typing import Dict, List, Optional
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DisplayConstants:
    """Display and layout constants for the overlay."""
    LANE_START_X: int = 50
    EXTRA_PADDING: int = 50
    KEYVIEWER_OFFSET_Y_TOP: int = 50
    KEYVIEWER_OFFSET_Y_BOTTOM: int = 50
    FALLBACK_SCREEN_HEIGHT: int = 1080
    FADE_START_Y: int = 800
    FADE_RANGE: int = 200

@dataclass
class VisualSettings:
    """Visual settings for bar appearance and behavior."""
    scroll_speed: int = 800
    lane_width: int = 70
    bar_width: int = 70
    bar_height: int = 20
    bar_color_str: str = "0,255,255,200"
    fall_direction: str = "up"

    @property
    def bar_color(self) -> QColor:
        """Parse and validate color string, returning QColor.

        Returns:
            QColor object parsed from bar_color_str.

        Raises:
            ValueError: If color string format is invalid.
        """
        try:
            parts = self.bar_color_str.split(',')
            if len(parts) != 4:
                raise ValueError("Color must have 4 components (R,G,B,A)")

            r, g, b, a = map(int, parts)
            # Validate ranges
            if not all(0 <= x <= 255 for x in [r, g, b, a]):
                raise ValueError("Color values must be between 0 and 255")

            return QColor(r, g, b, a)
        except (ValueError, AttributeError) as e:
            logger.error(f"Invalid color string '{self.bar_color_str}': {e}. Using default.")
            return QColor(0, 255, 255, 200)

@dataclass
class PositionSettings:
    """Overlay window position settings."""
    x: int = 0
    y: int = 0

    def validate(self) -> bool:
        """Validate position values are within screen bounds.

        Uses actual screen size when available, falls back to reasonable defaults.

        Returns:
            True if all values were valid, False if any were clamped.
        """
        # Get screen bounds for validation
        try:
            screen = QApplication.primaryScreen()
            if screen:
                size = screen.size()
                MIN_X = -size.width() // 2
                MIN_Y = -size.height() // 2
                MAX_X = size.width() * 2
                MAX_Y = size.height() * 2
            else:
                # Fallback bounds for headless or error cases
                MIN_X = -10000
                MIN_Y = -10000
                MAX_X = 10000
                MAX_Y = 10000
        except Exception:
            # If screen detection fails, use safe defaults
            MIN_X = -10000
            MIN_Y = -10000
            MAX_X = 10000
            MAX_Y = 10000

        valid = True

        if not (MIN_X <= self.x <= MAX_X):
            logger.warning(f"X position {self.x} out of range [{MIN_X}, {MAX_X}], clamping")
            self.x = max(MIN_X, min(MAX_X, self.x))
            valid = False

        if not (MIN_Y <= self.y <= MAX_Y):
            logger.warning(f"Y position {self.y} out of range [{MIN_Y}, {MAX_Y}], clamping")
            self.y = max(MIN_Y, min(MAX_Y, self.y))
            valid = False

        return valid

@dataclass
class KeyViewerSettings:
    """KeyViewer panel display settings."""
    enabled: bool = True
    layout: str = "horizontal"
    panel_position: str = "below"
    panel_offset_x: int = 0
    panel_offset_y: int = 0
    show_counts: bool = True
    height: int = 60
    opacity: float = 0.2

    def validate(self) -> bool:
        """Validate KeyViewer settings.

        Returns:
            True if all values were valid, False if any were clamped/changed.
        """
        valid = True

        # Validate height
        if not (10 <= self.height <= 500):
            logger.warning(f"KeyViewer height {self.height} out of range [10, 500], clamping")
            self.height = max(10, min(500, self.height))
            valid = False

        # Validate opacity
        if not (0.0 <= self.opacity <= 1.0):
            logger.warning(f"KeyViewer opacity {self.opacity} out of range [0.0, 1.0], clamping")
            self.opacity = max(0.0, min(1.0, self.opacity))
            valid = False

        # Validate panel_position
        if self.panel_position not in ("above", "below"):
            logger.warning(f"Invalid panel_position '{self.panel_position}', using 'below'")
            self.panel_position = "below"
            valid = False

        return valid

@dataclass
class AppConfig:
    """Main application configuration container.

    Attributes:
        visual: Visual display settings
        position: Window position settings
        key_viewer: KeyViewer panel settings
        lane_map: Mapping from key strings to lane indices
        MAX_BARS: Maximum number of concurrent bars to render
        INPUT_LATENCY_OFFSET: Timing offset for input latency compensation
        DEBUG_MODE: Enable debug rendering and logging
        VERSION: Application version string
        CONFIG_VERSION: Config schema version for migrations
        display: Display and layout constants
    """
    visual: VisualSettings = field(default_factory=VisualSettings)
    position: PositionSettings = field(default_factory=PositionSettings)
    key_viewer: KeyViewerSettings = field(default_factory=KeyViewerSettings)
    lane_map: Dict[str, int] = field(default_factory=lambda: {'d': 0, 'f': 1, 'j': 2, 'k': 3})

    # Constants
    MAX_BARS: int = 300
    INPUT_LATENCY_OFFSET: float = 0.0
    DEBUG_MODE: bool = False
    VERSION: str = "1.3.9"
    CONFIG_VERSION: int = 1  # Config schema version for migrations
    display: DisplayConstants = field(default_factory=DisplayConstants)
    
    def set_lane_keys(self, keys: List[str]) -> None:
        """Set lane key mapping.

        Args:
            keys: List of key strings to map to lanes (by index).

        Example:
            set_lane_keys(['d', 'f', 'j', 'k']) maps 'd' to lane 0, 'f' to lane 1, etc.
        """
        new_map = {}
        for idx, key in enumerate(keys):
            new_map[key] = idx
        self.lane_map = new_map

    def migrate_config(self, from_version: int) -> None:
        """Migrate configuration from an older version.

        Args:
            from_version: The config version to migrate from.

        Example:
            migrate_config(0)  # Migrate from version 0 to current version
        """
        if from_version >= self.CONFIG_VERSION:
            return  # Already at or past current version

        # Migration from version 0 to 1
        if from_version == 0:
            # Add any new settings introduced in version 1
            logger.info(f"Migrating config from version {from_version} to {self.CONFIG_VERSION}")
            # No changes needed for v0->v1 migration

        # Future migrations would go here
        # Example:
        # if from_version == 1:
        #     # Migrate v1 to v2
        #     pass

        logger.info(f"Config migration complete, now at version {self.CONFIG_VERSION}")
