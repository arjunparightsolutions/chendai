"""
Control Panel - AI Music Generation Controls
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QScrollArea, QFrame, QComboBox, QLineEdit, QTabWidget,
    QFormLayout, QSpinBox, QSlider, QCheckBox, QGroupBox, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from audio.recorder import AudioRecorder
from audio.midi_manager import MidiManager
from audio.plugin_manager import PluginManager
from ui.widgets.record_panel import RecordPanel
from ui.widgets.plugin_browser import PluginBrowser


class ControlPanel(QWidget):
    """Left panel with AI composition controls"""
    
    generate_clicked = pyqtSignal(dict)  # Emits generation parameters
    
    def __init__(self, plugin_manager):
        super().__init__()
        self.setObjectName("controlPanel")
        self.plugin_manager = plugin_manager
        
        self.use_natural_language = False
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Audio Recorder Panel (Global)
        self.recorder = AudioRecorder()
        self.midi_manager = MidiManager()
        # self.plugin_manager is already set
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #2b2d30;
                color: #aaa;
                padding: 8px 20px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #3c3f41;
                color: #fff;
                border-bottom: 2px solid #00d4ff;
            }
        """)
        
        # Tab 1: Library (Existing controls)
        library_tab = QWidget()
        self.setup_library_tab(library_tab)
        self.tabs.addTab(library_tab, "Library")
        
        # Tab 2: Plugins
        self.plugin_browser = PluginBrowser(self.plugin_manager)
        self.tabs.addTab(self.plugin_browser, "Plugins")
        
        main_layout.addWidget(self.tabs)
        
    def setup_library_tab(self, parent):
        """Setup the main library controls tab"""
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(15)
        
        # Record Panel
        self.record_panel = RecordPanel(self.recorder)
        layout.addWidget(self.record_panel)
        
        # MIDI Device Selector
        midi_group = QGroupBox("MIDI Input")
        midi_layout = QVBoxLayout(midi_group)
        self.midi_combo = QComboBox()
        self.midi_refresh_btn = QPushButton("Refresh MIDI")
        self.midi_refresh_btn.clicked.connect(self.refresh_midi_devices)
        self.midi_combo.currentIndexChanged.connect(self.on_midi_device_changed)
        
        midi_layout.addWidget(self.midi_combo)
        midi_layout.addWidget(self.midi_refresh_btn)
        layout.addWidget(midi_group)
        
        # Refresh initially
        self.refresh_midi_devices()
        
        # Scroll Area for composition controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setContentsMargins(15, 0, 15, 15)
        scroll_layout.setSpacing(20)
        
        # Compose Music Section
        compose_group = self.create_compose_section()
        scroll_layout.addWidget(compose_group)
        
        # CLI Debug Button
        scroll_layout.addSpacing(10)
        cli_btn = QPushButton("🖥️  CLI Debug Mode")
        cli_btn.clicked.connect(self.open_cli_terminal)
        self.style_cli_btn(cli_btn)
        scroll_layout.addWidget(cli_btn)

        # Pro Tips Section
        tips_group = self.create_tips_section()
        scroll_layout.addWidget(tips_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def style_cli_btn(self, btn):
        btn.setStyleSheet("""
            QPushButton {
                background-color: #2b3137;
                border: 1px solid #30363d;
                color: #c9d1d9;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #30363d;
                border-color: #8b949e;
            }
        """)

    def setup_export_ui(self, layout):
        """Setup export controls (placeholder for now)"""
        # Logic to be implemented later or if already exists in other methods
        pass

    def refresh_midi_devices(self):
        """Refresh MIDI input list"""
        self.midi_combo.clear()
        devices = self.midi_manager.get_input_devices()
        self.midi_combo.addItems(devices)
        
    def on_midi_device_changed(self, index):
        """Handle MIDI device selection"""
        if index >= 0:
            device_name = self.midi_combo.currentText()
            self.midi_manager.open_input(device_name)

    def open_cli_terminal(self):
        """Open CLI debug terminal"""
        from ui.dialogs.cli_dialog import CLIDialog
        dialog = CLIDialog(self)
        dialog.exec_()
        
    def create_compose_section(self):
        """Create composition controls"""
        group = QGroupBox("🎼 Compose Music")
        group.setObjectName("composeMusicGroup")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # Natural Language Toggle
        self.nl_checkbox = QCheckBox("Natural Language Mode")
        self.nl_checkbox.stateChanged.connect(self.toggle_mode)
        layout.addWidget(self.nl_checkbox)
        
        # Stack widget for switching between modes
        self.pattern_controls = self.create_pattern_controls()
        self.prompt_controls = self.create_prompt_controls()
        
        self.prompt_controls.hide()
        
        layout.addWidget(self.pattern_controls)
        layout.addWidget(self.prompt_controls)
        
        # Generate Button
        self.generate_btn = QPushButton("✨ Generate Music")
        self.generate_btn.setObjectName("generateBtn")
        self.generate_btn.setMinimumHeight(45)
        self.generate_btn.clicked.connect(self.on_generate)
        layout.addWidget(self.generate_btn)
        
        return group
        
    def create_pattern_controls(self):
        """Create traditional pattern selection controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        # Pattern Style
        pattern_label = QLabel("Pattern Style")
        pattern_label.setStyleSheet("font-weight: bold; color: #aaa;")
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems([
            "🥁 Panchari Melam (Temple)",
            "⚡ Pandi Melam (Powerful)",
            "🎯 Thayambaka (Solo)",
            "🎺 Panchavadyam (5 Instruments)"
        ])
        layout.addWidget(pattern_label)
        layout.addWidget(self.pattern_combo)
        
        # Duration
        duration_label = QLabel("Duration")
        duration_label.setStyleSheet("font-weight: bold; color: #aaa;")
        dur_layout = QHBoxLayout()
        self.duration_spin = QSpinBox()
        self.duration_spin.setMinimum(5)
        self.duration_spin.setMaximum(300)
        self.duration_spin.setValue(30)
        self.duration_spin.setSuffix(" seconds")
        dur_layout.addWidget(self.duration_spin)
        layout.addWidget(duration_label)
        layout.addLayout(dur_layout)
        
        # Orchestration Style
        orch_label = QLabel("Orchestration Style")
        orch_label.setStyleSheet("font-weight: bold; color: #aaa;")
        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems([
            "🏛️ Traditional (Authentic)",
            "⚡ Dynamic (AI Variations)",
            "🤝 Unison (Synchronized)",
            "🔄 Antiphonal (Call & Response)",
            "📚 Layered (Progressive)"
        ])
        layout.addWidget(orch_label)
        layout.addWidget(self.strategy_combo)
        
        return widget
        
    def create_prompt_controls(self):
        """Create natural language prompt controls"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        prompt_label = QLabel("Describe the music you want")
        prompt_label.setStyleSheet("font-weight: bold; color: #aaa;")
        layout.addWidget(prompt_label)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText(
            "e.g., Generate a traditional BGM for Kerala with chenda and cymbals, "
            "energetic temple festival atmosphere..."
        )
        self.prompt_text.setMinimumHeight(100)
        layout.addWidget(self.prompt_text)
        
        hint = QLabel("✨ Use natural language to describe any traditional Kerala music!")
        hint.setStyleSheet("color: #666; font-size: 11px; font-style: italic;")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        
        return widget
        
    def create_tips_section(self):
        """Create pro tips section"""
        group = QGroupBox("💡 Pro Tips")
        layout = QVBoxLayout(group)
        
        tips = [
            "Enable Natural Language for free-form descriptions",
            "Use headphones for immersive spatial audio",
            "Adjust mixer after generation for perfect mix",
            "Use Export to save high-quality files"
        ]
        
        for tip in tips:
            tip_label = QLabel(f"• {tip}")
            tip_label.setWordWrap(True)
            tip_label.setStyleSheet("color: #aaa; font-size: 11px; padding: 3px;")
            layout.addWidget(tip_label)
        
        return group
        
    def toggle_mode(self, state):
        """Toggle between pattern and prompt mode"""
        self.use_natural_language = (state == Qt.Checked)
        
        if self.use_natural_language:
            self.pattern_controls.hide()
            self.prompt_controls.show()
        else:
            self.prompt_controls.hide()
            self.pattern_controls.show()
            
    def on_generate(self):
        """Handle generate button click"""
        params = {
            'use_prompt': self.use_natural_language,
            'duration': self.duration_spin.value()
        }
        
        if self.use_natural_language:
            params['prompt'] = self.prompt_text.toPlainText()
        else:
            # Extract pattern name from combo text
            pattern_text = self.pattern_combo.currentText()
            pattern_map = {
                "Panchari": "panchari",
                "Pandi": "pandi",
                "Thayambaka": "thayambaka",
                "Panchavadyam": "panchavadyam"
            }
            for key, value in pattern_map.items():
                if key in pattern_text:
                    params['pattern'] = value
                    break
            
            # Extract strategy
            strategy_text = self.strategy_combo.currentText()
            strategy_map = {
                "Traditional": "traditional",
                "Dynamic": "dynamic",
                "Unison": "unison",
                "Antiphonal": "antiphonal",
                "Layered": "layered"
            }
            for key, value in strategy_map.items():
                if key in strategy_text:
                    params['strategy'] = value
                    break
        
        self.generate_clicked.emit(params)
