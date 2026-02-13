"""
AUTHENTIC TRADITIONAL KERALA INSTRUMENT SYNTHESIS
Based on acoustic research of real instruments
"""
import numpy as np
from scipy import signal as scipy_signal
from typing import Dict, Any

class TraditionalInstrumentSynthesizer:
    """Authentic synthesis for traditional Kerala

 instruments"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def synthesize_traditional(self, params: Dict[str, Any], duration: float, velocity: float) -> np.ndarray:
        """Route to appropriate synthesis method"""
        sound_id = params.get('sound_id', '')
        waveform_type = params.get('waveform', '')
        
        # Barrel drums
        if 'MADDALAM' in sound_id:
            return self._synthesize_maddalam(params, duration, velocity)
        elif 'THAVIL' in sound_id:
            return self._synthesize_thavil(params, duration, velocity)
        
        # Cylindrical drum
        elif 'THIMILA' in sound_id or 'PERCUSSION_SHARP' in waveform_type:
            return self._synthesize_thimila(params, duration, velocity)
        
        # Wind instruments
        elif 'NADASWARAM' in sound_id or 'WOODWIND_POWER' in waveform_type:
            return self._synthesize_nadaswaram(params, duration, velocity)
        elif 'KURUMKUZHAL' in sound_id or 'FLUTE_SOFT' in waveform_type:
            return self._synthesize_kurumkuzhal(params, duration, velocity)
        
        # Return None to use default synthesis
        return None
    
    def _synthesize_maddalam(self, params: Dict[str, Any], duration: float, velocity: float) -> np.ndarray:
        """Maddalam - Research-based synthesis with specific frequency peaks"""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        waveform = np.zeros(num_samples)
        
        # AUTHENTIC MADDALAM FREQUENCIES from research!
        # Peaks at: 228, 512, 602, 744, 1066 (dominant), 1244, 1737 Hz
        mode_freqs = [228.5, 512, 602.8, 744.1, 1066, 1244, 1737]
        mode_amps = [0.6, 0.7, 0.65, 0.55, 1.0, 0.5, 0.4]  # 1066 Hz most prominent!
        
        for freq, amp in zip(mode_freqs, mode_amps):
            decay_rate = 3.0 + (freq / 500)  # Higher frequencies decay faster
            mode_env = np.exp(-decay_rate * t)
            waveform += amp * np.sin(2 * np.pi * freq * t) * mode_env
        
        # Deep bass for "Thom" strokes
        if 'THOM' in params.get('sound_id', ''):
            bass_freq = params['base_freq']
            bass_decay = 8.0
            waveform += 1.2 * np.sin(2 * np.pi * bass_freq * t) * np.exp(-bass_decay * t)
        
        # Attack transient
        attack_samples = int(0.008 * self.sample_rate)
        if attack_samples > 0 and attack_samples < len(waveform):
            attack_noise = np.random.randn(attack_samples) * 0.8
            attack_env = np.exp(-200 * np.linspace(0, 0.008, attack_samples))
            waveform[:attack_samples] += attack_noise * attack_env
        
        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform)) * velocity * 0.9
        
        return waveform
    
    def _synthesize_thavil(self, params: Dict[str, Any], duration: float, velocity: float) -> np.ndarray:
        """Thavil - Loud outdoor drum with sharp attack"""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        waveform = np.zeros(num_samples)
        
        base_freq = params['base_freq']
        
        # Loud inharmonic modes
        mode_ratios = [1.0, 2.1, 3.4, 4.9, 6.3]
        mode_amps = [1.0, 0.8, 0.6, 0.4, 0.25]
        
        for ratio, amp in zip(mode_ratios, mode_amps):
            freq = base_freq * ratio
            decay_rate = 5.0 + (freq / 400)
            mode_env = np.exp(-decay_rate * t)
            waveform += amp * np.sin(2 * np.pi * freq * t) * mode_env
        
        # ULTRA-SHARP attack (thavil is VERY loud and sharp)
        attack_samples = int(0.003 * self.sample_rate)
        if attack_samples > 0 and attack_samples < len(waveform):
            attack_crack = np.random.randn(attack_samples) * 1.5
            attack_env = np.exp(-400 * np.linspace(0, 0.003, attack_samples))
            waveform[:attack_samples] += attack_crack * attack_env
        
        # Add punch with saturation
        waveform = np.tanh(waveform * 1.8) * 0.95
        
        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform)) * velocity * 0.95
        
        return waveform
    
    def _synthesize_thimila(self, params: Dict[str, Any], duration: float, velocity: float) -> np.ndarray:
        """Thimila - Clean, sharp resonance for panchavadyam"""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        waveform = np.zeros(num_samples)
        
        fundamental = params['base_freq']
        
        # Clean but inharmonic par tials (research says "clean resonant sound")
        partials = [1.0, 2.3, 3.8, 5.2, 6.9]
        amplitudes = [1.0, 0.6, 0.4, 0.25, 0.15]
        
        for partial_ratio, amp in zip(partials, amplitudes):
            freq = fundamental * partial_ratio
            decay_rate = 4.0 + partial_ratio
            partial_env = np.exp(-decay_rate * t)
            waveform += amp * np.sin(2 * np.pi * freq * t) * partial_env
        
        # Ultra-sharp attack (precision instrument)
        attack_samples = int(0.002 * self.sample_rate)
        if attack_samples > 0 and attack_samples < len(waveform):
            attack_burst = np.random.randn(attack_samples) * 0.7
            attack_env = np.exp(-500 * np.linspace(0, 0.002, attack_samples))
            waveform[:attack_samples] += attack_burst * attack_env
        
        # Clean resonance
        waveform = np.tanh(waveform * 1.3) * 0.85
        
        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform)) * velocity * 0.88
        
        return waveform
    
    def _synthesize_nadaswaram(self, params: Dict[str, Any], duration: float, velocity: float) -> np.ndarray:
        """Nadaswaram - Powerful double reed with complete harmonics"""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        waveform = np.zeros(num_samples)
        
        base_freq = params['base_freq']
        
        # COMPLETE harmonic series (research: "complete range of harmonics")
        for h in range(1, 25):
            harmonic_amp = 1.0 / h if h < 10 else 1.0 / (h * 1.5)
            # Slight inharmonicity
            freq = base_freq * h * (1 + 0.002 * h)
            waveform += harmonic_amp * np.sin(2 * np.pi * freq * t)
        
        # Conical bore effect - strong odd harmonics
        for odd_h in [3, 5, 7, 9, 11, 13]:
            waveform += 0.3 * np.sin(2 * np.pi * base_freq * odd_h * t)
        
        # WIDE vibrato (research specific!)
        vibrato_rate = 5.8
        vibrato_depth = 0.06  # Wider than kuzhal
        vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        vibrato_phase = 2 * np.pi * np.cumsum(base_freq * (1 + vibrato)) / self.sample_rate
        waveform += 0.4 * np.sin(vibrato_phase)
        
        # Heavy breath noise (double reed)
        breath_noise = np.random.randn(num_samples) * 0.25
        nyquist = self.sample_rate / 2
        b, a = scipy_signal.butter(2, [600/nyquist, 6000/nyquist], btype='band')
        breath_filtered = scipy_signal.filtfilt(b, a, breath_noise)
        waveform += breath_filtered
        
        # Powerful envelope (VERY LOUD outdoor instrument)
        attack_time = 0.12
        envelope = np.ones(num_samples)
        attack_samples = int(attack_time * self.sample_rate)
        if attack_samples < num_samples:
            envelope[:attack_samples] = 1 - np.exp(-5 * np.linspace(0, 1, attack_samples))
        
        waveform *= envelope
        waveform = np.tanh(waveform * 1.6) * 0.92  # LOUD!
        
        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform)) * velocity * 0.95
        
        return waveform
    
    def _synthesize_kurumkuzhal(self, params: Dict[str, Any], duration: float, velocity: float) -> np.ndarray:
        """Kurumkuzhal - Sweet breathy flute"""
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        waveform = np.zeros(num_samples)
        
        base_freq = params['base_freq']
        
        # Predominant fundamental with weak harmonics (flute characteristic)
        waveform += np.sin(2 * np.pi * base_freq * t)
        waveform += 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)
        waveform += 0.15 * np.sin(2 * np.pi * base_freq * 3 * t)
        waveform += 0.08 * np.sin(2 * np.pi * base_freq * 4 * t)
        
        # Breathy texture
        breath = np.random.randn(num_samples) * 0.12
        nyquist = self.sample_rate / 2
        b, a = scipy_signal.butter(2, [400/nyquist, 3000/nyquist], btype='band')
        breath_filtered = scipy_signal.filtfilt(b, a, breath)
        waveform += breath_filtered
        
        # Gentle envelope
        attack_time = 0.08
        release_time = 0.1
        envelope = np.ones(num_samples)
        attack_samples = int(attack_time * self.sample_rate)
        release_samples = int(release_time * self.sample_rate)
        
        if attack_samples < num_samples:
            envelope[:attack_samples] = np.linspace(0, 1, attack_samples) ** 2
        if release_samples < num_samples:
            envelope[-release_samples:] = np.exp(-4 * np.linspace(0, 1, release_samples))
        
        waveform *= envelope * 0.7
        
        # Normalize
        if np.max(np.abs(waveform)) > 0:
            waveform = waveform / np.max(np.abs(waveform)) * velocity * 0.75
        
        return waveform
