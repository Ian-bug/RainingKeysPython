from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QComboBox, QGroupBox
from PySide6.QtCore import Qt
from .settings_manager import SettingsManager

class SettingsWindow(QWidget):
    def __init__(self, settings_manager: SettingsManager):
        super().__init__()
        self.settings = settings_manager
        self.init_ui()
        self.setWindowTitle("RainingKeys Config")
        self.resize(300, 250)

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
