from dataclasses import dataclass, field
from typing import Dict, List, Optional
from PySide6.QtGui import QColor
from .logging_config import get_logger

logger = get_logger(__name__)

@dataclass
class VisualSettings:
    scroll_speed: int = 800
    lane_width: int = 70
    bar_width: int = 70
    bar_height: int = 20
    bar_color_str: str = "0,255,255,200"
    fall_direction: str = "up"

    # Display constants
    LANE_START_X: int = 50
    EXTRA_PADDING: int = 50
    KEYVIEWER_OFFSET_Y_TOP: int = 50
    KEYVIEWER_OFFSET_Y_BOTTOM: int = 50
    FALLBACK_SCREEN_HEIGHT: int = 1080

    @property
    def bar_color(self) -> QColor:
        """Parse and validate color string, returning QColor."""
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
            logger.warning(f"Invalid color string '{self.bar_color_str}': {e}. Using default.")
            return QColor(0, 255, 255, 200)

@dataclass
class PositionSettings:
    x: int = 0
    y: int = 0

    def validate(self) -> bool:
        """Validate position values are within reasonable bounds.

        Returns:
            True if all values were valid, False if any were clamped.
        """
        MIN_POS = -10000
        MAX_POS = 10000
        valid = True

        if not (MIN_POS <= self.x <= MAX_POS):
            logger.warning(f"X position {self.x} out of range, clamping to [{MIN_POS}, {MAX_POS}]")
            self.x = max(MIN_POS, min(MAX_POS, self.x))
            valid = False

        if not (MIN_POS <= self.y <= MAX_POS):
            logger.warning(f"Y position {self.y} out of range, clamping to [{MIN_POS}, {MAX_POS}]")
            self.y = max(MIN_POS, min(MAX_POS, self.y))
            valid = False

        return valid

@dataclass
class KeyViewerSettings:
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
    visual: VisualSettings = field(default_factory=VisualSettings)
    position: PositionSettings = field(default_factory=PositionSettings)
    key_viewer: KeyViewerSettings = field(default_factory=KeyViewerSettings)
    lane_map: Dict[str, int] = field(default_factory=dict)
    
    # Constants
    MAX_BARS: int = 300
    INPUT_LATENCY_OFFSET: float = 0.0
    FADE_START_Y: int = 800
    FADE_RANGE: int = 200
    DEBUG_MODE: bool = False
    VERSION: str = "1.3.7"
    
    def __post_init__(self):
        if not self.lane_map:
            self.lane_map = {'d': 0, 'f': 1, 'j': 2, 'k': 3}
    
    def set_lane_keys(self, keys: List[str]) -> None:
        """Set lane key mapping.

        Args:
            keys: List of key strings to map to lanes (by index).
        """
        new_map = {}
        for idx, key in enumerate(keys):
            new_map[key] = idx
        self.lane_map = new_map
