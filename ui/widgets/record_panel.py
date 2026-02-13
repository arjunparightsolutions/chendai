"""
Record Panel - UI for audio recording control
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QComboBox, QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

class RecordPanel(QWidget):
    """
    Panel for checking input levels and controlling recording.
    """
    
    def __init__(self, recorder, parent=None):
        super().__init__(parent)
        self.recorder = recorder
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        group = QGroupBox("Input / Recording")
        group_layout = QVBoxLayout(group)
        
        # Device Selector
        dev_layout = QHBoxLayout()
        dev_layout.addWidget(QLabel("Input:"))
        self.device_combo = QComboBox()
        self.refresh_devices()
        self.device_combo.currentIndexChanged.connect(self.on_device_changed)
        dev_layout.addWidget(self.device_combo, stretch=1)
        
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(24, 24)
        refresh_btn.setToolTip("Refresh Devices")
        refresh_btn.clicked.connect(self.refresh_devices)
        dev_layout.addWidget(refresh_btn)
        
        group_layout.addLayout(dev_layout)
        
        # Control Buttons
        btn_layout = QHBoxLayout()
        
        self.monitor_btn = QPushButton("Monitor")
        self.monitor_btn.setCheckable(True)
        self.monitor_btn.toggled.connect(self.toggle_monitoring)
        
        self.record_btn = QPushButton("● Record")
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #bd2c00;
                color: white;
                font-weight: bold;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #a02500; }
            QPushButton:checked { 
                background-color: #ff0000; 
                border: 2px solid white;
            }
        """)
        self.record_btn.setCheckable(True)
        self.record_btn.clicked.connect(self.toggle_recording)
        
        btn_layout.addWidget(self.monitor_btn)
        btn_layout.addWidget(self.record_btn)
        
        group_layout.addLayout(btn_layout)
        
        # Level Meter
        self.meter = QProgressBar()
        self.meter.setRange(-60, 0)
        self.meter.setValue(-60)
        self.meter.setTextVisible(False)
        self.meter.setFixedHeight(10)
        self.meter.setStyleSheet("""
            QProgressBar {
                background-color: #222;
                border: 1px solid #444;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00cc00, stop:0.7 #ffff00, stop:1 #ff0000);
            }
        """)
        group_layout.addWidget(self.meter)
        
        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-size: 10px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.status_label)
        
        layout.addWidget(group)
        
    def connect_signals(self):
        # Connect recorder signals
        self.recorder.level_updated.connect(self.update_meter)
        self.recorder.recording_started.connect(self.on_recording_started)
        self.recorder.recording_stopped.connect(self.on_recording_stopped)
        self.recorder.error_occurred.connect(self.on_error)
        
    def refresh_devices(self):
        self.device_combo.clear()
        devices = self.recorder.get_input_devices()
        for dev in devices:
            self.device_combo.addItem(f"{dev['name']} ({dev['channels']} ch)", dev['id'])
            if dev['default']:
                self.device_combo.setCurrentIndex(self.device_combo.count() - 1)
                
    def on_device_changed(self, index):
        if index >= 0:
            device_id = self.device_combo.itemData(index)
            self.recorder.set_device(device_id)
            
    def toggle_monitoring(self, checked):
        if checked:
            self.recorder.start_monitoring()
            self.monitor_btn.setText("Stop Mon")
            self.status_label.setText("Monitoring...")
        else:
            self.recorder.stop_monitoring()
            self.monitor_btn.setText("Monitor")
            self.status_label.setText("Ready")
            self.meter.setValue(-60)
            
        # Disable monitor button if recording
        self.monitor_btn.setEnabled(not self.recorder.is_recording)
            
    def toggle_recording(self, checked):
        if checked:
            # Start recording
            self.recorder.start_recording()
            self.monitor_btn.setChecked(False)
            self.monitor_btn.setEnabled(False)
            self.device_combo.setEnabled(False)
            self.status_label.setText("🔴 Recording...")
            self.status_label.setStyleSheet("color: #ff4444; font-weight: bold;")
        else:
            # Stop recording
            path = self.recorder.stop_recording()
            self.monitor_btn.setEnabled(True)
            self.device_combo.setEnabled(True)
            self.status_label.setText("Recorded")
            self.status_label.setStyleSheet("color: #888;")
            self.record_btn.setChecked(False) # Ensure UI reflects state
            
    def update_meter(self, level_db):
        # Update progress bar (level in dB)
        # Map -60dB to 0dB range to usage 
        try:
            val = int(level_db)
            if val < -60: val = -60
            if val > 0: val = 0
            self.meter.setValue(val)
        except:
            pass
            
    def on_recording_started(self, path):
        pass # UI already updated in toggle
        
    def on_recording_stopped(self):
        pass # UI already updated
        
    def on_error(self, msg):
        self.status_label.setText("Error!")
        self.status_label.setToolTip(msg)
        self.record_btn.setChecked(False)
        self.monitor_btn.setChecked(False)
        self.device_combo.setEnabled(True)
