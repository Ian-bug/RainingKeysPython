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
