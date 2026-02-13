"""
Piano Roll Editor - MIDI Note Editing Widget
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont

class PianoRoll(QWidget):
    """
    Grid-based editor for MIDI notes.
    Vertical axis: Pitch (Keys)
    Horizontal axis: Time
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.notes = []  # List of {'note': 60, 'start': 0.0, 'duration': 1.0, 'velocity': 100}
        
        # View settings
        self.key_height = 20
        self.pixels_per_beat = 40
        self.scroll_y = 60 * self.key_height # Start around Middle C
        
        self.setStyleSheet("background-color: #222;")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), QColor("#1e2124"))
        
        # Draw Keys (Left side) and Grid
        self.draw_grid(painter)
        
        # Draw Notes
        self.draw_notes(painter)
        
    def draw_grid(self, painter):
        # Draw piano keys background rows
        keys_width = 40
        width = self.width()
        height = self.height()
        
        # Pitch range (0-127) - but we draw visible range
        # Simple implementation: Draw all for now, optimize later
        
        for note in range(127, -1, -1):
            y = (127 - note) * self.key_height
            
            # Determine if black or white key
            is_black = (note % 12) in [1, 3, 6, 8, 10]
            
            # Draw row background
            color = QColor("#2a2d32") if is_black else QColor("#36393f")
            painter.fillRect(keys_width, y, width - keys_width, self.key_height, color)
            
            # Draw key on left
            key_color = QColor("#000") if is_black else QColor("#fff")
            painter.fillRect(0, y, keys_width, self.key_height, key_color)
            painter.setPen(QColor("#888"))
            painter.drawRect(0, y, keys_width, self.key_height)
            
            # Label C notes
            if note % 12 == 0:
                painter.setPen(QColor("#888") if is_black else QColor("#000"))
                painter.drawText(2, y + 15, f"C{note//12 - 1}")
                
            # Draw vertical grid lines (beats)
            painter.setPen(QPen(QColor("#444"), 1, Qt.DotLine))
            for beat in range(0, 100): # Mock range
                x = keys_width + beat * self.pixels_per_beat
                painter.drawLine(x, 0, x, height)
                
    def draw_notes(self, painter):
        keys_width = 40
        
        for note_data in self.notes:
            pitch = note_data['note']
            start = note_data['start']
            duration = note_data['duration']
            
            y = (127 - pitch) * self.key_height
            x = keys_width + int(start * self.pixels_per_beat)
            w = int(duration * self.pixels_per_beat)
            
            rect = QRectF(x, y + 1, w, self.key_height - 2)
            
            # Draw note
            painter.fillRect(rect, QColor("#00d4ff"))
            painter.setPen(QColor("white"))
            painter.drawRect(rect)
            
    def add_note(self, note, start, duration, velocity):
        self.notes.append({
            'note': note,
            'start': start,
            'duration': duration,
            'velocity': velocity
        })
        self.update()

class PianoRollEditor(QWidget):
    """Container for PianoRoll with controls"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Tools Header
        header = QFrame()
        header.setFixedHeight(40)
        header.setStyleSheet("background: #333;")
        layout.addWidget(header)
        
        # Scroll Area for Piano Roll
        scroll = QScrollArea()
        self.piano_roll = PianoRoll()
        self.piano_roll.setFixedSize(2000, 128 * 20) # Fixed size for now
        scroll.setWidget(self.piano_roll)
        layout.addWidget(scroll)
        
    def set_notes(self, notes):
        self.piano_roll.notes = notes
        self.piano_roll.update()
