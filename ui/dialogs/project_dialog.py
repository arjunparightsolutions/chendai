"""
New Project Dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QFileDialog, QGroupBox, QFormLayout
)
from PyQt5.QtCore import Qt
import os


class NewProjectDialog(QDialog):
    """Dialog for creating new project"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.project_name = ""
        self.project_path = ""
        self.sample_rate = 44100
        self.bpm = 120
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("New Project")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Project settings group
        settings_group = QGroupBox("Project Settings")
        settings_layout = QFormLayout(settings_group)
        
        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Awesome Track")
        self.name_edit.setText("Untitled Project")
        settings_layout.addRow("Project Name:", self.name_edit)
        
        # Project location
        location_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        default_path = os.path.join(
            os.path.expanduser("~/Documents/ChendAI Studio"),
            "Untitled Project"
        )
        self.path_edit.setText(default_path)
        self.path_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_location)
        
        location_layout.addWidget(self.path_edit, stretch=1)
        location_layout.addWidget(browse_btn)
        settings_layout.addRow("Save In:", location_layout)
        
        layout.addWidget(settings_group)
        
        # Audio settings group
        audio_group = QGroupBox("Audio Settings")
        audio_layout = QFormLayout(audio_group)
        
        # Sample rate
        self.sample_rate_spin = QSpinBox()
        self.sample_rate_spin.setRange(22050, 192000)
        self.sample_rate_spin.setValue(44100)
        self.sample_rate_spin.setSingleStep(11025)
        self.sample_rate_spin.setSuffix(" Hz")
        audio_layout.addRow("Sample Rate:", self.sample_rate_spin)
        
        # BPM
        self.bpm_spin = QSpinBox()
        self.bpm_spin.setRange(20, 300)
        self.bpm_spin.setValue(120)
        self.bpm_spin.setSuffix(" BPM")
        audio_layout.addRow("Tempo:", self.bpm_spin)
        
        layout.addWidget(audio_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        create_btn = QPushButton("Create Project")
        create_btn.setObjectName("generateBtn")
        create_btn.setDefault(True)
        create_btn.clicked.connect(self.accept_project)
        button_layout.addWidget(create_btn)
        
        layout.addLayout(button_layout)
        
    def browse_location(self):
        """Browse for project location"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Location",
            os.path.dirname(self.path_edit.text())
        )
        
        if directory:
            project_name = self.name_edit.text() or "Untitled Project"
            self.path_edit.setText(os.path.join(directory, project_name))
    
    def accept_project(self):
        """Validate and accept"""
        self.project_name = self.name_edit.text().strip()
        
        if not self.project_name:
            self.project_name = "Untitled Project"
            self.name_edit.setText(self.project_name)
        
        # Update path with correct name
        directory = os.path.dirname(self.path_edit.text())
        self.project_path = os.path.join(directory, self.project_name)
        
        # Create project directory
        os.makedirs(self.project_path, exist_ok=True)
        
        self.sample_rate = self.sample_rate_spin.value()
        self.bpm = self.bpm_spin.value()
        
        self.accept()
    
    def get_project_data(self):
        """Get project data"""
        return {
            'name': self.project_name,
            'path': self.project_path,
            'sample_rate': self.sample_rate,
            'bpm': self.bpm
        }
