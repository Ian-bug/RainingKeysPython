import configparser
import os
import shutil
from typing import Optional
from PySide6.QtCore import QObject, Signal
from .configuration import AppConfig
from .logging_config import get_logger

logger = get_logger(__name__)

class SettingsManager(QObject):
    settings_changed = Signal()  # Emitted when configuration changes

    def __init__(self, filename: str = "config.ini") -> None:
        super().__init__()
        self.filename = filename
        self.config_parser = configparser.ConfigParser()
        self.app_config = AppConfig()
        self.load()

    def load(self) -> None:
        """Loads configuration from file with schema validation and migration."""
        if os.path.exists(self.filename):
            try:
                self.config_parser.read(self.filename)
            except (configparser.Error, IOError) as e:
                logger.error(f"Failed to read config file {self.filename}: {e}")
                logger.info("Using default configuration")
                return

            # Get config version for migration
            try:
                config_version = self.config_parser.getint('General', 'config_version', fallback=0)
            except (configparser.Error, ValueError):
                config_version = 0

            # Validate config file schema
            if not self._validate_schema():
                logger.warning(f"Config file {self.filename} has schema issues, using defaults where invalid")

            # Visual
            if self.config_parser.has_section('Visual'):
                self.app_config.visual.scroll_speed = self.config_parser.getint('Visual', 'scroll_speed', fallback=800)
                self.app_config.visual.bar_color_str = self.config_parser.get('Visual', 'bar_color', fallback="0,255,255,200")
                self.app_config.visual.fall_direction = self.config_parser.get('Visual', 'fall_direction', fallback="up")

            # Position
            if self.config_parser.has_section('Position'):
                self.app_config.position.x = self.config_parser.getint('Position', 'x', fallback=0)
                self.app_config.position.y = self.config_parser.getint('Position', 'y', fallback=0)

            # KeyViewer
            if self.config_parser.has_section('keyviewer'):
                kv = self.app_config.key_viewer
                kv.enabled = self.config_parser.getboolean('keyviewer', 'enabled', fallback=True)
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

            # Run migrations if needed
            if config_version < self.app_config.CONFIG_VERSION:
                self.app_config.migrate_config(config_version)
                # Save migrated config
                self.save()
            else:
                # Validate loaded values and log if clamped
                pos_valid = self.app_config.position.validate()
                kv_valid = self.app_config.key_viewer.validate()

                if not pos_valid or not kv_valid:
                    logger.warning("Some configuration values were out of range and were clamped. Saving corrected config.")
                    self.save()  # Save the corrected values
        else:
            # File doesn't exist, save defaults
            self.save()

    def _validate_schema(self) -> bool:
        """Validate the configuration file schema.

        Returns:
            True if schema is valid, False if issues found.
        """
        is_valid = True

        # Check for required sections
        required_sections = ['Visual', 'Position', 'keyviewer', 'lanes']
        for section in required_sections:
            if not self.config_parser.has_section(section):
                logger.warning(f"Missing required section: {section}")
                is_valid = False

        # Check for required keys in each section
        visual_keys = ['scroll_speed', 'bar_color', 'fall_direction']
        for key in visual_keys:
            if self.config_parser.has_section('Visual') and key not in self.config_parser['Visual']:
                logger.warning(f"Missing required key 'Visual.{key}'")
                is_valid = False

        return is_valid

    def save(self) -> None:
        """Persist to file with atomic write for safety.

        Uses a temporary file and atomic rename to prevent corruption.
        If write fails, the original config file remains intact.

        Raises:
            IOError: If the file cannot be written.
        """
        # Create temporary file for atomic write
        temp_filename = f"{self.filename}.tmp"

        # Visual
        if not self.config_parser.has_section('Visual'): self.config_parser.add_section('Visual')
        self.config_parser.set('Visual', 'scroll_speed', str(self.app_config.visual.scroll_speed))
        self.config_parser.set('Visual', 'bar_color', self.app_config.visual.bar_color_str)
        self.config_parser.set('Visual', 'fall_direction', self.app_config.visual.fall_direction)

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

        # General (metadata)
        if not self.config_parser.has_section('General'): self.config_parser.add_section('General')
        self.config_parser.set('General', 'config_version', str(self.app_config.CONFIG_VERSION))

        # Atomic write: write to temp file first
        try:
            with open(temp_filename, 'w', encoding='utf-8') as f:
                self.config_parser.write(f)

            # Atomic rename (works on Unix and Windows)
            if os.path.exists(self.filename):
                shutil.copy2(self.filename, f"{self.filename}.bak")  # Backup original

            # On Windows, we need to remove the target first for atomic rename
            if os.name == 'nt' and os.path.exists(self.filename):
                os.remove(self.filename)

            os.rename(temp_filename, self.filename)

            # Clean up backup on success
            if os.path.exists(f"{self.filename}.bak"):
                os.remove(f"{self.filename}.bak")

            logger.debug(f"Configuration saved to {self.filename}")
        except (IOError, OSError) as e:
            # Clean up temp file on error
            if os.path.exists(temp_filename):
                try:
                    os.remove(temp_filename)
                except:
                    pass

            logger.error(f"Failed to save configuration to {self.filename}: {e}")
            raise

        self.settings_changed.emit()

    def update_lanes(self, key_list: list[str]) -> None:
        """Update lane configuration and reset key counters.

        Args:
            key_list: List of key strings to map to lanes.
        """
        self.app_config.set_lane_keys(key_list)
        self.save()
        logger.info(f"Lane configuration updated with {len(key_list)} keys")

    def reset_to_defaults(self) -> None:
        """Resets configuration to default values."""
        default_config = AppConfig()
        
        # Replace sub-objects with defaults
        self.app_config.visual = default_config.visual
        self.app_config.position = default_config.position
        self.app_config.key_viewer = default_config.key_viewer
        self.app_config.lane_map = default_config.lane_map
        
        self.save()
