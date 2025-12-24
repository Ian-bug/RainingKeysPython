from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QGroupBox, QPushButton, QCheckBox, QFrame, QColorDialog
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QPalette
from .settings_manager import SettingsManager
from .config import Config

class SettingsWindow(QWidget):
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings = settings_manager
        self.setWindowTitle(f"RainingKeys Config v{Config.VERSION}")
        self.resize(300, 350)

        # Recording State
        self.is_recording = False
        self.recorded_keys = []
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Position Group
        pos_group = QGroupBox("Overlay Position")
        pos_layout = QHBoxLayout()
        
        self.spin_x = QSpinBox()
        self.spin_x.setRange(-10000, 10000)
        self.spin_x.setPrefix("X: ")
        self.spin_x.setValue(self.settings.overlay_x)
        self.spin_x.valueChanged.connect(self.on_pos_changed)
        
        self.spin_y = QSpinBox()
        self.spin_y.setRange(-10000, 10000)
        self.spin_y.setPrefix("Y: ")
        self.spin_y.setValue(self.settings.overlay_y)
        self.spin_y.valueChanged.connect(self.on_pos_changed)
        
        pos_layout.addWidget(self.spin_x)
        pos_layout.addWidget(self.spin_y)
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)
        
        # Visual Group
        vis_group = QGroupBox("Visual Settings")
        vis_layout = QVBoxLayout()
        
        # Direction (REMOVED: Bound to Position)
        # dir_layout = QHBoxLayout()
        # dir_layout.addWidget(QLabel("Fall Direction:"))
        # self.combo_dir = QComboBox()
        # self.combo_dir.addItems(["down", "up"])
        # self.combo_dir.setCurrentText(self.settings.fall_direction)
        # self.combo_dir.currentTextChanged.connect(self.on_visual_changed)
        # dir_layout.addWidget(self.combo_dir)
        # vis_layout.addLayout(dir_layout)
        
        # Speed
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Scroll Speed (px/s):"))
        self.spin_speed = QSpinBox()
        self.spin_speed.setRange(100, 5000)
        self.spin_speed.setSingleStep(50)
        self.spin_speed.setValue(self.settings.scroll_speed)
        self.spin_speed.valueChanged.connect(self.on_visual_changed)
        speed_layout.addWidget(self.spin_speed)
        vis_layout.addLayout(speed_layout)
        
        # Custom Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Bar Color:"))
        self.btn_color = QPushButton("Choose Color")
        self.btn_color.clicked.connect(self.choose_color)
        self.update_color_btn_style()
        color_layout.addWidget(self.btn_color)
        vis_layout.addLayout(color_layout)
        
        vis_group.setLayout(vis_layout)
        layout.addWidget(vis_group)
        
        # Lane Configuration Group
        lane_group = QGroupBox("Lane Configuration")
        lane_layout = QVBoxLayout()
        
        self.lbl_lane_status = QLabel("Current Keys: " + str(len(Config.LANE_MAP)))
        self.lbl_lane_status.setWordWrap(True)
        lane_layout.addWidget(self.lbl_lane_status)
        
        self.btn_record = QPushButton("Record Lane Keys")
        self.btn_record.clicked.connect(self.toggle_recording)
        lane_layout.addWidget(self.btn_record)
        
        self.lbl_instruction = QLabel("Click 'Record', then press keys in order.\nClick 'Stop' when done.")
        self.lbl_instruction.setStyleSheet("color: gray; font-size: 10px;")
        lane_layout.addWidget(self.lbl_instruction)

        lane_group.setLayout(lane_layout)
        layout.addWidget(lane_group)

        # KeyViewer Configuration Group
        kv_group = QGroupBox("KeyViewer Panel")
        kv_layout = QVBoxLayout()

        self.chk_kv_enabled = QCheckBox("Enable KeyViewer")
        self.chk_kv_enabled.setChecked(self.settings.kv_enabled)
        self.chk_kv_enabled.stateChanged.connect(self.on_kv_changed)
        kv_layout.addWidget(self.chk_kv_enabled)

        # Layout & Position
        kv_grid = QHBoxLayout()
        kv_grid.addWidget(QLabel("Height:"))
        self.spin_kv_height = QSpinBox()
        self.spin_kv_height.setRange(10, 500)
        self.spin_kv_height.setValue(self.settings.kv_height)
        self.spin_kv_height.valueChanged.connect(self.on_kv_changed)
        kv_grid.addWidget(self.spin_kv_height)
        
        kv_grid.addWidget(QLabel("Pos:"))
        self.combo_kv_pos = QComboBox()
        self.combo_kv_pos.addItems(["below", "above"])
        # Handle removed 'auto' gracefully if config still has it
        current = self.settings.kv_position
        if current not in ["below", "above"]:
             current = "below" 
        self.combo_kv_pos.setCurrentText(current)
        self.combo_kv_pos.currentTextChanged.connect(self.on_kv_changed)
        kv_grid.addWidget(self.combo_kv_pos)
        kv_layout.addLayout(kv_grid)

        # Offsets
        off_layout = QHBoxLayout()
        off_layout.addWidget(QLabel("Offset X:"))
        self.spin_kv_off_x = QSpinBox()
        self.spin_kv_off_x.setRange(-1000, 1000)
        self.spin_kv_off_x.setValue(self.settings.kv_offset_x)
        self.spin_kv_off_x.valueChanged.connect(self.on_kv_changed)
        off_layout.addWidget(self.spin_kv_off_x)
        off_layout.addWidget(QLabel("Y:"))
        self.spin_kv_off_y = QSpinBox()
        self.spin_kv_off_y.setRange(-1000, 1000)
        self.spin_kv_off_y.setValue(self.settings.kv_offset_y)
        self.spin_kv_off_y.valueChanged.connect(self.on_kv_changed)
        off_layout.addWidget(self.spin_kv_off_y)
        kv_layout.addLayout(off_layout)

        # Transparency Control
        trans_layout = QHBoxLayout()
        trans_layout.addWidget(QLabel("Inactive Opacity:"))
        self.spin_kv_opacity = QSpinBox()
        self.spin_kv_opacity.setRange(0, 100)
        self.spin_kv_opacity.setSuffix("%")
        self.spin_kv_opacity.setValue(int(self.settings.kv_opacity * 100))
        self.spin_kv_opacity.valueChanged.connect(self.on_kv_changed)
        trans_layout.addWidget(self.spin_kv_opacity)
        kv_layout.addLayout(trans_layout)

        self.chk_kv_counts = QCheckBox("Show Key Counts")
        self.chk_kv_counts.setChecked(self.settings.kv_show_counts)
        self.chk_kv_counts.stateChanged.connect(self.on_kv_changed)
        kv_layout.addWidget(self.chk_kv_counts)

        kv_group.setLayout(kv_layout)
        layout.addWidget(kv_group)
        
        layout.addStretch()
        self.setLayout(layout)

    def on_pos_changed(self):
        self.settings.set('Position', 'x', self.spin_x.value())
        self.settings.set('Position', 'y', self.spin_y.value())
        self.settings.save() 
        
    def choose_color(self):
        current = self.settings.bar_color
        color = QColorDialog.getColor(current, self, "Select Bar Color", QColorDialog.ShowAlphaChannel)
        if color.isValid():
            rgba = f"{color.red()},{color.green()},{color.blue()},{color.alpha()}"
            self.settings.set('Visual', 'bar_color', rgba)
            self.settings.save()
            self.update_color_btn_style()
            
    def update_color_btn_style(self):
        c = self.settings.bar_color
        # Text color contrasting
        text_col = "black" if c.lightness() > 128 else "white"
        style = f"background-color: rgba({c.red()},{c.green()},{c.blue()},{c.alpha()}); color: {text_col};"
        self.btn_color.setStyleSheet(style)
        self.btn_color.setText(f"RGBA({c.red()},{c.green()},{c.blue()},{c.alpha()})") 
        
    def on_visual_changed(self):
        # self.settings.set('Visual', 'fall_direction', self.combo_dir.currentText())
        self.settings.set('Visual', 'scroll_speed', self.spin_speed.value())
        self.settings.save()

    def on_kv_changed(self):
        self.settings.set('keyviewer', 'enabled', self.chk_kv_enabled.isChecked())
        self.settings.set('keyviewer', 'height', self.spin_kv_height.value())
        self.settings.set('keyviewer', 'panel_position', self.combo_kv_pos.currentText())
        self.settings.set('keyviewer', 'panel_offset_x', self.spin_kv_off_x.value())
        self.settings.set('keyviewer', 'panel_offset_y', self.spin_kv_off_y.value())
        self.settings.set('keyviewer', 'show_counts', self.chk_kv_counts.isChecked())
        self.settings.set('keyviewer', 'opacity', self.spin_kv_opacity.value() / 100.0)
        self.settings.save()

    def toggle_recording(self):
        if not self.is_recording:
            # Start Recording
            self.is_recording = True
            self.recorded_keys = []
            self.btn_record.setText("Stop Recording")
            self.lbl_lane_status.setText("Recording... Press keys!")
            self.lbl_lane_status.setStyleSheet("color: red; font-weight: bold;")
        else:
            # Stop Recording
            self.is_recording = False
            self.btn_record.setText("Record Lane Keys")
            self.lbl_lane_status.setStyleSheet("")
            
            if self.recorded_keys:
                # Save
                self.settings.save_lanes(self.recorded_keys)
                self.lbl_lane_status.setText(f"Saved {len(self.recorded_keys)} lane keys.")
                
                # Update overlay if needed? save_lanes emits settings_changed which overlay listens to.
            else:
                 self.lbl_lane_status.setText("No keys recorded. Canceled.")

    @Slot(str)
    def handle_raw_key(self, key_str):
        """Slot to receive raw keys from InputMonitor."""
        if self.is_recording:
            # Avoid duplicates if desired
            if key_str not in self.recorded_keys:
                self.recorded_keys.append(key_str)
                self.lbl_lane_status.setText(f"Recorded: {', '.join(self.recorded_keys)}")
