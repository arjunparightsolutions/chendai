import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QScrollArea, QSlider,
                               QMenu, QSizePolicy, QAbstractScrollArea)
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QMouseEvent, QCursor

# Theme Constants (Shared)
COLOR_BG_DARK = "#09090b"
COLOR_BG_PANEL = "#18181b" 
COLOR_BORDER = "#27272a"
COLOR_ACCENT = "#fbbf24"
COLOR_TEXT_PRIMARY = "#f4f4f5"
COLOR_TEXT_SECONDARY = "#a1a1aa"
COLOR_CLIP_BG = "#3f3f46"
COLOR_CLIP_WAVE = "#fbbf24"
COLOR_CLIP_BORDER = "#52525b"
COLOR_SELECTION = "rgba(251, 191, 36, 0.3)"

class AudioClip:
    def __init__(self, data: np.ndarray, sr: int, name: str = "Clip", start_time: float = 0.0, source_path: str = None):
        self.data = data
        self.sr = sr
        self.name = name
        self.start_time = start_time # in seconds
        self.source_path = source_path
        self.gain = 1.0
        self.pan = 0.0
        self.selected = False

    def to_dict(self):
        return {
            "name": self.name,
            "start_time": self.start_time,
            "source_path": self.source_path,
            "gain": self.gain,
            "pan": self.pan,
            "duration": self.duration
        }
        
    @property
    def duration(self):
        if self.data is None: return 0
        return len(self.data) / self.sr
        
    @property
    def end_time(self):
        return self.start_time + self.duration

class TrackHeader(QWidget):
    mute_toggled = Signal(bool)
    solo_toggled = Signal(bool)
    volume_changed = Signal(float)
    pan_changed = Signal(float)
    
    def __init__(self, name="Track"):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet(f"background-color: {COLOR_BG_PANEL}; border-right: 1px solid {COLOR_BORDER}; border-bottom: 1px solid {COLOR_BORDER};")
        self.setup_ui(name)
        
    def setup_ui(self, name):
        layout = QVBoxLayout(self)
        layout.setSpacing(5)
        
        # Name
        self.lbl_name = QLabel(name)
        self.lbl_name.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(self.lbl_name)
        
        # Controls Row 1
        r1 = QHBoxLayout()
        self.btn_mute = QPushButton("M")
        self.btn_mute.setCheckable(True)
        self.btn_mute.setFixedSize(25, 25)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mute.setStyleSheet(self.get_btn_style("#ef4444")) # Red
        self.btn_mute.toggled.connect(self.mute_toggled.emit)
        
        self.btn_solo = QPushButton("S")
        self.btn_solo.setCheckable(True)
        self.btn_solo.setFixedSize(25, 25)
        self.btn_solo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_solo.setStyleSheet(self.get_btn_style("#eab308")) # Yellow
        self.btn_solo.toggled.connect(self.solo_toggled.emit)
        
        r1.addWidget(self.btn_mute)
        r1.addWidget(self.btn_solo)
        r1.addStretch()
        layout.addLayout(r1)
        
        # Vol Slider
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 120) # 0-1.2x
        self.slider_vol.setValue(100)
        self.slider_vol.valueChanged.connect(lambda v: self.volume_changed.emit(v/100.0))
        self.slider_vol.setStyleSheet(self.get_slider_style())
        
        layout.addWidget(QLabel("Vol"))
        layout.addWidget(self.slider_vol)
        
        # Pan Slider
        self.slider_pan = QSlider(Qt.Orientation.Horizontal)
        self.slider_pan.setRange(-100, 100)
        self.slider_pan.setValue(0)
        self.slider_pan.valueChanged.connect(lambda v: self.pan_changed.emit(v/100.0))
        self.slider_pan.setStyleSheet(self.get_slider_style())
        
        layout.addWidget(QLabel("Pan"))
        layout.addWidget(self.slider_pan)
        
    def get_btn_style(self, active_color):
        return f"""
            QPushButton {{ background: #27272a; border: 1px solid #3f3f46; border-radius: 3px; color: #a1a1aa; font-weight: bold; }}
            QPushButton:checked {{ background: {active_color}; color: #000; border: none; }}
        """

    def get_slider_style(self):
        return f"""
            QSlider::groove:horizontal {{ height: 4px; background: {COLOR_BORDER}; border-radius: 2px; }}
            QSlider::handle:horizontal {{ width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; background: {COLOR_TEXT_SECONDARY}; }}
            QSlider::handle:horizontal:hover {{ background: {COLOR_ACCENT}; }}
        """

class TrackView(QWidget):
    clip_selected = Signal(AudioClip)
    
    def __init__(self, timeline_widget, pixels_per_sec=50):
        super().__init__()
        self.timeline_widget = timeline_widget # Reference to parent TimelineWidget
        self.clips = []
        self.pixels_per_sec = pixels_per_sec
        self.setFixedHeight(120)
        self.setCursor(Qt.CursorShape.IBeamCursor) # Audacity default
        self.setStyleSheet(f"background-color: {COLOR_BG_DARK}; border-bottom: 1px solid {COLOR_BORDER};")
        
        self.selected_clip = None
        self.dragging_clip = False
        self.selecting_range = False
        self.drag_start_pos = QPoint()
        self.drag_start_time = 0.0
        
    def add_clip(self, clip: AudioClip):
        self.clips.append(clip)
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Background Lines (Grid)
        painter.setPen(QPen(QColor("#27272a"), 1, Qt.PenStyle.DotLine))
        for x in range(0, self.width(), self.pixels_per_sec):
            painter.drawLine(x, 0, x, self.height())
            
        # Draw Clips
        for clip in self.clips:
            self.draw_clip(painter, clip)
            
        # Draw Range Selection
        if self.timeline_widget.selection_start is not None and self.timeline_widget.selection_end is not None:
            s_x = int(self.timeline_widget.selection_start * self.pixels_per_sec)
            e_x = int(self.timeline_widget.selection_end * self.pixels_per_sec)
            w = e_x - s_x
            if w < 0:
                s_x = e_x
                w = -w
            
            if w > 0:
                painter.fillRect(QRect(s_x, 0, w, self.height()), QColor(255, 255, 255, 30)) # Transparent White
                painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
                painter.drawLine(s_x, 0, s_x, self.height())
                painter.drawLine(s_x + w, 0, s_x + w, self.height())

        # Draw Playhead
        ph_time = self.timeline_widget.playhead_pos
        ph_x = int(ph_time * self.pixels_per_sec)
        painter.setPen(QPen(QColor("#ef4444"), 2)) # Red Playhead
        painter.drawLine(ph_x, 0, ph_x, self.height())
        # Draw small triangle head
        painter.setBrush(QBrush(QColor("#ef4444")))
        painter.drawPolygon([QPoint(ph_x, 0), QPoint(ph_x-5, 5), QPoint(ph_x+5, 5)])
        
        painter.end()
            
    def draw_clip(self, painter, clip):
        x = int(clip.start_time * self.pixels_per_sec)
        w = int(clip.duration * self.pixels_per_sec)
        w = max(w, 2)
        h = self.height()
        rect = QRect(x, 0, w, h)
        
        # Check explicit clipping
        if x > self.width() or x + w < 0:
            return

        # Background
        bg_color = QColor(COLOR_CLIP_BG)
        if clip.selected:
            bg_color = bg_color.lighter(130)
            
        painter.fillRect(rect, bg_color)
        painter.setPen(QPen(QColor(COLOR_CLIP_BORDER), 1))
        painter.drawRect(rect)
        
        # Name
        painter.setPen(QPen(QColor(COLOR_TEXT_PRIMARY), 1))
        if w > 20:
            painter.drawText(rect.adjusted(5, 5, -5, -5), Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, clip.name)
        
        # Waveform Visualization
        if w < 5: return
        
        painter.setPen(QPen(QColor(COLOR_CLIP_WAVE), 1))
        cy = int(h / 2)
        
        if clip.data is None: return
        
        samples = clip.data
        if samples.ndim > 1: samples = np.mean(samples, axis=1) # Mix to mono
        
        n_samples = len(samples)
        if n_samples == 0: return
        
        step = max(1, n_samples // w)
        display_data = samples[::step]
        limit = min(len(display_data), w)
        
        # Draw Center Line
        painter.drawLine(x, cy, x + w, cy)
        
        scale_h = (h / 2) * 0.9
        
        # Draw Waveform Points
        # Pre-calculate to avoid loop overhead if possible, but loop is fine for Python
        for i in range(limit):
            val = display_data[i]
            if np.isnan(val) or np.isinf(val): continue
            
            amp = int(val * scale_h)
            x_pos = int(x + i)
            painter.drawLine(x_pos, cy - amp, x_pos, cy + amp)


    def mousePressEvent(self, event):
        pos = event.position().toPoint()
        click_time = pos.x() / self.pixels_per_sec
        
        # CTRL modifier for Clip Interaction
        modifiers = event.modifiers()
        is_ctrl = modifiers & Qt.KeyboardModifier.ControlModifier
        
        clicked_clip = None
        for clip in reversed(self.clips):
            x = int(clip.start_time * self.pixels_per_sec)
            w = int(clip.duration * self.pixels_per_sec)
            rect = QRect(x, 0, w, self.height())
            if rect.contains(pos):
                clicked_clip = clip
                break

        if event.button() == Qt.MouseButton.RightButton:
            # Context Menu (logic remains same, just ensure selection is stored)
            if clicked_clip:
                self.selected_clip = clicked_clip
                clicked_clip.selected = True
                self.clip_selected.emit(clicked_clip)
                self.update()
            
            menu = QMenu(self)
            menu.setStyleSheet(f"background: {COLOR_BG_PANEL}; color: {COLOR_TEXT_PRIMARY}; border: 1px solid {COLOR_BORDER};")
            
            # Add Actions
            if clicked_clip:
                menu.addAction("Split at Cursor").triggered.connect(lambda: self.split_clip(clicked_clip, pos.x()))
                menu.addAction("Delete Clip").triggered.connect(lambda: self.delete_clip(clicked_clip))
                menu.addSeparator()
            
            # Selection Actions
            if self.timeline_widget.selection_start != self.timeline_widget.selection_end:
                menu.addAction("Cut Selection").setEnabled(False) 
                menu.addAction("Copy Selection").setEnabled(False) 
                menu.addAction("Clear Selection").triggered.connect(self.clear_selection_range)

            menu.exec(event.globalPosition().toPoint())
            return

        # Playhead update on click
        self.timeline_widget.playhead_pos = click_time
        self.timeline_widget.update_all_views()

        # Deselect all first (unless Ctrl?)
        if not is_ctrl:
             for c in self.clips: c.selected = False
             self.selected_clip = None

        if clicked_clip:
            # Select the clip
            clicked_clip.selected = True
            self.selected_clip = clicked_clip
            self.clip_selected.emit(clicked_clip)
            
            if is_ctrl:
                # Move Mode explicit
                self.drag_start_pos = pos
                self.drag_start_time = clicked_clip.start_time
                self.dragging_clip = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            else:
                 # Default to potential move or just selection?
                 # Let's say click = select. Drag = move if on clip? 
                 # Audacity: Drag inside clip = Select Range. Drag Title = Move.
                 # We don't have titles separate. 
                 # Let's keep: Click = Select. Drag = Range Selection (Audacity style).
                 self.selecting_range = True
                 self.timeline_widget.selection_start = click_time
                 self.timeline_widget.selection_end = click_time
                 self.setCursor(Qt.CursorShape.IBeamCursor)
                 
        else:
            # Clicked empty space
            self.selecting_range = True
            self.timeline_widget.selection_start = click_time
            self.timeline_widget.selection_end = click_time
            self.setCursor(Qt.CursorShape.IBeamCursor)
            self.timeline_widget.update_all_views()
            
        self.update()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        curr_time = pos.x() / self.pixels_per_sec
        
        if self.dragging_clip and self.selected_clip:
            delta_px = pos.x() - self.drag_start_pos.x()
            delta_sec = delta_px / self.pixels_per_sec
            
            new_time = self.drag_start_time + delta_sec
            if new_time < 0: new_time = 0
            
            self.selected_clip.start_time = new_time
            self.update()
            
        elif self.selecting_range:
            self.timeline_widget.selection_end = curr_time
            self.timeline_widget.update_all_views()



    def split_clip(self, clip, split_px):
        split_time = split_px / self.pixels_per_sec
        
        # Verify split point is within clip
        if not (clip.start_time < split_time < clip.end_time):
            return

        # Calculate local split point
        local_split_sec = split_time - clip.start_time
        split_sample = int(local_split_sec * clip.sample_rate)
        
        # Verify split sample is valid
        if split_sample <= 0 or split_sample >= len(clip.data):
            return

        # Split data
        data1 = clip.data[:split_sample]
        data2 = clip.data[split_sample:]
        
        # Update original clip
        clip.data = data1
        clip.duration = len(data1) / clip.sample_rate
        
        # Create new clip
        new_clip = AudioClip(data2, clip.sample_rate, clip.name)
        new_clip.start_time = split_time
        
        self.clips.append(new_clip)
        self.update()
        
    def delete_clip(self, clip):
        if clip in self.clips:
            self.clips.remove(clip)
            if self.selected_clip == clip:
                self.selected_clip = None
            self.update()
            
    def mouseReleaseEvent(self, event):
        self.dragging_clip = False
        self.selecting_range = False
        
        if self.selected_clip:
            self.setCursor(Qt.CursorShape.OpenHandCursor if event.modifiers() & Qt.KeyboardModifier.ControlModifier else Qt.CursorShape.IBeamCursor)
        else:
            self.setCursor(Qt.CursorShape.IBeamCursor)

    def clear_selection_range(self):
        self.timeline_widget.selection_start = None
        self.timeline_widget.selection_end = None
        self.timeline_widget.update_all_views()


class AudioTrack(QWidget):
    def __init__(self, timeline_widget, name="Track"):
        super().__init__()
        self.setFixedHeight(120)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self.header = TrackHeader(name)
        self.view = TrackView(timeline_widget)
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.view)
        
    def add_clip(self, clip: AudioClip):
        self.view.add_clip(clip)

    def to_dict(self):
        return {
            "name": self.header.lbl_name.text(),
            "volume": self.header.slider_vol.value() / 100.0,
            "pan": self.header.slider_pan.value() / 100.0,
            "mute": self.header.btn_mute.isChecked(),
            "solo": self.header.btn_solo.isChecked(),
            "clips": [c.to_dict() for c in self.view.clips]
        }

class TimelineWidget(QWidget):
    def __init__(self):
        super().__init__()
        # State
        self.playhead_pos = 0.0
        self.selection_start = None
        self.selection_end = None
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Scroll Area for tracks
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet(f"border: none; background-color: {COLOR_BG_DARK};")
        
        self.track_container = QWidget()
        self.track_container.setStyleSheet(f"background-color: {COLOR_BG_DARK};")
        self.track_layout = QVBoxLayout(self.track_container)
        self.track_layout.setContentsMargins(0, 0, 0, 0)
        self.track_layout.setSpacing(1) # Gap between tracks color
        self.track_layout.addStretch()
        
        self.scroll.setWidget(self.track_container)
        self.layout.addWidget(self.scroll)
        
        self.tracks = []
        
    def add_track(self, name="New Track"):
        # Pass self as timeline_widget
        track = AudioTrack(self, name)
        # Insert before stretch
        idx = self.track_layout.count() - 1
        self.track_layout.insertWidget(idx, track)
        self.tracks.append(track)
        return track
        
    def to_dict(self):
        return {
             "type": "timeline",
             "tracks": [t.to_dict() for t in self.tracks]
        }
        
    def clear(self):
        for track in self.tracks:
            track.deleteLater()
        self.tracks = []
        self.playhead_pos = 0.0
        self.selection_start = None
        self.selection_end = None
        
    def update_all_views(self):
        for track in self.tracks:
            track.view.update()
