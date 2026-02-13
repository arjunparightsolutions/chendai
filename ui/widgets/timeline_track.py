"""
Timeline Track - Graphics View based track implementation
"""

from PyQt5.QtWidgets import (
    QGraphicsView, QGraphicsScene, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

from ui.widgets.clip_item import ClipItem

class TimelineTrack(QGraphicsView):
    """
    Track widget using QGraphicsView for high-performance 
    rendering of interactive clips.
    """
    
    clip_selected = pyqtSignal(object)
    double_clicked = pyqtSignal()
    
    def __init__(self, track_data, parent=None):
        super().__init__(parent)
        self.track_data = track_data
        self.setFixedHeight(100)
        
        # Setup Scene
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 5000, 100) # Fixed length for now
        self.setScene(self.scene)
        
        # Visual settings
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFrameShape(QFrame.NoFrame)
        self.setBackgroundBrush(QBrush(QColor("#1e2124")))
        
        # Grid settings
        self.pixels_per_sec = 20
        
        # Clips
        self.clips = []
        if 'notes' in track_data:
             # It's a MIDI track, create a clip for it
             self.add_clip({
                 'name': 'MIDI Clip',
                 'start': 0,
                 'duration': 10, # Mock duration
                 'color': track_data.get('color', '#00ff55')
             })
             
    def add_clip(self, clip_data):
        """Add a clip to the track"""
        clip = ClipItem(clip_data, pixels_per_sec=self.pixels_per_sec)
        self.scene.addItem(clip)
        self.clips.append(clip)
        
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        
        # Draw grid lines
        painter.setPen(QPen(QColor("#2f3136")))
        
        # Draw every second
        left = int(rect.left())
        right = int(rect.right())
        
        # Round to nearest grid interval
        start_x = (left // self.pixels_per_sec) * self.pixels_per_sec
        
        for x in range(start_x, right, self.pixels_per_sec):
            painter.drawLine(x, 0, x, self.height())
            
    def set_scale(self, scale):
        """Update view scale (zoom)"""
        # Transform the view matrix
        transform = self.transform()
        transform.reset()
        transform.scale(scale, 1.0) # Only scale X axis
        self.setTransform(transform)
        
    def mousePressEvent(self, event):
        # Check for Split Tool
        if hasattr(self.parent(), 'current_tool') and self.parent().current_tool == 'split':
            # Get position in scene coordinates
            scene_pos = self.mapToScene(event.pos())
            click_x = scene_pos.x()
            
            # Find clip under mouse
            item = self.scene.itemAt(scene_pos, self.transform())
            
            if isinstance(item, ClipItem):
                # Calculate split time relative to clip start
                clip_start_x = item.pos().x()
                split_point_x = click_x - clip_start_x
                
                # Minimum clip width check (e.g. 10px)
                if 10 < split_point_x < item.width - 10:
                    self.perform_split(item, split_point_x)
                    return # Handled
            
        super().mousePressEvent(event)
        
    def perform_split(self, clip_item, split_x):
        """Split a clip into two at split_x (local coordinates)"""
        original_data = clip_item.clip_data
        original_duration = original_data['duration']
        original_start = original_data['start']
        
        # Calculate new durations
        split_time = split_x / self.pixels_per_sec
        new_duration1 = split_time
        new_duration2 = original_duration - split_time
        
        # 1. Update original clip
        clip_item.width = split_x
        clip_item.prepareGeometryChange()
        clip_item.clip_data['duration'] = new_duration1
        # Re-draw to update width
        clip_item.update()
        
        # 2. Create new clip
        new_data = original_data.copy()
        new_data['start'] = original_start + split_time
        new_data['duration'] = new_duration2
        new_data['name'] = original_data.get('name', 'Clip') # + " (Split)"
        
        self.add_clip(new_data)
        
        print(f"✂️ Split clip at {split_time:.2f}s")

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)
