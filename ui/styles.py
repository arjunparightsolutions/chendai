"""
ChendAI Styles - Global QSS
"""

STYLE_SHEET = """
/* Global */
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #111;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #444;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #ffd700;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #333;
    border-radius: 4px;
}
QTabBar::tab {
    background: #2b2b2b;
    color: #888;
    padding: 8px 15px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #3c3f41;
    color: #ffd700; /* Gold */
    border-bottom: 2px solid #ffd700;
}
QTabBar::tab:hover {
    background: #333;
    color: #fff;
}

/* GroupBox */
QGroupBox {
    border: 1px solid #333;
    border-radius: 6px;
    margin-top: 20px;
    padding-top: 10px;
    font-weight: bold;
    color: #ffd700;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    left: 10px;
}

/* Buttons */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3a3a3a, stop:1 #2b2b2b);
    border: 1px solid #111;
    border-radius: 4px;
    color: #ddd;
    padding: 6px 12px;
    font-weight: bold;
}
QPushButton:hover {
    background: #444;
    border: 1px solid #666;
    color: #fff;
}
QPushButton:pressed {
    background: #222;
}

/* Generate Button Special */
QPushButton#generateBtn {
    background: qlineargradient(x1:0, y1:0.5, x2:1, y2:0.5, stop:0 #998100, stop:1 #ffd700);
    color: #000;
    border: none;
}
QPushButton#generateBtn:hover {
    background: #ffea55;
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox, QSpinBox {
    background-color: #111;
    border: 1px solid #333;
    border-radius: 4px;
    color: #fff;
    padding: 4px;
    selection-background-color: #ffd700;
    selection-color: #000;
}
QComboBox::drop-down {
    border: none;
    background: transparent;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #888;
    margin-right: 5px;
}

/* Slider */
QSlider::groove:horizontal {
    border: 1px solid #111;
    height: 6px;
    background: #222;
    margin: 2px 0;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffd700;
    border: 1px solid #111;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #333;
    border-radius: 4px;
    text-align: center;
    background: #111;
    color: #fff;
}
QProgressBar::chunk {
    background-color: #ffd700;
    width: 10px;
}

/* Panel Headers */
QLabel#panelHeader {
    background: #2b2b2b;
    color: #ddd;
    font-weight: bold;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    letter-spacing: 2px;
}

/* Status Bar */
QStatusBar {
    background: #111;
    color: #888;
    border-top: 1px solid #333;
}
"""
