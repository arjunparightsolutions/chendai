"""
Rotary Knob - Custom Painted Widget for DAW-style controls
"""

from PyQt5.QtWidgets import QWidget, QDial
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient, QFont

class RotaryKnob(QWidget):
    """
    Custom rotary knob with gold/modern styling.
    Replaces standard QDial/QSpinBox for better aesthetics.
    """
    
    valueChanged = pyqtSignal(float)
    
    def __init__(self, parent=None, min_val=0.0, max_val=100.0, value=50.0, suffix=""):
        super().__init__(parent)
        self.setFixedSize(60, 80) # Includes label space
        
        self.min_val = min_val
        self.max_val = max_val
        self._value = value
        self.suffix = suffix
        
        self.is_dragging = False
        self.last_y = 0
        self.sensitivity = 0.5
        
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, val):
        self._value = max(self.min_val, min(self.max_val, val))
        self.update()
        self.valueChanged.emit(self._value)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_y = event.y()
            
    def mouseMoveEvent(self, event):
        if self.is_dragging:
            delta = self.last_y - event.y()
            range_span = self.max_val - self.min_val
            change = delta * self.sensitivity * (range_span / 100.0)
            
            self.value += change
            self.last_y = event.y()
            
    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dimensions
        w, h = self.width(), self.height()
        knob_size = min(w, h - 20)
        knob_rect = QRectF((w - knob_size)/2, 0, knob_size, knob_size)
        
        # 1. Background (Dark Circle)
        grad = QRadialGradient(knob_rect.center(), knob_size/2)
        grad.setColorAt(0, QColor("#333"))
        grad.setColorAt(1, QColor("#111"))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(knob_rect)
        
        # 2. Indicator Arc
        painter.setPen(QPen(QColor("#111"), 6))
        start_angle = 225 * 16
        span_angle = -270 * 16
        painter.drawArc(knob_rect.adjusted(4, 4, -4, -4), start_angle, span_angle)
        
        # Active Arc (Gold)
        pct = (self._value - self.min_val) / (self.max_val - self.min_val)
        active_span = -270 * pct * 16
        
        active_pen = QPen(QColor("#ffd700"), 4) # Gold
        active_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(active_pen)
        painter.drawArc(knob_rect.adjusted(4, 4, -4, -4), start_angle, int(active_span))
        
        # 3. Pointer Line
        painter.save()
        painter.translate(knob_rect.center())
        angle_deg = 225 - (270 * pct)
        painter.rotate(-90 - angle_deg)
        
        painter.setPen(QPen(QColor("#ddd"), 2))
        painter.drawLine(0, 0, int(knob_size/2 - 8), 0)
        painter.restore()
        
        # 4. Text Label
        painter.setPen(QColor("#aaa"))
        painter.setFont(QFont("Arial", 8))
        text = f"{int(self._value)}{self.suffix}"
        painter.drawText(QRectF(0, h-20, w, 20), Qt.AlignCenter, text)
