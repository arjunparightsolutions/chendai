"""
ChendAI Physical Modeling Library - Karplus-Strong Algorithm
Implements physically accurate drum and string synthesis using delay lines and digital filters.
"""

import numpy as np
from scipy import signal

def generate_karplus_strong(
    freq: float, 
    duration: float, 
    sample_rate: int = 44100, 
    decay_factor: float = 0.99,
    stretch_factor: float = 0.0,
    blend_factor: float = 0.5,
    initial_noise_width: float = 1.0
) -> np.ndarray:
    """
    Generate sound using the Extended Karplus-Strong algorithm.
    """
    N = int(sample_rate / freq)
    if N < 2: N = 2
        
    total_samples = int(duration * sample_rate)
    
    # Excitation
    noise_len = int(N * initial_noise_width)
    if noise_len < 1: noise_len = 1
    excitation = np.random.randn(noise_len)
    
    # Filter Coeffs
    # H(z) = 1 / (1 - decay * 0.5 * (1 + z^-1) * z^-N) [String]
    # H(z) = 1 / (1 + decay * 0.5 * (1 + z^-1) * z^-N) [Drum]
    
    a = np.zeros(N + 2)
    a[0] = 1.0
    
    # Blend logic
    # String (0.0): feedback is Added (lowpass)
    # Drum (1.0): feedback is Subtracted (highpass-ish)
    
    w1 = 0.5 * decay_factor
    w2 = 0.5 * decay_factor
    
    # Linear interpolation of sign
    # blend 0 -> +1, blend 1 -> -1
    sign = 1.0 - 2.0 * blend_factor 
    
    a[N] = -w1 * sign
    a[N+1] = -w2 * sign
    
    b = [1.0]
    
    # Apply Stretch (Allpass approximation via index shifting or fractional delay)
    # For this simple implementation, we just rely on the 'blend' to create inharmonicity
    # But real stretch requires an allpass filter in the loop. 
    # We will simulate "stiffness" by filtering the input darker for stiff strings.
    
    if stretch_factor > 0:
        # Pre-filter excitation to simulate stiff impact
        sos = signal.butter(1, (1.0 - stretch_factor*0.5) * freq * 8 / (sample_rate/2), btype='low', output='sos')
        excitation = signal.sosfilt(sos, excitation)

    x = np.zeros(total_samples)
    noise_len = min(len(excitation), total_samples)
    x[:noise_len] = excitation[:noise_len]
    
    try:
        output = signal.lfilter(b, a, x)
    except:
        return np.zeros(total_samples)
        
    # Body Resonance
    body_freq = freq * 0.8
    if body_freq < 100: body_freq = 100
    nyquist = sample_rate / 2
    try:
        sos = signal.butter(1, body_freq / nyquist, btype='low', output='sos')
        body_tone = signal.sosfilt(sos, output)
        output = output * 0.7 + body_tone * 0.4
    except:
        pass

    return output

def variable_tension_edakka(
    base_freq: float,
    duration: float,
    sample_rate: int = 44100,
    tension_mod_freq: float = 5.0,
    tension_mod_amt: float = 20.0
) -> np.ndarray:
    """Simulate Edakka with variable tension (Pitch Bend)."""
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples)
    freq_curve = base_freq + tension_mod_amt * np.sin(2 * np.pi * tension_mod_freq * t)
    phase = 2 * np.pi * np.cumsum(freq_curve) / sample_rate
    impulse = np.sin(phase) * np.exp(-20 * t) 
    mod_idx = 1.5 
    mod_freq = freq_curve * 1.02 
    modulator = np.sin(2 * np.pi * np.cumsum(mod_freq)/sample_rate)
    waveform = np.sin(phase + mod_idx * modulator * np.exp(-5*t))
    env = np.exp(-4.0 * t)
    return waveform * env

def generate_transient(
    duration: float,
    sample_rate: int = 44100,
    center_freq: float = 1000.0,
    bandwidth: float = 500.0,
    decay: float = 0.05
) -> np.ndarray:
    """Generate a percussive transient (stick click / slap)."""
    num_samples = int(duration * sample_rate)
    if num_samples < 1: return np.array([])
    noise = np.random.randn(num_samples)
    nyquist = sample_rate / 2
    low = max(center_freq - bandwidth/2, 20) / nyquist
    high = min(center_freq + bandwidth/2, nyquist * 0.99) / nyquist
    if low < high:
        b, a = signal.butter(2, [low, high], btype='band')
        filtered_noise = signal.filtfilt(b, a, noise)
    else:
        filtered_noise = noise
    t = np.linspace(0, duration, num_samples)
    env = np.exp(-t / decay) 
    return filtered_noise * env

def generate_metallic_ring(
    freq: float,
    duration: float,
    sample_rate: int = 44100,
    decay: float = 0.5,
    modulation_index: float = 2.0
) -> np.ndarray:
    """Generate metallic sounds (Rim shots / Cymbals) using FM Synthesis."""
    num_samples = int(duration * sample_rate)
    if num_samples < 1: return np.array([])
    t = np.linspace(0, duration, num_samples)
    c_freq = freq
    m_freq = freq * 1.414 
    mod_env = np.exp(-5.0 * t / decay) * modulation_index
    waveform = np.sin(2 * np.pi * c_freq * t + mod_env * np.sin(2 * np.pi * m_freq * t))
    amp_env = np.exp(-3.0 * t / decay)
    return waveform * amp_env
    return waveform * amp_env

def generate_fm_drum(
    freq: float,
    duration: float,
    sample_rate: int = 44100,
    decay: float = 0.2,
    mod_ratio: float = 1.5,
    mod_index: float = 5.0,
    pitch_decay: float = 0.1,
    pitch_drop_octaves: float = 1.0
) -> np.ndarray:
    """
    Generate drum sounds using Frequency Modulation (FM).
    This creates inharmonic, membrane-like textures that do NOT sound like strings/pianos.
    
    Args:
        freq: Carrier frequency (fundamental tone)
        decay: Amplitude decay time
        mod_ratio: Ratio of modulator freq to carrier freq (non-integers = metallic/drummy)
        mod_index: Intensity of the FM effect (brightness)
    """
    num_samples = int(duration * sample_rate)
    if num_samples < 1: return np.array([])
    t = np.linspace(0, duration, num_samples)
    
    # Pitch Envelope (Pitch Drop) - Critical for drums
    pitch_env = np.exp(-t / pitch_decay) * pitch_drop_octaves * freq
    carrier_freq = freq + pitch_env
    
    # Phase accumulation for variable frequency
    carrier_phase = 2 * np.pi * np.cumsum(carrier_freq) / sample_rate
    
    # Modulator
    mod_freq = carrier_freq * mod_ratio
    mod_phase = 2 * np.pi * np.cumsum(mod_freq) / sample_rate
    
    # Modulation Index Envelope (Sound starts bright, gets duller)
    idx_env = np.exp(-t / (decay * 0.5)) * mod_index
    
    # FM Equation
    waveform = np.sin(carrier_phase + idx_env * np.sin(mod_phase))
    
    # Amplitude Envelope
    amp_env = np.exp(-t / decay)
    
    return waveform * amp_env
