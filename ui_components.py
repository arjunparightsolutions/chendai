from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsLineItem
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QPen, QColor, QPainter

class TimelineView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Performance settings
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setStyleSheet("background-color: #09090b; border: none;")
        
        self.scene.setBackgroundBrush(QColor("#09090b"))
        
        # Test Data
        self.draw_grid()
        self.draw_test_pattern()

    def draw_grid(self):
        width = 2000
        height = 600
        self.scene.setSceneRect(0, 0, width, height)
        
        # Grid Color
        grid_color = QColor("#27272a")
        pen = QPen(grid_color) 
        pen.setWidth(1)
        
        # Vertical grid lines (every 100px)
        for x in range(0, width, 100):
            line = self.scene.addLine(x, 0, x, height, pen)
            
        # Horizontal track separators (every 80px)
        sep_pen = QPen(grid_color)
        sep_pen.setWidth(1)
        for y in range(0, height, 80):
            self.scene.addLine(0, y, width, y, sep_pen)

    def draw_test_pattern(self):
        # Draw some "notes"
        colors = {
            "Lead": QColor("#fbbf24"),   # Gold
            "Base": QColor("#f97316"),   # Orange
            "Bell": QColor("#fde047"),   # Yellow
        }
        
        tracks = ["Lead", "Base", "Base", "Bell"]
        
        for t_idx, track in enumerate(tracks):
            y_base = t_idx * 80 + 20
            color = colors.get(track, Qt.GlobalColor.white)
            
            # Gradient effect for notes
            from PySide6.QtGui import QLinearGradient
            grad = QLinearGradient(0, y_base, 0, y_base + 40)
            grad.setColorAt(0, color.lighter(120))
            grad.setColorAt(1, color)
            
            brush = QBrush(grad)
            
            for i in range(10):
                x = i * 100 + (t_idx * 20)
                width = 80 if i % 2 == 0 else 40
                
                # Add rounded rect
                path = self._rounded_rect(x, y_base, width, 40, 4)
                item = self.scene.addPath(path, QPen(Qt.PenStyle.NoPen), brush)
                
                # Highlight effect
                item.setOpacity(0.9)

    def _rounded_rect(self, x, y, w, h, r):
        from PySide6.QtGui import QPainterPath
        path = QPainterPath()
        path.addRoundedRect(x, y, w, h, r, r)
        return path

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio) # Optional: auto-fit
