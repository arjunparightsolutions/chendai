"""
FX Rack - Dialog to manage plugins on a track
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel, QSplitter, QWidget
)
from PyQt5.QtCore import Qt
from ui.widgets.plugin_editor import GenericPluginEditor

class FXRackDialog(QDialog):
    """
    Dialog showing the chain of effects for a track.
    Allows opening editors for each plugin.
    """
    
    def __init__(self, track_name, plugins, parent=None):
        super().__init__(parent)
        self.track_name = track_name
        self.plugins = plugins # List of plugin instances
        
        self.setWindowTitle(f"FX Rack - {track_name}")
        self.resize(800, 600)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Plugin List
        list_container = QWidget()
        list_layout = QVBoxLayout(list_container)
        
        list_label = QLabel("Plugins")
        self.plugin_list = QListWidget()
        self.plugin_list.itemClicked.connect(self.on_plugin_selected)
        
        # Populate list
        for p in self.plugins:
            name = type(p).__name__
            self.plugin_list.addItem(name)
            
        list_layout.addWidget(list_label)
        list_layout.addWidget(self.plugin_list)
        
        # Right: Editor Container
        self.editor_container = QWidget()
        self.editor_layout = QVBoxLayout(self.editor_container)
        self.editor_layout.addWidget(QLabel("Select a plugin to edit"))
        
        splitter.addWidget(list_container)
        splitter.addWidget(self.editor_container)
        splitter.setSizes([200, 600])
        
        layout.addWidget(splitter)
        
    def on_plugin_selected(self, item):
        """Show editor for selected plugin"""
        # Clear current editor
        while self.editor_layout.count():
            child = self.editor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        index = self.plugin_list.row(item)
        if index < 0 or index >= len(self.plugins):
            return
            
        plugin = self.plugins[index]

        # Check if native editor supported (VST3)
        if hasattr(plugin, 'show_editor'):
            btn = QPushButton("Open Native Editor")
            btn.clicked.connect(plugin.show_editor)
            self.editor_layout.addWidget(btn)
            
            # Show generic as fallback or addition? Just button for now.
            label = QLabel("(External Window)")
            label.setAlignment(Qt.AlignCenter)
            self.editor_layout.addWidget(label)
        else:
            # Use generic editor (Built-in)
            editor = GenericPluginEditor(plugin)
            self.editor_layout.addWidget(editor)
