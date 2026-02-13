"""
Generator Panel - Beat Generation & Sequencing Controls (Right Panel)
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QScrollArea
from PyQt5.QtCore import Qt
from ui.widgets.knob import RotaryKnob
from ui.widgets.sequencer import StepSequencer

class GeneratorPanel(QWidget):
    """
    Right panel containing:
    1. Beat Generator controls (Knobs)
    2. Pattern Sequencer
    3. Mixer (Bottom)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # 1. Beat Generator Section
        gen_group = QGroupBox("Beat Generator")
        gen_layout = QVBoxLayout(gen_group)
        
        # Knobs Row
        knobs_layout = QHBoxLayout()
        
        self.knob_complexity = RotaryKnob(suffix="%")
        self.knob_complexity_lbl = QLabel("AI Complexity")
        self.knob_complexity_lbl.setAlignment(Qt.AlignCenter)
        
        self.knob_tempo = RotaryKnob(min_val=60, max_val=200, value=90, suffix=" BPM")
        self.knob_tempo_lbl = QLabel("Tempo")
        self.knob_tempo_lbl.setAlignment(Qt.AlignCenter)
        
        k1_box = QVBoxLayout()
        k1_box.addWidget(self.knob_complexity, 0, Qt.AlignCenter)
        k1_box.addWidget(self.knob_complexity_lbl)
        
        k2_box = QVBoxLayout()
        k2_box.addWidget(self.knob_tempo, 0, Qt.AlignCenter)
        k2_box.addWidget(self.knob_tempo_lbl)
        
        knobs_layout.addLayout(k1_box)
        knobs_layout.addLayout(k2_box)
        
        gen_layout.addLayout(knobs_layout)
        layout.addWidget(gen_group)
        
        # 2. Sequencer Section
        seq_group = QGroupBox("Pattern Sequencer")
        seq_layout = QVBoxLayout(seq_group)
        self.sequencer = StepSequencer()
        seq_layout.addWidget(self.sequencer)
        layout.addWidget(seq_group)
        
        # 3. Mixer Selection (Mini)
        # Placeholder for mixer faders
        mix_group = QGroupBox("Mixer")
        mix_layout = QHBoxLayout(mix_group)
        mix_layout.addWidget(QLabel("Vol / Pan / Mute"))
        layout.addWidget(mix_group)
        
        layout.addStretch()
