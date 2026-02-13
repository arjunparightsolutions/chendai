"""
ChendAI Stick Impact Physics
Advanced modeling of stick-membrane interaction
"""

import numpy as np
from material_properties import StickProperties, MembraneProperties, WoodProperties
from physical_modeling import generate_transient
from typing import Tuple


class StickImpactModeler:
    """Models the physics of stick striking membrane"""
    
    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate
    
    def calculate_impact_spectrum(
        self,
        stick: StickProperties,
        velocity: float,
        contact_point: float = 0.5,
        angle: float = 90.0
    ) -> dict:
        """
        Calculate the spectral characteristics of stick impact
        
        Args:
            stick: Stick properties
            velocity: Strike velocity (0.0-1.0 normalized)
            contact_point: 0.0 (edge) to 1.0 (center)
            angle: Strike angle in degrees (90 = perpendicular)
        
        Returns:
            Dictionary with impact characteristics
        """
        # Impact force (momentum transfer)
        # F = m * v * cos(angle)
        angle_rad = np.radians(angle)
        impact_force = stick.momentum_factor * velocity * np.cos(angle_rad - np.pi/2)
        
        # Contact duration (harder tips = shorter contact)
        # Typical range: 0.1ms - 2ms
        base_contact_duration = 0.001  # 1ms
        contact_duration = base_contact_duration / stick.impact_brightness
        
        # Spectral centroid (brightness)
        # Hard sticks + fast strikes = bright (high centroid)
        # Soft sticks + slow strikes = dark (low centroid)
        base_centroid = 2000  # Hz
        hardness_factor = stick.impact_brightness
        velocity_factor = 1.0 + velocity
        position_factor = 0.5 + contact_point * 0.5  # Center = brighter
        
        spectral_centroid = base_centroid * hardness_factor * velocity_factor * position_factor
        
        # Spectral width (spread of frequencies)
        # Fast impacts = wide spectrum (lots of harmonics)
        spectral_width = 1500 * velocity + 500
        
        # Transient energy (click/slap sound)
        # Harder sticks = more transient
        transient_energy = stick.impact_brightness * velocity * 0.3
        
        # Stick resonance contribution
        # The stick itself rings at its resonant frequency
        stick_resonance_freq = stick.resonant_frequency
        stick_resonance_energy = 0.1 * velocity  # Subtle contribution
        
        return {
            'impact_force': impact_force,
            'contact_duration': contact_duration,
            'spectral_centroid': spectral_centroid,
            'spectral_width': spectral_width,
            'transient_energy': transient_energy,
            'stick_resonance_freq': stick_resonance_freq,
            'stick_resonance_energy': stick_resonance_energy,
            'angle': angle,
            'contact_point': contact_point
        }
    
    def calculate_membrane_response(
        self,
        membrane: MembraneProperties,
        impact_spectrum: dict
    ) -> dict:
        """
        Calculate how the membrane responds to stick impact
        
        Args:
            membrane: Membrane properties
            impact_spectrum: Output from calculate_impact_spectrum
        
        Returns:
            Membrane response characteristics
        """
        # Membrane excitation amplitude
        # Higher tension = more efficient energy transfer
        excitation_amplitude = impact_spectrum['impact_force'] * membrane.effective_tension
        
        # Decay rate
        # Thicker membranes = longer decay
        # Higher tension = faster decay (more rigid)
        base_decay = 0.5
        thickness_factor = membrane.thickness / 3.5  # Normalized around 3.5mm
        tension_factor = 1.0 / membrane.effective_tension
        
        decay_time = base_decay * thickness_factor * tension_factor
        
        # Pitch bend (membrane "gives" under impact)
        # Softer membranes bend more, creating momentary pitch drop
        pitch_bend_amount = (1.0 - membrane.effective_tension) * 0.15  # Up to 15% drop
        pitch_bend_duration = impact_spectrum['contact_duration'] * 3
        
        return {
            'excitation_amplitude': excitation_amplitude,
            'decay_time': decay_time,
            'pitch_bend_amount': pitch_bend_amount,
            'pitch_bend_duration': pitch_bend_duration
        }
    
    def generate_impact_transient(
        self,
        impact_spectrum: dict,
        duration: float = 0.05
    ) -> np.ndarray:
        """
        Generate the transient (click/slap) component of stick impact
        
        Args:
            impact_spectrum: Output from calculate_impact_spectrum
            duration: Duration of transient in seconds
        
        Returns:
            Transient waveform
        """
        if impact_spectrum['transient_energy'] < 0.01:
            return np.zeros(int(duration * self.sample_rate))
        
        # Generate band-limited noise burst
        transient = generate_transient(
            duration=duration,
            sample_rate=self.sample_rate,
            center_freq=impact_spectrum['spectral_centroid'],
            bandwidth=impact_spectrum['spectral_width'],
            decay=impact_spectrum['contact_duration'] * 10  # Fast decay
        )
        
        # Scale by transient energy
        transient = transient * impact_spectrum['transient_energy']
        
        return transient
    
    def generate_stick_resonance(
        self,
        impact_spectrum: dict,
        duration: float = 0.1
    ) -> np.ndarray:
        """
        Generate the stick's own resonance contribution
        
        The stick vibrates at its natural frequency when it strikes
        This adds a subtle "woody" character
        """
        if impact_spectrum['stick_resonance_energy'] < 0.01:
            return np.zeros(int(duration * self.sample_rate))
        
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        # Simple damped sinusoid at stick's resonant frequency
        freq = impact_spectrum['stick_resonance_freq']
        decay = 15.0  # Fast decay
        
        waveform = np.sin(2 * np.pi * freq * t) * np.exp(-decay * t)
        waveform = waveform * impact_spectrum['stick_resonance_energy']
        
        return waveform
    
    def apply_contact_point_filtering(
        self,
        signal: np.ndarray,
        contact_point: float
    ) -> np.ndarray:
        """
        Apply filtering based on where the stick hit
        
        Center hits (contact_point = 1.0) are brighter
        Edge hits (contact_point = 0.0) are darker
        
        Args:
            signal: Input signal
            contact_point: 0.0 (edge) to 1.0 (center)
        
        Returns:
            Filtered signal
        """
        from scipy import signal as sp_signal
        
        # Edge hits emphasize lower frequencies
        # Center hits emphasize higher frequencies
        
        if contact_point > 0.5:
            # Center hit - slight high-pass emphasis
            # Boost highs
            cutoff = 300 + (contact_point - 0.5) * 1000  # 300-800 Hz
            sos = sp_signal.butter(1, cutoff / (self.sample_rate / 2), btype='high', output='sos')
            filtered = sp_signal.sosfilt(sos, signal)
            
            # Blend with original
            blend = (contact_point - 0.5) * 0.4  # Up to 20% blend
            return signal * (1 - blend) + filtered * blend
        else:
            # Edge hit - low-pass emphasis
            # Attenuate highs
            cutoff = 1500 + contact_point * 2000  # 1500-3500 Hz
            sos = sp_signal.butter(1, cutoff / (self.sample_rate / 2), btype='low', output='sos')
            filtered = sp_signal.sosfilt(sos, signal)
            
            # Blend with original
            blend = (0.5 - contact_point) * 0.4  # Up to 20% blend
            return signal * (1 - blend) + filtered * blend
    
    def calculate_rebound_dynamics(
        self,
        stick: StickProperties,
        membrane: MembraneProperties,
        velocity: float
    ) -> dict:
        """
        Calculate stick rebound characteristics
        This affects the timing for rapid successive strikes
        
        Args:
            stick: Stick properties
            membrane: Membrane properties
            velocity: Strike velocity
        
        Returns:
            Rebound characteristics
        """
        # Coefficient of restitution (bounciness)
        # Harder membranes = more bounce
        # Lighter sticks = faster rebound
        
        base_restitution = 0.3  # Typical for leather
        membrane_factor = membrane.effective_tension
        stick_factor = 1.0 / stick.momentum_factor
        
        restitution = base_restitution * membrane_factor * stick_factor
        
        # Rebound velocity
        rebound_velocity = velocity * restitution
        
        # Time to rebound (how long stick is in contact)
        contact_time = 0.001 / stick.impact_brightness  # Harder = shorter
        
        # Minimum time between hits (physical limit)
        min_inter_hit_time = contact_time * 2
        
        return {
            'restitution': restitution,
            'rebound_velocity': rebound_velocity,
            'contact_time': contact_time,
            'min_inter_hit_time': min_inter_hit_time
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_complete_strike_profile(
    stick: StickProperties,
    membrane: MembraneProperties,
    velocity: float,
    contact_point: float = 0.5,
    angle: float = 90.0,
    sample_rate: int = 44100
) -> dict:
    """
    Create a complete strike profile combining all physics
    
    This is the main function to use for synthesis
    
    Returns:
        Complete physical parameters for synthesis
    """
    modeler = StickImpactModeler(sample_rate)
    
    # Calculate impact spectrum
    impact = modeler.calculate_impact_spectrum(stick, velocity, contact_point, angle)
    
    # Calculate membrane response
    response = modeler.calculate_membrane_response(membrane, impact)
    
    # Calculate rebound
    rebound = modeler.calculate_rebound_dynamics(stick, membrane, velocity)
    
    # Generate transient components
    transient = modeler.generate_impact_transient(impact, duration=0.05)
    stick_resonance = modeler.generate_stick_resonance(impact, duration=0.1)
    
    return {
        'impact': impact,
        'response': response,
        'rebound': rebound,
        'transient_waveform': transient,
        'stick_resonance_waveform': stick_resonance,
        'velocity': velocity,
        'contact_point': contact_point
    }


if __name__ == "__main__":
    from material_properties import STICK_DATABASE, MEMBRANE_DATABASE
    
    print("🎵 ChendAI Stick Impact Physics")
    print("=" * 60)
    
    # Test with different sticks
    sticks = ["bamboo_light", "bamboo_heavy", "rosewood_heavy"]
    membrane = MEMBRANE_DATABASE["cow_high"]
    
    modeler = StickImpactModeler()
    
    for stick_name in sticks:
        stick = STICK_DATABASE[stick_name]
        
        print(f"\n🥁 Testing {stick_name}:")
        print(f"   Mass: {stick.mass}g, Hardness: {stick.tip_hardness}")
        
        # Test different velocities
        for velocity in [0.3, 0.6, 1.0]:
            impact = modeler.calculate_impact_spectrum(
                stick, velocity, contact_point=0.7
            )
            
            response = modeler.calculate_membrane_response(membrane, impact)
            
            print(f"\n   Velocity {velocity:.1f}:")
            print(f"     Impact Force: {impact['impact_force']:.3f}")
            print(f"     Spectral Centroid: {impact['spectral_centroid']:.0f} Hz")
            print(f"     Transient Energy: {impact['transient_energy']:.3f}")
            print(f"     Decay Time: {response['decay_time']:.3f}s")
    
    # Test contact point variation
    print("\n\n🎯 Contact Point Variation (bamboo_medium, velocity=0.8):")
    stick = STICK_DATABASE["bamboo_medium"]
    
    for contact_point in [0.0, 0.5, 1.0]:
        impact = modeler.calculate_impact_spectrum(
            stick, 0.8, contact_point=contact_point
        )
        
        position_name = "Edge" if contact_point == 0.0 else ("Mid" if contact_point == 0.5 else "Center")
        print(f"\n   {position_name} (contact={contact_point}):")
        print(f"     Spectral Centroid: {impact['spectral_centroid']:.0f} Hz")
        print(f"     Brightness: {impact['spectral_centroid'] / 2000:.2f}x")
    
    print("\n✅ Stick Physics System Ready!")
