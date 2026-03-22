from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton
from PySide6.QtCore import Slot, QTimer
from typing import List
from .settings_manager import SettingsManager
from .ui.components import (
    PositionSettingsGroup, VisualSettingsGroup,
    LaneSettingsGroup, KeyViewerSettingsGroup
)
from .ui.theme import DARK_THEME
from .logging_config import get_logger

logger = get_logger(__name__)

class SettingsWindow(QWidget):
    """Configuration window for RainingKeys settings.

    Provides UI for modifying all application settings including:
    - Overlay position
    - Visual appearance
    - Lane configuration
    - KeyViewer panel settings
    """

    def __init__(self, settings_manager: SettingsManager) -> None:
        """Initialize the settings window.

        Args:
            settings_manager: SettingsManager instance for config persistence.
        """
        super().__init__()
        self.settings = settings_manager
        self.config = self.settings.app_config
        self.setWindowTitle(f"RainingKeys Config v{self.config.VERSION}")
        self.resize(400, 670)

        # Apply Theme
        self.setStyleSheet(DARK_THEME)

        # Recording State
        self.is_recording = False
        self.recorded_keys: List[str] = []

        # Throttling for UI updates during recording
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.setInterval(100)  # Update UI at most 10 times per second
        self._pending_update_text = ""
        self._update_timer.timeout.connect(self._do_status_update)

        self.init_ui()

    def init_ui(self) -> None:
        """Initialize the UI components."""
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

    def on_record_toggled(self, is_recording: bool) -> None:
        """Handle recording state changes.

        Args:
            is_recording: True if recording started, False if stopped.
        """
        self.is_recording = is_recording
        if self.is_recording:
            # Start Recording
            self.recorded_keys = []
            self._update_timer.stop()  # Stop any pending updates
        else:
            # Stop Recording
            self._update_timer.stop()
            if self.recorded_keys:
                # Save
                self.settings.update_lanes(self.recorded_keys)
                self.lane_group.update_status(f"Saved {len(self.recorded_keys)} lane keys.")
            else:
                self.lane_group.update_status("No keys recorded. Canceled.")

    def _do_status_update(self) -> None:
        """Perform the actual status update (called by throttling timer)."""
        if self._pending_update_text:
            self.lane_group.update_status(self._pending_update_text)
            self._pending_update_text = ""

    @Slot(str)
    def handle_raw_key(self, key_str: str) -> None:
        """Slot to receive raw keys from InputMonitor.

        Args:
            key_str: String representation of the pressed key.
        """
        if self.is_recording:
            # Avoid duplicates
            if key_str not in self.recorded_keys:
                self.recorded_keys.append(key_str)
                # Throttle UI updates to prevent lag
                self._pending_update_text = f"Recorded: {', '.join(self.recorded_keys)}"
                if not self._update_timer.isActive():
                    self._update_timer.start()
