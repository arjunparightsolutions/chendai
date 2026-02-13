"""
CLI Debug Dialog - Embedded terminal for ChendAI CLI
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QPushButton, QComboBox, QCheckBox, QGroupBox
)
from PyQt5.QtCore import Qt, QProcess, QSettings
from PyQt5.QtGui import QFont, QColor, QTextCursor

class CLIDialog(QDialog):
    """Embedded CLI terminal for debugging and advanced generation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ChendAI CLI Debug Terminal")
        self.setMinimumSize(900, 600)
        
        self.process = None
        
        self.init_ui()
        self.load_history()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # --- Toolbar / Quick Actions ---
        toolbar_group = QGroupBox("Quick Actions")
        toolbar_layout = QHBoxLayout(toolbar_group)
        
        self.health_btn = QPushButton("🏥 Health Check")
        self.health_btn.clicked.connect(lambda: self.run_command("python chendai_cli.py --health-check"))
        
        self.list_patterns_btn = QPushButton("🥁 List Patterns")
        self.list_patterns_btn.clicked.connect(lambda: self.run_command("python chendai_cli.py --list-patterns"))
        
        self.debug_check = QCheckBox("Enable Debug Mode (--debug)")
        
        toolbar_layout.addWidget(self.health_btn)
        toolbar_layout.addWidget(self.list_patterns_btn)
        toolbar_layout.addWidget(self.debug_check)
        toolbar_layout.addStretch()
        
        layout.addWidget(toolbar_group)
        
        # --- Output Display ---
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 13px;
                border: 1px solid #30363d;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.output_display, stretch=1)
        
        # --- Command Input ---
        input_layout = QHBoxLayout()
        
        label = QLabel("🚀 Command:")
        label.setStyleSheet("font-weight: bold;")
        
        self.command_input = QComboBox()
        self.command_input.setEditable(True)
        self.command_input.setPlaceholderText("Enter CLI command (e.g., python chendai_cli.py --pattern panchari)")
        self.command_input.lineEdit().returnPressed.connect(self.execute_current_command)
        
        # Ensure the combo box expands properly
        from PyQt5.QtWidgets import QSizePolicy
        self.command_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        run_btn = QPushButton("Run")
        run_btn.setStyleSheet("""
            background-color: #238636;
            color: white;
            font-weight: bold;
        """)
        run_btn.clicked.connect(self.execute_current_command)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.output_display.clear)
        
        input_layout.addWidget(label)
        input_layout.addWidget(self.command_input, stretch=1)
        input_layout.addWidget(run_btn)
        input_layout.addWidget(clear_btn)
        
        layout.addLayout(input_layout)
        
        # Initial welcome message
        self.output_display.append("<span style='color:#58a6ff'><b>ChendAI CLI Debugger v1.0</b></span>")
        self.output_display.append("<span style='color:#8b949e'>Type commands below or use Quick Actions.</span>")
        self.output_display.append("<span style='color:#8b949e'>Try: <i>python chendai_cli.py --help</i></span><br>")

    def execute_current_command(self):
        command = self.command_input.currentText().strip()
        if not command:
            return
            
        # Add debug flag if checked/missing
        if self.debug_check.isChecked() and "--debug" not in command and "chendai_cli.py" in command:
            command += " --debug"
            
        self.run_command(command)
        
        # Add to history if unique
        if self.command_input.findText(command) == -1:
            self.command_input.addItem(command)
            self.save_history()

    def run_command(self, command):
        self.output_display.append(f"\n<span style='color:#79c0ff'>$ {command}</span>")
        self.output_display.moveCursor(QTextCursor.End)
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.on_process_finished)
        
        # Fix for Windows not finding python sometimes if not in path, though usually ok
        self.process.start(command)
        
        if not self.process.waitForStarted():
            self.output_display.append("<span style='color:#f85149'>❌ Failed to start process. check command syntax.</span>")

    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("utf8")
        self.output_display.insertPlainText(text)
        self.output_display.moveCursor(QTextCursor.End)
        
    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = bytes(data).decode("utf8")
        # Colorize error output
        self.output_display.append(f"<span style='color:#f85149'>{text}</span>")
        self.output_display.moveCursor(QTextCursor.End)

    def on_process_finished(self):
        self.output_display.append("<span style='color:#3fb950'>Process finished.</span>")
        self.output_display.moveCursor(QTextCursor.End)
        self.process = None

    def load_history(self):
        settings = QSettings("Right Solutions AI", "ChendAI Studio")
        history = settings.value("cli/history", [])
        if history:
            self.command_input.addItems(history)

    def save_history(self):
        history = [self.command_input.itemText(i) for i in range(self.command_input.count())]
        # Keep last 20
        history = history[-20:]
        settings = QSettings("Right Solutions AI", "ChendAI Studio")
        settings.setValue("cli/history", history)
