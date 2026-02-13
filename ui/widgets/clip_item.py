"""
Clip - Audio/MIDI Clip Graphic Item
"""

from PyQt5.QtWidgets import QGraphicsItem, QMenu, QAction
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont

class ClipItem(QGraphicsItem):
    """
    Interactive GraphicsItem representing a clip on the timeline.
    Supports selection, moving, and resizing.
    """
    
    def __init__(self, clip_data, track_height=100, pixels_per_sec=20):
        super().__init__()
        self.clip_data = clip_data
        self.track_height = track_height
        self.pixels_per_sec = pixels_per_sec
        
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        
        self.setAcceptHoverEvents(True)
        
        # Initial position
        x = self.clip_data['start'] * self.pixels_per_sec
        self.setPos(x, 0)
        
        # Dimensions
        self.width = self.clip_data['duration'] * self.pixels_per_sec
        self.height = self.track_height - 2
        
        # State
        self.is_resizing = False
        self.resize_edge = None # 'left' or 'right'
        
    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)
        
    def paint(self, painter, option, widget):
        # Background
        color = QColor(self.clip_data.get('color', '#00d4ff'))
        if self.isSelected():
            painter.setBrush(color.lighter(130))
            painter.setPen(QPen(Qt.white, 2))
        else:
            painter.setBrush(color.darker(110))
            painter.setPen(QPen(Qt.black, 1))
            
        painter.drawRoundedRect(self.boundingRect(), 4, 4)
        
        # Name
        painter.setPen(Qt.white)
        painter.drawText(QRectF(5, 5, self.width-10, 20), Qt.AlignLeft, self.clip_data.get('name', 'Clip'))
        
        # Resize handles (visual hint)
        if self.isSelected() or self.isUnderMouse():
            painter.setPen(QPen(Qt.white, 4))
            # Left handle
            painter.drawLine(2, 10, 2, self.height-10)
            # Right handle
            painter.drawLine(self.width-2, 10, self.width-2, self.height-10)
            
    def hoverMoveEvent(self, event):
        # Change cursor near edges
        pos = event.pos()
        if pos.x() < 10 or pos.x() > self.width - 10:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        super().hoverMoveEvent(event)
        
    def mousePressEvent(self, event):
        pos = event.pos()
        if pos.x() < 10:
            self.is_resizing = True
            self.resize_edge = 'left'
        elif pos.x() > self.width - 10:
            self.is_resizing = True
            self.resize_edge = 'right'
        else:
            self.is_resizing = False
            
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if self.is_resizing:
            pos = event.pos()
            scene_pos = event.scenePos()
            
            if self.resize_edge == 'right':
                # Resize from right: Change width
                new_width = pos.x()
                if new_width >= 10: # Minimum width
                    self.prepareGeometryChange()
                    self.width = new_width
                    # Update duration in data
                    self.clip_data['duration'] = self.width / self.pixels_per_sec
                    
            elif self.resize_edge == 'left':
                # Resize from left: Change x and width
                delta = pos.x()
                new_width = self.width - delta
                
                if new_width >= 10:
                    self.prepareGeometryChange()
                    self.width = new_width
                    # Move item to right by delta
                    self.setPos(self.pos().x() + delta, self.pos().y())
                    
                    # Update data
                    self.clip_data['start'] = self.pos().x() / self.pixels_per_sec
                    self.clip_data['duration'] = self.width / self.pixels_per_sec
                    
                    # Since we moved the item's local coordinates, we need to adjust visual/logic?
                    # Actually standard QGraphicsItem moving is easier if we just mapToParent.
                    # But here we are inside item coordinates.
                    # The setPos moves the origin.
                    
        else:
            super().mouseMoveEvent(event)
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            # Snap to grid logic or bounds check would go here
            new_pos = value
            # Update data
            self.clip_data['start'] = new_pos.x() / self.pixels_per_sec
            
        return super().itemChange(change, value)
        
    def mouseReleaseEvent(self, event):
        self.is_resizing = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
        super().mouseReleaseEvent(event)
