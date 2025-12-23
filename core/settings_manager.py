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
            
        # Defaults
        if not self.config.has_option('Visual', 'scroll_speed'):
            self.config.set('Visual', 'scroll_speed', str(Config.SCROLL_SPEED))
            changed = True
        if not self.config.has_option('Visual', 'fall_direction'):
            self.config.set('Visual', 'fall_direction', 'down')
            changed = True
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
    def fall_direction(self):
        return self.get('Visual', 'fall_direction', 'down', str)

    @property
    def overlay_x(self):
        return self.get('Position', 'x', 0, int)

    @property
    def overlay_y(self):
        return self.get('Position', 'y', 0, int)
