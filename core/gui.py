from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QGroupBox, QPushButton
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
        
        # Direction
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Fall Direction:"))
        self.combo_dir = QComboBox()
        self.combo_dir.addItems(["down", "up"])
        self.combo_dir.setCurrentText(self.settings.fall_direction)
        self.combo_dir.currentTextChanged.connect(self.on_visual_changed)
        dir_layout.addWidget(self.combo_dir)
        vis_layout.addLayout(dir_layout)
        
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
        
        layout.addStretch()
        self.setLayout(layout)

    def on_pos_changed(self):
        self.settings.set('Position', 'x', self.spin_x.value())
        self.settings.set('Position', 'y', self.spin_y.value())
        self.settings.save() 
        
    def on_visual_changed(self):
        self.settings.set('Visual', 'fall_direction', self.combo_dir.currentText())
        self.settings.set('Visual', 'scroll_speed', self.spin_speed.value())
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
