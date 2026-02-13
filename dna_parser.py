"""
ChendAI DNA Parser
Parses the DNA files containing synthesis parameters for Kerala percussion instruments.
"""

import re
from typing import Dict, List, Any


class DNAParser:
    """Parser for ChendAI DNA files"""
    
    def __init__(self):
        self.chenda_sounds = {}
        self.illathaalam_sounds = {}
        self.side_instrument_sounds = {}
    
    def parse_chenda_dna(self, filepath: str = 'chendadna.txt') -> Dict[str, Any]:
        """Parse chendadna.txt and return dictionary of sound definitions"""
        sounds = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip comments and empty lines
                if line.startswith('#') or not line:
                    continue
                
                # Parse sound definition
                # Format: ID | TYPE | BASE_FREQ | HARMONICS | DECAY | NOISE | PITCH_BEND
                parts = [p.strip() for p in line.split('|')]
                
                if len(parts) >= 7:
                    sound_id = parts[0]
                    sound_type = parts[1]
                    base_freq = float(parts[2])
                    
                    # Parse harmonic ratios
                    harmonic_str = parts[3]
                    if harmonic_str == 'NO_HARMONICS':
                        harmonics = []
                    else:
                        harmonics = [float(h.strip()) for h in harmonic_str.split(',')]
                    
                    decay = float(parts[4])
                    noise_amount = float(parts[5])
                    pitch_bend = float(parts[6])
                    
                    sounds[sound_id] = {
                        'id': sound_id,
                        'type': sound_type,
                        'base_freq': base_freq,
                        'harmonics': harmonics,
                        'decay': decay,
                        'noise_amount': noise_amount,
                        'pitch_bend': pitch_bend,
                        'instrument': 'chenda'
                    }
        
        self.chenda_sounds = sounds
        return sounds
    
    def parse_illathaalam_dna(self, filepath: str = 'illathalamdna.txt') -> Dict[str, Any]:
        """Parse illathalamdna.txt and return dictionary of sound definitions"""
        sounds = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('#') or not line:
                    continue
                
                # Format: ID | TYPE | BASE_FREQ | INHARMONIC_RATIOS | DECAY | NOISE | PHASE
                parts = [p.strip() for p in line.split('|')]
                
                if len(parts) >= 7:
                    sound_id = parts[0]
                    sound_type = parts[1]
                    base_freq = float(parts[2])
                    
                    # Parse inharmonic ratios
                    harmonic_str = parts[3]
                    if 'RANDOM' in harmonic_str or harmonic_str == 'NO_HARMONICS':
                        harmonics = [1.45, 1.78, 2.55, 3.14, 5.8]  # Default cymbal ratios
                    else:
                        harmonics = [float(h.strip()) for h in harmonic_str.split(',')]
                    
                    decay = float(parts[4])
                    noise_amount = float(parts[5])
                    phase_offset = float(parts[6])
                    
                    sounds[sound_id] = {
                        'id': sound_id,
                        'type': sound_type,
                        'base_freq': base_freq,
                        'harmonics': harmonics,
                        'decay': decay,
                        'noise_amount': noise_amount,
                        'phase_offset': phase_offset,
                        'instrument': 'illathaalam'
                    }
        
        self.illathaalam_sounds = sounds
        return sounds
    
    def parse_side_instruments_dna(self, filepath: str = 'sideinstrumentsdna.txt') -> Dict[str, Any]:
        """Parse sideinstrumentsdna.txt and return dictionary of sound definitions"""
        sounds = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('#') or not line:
                    continue
                
                # Format: ID TYPE BASE_FREQ WAVEFORM FILTER SPECIAL_FX
                parts = line.split()
                
                if len(parts) >= 6:
                    sound_id = parts[0]
                    sound_type = parts[1]
                    base_freq = float(parts[2])
                    waveform = parts[3]
                    filter_cutoff = parts[4]
                    special_fx = parts[5]
                    
                    sounds[sound_id] = {
                        'id': sound_id,
                        'type': sound_type,
                        'base_freq': base_freq,
                        'waveform': waveform,
                        'filter_cutoff': filter_cutoff,
                        'special_fx': special_fx,
                        'instrument': 'side_instrument'
                    }
        
        self.side_instrument_sounds = sounds
        return sounds
    
    def get_all_sounds(self) -> Dict[str, Any]:
        """Return all parsed sounds from all instruments"""
        all_sounds = {}
        all_sounds.update(self.chenda_sounds)
        all_sounds.update(self.illathaalam_sounds)
        all_sounds.update(self.side_instrument_sounds)
        return all_sounds
    
    def get_sound_by_id(self, sound_id: str) -> Dict[str, Any]:
        """Retrieve a specific sound by its ID"""
        all_sounds = self.get_all_sounds()
        return all_sounds.get(sound_id, None)
    
    def list_available_sounds(self, instrument: str = None) -> List[str]:
        """List all available sound IDs, optionally filtered by instrument"""
        all_sounds = self.get_all_sounds()
        
        if instrument:
            return [sid for sid, sound in all_sounds.items() 
                   if sound.get('instrument') == instrument]
        
        return list(all_sounds.keys())


if __name__ == '__main__':
    # Test the parser
    parser = DNAParser()
    
    print("Parsing Chenda DNA...")
    chenda = parser.parse_chenda_dna()
    print(f"✓ Loaded {len(chenda)} chenda sounds")
    
    print("\nParsing Illathaalam DNA...")
    illathaalam = parser.parse_illathaalam_dna()
    print(f"✓ Loaded {len(illathaalam)} illathaalam sounds")
    
    print("\nParsing Side Instruments DNA...")
    side = parser.parse_side_instruments_dna()
    print(f"✓ Loaded {len(side)} side instrument sounds")
    
    print(f"\nTotal sounds available: {len(parser.get_all_sounds())}")
    
    # Show sample sound
    print("\nSample sound (THAAM_MAIN_HARD):")
    sample = parser.get_sound_by_id('THAAM_MAIN_HARD')
    if sample:
        for key, value in sample.items():
            print(f"  {key}: {value}")
