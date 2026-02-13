"""
Transport Controls - Playback controls
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon


class TransportControls(QWidget):
    """Transport bar with play/pause/stop controls"""
    
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setObjectName("transport")
        self.setFixedHeight(80)
        
        self.is_playing = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # Stop button
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setObjectName("transportBtn")
        self.stop_btn.setFixedSize(50, 50)
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)
        layout.addWidget(self.stop_btn)
        
        # Play/Pause button
        self.play_btn = QPushButton("▶")
        self.play_btn.setObjectName("playBtn")
        self.play_btn.setFixedSize(60, 60)
        self.play_btn.clicked.connect(self.on_play_pause)
        self.play_btn.setEnabled(False)
        layout.addWidget(self.play_btn)
        
        layout.addSpacing(20)
        
        # Time display
        self.time_label = QLabel("0:00 / 0:30")
        self.time_label.setStyleSheet("font-size: 16px; color: #fff; font-family: 'Consolas', monospace;")
        layout.addWidget(self.time_label)
        
        layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("○ No Audio")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.status_label)
        
    def on_play_pause(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.is_playing = False
            self.play_btn.setText("▶")
            self.pause_clicked.emit()
        else:
            self.is_playing = True
            self.play_btn.setText("⏸")
            self.play_clicked.emit()
            
    def on_stop(self):
        """Stop playback"""
        self.is_playing = False
        self.play_btn.setText("▶")
        self.stop_clicked.emit()
        
    def set_audio_loaded(self, loaded):
        """Enable/disable controls based on audio state"""
        self.play_btn.setEnabled(loaded)
        self.stop_btn.setEnabled(loaded)
        
        if loaded:
            self.status_label.setText("● Ready")
            self.status_label.setStyleSheet("color: #00d4ff; font-size: 12px;")
        else:
            self.status_label.setText("○ No Audio")
            self.status_label.setStyleSheet("color: #888; font-size: 12px;")
            
    def update_time(self, current, total):
        """Update time display"""
        current_min = int(current // 60)
        current_sec = int(current % 60)
        total_min = int(total // 60)
        total_sec = int(total % 60)
        
        self.time_label.setText(f"{current_min}:{current_sec:02d} / {total_min}:{total_sec:02d}")
