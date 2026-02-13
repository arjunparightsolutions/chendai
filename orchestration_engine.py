"""
ChendAI Orchestration Engine
AI system that assigns musical events to specific players in the ensemble
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

from player_system import Ensemble, Player, PlayerRole, InstrumentType
from traditional_patterns import STROKE_LIBRARY


class OrchestrationStrategy(Enum):
    """Different orchestration strategies"""
    TRADITIONAL = "traditional"  # Follow traditional melam rules
    DYNAMIC = "dynamic"  # AI decides based on pattern complexity
    ANTIPHONAL = "antiphonal"  # Call and response between players
    UNISON = "unison"  # All chendas play together
    LAYERED = "layered"  # Stagger entries


@dataclass
class StrokeEvent:
    """A single stroke event"""
    time: float  # Absolute time in seconds
    stroke_type: str  # "Ta", "Ka", "Na", etc.
    sound_category: str  # "THAAM", "CHAPU", "NAM", etc.
    intensity: float  # 0.0-1.0
    duration: float  # Duration in seconds
    
    # Orchestration metadata
    assigned_player: Optional[str] = None
    velocity: Optional[float] = None
    contact_point: Optional[float] = None


@dataclass
class OrchestrationPattern:
    """Complete orchestrated pattern with player assignments"""
    chenda_events: Dict[str, List[StrokeEvent]] = field(default_factory=dict)  # player_id -> events
    cymbal_events: Dict[str, List[StrokeEvent]] = field(default_factory=dict)
    wind_events: Dict[str, List[StrokeEvent]] = field(default_factory=dict)
    
    def get_all_player_events(self) -> Dict[str, List[StrokeEvent]]:
        """Get all events organized by player"""
        all_events = {}
        all_events.update(self.chenda_events)
        all_events.update(self.cymbal_events)
        all_events.update(self.wind_events)
        return all_events


class OrchestrationEngine:
    """
    AI Orchestration Engine
    Decides which player plays which stroke at each moment
    """
    
    def __init__(self, ensemble: Ensemble):
        self.ensemble = ensemble
        self.strategy = OrchestrationStrategy.TRADITIONAL
    
    def orchestrate_sequence(
        self,
        events: List[StrokeEvent],
        strategy: OrchestrationStrategy = OrchestrationStrategy.TRADITIONAL
    ) -> OrchestrationPattern:
        """
        Orchestrate a sequence of musical events
        
        Args:
            events: List of stroke events to orchestrate
            strategy: Orchestration strategy to use
        
        Returns:
            Orchestrated pattern with player assignments
        """
        self.strategy = strategy
        
        if strategy == OrchestrationStrategy.TRADITIONAL:
            return self._orchestrate_traditional(events)
        elif strategy == OrchestrationStrategy.DYNAMIC:
            return self._orchestrate_dynamic(events)
        elif strategy == OrchestrationStrategy.ANTIPHONAL:
            return self._orchestrate_antiphonal(events)
        elif strategy == OrchestrationStrategy.UNISON:
            return self._orchestrate_unison(events)
        elif strategy == OrchestrationStrategy.LAYERED:
            return self._orchestrate_layered(events)
        else:
            return self._orchestrate_traditional(events)
    
    def _orchestrate_traditional(self, events: List[StrokeEvent]) -> OrchestrationPattern:
        """
        Traditional Chendamelam orchestration rules:
        
        1. Lead player handles complex patterns and melodic lines
        2. Rhythm player maintains steady pulse (main beats)
        3. Accent player emphasizes important structural points
        4. Cymbals mark time divisions and structural beats
        """
        pattern = OrchestrationPattern()
        
        # Initialize event lists
        lead_player = self.ensemble.get_players_by_role(PlayerRole.CHENDA_LEAD)[0]
        rhythm_player = self.ensemble.get_players_by_role(PlayerRole.CHENDA_RHYTHM)[0]
        accent_player = self.ensemble.get_players_by_role(PlayerRole.CHENDA_ACCENT)[0]
        
        pattern.chenda_events[lead_player.id] = []
        pattern.chenda_events[rhythm_player.id] = []
        pattern.chenda_events[accent_player.id] = []
        
        # Get cymbals
        cymbals = self.ensemble.get_cymbal_players()
        for cymbal in cymbals:
            pattern.cymbal_events[cymbal.id] = []
        
        # Analyze pattern complexity
        complexity = self._analyze_pattern_complexity(events)
        
        # Assign events to players
        for i, event in enumerate(events):
            if event.sound_category == "REST":
                continue
            
            # Determine which player should play this
            player = self._select_player_traditional(
                event, i, complexity, lead_player, rhythm_player, accent_player
            )
            
            # Create assigned event
            assigned_event = self._assign_event_to_player(event, player)
            
            # Add to pattern
            pattern.chenda_events[player.id].append(assigned_event)
            
            # Add cymbal events on structural beats
            if self._is_structural_beat(i, len(events)):
                self._add_cymbal_events(event.time, cymbals, pattern)
        
        return pattern
    
    def _select_player_traditional(
        self,
        event: StrokeEvent,
        position: int,
        complexity: float,
        lead: Player,
        rhythm: Player,
        accent: Player
    ) -> Player:
        """
        Select which player plays this event using traditional rules
        
        Rules:
        - High complexity patterns → Lead player
        - Steady pulse (on-beat) → Rhythm player
        - Syncopation/accents → Accent player
        - High intensity → Lead or Accent
        - Low intensity → Rhythm
        """
        
        # Check if it's a main beat (steady pulse)
        is_downbeat = position % 4 == 0  # Simple grid detection
        
        # High intensity events
        if event.intensity > 0.8:
            # Heavy accents go to accent player
            if event.stroke_type in ["Dheem", "Dha"]:
                return accent
            # Otherwise lead takes it
            return lead
        
        # Steady rhythm maintenance
        if is_downbeat and event.intensity < 0.6:
            return rhythm
        
        # Complex syncopated patterns
        if complexity > 0.7:
            return lead
        
        # Default: rotate between players for variety
        player_cycle = [lead, rhythm, accent]
        return player_cycle[position % 3]
    
    def _orchestrate_dynamic(self, events: List[StrokeEvent]) -> OrchestrationPattern:
        """
        Dynamic orchestration: AI analyzes pattern and distributes intelligently
        """
        pattern = OrchestrationPattern()
        
        chenda_players = self.ensemble.get_chenda_players()
        for player in chenda_players:
            pattern.chenda_events[player.id] = []
        
        cymbals = self.ensemble.get_cymbal_players()
        for cymbal in cymbals:
            pattern.cymbal_events[cymbal.id] = []
        
        # Analyze density and distribute
        density = self._calculate_density(events)
        
        for i, event in enumerate(events):
            if event.sound_category == "REST":
                continue
            
            # Select based on current load and player characteristics
            player = self._select_player_by_load(event, chenda_players, pattern)
            assigned_event = self._assign_event_to_player(event, player)
            pattern.chenda_events[player.id].append(assigned_event)
            
            # Cymbals
            if i % 8 == 0:  # Every 8th beat
                self._add_cymbal_events(event.time, cymbals, pattern)
        
        return pattern
    
    def _orchestrate_antiphonal(self, events: List[StrokeEvent]) -> OrchestrationPattern:
        """
        Call and response orchestration
        Alternate between lead and rhythm/accent
        """
        pattern = OrchestrationPattern()
        
        lead = self.ensemble.get_players_by_role(PlayerRole.CHENDA_LEAD)[0]
        rhythm = self.ensemble.get_players_by_role(PlayerRole.CHENDA_RHYTHM)[0]
        accent = self.ensemble.get_players_by_role(PlayerRole.CHENDA_ACCENT)[0]
        
        pattern.chenda_events[lead.id] = []
        pattern.chenda_events[rhythm.id] = []
        pattern.chenda_events[accent.id] = []
        
        cymbals = self.ensemble.get_cymbal_players()
        for cymbal in cymbals:
            pattern.cymbal_events[cymbal.id] = []
        
        # Split into phrases and alternate
        phrase_length = 4
        
        for i, event in enumerate(events):
            if event.sound_category == "REST":
                continue
            
            phrase_num = i // phrase_length
            
            if phrase_num % 2 == 0:
                # Lead plays
                player = lead
            else:
                # Response: rhythm and accent play together
                player = rhythm if i % 2 == 0 else accent
            
            assigned_event = self._assign_event_to_player(event, player)
            pattern.chenda_events[player.id].append(assigned_event)
        
        return pattern
    
    def _orchestrate_unison(self, events: List[StrokeEvent]) -> OrchestrationPattern:
        """
        All chenda players play in unison (with slight timing variations)
        """
        pattern = OrchestrationPattern()
        
        chenda_players = self.ensemble.get_chenda_players()
        for player in chenda_players:
            pattern.chenda_events[player.id] = []
        
        cymbals = self.ensemble.get_cymbal_players()
        for cymbal in cymbals:
            pattern.cymbal_events[cymbal.id] = []
        
        for i, event in enumerate(events):
            if event.sound_category == "REST":
                continue
            
            # All chendas play the same event
            for player in chenda_players:
                assigned_event = self._assign_event_to_player(event, player)
                pattern.chenda_events[player.id].append(assigned_event)
            
            # Cymbals on structural beats
            if self._is_structural_beat(i, len(events)):
                self._add_cymbal_events(event.time, cymbals, pattern)
        
        return pattern
    
    def _orchestrate_layered(self, events: List[StrokeEvent]) -> OrchestrationPattern:
        """
        Staggered entry: Players enter one by one
        """
        pattern = OrchestrationPattern()
        
        chenda_players = self.ensemble.get_chenda_players()
        for player in chenda_players:
            pattern.chenda_events[player.id] = []
        
        cymbals = self.ensemble.get_cymbal_players()
        for cymbal in cymbals:
            pattern.cymbal_events[cymbal.id] = []
        
        # Stagger entry
        entry_points = [0, len(events) // 4, len(events) // 2]
        
        for i, event in enumerate(events):
            if event.sound_category == "REST":
                continue
            
            # Determine which players have entered
            active_players = []
            for idx, entry in enumerate(entry_points):
                if i >= entry and idx < len(chenda_players):
                    active_players.append(chenda_players[idx])
            
            # All active players play
            for player in active_players:
                assigned_event = self._assign_event_to_player(event, player)
                pattern.chenda_events[player.id].append(assigned_event)
        
        return pattern
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    def _assign_event_to_player(self, event: StrokeEvent, player: Player) -> StrokeEvent:
        """
        Assign an event to a specific player
        Calculates velocity, timing offset, contact point based on player characteristics
        """
        # Calculate velocity based on player's dynamic range
        velocity = player.get_velocity_for_intensity(event.intensity)
        
        # Calculate timing offset
        timing_offset = player.timing.get_timing_offset(event.time)
        adjusted_time = event.time + timing_offset
        
        # Contact point variation (center hits for loud, edge for soft)
        if event.intensity > 0.7:
            contact_point = np.random.uniform(0.6, 0.9)  # Center hits
        else:
            contact_point = np.random.uniform(0.3, 0.6)  # Mid/edge hits
        
        # Create new event with player-specific parameters
        assigned = StrokeEvent(
            time=adjusted_time,
            stroke_type=event.stroke_type,
            sound_category=event.sound_category,
            intensity=event.intensity,
            duration=event.duration,
            assigned_player=player.id,
            velocity=velocity,
            contact_point=contact_point
        )
        
        return assigned
    
    def _add_cymbal_events(
        self,
        time: float,
        cymbals: List[Player],
        pattern: OrchestrationPattern
    ):
        """Add cymbal hits at specified time"""
        for cymbal in cymbals:
            cymbal_event = StrokeEvent(
                time=time + cymbal.timing.get_timing_offset(time),
                stroke_type="1",
                sound_category="NAM",  # Use NAM for metal
                intensity=0.6,
                duration=0.5,
                assigned_player=cymbal.id,
                velocity=cymbal.get_velocity_for_intensity(0.6),
                contact_point=0.5
            )
            pattern.cymbal_events[cymbal.id].append(cymbal_event)
    
    def _analyze_pattern_complexity(self, events: List[StrokeEvent]) -> float:
        """
        Analyze pattern complexity
        Returns 0.0-1.0 where 1.0 = most complex
        """
        if not events:
            return 0.0
        
        # Factors:
        # - High event density
        # - Wide dynamic range
        # - Syncopation (off-beat accents)
        
        # Event density
        non_rest = [e for e in events if e.sound_category != "REST"]
        density = len(non_rest) / len(events)
        
        # Dynamic range
        intensities = [e.intensity for e in non_rest]
        if intensities:
            dynamic_range = max(intensities) - min(intensities)
        else:
            dynamic_range = 0.0
        
        # Combine factors
        complexity = (density * 0.5 + dynamic_range * 0.5)
        
        return np.clip(complexity, 0.0, 1.0)
    
    def _calculate_density(self, events: List[StrokeEvent]) -> float:
        """Calculate event density (events per second)"""
        if not events or len(events) < 2:
            return 0.0
        
        non_rest = [e for e in events if e.sound_category != "REST"]
        if not non_rest:
            return 0.0
        
        duration = non_rest[-1].time - non_rest[0].time
        if duration == 0:
            return 0.0
        
        return len(non_rest) / duration
    
    def _is_structural_beat(self, position: int, total_length: int) -> bool:
        """Determine if this is a structural beat (downbeat, etc.)"""
        # Downbeats: every 4th, 8th, 16th
        return position % 4 == 0
    
    def _select_player_by_load(
        self,
        event: StrokeEvent,
        players: List[Player],
        pattern: OrchestrationPattern
    ) -> Player:
        """
        Select player based on current load balancing
        """
        # Count events per player
        loads = {}
        for player in players:
            loads[player.id] = len(pattern.chenda_events.get(player.id, []))
        
        # Select player with least load
        min_load_id = min(loads, key=loads.get)
        return self.ensemble.get_player(min_load_id)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_stroke_events_from_pattern(
    pattern: List[str],
    bpm: float,
    intensity_curve: Optional[List[float]] = None
) -> List[StrokeEvent]:
    """
    Create stroke events from a pattern list
    
    Args:
        pattern: List of stroke names (e.g., ["Ta", "Ka", "Na", "."])
        bpm: Beats per minute
        intensity_curve: Optional intensity for each stroke (0.0-1.0)
    
    Returns:
        List of StrokeEvents
    """
    events = []
    beat_duration = 60.0 / bpm
    
    for i, stroke in enumerate(pattern):
        time = i * beat_duration
        
        # Get sound category
        sound_cat = STROKE_LIBRARY.get(stroke, "REST")
        
        # Get intensity
        if intensity_curve and i < len(intensity_curve):
            intensity = intensity_curve[i]
        else:
            intensity = 0.7 if sound_cat != "REST" else 0.0
        
        event = StrokeEvent(
            time=time,
            stroke_type=stroke,
            sound_category=sound_cat,
            intensity=intensity,
            duration=beat_duration * 0.8  # Slight separation
        )
        
        events.append(event)
    
    return events


if __name__ == "__main__":
    from player_system import Ensemble
    from traditional_patterns import PANCHARI_PATTERNS
    
    print("🎵 ChendAI Orchestration Engine")
    print("=" * 70)
    
    # Create ensemble
    ensemble = Ensemble().build_standard_melam()
    
    # Create orchestration engine
    engine = OrchestrationEngine(ensemble)
    
    # Test with a simple pattern
    test_pattern = ["Ta", "Ka", "Na", "Ta", "Ka", "Na", "Ta", ".", "Dheem", ".", "Ta", "Ka"]
    test_bpm = 120
    
    print(f"\n📝 Test Pattern: {test_pattern}")
    print(f"   BPM: {test_bpm}")
    
    # Create events
    events = create_stroke_events_from_pattern(test_pattern, test_bpm)
    
    print(f"\n🎼 Testing Different Orchestration Strategies:\n")
    
    # Test TRADITIONAL
    print("1. TRADITIONAL Strategy:")
    trad_pattern = engine.orchestrate_sequence(events, OrchestrationStrategy.TRADITIONAL)
    for player_id, player_events in trad_pattern.chenda_events.items():
        if player_events:
            player = ensemble.get_player(player_id)
            print(f"   {player.name}: {len(player_events)} events")
    
    # Test UNISON
    print("\n2. UNISON Strategy:")
    unison_pattern = engine.orchestrate_sequence(events, OrchestrationStrategy.UNISON)
    for player_id, player_events in unison_pattern.chenda_events.items():
        if player_events:
            player = ensemble.get_player(player_id)
            print(f"   {player.name}: {len(player_events)} events")
    
    # Test ANTIPHONAL
    print("\n3. ANTIPHONAL Strategy:")
    anti_pattern = engine.orchestrate_sequence(events, OrchestrationStrategy.ANTIPHONAL)
    for player_id, player_events in anti_pattern.chenda_events.items():
        if player_events:
            player = ensemble.get_player(player_id)
            print(f"   {player.name}: {len(player_events)} events")
    
    print("\n✅ Orchestration Engine Ready!")
