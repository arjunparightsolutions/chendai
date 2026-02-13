"""
Audio Recorder - Low-latency audio recording using sounddevice
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import os
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

class AudioRecorder(QObject):
    """
    Handles audio recording from input devices.
    Supports monitoring, level metering, and file saving.
    """
    
    # Signals
    level_updated = pyqtSignal(float)  # Peak level in dB
    recording_started = pyqtSignal(str) # File path
    recording_stopped = pyqtSignal(str) # File path
    error_occurred = pyqtSignal(str)
    
    def __init__(self, sample_rate=44100, channels=1):
        super().__init__()
        
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_id = None  # Default input device
        
        self.is_recording = False
        self.is_monitoring = False
        
        self.stream = None
        self.audio_file = None
        self.output_path = None
        
        # Buffer for level metering
        self.peak = 0.0
        
    def get_input_devices(self):
        """Get list of available input devices"""
        try:
            devices = sd.query_devices()
            input_devices = []
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    input_devices.append({
                        'id': i,
                        'name': dev['name'],
                        'channels': dev['max_input_channels'],
                        'default': i == sd.default.device[0]
                    })
            return input_devices
        except Exception as e:
            self.error_occurred.emit(f"Failed to query devices: {e}")
            return []
            
    def set_device(self, device_id):
        """Set input device"""
        self.device_id = device_id
        
    def start_monitoring(self):
        """Start monitoring input levels without recording"""
        if self.is_recording or self.is_monitoring:
            return
            
        try:
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback
            )
            self.stream.start()
            self.is_monitoring = True
        except Exception as e:
            self.error_occurred.emit(f"Failed to start monitoring: {e}")
            
    def stop_monitoring(self):
        """Stop monitoring"""
        if not self.is_monitoring or self.is_recording:
            return
            
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
        self.is_monitoring = False
        self.level_updated.emit(-100.0)  # Reset meter
        
    def start_recording(self, output_dir="recordings", filename=None):
        """Start recording to file"""
        if self.is_recording:
            return
            
        # Stop monitoring if active (will restart as recording stream)
        if self.is_monitoring:
            self.stop_monitoring()
            
        try:
            # Setup output file
            os.makedirs(output_dir, exist_ok=True)
            
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"rec_{timestamp}.wav"
                
            self.output_path = os.path.join(output_dir, filename)
            
            # Open soundfile for writing
            self.audio_file = sf.SoundFile(
                self.output_path, 
                mode='w', 
                samplerate=self.sample_rate, 
                channels=self.channels
            )
            
            # Start stream
            self.stream = sd.InputStream(
                device=self.device_id,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._record_callback
            )
            self.stream.start()
            self.is_recording = True
            self.recording_started.emit(self.output_path)
            
        except Exception as e:
            self.error_occurred.emit(f"Failed to start recording: {e}")
            self.cleanup()
            
    def stop_recording(self):
        """Stop recording"""
        if not self.is_recording:
            return
            
        try:
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
                
            if self.audio_file:
                self.audio_file.close()
                self.audio_file = None
                
            self.is_recording = False
            self.recording_stopped.emit(self.output_path)
            self.level_updated.emit(-100.0)
            
            return self.output_path
            
        except Exception as e:
            self.error_occurred.emit(f"Error stopping recording: {e}")
            self.cleanup()
            return None
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback for monitoring"""
        if status:
            print(f"Stream status: {status}")
            
        # Calculate peak level in dB
        peak = np.max(np.abs(indata))
        db = 20 * np.log10(peak + 1e-9)  # Avoid log(0)
        self.level_updated.emit(db)
        
    def _record_callback(self, indata, frames, time, status):
        """Callback for recording"""
        if status:
            print(f"Record status: {status}")
            
        # Write to file
        if self.audio_file:
            self.audio_file.write(indata)
            
        # Update level meter
        peak = np.max(np.abs(indata))
        db = 20 * np.log10(peak + 1e-9)
        self.level_updated.emit(db)
        
    def cleanup(self):
        """Clean up resources"""
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
            self.stream = None
            
        if self.audio_file:
            try:
                self.audio_file.close()
            except:
                pass
            self.audio_file = None
            
        self.is_recording = False
        self.is_monitoring = False
