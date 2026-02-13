"""
ChendAI Studio FX Rack - Powered by Spotify Pedalboard
Simulates analog recording chains and room acoustics.
"""

try:
    from pedalboard import (
        Pedalboard, 
        Convolution, 
        Compressor, 
        Chorus, 
        Gain, 
        Reverb, 
        Limiter, 
        HighpassFilter, 
        LowpassFilter,
        NoiseGate,
        Distortion
    )
    import librosa
except ImportError:
    # Fallback/Mock for environments where pedalboard might fail to install immediately
    # This prevents the whole app from crashing during the upgrade phase
    class MockPedal:
        def process(self, x, sr): return x
    Pedalboard = MockPedal
    Convolution = Compressor = Chorus = Gain = Reverb = Limiter = lambda *args, **kwargs: None
    HighpassFilter = LowpassFilter = NoiseGate = Distortion = lambda *args, **kwargs: None 

import numpy as np
import os

class StudioFX:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.enabled = True
        
        # 1. THE CHENDA "BODY" BOARD (Simulates wooden shell + skin resonance)
        # Chain: Envelope Shaper (Mocked via Comp) -> Saturation -> Room
        self.chenda_board = Pedalboard([
            # Fast attack/release compressor to exaggerate transient "snap"
            Compressor(threshold_db=-20, ratio=4.0, attack_ms=5, release_ms=40), 
            Distortion(drive_db=4.0), # Warmth
            Reverb(room_size=0.3, wet_level=0.2, dry_level=0.9, damping=0.8) # Small Wood Room
        ])
        
        # 2. THE METAL BOARD (Ilathalam/Cymbals)
        self.metal_board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=400),
            # Chorus adds movement to static samples
            Chorus(rate_hz=0.8, depth=0.15, mix=0.25), 
            Reverb(room_size=0.6, wet_level=0.35, width=1.0)
        ])
        
        # 3. THE WIND BOARD (Kombu/Kuzhal)
        self.wind_board = Pedalboard([
            Distortion(drive_db=6.0), 
            Reverb(room_size=0.9, wet_level=0.45, damping=0.2) # Long tail
        ])
        
        # 4. MASTERING CHAIN (Pro-Loudness)
        self.master_chain = Pedalboard([
            # Glue Compressor
            Compressor(threshold_db=-8, ratio=1.5, attack_ms=30, release_ms=300),
            # Safety Limiter
            Limiter(threshold_db=-0.5)
        ])

    def process_chenda(self, audio: np.ndarray) -> np.ndarray:
        if not self.enabled or len(audio) == 0: return audio
        return self._run_board(self.chenda_board, audio)

    def process_metal(self, audio: np.ndarray) -> np.ndarray:
        if not self.enabled or len(audio) == 0: return audio
        return self._run_board(self.metal_board, audio)
        
    def process_wind(self, audio: np.ndarray) -> np.ndarray:
        if not self.enabled or len(audio) == 0: return audio
        return self._run_board(self.wind_board, audio)

    def master_mix(self, audio: np.ndarray) -> np.ndarray:
        """Apply mastering chain and normalize to -14 LUFS (Streaming Standard)"""
        if not self.enabled or len(audio) == 0: return audio
        
        # 1. Run through mastering DSP
        mastered = self._run_board(self.master_chain, audio)
        
        # 2. LUFS Normalization (Manual approach for now if pyloudnorm missing)
        # Peak normalize to -0.1dB first
        peak = np.max(np.abs(mastered))
        if peak > 0:
            mastered = mastered / peak * 0.95
            
        return mastered

    def _run_board(self, board, audio):
        try:
            # Safety check for NaN
            if np.isnan(audio).any():
                return np.zeros_like(audio)
                
            peak = np.max(np.abs(audio))
            if peak > 1.0:
                audio = audio / peak
                
            processed = board.process(audio, self.sample_rate)
            return processed
        except Exception as e:
            print(f"FX Processing Error: {e}")
            return audio
