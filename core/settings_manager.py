import configparser
import os
from PySide6.QtCore import QObject, Signal
from .config import Config

class SettingsManager(QObject):
    settings_changed = Signal()

    def __init__(self, filename="config.ini"):
        super().__init__()
        self.filename = filename
        self.config = configparser.ConfigParser()
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            self.config.read(self.filename)
        
        # Ensure sections exist with defaults if missing
        changed = False
        if not self.config.has_section('Visual'):
            self.config.add_section('Visual')
            changed = True
        if not self.config.has_section('Position'):
            self.config.add_section('Position')
            changed = True
        if not self.config.has_section('lanes'):
            self.config.add_section('lanes')
            changed = True
        if not self.config.has_section('keyviewer'):
            self.config.add_section('keyviewer')
            changed = True
            
        # Defaults
        if not self.config.has_option('Visual', 'scroll_speed'):
            self.config.set('Visual', 'scroll_speed', str(Config.SCROLL_SPEED))
            changed = True
        if not self.config.has_option('Visual', 'scroll_speed'):
            self.config.set('Visual', 'scroll_speed', str(Config.SCROLL_SPEED))
            changed = True
        
        # Color (RGBA)
        if not self.config.has_option('Visual', 'bar_color'):
            # Default Cyan: 0, 255, 255, 200
            self.config.set('Visual', 'bar_color', "0,255,255,200") 
            changed = True
        # REMOVED: Fall Direction (Now bound to Panel Position)
        if not self.config.has_option('Position', 'x'):
            self.config.set('Position', 'x', str(0))
            changed = True
        if not self.config.has_option('Position', 'y'):
            self.config.set('Position', 'y', str(0))
            changed = True
            
        if not self.config.has_option('lanes', 'keys'):
            # Default keys
            default_keys = "'a','s','l',';'"
            self.config.set('lanes', 'keys', default_keys)
            changed = True
        
        # Apply lanes to Config
        self._apply_lanes()
            
        # KeyViewer defaults
        if not self.config.has_option('keyviewer', 'enabled'):
            self.config.set('keyviewer', 'enabled', 'True')
            changed = True
        if not self.config.has_option('keyviewer', 'layout'):
            self.config.set('keyviewer', 'layout', 'horizontal')
            changed = True
        if not self.config.has_option('keyviewer', 'panel_position'):
            self.config.set('keyviewer', 'panel_position', 'auto')
            changed = True
        if not self.config.has_option('keyviewer', 'panel_offset_x'):
            self.config.set('keyviewer', 'panel_offset_x', '0')
            changed = True
        if not self.config.has_option('keyviewer', 'panel_offset_y'):
            self.config.set('keyviewer', 'panel_offset_y', '0')
            changed = True
        if not self.config.has_option('keyviewer', 'show_counts'):
            self.config.set('keyviewer', 'show_counts', 'True')
            changed = True
        if not self.config.has_option('keyviewer', 'height'):
            self.config.set('keyviewer', 'height', '50')
            changed = True
            
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
