"""
ChendAI 6-Player Edition - Main Application
Integrates AI orchestration, material physics, and ensemble synthesis
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
import argparse
import numpy as np

# Import existing components
from dna_parser import DNAParser
from ai_composer import AIComposer

# Import new 6-player components
from player_system import Ensemble
from orchestration_engine import OrchestrationEngine, create_stroke_events_from_pattern, OrchestrationStrategy
from ensemble_mixer import EnsembleMixer
from spectral_engine import SpectralEngine

# Load environment variables
load_dotenv()


class ChendAI6Player:
    """ChendAI with 6-player ensemble and material physics"""
    
    def __init__(self, enable_spatial: bool = True, orchestration_strategy: str = "traditional"):
        self.parser = DNAParser()
        self.composer = AIComposer()
        self.enable_spatial = enable_spatial
        self.orchestration_strategy = OrchestrationStrategy[orchestration_strategy.upper()]
        
        # Initialize new components
        print("🎵 ChendAI 6-Player Edition - AI-Orchestrated Ensemble")
        print("=" * 70)
        print("\n📖 Loading components...")
        
        # Load DNA files
        self.parser.parse_chenda_dna()
        print("   ✓ Chenda DNA loaded")
        
        self.parser.parse_illathaalam_dna()
        print("   ✓ Illathaalam DNA loaded")
        
        self.parser.parse_side_instruments_dna()
        print("   ✓ Side instruments DNA loaded")
        
        # Initialize spectral engine
        self.spectral_engine = SpectralEngine(sample_rate=44100)
        self.spectral_engine.load_db()
        print("   ✓ Spectral synthesis engine loaded")
        
        # Build ensemble
        print("\n🎭 Building 6-Player Ensemble...")
        self.ensemble = Ensemble().build_standard_melam()
        
        # Print ensemble details
        chenda_players = self.ensemble.get_chenda_players()
        cymbal_players = self.ensemble.get_cymbal_players()
        
        print(f"   ✓ {len(chenda_players)} Chenda players")
        print(f"   ✓ {len(cymbal_players)} Elathaalam players")
        print(f"   ✓ 1 Kombu player")
        
        # Initialize orchestration engine
        self.orchestration_engine = OrchestrationEngine(self.ensemble)
        print(f"   ✓ AI orchestration engine ({self.orchestration_strategy.value} mode)")
        
        # Initialize mixer
        self.mixer = EnsembleMixer(sample_rate=44100)
        spatial_mode = "Stereo" if enable_spatial else "Mono"
        print(f"   ✓ Ensemble mixer ({spatial_mode})")
        
        total_sounds = len(self.parser.get_all_sounds())
        print(f"\n✅ Ready! {total_sounds} sounds, 6 players, spatial audio enabled\\n")
    
    def generate_melam(
        self,
        prompt: str,
        duration: int = 30,
        output_dir: str = 'output',
        orchestration_strategy: str = None,
        log_callback: callable = None
    ) -> str:
        """
        Generate a complete 6-player melam from prompt
        
        Args:
            prompt: User's beat description
            duration: Duration in seconds
            output_dir: Directory to save output files
            orchestration_strategy: Override default orchestration strategy
        
        Returns:
            Path to generated audio file
        """
        print(f"🎵 Request: {prompt}")
        print(f"⏱️  Duration: {duration} seconds")
        print(f"🎼 Orchestration: {orchestration_strategy or self.orchestration_strategy.value}\\n")
        
        # Step 1: AI Composition
        if log_callback: log_callback("🤖 AI Composition Phase starting...")
        beat_sequence = self.composer.compose_beat_sequence(prompt, duration, log_callback=log_callback)
        
        print(f"   ✓ Style: {beat_sequence['style']}")
        print(f"   ✓ BPM: {beat_sequence['bpm']}")
        
        total_events = sum(len(events) for events in beat_sequence['tracks'].values())
        print(f"   ✓ Base events: {total_events}\\n")
        
        # Step 2: Convert to stroke events and orchestrate
        if log_callback: log_callback("🎭 Orchestration Phase starting...")
        
        # Extract main chenda track
        chenda_events = beat_sequence['tracks'].get('chenda', [])
        
        # Convert to stroke events format
        stroke_events = []
        for event in chenda_events:
            from orchestration_engine import StrokeEvent
            from traditional_patterns import STROKE_LIBRARY
            
            # Map sound ID to stroke type (reverse lookup)
            # This is a simplification - in production, we'd store stroke type in event
            stroke_type = "Ta"  # Default
            sound_category = "THAAM"  # Default
            
            # Try to infer from sound ID
            sound_params = self.parser.get_sound_by_id(event['sound'])
            if sound_params:
                sound_category = sound_params.get('category', 'THAAM')
            
            stroke_event = StrokeEvent(
                time=event['time'],
                stroke_type=stroke_type,
                sound_category=sound_category,
                intensity=event.get('velocity', 0.7),
                duration=event.get('duration', 0.3)
            )
            stroke_events.append(stroke_event)
        
        # Orchestrate to 6 players
        strategy = orchestration_strategy or self.orchestration_strategy
        if isinstance(strategy, str):
            strategy = OrchestrationStrategy[strategy.upper()]
        
        orchestrated = self.orchestration_engine.orchestrate_sequence(stroke_events, strategy)
        
        # Print orchestration results
        player_counts = {}
        for player_id, events in orchestrated.get_all_player_events().items():
            if events:
                player = self.ensemble.get_player(player_id)
                player_counts[player.name] = len(events)
                print(f"   ✓ {player.name}: {len(events)} events")
        
        print()
        
        # Step 3: Render ensemble
        if log_callback: log_callback(f"🔊 Rendering Ensemble ({'Stereo' if self.enable_spatial else 'Mono'})...")
        
        audio, stems = self.mixer.render_ensemble(
            ensemble=self.ensemble,
            orchestrated_pattern=orchestrated,
            duration=duration,
            spectral_engine=self.spectral_engine,
            enable_spatial=self.enable_spatial,
            return_stems=True
        )
        
        print("   ✓ Ensemble rendered\\n")
        
        # Step 4: Export
        if log_callback: log_callback("💾 Exporting audio tracks...")
        
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        style_name = beat_sequence['style'].replace(' ', '_')
        base_filename = f"6player_{style_name}_{timestamp}"
        master_filename = os.path.join(output_dir, f"{base_filename}_master.wav")
        
        # Export Master
        if self.enable_spatial and audio.ndim == 2:
            output_file = self.mixer.export_stereo(audio, master_filename)
        else:
            # Mono export
            import soundfile as sf
            sf.write(master_filename, audio, 44100, subtype='PCM_16')
            output_file = master_filename
            
        # Export Stems
        stem_paths = {}
        stems_dir = os.path.join(output_dir, f"{base_filename}_stems")
        if not os.path.exists(stems_dir):
            os.makedirs(stems_dir)
            
        print(f"   ✓ Exporting stems to {stems_dir}...")
        import soundfile as sf
        
        for player_id, stem_audio in stems.items():
            player = self.ensemble.get_player(player_id)
            # Sanitize player name for filename
            safe_name = "".join(c for c in player.name if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
            stem_filename = os.path.join(stems_dir, f"{safe_name}.wav")
            
            # Stems are mono
            sf.write(stem_filename, stem_audio, 44100, subtype='PCM_16')
            stem_paths[player_id] = stem_filename
        
        # Calculate file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
        
        print(f"   ✓ Exported Master to: {output_file}")
        print(f"   ✓ Size: {file_size:.2f} MB")
        
        print("\\n✅ 6-Player Melam Generated Successfully!")
        print("=" * 70)
        print(f"\\n🎧 Listen to hear:")
        print(f"   • {len(player_counts)} players with unique timbres")
        print(f"   • Material physics (wood, leather, stick)")
        print(f"   • Natural micro-timing variations")
        if self.enable_spatial:
            print(f"   • Spatial positioning (use headphones!)")
        print("\\n")
        
        # Serialize orchestration data
        orchestration_data = {}
        all_events = orchestrated.get_all_player_events()
        
        for player_id, events in all_events.items():
            serialized_events = []
            for event in events:
                serialized_events.append({
                    "time": float(event.time),
                    "type": event.stroke_type,
                    "category": event.sound_category,
                    "velocity": float(event.velocity) if event.velocity else 0.7,
                    "duration": float(event.duration)
                })
            orchestration_data[player_id] = serialized_events

        return {
            "master": os.path.abspath(output_file),
            "stems": {k: os.path.abspath(v) for k, v in stem_paths.items()},
            "metadata": {
                "style": beat_sequence.get('style', 'Unknown'),
                "bpm": beat_sequence.get('bpm', 'Standard'),
                "total_events": total_events,
                "orchestration": orchestration_strategy or self.orchestration_strategy.value,
                "tracks": orchestration_data
            }
        }
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("💡 Enter your melam requests (or 'quit' to exit)")
        print("📝 Commands:")
        print("   - Type your request normally")
        print("   - Add 'duration=X' to set duration (default: 30s)")
        print("   - Add 'strategy=X' for orchestration (traditional/dynamic/unison/antiphonal/layered)")
        print()
        
        while True:
            try:
                user_input = input("🎵 Request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\\n👋 Thanks for using ChendAI 6-Player Edition!\\n")
                    break
                
                if not user_input:
                    continue
                
                # Parse duration and strategy from input
                duration = 30
                strategy = None
                
                if 'duration=' in user_input.lower():
                    import re
                    match = re.search(r'duration=(\d+)', user_input.lower())
                    if match:
                        duration = int(match.group(1))
                        user_input = user_input.replace(match.group(0), '').strip()
                
                if 'strategy=' in user_input.lower():
                    import re
                    match = re.search(r'strategy=(\w+)', user_input.lower())
                    if match:
                        strategy = match.group(1)
                        user_input = user_input.replace(match.group(0), '').strip()
                
                print()
                self.generate_melam(user_input, duration, orchestration_strategy=strategy)
                
            except KeyboardInterrupt:
                print("\\n\\n👋 Thanks for using ChendAI 6-Player Edition!\\n")
                break
            except Exception as e:
                print(f"\\n❌ Error: {e}\\n")
                import traceback
                traceback.print_exc()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ChendAI 6-Player Edition - AI-orchestrated ensemble with material physics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python chendai_6player.py
  
  # Generate with prompt
  python chendai_6player.py --prompt "Create an intense Panchari melam" --duration 60
  
  # Different orchestration strategies
  python chendai_6player.py --prompt "Gentle melam" --strategy unison
  python chendai_6player.py --prompt "Call and response" --strategy antiphonal
  
  # Mono output (faster)
  python chendai_6player.py --prompt "Fast melam" --mono
        """
    )
    
    parser.add_argument('--prompt', type=str, help='Melam description prompt')
    parser.add_argument('--duration', type=int, default=30, help='Duration in seconds (default: 30)')
    parser.add_argument('--output', type=str, default='output', help='Output directory (default: output)')
    parser.add_argument('--strategy', type=str, default='traditional',
                       choices=['traditional', 'dynamic', 'unison', 'antiphonal', 'layered'],
                       help='Orchestration strategy (default: traditional)')
    parser.add_argument('--mono', action='store_true', help='Disable spatial audio (faster rendering)')
    
    args = parser.parse_args()
    
    try:
        # Initialize ChendAI 6-Player
        chendai = ChendAI6Player(
            enable_spatial=not args.mono,
            orchestration_strategy=args.strategy
        )
        
        # Run in appropriate mode
        if args.prompt:
            # Command-line mode
            chendai.generate_melam(
                args.prompt,
                args.duration,
                args.output,
                args.strategy
            )
        else:
            # Interactive mode
            chendai.interactive_mode()
    
    except Exception as e:
        print(f"\\n❌ Fatal error: {e}\\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
