from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QSplitter,
    QFrame, QLabel, QPushButton, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from ui.widgets.timeline_track import TimelineTrack
from ui.widgets.track_header import TrackHeader

class TimelineEditor(QWidget):
    """
    Main timeline editor widget managing multiple tracks.
    Replaces the simple WaveformWidget.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tracks = []
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Time Ruler (Placeholder)
        self.ruler = QLabel("Time Ruler (0:00 - 5:00)")
        self.ruler.setFixedHeight(30)
        self.ruler.setStyleSheet("background: #1e2124; color: #888; padding-left: 200px; border-bottom: 1px solid #444;")
        main_layout.addWidget(self.ruler)
        
        # Tools Bar (Zoom, Snap)
        tools_layout = QHBoxLayout()
        tools_layout.setContentsMargins(5, 0, 5, 0)
        
        zoom_out_btn = QPushButton("−")
        zoom_out_btn.setFixedSize(24, 24)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.zoom_level_lbl = QLabel("100%")
        self.zoom_level_lbl.setFixedWidth(40)
        self.zoom_level_lbl.setAlignment(Qt.AlignCenter)
        self.zoom_level_lbl.setStyleSheet("color: #888;")
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(24, 24)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        self.snap_check = QCheckBox("Snap")
        self.snap_check.setChecked(True)
        self.snap_check.setStyleSheet("color: #888;")
        
        tools_layout.addWidget(QLabel("Zoom:"))
        tools_layout.addWidget(zoom_out_btn)
        tools_layout.addWidget(self.zoom_level_lbl)
        tools_layout.addWidget(zoom_in_btn)
        tools_layout.addSpacing(15)
        tools_layout.addWidget(self.snap_check)
        
        # Split Tool
        tools_layout.addSpacing(15)
        self.split_btn = QPushButton("✂️ Split")
        self.split_btn.setCheckable(True)
        self.split_btn.clicked.connect(self.toggle_split_mode)
        self.split_btn.setStyleSheet("""
            QPushButton { background: #444; color: #aaa; border: none; padding: 5px; }
            QPushButton:checked { background: #00d4ff; color: black; }
        """)
        tools_layout.addWidget(self.split_btn)
        
        tools_layout.addStretch()
        
        main_layout.addLayout(tools_layout)
        
        # Scroll Area for tracks
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setStyleSheet("background: #111;")
        
        # Container for tracks
        self.track_container = QWidget()
        self.track_layout = QVBoxLayout(self.track_container)
        self.track_layout.setContentsMargins(0, 0, 0, 0)
        self.track_layout.setSpacing(1)
        self.track_layout.addStretch()  # Push tracks to top
        
        self.scroll.setWidget(self.track_container)
        main_layout.addWidget(self.scroll)
        
        self.scale_factor = 1.0
        self.selected_track_index = -1
        self.current_tool = 'pointer' # pointer, split
        
    def toggle_split_mode(self, checked):
        self.current_tool = 'split' if checked else 'pointer'
        # Update cursor or visual feedback if possible
        if self.current_tool == 'split':
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
    def zoom_in(self):
        self.scale_factor *= 1.2
        self.update_zoom()
        
    def zoom_out(self):
        self.scale_factor /= 1.2
        self.update_zoom()
        
    def update_zoom(self):
        self.zoom_level_lbl.setText(f"{int(self.scale_factor * 100)}%")
        # Update tracks
        for track in self.tracks:
            # TODO: Implement set_scale in TimelineTrack
            if hasattr(track['timeline'], 'set_scale'):
                track['timeline'].set_scale(self.scale_factor)
        
    def add_track(self, track_data):
        """Add a new track to the timeline"""
        # Create container for header + track
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(0)
        
        # Track Header
        header = TrackHeader(track_data)
        header.setFixedWidth(200)
        
        # Track Timeline
        timeline = TimelineTrack(track_data, parent=self)
        timeline.double_clicked.connect(lambda: self.open_piano_roll(track_data))
        
        # Connect FX button
        header.fx_clicked.connect(lambda: self.open_fx_rack(len(self.tracks))) # Capture current index
        # Note: lambda capture value at definition time if used like this? 
        # Actually in loop variable capture is problem. Here len(self.tracks) is evaluated at call time? 
        # No, default arg trick needed or partial.
        # But wait, add_track is called one by one. len(self.tracks) is effectively the current index we are about to append.
        # So passing current_index = len(self.tracks) as default arg works.
        
        current_idx = len(self.tracks)
        header.fx_clicked.connect(lambda: self.open_fx_rack(current_idx))
        
        # Connect selection
        index = len(self.tracks)
        # Using a closure to capture index is tricky, better use custom signal if possible
        # For now, simple mouse press logic in header
        
        row_layout.addWidget(header)
        row_layout.addWidget(timeline, stretch=1)
        
        # Add to main layout (before the stretch)
        count = self.track_layout.count()
        self.track_layout.insertWidget(count - 1, row_widget)
        
        self.tracks.append({
            'widget': row_widget,
            'header': header,
            'timeline': timeline,
            'data': track_data
        })
        
        # Auto-select new track
        self.select_track(len(self.tracks) - 1)
        
    def select_track(self, index):
        """Select a track by index"""
        if 0 <= index < len(self.tracks):
            # Deselect previous
            if 0 <= self.selected_track_index < len(self.tracks):
                self.tracks[self.selected_track_index]['header'].setStyleSheet("")
                
            self.selected_track_index = index
            # Highlight new (simple border for now)
            self.tracks[index]['header'].setStyleSheet("border: 2px solid #00d4ff;")
            print(f"Selected Track {index}")
        
    def open_piano_roll(self, track_data):
        """Open Piano Roll for the track"""
        from ui.widgets.piano_roll import PianoRollEditor
        # Keep reference to prevent garbage collection if not modal
        self.piano_roll = PianoRollEditor() 
        self.piano_roll.show()
        
    def open_fx_rack(self, track_index):
        """Open FX Rack for the track"""
        if track_index < 0 or track_index >= len(self.tracks):
            return
            
        track_data = self.tracks[track_index]['data']
        track_name = track_data.get('name', f'Track {track_index+1}')
        
        # Get plugin manager from parent (MainWindow)
        main_window = self.window()
        if hasattr(main_window, 'plugin_manager'):
            plugins = main_window.plugin_manager.loaded_plugins.get(track_index, [])
            
            from ui.dialogs.fx_rack import FXRackDialog
            dialog = FXRackDialog(track_name, plugins, parent=self)
            dialog.exec_()
        else:
            print("❌ Plugin Manager not found")
        
    def clear_tracks(self):
        """Remove all tracks"""
        for track in self.tracks:
            track['widget'].deleteLater()
        self.tracks = []
        
    def load_project_tracks(self, tracks_data):
        """Load tracks from project data"""
        self.clear_tracks()
        for track in tracks_data:
            self.add_track(track)
            
        # If empty, add default tracks
        if not tracks_data:
            self.add_track({'name': 'Audio 1', 'color': '#00d4ff'})
            self.add_track({'name': 'Audio 2', 'color': '#ff0055'})
            self.add_track({'name': 'Midi 1', 'color': '#00ff55'})
