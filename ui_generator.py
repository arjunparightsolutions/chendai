import threading
import os
import numpy as np
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QSpinBox, QFrame, 
                               QSplitter, QScrollArea, QMessageBox, QFileDialog)
from PySide6.QtCore import Qt, Signal, QTimer
from chendai_6player import ChendAI6Player
from ui_timeline import TimelineWidget, AudioClip
from ui_mixer import ChannelStrip
from audio_processor import AudioProcessor

# Theme Constants (Shared)
COLOR_BG_DARK = "#09090b"
COLOR_BG_PANEL = "#18181b" 
COLOR_BORDER = "#27272a"
COLOR_ACCENT = "#fbbf24"
COLOR_ACCENT_HOVER = "#f59e0b"
COLOR_TEXT_PRIMARY = "#f4f4f5"
COLOR_TEXT_SECONDARY = "#a1a1aa"

class MelamGenerator(QWidget):
    """
    The Melam Generator Module.
    Encapsulates the Chenda ensemble generation logic and UI.
    """
    # Signals to communicate with the main window or status bar
    status_message = Signal(str)
    
    def __init__(self, player_instance=None):
        super().__init__()
        self.player = player_instance
        self.current_audio = None
        self.sample_rate = 44100
        
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.update_playhead)
        self.playback_start_time = 0.0
        
        self.setup_ui()
        
    def set_player(self, player):
        """Set the shared audio engine instance"""
        self.player = player

    def setup_ui(self):
        # Main Layout using Splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main_splitter)
        
        # 1. Sidebar (Control Panel)
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet(f"background-color: {COLOR_BG_PANEL}; border-right: 1px solid {COLOR_BORDER};")
        self.setup_sidebar()
        self.main_splitter.addWidget(self.sidebar)
        
        # 2. Main Content
        self.content_splitter = QSplitter(Qt.Orientation.Vertical)
        self.main_splitter.addWidget(self.content_splitter)
        
        # 2a. Timeline Area
        self.timeline_area = QWidget()
        self.setup_timeline()
        self.content_splitter.addWidget(self.timeline_area)
        
        # 2b. Mixer Area
        self.mixer_area = QWidget()
        self.setup_mixer()
        self.content_splitter.addWidget(self.mixer_area)
        
        self.content_splitter.setSizes([600, 250])

    def setup_sidebar(self):
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Logo/Header
        header = QLabel("AI COMPOSER")
        header.setStyleSheet(f"font-weight: 900; color: {COLOR_TEXT_SECONDARY}; letter-spacing: 2px; font-size: 12px;")
        layout.addWidget(header)
        
        # Generator Controls Container
        controls = QFrame()
        controls.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_DARK};
                border: 1px solid {COLOR_BORDER};
                border-radius: 8px;
            }}
        """)
        c_layout = QVBoxLayout(controls)
        c_layout.setSpacing(15)
        
        # Scenario Input
        lbl_scenario = QLabel("SCENARIO / PROMPT")
        lbl_scenario.setStyleSheet("font-size: 11px; font-weight: bold; color: #71717a;")
        c_layout.addWidget(lbl_scenario)
        
        from PySide6.QtWidgets import QPlainTextEdit
        self.scenario_input = QPlainTextEdit()
        self.scenario_input.setPlaceholderText("Describe the vibe (e.g. 'Slow temple procession', 'Frantic festival climax', 'Royal entry with elephants')...")
        self.scenario_input.setFixedHeight(80)
        self.scenario_input.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: {COLOR_BG_PANEL};
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
                color: {COLOR_TEXT_PRIMARY};
                padding: 10px;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }}
            QPlainTextEdit:focus {{ border: 1px solid {COLOR_ACCENT}; }}
        """)
        c_layout.addWidget(self.scenario_input)
        
        # Duration Control
        lbl_dur = QLabel("DURATION")
        lbl_dur.setStyleSheet("font-size: 11px; font-weight: bold; color: #71717a;")
        c_layout.addWidget(lbl_dur)
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 300)
        self.duration_spin.setValue(30)
        self.duration_spin.setSuffix(" sec")
        self.duration_spin.setStyleSheet(f"""
            QSpinBox {{ 
                background: {COLOR_BG_PANEL}; 
                border: 1px solid {COLOR_BORDER}; 
                border-radius: 4px; 
                padding: 10px;
                color: {COLOR_TEXT_PRIMARY};
                font-weight: bold;
            }}
            QSpinBox:hover {{ border-color: {COLOR_ACCENT}; }}
        """)
        c_layout.addWidget(self.duration_spin)
        
        layout.addWidget(controls)
        
        # Action Buttons
        self.btn_generate = QPushButton("GENERATE AUDIO")
        self.btn_generate.setFixedHeight(50)
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.setStyleSheet(f"""
            QPushButton {{ 
                background: {COLOR_ACCENT}; 
                color: {COLOR_BG_DARK}; 
                font-weight: 800; 
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 0.5px;
                border: none;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
            QPushButton:pressed {{ background-color: #d97706; transform: translateY(1px); }}
        """)
        self.btn_generate.clicked.connect(self.generate_audio)
        layout.addWidget(self.btn_generate)
        
        self.btn_play = QPushButton("PLAY PREVIEW")
        self.btn_play.setFixedHeight(45)
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.setStyleSheet(f"""
            QPushButton {{ 
                background: {COLOR_BG_PANEL}; 
                border: 1px solid {COLOR_BORDER};
                color: {COLOR_TEXT_PRIMARY}; 
                font-weight: bold; 
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: {COLOR_BORDER}; border-color: {COLOR_TEXT_SECONDARY}; }}
            QPushButton:disabled {{ opacity: 0.5; }}
        """)
        self.btn_play.clicked.connect(self.play_audio)
        self.btn_play.setEnabled(False)
        layout.addWidget(self.btn_play)
        
        layout.addStretch()

    def setup_timeline(self):
        layout = QVBoxLayout(self.timeline_area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Toolbar
        toolbar = QFrame()
        toolbar.setFixedHeight(50)
        toolbar.setStyleSheet(f"background-color: {COLOR_BG_PANEL}; border-bottom: 1px solid {COLOR_BORDER};")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(10, 5, 10, 5)
        
        # 1. Export
        btn_export = QPushButton("EXPORT MIX")
        btn_export.setStyleSheet(f"background-color: {COLOR_BG_DARK}; color: {COLOR_TEXT_PRIMARY}; border: 1px solid {COLOR_BORDER}; border-radius: 4px; padding: 5px 10px; font-weight: bold;")
        btn_export.clicked.connect(self.export_mix)
        tl.addWidget(btn_export)
        
        tl.addStretch()
        
        # 2. Edit Tools
        btn_split = QPushButton("✂ Split")
        btn_split.setToolTip("Split Clip at Playhead")
        btn_split.setStyleSheet(self.get_btn_style())
        btn_split.clicked.connect(self.split_selection)
        tl.addWidget(btn_split)
        
        btn_del = QPushButton("🗑 Delete")
        btn_del.setStyleSheet(self.get_btn_style())
        btn_del.clicked.connect(self.delete_selection)
        tl.addWidget(btn_del)
        
        tl.addStretch()
        
        # 3. Transport
        self.btn_rewind = QPushButton("⏪")
        self.btn_rewind.setStyleSheet(self.get_btn_style())
        self.btn_rewind.clicked.connect(self.rewind)
        tl.addWidget(self.btn_rewind)
        
        self.btn_play_pause = QPushButton("▶")
        self.btn_play_pause.setFixedSize(40, 30)
        self.btn_play_pause.setStyleSheet(f"background-color: {COLOR_ACCENT}; color: {COLOR_BG_DARK}; border-radius: 4px; font-size: 16px;")
        self.btn_play_pause.clicked.connect(self.toggle_playback)
        tl.addWidget(self.btn_play_pause)
        
        self.btn_stop = QPushButton("⏹")
        self.btn_stop.setStyleSheet(self.get_btn_style())
        self.btn_stop.clicked.connect(self.stop_playback)
        tl.addWidget(self.btn_stop)

        self.btn_forward = QPushButton("⏩")
        self.btn_forward.setStyleSheet(self.get_btn_style())
        self.btn_forward.clicked.connect(self.forward)
        tl.addWidget(self.btn_forward)
        
        tl.addStretch() # Balance
        
        layout.addWidget(toolbar)
        
        # Timeline Widget (Audacity Style)
        self.timeline = TimelineWidget()
        layout.addWidget(self.timeline)

    def setup_mixer(self):
        layout = QVBoxLayout(self.mixer_area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setFixedHeight(35)
        header.setStyleSheet(f"background-color: {COLOR_BG_PANEL}; border-top: 1px solid {COLOR_BORDER}; border-bottom: 1px solid {COLOR_BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(15, 0, 15, 0)
        h_layout.addWidget(QLabel("MIXER CONSOLE"))
        layout.addWidget(header)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: #09090b;")
        
        mixer_content = QWidget()
        mixer_content.setStyleSheet(f"background-color: {COLOR_BG_DARK};")
        self.mixer_layout = QHBoxLayout(mixer_content)
        self.mixer_layout.setContentsMargins(20, 20, 20, 20)
        self.mixer_layout.setSpacing(5)
        
        # Add Example Tracks
        tracks = [
            ("LEAD 1", "Lead"), ("LEAD 2", "Lead"), 
            ("BASE 1", "Base"), ("BASE 2", "Base"), 
            ("BELL", "Bell"), ("FX", "Lead")
        ]
        for name, role in tracks:
            strip = ChannelStrip(name, role)
            self.mixer_layout.addWidget(strip)
            
        self.mixer_layout.addStretch()
        scroll.setWidget(mixer_content)
        layout.addWidget(scroll)

    def generate_audio(self):
        if not self.player:
            self.status_message.emit("Audio Engine not initialized!")
            return

        scenario = self.scenario_input.toPlainText().strip()
        if not scenario:
            scenario = "Traditional Panchari Melam" # Default
            
        duration = self.duration_spin.value()
        
        self.status_message.emit(f"Composing: '{scenario}' ({duration}s)...")
        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("COMPOSING...")
        self.btn_generate.setStyleSheet(f"background-color: {COLOR_BORDER}; color: {COLOR_TEXT_SECONDARY}; border-radius: 6px;")
        
        threading.Thread(target=self._generate_thread, args=(scenario, duration)).start()

    def _generate_thread(self, style, duration_sec):
        try:
            print(f"DEBUG: Calling generate_melam with prompt='Play {style}', duration={duration_sec}")
            # print(f"DEBUG: Player methods: {dir(self.player)}")
            
            result = self.player.generate_melam(prompt=f"Play {style}", duration=duration_sec)
            self.generation_finished_internal.emit(result)
            
        except TypeError as te:
             print(f"DEBUGGING TYPEERROR: {te}")
             import traceback
             traceback.print_exc()
             self.generation_error_internal.emit(str(te))
        except Exception as e:
            self.generation_error_internal.emit(str(e))

    # Internal signals for thread safety
    generation_finished_internal = Signal(dict)
    generation_error_internal = Signal(str)

    def check_signals(self):
        # Connect internal signals
        try:
            self.generation_finished_internal.connect(self.on_generation_finished)
            self.generation_error_internal.connect(self.on_generation_error)
        except:
            pass # Already connected

    def showEvent(self, event):
        self.check_signals()
        super().showEvent(event)

    def on_generation_finished(self, result):
        self.current_audio = result['master']
        stems = result.get('stems', {})
        style = result['metadata']['style']
        
        # Update Timeline with Stems!
        self.timeline.clear()
        
        try:
            # 1. Add Master Track (Optional, maybe muted)
            # sr, master_data = AudioProcessor.load(self.current_audio)
            # tr = self.timeline.add_track("MASTER MIX")
            # tr.add_clip(AudioClip(master_data, sr, "Master"))
            # tr.header.btn_mute.setChecked(True) # Mute master so we hear stems
            
            # 2. Add Stems
            for stem_name, stem_path in stems.items():
                if os.path.exists(stem_path):
                    sr, data = AudioProcessor.load(stem_path)
                    track = self.timeline.add_track(stem_name.upper().replace("_", " "))
                    track.add_clip(AudioClip(data, sr, stem_name))
            
            self.status_message.emit(f"Generated: {style} (Stems Loaded)")
            
        except Exception as e:
            self.status_message.emit(f"Error loading stems: {str(e)}")
        
        # Update UI
        self.btn_play.setEnabled(True)
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("GENERATE AUDIO")
        self.btn_generate.setStyleSheet(f"""
            QPushButton {{ 
                background: {COLOR_ACCENT}; 
                color: {COLOR_BG_DARK}; 
                font-weight: 800; 
                border-radius: 6px;
                font-size: 14px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
        """)

    def on_generation_error(self, error_msg):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("GENERATE AUDIO")
        self.status_message.emit(f"Error: {error_msg}")

    def get_btn_style(self):
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {COLOR_BORDER};
            }}
        """

    def export_mix(self):
        mixed = self.mix_timeline()
        if mixed is None:
            self.status_message.emit("Nothing to export!")
            return
            
        filename, _ = QFileDialog.getSaveFileName(self, "Export Mix", "", "WAV File (*.wav)")
        if filename:
            try:
                AudioProcessor.save(filename, self.sample_rate, mixed)
                self.status_message.emit(f"Exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))

    def toggle_playback(self):
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
            
        if pygame.mixer.music.get_busy():
            # Pause
            pygame.mixer.music.pause()
            self.btn_play_pause.setText("▶")
            self.playback_timer.stop()
            self.status_message.emit("Paused")
        else:
            # Play
            # Check if paused or stopped
            # If we have a playhead pos, we should probably start from there if not already playing
            # But pygame pause/unpause is for the *current* stream. 
            # If we stopped, we need to restart.
            
            # Simple logic: If paused (and stream exists), unpause. Else play mix.
            try:
                # Hacky check for pause state in pygame? 
                # pygame doesn't have is_paused().
                
                # Let's just track state manually or re-trigger play
                self.play_audio()
                self.btn_play_pause.setText("⏸")
            except Exception as e:
                pass

    def stop_playback(self):
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        self.playback_timer.stop()
        self.btn_play_pause.setText("▶")
        self.status_message.emit("Stopped")
        
        # Reset playhead? Audacity stays or resets depending on pref.
        # Let's reset to 0
        self.timeline.playhead_pos = 0.0
        self.playback_start_time = 0.0
        self.timeline.update_all_views()

    def rewind(self):
        self.timeline.playhead_pos = 0.0
        self.timeline.update_all_views()
        if self.playback_timer.isActive():
            self.play_audio() # Restart from 0

    def forward(self):
        # Jump to end
        max_time = 0
        for track in self.timeline.tracks:
            for clip in track.view.clips:
                max_time = max(max_time, clip.end_time)
        
        self.timeline.playhead_pos = max_time
        self.timeline.update_all_views()
        self.stop_playback()

    def split_selection(self):
        # Split selected clips OR all clips at playhead if nothing selected
        playhead_time = self.timeline.playhead_pos
        pixels = playhead_time * 50 
        
        count = 0
        any_selected = False
        
        # Check explicit selection first
        for track in self.timeline.tracks:
            if track.view.selected_clip:
                any_selected = True
                track.view.split_clip(track.view.selected_clip, pixels)
                count += 1
        
        # If nothing selected, split EVERYTHING at playhead (Audacity behavior)
        if not any_selected:
            for track in self.timeline.tracks:
                # Find clip at playhead
                for clip in track.view.clips:
                    if clip.start_time <= playhead_time < clip.end_time:
                         track.view.split_clip(clip, pixels)
                         count += 1
                         break 
                
        if count > 0:
            self.status_message.emit(f"Split {count} clips at {playhead_time:.2f}s")
        else:
            self.status_message.emit("No clips at cursor to split.")

    def delete_selection(self):
        count = 0
        # Delete explicitly selected clips
        for track in self.timeline.tracks:
            clip = track.view.selected_clip
            if clip:
                track.view.delete_clip(clip)
                count += 1
        
        if count > 0:
            self.status_message.emit(f"Deleted {count} clips")
        else:
             self.status_message.emit("Select a clip to delete.")

    def mix_timeline(self):
            # Reuse mixing logic (should abstract this to a mixer class later)
            max_len = 0
            sr = 44100
            
            for track in self.timeline.tracks:
                for clip in track.view.clips:
                    end_sample = int((clip.start_time + clip.duration) * sr)
                    if end_sample > max_len: max_len = end_sample
            
            if max_len == 0: return None
            
            master = np.zeros((max_len, 2), dtype=np.float32)
            
            for track in self.timeline.tracks:
                if track.header.btn_mute.isChecked(): continue
                
                vol = track.header.slider_vol.value() / 100.0
                pan = track.header.slider_pan.value() / 100.0
                
                for clip in track.view.clips:
                    data = clip.data
                    if data is None: continue
                    if data.ndim == 1: data = np.column_stack((data, data))
                    
                    # Pan
                    l = data[:, 0] * vol * (1 - pan if pan > 0 else 1)
                    r = data[:, 1] * vol * (1 + pan if pan < 0 else 1)
                    processed = np.column_stack((l, r))
                    
                    start_idx = int(clip.start_time * sr)
                    can_copy = min(len(processed), max_len - start_idx)
                    master[start_idx:start_idx+can_copy] += processed[:can_copy]
                        
            return master

    def play_audio(self):
        # Mix timeline instead of playing static file
        mixed = self.mix_timeline()
        if mixed is None:
             # Fallback
            if self.current_audio:
                super_play(self.current_audio)
            return

        import tempfile
        import pygame
        
        try:
            fd, path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            AudioProcessor.save(path, self.sample_rate, mixed)
            
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(path)
            
            start_time = self.timeline.playhead_pos
            if start_time > 0:
                pygame.mixer.music.play(start=start_time)
            else:
                pygame.mixer.music.play()
                
            self.status_message.emit("Playing Mix...")
            self.btn_play_pause.setText("⏸")
            
            # Start Timer
            self.playback_start_time = start_time
            self.playback_timer.start(50)
            
        except Exception as e:
            self.status_message.emit(message=f"Playback Error: {e}") 

    def update_playhead(self):
        import pygame
        if not pygame.mixer.get_init() or not pygame.mixer.music.get_busy():
            # If we were playing and now we are not, it means we finished or stopped
            if self.btn_play_pause.text() == "⏸":
                 self.btn_play_pause.setText("▶")
                 self.playback_timer.stop()
            return

        # Get position in ms
        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms == -1: return

        # Update timeline
        current_time = self.playback_start_time + (pos_ms / 1000.0)
        self.timeline.playhead_pos = current_time
        self.timeline.update_all_views()

def super_play(audio_path):
    import pygame
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()
