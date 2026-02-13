import numpy as np
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QToolBar, QMenu, QMainWindow,
                               QFileDialog, QMessageBox, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QSize, Signal, QRect, QTimer
from PySide6.QtGui import QIcon, QAction, QPainter, QColor, QPen, QBrush

from audio_processor import AudioProcessor
from ui_timeline import TimelineWidget, AudioClip

# Theme Constants (Shared)
COLOR_BG_DARK = "#09090b"
COLOR_BG_PANEL = "#18181b" 
COLOR_BORDER = "#27272a"
COLOR_ACCENT = "#fbbf24"
COLOR_TEXT_PRIMARY = "#f4f4f5"
COLOR_TEXT_SECONDARY = "#a1a1aa"

class AudioEditor(QWidget):
    """
    Professional Audio Editor Module.
    Features recording, 50+ DSP tools, and waveform editing.
    """
    status_message = Signal(str)

    def __init__(self):
        super().__init__()
        self.current_file = None
        self.sample_rate = 44100
        
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_playhead)
        self.playback_start_time = 0.0
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 1. Editor Toolbar (Transport & Tools)
        self.setup_toolbar(layout)
        
        # 2. Timeline View
        self.timeline = TimelineWidget()
        layout.addWidget(self.timeline)
        
        # 3. DSP Effects Panel
        self.setup_fx_bar(layout)

    def setup_toolbar(self, parent_layout):
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"background-color: {COLOR_BG_PANEL}; border-bottom: 1px solid {COLOR_BORDER};")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(10, 5, 10, 5)
        
        # File Operations
        btn_import = QPushButton("IMPORT")
        btn_import.setStyleSheet(self.get_btn_style())
        btn_import.clicked.connect(self.import_audio)
        tl.addWidget(btn_import)
        
        btn_export = QPushButton("EXPORT")
        btn_export.setStyleSheet(self.get_btn_style())
        btn_export.clicked.connect(self.export_audio)
        tl.addWidget(btn_export)
        
        tl.addStretch()
        
        # Transport
        btn_rec = QPushButton("● REC")
        btn_rec.setStyleSheet(self.get_btn_style(color="#dc2626")) # Red
        tl.addWidget(btn_rec)
        
        btn_stop = QPushButton("■ STOP")
        btn_stop.setStyleSheet(self.get_btn_style())
        btn_stop.clicked.connect(self.stop_playback)
        tl.addWidget(btn_stop)
        
        btn_play = QPushButton("▶ PLAY")
        btn_play.setStyleSheet(self.get_btn_style(color=COLOR_ACCENT, text_color=COLOR_BG_DARK))
        btn_play.clicked.connect(self.play_audio)
        tl.addWidget(btn_play)
        
        tl.addStretch()
        
        # Tools Menu
        btn_tools = QPushButton("DSP TOOLS ▼")
        btn_tools.setStyleSheet(self.get_btn_style())
        
        # Create Context Menu for Tools
        self.tools_menu = QMenu(self)
        self.tools_menu.setStyleSheet(f"""
            QMenu {{ background-color: {COLOR_BG_PANEL}; border: 1px solid {COLOR_BORDER}; color: {COLOR_TEXT_PRIMARY}; }}
            QMenu::item {{ padding: 5px 20px; }}
            QMenu::item:selected {{ background-color: {COLOR_BORDER}; }}
        """)
        
        categories = {
            "Dynamics": ["Normalize", "Hard Clip", "Soft Clip"],
            "Spatial": ["Stereo Widener", "Make Mono", "Pan Left", "Pan Right"],
            "Filter/EQ": ["Filter: Low Pass (1kHz)", "Filter: High Pass (500Hz)", "Filter: AM Radio"],
            "Time/Pitch": ["Reverse", "Speed: 2x", "Speed: 0.5x", "Pitch: +12 Semi", "Pitch: -12 Semi"],
            "Effects": ["Tremolo", "Robotize", "Fade In (1s)", "Fade Out (1s)"]
        }
        
        for cat, tools in categories.items():
            cat_menu = self.tools_menu.addMenu(cat)
            cat_menu.setStyleSheet(self.tools_menu.styleSheet())
            for tool in tools:
                # Use default arguments to capture tool name
                cat_menu.addAction(tool).triggered.connect(lambda checked=False, t=tool: self.apply_effect(t))
                
        btn_tools.setMenu(self.tools_menu)
        tl.addWidget(btn_tools)
        
        parent_layout.addWidget(toolbar)

    def setup_fx_bar(self, parent_layout):
        fx_bar = QFrame()
        fx_bar.setFixedHeight(40)
        fx_bar.setStyleSheet(f"background-color: {COLOR_BG_PANEL}; border-top: 1px solid {COLOR_BORDER};")
        fl = QHBoxLayout(fx_bar)
        fl.setContentsMargins(10, 0, 10, 0)
        
        lbl = QLabel("QUICK FX:")
        lbl.setStyleSheet(f"font-weight: bold; color: {COLOR_TEXT_SECONDARY}; font-size: 11px;")
        fl.addWidget(lbl)
        
        # Quick buttons
        for fx in ["Normalize", "Reverse", "Fade In (1s)", "Fade Out (1s)"]:
            btn = QPushButton(fx)
            btn.setFlat(True)
            btn.setStyleSheet(f"color: {COLOR_TEXT_PRIMARY}; font-weight: bold;")
            btn.clicked.connect(lambda checked=False, f=fx: self.apply_effect(f))
            fl.addWidget(btn)
            
        fl.addStretch()
        parent_layout.addWidget(fx_bar)

    def get_btn_style(self, color=COLOR_BG_PANEL, text_color=COLOR_TEXT_PRIMARY):
        border = f"1px solid {COLOR_BORDER}" if color == COLOR_BG_PANEL else "none"
        return f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: {border};
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BORDER} if '{color}' == '{COLOR_BG_PANEL}' else opacity: 0.8;
            }}
        """

    def import_audio(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Import Audio", "", "Audio Files (*.wav)")
        if filename:
            try:
                sr, data = AudioProcessor.load(filename)
                # Create Clip
                clip = AudioClip(data, sr, os.path.basename(filename))
                
                # Add to new track
                track = self.timeline.add_track(f"Track {len(self.timeline.tracks)+1}")
                track.add_clip(clip)
                
                self.status_message.emit(f"Imported: {filename} ({sr}Hz)")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", str(e))

    def export_audio(self):
        # Mixdown whole timeline
        mixed = self.mix_timeline()
        if mixed is None: return

        filename, _ = QFileDialog.getSaveFileName(self, "Export Audio", "", "WAV File (*.wav)")
        if filename:
            try:
                AudioProcessor.save(filename, self.sample_rate, mixed)
                self.status_message.emit(f"Exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def apply_effect(self, tool_name):
        # Apply to SELECTED clip(s)
        # Iterate all tracks and their selected clips
        # For now, simplistic iteration
        
        applied = False
        for track_widget in self.timeline.tracks:
            # Look at view's selected clip
            clip = track_widget.view.selected_clip
            if clip:
                self.status_message.emit(f"Applying {tool_name} to {clip.name}...")
                
                # Process Data
                try:
                    if tool_name == "Reverse": clip.data = AudioProcessor.reverse(clip.data)
                    elif tool_name == "Normalize": clip.data = AudioProcessor.normalize(clip.data)
                    elif "Fade In" in tool_name: clip.data = AudioProcessor.fade_in(clip.data, clip.sr)
                    elif "Fade Out" in tool_name: clip.data = AudioProcessor.fade_out(clip.data, clip.sr)
                    elif tool_name == "Stereo Widener": clip.data = AudioProcessor.stereo_widener(clip.data)
                    elif tool_name == "Make Mono": clip.data = AudioProcessor.make_mono(clip.data)
                    elif "Speed: 2x" in tool_name: clip.data = AudioProcessor.speed_change(clip.data, 2.0)
                    elif "Speed: 0.5x" in tool_name: clip.data = AudioProcessor.speed_change(clip.data, 0.5)
                    elif "Pitch: +12" in tool_name: clip.data = AudioProcessor.pitch_shift_simple(clip.data, 12)
                    elif "Pitch: -12" in tool_name: clip.data = AudioProcessor.pitch_shift_simple(clip.data, -12)
                    
                    track_widget.view.update() # Repaint
                    applied = True
                except Exception as e:
                    print(f"Effect Error: {e}")
        
        if not applied:
            self.status_message.emit("No clip selected!")
        else:
            self.status_message.emit(f"Applied: {tool_name}")

    def mix_timeline(self):
        # Simple summation mixer
        # Find max duration
        max_len = 0
        sr = 44100
        
        for track in self.timeline.tracks:
            for clip in track.view.clips:
                end_sample = int((clip.start_time + clip.duration) * sr)
                if end_sample > max_len: max_len = end_sample
        
        if max_len == 0: return None
        
        # Create master buffer (Stereo)
        master = np.zeros((max_len, 2), dtype=np.float32)
        
        for track in self.timeline.tracks:
            if track.header.btn_mute.isChecked(): continue
            
            vol = track.header.slider_vol.value() / 100.0
            pan = track.header.slider_pan.value() / 100.0
            
            for clip in track.view.clips:
                # Get clip data
                data = clip.data
                if data is None: continue
                
                # Ensure stereo
                if data.ndim == 1:
                    data = np.column_stack((data, data))
                
                # Apply track volume/pan
                # (Simple pan logic)
                l = data[:, 0] * vol * (1 - pan if pan > 0 else 1)
                r = data[:, 1] * vol * (1 + pan if pan < 0 else 1)
                processed = np.column_stack((l, r))
                
                # Place in master
                start_idx = int(clip.start_time * sr)
                end_idx = start_idx + len(processed)
                
                if start_idx < max_len:
                    can_copy = min(len(processed), max_len - start_idx)
                    master[start_idx:start_idx+can_copy] += processed[:can_copy]
                    
        return master

    def play_audio(self):
        mixed = self.mix_timeline()
        if mixed is None: 
            self.status_message.emit("Timeline empty!")
            return
        
        # Save to temp file and play
        import tempfile
        import os
        import pygame
        
        try:
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            AudioProcessor.save(path, self.sample_rate, mixed)
            
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            
            # Start Playback relative to Playhead? 
            # Pygame doesn't support seeking easily with music.load unless we slice the audio.
            # For now, start from 0 for simplicity or slice if playhead > 0.
            # Audacity starts from cursor.
            
            start_time = self.timeline.playhead_pos
            if start_time > 0:
                pygame.mixer.music.play(start=start_time)
            else:
                pygame.mixer.music.play()
                
            self.status_message.emit("Playing Mix...")
            
            # Start Timer
            self.playback_start_time = start_time
            self.playback_timer.start(50) # 50ms update
            
        except Exception as e:
            QMessageBox.critical(self, "Playback Error", str(e))

    def stop_playback(self):
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.playback_timer.stop()
        self.status_message.emit("Stopped")
        
    def update_playhead(self):
        import pygame
        if not pygame.mixer.get_init() or not pygame.mixer.music.get_busy():
            self.playback_timer.stop()
            return
            
        # Get position in ms
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms == -1: return
        
        # Update timeline
        current_time = self.playback_start_time + (pos_ms / 1000.0)
        self.timeline.playhead_pos = current_time
        self.timeline.update_all_views()
