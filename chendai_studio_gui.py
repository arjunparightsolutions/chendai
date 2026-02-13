"""
ChendAI Studio - Professional PyQt5 GUI
Beautiful, modern Digital Audio Workstation for Kerala Traditional Percussion
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon, QPalette, QColor
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from ui.main_window import ChendAIMainWindow


def setup_application():
    """Configure application settings and theme"""
    # Enable high DPI support BEFORE QApplication creation
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Application metadata
    app.setApplicationName("ChendAI Studio")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Right Solutions A.I")
    
    # Set application-wide dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(26, 26, 46))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(22, 33, 62))
    palette.setColor(QPalette.AlternateBase, QColor(32, 32, 52))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(42, 42, 62))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(0, 212, 255))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    
    app.setPalette(palette)
    
    # Load stylesheet
    stylesheet_path = os.path.join(os.path.dirname(__file__), 'ui', 'styles', 'dark_theme.qss')
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, 'r') as f:
            app.setStyleSheet(f.read())
    
    return app


def main():
    """Main application entry point"""
    print("=" * 70)
    print("🥁 ChendAI Studio Pro v2.0")
    print("=" * 70)
    print("Starting PyQt5 GUI...")
    
    app = setup_application()
    
    # Create and show main window
    window = ChendAIMainWindow()
    window.show()
    
    print("✅ GUI Ready!")
    print("=" * 70)
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
