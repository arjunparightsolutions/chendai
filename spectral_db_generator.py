"""
ChendAI ULTRA-WOODEN Spectral Generator
EXTREME LOW-FREQUENCY EMPHASIS for authentic wooden character
"""

import numpy as np
import json
import scipy.special as sp
from scipy import signal
import os
import random

def calculate_wooden_spectrum(base_freq, num_partials=12):
    """
    Generate WOODEN spectrum: HEAVY low-end, minimal highs
    Only 12 partials total (not 60) - wood dampens everything above
    """
    # Use only FIRST 12 Bessel zeros (eliminate high modes)
    zeros = sp.jn_zeros(0, num_partials)  # Only radial modes, no angular
    fundamental = zeros[0]
    
    partials = []
    for i, z in enumerate(zeros):
        ratio = z / fundamental
        freq = base_freq * ratio
        
        # EXTREME WOODEN WEIGHTING:
        # First 3 partials = 80% of energy (wood body)
        # Rest = 20% (quickly dying off)
        if i == 0:
            amp = 1.0  # Fundamental = STRONGEST
        elif i == 1:
            amp = 0.8  # 2nd partial = strong
        elif i == 2:
            amp = 0.6  # 3rd partial = medium
        else:
            amp = 0.3 / (i**1.5)  # Everything else = VERY weak
        
        # Wood = FAST decay for high frequencies
        decay = 2.0 / (ratio ** 0.8)
        
        partials.append({
            "r": float(np.round(ratio, 4)),
            "a": float(np.round(amp, 4)),
            "d": float(np.round(decay, 4))
        })
        
    return partials

def add_sub_bass_body(partials, base_freq):
    """
    Add SUB-BASS wood body resonances (50-150Hz)
    This is the THUD you hear in real wooden drums
    """
    body_resonances = [
        {"r": 60.0 / base_freq, "a": 0.7, "d": 2.5},   # Deep body thud
        {"r": 95.0 / base_freq, "a": 0.5, "d": 2.0},   # Mid body
        {"r": 130.0 / base_freq, "a": 0.3, "d": 1.5}   # Upper body
    ]
    
    return body_resonances + partials

def generate_variation(base_name, base_freq, count, category):
    """Generate WOODEN variations"""
    variations = {}
    
    print(f"   Generating {count} WOODEN variations for {base_name} @ {base_freq}Hz...")
    
    # Generate WOODEN spectrum (only 12 partials, heavy low-end)
    base_modes = calculate_wooden_spectrum(base_freq, num_partials=12)
    
    # Add sub-bass body
    base_modes = add_sub_bass_body(base_modes, base_freq)
    
    for i in range(count):
        tension_variance = np.random.normal(1.0, 0.02)
        
        var_id = f"{base_name}_VAR_{i:04d}"
        instance_freq = base_freq * tension_variance
        
        instance_partials = []
        for p in base_modes:
            p_shift = p['r'] * np.random.normal(1.0, 0.01)
            p_amp = p['a'] * np.random.normal(1.0, 0.08)
            p_dk = p['d'] * np.random.normal(1.0, 0.05)
            
            instance_partials.append([
                float(np.round(p_shift * instance_freq, 2)),
                float(np.round(max(0, p_amp), 4)),
                float(np.round(p_dk, 4))
            ])
            
        variations[var_id] = {
            "cat": category,
            "partials": instance_partials,
            "noise": {
                "color": "brown",  # Deep brown noise = wood
                "attack": 0.001,
                "mix": 0.08  # Minimal noise, maximum tone
            }
        }
        
    return variations

def main():
    print("🪵 ULTRA-WOODEN SPECTRAL GENERATOR")
    print("   EXTREME LOW-FREQUENCY EMPHASIS")
    print("   Only 12 partials per sound (wood dampens highs)")
    
    master_db = {}
    
    # WOODEN FREQUENCIES (emphasizing LOW fundamentals)
    
    # 1. THAAM - Lower fundamental for more wood, less ping
    master_db.update(generate_variation("CHENDA_THAAM", 280.0, 1200, "THAAM"))
    
    # 2. DHEEM - DEEP bass
    master_db.update(generate_variation("CHENDA_DHEEM", 95.0, 800, "DHEEM"))
    
    # 3. NAM - Rim (lower than before)
    master_db.update(generate_variation("CHENDA_NAM", 720.0, 500, "NAM"))
    
    # 4. URUTTU
    master_db.update(generate_variation("CHENDA_URUTTU", 320.0, 1500, "URUTTU"))
    
    # 5. CHAPU
    master_db.update(generate_variation("CHENDA_CHAPU", 310.0, 500, "CHAPU"))
    
    # 6. WIND
    master_db.update(generate_variation("KOMBU_SA", 370.0, 250, "WIND"))
    master_db.update(generate_variation("KOMBU_PA", 554.0, 250, "WIND"))
    
    total_sounds = len(master_db)
    print(f"\n✅ GENERATION COMPLETE")
    print(f"   Total: {total_sounds}")
    print(f"   Character: ULTRA-WOODEN (12 partials max)")
    print(f"   Focus: 80% energy in first 3 partials")
    print(f"   Sub-bass: 60-130Hz body resonance")
    print(f"   Saving...")
    
    with open("chenda_master_db.json", "w") as f:
        json.dump(master_db, f)
        
    print("🎉 WOODEN Database Ready.")

if __name__ == "__main__":
    main()
