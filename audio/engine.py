"""
Audio Engine - Real-time playback and processing using SoundDevice and Pedalboard
"""

import sounddevice as sd
import soundfile as sf
import numpy as np
from pedalboard import Pedalboard
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import threading
import time

class AudioEngine(QObject):
    """
    Manages real-time audio playback and effect processing.
    Replaces Pygame mixer.
    """
    
    playback_finished = pyqtSignal()
    position_changed = pyqtSignal(float) # current time in seconds
    
    def __init__(self, plugin_manager):
        super().__init__()
        self.plugin_manager = plugin_manager
        
        self.stream = None
        self.audio_data = None
        self.sample_rate = 44100
        self.current_frame = 0
        self.is_playing = False
        self.frames_per_buffer = 1024
        
        # Audio lock to prevent race conditions during updates
        self.lock = threading.Lock()
        
    def load_audio(self, file_path):
        """Load audio file into memory"""
        try:
            data, fs = sf.read(file_path, dtype='float32')
            
            # Handle channels
            if len(data.shape) == 1:
                # Mono to Stereo
                data = np.stack([data, data], axis=1)
            
            with self.lock:
                self.audio_data = data
                self.sample_rate = fs
                self.current_frame = 0
                
            print(f"🎵 Loaded audio: {file_path} ({fs}Hz)")
            return True
        except Exception as e:
            print(f"❌ Failed to load audio: {e}")
            return False
            
    def play(self):
        """Start or resume playback"""
        if self.audio_data is None:
            return
            
        if self.is_playing:
            return
            
        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,
                blocksize=self.frames_per_buffer,
                callback=self.audio_callback,
                finished_callback=self.on_stream_finished
            )
            self.stream.start()
            self.is_playing = True
            
            # Start timer for UI updates (position)
            self.timer = QTimer()
            self.timer.timeout.connect(self.emit_position)
            self.timer.start(50) # 50ms update
            
        except Exception as e:
            print(f"❌ Failed to start stream: {e}")
            
    def pause(self):
        """Pause playback"""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        self.is_playing = False
        if hasattr(self, 'timer'):
            self.timer.stop()
            
    def stop(self):
        """Stop playback and reset position"""
        self.pause()
        self.current_frame = 0
        self.emit_position()
        
    def audio_callback(self, outdata, frames, time, status):
        """Real-time processing callback"""
        if status:
            print(f"⚠️ Audio Status: {status}")
            
        with self.lock:
            if self.audio_data is None:
                outdata[:] = 0
                return
                
            # Calculate remaining frames
            remaining = len(self.audio_data) - self.current_frame
            
            if remaining <= 0:
                outdata[:] = 0
                raise sd.CallbackStop
                
            # Get chunk
            n_frames = min(remaining, frames)
            chunk = self.audio_data[self.current_frame : self.current_frame + n_frames]
            
            # Process Effect Chain
            # For now, we mix everything to a master bus.
            # Ideally, we process tracks individually then mix, but here we just have one stereo file (the backing track/generated mix).
            # We'll apply the chain of the FIRST track as a "Master" chain for now, or sum them.
            
            # Let's apply Track 1's effects to the master output for demonstration
            # In a real DAW, we'd have a mix graph.
            
            processed_chunk = chunk
            
            # Apply all loaded plugins sequentially (simulate Master Bus)
            # We iterate through all tracks and verify if they have plugins.
            # Since this is a simple stereo play, we treat it as "Track 1" or Master.
            
            # Temporary: Apply Track 0 (Master) chain if exists, or just iterate all valid chains
            # Better: Let's assume Track 0 is where we put effects for the mix.
            
            # Quick hack for Sprint 6: Summing is complex. Let's just apply Track 0's chain to the output.
            chain = self.plugin_manager.get_chain(0) # Track 1
            if chain:
                 processed_chunk = chain(chunk, self.sample_rate, reset=False)
            
            # Write to output
            outdata[:n_frames] = processed_chunk
            
            # Zero padding if needed
            if n_frames < frames:
                outdata[n_frames:] = 0
                
            self.current_frame += n_frames
            
    def on_stream_finished(self):
        """Called when stream finishes"""
        self.is_playing = False
        self.current_frame = 0
        self.playback_finished.emit()
        
    def emit_position(self):
        """Emit current position signal"""
        if self.sample_rate > 0:
            pos_sec = self.current_frame / self.sample_rate
            self.position_changed.emit(pos_sec)
            
    def get_duration(self):
        if self.audio_data is not None:
            return len(self.audio_data) / self.sample_rate
        return 0
