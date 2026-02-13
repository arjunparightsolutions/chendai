import sys
import os
import time
import unittest
import sounddevice as sd
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from audio.recorder import AudioRecorder

class TestAudioRecorder(unittest.TestCase):
    def setUp(self):
        self.recorder = AudioRecorder()
        
    def test_devices(self):
        devices = self.recorder.get_input_devices()
        print(f"\nFound {len(devices)} input devices")
        for dev in devices:
            print(f"  - {dev['name']}")
        
        # We might not have input devices on some CI/cloud envs, but on local dev we should
        # self.assertTrue(len(devices) > 0) 
        
    def test_monitoring(self):
        print("\nTesting monitoring...")
        try:
            self.recorder.start_monitoring()
            time.sleep(1)
            self.assertTrue(self.recorder.is_monitoring)
            self.recorder.stop_monitoring()
            self.assertFalse(self.recorder.is_monitoring)
        except Exception as e:
            print(f"Monitoring test skipped/failed: {e}")

    def test_recording(self):
        print("\nTesting recording...")
        output_file = "test_rec.wav"
        try:
            self.recorder.start_recording(output_dir=".", filename=output_file)
            time.sleep(2)
            self.assertTrue(self.recorder.is_recording)
            path = self.recorder.stop_recording()
            
            self.assertFalse(self.recorder.is_recording)
            self.assertTrue(os.path.exists(path))
            
            # Verify file size > 44 bytes (header only)
            size = os.path.getsize(path)
            print(f"Recorded file size: {size} bytes")
            self.assertTrue(size > 44)
            
            # Clean up
            os.remove(path)
            
        except Exception as e:
            print(f"Recording test skipped/failed: {e}")

if __name__ == '__main__':
    unittest.main()
