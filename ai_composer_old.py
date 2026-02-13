"""
ChendAI AI Composer
Uses OpenAI to intelligently compose beat sequences based on user prompts.
"""

import json
from typing import Dict, List, Any
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AIComposer:
    """AI-powered beat composer using OpenAI"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.available_sounds = self._load_available_sounds()
    
    def _load_available_sounds(self) -> Dict[str, List[str]]:
        """Load available sound IDs from DNA files"""
        from dna_parser import DNAParser
        
        parser = DNAParser()
        parser.parse_chenda_dna()
        parser.parse_illathaalam_dna()
        parser.parse_side_instruments_dna()
        
        return {
            'chenda': parser.list_available_sounds('chenda'),
            'illathaalam': parser.list_available_sounds('illathaalam'),
            'side_instruments': parser.list_available_sounds('side_instrument')
        }
    
    def compose_beat_sequence(self, user_prompt: str, duration: int = 30) -> Dict[str, Any]:
        """
        Use OpenAI to compose a beat sequence based on user prompt
        
        Args:
            user_prompt: User's request (e.g., "generate a kalyanam beat")
            duration: Duration in seconds
        
        Returns:
            Dict containing beat sequence with timing information
        """
        # Create system prompt with Kerala percussion knowledge
        system_prompt = f"""You are an expert in traditional Kerala percussion music (Chenda Melam, Panchavadyam).
You compose authentic beat sequences for the following instruments:

**CHENDA SOUNDS AVAILABLE:**
{', '.join(self.available_sounds['chenda'])}

**ILLATHAALAM SOUNDS AVAILABLE:**
{', '.join(self.available_sounds['illathaalam'])}

**SIDE INSTRUMENTS AVAILABLE:**
{', '.join(self.available_sounds['side_instruments'])}

**BEAT STYLES:**
- **Kalyanam (Wedding)**: Celebratory, medium-fast tempo (120-140 BPM), uses THAAM_MAIN, ILA_OPEN, KOMBU
- **Kathakali**: Slower, dramatic (80-100 BPM), uses varied dynamics, CHAPU, NAKKU for subtlety
- **Panchavadyam**: Complex, building intensity (100-180 BPM), all instruments, URUTTU rolls
- **Thayambaka**: Solo chenda showcase, intricate rhythms, fast URUTTU sequences

**COMPOSITION RULES:**
1. Start with a basic rhythm pattern that repeats
2. The chenda provides the main rhythm (THAAM = main beat, OPPU = muted, NAM = rim)
3. Illathaalam accents on important beats (ILA_OPEN for ring, ILA_CLOSE for "chk")
4. Use velocity variations (0.5-1.0) for dynamics
5. Create musical phrases that repeat and build

Generate a beat sequence in JSON format with exact timing for each note.
"""
        
        user_message = f"""Create a {duration}-second beat sequence for: {user_prompt}

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "style": "style_name",
  "bpm": 120,
  "duration": {duration},
  "tracks": {{
    "chenda": [
      {{"time": 0.0, "sound": "THAAM_MAIN_HARD", "velocity": 1.0}},
      {{"time": 0.5, "sound": "OPPU_HARD", "velocity": 0.8}}
    ],
    "illathaalam": [
      {{"time": 0.0, "sound": "ILA_OPEN_LOUD", "velocity": 1.0}}
    ]
  }}
}}

Include at least 20-100 note events depending on the style and tempo."""
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            # Extract and parse response
            content = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            beat_sequence = json.loads(content)
            
            # Validate the structure
            if not self._validate_beat_sequence(beat_sequence):
                raise ValueError("Invalid beat sequence structure from AI")
            
            return beat_sequence
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {e}")
            print(f"Response was: {content}")
            # Return a simple fallback pattern
            return self._create_fallback_pattern(duration)
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return self._create_fallback_pattern(duration)
    
    def _validate_beat_sequence(self, sequence: Dict[str, Any]) -> bool:
        """Validate that the beat sequence has the correct structure"""
        required_keys = ['style', 'bpm', 'duration', 'tracks']
        
        if not all(key in sequence for key in required_keys):
            return False
        
        if not isinstance(sequence['tracks'], dict):
            return False
        
        # Check that each track has valid note events
        for track_name, events in sequence['tracks'].items():
            if not isinstance(events, list):
                return False
            
            for event in events:
                if not all(key in event for key in ['time', 'sound', 'velocity']):
                    return False
        
        return True
    
    def _create_fallback_pattern(self, duration: int) -> Dict[str, Any]:
        """Create a simple fallback pattern if AI fails"""
        beat_interval = 0.5  # 120 BPM
        num_beats = int(duration / beat_interval)
        
        chenda_events = []
        illathaalam_events = []
        
        for i in range(num_beats):
            time = i * beat_interval
            
            # Simple alternating pattern
            if i % 4 == 0:
                chenda_events.append({"time": time, "sound": "THAAM_MAIN_HARD", "velocity": 1.0})
                illathaalam_events.append({"time": time, "sound": "ILA_OPEN_LOUD", "velocity": 1.0})
            elif i % 2 == 0:
                chenda_events.append({"time": time, "sound": "OPPU_HARD", "velocity": 0.8})
            else:
                chenda_events.append({"time": time, "sound": "NAM_MED", "velocity": 0.7})
        
        return {
            "style": "basic_pattern",
            "bpm": 120,
            "duration": duration,
            "tracks": {
                "chenda": chenda_events,
                "illathaalam": illathaalam_events
            }
        }


if __name__ == '__main__':
    # Test the AI composer
    composer = AIComposer()
    
    print("Testing AI Composer...")
    print("Composing a kalyanam beat...\n")
    
    sequence = composer.compose_beat_sequence("generate a kalyanam wedding beat", duration=10)
    
    print(f"Style: {sequence['style']}")
    print(f"BPM: {sequence['bpm']}")
    print(f"Duration: {sequence['duration']}s")
    print(f"\nTracks:")
    
    for track_name, events in sequence['tracks'].items():
        print(f"  {track_name}: {len(events)} events")
        if events:
            print(f"    First event: {events[0]}")
