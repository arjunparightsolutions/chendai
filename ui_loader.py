from PySide6.QtWidgets import (QSplashScreen, QProgressBar, QLabel, QVBoxLayout, 
                               QWidget, QTextEdit, QApplication)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QPixmap, QColor, QPainter, QFont, QLinearGradient

class LogHandler(QObject):
    """
    Handles log emission to the UI.
    """
    log_signal = Signal(str)

    def write(self, text):
        if text.strip():
            self.log_signal.emit(text.strip())

    def flush(self):
        pass

class LoaderWindow(QSplashScreen):
    def __init__(self):
        # Create a dummy pixmap for the splash screen
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(10, 10, 10)) # Dark background
        super().__init__(pixmap)
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main Layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        self.title_label = QLabel("CHENDAI STUDIO PRO")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #fbbf24;
            font-size: 32px;
            font-weight: bold;
            font-family: 'Segoe UI', sans-serif;
            letter-spacing: 2px;
        """)
        self.main_layout.addWidget(self.title_label)
        
        self.subtitle_label = QLabel("AI-Powered Kerala Percussion Engine")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setStyleSheet("color: #a1a1aa; font-size: 14px; margin-bottom: 20px;")
        self.main_layout.addWidget(self.subtitle_label)
        
        self.main_layout.addStretch()
        
        # Log Output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #18181b;
                color: #22c55e;
                border: 1px solid #27272a;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                padding: 5px;
            }
        """)
        self.log_output.setFixedHeight(120)
        self.main_layout.addWidget(self.log_output)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #27272a;
                border: none;
                border-radius: 2px;
                height: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #fbbf24;
                border-radius: 2px;
            }
        """)
        self.progress_bar.setTextVisible(False)
        self.main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #71717a; font-size: 10px; margin-top: 5px;")
        self.main_layout.addWidget(self.status_label)
        
    def paintEvent(self, event):
        # Draw gradient background
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#09090b"))
        gradient.setColorAt(1, QColor("#18181b"))
        painter.fillRect(self.rect(), gradient)
        
        # Draw border
        painter.setPen(QColor("#27272a"))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def log(self, text):
        self.log_output.append(text)
        # Auto-scroll
        cursor = self.log_output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_output.setTextCursor(cursor)

    def set_progress(self, value, message=""):
        self.progress_bar.setValue(value)
        if message:
            self.status_label.setText(message)
            self.log(f"[INFO] {message}")
