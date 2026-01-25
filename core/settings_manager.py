import configparser
import os
from PySide6.QtCore import QObject, Signal
from .configuration import AppConfig

class SettingsManager(QObject):
    settings_changed = Signal()

    def __init__(self, filename="config.ini"):
        super().__init__()
        self.filename = filename
        self.config_parser = configparser.ConfigParser()
        self.app_config = AppConfig()
        self.load()

    def load(self):
        """Loads configuration from file."""
        if os.path.exists(self.filename):
            self.config_parser.read(self.filename)
            
            # Visual
            if self.config_parser.has_section('Visual'):
                self.app_config.visual.scroll_speed = self.config_parser.getint('Visual', 'scroll_speed', fallback=800)
                self.app_config.visual.bar_color_str = self.config_parser.get('Visual', 'bar_color', fallback="0,255,255,200")

            # Position
            if self.config_parser.has_section('Position'):
                self.app_config.position.x = self.config_parser.getint('Position', 'x', fallback=0)
                self.app_config.position.y = self.config_parser.getint('Position', 'y', fallback=0)

            # KeyViewer
            if self.config_parser.has_section('keyviewer'):
                kv = self.app_config.key_viewer
                kv.enabled = self.config_parser.getboolean('keyviewer', 'enabled', fallback=False)
                kv.layout = self.config_parser.get('keyviewer', 'layout', fallback="horizontal")
                kv.panel_position = self.config_parser.get('keyviewer', 'panel_position', fallback="below")
                kv.panel_offset_x = self.config_parser.getint('keyviewer', 'panel_offset_x', fallback=0)
                kv.panel_offset_y = self.config_parser.getint('keyviewer', 'panel_offset_y', fallback=0)
                kv.show_counts = self.config_parser.getboolean('keyviewer', 'show_counts', fallback=True)
                kv.height = self.config_parser.getint('keyviewer', 'height', fallback=60)
                kv.opacity = self.config_parser.getfloat('keyviewer', 'opacity', fallback=0.2)

            # Lanes
            if self.config_parser.has_section('lanes'):
                keys_str = self.config_parser.get('lanes', 'keys', fallback="")
                if keys_str:
                    key_list = [k.strip() for k in keys_str.split(',') if k.strip()]
                    self.app_config.set_lane_keys(key_list)
        else:
            # File doesn't exist, save defaults
            self.save()

    def save(self):
        """Persist to file and emit signal."""
        # Visual
        if not self.config_parser.has_section('Visual'): self.config_parser.add_section('Visual')
        self.config_parser.set('Visual', 'scroll_speed', str(self.app_config.visual.scroll_speed))
        self.config_parser.set('Visual', 'bar_color', self.app_config.visual.bar_color_str)

        # Position
        if not self.config_parser.has_section('Position'): self.config_parser.add_section('Position')
        self.config_parser.set('Position', 'x', str(self.app_config.position.x))
        self.config_parser.set('Position', 'y', str(self.app_config.position.y))

        # KeyViewer
        if not self.config_parser.has_section('keyviewer'): self.config_parser.add_section('keyviewer')
        kv = self.app_config.key_viewer
        self.config_parser.set('keyviewer', 'enabled', str(kv.enabled))
        self.config_parser.set('keyviewer', 'layout', kv.layout)
        self.config_parser.set('keyviewer', 'panel_position', kv.panel_position)
        self.config_parser.set('keyviewer', 'panel_offset_x', str(kv.panel_offset_x))
        self.config_parser.set('keyviewer', 'panel_offset_y', str(kv.panel_offset_y))
        self.config_parser.set('keyviewer', 'show_counts', str(kv.show_counts))
        self.config_parser.set('keyviewer', 'height', str(kv.height))
        self.config_parser.set('keyviewer', 'opacity', str(kv.opacity))

        # Lanes
        if not self.config_parser.has_section('lanes'): self.config_parser.add_section('lanes')
        # Reconstruct keys string from lane_map keys sorted by index
        sorted_keys = sorted(self.app_config.lane_map.items(), key=lambda item: item[1])
        keys_str = ",".join([k for k, v in sorted_keys])
        self.config_parser.set('lanes', 'keys', keys_str)

        with open(self.filename, 'w') as f:
            self.config_parser.write(f)
        
        self.settings_changed.emit()

    def update_lanes(self, key_list):
        self.app_config.set_lane_keys(key_list)
        self.save()
