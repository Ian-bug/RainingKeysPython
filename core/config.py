from PySide6.QtGui import QColor

class Config:
    # Visual Settings
    SCROLL_SPEED = 800  # Pixels per second
    BAR_WIDTH = 60      # Width of a single note bar
    BAR_HEIGHT = 20     # Visual thickness of the bar (does not affect timing)
    
    # Lane Configuration
    # Maps key strings (pynput format) to lane indices (0-based)
    LANE_MAP = {
        "'a'": 0,
        "'s'": 1,
        "'l'": 2,
        "';'": 3
    }
    LANE_WIDTH = 70     # Horizontal spacing between lane starts
    LANE_START_X = 50   # Starting X offset for the first lane

    # Performance & Logic
    MAX_BARS = 300      # Soft limit for object pool
    INPUT_LATENCY_OFFSET = 0.0  # Seconds to add/subtract to align visual with audio
    
    # Fade Out Logic
    # Position Y where fade starts (e.g., 80% down the screen)
    FADE_START_Y = 800  
    FADE_RANGE = 200    # Distance over which it fades to 0 opacity

    # Debugging
    DEBUG_MODE = True

    # Colors (R, G, B, A)
    COLOR_BAR = QColor(100, 200, 255, 200)
    COLOR_BAR_BORDER = QColor(255, 255, 255, 230)
    COLOR_DEBUG_TEXT = QColor(0, 255, 0, 255)
