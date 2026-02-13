"""
Plugin Browser - Widget to browse and drag plugins
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QLabel, 
    QLineEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDrag, QIcon

class PluginList(QListWidget):
    """Draggable list of plugins"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
            
        mime = QMimeData()
        mime.setText(item.text())
        mime.setData("application/x-plugin", item.text().encode())
        
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec_(Qt.CopyAction)

class PluginBrowser(QWidget):
    """
    Panel to browse VST3 plugins.
    Allows dragging plugins to mixer/tracks.
    """
    
    plugin_selected = pyqtSignal(str) # plugin_name
    
    def __init__(self, plugin_manager):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header = QLabel("VST3 PLUGINS")
        header.setStyleSheet("font-weight: bold; color: #aaa; letter-spacing: 1px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search...")
        layout.addWidget(self.search)
        
        # Scan Button
        self.scan_btn = QPushButton("Scan Plugins")
        layout.addWidget(self.scan_btn)
        
        # List
        self.list = PluginList()
        self.list.setStyleSheet("""
            QListWidget {
                background: #1e1e1e;
                border: none;
                color: #ddd;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background: #00d4ff;
                color: black;
            }
        """)
        self.list.itemDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.list)
        
    def connect_signals(self):
        self.scan_btn.clicked.connect(self.plugin_manager.scan_plugins)
        self.plugin_manager.plugin_scanned.connect(self.add_plugin)
        self.search.textChanged.connect(self.filter_list)
        
    def on_double_click(self, item):
        self.plugin_selected.emit(item.text())
        
    def add_plugin(self, name, path):
        self.list.addItem(name)
        
    def filter_list(self, text):
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
