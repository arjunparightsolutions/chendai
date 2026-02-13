"""
Generic Plugin Editor - Auto-generated UI for VST3/Pedalboard parameters
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QDoubleSpinBox, QScrollArea
)
from PyQt5.QtCore import Qt

class GenericPluginEditor(QWidget):
    """
    Auto-generates sliders and knobs for plugin parameters.
    """
    
    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(type(self.plugin).__name__)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Scroll Area for parameters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        param_layout = QVBoxLayout(container)
        
        # Introspect parameters
        # Pedalboard plugins have properties like 'drive_db', 'cutoff_hz' etc.
        # But there isn't a unified .parameters dict for built-ins in all versions?
        # Let's check common attributes or just dir() filtering
        
        # Actually pedalboard objects usually have a way to inspect parameters.
        # But for valid python objects, we can just look for float/int properties that are not private.
        
        from pedalboard import Plugin
        
        # Get all properties that are float or int and settable
        for name in dir(self.plugin):
            if name.startswith("_"): continue
            
            try:
                # Get the attribute
                attr = getattr(self.plugin, name)
                prop = getattr(type(self.plugin), name, None)
                
                # Check if it's a property (likely a parameter)
                if isinstance(prop, property) and isinstance(attr, (int, float)):
                    self.add_parameter_control(param_layout, name, attr)
                    
            except:
                continue
                
        param_layout.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
        
    def add_parameter_control(self, layout, name, value):
        """Add control for a single parameter"""
        row = QHBoxLayout()
        
        label = QLabel(name.replace('_', ' ').title())
        label.setFixedWidth(120)
        
        # Spinbox for precise value
        spin = QDoubleSpinBox()
        spin.setRange(-10000, 10000) # Wide range
        spin.setValue(value)
        spin.setSingleStep(0.1)
        
        # Slider (mapped 0-1000 for granularity)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 1000)
        
        # Heuristic for slider range... this is tricky without metadata.
        # Let's just use spinbox for now as primary, slider is hard to map without min/max info.
        
        spin.valueChanged.connect(lambda v: setattr(self.plugin, name, v))
        
        row.addWidget(label)
        row.addWidget(spin)
        
        layout.addLayout(row)
