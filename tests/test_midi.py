import unittest
from audio.midi_manager import MidiManager

class TestMidiManager(unittest.TestCase):
    def setUp(self):
        self.midi = MidiManager()
        
    def test_device_enumeration(self):
        inputs = self.midi.get_input_devices()
        outputs = self.midi.get_output_devices()
        print(f"\nMIDI Inputs: {inputs}")
        print(f"MIDI Outputs: {outputs}")
        # Note: Might be empty on CI/headless
        
    def test_open_close(self):
        inputs = self.midi.get_input_devices()
        if inputs:
            success = self.midi.open_input(inputs[0])
            # self.assertTrue(success) # Allow fail if device busy
            if success:
                self.assertTrue(self.midi.is_active)
                self.midi.close_input()
                self.assertFalse(self.midi.is_active)
        else:
            print("No MIDI inputs to test open/close")

if __name__ == '__main__':
    unittest.main()
