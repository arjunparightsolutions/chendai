"""
Step Sequencer - Rhythm Programming Widget
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal

class StepSequencer(QWidget):
    """
    16-step sequencer grid for programming beats.
    Rows: Chenda, Bass, Rhythm
    Cols: 16 steps
    """
    
    pattern_changed = pyqtSignal(dict) # {instrument: [0, 1, 0, ...]}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.instruments = ["Chenda", "Bass", "Rhythm"]
        self.steps = 16
        self.grid_buttons = {} # (row, col): button
        self.current_pattern = {inst: [0]*self.steps for inst in self.instruments}
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with page selector
        header = QHBoxLayout()
        header.addWidget(QLabel("PATTERN SEQUENCER"))
        layout.addLayout(header)
        
        # Grid
        grid_widget = QWidget()
        self.grid = QGridLayout(grid_widget)
        self.grid.setSpacing(4)
        
        # Labels column
        for row, inst in enumerate(self.instruments):
            lbl = QLabel(inst)
            lbl.setStyleSheet("color: #aaa; font-size: 10px; font-weight: bold;")
            self.grid.addWidget(lbl, row, 0)
            
            # Steps
            for col in range(self.steps):
                btn = QPushButton()
                btn.setFixedSize(20, 25)
                btn.setCheckable(True)
                btn.setProperty("step_btn", True)
                
                # Special styling for beats (every 4th)
                if col % 4 == 0:
                    btn.setStyleSheet(self.get_btn_style(is_beat=True))
                else:
                    btn.setStyleSheet(self.get_btn_style(is_beat=False))
                    
                btn.toggled.connect(lambda checked, r=row, c=col: self.on_step_toggled(r, c, checked))
                
                self.grid.addWidget(btn, row, col + 1)
                self.grid_buttons[(row, col)] = btn
                
        layout.addWidget(grid_widget)
        
    def get_btn_style(self, is_beat=False):
        color = "#444" if is_beat else "#333"
        return f"""
            QPushButton {{
                background-color: {color};
                border: none;
                border-radius: 2px;
            }}
            QPushButton:checked {{
                background-color: #ffd700;
                border: 1px solid #fff;
            }}
            QPushButton:hover {{
                border: 1px solid #888;
            }}
        """

    def on_step_toggled(self, row, col, checked):
        inst_name = self.instruments[row]
        self.current_pattern[inst_name][col] = 1 if checked else 0
        self.pattern_changed.emit(self.current_pattern)
