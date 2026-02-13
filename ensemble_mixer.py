"""
ChendAI Ensemble Mixer
Spatial audio mixing and synthesis for multi-player ensemble
"""

import numpy as np
from typing import Dict, List, Tuple
from scipy import signal

from player_system import Ensemble, Player, InstrumentType, ChendaInstrument
from orchestration_engine import OrchestrationPattern, StrokeEvent
from material_properties import MaterialEffectsCalculator, WoodProperties, MembraneProperties
from stick_physics import StickImpactModeler, create_complete_strike_profile


class EnsembleMixer:
    """
    Mixes multiple players with spatial positioning
    """
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
        self.material_calc = MaterialEffectsCalculator()
        self.stick_modeler = StickImpactModeler(sample_rate)
    
    def render_ensemble(
        self,
        ensemble: Ensemble,
        orchestrated_pattern: OrchestrationPattern,
        duration: float,
        spectral_engine=None,  # Will be passed from main system
        enable_spatial: bool = True,
        return_stems: bool = False
    ) -> (np.ndarray, Dict[str, np.ndarray]):
        """
        Render complete ensemble with spatial audio
        
        Args:
            ensemble: The ensemble object
            orchestrated_pattern: Orchestrated pattern with player assignments
            duration: Total duration in seconds
            spectral_engine: Reference to spectral synthesis engine
            enable_spatial: Enable spatial positioning
        
        Returns:
            If return_stems is False:
                Mixed stereo audio (2 x num_samples)
            If return_stems is True:
                (Mixed stereo audio, Dict[player_id, mono_audio])
        """
        num_samples = int(duration * self.sample_rate)
        
        if enable_spatial:
            # Stereo output
            mix_left = np.zeros(num_samples, dtype=np.float32)
            mix_right = np.zeros(num_samples, dtype=np.float32)
        else:
            # Mono output
            mix_mono = np.zeros(num_samples, dtype=np.float32)
            
        # Dictionary to store stems if requested
        stems = {}
        
        # Render each player's track
        all_events = orchestrated_pattern.get_all_player_events()
        
        # Check for soloed players
        all_players = [ensemble.get_player(pid) for pid in all_events.keys()]
        solo_active = any(p.solo for p in all_players if p)

        for player_id, events in all_events.items():
            if not events:
                continue
            
            player = ensemble.get_player(player_id)
            
            # Skip if muted (unless soloed)
            if player.mute and not player.solo:
                continue
                
            # Skip if solo is active and this player is not soloed
            if solo_active and not player.solo:
                continue

            print(f"   🎼 Rendering {player.name} ({len(events)} events)...")
            
            # Render player's track
            player_track = self._render_player_track(
                player, events, duration, spectral_engine
            )
            
            # Store stem (pre-gain, pre-spatial)
            if return_stems:
                stems[player_id] = player_track.copy()
            
            # Apply Volume/Gain
            player_track *= player.gain
            
            if enable_spatial:
                # Use pan override if available, otherwise use spatial position
                # Pan (-1 to 1) maps to X coordinate
                # Standard stage width is approx +/- 2 meters
                
                pos_x, pos_y, pos_z = player.spatial_position
                
                # If pan is explicitly set (mixer override), update x
                # We assume pan 0 is center. 
                # Let's just use the player.pan attribute directly mapping to x range -1.0 to 1.0
                # But _apply_spatial_position expects meters.
                # Let's Map pan (-1 to 1) to x (-2m to 2m) or just use logic in apply_spatial
                
                # Actually _apply_spatial_position treats X as "left (-) to right (+)" and clamps pan -1 to 1 based on X.
                # So we can just pass (player.pan, pos_y, pos_z) effectively.
                
                effective_position = (player.pan, pos_y, pos_z)

                # Apply spatial positioning
                left, right = self._apply_spatial_position(
                    player_track, effective_position
                )
                
                mix_left += left
                mix_right += right
            else:
                mix_mono += player_track
        
        # Industrial-Standard Mastering Chain
        
        # 1. Glue Compression (simulate buss compressor)
        # Gentle ratio, slow attack, fast release to "glue" tracks
        if enable_spatial:
             # Process L/R
             stereo = np.vstack([mix_left, mix_right])
             
             # Apply soft clipper/limiter to catch peaks without hard digital clip
             # Use tanh for analog-style saturation
             # Preserve headroom (0.95 max)
             
             # Check pre-mastering levels
             peak_pre = np.max(np.abs(stereo))
             
             # "Maximize" volume if too quiet, or limit if too loud
             target_loudness = 0.9
             
             if peak_pre > 0:
                 # Soft saturation curve: y = tanh(x)
                 # We drive it slightly if low
                 drive = 1.0
                 if peak_pre < 0.5:
                     drive = 1.5 # Boost low signals
                 
                 stereo = np.tanh(stereo * drive)
                 
                 # Final safety normalize
                 peak_post = np.max(np.abs(stereo))
                 if peak_post > 0.98:
                     stereo = stereo / peak_post * 0.98
             
             if return_stems:
                 return stereo, stems
             return stereo
        else:
            # Mono Mastering
            peak_pre = np.max(np.abs(mix_mono))
            
            if peak_pre > 0:
                mix_mono = np.tanh(mix_mono * 1.2) # Slight drive
                
                peak_post = np.max(np.abs(mix_mono))
                if peak_post > 0.98:
                    mix_mono = mix_mono / peak_post * 0.98
            
            if return_stems:
                return mix_mono, stems
            return mix_mono
    
    def _render_player_track(
        self,
        player: Player,
        events: List[StrokeEvent],
        duration: float,
        spectral_engine
    ) -> np.ndarray:
        """
        Render a single player's track
        
        For Chenda players: Use material-aware synthesis
        For Cymbals: Use spectral synthesis
        For Wind: Use separate synthesis (future)
        """
        num_samples = int(duration * self.sample_rate)
        track = np.zeros(num_samples, dtype=np.float32)
        
        for event in events:
            if event.sound_category == "REST":
                continue
            
            # Synthesize sound based on instrument type
            if player.instrument_type == InstrumentType.CHENDA:
                sound = self._synthesize_chenda_strike(
                    player, event, spectral_engine
                )
            elif player.instrument_type == InstrumentType.ELATHAALAM:
                sound = self._synthesize_cymbal_strike(
                    player, event, spectral_engine
                )
            else:
                # Wind instruments - placeholder
                sound = np.zeros(int(0.1 * self.sample_rate))
            
            # Place in track  
            # Check for empty or zero-sized arrays
            if sound.size == 0 or len(sound) == 0:
                # Skip empty sounds
                continue
                
            # FLATTEN SOUND IF NEEDED (Fix for shape mismatch)
            if sound.ndim > 1:
                # If sound is stereo (2D) but we are rendering a mono player track
                # we should mix it down to mono or pick a channel. 
                # Since _render_player_track returns a mono float32 array, we need mono sound.
                sound = np.mean(sound, axis=1) if sound.shape[1] > 1 else sound.flatten()

            start_sample = max(0, int(event.time * self.sample_rate))
            
            # Skip if event is completely outside the track duration
            if start_sample >= num_samples:
                continue
                
            end_sample = min(start_sample + len(sound), num_samples)
            sound_length = end_sample - start_sample
            
            # Only add to track if we have valid bounds and data
            if sound_length > 0:
                try:
                    track[start_sample:end_sample] += sound[:sound_length]
                except ValueError as e:
                    # Catch broadcast errors and show informative error but continue
                    print(f"[Mixer] Error adding sound: {e}")
                    print(f"  Track shape: {track[start_sample:end_sample].shape}")
                    print(f"  Sound shape: {sound[:sound_length].shape}")
                    continue
        
        return track
    
    def _synthesize_chenda_strike(
        self,
        player: Player,
        event: StrokeEvent,
        spectral_engine
    ) -> np.ndarray:
        """
        Synthesize a Chenda strike with full material physics
        
        This is where all the material modeling comes together!
        """
        instrument = player.instrument
        
        if not isinstance(instrument, ChendaInstrument):
            # Fallback to basic synthesis
            return self._synthesize_basic(event, spectral_engine)
        
        # Determine which side (Valam vs Edamthala)
        # THAAM/CHAPU = Valam (right, treble)
        # DHEEM/NAM = Edamthala (left, bass)
        
        if event.sound_category in ["THAAM", "CHAPU"]:
            membrane = instrument.membrane_valam
            stick = instrument.stick_valam
            base_category = event.sound_category
        else:
            membrane = instrument.membrane_edamthala
            stick = instrument.stick_edamthala
            base_category = event.sound_category
        
        # Create complete strike profile
        strike_profile = create_complete_strike_profile(
            stick=stick,
            membrane=membrane,
            velocity=event.velocity,
            contact_point=event.contact_point,
            angle=90.0,
            sample_rate=self.sample_rate
        )
        
        # Get base spectral sound
        base_sound = spectral_engine.get_sound(
            category=base_category,
            velocity=event.velocity,
            duration=event.duration
        )
        
        # Apply material modifications
        modified_sound = self._apply_material_effects(
            base_sound,
            strike_profile,
            instrument.body_wood,
            membrane
        )
        
        # Add transient
        transient = strike_profile['transient_waveform']
        if len(transient) > 0:
            # Mix transient at start
            transient_len = min(len(transient), len(modified_sound))
            modified_sound[:transient_len] += transient[:transient_len] * 0.3
        
        # Add stick resonance
        stick_res = strike_profile['stick_resonance_waveform']
        if len(stick_res) > 0:
            stick_len = min(len(stick_res), len(modified_sound))
            modified_sound[:stick_len] += stick_res[:stick_len] * 0.15
        
        return modified_sound.astype(np.float32)
    
    def _apply_material_effects(
        self,
        audio_signal: np.ndarray,
        strike_profile: dict,
        wood: WoodProperties,
        membrane: MembraneProperties
    ) -> np.ndarray:
        """
        Apply material-specific effects to the sound
        """
        output = audio_signal.copy()
        
        # 1. Frequency shift based on membrane tension
        # (Already baked into spectral engine, but can add subtle modulation)
        
        # 2. Pitch bend (membrane "gives" under impact)
        pitch_bend = strike_profile['response']['pitch_bend_amount']
        if pitch_bend > 0.01:
            output = self._apply_pitch_bend(
                output,
                pitch_bend,
                strike_profile['response']['pitch_bend_duration']
            )
        
        # 3. Wood resonance filtering
        # Darker woods = emphasize lows, brighter woods = emphasize highs
        brightness = wood.resonance_brightness
        output = self._apply_wood_character(output, brightness)
        
        # 4. Contact point filtering
        output = self.stick_modeler.apply_contact_point_filtering(
            output,
            strike_profile['contact_point']
        )
        
        return output
    
    def _apply_pitch_bend(
        self,
        audio_signal: np.ndarray,
        bend_amount: float,
        bend_duration: float
    ) -> np.ndarray:
        """
        Apply momentary pitch bend at attack
        Simulates membrane "giving" under stick impact
        """
        # Simple pitch shift using resampling
        # This is a simplified approach - proper pitch bend needs phase vocoder
        
        bend_samples = int(bend_duration * self.sample_rate)
        if bend_samples > len(audio_signal):
            bend_samples = len(audio_signal)
        
        if bend_samples < 10:
            return audio_signal
        
        # Create pitch envelope (starts low, rises to normal)
        pitch_env = 1.0 - bend_amount * np.exp(-np.arange(bend_samples) / (bend_samples * 0.1))
        
        # Apply simple time-stretching to bent portion (simplified)
        # In production, use proper pitch shifting
        bent_portion = audio_signal[:bend_samples]
        
        # Crude pitch shift via resampling
        try:
            from scipy.interpolate import interp1d
            
            t_orig = np.arange(len(bent_portion))
            t_new = t_orig * (1.0 / (1.0 - bend_amount * 0.5))  # Rough approximation
            
            if t_new[-1] < len(bent_portion):
                interp = interp1d(t_orig, bent_portion, kind='linear', fill_value=0, bounds_error=False)
                audio_signal[:bend_samples] = interp(t_new[:bend_samples])
        except:
            pass  # Fall back to no bend if interpolation fails
        
        return audio_signal
    
    def _apply_wood_character(self, audio_signal: np.ndarray, brightness: float) -> np.ndarray:
        """
        Apply wood character filtering
        
        Args:
            brightness: 0.0-1.0, where 1.0 = bright wood (emphasize highs)
        """
        from scipy import signal as sp_signal
        
        # Apply subtle EQ
        # Bright woods (lower density) → slight high boost
        # Dark woods (higher density) → slight low boost
        
        if brightness > 0.6:
            # Bright wood - boost highs slightly
            cutoff = 1500  # Hz
            sos = sp_signal.butter(1, cutoff / (self.sample_rate / 2), btype='high', output='sos')
            filtered = sp_signal.sosfilt(sos, audio_signal)
            
            # Subtle blend
            blend = (brightness - 0.6) * 0.5
            return audio_signal * (1 - blend) + filtered * blend
        elif brightness < 0.4:
            # Dark wood - boost lows slightly
            cutoff = 800  # Hz
            sos = sp_signal.butter(1, cutoff / (self.sample_rate / 2), btype='low', output='sos')
            filtered = sp_signal.sosfilt(sos, audio_signal)
            
            # Subtle blend
            blend = (0.4 - brightness) * 0.5
            return audio_signal * (1 - blend) + filtered * blend
        else:
            # Neutral
            return audio_signal
    
    def _synthesize_cymbal_strike(
        self,
        player: Player,
        event: StrokeEvent,
        spectral_engine
    ) -> np.ndarray:
        """Synthesize cymbal strike"""
        # Use spectral engine with cymbal category
        return spectral_engine.get_sound(
            category="NAM",  # Use NAM for metallic sounds
            velocity=event.velocity,
            duration=event.duration
        )
    
    def _synthesize_basic(self, event: StrokeEvent, spectral_engine) -> np.ndarray:
        """Basic synthesis fallback"""
        return spectral_engine.get_sound(
            category=event.sound_category,
            velocity=event.velocity,
            duration=event.duration
        )
    
    def _apply_spatial_position(
        self,
        mono_signal: np.ndarray,
        position: Tuple[float, float, float]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply spatial positioning to create stereo image
        
        Args:
            mono_signal: Mono input signal
            position: (x, y, z) position in meters
                     x: left (-) to right (+)
                     y: down (-) to up (+)  [not used currently]
                     z: distance (front=0, back=+)
        
        Returns:
            (left_channel, right_channel)
        """
        x, y, z = position
        
        # Calculate pan position (-1 = full left, +1 = full right)
        pan = np.clip(x, -1.0, 1.0)
        
        # Calculate distance attenuation
        # Closer = louder, farther = quieter
        reference_distance = 1.0  # meters
        distance = np.sqrt(x**2 + y**2 + z**2)
        
        if distance < 0.1:
            distance = 0.1  # Avoid division by zero
        
        # Inverse square law (simplified)
        attenuation = reference_distance / distance
        attenuation = np.clip(attenuation, 0.5, 2.0)  # Reasonable limits
        
        # Apply pan law (constant power panning)
        # Pan angle: -45° (left) to +45° (right)
        angle = (pan + 1.0) * np.pi / 4  # 0 to π/2
        
        left_gain = np.cos(angle) * attenuation
        right_gain = np.sin(angle) * attenuation
        
        # Apply gains
        left_channel = mono_signal * left_gain
        right_channel = mono_signal * right_gain
        
        # Optional: Add subtle delay for distance cue
        # Speed of sound ~ 343 m/s
        if z > 0.5:
            delay_samples = int((z - 0.5) / 343.0 * self.sample_rate)
            if delay_samples > 0 and delay_samples < 100:  # Max 100 samples
                left_channel = np.pad(left_channel, (delay_samples, 0))[:-delay_samples]
                right_channel = np.pad(right_channel, (delay_samples, 0))[:-delay_samples]
        
        return left_channel.astype(np.float32), right_channel.astype(np.float32)
    
    def export_stereo(
        self,
        stereo_signal: np.ndarray,
        filename: str
    ) -> str:
        """
        Export stereo signal to file
        
        Args:
            stereo_signal: 2 x num_samples array
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        import soundfile as sf
        
        # Transpose to (num_samples, 2) for soundfile
        if stereo_signal.shape[0] == 2:
            audio_data = stereo_signal.T
        else:
            audio_data = stereo_signal
        
        # Ensure 16-bit range
        audio_data = np.clip(audio_data, -1.0, 1.0)
        
        # Save
        sf.write(filename, audio_data, self.sample_rate, subtype='PCM_16')
        
        return filename


if __name__ == "__main__":
    from player_system import Ensemble
    from orchestration_engine import OrchestrationEngine, create_stroke_events_from_pattern, OrchestrationStrategy
    from spectral_engine import SpectralEngine
    
    print("🎵 ChendAI Ensemble Mixer")
    print("=" * 70)
    
    # Create ensemble
    print("\n1. Building Ensemble...")
    ensemble = Ensemble().build_standard_melam()
    ensemble.print_ensemble()
    
    # Create test pattern
    print("\n\n2. Creating Test Pattern...")
    test_pattern = ["Ta", "Ka", "Na", "Ta", "Ka", "Na", "Dheem", ".", "Ta", "Ka", "Na", "Ta"]
    test_bpm = 120
    events = create_stroke_events_from_pattern(test_pattern, test_bpm)
    
    # Orchestrate
    print("\n3. Orchestrating...")
    engine = OrchestrationEngine(ensemble)
    orchestrated = engine.orchestrate_sequence(events, OrchestrationStrategy.TRADITIONAL)
    
    print("   Orchestration complete:")
    for pid, pevents in orchestrated.chenda_events.items():
        if pevents:
            player = ensemble.get_player(pid)
            print(f"   - {player.name}: {len(pevents)} events")
    
    # Render (requires spectral engine)
    print("\n4. Testing Mixer Components...")
    mixer = EnsembleMixer()
    
    # Test spatial positioning
    test_signal = np.random.randn(1000)
    left, right = mixer._apply_spatial_position(test_signal, (-0.5, 0, 1.0))
    print(f"   Spatial test: L={np.max(np.abs(left)):.3f}, R={np.max(np.abs(right)):.3f}")
    
    print("\n✅ Ensemble Mixer Ready!")
    print("   Note: Full rendering requires spectral engine integration")
