"""
MIDI Manager - Handles MIDI Input/Output and Device Management
"""

import threading
import time
import mido
import rtmidi
from PyQt5.QtCore import QObject, pyqtSignal

class MidiManager(QObject):
    """
    Manages MIDI devices and routing.
    Emits signals when MIDI messages are received.
    """
    
    # Signals
    midi_message_received = pyqtSignal(object)  # mido.Message
    device_list_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.input_port = None
        self.output_port = None
        self.input_name = None
        self.output_name = None
        self.is_active = False
        
        # Background listener thread
        self._stop_event = threading.Event()
        self._listener_thread = None

    def get_input_devices(self):
        """Get list of available MIDI input ports"""
        try:
            return mido.get_input_names()
        except Exception as e:
            print(f"Error listing MIDI inputs: {e}")
            return []

    def get_output_devices(self):
        """Get list of available MIDI output ports"""
        try:
            return mido.get_output_names()
        except Exception as e:
            print(f"Error listing MIDI outputs: {e}")
            return []

    def open_input(self, port_name):
        """Open a MIDI input port"""
        if self.input_port:
            self.close_input()
            
        try:
            self.input_port = mido.open_input(port_name, callback=self._mid_callback)
            self.input_name = port_name
            self.is_active = True
            print(f"🎹 MIDI Input Opened: {port_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to open MIDI input {port_name}: {e}")
            return False

    def close_input(self):
        """Close current input port"""
        if self.input_port:
            self.input_port.close()
            self.input_port = None
            self.input_name = None
            self.is_active = False

    def _mid_callback(self, msg):
        """Callback for incoming MIDI messages"""
        self.midi_message_received.emit(msg)
        
    def send_message(self, msg):
        """Send a MIDI message to output"""
        if self.output_port:
            self.output_port.send(msg)
            
    def open_output(self, port_name):
        """Open a MIDI output port"""
        if self.output_port:
            self.output_port.close()
            
        try:
            self.output_port = mido.open_output(port_name)
            self.output_name = port_name
            print(f"🎹 MIDI Output Opened: {port_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to open MIDI output {port_name}: {e}")
            return False
            
    def refresh_devices(self):
        """Force refresh of device lists (mostly for UI updates)"""
        self.device_list_changed.emit()
