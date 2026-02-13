"""
ChendAI Studio - Main Window
Professional 3-panel DAW layout
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QMenuBar, QMenu, QAction, QStatusBar, QToolBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont

from ui.widgets.control_panel import ControlPanel
from ui.widgets.mixer_panel import MixerPanel
from ui.widgets.timeline_editor import TimelineEditor
from ui.widgets.transport import TransportControls
from ui.audio_worker import AudioGenerationWorker
from ui.dialogs.project_dialog import NewProjectDialog
from ui.dialogs.project_browser import ProjectBrowserDialog
from database.project_manager import ProjectManager
from audio.plugin_manager import PluginManager


class ChendAIMainWindow(QMainWindow):
    """Main application window with professional DAW layout"""
    
    # Signals
    audio_generated = pyqtSignal(str)  # path to generated audio
    
    def __init__(self):
        super().__init__()
        
        self.audio_path = None
        self.is_playing = False
        self.worker = None
        self.chendai_system = None
        self.audio_channel = None
        self.current_project_id = None
        
        # Initialize project manager
        self.project_manager = ProjectManager()
        
        # Initialize plugin manager (Required by audio engine)
        self.plugin_manager = PluginManager()
        
        # Restore window geometry
        self.restore_geometry()
        
        # Initialize audio engine
        self.init_audio_engine()
        
        self.init_ui()
        self.setup_menu_bar()
        self.setup_status_bar()
        
    def init_audio_engine(self):
        """Initialize ChendAI audio engine"""
        try:
            from chendai_6player import ChendAI6Player
            from audio.engine import AudioEngine
            
            print("🎵 Initializing ChendAI 6-Player System...")
            self.chendai_system = ChendAI6Player()
            
            # Initialize Real-time Audio Engine
            self.audio_engine = AudioEngine(self.plugin_manager)
            self.audio_engine.position_changed.connect(self.update_playback_time)
            self.audio_engine.playback_finished.connect(self.on_playback_finished)
            
            print("✅ Audio engine ready!")
        except Exception as e:
            print(f"⚠️ Failed to initialize audio engine: {e}")
            print("   The app will run in UI-only mode.")
            print("✅ Audio engine ready!")
        except Exception as e:
            print(f"⚠️ Failed to initialize audio engine: {e}")
            print("   The app will run in UI-only mode.")
            self.chendai_system = None
        
    def init_ui(self):
        """Initialize user interface"""
        # Apply Theme
        from ui.styles import STYLE_SHEET
        self.setStyleSheet(STYLE_SHEET)
        
        self.setWindowTitle("ChendAI Studio Pro v2.0")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Center window on screen
        self.center_on_screen()
        
        # Create main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(5)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main 3-panel workspace
        workspace = self.create_workspace()
        main_layout.addWidget(workspace, stretch=1)
        
        # Transport controls at bottom
        self.transport = TransportControls()
        main_layout.addWidget(self.transport)
        
        # Connect signals
        self.connect_signals()
        
    def create_header(self):
        """Create header with logo and title"""
        header = QWidget()
        header.setObjectName("header")
        header.setFixedHeight(50)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Logo and title
        logo_label = QLabel("🥁")
        logo_label.setStyleSheet("font-size: 28px;")
        
        title_label = QLabel("ChendAI Studio")
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00d4ff;")
        
        version_label = QLabel("Pro v2.0")
        version_label.setStyleSheet("color: #888; font-size: 9px; margin-left: 8px;")
        
        layout.addWidget(logo_label)
        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addStretch()
        
        return header
        
    def create_workspace(self):
        """Create 3-panel workspace layout"""
        splitter = QSplitter(Qt.Horizontal)
        
        # Panels are now initialized below
        
        # Connect signals
        # self.plugin_manager.scan_finished.connect(self.on_scan_finished) # This line was not in the original, adding it would be an unrelated edit.
        
        # Left Panel - Library & Controls
        # self.control_panel is now just the Library/Plugin browser
        self.control_panel = ControlPanel(self.plugin_manager)
        self.control_panel.setMinimumWidth(300)
        self.control_panel.setMaximumWidth(350)
        
        # Center Panel - Timeline/Arrangement
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(5, 5, 5, 5)
        center_layout.setSpacing(5)
        
        timeline_header = QLabel("ARRANGEMENT")
        timeline_header.setObjectName("panelHeader")
        timeline_header.setFixedHeight(35)
        timeline_header.setAlignment(Qt.AlignCenter)
        
        self.timeline_editor = TimelineEditor()
        
        center_layout.addWidget(timeline_header)
        center_layout.addWidget(self.timeline_editor, stretch=1)
        
        # Right Panel - Generator & Sequencer
        from ui.widgets.generator_panel import GeneratorPanel
        self.generator_panel = GeneratorPanel()
        self.generator_panel.setMinimumWidth(350)
        self.generator_panel.setMaximumWidth(400)
        
        # Add panels to splitter
        splitter.addWidget(self.control_panel)
        splitter.addWidget(center_widget)
        splitter.addWidget(self.generator_panel)
        
        # Set initial sizes (proportional)
        splitter.setSizes([300, 900, 400])
        
        return splitter
        
    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save Project As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export Audio...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_audio)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()

        import_midi_action = QAction("Import MIDI File...", self)
        import_midi_action.triggered.connect(self.import_midi)
        file_menu.addAction(import_midi_action)
        
        export_midi_action = QAction("Export MIDI File...", self)
        export_midi_action.triggered.connect(self.export_midi)
        file_menu.addAction(export_midi_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
        
        # View Menu
        view_menu = menubar.addMenu("View")
        
        zoom_in = QAction("Zoom In", self)
        zoom_in.setShortcut("Ctrl++")
        view_menu.addAction(zoom_in)
        
        zoom_out = QAction("Zoom Out", self)
        zoom_out.setShortcut("Ctrl+-")
        view_menu.addAction(zoom_out)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About ChendAI Studio", self)
        help_menu.addAction(about_action)
        
    def setup_status_bar(self):
        """Setup status bar at bottom"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        status_bar.showMessage("Ready")
        
    def connect_signals(self):
        """Connect widget signals"""
        # Connect control panel generate button to handler
        self.control_panel.generate_clicked.connect(self.on_generate_music)
        
        # Connect recorder
        self.control_panel.recorder.recording_stopped.connect(self.on_recording_finished)
        
        # Connect plugin browser
        self.control_panel.plugin_browser.plugin_selected.connect(self.on_plugin_selected)
        
        # Connect transport controls
        self.transport.play_clicked.connect(self.on_play)
        self.transport.pause_clicked.connect(self.on_pause)
        self.transport.stop_clicked.connect(self.on_stop) 
        
    def on_plugin_selected(self, plugin_name):
        """Handle plugin selection"""
        track_idx = self.timeline_editor.selected_track_index
        if track_idx < 0:
            self.statusBar().showMessage("Please select a track first!", 3000)
            return
            
        self.statusBar().showMessage(f"Loading plugin: {plugin_name}...", 2000)
        
        # Provide visual feedback (simulated loading)
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()
        
        plugin = self.plugin_manager.load_plugin(plugin_name, track_idx)
        
        if plugin:
            self.statusBar().showMessage(f"Loaded: {plugin_name} on Track {track_idx+1}", 4000)
            # Open editor immediately
            self.plugin_manager.open_editor(plugin)
        else:
            self.statusBar().showMessage(f"Failed to load: {plugin_name}", 4000)
        
    def on_recording_finished(self, path):
        """Handle recording finished"""
        if path:
            print(f"✅ Recording saved: {path}")
            self.statusBar().showMessage(f"Recorded: {path}", 5000)
            
            # Add new track with recording
            from datetime import datetime
            name = f"Rec {datetime.now().strftime('%H:%M:%S')}"
            
            self.timeline_editor.add_track({
                'name': name,
                'color': '#ff4444'
            })
            # TODO: Add clip to track once we have duration
            # For now we just create the track to show it worked
        
    def on_generate_music(self, params):
        """Handle music generation request"""
        if not self.chendai_system:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Audio Engine Not Available",
                "The audio engine failed to initialize.\n\n"
                "Please check that all dependencies are installed:\n"
                "- ChendAI 6-Player system\n"
                "- NumPy, SciPy, librosa\n"
                "- soundfile"
            )
            return
            
        # Cancel any existing generation
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        
        # Create progress dialog
        from PyQt5.QtWidgets import QProgressDialog
        self.progress_dialog = QProgressDialog(
            "Initializing...",
            "Cancel",
            0, 100,
            self
        )
        self.progress_dialog.setWindowTitle("Generating Music")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setValue(0)
        
        # Create worker thread
        self.worker = AudioGenerationWorker(self.chendai_system, params)
        
        # Connect signals
        self.worker.progress_updated.connect(self.on_generation_progress)
        self.worker.generation_complete.connect(self.on_generation_complete)
        self.worker.generation_failed.connect(self.on_generation_failed)
        self.progress_dialog.canceled.connect(self.on_generation_canceled)
        
        # Start generation
        self.statusBar().showMessage("Generating music...")
        self.worker.start()
        
    def on_generation_progress(self, progress, message):
        """Update progress dialog"""
        if progress == -1:
            # This is a log message
            self.statusBar().showMessage(message)
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.setLabelText(message)
            return

        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(progress)
            self.progress_dialog.setLabelText(message)
            
    def on_generation_complete(self, audio_path):
        """Handle successful generation"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        self.audio_path = audio_path
        self.statusBar().showMessage(f"Generated: {audio_path}", 5000)
        
        # Update waveform
        self.timeline_editor.clear_tracks()
        colors = ['#00d4ff', '#ff0055', '#00ff55', '#ffee00', '#00aaff', '#aa00ff']
        for i in range(6):
            self.timeline_editor.add_track({
                'name': f'Player {i+1}',
                'color': colors[i % len(colors)]
            })
        
        # Enable transport controls
        self.transport.set_audio_loaded(True)
        
        # Load audio for playback
        if self.audio_engine.load_audio(audio_path):
            self.statusBar().showMessage("Music ready to play!", 3000)
            self.audio_duration = self.audio_engine.get_duration()
        else:
             self.statusBar().showMessage("Failed to load audio engine", 3000)
            
        print(f"✅ Music generated: {audio_path}")
        
    def on_generation_failed(self, error_msg):
        """Handle generation failure"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
            
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(
            self,
            "Generation Failed",
            f"Failed to generate music:\n\n{error_msg}\n\n"
            "Please check the console for more details."
        )
        
        self.statusBar().showMessage("Generation failed", 5000)
        
    def on_generation_canceled(self):
        """Handle generation cancellation"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
        
        self.statusBar().showMessage("Generation canceled", 3000)
        
    def on_play(self):
        """Handle play button"""
        if not self.audio_path:
            self.statusBar().showMessage("No audio loaded", 2000)
            return
            
        self.audio_engine.play()
        self.statusBar().showMessage("Playing...")
            
    def on_pause(self):
        """Handle pause button"""
        self.audio_engine.pause()
        self.statusBar().showMessage("Paused")
        
    def on_stop(self):
        """Handle stop button"""
        self.audio_engine.stop()
        self.transport.play_btn.setText("▶")
        self.transport.update_time(0, self.audio_duration if hasattr(self, 'audio_duration') else 30)
        self.statusBar().showMessage("Stopped")
            
    def update_playback_time(self, current_time):
        """Update playback time display from engine signal"""
        total = self.audio_duration if hasattr(self, 'audio_duration') else 30.0
        self.transport.update_time(current_time, total)
        
    def on_playback_finished(self):
        """Handle end of playback"""
        self.on_stop()
    
    # Project Management Methods
    def new_project(self):
        """Create new project"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Ask to save current project if modified
        if self.current_project_id:
            reply = QMessageBox.question(
                self,
                "Save Current Project?",
                "Do you want to save the current project before creating a new one?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_project()
        
        # Show new project dialog
        dialog = NewProjectDialog(self)
        
        if dialog.exec_() == dialog.Accepted:
            data = dialog.get_project_data()
            
            # Create in database
            project_id = self.project_manager.create_project(
                name=data['name'],
                file_path=data['path'],
                sample_rate=data['sample_rate'],
                bpm=data['bpm']
            )
            
            # Load the new project
            self.load_project(project_id)
            
            self.statusBar().showMessage(f"Created project: {data['name']}", 3000)
    
    def open_project(self):
        """Open existing project"""
        dialog = ProjectBrowserDialog(self.project_manager, self)
        
        if dialog.exec_() == dialog.Accepted:
            if dialog.selected_project:
                self.load_project(dialog.selected_project['id'])
    
    def load_project(self, project_id):
        """Load project by ID"""
        project = self.project_manager.get_project(project_id)
        
        if not project:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Project not found")
            return
        
        self.current_project_id = project_id
        
        # Update window title
        self.setWindowTitle(f"ChendAI Studio - {project['name']}")
        
        # Load tracks
        tracks = self.project_manager.get_tracks(project_id)
        
        # TODO: Populate timeline with tracks
        
        self.statusBar().showMessage(f"Loaded project: {project['name']}", 3000)
        
        # Save to config
        from utils.config_manager import ConfigManager
        config = ConfigManager()
        config.save_recent_project(project_id)
    
    def save_project(self):
        """Save current project"""
        if not self.current_project_id:
            self.save_project_as()
            return
        
        # TODO: Save current state to database
        # - Update tracks
        # - Update clips
        # - Update mixer states
        
        self.project_manager.update_project(
            self.current_project_id,
            modified_at=None  # Will use current time
        )
        
        project = self.project_manager.get_project(self.current_project_id)
        self.statusBar().showMessage(f"Saved: {project['name']}", 2000)
    
    def save_project_as(self):
        """Save project as new"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Save Project As",
            os.path.expanduser("~/Documents/ChendAI Studio")
        )
        
        if directory:
            project_name = os.path.basename(directory)
            
            # Create new project in database
            project_id = self.project_manager.create_project(
                name=project_name,
                file_path=directory
            )
            
            # TODO: Copy current project data to new project
            
            self.current_project_id = project_id
            self.setWindowTitle(f"ChendAI Studio - {project_name}")
            
            self.statusBar().showMessage(f"Saved as: {project_name}", 3000)
    
    def export_audio(self):
        """Export audio"""
        from PyQt5.QtWidgets import QMessageBox
        
        QMessageBox.information(
            self,
            "Export Audio",
            "Export feature will be available in Sprint 5.\n\n"
            "For now, generated audio files are saved in the output folder."
        )

    def import_midi(self):
        """Import MIDI file"""
        from PyQt5.QtWidgets import QFileDialog
        from utils.midi_io import MidiIO
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import MIDI", "", "MIDI Files (*.mid *.midi)"
        )
        
        if file_path:
            tracks = MidiIO.import_midi(file_path)
            if tracks:
                for track in tracks:
                    self.timeline_editor.add_track(track)
                self.statusBar().showMessage(f"Imported {len(tracks)} MIDI tracks", 3000)
            else:
                self.statusBar().showMessage("Failed to import MIDI", 3000)
                
    def export_midi(self):
        """Export MIDI file"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from utils.midi_io import MidiIO
        
        # Collect track data from timeline (needs implementation in TimelineEditor to return data)
        # For now, just a placeholder
        QMessageBox.information(self, "Export MIDI", "MIDI Export requires timeline data access (Coming in Sprint 4)")

    def restore_geometry(self):
        """Restore window geometry from config"""
        from utils.config_manager import ConfigManager
        
        config = ConfigManager()
        geometry = config.get_window_geometry()
        
        if geometry:
            self.restoreGeometry(geometry)
    
    def save_geometry(self):
        """Save window geometry to config"""
        from utils.config_manager import ConfigManager
        
        config = ConfigManager()
        config.save_window_geometry(self.saveGeometry())
    
    def closeEvent(self, event):
        """Handle window close"""
        from PyQt5.QtWidgets import QMessageBox
        
        # Ask to save if project is modified
        if self.current_project_id:
            reply = QMessageBox.question(
                self,
                "Save Project?",
                "Do you want to save changes before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.Yes:
                self.save_project()
        
        # Save window geometry
        self.save_geometry()
        
        # Clean up
        if hasattr(self, 'playback_timer'):
            self.playback_timer.stop()
        
        try:
            import pygame
            pygame.mixer.quit()
        except:
            pass
        
        # Close database
        if self.project_manager:
            self.project_manager.close()
        
        event.accept()
        
    def center_on_screen(self):
        """Center window on screen"""
        from PyQt5.QtWidgets import QDesktopWidget
        center_point = QDesktopWidget().availableGeometry().center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
