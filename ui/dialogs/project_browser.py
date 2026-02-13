"""
Project Browser - Recent projects list
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from datetime import datetime
import os


class ProjectBrowserDialog(QDialog):
    """Dialog for browsing and opening recent projects"""
    
    def __init__(self, project_manager, parent=None):
        super().__init__(parent)
        
        self.project_manager = project_manager
        self.selected_project = None
        
        self.init_ui()
        self.load_recent_projects()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Open Project")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Recent Projects")
        header_font = QFont("Segoe UI", 14, QFont.Bold)
        header.setFont(header_font)
        layout.addWidget(header)
        
        # Projects list
        self.projects_list = QListWidget()
        self.projects_list.setIconSize(QSize(48, 48))
        self.projects_list.itemDoubleClicked.connect(self.on_project_double_clicked)
        layout.addWidget(self.projects_list, stretch=1)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_project)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_project)
        button_layout.addWidget(browse_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.open_btn = QPushButton("Open Project")
        self.open_btn.setObjectName("generateBtn")
        self.open_btn.setDefault(True)
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_project)
        button_layout.addWidget(self.open_btn)
        
        layout.addLayout(button_layout)
        
        # Connect selection changed
        self.projects_list.itemSelectionChanged.connect(self.on_selection_changed)
        
    def load_recent_projects(self):
        """Load recent projects from database"""
        self.projects_list.clear()
        
        projects = self.project_manager.get_recent_projects(limit=20)
        
        if not projects:
            # Show empty state
            item = QListWidgetItem("No recent projects. Create a new project to get started!")
            item.setFlags(Qt.NoItemFlags)
            self.projects_list.addItem(item)
            return
        
        for project in projects:
            item = QListWidgetItem()
            
            # Project info
            name = project['name']
            path = project['file_path']
            
            # Format last opened time
            if project['last_opened']:
                last_opened = datetime.fromisoformat(project['last_opened'])
                time_str = last_opened.strftime("%B %d, %Y at %I:%M %p")
            else:
                time_str = "Never opened"
            
            # Check if project still exists
            exists = os.path.exists(path)
            status = "✓" if exists else "⚠️ Missing"
            
            # Build display text
            text = f"🎼 {name}\n"
            text += f"   📁 {path}\n"
            text += f"   🕒 {time_str}  {status}"
            
            item.setText(text)
            item.setData(Qt.UserRole, project['id'])
            
            if not exists:
                item.setForeground(Qt.gray)
            
            self.projects_list.addItem(item)
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = len(self.projects_list.selectedItems()) > 0
        self.open_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def on_project_double_clicked(self, item):
        """Handle double-click"""
        self.open_project()
    
    def open_project(self):
        """Open selected project"""
        items = self.projects_list.selectedItems()
        if not items:
            return
        
        project_id = items[0].data(Qt.UserRole)
        self.selected_project = self.project_manager.get_project(project_id)
        
        if not self.selected_project:
            QMessageBox.warning(self, "Error", "Project not found in database.")
            return
        
        # Check if project path exists
        if not os.path.exists(self.selected_project['file_path']):
            QMessageBox.warning(
                self,
                "Project Missing",
                f"Project folder not found:\n{self.selected_project['file_path']}\n\n"
                "The project may have been moved or deleted."
            )
            return
        
        # Update last opened
        self.project_manager.update_last_opened(project_id)
        
        self.accept()
    
    def browse_project(self):
        """Browse for project file"""
        from PyQt5.QtWidgets import QFileDialog
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Folder",
            os.path.expanduser("~/Documents/ChendAI Studio")
        )
        
        if directory:
            # Check if this project exists in database
            project = self.project_manager.get_project_by_path(directory)
            
            if project:
                self.selected_project = project
                self.project_manager.update_last_opened(project['id'])
                self.accept()
            else:
                # Not in database, try to import
                QMessageBox.information(
                    self,
                    "Import Project",
                    "This project is not in the database. Creating new entry..."
                )
                
                project_name = os.path.basename(directory)
                project_id = self.project_manager.create_project(
                    name=project_name,
                    file_path=directory
                )
                
                self.selected_project = self.project_manager.get_project(project_id)
                self.accept()
    
    def delete_project(self):
        """Delete selected project"""
        items = self.projects_list.selectedItems()
        if not items:
            return
        
        project_id = items[0].data(Qt.UserRole)
        project = self.project_manager.get_project(project_id)
        
        reply = QMessageBox.question(
            self,
            "Delete Project",
            f"Are you sure you want to remove '{project['name']}' from recent projects?\n\n"
            "This will NOT delete the project files, only remove it from the list.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.project_manager.delete_project(project_id)
            self.load_recent_projects()
