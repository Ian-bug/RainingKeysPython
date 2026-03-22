from typing import Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QComboBox, QGroupBox, QPushButton, QCheckBox, QColorDialog
)
from PySide6.QtCore import Signal
from ..settings_manager import SettingsManager
from ..qt_utils import signals_blocked

class PositionSettingsGroup(QGroupBox):
    """Settings group for overlay position configuration."""

    def __init__(self, settings_manager: SettingsManager, parent: Optional[QWidget] = None) -> None:
        """Initialize position settings group.

        Args:
            settings_manager: SettingsManager for config persistence.
            parent: Parent widget (optional).
        """
        super().__init__("Overlay Position", parent)
        self.settings = settings_manager
        self.config = self.settings.app_config
        self.init_ui()
        self.settings.settings_changed.connect(self.update_from_config)

    def init_ui(self) -> None:
        """Initialize UI components."""
        layout = QHBoxLayout()

        self.spin_x = QSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.setPrefix("X: ")
        self.spin_x.setValue(self.config.position.x)
        self.spin_x.valueChanged.connect(self.on_change)

        self.spin_y = QSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.setPrefix("Y: ")
        self.spin_y.setValue(self.config.position.y)
        self.spin_y.valueChanged.connect(self.on_change)

        layout.addWidget(self.spin_x)
        layout.addWidget(self.spin_y)
        self.setLayout(layout)

    def on_change(self) -> None:
        """Handle position value changes."""
        self.config.position.x = self.spin_x.value()
        self.config.position.y = self.spin_y.value()
        self.settings.save()

    def update_from_config(self) -> None:
        """Update UI from current configuration."""
        with signals_blocked(self.spin_x, self.spin_y):
            self.spin_x.setValue(self.config.position.x)
            self.spin_y.setValue(self.config.position.y)

class VisualSettingsGroup(QGroupBox):
    """Settings group for visual appearance configuration."""

    def __init__(self, settings_manager: SettingsManager, parent: Optional[QWidget] = None) -> None:
        """Initialize visual settings group.

        Args:
            settings_manager: SettingsManager for config persistence.
            parent: Parent widget (optional).
        """
        super().__init__("Visual Settings", parent)
        self.settings = settings_manager
        self.config = self.settings.app_config
        self.init_ui()
        self.settings.settings_changed.connect(self.update_from_config)

    def init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Scroll Speed (px/s):"))
        self.spin_speed = QSpinBox()
        self.spin_speed.setRange(100, 5000)
        self.spin_speed.setSingleStep(50)
        self.spin_speed.setValue(self.config.visual.scroll_speed)
        self.spin_speed.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.spin_speed)
        layout.addLayout(speed_layout)

        # Custom Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Bar Color:"))
        self.btn_color = QPushButton("Choose Color")
        self.btn_color.clicked.connect(self.choose_color)
        self.update_color_btn_style()
        color_layout.addWidget(self.btn_color)
        layout.addLayout(color_layout)

        self.setLayout(layout)

    def on_speed_changed(self) -> None:
        """Handle scroll speed changes."""
        self.config.visual.scroll_speed = self.spin_speed.value()
        self.settings.save()

    def choose_color(self) -> None:
        """Open color picker dialog."""
        current = self.config.visual.bar_color
        color = QColorDialog.getColor(current, self, "Select Bar Color", QColorDialog.ShowAlphaChannel)
        if color.isValid():
            rgba = f"{color.red()},{color.green()},{color.blue()},{color.alpha()}"
            self.config.visual.bar_color_str = rgba
            self.settings.save()
            self.update_color_btn_style()

    def update_color_btn_style(self) -> None:
        """Update color button appearance based on current color."""
        c = self.config.visual.bar_color
        # Text color contrasting
        text_col = "black" if c.lightness() > 128 else "white"
        style = f"background-color: rgba({c.red()},{c.green()},{c.blue()},{c.alpha()}); color: {text_col};"
        self.btn_color.setStyleSheet(style)
        self.btn_color.setText(f"RGBA({c.red()},{c.green()},{c.blue()},{c.alpha()})")

    def update_from_config(self) -> None:
        """Update UI from current configuration."""
        with signals_blocked(self.spin_speed):
            self.spin_speed.setValue(self.config.visual.scroll_speed)
        self.update_color_btn_style()

class LaneSettingsGroup(QGroupBox):
    """Settings group for lane key configuration.

    Emits:
        record_toggled(bool): Signal emitted when recording state changes.
    """
    record_toggled = Signal(bool)  # Emits is_recording state

    def __init__(self, settings_manager: SettingsManager, parent: Optional[QWidget] = None) -> None:
        """Initialize lane settings group.

        Args:
            settings_manager: SettingsManager for config persistence.
            parent: Parent widget (optional).
        """
        super().__init__("Lane Configuration", parent)
        self.settings = settings_manager
        self.config = self.settings.app_config
        self.is_recording = False
        self.init_ui()
        self.settings.settings_changed.connect(self.update_from_config)

    def init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        self.lbl_lane_status = QLabel("Current Keys: " + str(len(self.config.lane_map)))
        self.lbl_lane_status.setWordWrap(True)
        layout.addWidget(self.lbl_lane_status)

        self.btn_record = QPushButton("Record Lane Keys")
        self.btn_record.clicked.connect(self.toggle_recording)
        layout.addWidget(self.btn_record)

        self.lbl_instruction = QLabel("Click 'Record', then press keys in order.\nClick 'Stop' when done.")
        self.lbl_instruction.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(self.lbl_instruction)

        self.setLayout(layout)

    def update_from_config(self) -> None:
        """Update UI from current configuration."""
        self.update_status("Current Keys: " + str(len(self.config.lane_map)))

    def toggle_recording(self) -> None:
        """Toggle recording state."""
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.btn_record.setText("Stop Recording")
            self.lbl_lane_status.setText("Recording... Press keys!")
            self.lbl_lane_status.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.btn_record.setText("Record Lane Keys")
            self.lbl_lane_status.setStyleSheet("")

        self.record_toggled.emit(self.is_recording)

    def update_status(self, text: str) -> None:
        """Update the status label text.

        Args:
            text: New status text to display.
        """
        self.lbl_lane_status.setText(text)

class KeyViewerSettingsGroup(QGroupBox):
    """Settings group for KeyViewer panel configuration."""

    def __init__(self, settings_manager: SettingsManager, parent: Optional[QWidget] = None) -> None:
        """Initialize KeyViewer settings group.

        Args:
            settings_manager: SettingsManager for config persistence.
            parent: Parent widget (optional).
        """
        super().__init__("KeyViewer Panel", parent)
        self.settings = settings_manager
        self.config = self.settings.app_config
        self.init_ui()
        self.settings.settings_changed.connect(self.update_from_config)

    @staticmethod
    def _validate_panel_position(position: str) -> str:
        """Validate and normalize panel position string.

        Args:
            position: Position string to validate.

        Returns:
            Valid position string ('above' or 'below').
        """
        if position not in ("above", "below"):
            return "below"
        return position

    def init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        self.chk_kv_enabled = QCheckBox("Enable KeyViewer")
        self.chk_kv_enabled.setChecked(self.config.key_viewer.enabled)
        self.chk_kv_enabled.stateChanged.connect(self.on_change)
        layout.addWidget(self.chk_kv_enabled)

        # Layout & Position
        kv_grid = QHBoxLayout()
        kv_grid.addWidget(QLabel("Height:"))
        self.spin_kv_height = QSpinBox()
        self.spin_kv_height.setRange(10, 500)
        self.spin_kv_height.setValue(self.config.key_viewer.height)
        self.spin_kv_height.valueChanged.connect(self.on_change)
        kv_grid.addWidget(self.spin_kv_height)

        kv_grid.addWidget(QLabel("Pos:"))
        self.combo_kv_pos = QComboBox()
        self.combo_kv_pos.addItems(["below", "above"])
        current = self._validate_panel_position(self.config.key_viewer.panel_position)
        self.combo_kv_pos.setCurrentText(current)
        self.combo_kv_pos.currentTextChanged.connect(self.on_change)
        kv_grid.addWidget(self.combo_kv_pos)
        layout.addLayout(kv_grid)

        # Offsets
        off_layout = QHBoxLayout()
        off_layout.addWidget(QLabel("Offset X:"))
        self.spin_kv_off_x = QSpinBox()
        self.spin_kv_off_x.setRange(-1000, 1000)
        self.spin_kv_off_x.setValue(self.config.key_viewer.panel_offset_x)
        self.spin_kv_off_x.valueChanged.connect(self.on_change)
        off_layout.addWidget(self.spin_kv_off_x)

        off_layout.addWidget(QLabel("Y:"))
        self.spin_kv_off_y = QSpinBox()
        self.spin_kv_off_y.setRange(-1000, 1000)
        self.spin_kv_off_y.setValue(self.config.key_viewer.panel_offset_y)
        self.spin_kv_off_y.valueChanged.connect(self.on_change)
        off_layout.addWidget(self.spin_kv_off_y)
        layout.addLayout(off_layout)

        # Transparency Control
        trans_layout = QHBoxLayout()
        trans_layout.addWidget(QLabel("Inactive Opacity:"))
        self.spin_kv_opacity = QSpinBox()
        self.spin_kv_opacity.setRange(0, 100)
        self.spin_kv_opacity.setSuffix("%")
        self.spin_kv_opacity.setValue(int(self.config.key_viewer.opacity * 100))
        self.spin_kv_opacity.valueChanged.connect(self.on_change)
        trans_layout.addWidget(self.spin_kv_opacity)
        layout.addLayout(trans_layout)

        self.chk_kv_counts = QCheckBox("Show Key Counts")
        self.chk_kv_counts.setChecked(self.config.key_viewer.show_counts)
        self.chk_kv_counts.stateChanged.connect(self.on_change)
        layout.addWidget(self.chk_kv_counts)

        self.setLayout(layout)

    def on_change(self) -> None:
        """Handle any setting value change."""
        self.config.key_viewer.enabled = self.chk_kv_enabled.isChecked()
        self.config.key_viewer.height = self.spin_kv_height.value()
        self.config.key_viewer.panel_position = self.combo_kv_pos.currentText()
        self.config.key_viewer.panel_offset_x = self.spin_kv_off_x.value()
        self.config.key_viewer.panel_offset_y = self.spin_kv_off_y.value()
        self.config.key_viewer.show_counts = self.chk_kv_counts.isChecked()
        self.config.key_viewer.opacity = self.spin_kv_opacity.value() / 100.0
        self.settings.save()

    def update_from_config(self) -> None:
        """Update UI from current configuration."""
        with signals_blocked(
            self.chk_kv_enabled,
            self.spin_kv_height,
            self.combo_kv_pos,
            self.spin_kv_off_x,
            self.spin_kv_off_y,
            self.spin_kv_opacity,
            self.chk_kv_counts
        ):
            self.chk_kv_enabled.setChecked(self.config.key_viewer.enabled)
            self.spin_kv_height.setValue(self.config.key_viewer.height)

            current = self._validate_panel_position(self.config.key_viewer.panel_position)
            self.combo_kv_pos.setCurrentText(current)

            self.spin_kv_off_x.setValue(self.config.key_viewer.panel_offset_x)
            self.spin_kv_off_y.setValue(self.config.key_viewer.panel_offset_y)
            self.spin_kv_opacity.setValue(int(self.config.key_viewer.opacity * 100))
            self.chk_kv_counts.setChecked(self.config.key_viewer.show_counts)
