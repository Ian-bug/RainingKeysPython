from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton
from PySide6.QtCore import Slot
from .settings_manager import SettingsManager
from .ui.components import (
    PositionSettingsGroup, VisualSettingsGroup, 
    LaneSettingsGroup, KeyViewerSettingsGroup
)
from .ui.theme import DARK_THEME

class SettingsWindow(QWidget):
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings = settings_manager
        self.config = self.settings.app_config
        self.setWindowTitle(f"RainingKeys Config v{self.config.VERSION}")
        self.resize(340, 500)
        
        # Apply Theme
        self.setStyleSheet(DARK_THEME)

        # Recording State
        self.is_recording = False
        self.recorded_keys = []
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Scroll Area for better usability on small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)
        
        # Components
        self.pos_group = PositionSettingsGroup(self.settings)
        layout.addWidget(self.pos_group)
        
        self.vis_group = VisualSettingsGroup(self.settings)
        layout.addWidget(self.vis_group)
        
        self.lane_group = LaneSettingsGroup(self.settings)
        self.lane_group.record_toggled.connect(self.on_record_toggled)
        layout.addWidget(self.lane_group)
        
        self.kv_group = KeyViewerSettingsGroup(self.settings)
        layout.addWidget(self.kv_group)

        # Reset Button
        self.btn_reset = QPushButton("Reset Config to Defaults")
        self.btn_reset.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold; padding: 8px;")
        self.btn_reset.clicked.connect(self.settings.reset_to_defaults)
        layout.addWidget(self.btn_reset)
        
        layout.addStretch()
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def on_record_toggled(self, is_recording):
        self.is_recording = is_recording
        if self.is_recording:
            # Start Recording
            self.recorded_keys = []
        else:
            # Stop Recording
            if self.recorded_keys:
                # Save
                self.settings.update_lanes(self.recorded_keys)
                self.lane_group.update_status(f"Saved {len(self.recorded_keys)} lane keys.")
            else:
                self.lane_group.update_status("No keys recorded. Canceled.")

    @Slot(str)
    def handle_raw_key(self, key_str):
        """Slot to receive raw keys from InputMonitor."""
        if self.is_recording:
            # Avoid duplicates if desired
            if key_str not in self.recorded_keys:
                self.recorded_keys.append(key_str)
                self.lane_group.update_status(f"Recorded: {', '.join(self.recorded_keys)}")
