"""
ChendAI - Traditional Kerala Percussion Beat Generator
Main application entry point
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import argparse
import numpy as np

from dna_parser import DNAParser
from audio_synthesizer import AudioSynthesizer
from ai_composer import AIComposer

# Load environment variables
load_dotenv()


class ChendAI:
    """Main ChendAI application"""
    
    def __init__(self):
        self.parser = DNAParser()
        self.synthesizer = AudioSynthesizer()
        self.composer = AIComposer()
        
        # Load DNA files
        print("🎵 ChendAI - Traditional Kerala Percussion Beat Generator")
        print("=" * 60)
        print("\n📖 Loading instrument DNA files...")
        
        self.parser.parse_chenda_dna()
        print("   ✓ Chenda DNA loaded")
        
        self.parser.parse_illathaalam_dna()
        print("   ✓ Illathaalam DNA loaded")
        
        self.parser.parse_side_instruments_dna()
        print("   ✓ Side instruments DNA loaded")
        
        total_sounds = len(self.parser.get_all_sounds())
        print(f"\n✅ Ready! {total_sounds} sounds available\n")
    
    def generate_beat(self, prompt: str, duration: int = 30, output_dir: str = 'output') -> str:
        """
        Generate a beat from a text prompt
        
        Args:
            prompt: User's beat description
            duration: Duration in seconds
            output_dir: Directory to save output files
        
        Returns:
            Path to generated audio file
        """
        print(f"🎵 Request: {prompt}")
        print(f"⏱️  Duration: {duration} seconds\n")
        
        # Step 1: Compose beat sequence using AI
        print("🤖 Analyzing your request with AI...")
        beat_sequence = self.composer.compose_beat_sequence(prompt, duration)
        
        print(f"   ✓ Detected style: {beat_sequence['style']}")
        print(f"   ✓ BPM: {beat_sequence['bpm']}")
        
        # Count total events
        total_events = sum(len(events) for events in beat_sequence['tracks'].values())
        print(f"   ✓ Generated {total_events} note events\n")
        
        # Step 2: Synthesize audio for each track (OPTIMIZED for memory)
        print("🔊 Synthesizing audio...")
        
        all_tracks = []
        
        for track_name, events in beat_sequence['tracks'].items():
            if not events:
                continue
            
            print(f"   🎼 Processing {track_name} ({len(events)} notes)...")
            
            # Create full-length track buffer
            total_samples = int(duration * self.synthesizer.sample_rate)
            track_buffer = np.zeros(total_samples, dtype=np.float32)  # Use float32 to save memory
            
            # Process events in batches to save memory
            batch_size = 50  # Process 50 sounds at a time
            for batch_start in range(0, len(events), batch_size):
                batch_events = events[batch_start:batch_start + batch_size]
                
                for event in batch_events:
                    sound_id = event['sound']
                    time_pos = event['time']
                    velocity = event.get('velocity', 1.0)
                    event_duration = event.get('duration', None)
                    
                    # Get sound parameters
                    sound_params = self.parser.get_sound_by_id(sound_id)
                    
                    if sound_params:
                        # Use event duration if specified
                        if event_duration:
                            sound_duration = event_duration
                        else:
                            sound_duration = sound_params.get('decay', 0.5)
                        
                        # Synthesize the sound
                        sound_wave = self.synthesizer.synthesize_sound(
                            sound_params, 
                            sound_duration, 
                            velocity
                        )
                        
                        # Place directly into track buffer (more memory efficient)
                        start_sample = int(time_pos * self.synthesizer.sample_rate)
                        end_sample = min(start_sample + len(sound_wave), total_samples)
                        
                        if start_sample < total_samples:
                            sound_length = end_sample - start_sample
                            track_buffer[start_sample:end_sample] += sound_wave[:sound_length].astype(np.float32)
            
            all_tracks.append(track_buffer)
        
        # Step 3: Mix all tracks together
        print("   🎚️  Mixing all tracks...")
        final_mix = self.synthesizer.mix_tracks(all_tracks)
        
        # Step 4: Export to file
        print("   💾 Exporting audio...\n")
        
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        style_name = beat_sequence['style'].replace(' ', '_')
        filename = os.path.join(output_dir, f"{style_name}_{timestamp}.wav")
        
        output_file = self.synthesizer.export_audio(final_mix, filename)
        
        # Calculate file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        
        print("✅ Audio generated successfully!")
        print(f"   📁 File: {output_file}")
        print(f"   ⏱️  Duration: {duration} seconds")
        print(f"   💾 Size: {file_size:.2f} MB")
        print(f"\n🎧 Your beat is ready to play!\n")
        
        return output_file
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("💡 Enter your beat requests (or 'quit' to exit)\n")
        
        while True:
            try:
                prompt = input("Enter your request: ").strip()
                
                if prompt.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Thanks for using ChendAI!\n")
                    break
                
                if not prompt:
                    continue
                
                # Get optional duration
                duration_input = input("Duration (seconds, default 30): ").strip()
                duration = int(duration_input) if duration_input else 30
                
                print()
                self.generate_beat(prompt, duration)
                print()
                
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using ChendAI!\n")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ChendAI - AI-powered Kerala percussion beat generator'
    )
    parser.add_argument(
        '--prompt', 
        type=str, 
        help='Beat description prompt'
    )
    parser.add_argument(
        '--duration', 
        type=int, 
        default=30, 
        help='Duration in seconds (default: 30)'
    )
    parser.add_argument(
        '--output', 
        type=str, 
        default='output', 
        help='Output directory (default: output)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize ChendAI
        chendai = ChendAI()
        
        # Run in appropriate mode
        if args.prompt:
            # Command-line mode
            chendai.generate_beat(args.prompt, args.duration, args.output)
        else:
            # Interactive mode
            chendai.interactive_mode()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
