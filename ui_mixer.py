from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSlider, QLabel, 
                               QPushButton, QFrame, QStyleOptionSlider, QStyle)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QFont

class FaderWidget(QWidget):
    valueChanged = Signal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setRange(0, 100)
        self.slider.setValue(80)
        self.slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: #27272a;
                width: 6px;
                border-radius: 3px;
            }
            QSlider::handle:vertical {
                background: #fbbf24;
                height: 15px;
                width: 14px;
                margin: 0 -4px; 
                border-radius: 2px;
            }
            QSlider::sub-page:vertical {
                background: #3f3f46;
                border-radius: 3px;
            }
            QSlider::add-page:vertical {
                background: #27272a;
                border-radius: 3px;
            }
        """)
        self.layout.addWidget(self.slider, 0, Qt.AlignmentFlag.AlignHCenter)

class ChannelStrip(QFrame):
    def __init__(self, name="Track", role="Lead", parent=None):
        super().__init__(parent)
        self.setFixedWidth(70)
        self.setStyleSheet("""
            ChannelStrip {
                background-color: #121214; 
                border-right: 1px solid #27272a;
                border-radius: 4px;
            }
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4, 8, 4, 8)
        self.layout.setSpacing(6)
        
        # Role Indicator
        self.role_bar = QFrame()
        self.role_bar.setFixedHeight(2)
        role_cols = {"Lead": "#fbbf24", "Base": "#f97316", "Bell": "#fde047"}
        self.role_bar.setStyleSheet(f"background-color: {role_cols.get(role, '#71717a')};")
        self.layout.addWidget(self.role_bar)
        
        # Name
        self.name_label = QLabel(name.upper())
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-weight: 900; color: #a1a1aa; font-size: 9px; letter-spacing: 0.5px;")
        self.layout.addWidget(self.name_label)
        
        # Pan Knob (Styled Slider)
        self.pan_slider = QSlider(Qt.Orientation.Horizontal)
        self.pan_slider.setRange(-50, 50)
        self.pan_slider.setValue(0)
        self.pan_slider.setFixedHeight(12)
        self.pan_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 2px;
                background: #3f3f46;
            }
            QSlider::handle:horizontal {
                background: #71717a;
                width: 8px;
                height: 8px;
                margin: -3px 0;
                border-radius: 4px;
            }
        """)
        self.layout.addWidget(self.pan_slider)
        
        # Mute/Solo
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(1)
        
        self.btn_solo = QPushButton("S")
        self.btn_solo.setCheckable(True)
        self.btn_solo.setFixedSize(18, 18)
        self.btn_solo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_solo.setStyleSheet("""
            QPushButton { 
                background: #27272a; 
                color: #71717a; 
                border: 1px solid #3f3f46;
                border-radius: 2px; 
                font-size: 9px; 
                font-weight: bold; 
            }
            QPushButton:checked { 
                background: #fbbf24; 
                color: #09090b; 
                border-color: #fbbf24;
            }
        """)
        
        self.btn_mute = QPushButton("M")
        self.btn_mute.setCheckable(True)
        self.btn_mute.setFixedSize(18, 18)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mute.setStyleSheet("""
            QPushButton { 
                background: #27272a; 
                color: #71717a; 
                border: 1px solid #3f3f46;
                border-radius: 2px; 
                font-size: 9px; 
                font-weight: bold; 
            }
            QPushButton:checked { 
                background: #ef4444; 
                color: white; 
                border-color: #ef4444;
            }
        """)
        
        btn_layout.addWidget(self.btn_solo)
        btn_layout.addWidget(self.btn_mute)
        self.layout.addLayout(btn_layout)
        
        # Spacer
        self.layout.addStretch(1)
        
        # Fader
        self.fader = FaderWidget()
        self.layout.addWidget(self.fader, 5)
        
        # VU Meter Placeholder
        self.meter = QFrame()
        self.meter.setFixedHeight(4)
        self.meter.setStyleSheet("background: #09090b; border: 1px solid #27272a; border-radius: 1px;")
        self.layout.addWidget(self.meter)
