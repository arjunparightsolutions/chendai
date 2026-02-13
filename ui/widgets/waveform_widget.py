"""
Waveform Widget - Audio visualization and timeline
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen


class WaveformWidget(QWidget):
    """Custom waveform display widget"""
    
    def __init__(self):
        super().__init__()
        self.setObjectName("waveformWidget")
        self.setMinimumHeight(300)
        
        self.audio_data = None
        self.waveforms = []  # List of (player_name, waveform_data) tuples
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Empty state
        self.empty_label = QLabel("Generate a melam to see waveforms")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            color: #666;
            font-size: 14px;
            padding: 100px;
        """)
        layout.addWidget(self.empty_label)
        
    def set_audio_data(self, audio_path, players):
        """Set audio data and player info"""
        self.audio_path = audio_path
        self.waveforms = []
        
        # TODO: Load actual waveform data
        # For now, create placeholder
        for player in players:
            self.waveforms.append((player['name'], []))
        
        self.empty_label.hide()
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for waveform display"""
        super().paintEvent(event)
        
        if not self.waveforms:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw track lanes
        width = self.width()
        height = self.height()
        track_height = height / max(len(self.waveforms), 1)
        
        for i, (player_name, waveform) in enumerate(self.waveforms):
            y_offset = i * track_height
            
            # Draw track background
            if i % 2 == 0:
                painter.fillRect(0, int(y_offset), width, int(track_height), QColor(30, 30, 50, 100))
            
            # Draw track label
            painter.setPen(QColor(200, 200, 200))
            painter.drawText(10, int(y_offset + 20), player_name)
            
            # Draw waveform placeholder (TODO: actual waveform rendering)
            painter.setPen(QPen(QColor(0, 212, 255), 2))
            mid_y = y_offset + track_height / 2
            painter.drawLine(50, int(mid_y), width - 50, int(mid_y))
        
        painter.end()
