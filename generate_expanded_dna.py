"""
Generate expanded chendadna.txt with 1500+ sound variations
"""

def generate_chenda_database():
    """Generate comprehensive chenda sound database"""
    
    sounds = []
    
    # Header
    sounds.append("# RIGHT SOLUTIONS A.I. - CHENDAI SYNTHESIS MAP (EXPANDED)")
    sounds.append("# FORMAT: [ID] | [TYPE] | [BASE_FREQ_HZ] | [HARMONIC_RATIOS] | [DECAY_SEC] | [NOISE_ATTACK_AMT] | [PITCH_BEND_AMT]")
    sounds.append("# NOTE: Harmonic Ratios are comma-separated multipliers of Base Freq.")
    sounds.append("# NOTE: Noise Attack is 0.0 (clean) to 1.0 (pure noise).")
    sounds.append("# NOTE: Pitch Bend is Hz drop over time (simulates skin stretching).")
    sounds.append("")
    
    # =====================================================================
    # SECTION 1: VALAM THALA (RIGHT SIDE - STICK) - THAAM VARIATIONS
    # =====================================================================
    sounds.append("# --- SECTION 1: VALAM THALA (RIGHT SIDE - STICK) - THAAM FAMILY ---")
    sounds.append("# The main striking sounds - 300 variations")
    sounds.append("")
    
    # Generate THAAM variations (main center strike)
    base_freqs = range(400, 600, 2)  # 100 frequency variations
    for i, freq in enumerate(base_freqs):
        for intensity in ['SOFT', 'MED', 'HARD']:
            if intensity == 'SOFT':
                harmonics = "1.5, 2.0"
                decay = 0.18 + (i % 10) * 0.01
                noise = 0.20 + (i % 10) * 0.01
                bend = 8.0 + (i % 10) * 0.5
            elif intensity == 'MED':
                harmonics = "1.5, 2.0, 3.5"
                decay = 0.22 + (i % 10) * 0.01
                noise = 0.35 + (i % 10) * 0.02
                bend = 15.0 + (i % 10) * 1.0
            else:  # HARD
                harmonics = "1.5, 2.0, 3.5, 4.2"
                decay = 0.25 + (i % 10) * 0.01
                noise = 0.40 + (i % 10) * 0.02
                bend = 20.0 + (i % 10) * 1.5
            
            sound_id = f"THAAM_{freq}HZ_{intensity}"
            sounds.append(f"{sound_id} | STICK_CENTER | {freq}.0 | {harmonics} | {decay:.2f} | {noise:.2f} | {bend:.1f}")
    
    sounds.append("")
    
    # =====================================================================
    # SECTION 2: OPPU (MUTED STRIKES) - 200 variations
    # =====================================================================
    sounds.append("# --- SECTION 2: OPPU (MUTED STRIKES) - DAMPENED SOUNDS ---")
    sounds.append("# The 'thok' sound with stick pressed into skin - 200 variations")
    sounds.append("")
    
    base_freqs = range(250, 350, 1)  # 100 frequency variations
    for i, freq in enumerate(base_freqs):
        for intensity in ['SOFT', 'HARD']:
            if intensity == 'SOFT':
                harmonics = "1.2, 1.8"
                decay = 0.03 + (i % 10) * 0.002
                noise = 0.50 + (i % 15) * 0.01
                bend = 25.0 + (i % 10) * 2.0
            else:  # HARD
                harmonics = "1.2, 1.8, 2.5"
                decay = 0.05 + (i % 10) * 0.002
                noise = 0.60 + (i % 15) * 0.015
                bend = 50.0 + (i % 10) * 3.0
            
            sound_id = f"OPPU_{freq}HZ_{intensity}"
            sounds.append(f"{sound_id} | STICK_MUTE | {freq}.0 | {harmonics} | {decay:.3f} | {noise:.2f} | {bend:.1f}")
    
    sounds.append("")
    
    # =====================================================================
    # SECTION 3: NAM (RIM SHOTS) - 200 variations
    # =====================================================================
    sounds.append("# --- SECTION 3: NAM (RIM/EDGE STRIKES) - METALLIC SOUNDS ---")
    sounds.append("# Sharp, metallic rim shots - 200 variations")
    sounds.append("")
    
    base_freqs = range(700, 900, 1)  # 200 frequency variations
    for i, freq in enumerate(base_freqs):
        intensity = ['GHOST', 'MED', 'HARD'][i % 3]
        
        if intensity == 'GHOST':
            harmonics = "1.4, 1.9"
            decay = 0.15 + (i % 8) * 0.01
            noise = 0.05 + (i % 8) * 0.005
            bend = 0.0
        elif intensity == 'MED':
            harmonics = "1.4, 1.9, 4.5"
            decay = 0.30 + (i % 8) * 0.01
            noise = 0.10 + (i % 8) * 0.01
            bend = 2.0 + (i % 5) * 0.5
        else:  # HARD
            harmonics = "1.4, 1.9, 4.5, 6.0"
            decay = 0.35 + (i % 8) * 0.015
            noise = 0.15 + (i % 8) * 0.015
            bend = 5.0 + (i % 5) * 1.0
        
        sound_id = f"NAM_{freq}HZ_{intensity}"
        sounds.append(f"{sound_id} | RIM_SHOT | {freq}.0 | {harmonics} | {decay:.2f} | {noise:.3f} | {bend:.1f}")
    
    sounds.append("")
    
    # =====================================================================
    # SECTION 4: URUTTU (ROLLS) - 200 variations
    # =====================================================================
    sounds.append("# --- SECTION 4: URUTTU (ROLLING STRIKES) - FAST SEQUENCES ---")
    sounds.append("# Light, fast rolling strikes - 200 variations")
    sounds.append("")
    
    base_freqs = range(480, 580, 1)  # 100 frequency variations
    for i, freq in enumerate(base_freqs):
        for roll_type in ['LEAD', 'FOLLOW']:
            if roll_type == 'LEAD':
                harmonics = "1.5, 2.2, 3.0"
                decay = 0.12 + (i % 10) * 0.005
                noise = 0.30 + (i % 10) * 0.01
                bend = 15.0 + (i % 8) * 1.0
            else:  # FOLLOW
                harmonics = "1.5, 2.2"
                decay = 0.10 + (i % 10) * 0.005
                noise = 0.25 + (i % 10) * 0.01
                bend = 10.0 + (i % 8) * 0.8
            
            sound_id = f"URUTTU_{freq}HZ_{roll_type}"
            sounds.append(f"{sound_id} | ROLL_STICK | {freq}.0 | {harmonics} | {decay:.3f} | {noise:.2f} | {bend:.1f}")
    
    sounds.append("")
    
    # =====================================================================
    # SECTION 5: EDAM THALA (LEFT SIDE - BASS) - 300 variations
    # =====================================================================
    sounds.append("# --- SECTION 5: EDAM THALA (LEFT SIDE - BASS/HAND) ---")
    sounds.append("# Deep, resonant bass sounds - 300 variations")
    sounds.append("")
    
    # DHEEM (Bass notes)
    base_freqs = range(140, 240, 1)  # 100 frequency variations
    for i, freq in enumerate(base_freqs):
        for intensity in ['SOFT', 'MED', 'FULL']:
            if intensity == 'SOFT':
                harmonics = "1.6, 2.3"
                decay = 0.50 + (i % 12) * 0.03
                noise = 0.05 + (i % 10) * 0.003
                bend = 8.0 + (i % 8) * 0.5
            elif intensity == 'MED':
                harmonics = "1.6, 2.3, 3.1"
                decay = 0.70 + (i % 12) * 0.04
                noise = 0.08 + (i % 10) * 0.005
                bend = 10.0 + (i % 8) * 0.8
            else:  # FULL
                harmonics = "1.6, 2.3, 3.1, 4.5"
                decay = 0.85 + (i % 12) * 0.05
                noise = 0.10 + (i % 10) * 0.008
                bend = 15.0 + (i % 8) * 1.2
            
            sound_id = f"DHEEM_{freq}HZ_{intensity}"
            sounds.append(f"{sound_id} | BASS_OPEN | {freq}.0 | {harmonics} | {decay:.2f} | {noise:.3f} | {bend:.1f}")
    
    sounds.append("")
    
    # =====================================================================
    # SECTION 6: CHAPU (HAND SLAPS) - 200 variations
    # =====================================================================
    sounds.append("# --- SECTION 6: CHAPU (HAND SLAPS) - POPPING SOUNDS ---")
    sounds.append("# Hand slap 'pop' sounds - 200 variations")
    sounds.append("")
    
    base_freqs = range(380, 480, 1)  # 100 frequency variations
    for i, freq in enumerate(base_freqs):
        for slap_type in ['OPEN', 'CLOSED']:
            if slap_type == 'OPEN':
                harmonics = "2.1, 3.0, 5.0"
                decay = 0.18 + (i % 10) * 0.01
                noise = 0.20 + (i % 10) * 0.015
                bend = 25.0 + (i % 10) * 2.0
            else:  # CLOSED
                harmonics = "2.1, 3.0"
                decay = 0.08 + (i % 10) * 0.005
                noise = 0.30 + (i % 10) * 0.02
                bend = 40.0 + (i % 10) * 3.0
            
            sound_id = f"CHAPU_{freq}HZ_{slap_type}"
            sounds.append(f"{sound_id} | HAND_SLAP | {freq}.0 | {harmonics} | {decay:.2f} | {noise:.2f} | {bend:.1f}")
    
    sounds.append("")
    
    # =====================================================================
    # SECTION 7: NAKKU (FINGER TAPS) - 150 variations
    # =====================================================================
    sounds.append("# --- SECTION 7: NAKKU (FINGER TAPS) - SUBTLE FILLERS ---")
    sounds.append("# Light finger taps - 150 variations")
    sounds.append("")
    
    # Index finger taps
    for i, freq in enumerate(range(550, 650, 1)):
        harmonics = "2.0" if i % 2 == 0 else "2.0, 3.5"
        decay = 0.04 + (i % 8) * 0.003
        noise = 0.05
        bend = 0.0
        
        sound_id = f"NAKKU_INDEX_{freq}HZ"
        sounds.append(f"{sound_id} | FINGER_TAP | {freq}.0 | {harmonics} | {decay:.3f} | {noise:.2f} | {bend:.1f}")
    
    # Thumb taps
    for i, freq in enumerate(range(220, 270, 1)):
        harmonics = "1.5" if i % 2 == 0 else "1.5, 2.2"
        decay = 0.06 + (i % 8) * 0.004
        noise = 0.05
        bend = 0.0
        
        sound_id = f"NAKKU_THUMB_{freq}HZ"
        sounds.append(f"{sound_id} | FINGER_TAP | {freq}.0 | {harmonics} | {decay:.3f} | {noise:.2f} | {bend:.1f}")
    
    sounds.append("")
    
    # =====================================================================
    # SECTION 8: ARTIFACTS & TEXTURES - 150 variations
    # =====================================================================
    sounds.append("# --- SECTION 8: MICRO-NUANCES & ARTIFACTS ---")
    sounds.append("# These noises make synthesis sound 'dirty' and real - 150 variations")
    sounds.append("")
    
    # Stick clicks
    for i, freq in enumerate(range(1100, 1300, 2)):
        harmonics = "2.0, 4.0" if i % 2 == 0 else "2.0, 4.0, 6.0"
        decay = 0.015 + (i % 10) * 0.002
        noise = 0.85 + (i % 10) * 0.01
        
        sound_id = f"STICK_CLICK_{freq}HZ"
        sounds.append(f"{sound_id} | ARTIFACT | {freq}.0 | {harmonics} | {decay:.3f} | {noise:.2f} | 0.0")
    
    # Skin rubs
    for i, freq in enumerate(range(280, 330, 1)):
        decay = 0.35 + (i % 12) * 0.02
        noise = 0.75 + (i % 10) * 0.015
        
        sound_id = f"SKIN_RUB_{freq}HZ"
        sounds.append(f"{sound_id} | FRICTION | {freq}.0 | NO_HARMONICS | {decay:.2f} | {noise:.2f} | 0.0")
    
    # Air whooshes
    for i, freq in enumerate(range(80, 130, 1)):
        decay = 0.08 + (i % 10) * 0.01
        noise = 0.95 + (i % 5) * 0.01
        
        sound_id = f"AIR_WHOOSH_{freq}HZ"
        sounds.append(f"{sound_id} | AMBIENCE | {freq}.0 | NO_HARMONICS | {decay:.2f} | {noise:.2f} | 0.0")
    
    sounds.append("")
    sounds.append(f"# TOTAL SOUNDS: {len([s for s in sounds if '|' in s])}")
    
    return '\n'.join(sounds)


if __name__ == '__main__':
    print("Generating expanded chendadna.txt...")
    content = generate_chenda_database()
    
    with open('chendadna.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Count the sounds
    sound_count = len([line for line in content.split('\n') if '|' in line and not line.strip().startswith('#')])
    print(f"✓ Generated {sound_count} chenda sounds!")
    print(f"✓ Saved to chendadna.txt")
