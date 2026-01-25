
# Theme Colors
COLOR_BG_DARK = "#2b2b2b"
COLOR_BG_DARKER = "#1e1e1e"
COLOR_BG_BUTTON = "#3e3e3e"
COLOR_BG_BUTTON_HOVER = "#4e4e4e"
COLOR_BG_BUTTON_PRESSED = "#2e2e2e"
COLOR_BORDER = "#555"
COLOR_BORDER_LIGHT = "#3e3e3e"
COLOR_TEXT_MAIN = "#e0e0e0"
COLOR_TEXT_DIM = "#a0a0a0"
COLOR_TEXT_MUTED = "#cccccc"
COLOR_TEXT_BRIGHT = "#fff"

DARK_THEME = f"""
QWidget {{
    background-color: {COLOR_BG_DARK};
    color: {COLOR_TEXT_MAIN};
    font-family: "Segoe UI", sans-serif;
    font-size: 14px;
}}

QGroupBox {{
    border: 1px solid {COLOR_BORDER_LIGHT};
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    font-weight: bold;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: {COLOR_TEXT_DIM};
}}

QPushButton {{
    background-color: {COLOR_BG_BUTTON};
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
    padding: 5px 10px;
    color: {COLOR_TEXT_BRIGHT};
}}

QPushButton:hover {{
    background-color: {COLOR_BG_BUTTON_HOVER};
}}

QPushButton:pressed {{
    background-color: {COLOR_BG_BUTTON_PRESSED};
}}

QSpinBox, QComboBox {{
    background-color: {COLOR_BG_DARKER};
    border: 1px solid {COLOR_BORDER};
    border-radius: 3px;
    padding: 3px;
    color: {COLOR_TEXT_BRIGHT};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {COLOR_BG_BUTTON};
    border: none;
    width: 16px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLOR_BG_BUTTON_HOVER};
}}

QLabel {{
    color: {COLOR_TEXT_MUTED};
}}

QCheckBox {{
    spacing: 5px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
}}
"""
