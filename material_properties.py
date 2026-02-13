"""
ChendAI Material Properties System
Physical properties of woods, leathers, and other materials used in traditional instruments
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional
import json
import os


@dataclass
class WoodProperties:
    """Physical properties of wood materials"""
    name: str
    density: float  # kg/m³
    youngs_modulus: float  # GPa (elasticity)
    damping_coefficient: float  # 0.0-1.0
    speed_of_sound: float  # m/s
    hardness: float  # Shore D scale
    
    @property
    def stiffness_factor(self) -> float:
        """Calculate stiffness factor for synthesis"""
        return np.sqrt(self.youngs_modulus / self.density)
    
    @property
    def resonance_brightness(self) -> float:
        """Higher density woods produce darker tones"""
        return 1.0 - (self.density - 500) / 1000  # Normalize 500-1500 range


@dataclass
class MembraneProperties:
    """Properties of drum head/membrane"""
    material: str  # "cow_leather", "goat_leather", "synthetic"
    thickness: float  # mm
    tension: float  # N/m² (normalized 0-1 for easy use)
    age_months: int  # Affects stiffness
    moisture_absorption: float  # 0.0-1.0
    
    @property
    def effective_tension(self) -> float:
        """Calculate effective tension considering age"""
        # Leather stiffens with age
        age_factor = 1.0 + (self.age_months / 24) * 0.3  # +30% over 2 years
        return self.tension * age_factor
    
    @property
    def fundamental_freq_factor(self) -> float:
        """Higher tension = higher pitch"""
        return np.sqrt(self.effective_tension)


@dataclass
class StickProperties:
    """Properties of drum stick"""
    material: str
    mass: float  # grams
    length: float  # cm
    diameter: float  # cm
    tip_hardness: float  # Shore D scale
    tip_radius: float  # mm
    
    @property
    def momentum_factor(self) -> float:
        """Heavier sticks = more momentum = louder, deeper"""
        return self.mass / 100.0  # Normalize around 100g
    
    @property
    def resonant_frequency(self) -> float:
        """Stick's own resonant frequency (Hz)"""
        # Simplified beam resonance formula
        # Higher for shorter, stiffer sticks
        wood_stiffness = WOOD_DATABASE.get(self.material, WOOD_DATABASE["bamboo"]).youngs_modulus
        return 100 * wood_stiffness / (self.length ** 2)
    
    @property
    def impact_brightness(self) -> float:
        """Hard tips = brighter impact"""
        return self.tip_hardness / 100.0


@dataclass
class InstrumentBody:
    """Physical body of the instrument"""
    wood_type: str
    length: float  # cm
    diameter: float  # cm
    wall_thickness: float  # cm
    
    @property
    def cavity_volume(self) -> float:
        """Internal volume in cm³"""
        inner_radius = (self.diameter / 2) - self.wall_thickness
        return np.pi * (inner_radius ** 2) * self.length
    
    @property
    def resonance_frequency(self) -> float:
        """Helmholtz resonance of cavity (Hz)"""
        # Simplified: smaller cavity = higher resonance
        return 15000 / np.sqrt(self.cavity_volume)


# ============================================================================
# MATERIAL DATABASE
# ============================================================================

WOOD_DATABASE: Dict[str, WoodProperties] = {
    "jackwood": WoodProperties(
        name="Jackwood (Varikka)",
        density=720,  # kg/m³
        youngs_modulus=9.8,  # GPa
        damping_coefficient=0.15,
        speed_of_sound=3800,
        hardness=65
    ),
    "rosewood": WoodProperties(
        name="Rosewood (Eetti)",
        density=900,
        youngs_modulus=12.5,
        damping_coefficient=0.18,
        speed_of_sound=4200,
        hardness=80
    ),
    "teak": WoodProperties(
        name="Teak (Thekkу)",
        density=680,
        youngs_modulus=10.2,
        damping_coefficient=0.12,
        speed_of_sound=3900,
        hardness=70
    ),
    "bamboo": WoodProperties(
        name="Bamboo (Mula)",
        density=400,
        youngs_modulus=17.0,  # Very stiff for its weight
        damping_coefficient=0.08,
        speed_of_sound=4500,
        hardness=55
    ),
    "mango": WoodProperties(
        name="Mango Wood (Maavu)",
        density=650,
        youngs_modulus=8.5,
        damping_coefficient=0.14,
        speed_of_sound=3600,
        hardness=60
    )
}


MEMBRANE_DATABASE: Dict[str, MembraneProperties] = {
    "cow_high": MembraneProperties(
        material="cow_leather",
        thickness=3.2,
        tension=0.85,  # High tension
        age_months=6,
        moisture_absorption=0.3
    ),
    "cow_medium": MembraneProperties(
        material="cow_leather",
        thickness=3.5,
        tension=0.65,  # Medium tension
        age_months=12,
        moisture_absorption=0.3
    ),
    "cow_low": MembraneProperties(
        material="cow_leather",
        thickness=4.0,
        tension=0.45,  # Low tension
        age_months=18,
        moisture_absorption=0.3
    ),
    "goat_high": MembraneProperties(
        material="goat_leather",
        thickness=2.8,
        tension=0.75,
        age_months=4,
        moisture_absorption=0.25
    )
}


STICK_DATABASE: Dict[str, StickProperties] = {
    "bamboo_light": StickProperties(
        material="bamboo",
        mass=85,
        length=35,
        diameter=1.2,
        tip_hardness=70,
        tip_radius=8
    ),
    "bamboo_medium": StickProperties(
        material="bamboo",
        mass=95,
        length=35,
        diameter=1.4,
        tip_hardness=75,
        tip_radius=8
    ),
    "bamboo_heavy": StickProperties(
        material="bamboo",
        mass=110,
        length=38,
        diameter=1.5,
        tip_hardness=78,
        tip_radius=9
    ),
    "teak_medium": StickProperties(
        material="teak",
        mass=125,
        length=34,
        diameter=1.3,
        tip_hardness=82,
        tip_radius=7
    ),
    "rosewood_heavy": StickProperties(
        material="rosewood",
        mass=145,
        length=33,
        diameter=1.4,
        tip_hardness=88,
        tip_radius=6
    )
}


# ============================================================================
# MATERIAL EFFECTS CALCULATOR
# ============================================================================

class MaterialEffectsCalculator:
    """Calculates how material properties affect synthesis parameters"""
    
    @staticmethod
    def calculate_frequency_shift(
        base_freq: float,
        membrane: MembraneProperties,
        wood: WoodProperties
    ) -> float:
        """
        Calculate frequency shift based on material properties
        Higher tension = higher pitch
        Denser wood = slightly lower pitch (more mass)
        """
        tension_factor = membrane.fundamental_freq_factor
        wood_factor = 1.0 - (wood.density - 650) / 2000  # Slight shift
        
        return base_freq * tension_factor * wood_factor
    
    @staticmethod
    def calculate_decay_time(
        base_decay: float,
        membrane: MembraneProperties,
        wood: WoodProperties
    ) -> float:
        """
        Calculate decay time based on damping
        More damping = shorter decay
        """
        membrane_damping = 0.3  # Leather has moderate damping
        combined_damping = (wood.damping_coefficient + membrane_damping) / 2
        
        # More damping = shorter decay
        return base_decay * (1.0 - combined_damping * 0.5)
    
    @staticmethod
    def calculate_brightness(
        stick: StickProperties,
        impact_velocity: float,
        contact_point: float = 0.5
    ) -> float:
        """
        Calculate brightness factor (high-frequency content)
        
        Args:
            stick: Stick properties
            impact_velocity: 0.0-1.0 (normalized velocity)
            contact_point: 0.0 (edge) to 1.0 (center)
        
        Returns:
            Brightness factor (0.0-1.0)
        """
        # Hard tips = brighter
        hardness_brightness = stick.impact_brightness
        
        # Faster strikes = brighter
        velocity_brightness = min(impact_velocity * 1.5, 1.0)
        
        # Center hits = brighter, edge hits = darker
        position_brightness = contact_point * 0.3 + 0.7
        
        return hardness_brightness * velocity_brightness * position_brightness
    
    @staticmethod
    def calculate_body_resonance_freq(
        body: InstrumentBody
    ) -> float:
        """Calculate the dominant body resonance frequency"""
        return body.resonance_frequency
    
    @staticmethod
    def calculate_impact_force(
        stick: StickProperties,
        velocity: float
    ) -> float:
        """
        Calculate impact force (affects amplitude and transient)
        F = m * v (simplified)
        """
        return stick.momentum_factor * velocity


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_random_wood_variant(base_wood: str, variation: float = 0.1) -> WoodProperties:
    """
    Get a wood variant with slight property variations
    This creates unique instruments from the same wood type
    
    Args:
        base_wood: Base wood type from database
        variation: Amount of variation (0.0-1.0), default 10%
    """
    base = WOOD_DATABASE[base_wood]
    
    return WoodProperties(
        name=f"{base.name} (Variant)",
        density=base.density * np.random.uniform(1 - variation, 1 + variation),
        youngs_modulus=base.youngs_modulus * np.random.uniform(1 - variation/2, 1 + variation/2),
        damping_coefficient=base.damping_coefficient * np.random.uniform(1 - variation, 1 + variation),
        speed_of_sound=base.speed_of_sound * np.random.uniform(1 - variation/4, 1 + variation/4),
        hardness=base.hardness * np.random.uniform(1 - variation, 1 + variation)
    )


def save_instrument_database(filepath: str = "instruments_db.json"):
    """Save instrument database to JSON"""
    # This would be a more complex function to serialize all variants
    pass


def load_instrument_database(filepath: str = "instruments_db.json"):
    """Load instrument database from JSON"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


if __name__ == "__main__":
    # Test material properties
    print("🎵 ChendAI Material Properties System")
    print("=" * 60)
    
    print("\n📊 Wood Database:")
    for name, wood in WOOD_DATABASE.items():
        print(f"\n{wood.name}:")
        print(f"  Density: {wood.density} kg/m³")
        print(f"  Stiffness Factor: {wood.stiffness_factor:.2f}")
        print(f"  Resonance Brightness: {wood.resonance_brightness:.2f}")
    
    print("\n\n📊 Stick Database:")
    for name, stick in STICK_DATABASE.items():
        print(f"\n{name}:")
        print(f"  Mass: {stick.mass}g")
        print(f"  Resonant Freq: {stick.resonant_frequency:.1f} Hz")
        print(f"  Impact Brightness: {stick.impact_brightness:.2f}")
    
    print("\n\n🧪 Testing Material Effects:")
    calc = MaterialEffectsCalculator()
    
    test_membrane = MEMBRANE_DATABASE["cow_high"]
    test_wood = WOOD_DATABASE["jackwood"]
    test_stick = STICK_DATABASE["bamboo_medium"]
    
    base_freq = 450
    shifted_freq = calc.calculate_frequency_shift(base_freq, test_membrane, test_wood)
    print(f"\nBase Frequency: {base_freq} Hz")
    print(f"Material-Shifted Frequency: {shifted_freq:.1f} Hz")
    
    brightness = calc.calculate_brightness(test_stick, impact_velocity=0.8, contact_point=0.7)
    print(f"Impact Brightness (vel=0.8, center=0.7): {brightness:.3f}")
    
    print("\n✅ Material Properties System Ready!")
