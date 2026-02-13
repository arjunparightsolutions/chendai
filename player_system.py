"""
ChendAI 6-Player Ensemble System
Models individual players with unique instruments and playing characteristics
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

from material_properties import (
    WoodProperties, MembraneProperties, StickProperties, InstrumentBody,
    WOOD_DATABASE, MEMBRANE_DATABASE, STICK_DATABASE,
    get_random_wood_variant
)


class PlayerRole(Enum):
    """Defines the role of a player in the ensemble"""
    CHENDA_LEAD = "chenda_lead"  # Bhagavathi - Main melodic patterns
    CHENDA_RHYTHM = "chenda_rhythm"  # Base rhythm keeper
    CHENDA_ACCENT = "chenda_accent"  # Accent and fills
    ELATHAALAM_PRIMARY = "elathaalam_primary"  # Main cymbal
    ELATHAALAM_SECONDARY = "elathaalam_secondary"  # Supporting cymbal
    KOMBU = "kombu"  # Wind instrument (drone/melody)


class InstrumentType(Enum):
    """Type of instrument"""
    CHENDA = "chenda"
    ELATHAALAM = "elathaalam"
    KOMBU = "kombu"
    KUZHAL = "kuzhal"


@dataclass
class TimingCharacteristics:
    """Human timing variability for natural feel"""
    base_precision: float  # 0.0-1.0, higher = more precise
    rush_tendency: float  # Negative = drags, Positive = rushes
    groove_offset: float  # Consistent timing offset in ms
    
    def get_timing_offset(self, beat_position: float) -> float:
        """
        Calculate timing offset for a specific beat
        
        Args:
            beat_position: Position in the bar (0.0-1.0)
        
        Returns:
            Timing offset in seconds
        """
        # Human variation
        random_variation = np.random.normal(0, (1.0 - self.base_precision) * 0.01)  # ±10ms max
        
        # Rush/drag tendency
        rush_component = self.rush_tendency * 0.005  # ±5ms
        
        # Consistent groove offset
        groove_component = self.groove_offset / 1000.0  # Convert ms to s
        
        return random_variation + rush_component + groove_component


@dataclass
class ChendaInstrument:
    """A specific Chenda instrument with unique properties"""
    id: str
    body_wood: WoodProperties
    membrane_valam: MembraneProperties  # Right side (high pitch)
    membrane_edamthala: MembraneProperties  # Left side (low pitch)
    body: InstrumentBody
    stick_valam: StickProperties  # Right stick (thin, for treble)
    stick_edamthala: StickProperties  # Left stick (thick, for bass)
    
    def __str__(self):
        return f"Chenda({self.id}, wood={self.body_wood.name}, valam_tension={self.membrane_valam.tension:.2f})"


@dataclass
class ElathaalamInstrument:
    """Cymbal instrument"""
    id: str
    diameter: float  # cm
    thickness: float  # mm
    metal_type: str  # "bronze", "brass"
    age_years: int
    
    def get_base_frequency(self) -> float:
        """Calculate fundamental frequency based on size"""
        # Larger = lower pitch
        return 2000 / self.diameter  # Simplified
    
    def __str__(self):
        return f"Elathaalam({self.id}, {self.metal_type}, {self.diameter}cm)"


@dataclass
class Player:
    """A player in the ensemble"""
    id: str
    name: str
    role: PlayerRole
    instrument_type: InstrumentType
    instrument: any  # ChendaInstrument or ElathaalamInstrument
    timing: TimingCharacteristics
    skill_level: float  # 0.0-1.0
    dynamic_range: Tuple[float, float]  # (min_velocity, max_velocity)
    spatial_position: Tuple[float, float, float]  # (x, y, z) in meters
    gain: float = 1.0  # Volume multiplier
    pan: Optional[float] = None   # Pan position (-1.0 to 1.0), defaults to spatial_position[0]
    mute: bool = False # Mute status
    solo: bool = False # Solo status
    eq_low: float = 0.0 # Low shelf gain (dB)
    eq_mid: float = 0.0 # Mid peak gain (dB)
    eq_high: float = 0.0 # High shelf gain (dB)
    compress: float = 0.0 # Compression amount (0.0-1.0)
    reverb: float = 0.0 # Reverb send amount (0.0-1.0)
    delay: float = 0.0 # Delay send amount (0.0-1.0)
    pitch: float = 0.0 # Pitch shift (semitones)
    saturation: float = 0.0 # Saturation amount (0.0-1.0)
    hpf_freq: float = 20.0 # High pass filter frequency
    lpf_freq: float = 20000.0 # Low pass filter frequency
    stereo_width: float = 1.0 # Stereo width factor
    
    def __post_init__(self):
        if self.pan is None:
            self.pan = self.spatial_position[0]

    def get_velocity_for_intensity(self, intensity: float) -> float:
        """
        Convert musical intensity to player velocity
        
        Args:
            intensity: Musical intensity 0.0-1.0
        
        Returns:
            Actual velocity considering player's dynamic range and skill
        """
        min_vel, max_vel = self.dynamic_range
        
        # Map intensity to player's dynamic range
        base_velocity = min_vel + intensity * (max_vel - min_vel)
        
        # Add slight human variation
        variation = np.random.normal(0, (1.0 - self.skill_level) * 0.05)
        
        return np.clip(base_velocity + variation, 0.0, 1.0)
    
    def __str__(self):
        return f"Player({self.name}, {self.role.value}, {self.instrument})"


# ============================================================================
# INSTRUMENT FACTORY
# ============================================================================

class InstrumentFactory:
    """Factory for creating varied instruments"""
    
    @staticmethod
    def create_chenda(
        chenda_id: str,
        base_wood: str = "jackwood",
        valam_tension: str = "high",
        edamthala_tension: str = "medium",
        valam_stick: str = "bamboo_light",
        edamthala_stick: str = "bamboo_heavy",
        variation: float = 0.08
    ) -> ChendaInstrument:
        """Create a Chenda with slight variations"""
        
        # Get wood with variation
        wood = get_random_wood_variant(base_wood, variation)
        
        # Get membranes
        membrane_v = MEMBRANE_DATABASE[f"cow_{valam_tension}"]
        membrane_e = MEMBRANE_DATABASE[f"cow_{edamthala_tension}"]
        
        # Add slight tension variation
        membrane_v.tension *= np.random.uniform(0.95, 1.05)
        membrane_e.tension *= np.random.uniform(0.95, 1.05)
        
        # Create body
        body = InstrumentBody(
            wood_type=base_wood,
            length=np.random.uniform(58, 62),  # cm
            diameter=np.random.uniform(28, 32),
            wall_thickness=np.random.uniform(2.3, 2.7)
        )
        
        # Get sticks
        stick_v = STICK_DATABASE[valam_stick]
        stick_e = STICK_DATABASE[edamthala_stick]
        
        return ChendaInstrument(
            id=chenda_id,
            body_wood=wood,
            membrane_valam=membrane_v,
            membrane_edamthala=membrane_e,
            body=body,
            stick_valam=stick_v,
            stick_edamthala=stick_e
        )
    
    @staticmethod
    def create_elathaalam(
        elathaalam_id: str,
        size: str = "medium"
    ) -> ElathaalamInstrument:
        """Create an Elathaalam cymbal"""
        
        sizes = {
            "small": (12, 14),
            "medium": (14, 16),
            "large": (16, 18)
        }
        
        diameter_range = sizes.get(size, sizes["medium"])
        diameter = np.random.uniform(*diameter_range)
        
        return ElathaalamInstrument(
            id=elathaalam_id,
            diameter=diameter,
            thickness=np.random.uniform(1.5, 2.5),
            metal_type=random.choice(["bronze", "brass"]),
            age_years=random.randint(1, 10)
        )


# ============================================================================
# PLAYER FACTORY
# ============================================================================

class PlayerFactory:
    """Factory for creating players with appropriate characteristics"""
    
    @staticmethod
    def create_chenda_lead(player_id: str = "P1") -> Player:
        """Create lead Chenda player (Bhagavathi)"""
        
        instrument = InstrumentFactory.create_chenda(
            chenda_id=f"{player_id}_chenda",
            base_wood="jackwood",
            valam_tension="high",  # Tight for bright, cutting sound
            valam_stick="bamboo_medium"
        )
        
        timing = TimingCharacteristics(
            base_precision=0.95,  # Very precise
            rush_tendency=0.02,  # Slight rush (leads the group)
            groove_offset=0.0
        )
        
        return Player(
            id=player_id,
            name="Lead Player",
            role=PlayerRole.CHENDA_LEAD,
            instrument_type=InstrumentType.CHENDA,
            instrument=instrument,
            timing=timing,
            skill_level=0.95,
            dynamic_range=(0.6, 1.0),  # Loud player
            spatial_position=(-0.3, 0, 1.0)  # Slightly left, front
        )
    
    @staticmethod
    def create_chenda_rhythm(player_id: str = "P2") -> Player:
        """Create rhythm Chenda player"""
        
        instrument = InstrumentFactory.create_chenda(
            chenda_id=f"{player_id}_chenda",
            base_wood="teak",
            valam_tension="medium",  # Balanced
            valam_stick="bamboo_medium"
        )
        
        timing = TimingCharacteristics(
            base_precision=0.98,  # Most precise (timekeeper)
            rush_tendency=0.0,  # Perfectly on time
            groove_offset=0.0
        )
        
        return Player(
            id=player_id,
            name="Rhythm Player",
            role=PlayerRole.CHENDA_RHYTHM,
            instrument_type=InstrumentType.CHENDA,
            instrument=instrument,
            timing=timing,
            skill_level=0.92,
            dynamic_range=(0.5, 0.85),  # Moderate volume
            spatial_position=(0.3, 0, 1.0)  # Slightly right, front
        )
    
    @staticmethod
    def create_chenda_accent(player_id: str = "P3") -> Player:
        """Create accent Chenda player"""
        
        instrument = InstrumentFactory.create_chenda(
            chenda_id=f"{player_id}_chenda",
            base_wood="rosewood",
            valam_tension="high",
            valam_stick="teak_medium"  # Heavier stick for accents
        )
        
        timing = TimingCharacteristics(
            base_precision=0.90,  # Slightly looser
            rush_tendency=-0.01,  # Slight drag (creates tension)
            groove_offset=0.0
        )
        
        return Player(
            id=player_id,
            name="Accent Player",
            role=PlayerRole.CHENDA_ACCENT,
            instrument_type=InstrumentType.CHENDA,
            instrument=instrument,
            timing=timing,
            skill_level=0.90,
            dynamic_range=(0.4, 1.0),  # Wide dynamic range
            spatial_position=(0, 0, 0.8)  # Center, slightly back
        )
    
    @staticmethod
    def create_elathaalam_primary(player_id: str = "P4") -> Player:
        """Create primary Elathaalam player"""
        
        instrument = InstrumentFactory.create_elathaalam(
            elathaalam_id=f"{player_id}_elathaalam",
            size="medium"
        )
        
        timing = TimingCharacteristics(
            base_precision=0.93,
            rush_tendency=0.0,
            groove_offset=0.0
        )
        
        return Player(
            id=player_id,
            name="Elathaalam 1",
            role=PlayerRole.ELATHAALAM_PRIMARY,
            instrument_type=InstrumentType.ELATHAALAM,
            instrument=instrument,
            timing=timing,
            skill_level=0.90,
            dynamic_range=(0.5, 0.9),
            spatial_position=(-0.8, 0, 1.2)  # Left, front
        )
    
    @staticmethod
    def create_elathaalam_secondary(player_id: str = "P5") -> Player:
        """Create secondary Elathaalam player"""
        
        instrument = InstrumentFactory.create_elathaalam(
            elathaalam_id=f"{player_id}_elathaalam",
            size="small"  # Slightly smaller = higher pitch
        )
        
        timing = TimingCharacteristics(
            base_precision=0.91,
            rush_tendency=0.0,
            groove_offset=0.5  # 0.5ms offset for subtle chorus
        )
        
        return Player(
            id=player_id,
            name="Elathaalam 2",
            role=PlayerRole.ELATHAALAM_SECONDARY,
            instrument_type=InstrumentType.ELATHAALAM,
            instrument=instrument,
            timing=timing,
            skill_level=0.88,
            dynamic_range=(0.4, 0.8),
            spatial_position=(0.8, 0, 1.2)  # Right, front
        )
    
    @staticmethod
    def create_kombu(player_id: str = "P6") -> Player:
        """Create Kombu (wind) player"""
        
        # For now, use a simple placeholder
        # Wind instruments will be synthesized differently
        
        timing = TimingCharacteristics(
            base_precision=0.85,  # Looser timing for wind
            rush_tendency=0.0,
            groove_offset=0.0
        )
        
        return Player(
            id=player_id,
            name="Kombu Player",
            role=PlayerRole.KOMBU,
            instrument_type=InstrumentType.KOMBU,
            instrument=None,  # Will implement wind synthesis separately
            timing=timing,
            skill_level=0.85,
            dynamic_range=(0.3, 0.7),
            spatial_position=(0, 0, 1.5)  # Center, back
        )


# ============================================================================
# ENSEMBLE BUILDER
# ============================================================================

class Ensemble:
    """Manages the complete 6-player ensemble"""
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
    
    def build_standard_melam(self) -> 'Ensemble':
        """Build a standard 6-player Chendamelam ensemble"""
        
        self.players = {
            "P1": PlayerFactory.create_chenda_lead("P1"),
            "P2": PlayerFactory.create_chenda_rhythm("P2"),
            "P3": PlayerFactory.create_chenda_accent("P3"),
            "P4": PlayerFactory.create_elathaalam_primary("P4"),
            "P5": PlayerFactory.create_elathaalam_secondary("P5"),
            "P6": PlayerFactory.create_kombu("P6")
        }
        
        return self
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get a specific player"""
        return self.players.get(player_id)
    
    def get_players_by_role(self, role: PlayerRole) -> List[Player]:
        """Get all players with a specific role"""
        return [p for p in self.players.values() if p.role == role]
    
    def get_chenda_players(self) -> List[Player]:
        """Get all Chenda players"""
        return [p for p in self.players.values() if p.instrument_type == InstrumentType.CHENDA]
    
    def get_cymbal_players(self) -> List[Player]:
        """Get all cymbal players"""
        return [p for p in self.players.values() if p.instrument_type == InstrumentType.ELATHAALAM]
    
    def print_ensemble(self):
        """Print ensemble details"""
        print("🎵 Chendamelam Ensemble")
        print("=" * 70)
        for player_id, player in self.players.items():
            print(f"\n{player_id}: {player.name} ({player.role.value})")
            print(f"   Skill: {player.skill_level:.2f} | Dynamics: {player.dynamic_range}")
            print(f"   Position: {player.spatial_position}")
            print(f"   Timing: Precision={player.timing.base_precision:.2f}, Rush={player.timing.rush_tendency:+.3f}")
            print(f"   Instrument: {player.instrument}")


if __name__ == "__main__":
    print("🎵 ChendAI 6-Player Ensemble System")
    print("=" * 70)
    
    # Build standard ensemble
    ensemble = Ensemble().build_standard_melam()
    ensemble.print_ensemble()
    
    print("\n\n🧪 Testing Player Characteristics:")
    
    # Test velocity mapping
    lead = ensemble.get_player("P1")
    rhythm = ensemble.get_player("P2")
    
    print(f"\nIntensity 0.5:")
    print(f"  Lead player velocity: {lead.get_velocity_for_intensity(0.5):.3f}")
    print(f"  Rhythm player velocity: {rhythm.get_velocity_for_intensity(0.5):.3f}")
    
    print(f"\nIntensity 1.0:")
    print(f"  Lead player velocity: {lead.get_velocity_for_intensity(1.0):.3f}")
    print(f"  Rhythm player velocity: {rhythm.get_velocity_for_intensity(1.0):.3f}")
    
    # Test timing variation
    print(f"\n\nTiming Offsets (10 beats):")
    print(f"Lead player: {[f'{lead.timing.get_timing_offset(i/10)*1000:.2f}' for i in range(10)]} ms")
    print(f"Rhythm player: {[f'{rhythm.timing.get_timing_offset(i/10)*1000:.2f}' for i in range(10)]} ms")
    
    print("\n✅ Player System Ready!")
