"""
Mixer Panel - Professional channel strips and mixer controls
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QScrollArea, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class ChannelStrip(QWidget):
    """Individual channel strip with fader and controls"""
    
    value_changed = pyqtSignal(str, str, float)  # player_id, param, value
    
    def __init__(self, player_id, player_name, icon="🥁"):
        super().__init__()
        self.setObjectName("channelStrip")
        
        self.player_id = player_id
        self.player_name = player_name
        self.icon = icon
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setSpacing(8)
        
        # Header
        icon_label = QLabel(self.icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 20px;")
        layout.addWidget(icon_label)
        
        name_label = QLabel(self.player_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-size: 10px; color: #aaa;")
        layout.addWidget(name_label)
        
        # Solo/Mute buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(4)
        
        self.solo_btn = QPushButton("S")
        self.solo_btn.setObjectName("soloBtn")
        self.solo_btn.setCheckable(True)
        self.solo_btn.setFixedSize(30, 25)
        btn_layout.addWidget(self.solo_btn)
        
        self.mute_btn = QPushButton("M")
        self.mute_btn.setObjectName("muteBtn")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setFixedSize(30, 25)
        btn_layout.addWidget(self.mute_btn)
       
        layout.addLayout(btn_layout)
        
        # Volume fader
        self.volume_slider = QSlider(Qt.Vertical)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setMinimumHeight(150)
        self.volume_slider.valueChanged.connect(lambda v: self.value_changed.emit(
            self.player_id, 'volume', v / 100.0
        ))
        layout.addWidget(self.volume_slider, alignment=Qt.AlignCenter)
        
        # Volume label
        self.vol_label = QLabel("70%")
        self.vol_label.setAlignment(Qt.AlignCenter)
        self.vol_label.setStyleSheet("font-size: 11px; color: #00d4ff; font-weight: bold;")
        self.volume_slider.valueChanged.connect(lambda v: self.vol_label.setText(f"{v}%"))
        layout.addWidget(self.vol_label)
        
        # Pan control
        pan_layout = QVBoxLayout()
        pan_label = QLabel("Pan")
        pan_label.setAlignment(Qt.AlignCenter)
        pan_label.setStyleSheet("font-size: 9px; color: #888;")
        
        self.pan_slider = QSlider(Qt.Horizontal)
        self.pan_slider.setRange(-50, 50)
        self.pan_slider.setValue(0)
        self.pan_slider.valueChanged.connect(lambda v: self.value_changed.emit(
            self.player_id, 'pan', v / 50.0
        ))
        
        self.pan_label = QLabel("C")
        self.pan_label.setAlignment(Qt.AlignCenter)
        self.pan_label.setStyleSheet("font-size: 9px; color: #aaa;")
        self.pan_slider.valueChanged.connect(self.update_pan_label)
        
        pan_layout.addWidget(pan_label)
        pan_layout.addWidget(self.pan_slider)
        pan_layout.addWidget(self.pan_label)
        layout.addLayout(pan_layout)
        
    def update_pan_label(self, value):
        """Update pan label text"""
        if value == 0:
            self.pan_label.setText("C")
        elif value < 0:
            self.pan_label.setText(f"L{abs(value)}")
        else:
            self.pan_label.setText(f"R{value}")


class MixerPanel(QWidget):
    """Right panel with all channel strips"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("mixerPanel")
        
        self.channel_strips = []
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("MIXER & FX")
        header.setObjectName("panelHeader")
        header.setFixedHeight(30)
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
        # Scrollable channel strips
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        strips_container = QWidget()
        strips_layout = QHBoxLayout(strips_container)
        strips_layout.setContentsMargins(10, 10, 10, 10)
        strips_layout.setSpacing(12)
        
        # Create default players
        players = [
            ('P1', 'Lead Player', '🥁'),
            ('P2', 'Rhythm Player', '🎯'),
            ('P3', 'Elathaalam 1', '🔔'),
            ('P4', 'Elathaalam 2', '🔔'),
        ]
        
        for player_id, name, icon in players:
            strip = ChannelStrip(player_id, name, icon)
            self.channel_strips.append(strip)
            strips_layout.addWidget(strip)
        
        strips_layout.addStretch()
        scroll.setWidget(strips_container)
        
        main_layout.addWidget(scroll, stretch=1)
        
        # Master section
        master_widget = self.create_master_section()
        main_layout.addWidget(master_widget)
        
    def create_master_section(self):
        """Create master output section"""
        widget = QWidget()
        widget.setObjectName("masterSection")
        widget.setFixedHeight(80)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        label = QLabel("MASTER OUT")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        layout.addWidget(label)
        
        return widget
