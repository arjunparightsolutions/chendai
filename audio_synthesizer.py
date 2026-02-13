"""
ChendAI ULTRA SPECTRAL Audio Synthesizer
PURE SPECTRAL MODELING SYNTHESIS (SMS)
NO PIANO ARTIFACTS. NO STRING MODELS. 100% PHYSICS.
"""

import numpy as np
from typing import Dict, Any, List
import soundfile as sf
import os
import spectral_engine
import studio_fx 

class AudioSynthesizer:
    """
    The Ultra-Spectral Synth.
    Relies 100% on the 5000-entry Spectral Database.
    Reconstructs sound atom-by-atom using Numba.
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        
        # Power up the Spectral Core
        print("⚛️  Initializing Numba Spectral Engine...")
        self.engine = spectral_engine.SpectralEngine(sample_rate)
        self.engine.load_db()
        
        # Initialize Studio Rack (Post-Processing)
        print("🎛️  Warming up Studio Vacuum Tubes...")
        self.fx = studio_fx.StudioFX(sample_rate)
        
        # Legacy map for pitch reference only (no synthesis)
        self.PITCH_REF = {
            'THAAM': 554.37,
            'DHEEM': 92.50,
            'NAM': 880.0,
            'URUTTU': 466.16,
            'CHAPU': 740.0
        }
    
    def synthesize_sound(self, params: Dict[str, Any], duration: float, velocity: float = 1.0) -> np.ndarray:
        """
        Synthesize sound using SPECTRAL MODELING ONLY.
        No algorithmic approximations.
        """
        sound_id = params.get('id', '')
        instrument = params.get('instrument', 'chenda')
        
        raw_audio = np.array([])
        
        # 1. IDENTIFY SPECTRAL CATEGORY
        category = "THAAM" # Default
        
        if instrument == 'chenda':
            if 'THAAM' in sound_id: category = "THAAM"
            elif 'DHEEM' in sound_id: category = "DHEEM"
            elif 'NAM' in sound_id: category = "NAM"
            elif 'URUTTU' in sound_id: category = "URUTTU"
            elif 'CHAPU' in sound_id: category = "CHAPU"
            elif 'OPPU' in sound_id: category = "CHAPU" # Muted slap similar spectral profile
            elif 'NAKKU' in sound_id: category = "NAM" # Light rim
        elif instrument == 'illathaalam':
            # Metal fits into NAM category spectrally (high inharmonic)
            # but we should probably add metal to DB. 
            # For now, we rely on the high-freq partials of NAM or a fallback.
            # Actually, standardizing on NAM for now as it's metallic.
            category = "NAM" 
        elif instrument == 'side_instrument':
             if 'KOMBU' in sound_id: category = "WIND"
             # For others, we map to closest physics or silence if not in DB
             elif 'KUZHAL' in sound_id: category = "WIND"
             else: category = "DHEEM"
             
        # 2. GENERATE AUDIO ATOM-BY-ATOM
        # This calls the Numba kernel to sum 80+ sine waves
        raw_audio = self.engine.get_sound(category, velocity, duration)
        
        # 3. APPLY STUDIO FX (Tube Preamp, Room, etc)
        if len(raw_audio) > 0:
            if instrument == 'chenda':
                raw_audio = self.fx.process_chenda(raw_audio)
            elif instrument == 'illathaalam' or 'KOMBU' in sound_id:
                raw_audio = self.fx.process_metal(raw_audio)
            elif 'KUZHAL' in sound_id:
                raw_audio = self.fx.process_wind(raw_audio)
                
        return raw_audio

    def mix_tracks(self, tracks: List[np.ndarray]) -> np.ndarray:
        if not tracks: return np.array([])
        max_len = max(len(t) for t in tracks)
        mixed = np.zeros(max_len)
        for t in tracks:
            mixed[:len(t)] += t
        return mixed

    def place_sound_at_time(self, sound: np.ndarray, time_position: float, total_duration: float) -> np.ndarray:
        total_samples = int(total_duration * self.sample_rate)
        track = np.zeros(total_samples)
        start = int(time_position * self.sample_rate)
        if start >= total_samples: return track
        end = min(start + len(sound), total_samples)
        track[start:end] = sound[:end-start]
        return track

    def export_audio(self, waveform: np.ndarray, filename: str, format: str = 'wav'):
        print("🎚️  Applying Mastering Limiter...")
        waveform = self.fx.master_mix(waveform)
        output_dir = os.path.dirname(filename)
        if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir)
        sf.write(filename, waveform, self.sample_rate)
        return filename
