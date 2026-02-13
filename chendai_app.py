import sys
import time
import threading
from chendai_6player import ChendAI6Player
from ui_loader import LoaderWindow, LogHandler
from ui_generator import MelamGenerator
from ui_editor import AudioEditor
from database.project_manager import ProjectManager

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QStackedWidget, QPushButton, 
                               QFrame, QSizePolicy, QButtonGroup, QMenuBar, QMenu,
                               QFileDialog, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QIcon, QPalette, QColor, QAction

# THEME CONSTANTS
COLOR_BG_DARK = "#09090b"
COLOR_BG_PANEL = "#18181b" 
COLOR_BORDER = "#27272a"
COLOR_ACCENT = "#fbbf24" # Amber-400
COLOR_ACCENT_HOVER = "#f59e0b" # Amber-500
COLOR_TEXT_PRIMARY = "#f4f4f5"
COLOR_TEXT_SECONDARY = "#a1a1aa"

STYLESHEET = f"""
    QMainWindow {{
        background-color: {COLOR_BG_DARK};
    }}
    QWidget {{
        color: {COLOR_TEXT_PRIMARY};
        font-family: 'Segoe UI', sans-serif;
    }}
    QSplitter::handle {{
        background-color: {COLOR_BORDER};
        width: 1px;
    }}
    QScrollArea {{
        border: none;
        background-color: {COLOR_BG_DARK};
    }}
    /* Menu Bar */
    QMenuBar {{
        background-color: {COLOR_BG_PANEL};
        border-bottom: 1px solid {COLOR_BORDER};
        color: {COLOR_TEXT_PRIMARY};
    }}
    QMenuBar::item {{
        background-color: transparent;
        padding: 8px 12px;
    }}
    QMenuBar::item:selected {{
        background-color: {COLOR_BORDER};
    }}
    QMenu {{
        background-color: {COLOR_BG_PANEL};
        border: 1px solid {COLOR_BORDER};
    }}
    QMenu::item {{
        padding: 5px 20px 5px 20px;
    }}
    QMenu::item:selected {{
        background-color: {COLOR_BORDER};
    }}
"""

class StudioWindow(QMainWindow):
    # Signals for thread-safe UI updates
    log_signal = Signal(str)
    progress_signal = Signal(int, str)
    ready_signal = Signal()
    generation_finished = Signal(dict)
    generation_error = Signal(str)

    def __init__(self, loader=None):
        super().__init__()
        self.setWindowTitle("ChendAI Studio Pro")
        self.resize(1400, 900)
        self.setWindowOpacity(0) # Start invisible
        
        # Keep reference to loader to update it
        self.loader = loader
        
        # Connect signals
        if self.loader:
            self.log_signal.connect(self.loader.log)
            self.progress_signal.connect(self.loader.set_progress)
        self.ready_signal.connect(self.on_ready)
        
        # Audio Engine (Initialized in thread)
        self.player = None 
        
        # Project Manager
        self.project_manager = ProjectManager()
        self.current_project_id = None
        
        # Animation
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Setup UI
        self.setup_ui()
        self.setup_menubar()
        
        # Initialize Engine in Background
        QTimer.singleShot(100, self.init_engine)

    def setup_menubar(self):
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_project_dialog)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu (Placeholder for Undo/Redo)
        edit_menu = menubar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setEnabled(False) # For now
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setEnabled(False) # For now
        edit_menu.addAction(redo_action)
        
    def new_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project Name:")
        if ok and name:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Project As", f"{name}.chendai", "ChendAI Project (*.chendai)")
            if filename:
                try:
                     # Reset Timeline
                     self.editor.timeline.clear()
                     self.generator_view.timeline.clear() # Fix variable name
                     self.current_project_id = None
                     
                     # Create DB Record
                     pid = self.project_manager.create_project(name, filename)
                     self.current_project_id = pid
                     self.setWindowTitle(f"ChendAI Studio Pro - {name}")
                     self.log_signal.emit(f"Created new project: {name}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))

    def save_project(self):
        if not self.current_project_id:
            self.new_project()
            return
            
        try:
            # 1. Get Project Info
            project = self.project_manager.get_project(self.current_project_id)
            if not project:
                raise Exception("Project handle lost!")
                
            project_path = project['file_path']
            project_dir = os.path.dirname(project_path)
            data_dir = os.path.join(project_dir, f"{project['name']}_data")
            os.makedirs(data_dir, exist_ok=True)
            
            # 2. Update Project Metadata
            self.project_manager.update_project(self.current_project_id)
            
            # 3. Clear existing tracks/clips in DB (Overwrite strategy)
            existing_tracks = self.project_manager.get_tracks(self.current_project_id)
            for t in existing_tracks:
                self.project_manager.delete_track(t['id'])
                
            # 4. Save Editor Timeline State
            # We iterate directly over objects to access .data
            tracks = self.editor.timeline.tracks
            
            from audio_processor import AudioProcessor
            
            for i, track in enumerate(tracks):
                # Create Track in DB
                tid = self.project_manager.create_track(
                    self.current_project_id, 
                    track.header.lbl_name.text(),
                    volume=track.header.slider_vol.value() / 100.0,
                    pan=track.header.slider_pan.value() / 100.0,
                    order_index=i
                )
                
                # Process Clips
                for j, clip in enumerate(track.view.clips):
                    # CONSOLIDATE: Save every clip as a new WAV file to ensure persistence
                    # This handles splits, in-memory generations, etc.
                    
                    # Generate unique filename
                    safe_track_name = "".join([c for c in track.header.lbl_name.text() if c.isalnum()])
                    clip_filename = f"T{i}_{safe_track_name}_C{j}.wav"
                    clip_path = os.path.join(data_dir, clip_filename)
                    
                    # Save Audio Data
                    AudioProcessor.save(clip_path, clip.sr, clip.data)
                    
                    # Store RELATIVE path in DB
                    rel_path = os.path.join(f"{project['name']}_data", clip_filename)
                    
                    self.project_manager.create_clip(
                        tid, rel_path,
                        clip.start_time,
                        clip.duration,
                        volume=clip.gain
                    )
            
            self.log_signal.emit(f"Project saved to {project_path}")
            self.statusBar().showMessage("Project Saved Successfully", 5000)
            
        except Exception as e:
             QMessageBox.critical(self, "Save Error", str(e))
             print(e)
             import traceback
             traceback.print_exc()

    def open_project_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "ChendAI Project (*.chendai)")
        if filename:
            try:
                # 1. Find or Import Project
                project = self.project_manager.get_project_by_path(filename)
                
                if not project:
                     # Auto-import if not in DB but file exists
                     name = os.path.splitext(os.path.basename(filename))[0]
                     pid = self.project_manager.create_project(name, filename)
                     project = self.project_manager.get_project(pid)
                     
                self.load_project(project['id'])
                     
            except Exception as e:
                QMessageBox.critical(self, "Open Error", str(e))

    def load_project(self, project_id):
        try:
            project = self.project_manager.get_project(project_id)
            if not project: return
            
            self.current_project_id = project_id
            self.setWindowTitle(f"ChendAI Studio Pro - {project['name']}")
            
            # Project Directory for resolving relative paths
            project_dir = os.path.dirname(project['file_path'])
            
            # Clear Timeline
            self.editor.timeline.clear()
            
            # Load Tracks
            tracks = self.project_manager.get_tracks(project_id)
            
            # Imports
            from ui_timeline import AudioClip
            from audio_processor import AudioProcessor
            import numpy as np
            
            for t_data in tracks:
                track = self.editor.timeline.add_track(t_data['name'])
                # Set Vol/Pan logic
                track.header.slider_vol.setValue(int(t_data['volume'] * 100))
                track.header.slider_pan.setValue(int(t_data['pan'] * 100))
                if t_data.get('mute'): track.header.btn_mute.setChecked(True)
                if t_data.get('solo'): track.header.btn_solo.setChecked(True)
                
                # Load Clips
                clips = self.project_manager.get_clips(t_data['id'])
                for c_data in clips:
                     audio_path = c_data['audio_path']
                     if not audio_path: continue
                     
                     # Resolve Path
                     if not os.path.isabs(audio_path):
                         full_path = os.path.join(project_dir, audio_path)
                     else:
                         full_path = audio_path
                         
                     if os.path.exists(full_path):
                          try:
                              sr, data = AudioProcessor.load(full_path)
                              # Create Clip
                              clip = AudioClip(data, sr, "Clip", c_data['start_time'], source_path=full_path)
                              clip.gain = c_data.get('volume', 1.0)
                              track.add_clip(clip)
                          except Exception as e:
                              print(f"Failed to load clip {full_path}: {e}")
                     else:
                          print(f"Missing audio file: {full_path}")
                              
            self.project_manager.update_last_opened(project_id)
            self.log_signal.emit(f"Loaded project: {project['name']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))
            print(e)

    def init_engine(self):
        """Initialize heavy resources while updating loader"""
        self.log_signal.emit("Initializing Audio Engine Core...")
        self.progress_signal.emit(20, "Loading Sound Banks...")
        
        self.thread = threading.Thread(target=self._run_heavy_load)
        self.thread.start()

    def _run_heavy_load(self):
        try:
            time.sleep(0.5)
            self.log_signal.emit("Loading Sample Library: Chenda_Master_DB.json...")
            self.progress_signal.emit(40, "Parsing DNA Sequences...")
            
            time.sleep(0.5)
            self.player = ChendAI6Player() 
            
            self.log_signal.emit("Audio Engine Ready.")
            self.progress_signal.emit(80, "Initializing UI Components...")
            
            time.sleep(0.3)
            self.progress_signal.emit(100, "Ready.")
            
            # Signal main thread to show window
            self.ready_signal.emit()
            
        except Exception as e:
            self.log_signal.emit(f"ERROR: {str(e)}")

    def on_ready(self):
        if self.loader:
            self.loader.close()
            
        # Pass player instance to generator
        if self.player:
            self.generator_view.set_player(self.player)
            
        self.show()
        self.anim.start()

    def setup_ui(self):
        # Central Widget Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout (Horizontal: Nav | Content)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Navigation Sidebar
        self.setup_nav_sidebar()
        main_layout.addWidget(self.nav_sidebar)
        
        # 2. Content Stack
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # 2a. Melam Generator View
        self.generator_view = MelamGenerator()
        self.generator_view.status_message.connect(self.statusBar().showMessage)
        self.stack.addWidget(self.generator_view)
        
        # 2b. Audio Editor View
        self.editor_view = AudioEditor()
        self.editor_view.status_message.connect(self.statusBar().showMessage)
        self.stack.addWidget(self.editor_view)
        
        # Setup Menu Bar
        self.setup_menu_bar()
        
        self.statusBar().showMessage("ChendAI Studio Pro - Initializing...")
        self.statusBar().setStyleSheet(f"background-color: {COLOR_BG_PANEL}; color: {COLOR_TEXT_SECONDARY}; border-top: 1px solid {COLOR_BORDER};")

    def setup_nav_sidebar(self):
        self.nav_sidebar = QFrame()
        self.nav_sidebar.setFixedWidth(60)
        self.nav_sidebar.setStyleSheet(f"background-color: {COLOR_BG_PANEL}; border-right: 1px solid {COLOR_BORDER};")
        
        layout = QVBoxLayout(self.nav_sidebar)
        layout.setContentsMargins(5, 20, 5, 20)
        layout.setSpacing(15)
        
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        
        # Navigation Buttons
        self.btn_gen = self.create_nav_btn("GEN", "Generator", 0)
        self.btn_edit = self.create_nav_btn("EDIT", "Audio Editor", 1)
        
        layout.addWidget(self.btn_gen)
        layout.addWidget(self.btn_edit)
        
        layout.addStretch()
        
        self.btn_gen.setChecked(True)

    def create_nav_btn(self, text, tooltip, index):
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setFixedSize(50, 50)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10px;
            }}
            QPushButton:checked {{
                background-color: {COLOR_ACCENT};
                color: {COLOR_BG_DARK};
            }}
            QPushButton:hover:!checked {{
                background-color: {COLOR_BORDER};
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        self.nav_group.addButton(btn)
        return btn

    def setup_menu_bar(self):
        menubar = self.menuBar()
        # File Menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction("&New Project").setShortcut("Ctrl+N")
        file_menu.addAction("&Open Project...").setShortcut("Ctrl+O")
        file_menu.addSeparator()
        file_menu.addAction("E&xit").triggered.connect(self.close)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction("Switch to &Generator").triggered.connect(lambda: self.switch_view(0))
        view_menu.addAction("Switch to &Editor").triggered.connect(lambda: self.switch_view(1))

        # Help Menu
        menubar.addMenu("&Help").addAction("&About").triggered.connect(self.show_about)

    def switch_view(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0: self.btn_gen.setChecked(True)
        else: self.btn_edit.setChecked(True)

    def show_about(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(self, "About ChendAI", "ChendAI Studio Pro\nversion 2.0 (Studio Edition)\n\n(c) 2026")

    def closeEvent(self, event):
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    
    # 1. Show Loader
    loader = LoaderWindow()
    loader.show()
    loader.log("ChendAI Studio Launcher Started.")
    
    # 2. Main Windows (Passed loader reference)
    window = StudioWindow(loader=loader)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
