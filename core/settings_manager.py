import configparser
import os
from PySide6.QtCore import QObject, Signal
from .config import Config

class SettingsManager(QObject):
    settings_changed = Signal()

    DEFAULTS = {
        'Visual': {
            'scroll_speed': str(Config.SCROLL_SPEED),
            'bar_color': "0,255,255,200"
        },
        'Position': {
            'x': '0',
            'y': '0'
        },
        'lanes': {
            'keys': "'a','s','l',';'"
        },
        'keyviewer': {
            'enabled': 'True',
            'layout': 'horizontal',
            'panel_position': 'auto',
            'panel_offset_x': '0',
            'panel_offset_y': '0',
            'show_counts': 'True',
            'height': '50',
            'opacity': '0.2'
        }
    }

    def __init__(self, filename="config.ini"):
        super().__init__()
        self.filename = filename
        self.config = configparser.ConfigParser()
        self._load()

    def _load(self):
        """Loads configuration from file, applying defaults where missing."""
        if os.path.exists(self.filename):
            self.config.read(self.filename)
        
        changed = False
        
        for section, options in self.DEFAULTS.items():
            if not self.config.has_section(section):
                self.config.add_section(section)
                changed = True
            
            for key, val in options.items():
                if not self.config.has_option(section, key):
                    self.config.set(section, key, val)
                    changed = True
                    
        # Apply lanes to Config
        self._apply_lanes()

        if changed:
            self.save()

    def get(self, section, key, default, type_func=str):
        """Generic getter with type conversion."""
        if not self.config.has_option(section, key):
            return default
        try:
            val = self.config.get(section, key)
            return type_func(val)
        except ValueError:
            return default

    def set(self, section, key, value):
        """Generic setter. Does NOT autosave."""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value))
        
    def save(self):
        """Persist to file and emit signal."""
        with open(self.filename, 'w') as f:
            self.config.write(f)
        self.settings_changed.emit()

    def _apply_lanes(self):
        """Reads keys from config and updates Config.LANE_MAP."""
        if self.config.has_option('lanes', 'keys'):
            keys_str = self.config.get('lanes', 'keys')
            key_list = [k.strip() for k in keys_str.split(',') if k.strip()]
            
            # Rebuild map
            Config.LANE_MAP.clear()
            for idx, k in enumerate(key_list):
                Config.LANE_MAP[k] = idx
                
    def save_lanes(self, key_list):
        """Saves a list of key strings to config."""
        keys_str = ",".join(key_list)
        if not self.config.has_section('lanes'):
            self.config.add_section('lanes')
        self.config.set('lanes', 'keys', keys_str)
        self.save() # Saves to file
        self._apply_lanes() # Updates runtime config
        self.settings_changed.emit() # Notify UI/Overlay

    # Properties for easy access
    @property
    def scroll_speed(self):
        return self.get('Visual', 'scroll_speed', Config.SCROLL_SPEED, int)
    
    # REMOVED: fall_direction property

    @property
    def overlay_x(self):
        return self.get('Position', 'x', 0, int)

    @property
    def overlay_y(self):
        return self.get('Position', 'y', 0, int)

    @property
    def bar_color(self):
        s = self.get('Visual', 'bar_color', "0,255,255,200", str)
        try:
            r, g, b, a = map(int, s.split(','))
            from PySide6.QtGui import QColor 
            return QColor(r, g, b, a)
        except:
            from PySide6.QtGui import QColor
            return QColor(0, 255, 255, 200)

    # KeyViewer Properties
    @property
    def kv_enabled(self):
        return self.config.getboolean('keyviewer', 'enabled')
    @property
    def kv_layout(self):
        return self.config.get('keyviewer', 'layout')
    @property
    def kv_position(self):
        return self.config.get('keyviewer', 'panel_position')
    @property
    def kv_height(self):
         return self.get('keyviewer', 'height', 50, int)
    @property
    def kv_offset_x(self):
         return self.get('keyviewer', 'panel_offset_x', 0, int)
    @property
    def kv_offset_y(self):
         return self.get('keyviewer', 'panel_offset_y', 0, int)
    @property
    def kv_show_counts(self):
        return self.config.getboolean('keyviewer', 'show_counts')
    @property
    def kv_opacity(self):
        return self.get('keyviewer', 'opacity', 0.2, float)
