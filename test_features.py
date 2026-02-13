import numpy as np
from audio_processor import AudioProcessor

def test_audio_processor():
    ap = AudioProcessor(sample_rate=44100)
    
    # Create 1 second stereo sine wave
    t = np.linspace(0, 1, 44100)
    audio = np.array([np.sin(2 * np.pi * 440 * t), np.sin(2 * np.pi * 440 * t)])
    
    # 1. Test Split
    left, right = ap.split_audio(audio, 0.5)
    assert left.shape[1] == 22050
    assert right.shape[1] == 22050
    print("✅ Split Test Passed")
    
    # 2. Test Trim
    trimmed = ap.trim_audio(audio, 0.2, 0.8)
    expected_len = int(0.6 * 44100)
    # Slight rounding diff potential
    assert abs(trimmed.shape[1] - expected_len) < 5
    print("✅ Trim Test Passed")
    
    # 3. Test Fade
    to_fade = audio.copy()
    faded = ap.apply_fade(to_fade, fade_in_sec=0.1, fade_out_sec=0.1)
    assert faded[0, 0] == 0.0
    assert faded[0, -1] == 0.0
    print("✅ Fade Test Passed")

    # 4. Test Automation (Volume)
    to_automate = np.ones((2, 100)) # Constant DC
    points = [
        {'time': 0.0, 'value': 0.0, 'curve': 0},
        {'time': 1.0, 'value': 1.0, 'curve': 0} # 1 sec = 44100 samples
    ]
    # We passed 100 samples, so time indices are near 0.0
    # The interpolation should work based on time
    # This mock test is tricky with small samples but let's try
    # 100 samples is approx 0.002 seconds
    # So value should interpolate from 0 to very small number
    
    # Let's use a bigger buffer for auto test matching the time range
    to_automate_big = np.ones((2, 44100))
    automated = ap.apply_automation_curve(to_automate_big, points, 'volume')
    
    assert abs(automated[0, 0] - 0.0) < 0.001
    assert abs(automated[0, -1] - 1.0) < 0.001
    assert abs(automated[0, 22050] - 0.5) < 0.001 # Midpoint
    print("✅ Automation Test Passed")

if __name__ == "__main__":
    test_audio_processor()
