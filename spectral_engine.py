"""
ChendAI Ensemble Spectral Engine
Models MULTIPLE drummers playing together (not a single drum)
Creates natural chorus, warmth, and eliminates metallic single-drum character
"""

import numpy as np
import math
import json
import os
import random

try:
    from numba import jit, prange
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    def jit(*args, **kwargs):
        def decorator(func): return func
        return decorator

class SpectralEngine:
    def __init__(self, sample_rate=44100, db_path="chenda_master_db.json"):
        self.sample_rate = sample_rate
        self.db_path = db_path
        self.db = {}
        self.loaded = False
        
    def load_db(self):
        if self.loaded: return
        print(f"📂 Loading Spectral Database from {self.db_path}...")
        try:
            with open(self.db_path, "r") as f:
                self.db = json.load(f)
            self.loaded = True
            print(f"   Loaded {len(self.db)} acoustic signatures.")
        except FileNotFoundError:
            print("⚠️ DB NOT FOUND. Please run generator.")
            self.db = {}

    def get_sound(self, category: str, velocity: float = 1.0, duration: float = 1.0) -> np.ndarray:
        """
        Synthesize ENSEMBLE sound (multiple drummers)
        """
        if not self.loaded: self.load_db()
        
        candidates = [k for k, v in self.db.items() if v['cat'] == category]
        if not candidates:
            return np.zeros(int(duration * self.sample_rate))
            
        
        # ENSEMBLE MODELING: Layer 4 slightly different drums
        num_drummers = 4
        
        # Calculate target size based on duration
        target_samples = int(duration * self.sample_rate)
        layers = []
        
        for i in range(num_drummers):
            # Each drummer has a slightly different drum
            sound_id = random.choice(candidates)
            data = self.db[sound_id]
            partials = np.array(data['partials'], dtype=np.float64)
            
            # MICRO-DETUNING: Each drum tuned slightly differently
            detune = 1.0 + np.random.normal(0, 0.015)  # ±1.5% tuning variation
            
            # TIMING VARIATION: Not perfectly synchronized
            timing_offset = np.random.normal(0, 0.008)  # ±8ms variation
            
            # Synthesize this drummer's hit
            layer = synthesize_additive(
                partials * detune,  # Apply detuning
                duration, 
                self.sample_rate, 
                velocity * np.random.uniform(0.9, 1.1)  # Velocity variation
            )
            
            # Ensure layer is the correct size
            if len(layer) < target_samples:
                # Pad if too short
                layer = np.pad(layer, (0, target_samples - len(layer)), mode='constant')
            elif len(layer) > target_samples:
                # Trim if too long
                layer = layer[:target_samples]
            
            # Apply timing offset (after ensuring correct size)
            if timing_offset > 0:
                offset_samples = int(abs(timing_offset) * self.sample_rate)
                if offset_samples > 0:
                    layer = np.pad(layer, (offset_samples, 0))[:target_samples]
            elif timing_offset < 0:
                offset_samples = int(abs(timing_offset) * self.sample_rate)
                if offset_samples > 0:
                    layer = np.pad(layer, (0, offset_samples))[offset_samples:offset_samples + target_samples]
            
            layers.append(layer)
        
        # Mix all drummers together - all layers now have same size
        ensemble = np.zeros(target_samples, dtype=np.float32)
        for layer in layers:
            if len(layer) == target_samples:  # Safety check
                ensemble += layer
        
        # Normalize ensemble
        max_val = np.max(np.abs(ensemble))
        if max_val > 0:
            ensemble = ensemble / max_val * velocity
            
        return ensemble

# --- NUMBA KERNELS ---

@jit(nopython=True, cache=True)
def synthesize_additive(partials, duration, sample_rate, velocity):
    """
    Core Additive Synthesis Kernel with Physics-Informed Wood Tone
    Includes:
    - Transient Shaping (Stick impact)
    - Wood Body Resonance (Thud/Pop)
    - Inharmonicity (Stiff skin simulation)
    """
    num_samples = int(duration * sample_rate)
    output = np.zeros(num_samples, dtype=np.float64)
    time_step = 1.0 / sample_rate
    
    num_partials = partials.shape[0]
    
    # Transient Shaper: Sharp initial spike for stick impact
    # Helps it cut through the mix like a real drum
    transient_decay = -500.0 # Very fast decay
    
    for i in range(num_partials):
        freq = partials[i, 0]
        amp = partials[i, 1]
        decay_scale = partials[i, 2]
        
        if amp < 0.001: continue
        
        # WOOD-TONE FILTER 2.0 (Exact Chenda Profile)
        # Based on spectral analysis of authentic Valam Thala
        freq_factor = 1.0
        
        if freq < 80:     freq_factor = 0.4  # Reduce mud
        elif freq < 180:  freq_factor = 1.2  # Fundamental Body (Thud)
        elif freq < 450:  freq_factor = 1.6  # Lower Wood Resonance (Warmth)
        elif freq < 800:  freq_factor = 1.1  # Upper Wood (Pop)
        elif freq < 2500: freq_factor = 0.8  # Scoop mids slightly
        elif freq < 5000: freq_factor = 0.6  # Presence
        else:             freq_factor = 0.1  # Aggressive HF cut (No metallic ping)
        
        # Inharmonicity: Shift frequencies slightly to simulate stiff skin
        # Real drums are not perfectly harmonic
        inharmonic_stretch = 1.0 + (freq * 0.00005) # Subtle stretch
        target_freq = freq * inharmonic_stretch
        
        amp_filtered = amp * freq_factor
        
        omega = 2.0 * math.pi * target_freq
        decay_coef = -5.0 * decay_scale
        
        # Warmth Distortion (Even harmonics)
        distortion = 1.0 + 0.1 * abs(math.sin(omega * 0.002))
        
        # Pre-calculate transient part for this frequency (stick click)
        # Higher freqs get more transient emphasis
        transient_mix = 0.0
        if freq > 1000:
            transient_mix = 0.4
        
        for t_idx in range(num_samples):
            t = t_idx * time_step
            env = math.exp(decay_coef * t)
            
            # Mix regular envelope with a sharp transient spike
            transient_env = math.exp(transient_decay * t) * transient_mix
            
            total_amp = (env + transient_env) * amp_filtered * distortion
            
            if total_amp < 0.00001: break
            
            output[t_idx] += math.sin(omega * t) * total_amp
            
    # Normalize
    max_val = 0.0
    for i in range(num_samples):
        if abs(output[i]) > max_val:
            max_val = abs(output[i])
            
    if max_val > 0:
        factor = (1.0 / max_val) * velocity
        for i in range(num_samples):
            output[i] *= factor
            
    return output

