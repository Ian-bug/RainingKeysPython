from dataclasses import dataclass, field
from typing import Dict, List
from PySide6.QtGui import QColor

@dataclass
class VisualSettings:
    scroll_speed: int = 800
    lane_width: int = 70
    bar_width: int = 70
    bar_height: int = 20
    bar_color_str: str = "0,255,255,200"
    fall_direction: str = "up"
    
    @property
    def bar_color(self) -> QColor:
        try:
            r, g, b, a = map(int, self.bar_color_str.split(','))
            return QColor(r, g, b, a)
        except ValueError:
            return QColor(0, 255, 255, 200)

@dataclass
class PositionSettings:
    x: int = 0
    y: int = 0

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
    VERSION: str = "1.3.5"
    
    def __post_init__(self):
        if not self.lane_map:
            self.lane_map = {'d': 0, 'f': 1, 'j': 2, 'k': 3}
    
    def set_lane_keys(self, keys: List[str]):
        new_map = {}
        for idx, key in enumerate(keys):
            new_map[key] = idx
        self.lane_map = new_map
