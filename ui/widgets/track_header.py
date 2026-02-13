"""
Timeline Header - Controls for a track (Mute, Solo, Volume, Name)
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QSlider, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal

class TrackHeader(QWidget):
    """
    Control header for a track (left side of timeline).
    """
    
    mute_toggled = pyqtSignal(bool)
    solo_toggled = pyqtSignal(bool)
    volume_changed = pyqtSignal(float)
    fx_clicked = pyqtSignal()
    
    def __init__(self, track_data, parent=None):
        super().__init__(parent)
        self.track_data = track_data
        self.setFixedHeight(100)
        self.setFixedWidth(200)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Background
        self.setStyleSheet(f"""
            TrackHeader {{
                background-color: #2b2d31;
                border-bottom: 1px solid #111;
                border-right: 1px solid #000;
            }}
        """)
        
        # Track Name
        self.name_edit = QLineEdit(self.track_data.get('name', 'Track'))
        self.name_edit.setStyleSheet("background: transparent; color: white; font-weight: bold; border: none;")
        layout.addWidget(self.name_edit)
        
        # Controls Row
        ctrl_layout = QHBoxLayout()
        
        # Mute
        self.mute_btn = QPushButton("M")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setFixedSize(25, 25)
        self.mute_btn.setStyleSheet("""
            QPushButton { background: #444; color: #aaa; border: none; }
            QPushButton:checked { background: #ff4444; color: white; }
        """)
        
        # Solo
        self.solo_btn = QPushButton("S")
        self.solo_btn.setCheckable(True)
        self.solo_btn.setFixedSize(25, 25)
        self.solo_btn.setStyleSheet("""
            QPushButton { background: #444; color: #aaa; border: none; }
            QPushButton:checked { background: #ffbb00; color: black; }
        """)
        
        # Record Arm
        self.rec_btn = QPushButton("●")
        self.rec_btn.setCheckable(True)
        self.rec_btn.setFixedSize(25, 25)
        self.rec_btn.setStyleSheet("""
            QPushButton { background: #444; color: #aaa; border: none; border-radius: 12px; }
            QPushButton:checked { background: #ff0000; color: white; }
        """)
        
        # FX Button
        self.fx_btn = QPushButton("FX")
        self.fx_btn.setFixedSize(25, 25)
        self.fx_btn.setStyleSheet("""
            QPushButton { background: #333; color: #00d4ff; border: 1px solid #00d4ff; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #00d4ff; color: black; }
        """)
        self.fx_btn.clicked.connect(self.on_fx_clicked)
        
        ctrl_layout.addWidget(self.mute_btn)
        ctrl_layout.addWidget(self.solo_btn)
        ctrl_layout.addWidget(self.rec_btn)
        ctrl_layout.addWidget(self.fx_btn)
        ctrl_layout.addStretch()
        
        layout.addLayout(ctrl_layout)
        
        # Volume Slider
        vol_layout = QHBoxLayout()
        vol_label = QLabel("Vol")
        vol_label.setStyleSheet("color: #888; font-size: 10px;")
        
        self.vol_slider = QSlider(Qt.Horizontal)
        self.vol_slider.setRange(0, 120)
        self.vol_slider.setValue(100)
        
        vol_layout.addWidget(vol_label)
        vol_layout.addWidget(self.vol_slider)
        layout.addLayout(vol_layout)
        
        # Color Strip
        self.color_strip = QFrame()
        self.color_strip.setFixedHeight(4)
        self.color_strip.setStyleSheet(f"background-color: {self.track_data.get('color', '#00d4ff')};")
        layout.addWidget(self.color_strip)

    def on_fx_clicked(self):
        self.fx_clicked.emit()
