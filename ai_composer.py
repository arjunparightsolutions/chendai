"""
ChendAI AI Composer - ULTRA-DENSE AUTHENTIC VERSION
Maximum beat density with continuous subdivisions
"""

import json
import random
from typing import Dict, List, Any, Tuple
from openai import OpenAI
import os
from dotenv import load_dotenv
from traditional_patterns import (
    PANCHARI_PATTERNS, PANDI_PATTERNS, THAYAMBAKA_PATTERNS,
    PANCHAVADYAM_PATTERNS, MANGALAM_PATTERN, STROKE_LIBRARY
)

# Load environment variables
load_dotenv()

class AIComposer:
    """AI-powered beat composer - ULTRA DENSE like real traditional chenda"""
    
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
    
    def compose_beat_sequence(self, user_prompt: str, duration: int = 30, log_callback: callable = None) -> Dict[str, Any]:
        """Compose authentic beat using traditional patterns, modulated by AI interpretation of prompt"""
        
        # 1. ANALYZE PROMPT (Rule-based + LLM Enhancement)
        if log_callback: log_callback(f"🔍 Analyzing user prompt: '{user_prompt}'")
        ai_params = self._analyze_prompt_with_ai(user_prompt, log_callback)
        
        if log_callback: log_callback(f"🤖 AI Interpretation: style={ai_params.get('style')}, intensity={ai_params.get('intensity_multiplier')}")
        
        base_style = ai_params.get('style', 'panchari')
        tempo_mult = ai_params.get('tempo_multiplier') or 1.0
        intensity_mult = ai_params.get('intensity_multiplier') or 1.0
        
        # 2. SELECT GENERATOR
        if "panchari" in base_style:
            return self._compose_panchari_ultra_dense(duration, tempo_mult, intensity_mult)
        elif "pandi" in base_style:
            return self._compose_pandi(duration, tempo_mult, intensity_mult)
        elif "thayambaka" in base_style:
            return self._compose_thayambaka(duration, tempo_mult, intensity_mult)
        elif "panchavadyam" in base_style:
            return self._compose_panchavadyam(duration)
        elif "mangalam" in base_style:
            return self._compose_mangalam(duration)
        else:
            return self._compose_panchari_ultra_dense(duration, tempo_mult, intensity_mult)

    def _analyze_prompt_rules(self, prompt: str) -> Dict[str, Any]:
        """Deterministic Keyword-based Scenario Interpreter (The Neuro-Rhythmic Driver)"""
        p = prompt.lower()
        params = {'style': 'panchari', 'tempo_multiplier': 1.0, 'intensity_multiplier': 1.0}
        
        # Style Mappings
        if any(w in p for w in ['pandi', 'pooram', 'festival', 'climax', 'fireworks', 'chaos']):
            params['style'] = 'pandi'
        elif any(w in p for w in ['thayambaka', 'solo', 'improvisation', 'freestyle', 'concert']):
            params['style'] = 'thayambaka'
        elif any(w in p for w in ['panchavadyam', 'conch', 'thimila', 'sculptural']):
            params['style'] = 'panchavadyam'
        elif any(w in p for w in ['mangalam', 'ending', 'prayer', 'worship']):
            params['style'] = 'mangalam'
        elif any(w in p for w in ['chempada', 'rustic', 'folk', 'boat']):
            params['style'] = 'panchari' # Map closest for now
        
        # Tempo Modifiers
        if any(w in p for w in ['fast', 'speed', 'rapid', 'frenetic', 'wild', 'run']):
            params['tempo_multiplier'] = 1.3
        elif any(w in p for w in ['slow', 'calm', 'procession', 'elephant', 'royal', 'majestic']):
            params['tempo_multiplier'] = 0.8
        elif any(w in p for w in ['medium', 'walking', 'steady']):
            params['tempo_multiplier'] = 1.0
            
        # Intensity Modifiers
        if any(w in p for w in ['loud', 'heavy', 'thunder', 'explosive', 'war']):
            params['intensity_multiplier'] = 1.2
        elif any(w in p for w in ['soft', 'quiet', 'subtle', 'distant', 'night']):
            params['intensity_multiplier'] = 0.8
            
        return params

    def _analyze_prompt_with_ai(self, prompt: str, log_callback: callable = None) -> Dict[str, Any]:
        """Professional LLM Analysis for Authentic Chendamelam"""
        if log_callback: log_callback("🧠 Consulting ChendAI Master Model for musical structure...")
        
        system_prompt = """
        You are 'ChendAI Master', a professional Kerala Chenda Melam expert. 
        Your task is to translate a user's musical request into technical parameters for a traditional ensemble.
        
        Styles: 
        - 'panchari': 6-beat temple melam, slow to fast (levels 1-5).
        - 'pandi': 7-beat powerful outdoor melam, high energy.
        - 'thayambaka': Solo improvisational chenda with rhythmic complexity.
        - 'panchavadyam': 5-instrument ensemble (thimila, maddalam, elathalam, kombu, edakka).
        
        Output MUST be JSON:
        {
          "style": "panchari" | "pandi" | "thayambaka" | "panchavadyam",
          "tempo_multiplier": 0.5 - 2.0,
          "intensity_multiplier": 0.5 - 1.5,
          "complexity": "low" | "medium" | "high" | "insane",
          "stages": ["list of stages based on style"],
          "reasoning": "Brief explanation of musical choices"
        }
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini", # Using a fast but smart model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            result = json.loads(response.choices[0].message.content)
            if log_callback: log_callback(f"📝 Master Plan: {result.get('reasoning')}")
            return result
        except Exception as e:
            if log_callback: log_callback(f"⚠️ LLM Error (using fallback rules): {str(e)}")
            return self._analyze_prompt_rules(prompt)
    
    def _compose_panchari_ultra_dense(self, duration: int, tempo_mult: float = 1.0, intensity_mult: float = 1.0) -> Dict[str, Any]:
        """Compose Panchari with COMPLETE TRADITIONAL ENSEMBLE"""
        chenda_events = []
        illathaalam_events = []
        kombu_events = []
        kuzhal_events = []
        edakka_events = []
        thimila_events = []  # Panchavadyam lead
        maddalam_events = []  # Barrel drum
        thavil_events = []  # Powerful outdoor drum
        nadaswaram_events = []  # Large double reed
        kurumkuzhal_events = []  # Sweet flute
        current_time = 0.0
        
        stages = ["pathikaalam", "randam_kaalam", "moonam_kaalam", "naalam_kaalam", "anchaam_kaalam"]
        stage_duration = duration / len(stages)
        
        # Melodic notes (Sa, Ri, Ga, Ma, Pa, Dha, Ni)
        melodic_cycle = ["SA", "RI", "GA", "PA", "DHA", "NI", "SA"]
        
        for stage_idx, stage_name in enumerate(stages):
            stage = PANCHARI_PATTERNS[stage_name]
            bpm = stage["base_bpm"] * tempo_mult
            beat_duration = 60.0 / bpm
            pattern = stage["pattern"]
            
            beats_in_stage = int(stage_duration / beat_duration)
            pattern_length = len(pattern)
            stage_intensity = ((stage_idx + 1) / len(stages)) * intensity_mult
            
            for beat_idx in range(beats_in_stage):
                pattern_pos = beat_idx % pattern_length
                stroke = pattern[pattern_pos]
                
                # CHENDA - ULTRA DENSE
                if stroke != ".":
                    sound_id = self._get_stroke_sound(stroke)
                    
                    # PHASE 5 OVERRIDE (User Request)
                    if stage_name == "anchaam_kaalam":
                         if "Trill" in sound_id or "Roll" in sound_id or "Ta" in stroke or "ka" in stroke:
                             sound_id = "CHENDA_URUTTU_ROLL_HI" if beat_idx % 2 == 0 else "CHENDA_URUTTU_ROLL_LO"
                         elif "Tha" in stroke:
                             sound_id = "CHENDA_THAAM_SHARP" 
                         elif "Chapu" in stroke:
                             sound_id = "CHENDA_CHAPU_SNAP"

                    velocity = self._calculate_velocity(beat_idx, beats_in_stage, stage_name)
                    
                    chenda_events.append({"time": current_time, "sound": sound_id, "velocity": velocity})
                    
                    # SUBDIVISIONS
                    num_subdivisions = 2 if stage_intensity < 0.4 else 3 if stage_intensity < 0.7 else 4
                    subdivision_interval = beat_duration / (num_subdivisions + 1)
                    
                    for sub_idx in range(1, num_subdivisions + 1):
                        sub_time = current_time + (subdivision_interval * sub_idx)
                        sub_stroke = "ka" if sub_idx % 2 == 0 else "ta"
                        sub_sound = self._get_stroke_sound(sub_stroke)
                        sub_velocity = velocity * (0.4 + (sub_idx * 0.08))
                        chenda_events.append({"time": sub_time, "sound": sub_sound, "velocity": sub_velocity})
                    
                    # TRIPLE HITS
                    if stage.get("triple_hits"):
                        micro_delay = beat_duration / 9
                        for triple_idx in range(1, 3):
                            chenda_events.append({"time": current_time + (micro_delay * triple_idx), "sound": sound_id, "velocity": velocity * (1.0 - triple_idx * 0.15)})
                    
                    # FILLS
                    if beat_idx % 3 == 2:
                        fill_time = current_time + beat_duration * 0.55
                        chenda_events.append({"time": fill_time, "sound": self._get_stroke_sound("TaTa"), "velocity": velocity * 0.68})
                        if stage_intensity > 0.6:
                            chenda_events.append({"time": fill_time + beat_duration * 0.12, "sound": self._get_stroke_sound("KaKa"), "velocity": velocity * 0.58})
                    
                    # MICRO-FILLS
                    if stage_intensity > 0.5:
                        micro_fill_time = current_time + beat_duration * 0.33
                        chenda_events.append({"time": micro_fill_time, "sound": self._get_stroke_sound("ka"), "velocity": velocity * 0.38})
                        if stage_intensity > 0.7:
                            chenda_events.append({"time": micro_fill_time + beat_duration * 0.14, "sound": self._get_stroke_sound("ta"), "velocity": velocity * 0.32})
                
                # ILLATHAALAM
                ila_pattern = stage.get("illathaalam", "")
                if pattern_pos < len(ila_pattern) and ila_pattern[pattern_pos] == "1":
                    # PHASE 5 OVERRIDE
                    if stage_name == "anchaam_kaalam":
                        illathaalam_events.append({"time": current_time, "sound": "ILATHALAM_OPEN_SIZZLE", "velocity": 0.9})
                        illathaalam_events.append({"time": current_time + beat_duration * 0.5, "sound": "ILATHALAM_CLOSE_MUTE", "velocity": 0.85})
                    else:
                        illathaalam_events.append({"time": current_time, "sound": "ILA_OPEN_LOUD" if velocity > 0.7 else "ILA_OPEN_MED", "velocity": velocity})
                        for i in range(1, 4):
                            illathaalam_events.append({"time": current_time + beat_duration * (0.18 * i), "sound": "ILA_CLOSE_FAST", "velocity": velocity * (0.58 - i * 0.08)})
                
                # KOMBU - Traditional horn
                if beat_idx % (pattern_length // 2) == 0 and stage_intensity > 0.4:
                    if stage_name == "anchaam_kaalam":
                         # Sa-Pa-Sa rhythmic stab
                         kombu_events.append({"time": current_time, "sound": "KOMBU_SA_LOW", "velocity": 0.95, "duration": beat_duration})
                         kombu_events.append({"time": current_time + beat_duration, "sound": "KOMBU_PA_MID", "velocity": 0.95, "duration": beat_duration})
                         kombu_events.append({"time": current_time + beat_duration * 2, "sound": "KOMBU_SA_HIGH", "velocity": 1.0, "duration": beat_duration * 2})
                    else:
                        kombu_events.append({"time": current_time, "sound": "KOMBU_MID_BLAST", "velocity": 0.72 + (stage_intensity * 0.28), "duration": beat_duration * 4})
                
                # KUZHAL - Double reed with MELODY
                if beat_idx % 2 == 0:
                    note_pos = (beat_idx // 2) % len(melodic_cycle)
                    note_name = melodic_cycle[note_pos]
                    
                    if stage_intensity < 0.5:
                        kuzhal_note = f"KUZHAL_{note_name}_LOW"
                    elif stage_intensity < 0.8:
                        kuzhal_note = f"KUZHAL_{note_name}_MID" if note_name in ["MA", "PA", "DHA", "NI"] else f"KUZHAL_{note_name}_LOW"
                    else:
                        kuzhal_note = f"KUZHAL_{note_name}_HIGH" if note_name in ["SA", "RI"] else f"KUZHAL_{note_name}_MID"
                    
                    if stage_name == "anchaam_kaalam":
                         kuzhal_note = "KUZHAL_NAASAL_TONE_2" if beat_idx % 4 == 0 else "KUZHAL_NAASAL_TONE_1"
                    
                    kuzhal_events.append({"time": current_time, "sound": kuzhal_note, "velocity": 0.52 + (stage_intensity * 0.28), "duration": beat_duration * 2})
                
                # NADASWARAM - Powerful reed (melodic in climax)
                if beat_idx % 4 == 0 and stage_intensity > 0.5:
                    note_pos = (beat_idx // 4) % len(melodic_cycle)
                    note_name = melodic_cycle[note_pos]
                    
                    if stage_intensity < 0.7:
                        nadaswaram_note = f"NADASWARAM_{note_name}_LOW"
                    else:
                        nadaswaram_note = f"NADASWARAM_{note_name}_MID" if note_name in ["PA"] else f"NADASWARAM_SA_HIGH"
                    
                    nadaswaram_events.append({"time": current_time, "sound": nadaswaram_note, "velocity": 0.7 + (stage_intensity * 0.3), "duration": beat_duration * 5})
                
                # KURUMKUZHAL - Sweet flute (melodic fills)
                if beat_idx % 3 == 0 and stage_intensity > 0.3:
                    note_pos = (beat_idx // 3) % len(melodic_cycle)
                    note_name = melodic_cycle[note_pos]
                    kurumkuzhal_note = f"KURUMKUZHAL_{note_name}_LOW" if note_name in ["SA", "RI", "GA"] else f"KURUMKUZHAL_{note_name[0:2]}"
                    kurumkuzhal_events.append({"time": current_time, "sound": kurumkuzhal_note, "velocity": 0.45 + (stage_intensity * 0.25), "duration": beat_duration * 2.5})
                
                # THIMILA - Panchavadyam lead (rhythmic patterns)
                if stage_intensity > 0.4 and beat_idx % 2 == 0:
                    thimila_sound = "THIMILA_TA_HIGH" if beat_idx % 4 == 0 else "THIMILA_KA_MID"
                    if stage_intensity > 0.7:
                        thimila_sound = "THIMILA_TA_VHIGH"
                    thimila_events.append({"time": current_time, "sound": thimila_sound, "velocity": 0.65 + (stage_intensity * 0.35), "duration": beat_duration * 0.8})
                
                # MADDALAM - Barrel drum (deep foundation)
                if beat_idx % 4 == 0:
                    maddalam_sound = "MADDALAM_THOM_DEEP" if beat_idx % 8 == 0 else "MADDALAM_THA_MID"
                    if stage_intensity > 0.8:
                        maddalam_sound = "MADDALAM_THOM_VDEEP"
                    
                    if stage_name == "anchaam_kaalam":
                        maddalam_sound = "CHENDA_DHEEM_THUD" if beat_idx % 2 == 0 else "CHENDA_DHEEM_RESO"

                    maddalam_events.append({"time": current_time, "sound": maddalam_sound, "velocity": 0.55 + (stage_intensity * 0.3), "duration": beat_duration * 2})
                
                # THAVIL - Powerful outdoor drum (with nadaswaram)
                if beat_idx % 5 == 0 and stage_intensity> 0.6:
                    thavil_sound = "THAVIL_NAM_SHARP" if beat_idx % 10 == 0 else "THAVIL_TA_MID"
                    thavil_events.append({"time": current_time, "sound": thavil_sound, "velocity": 0.70 + (stage_intensity * 0.3), "duration": beat_duration * 1.2})
                
                # EDAKKA - Soft pulse
                edakka_freq = 6 if stage_intensity < 0.6 else 3
                if beat_idx % edakka_freq == 0:
                    edakka_events.append({"time": current_time, "sound": "VEEKU_THUD_MID" if beat_idx % 10 == 0 else "VEEKU_THUD_LOW", "velocity": 0.42 + (stage_intensity * 0.18), "duration": beat_duration * 1.4})
                
                current_time += beat_duration
            
            # CLIMAX additions
            if stage.get("add_uruttu") and stage_name == "anchaam_kaalam":
                chenda_events = self._add_fast_rolls(chenda_events, current_time - stage_duration, stage_duration, bpm)
                for i in range(6):
                    scream_time = current_time - stage_duration + (stage_duration / 6) * i
                    kombu_events.append({"time": scream_time, "sound": "KOMBU_HI_SCREAM", "velocity": 0.92, "duration": beat_duration * 2.8})
                    nadaswaram_events.append({"time": scream_time + 0.1, "sound": "NADASWARAM_BLAST", "velocity": 0.95, "duration": beat_duration * 3})
                    thavil_events.append({"time": scream_time + 0.05, "sound": "THAVIL_ROLL_FAST", "velocity": 0.88, "duration": beat_duration * 2.5})
            
            # PHASE 6: MURI-PANCHARI (Ending)
            if stage_name == "anchaam_kaalam":
                cut_time = current_time + 0.2
                # 3 hard hits
                for k in range(3):
                    hit_time = cut_time + (0.4 * k)
                    chenda_events.append({"time": hit_time, "sound": "FINAL_CUT_UNISON_HIT", "velocity": 1.0})
                    kombu_events.append({"time": hit_time, "sound": "KOMBU_BLAST_DISTORT", "velocity": 1.0, "duration": 0.3})
                    illathaalam_events.append({"time": hit_time, "sound": "ILATHALAM_OPEN_SIZZLE", "velocity": 1.0})
        
        return {
            "style": "Panchari Melam - COMPLETE TRADITIONAL ENSEMBLE (10 instruments!)",
            "bpm": "70-380 (progressive)",
            "tala": "6-beat Panchari",
            "duration": duration,
            "stages": 5,
            "instruments": ["Chenda", "Illathaalam", "Kombu", "Kuzhal", "Edakka", "Thimila", "Maddalam", "Thavil", "Nadaswaram", "Kurumkuzhal"],
            "tracks": {
                "chenda": chenda_events,
                "illathaalam": illathaalam_events,
                "kombu": kombu_events,
                "kuzhal": kuzhal_events,
                "edakka": edakka_events,
                "thimila": thimila_events,
                "maddalam": maddalam_events,
                "thavil": thavil_events,
                "nadaswaram": nadaswaram_events,
                "kurumkuzhal": kurumkuzhal_events
            }
        }
    
    def _get_stroke_sound(self, stroke: str) -> str:
        """Get sound ID for stroke"""
        if stroke in STROKE_LIBRARY:
            sound_options = STROKE_LIBRARY[stroke]
            if isinstance(sound_options, list):
                return random.choice(sound_options)
            return sound_options
        return "THAAM_480HZ_HARD"
    
    def _calculate_velocity(self, beat_idx: int, total_beats: int, stage: str) -> float:
        """Calculate velocity with crescendo"""
        base_velocity = 0.62
        progress = beat_idx / max(total_beats, 1)
        
        if "anchaam" in stage or "naalam" in stage:
            base_velocity = 0.87
        
        crescendo = progress * 0.28
        variation = random.uniform(-0.04, 0.04)
        
        return min(1.0, base_velocity + crescendo + variation)
    
    def _add_fast_rolls(self, events: List[Dict], start_time: float, duration: float, base_bpm: int) -> List[Dict]:
        """Add rapid URUTTU rolls"""
        roll_beat_duration = 60.0 / (base_bpm * 5)  # 5x faster!
        num_rolls = int(duration / roll_beat_duration * 0.4)
        
        for i in range(num_rolls):
            roll_time = start_time + random.uniform(0, duration)
            events.append({"time": roll_time, "sound": self._get_stroke_sound("TaTa"), "velocity": 0.82})
            events.append({"time": roll_time + roll_beat_duration, "sound": self._get_stroke_sound("KaKa"), "velocity": 0.77})
        
        events.sort(key=lambda x: x['time'])
        return events
    def _compose_pandi(self, duration: int, tempo_mult: float = 1.0, intensity_mult: float = 1.0) -> Dict[str, Any]:
        """Pandi Melam - The Festival Rhythm (7 beats: 3+2+2)"""
        # Pandi pattern: [Dhin, ., Tha, ., Ka, Tha, Dhim] roughly
        events = {inst: [] for inst in ['chenda', 'illathaalam', 'kombu', 'kuzhal', 'edakka', 'thimila', 'maddalam', 'thavil', 'nadaswaram', 'kurumkuzhal']}
        
        bpm = 120 * tempo_mult
        beat_dur = 60.0 / bpm
        cycle_len = 7
        
        total_cycles = int(duration / (beat_dur * cycle_len))
        current_time = 0.0
        
        for i in range(total_cycles):
            # Intensity ramps up
            prog = i / total_cycles
            cycle_intensity = intensity_mult * (0.6 + 0.4 * prog)
            
            # 7-beat basic cycle
            # Beat 1: Heavy
            events['chenda'].append({"time": current_time, "sound": "CHENDA_VALANTHALA_OPEN", "velocity": 1.0})
            events['illathaalam'].append({"time": current_time, "sound": "ILATHALAM_OPEN_LOUD", "velocity": 0.9})
            
            # Beat 3: Tha
            events['chenda'].append({"time": current_time + beat_dur * 2, "sound": self._get_stroke_sound("Tha"), "velocity": 0.8})
            
            # Beat 4: Ka (Sub)
            if cycle_intensity > 0.7:
                 events['chenda'].append({"time": current_time + beat_dur * 3.5, "sound": self._get_stroke_sound("Ka"), "velocity": 0.7})
            
            # Beat 5: Ka
            events['chenda'].append({"time": current_time + beat_dur * 4, "sound": self._get_stroke_sound("Ka"), "velocity": 0.85})
            
            # Beat 6: Tha
            events['chenda'].append({"time": current_time + beat_dur * 5, "sound": self._get_stroke_sound("Tha"), "velocity": 0.9})
            events['illathaalam'].append({"time": current_time + beat_dur * 5, "sound": "ILA_CLOSE_FAST", "velocity": 0.8})

            # Beat 7: Dhim (End of cycle kick)
            if i % 2 == 1:
                events['chenda'].append({"time": current_time + beat_dur * 6, "sound": "CHENDA_DHEEM_RESO", "velocity": 0.95})
            
            # Fills
            if i % 4 == 3:
                # Roll at end of 4th cycle
                self._add_fast_rolls(events['chenda'], current_time + beat_dur * 5, beat_dur * 2, bpm)
                
            current_time += beat_dur * cycle_len
            
        # Combine into result dict
        return {
            "style": "Pandi Melam (Festival)",
            "bpm": f"{int(bpm)} (Adjusted)",
            "tala": "7-beat Tripuda",
            "duration": duration,
            "stages": 1,
            "instruments": list(events.keys()),
            "tracks": events
        }

    def _compose_thayambaka(self, duration: int, tempo_mult: float = 1.0, intensity_mult: float = 1.0) -> Dict[str, Any]:
        """Thayambaka - Improvisational Solo"""
        # Chempada structure (8 beats) with free-form Idakka/Chenda interplay
        events = {inst: [] for inst in ['chenda', 'illathaalam', 'kombu', 'kuzhal', 'edakka', 'thimila', 'maddalam', 'thavil', 'nadaswaram', 'kurumkuzhal']}
        
        bpm = 90 * tempo_mult
        beat_dur = 60.0 / bpm
        current_time = 0.0
        
        while current_time < duration:
            # Improvisation Logic: switching between 'sarva-laghu' (flow) and 'theerumanam' (cadence)
            
            mode = random.choice(['flow', 'flow', 'cadence'])
            if current_time > duration * 0.8: mode = 'climax'
            if current_time + 4 > duration: mode = 'ending'
            
            if mode == 'flow':
                # 8 beats constant playing
                for b in range(8):
                    t = current_time + b * beat_dur
                    if b % 2 == 0:
                        events['chenda'].append({"time": t, "sound": self._get_stroke_sound("Na"), "velocity": 0.7 * intensity_mult})
                        events['edakka'].append({"time": t, "sound": "VEEKU_THUD_LOW", "velocity": 0.6})
                    else:
                        events['chenda'].append({"time": t, "sound": self._get_stroke_sound("Dhin"), "velocity": 0.6 * intensity_mult})
                    
                    if b == 0:
                        events['illathaalam'].append({"time": t, "sound": "ILATHALAM_OPEN_SIZZLE", "velocity": 0.8})
                        
                current_time += beat_dur * 8
                
            elif mode == 'cadence':
                # Fast triplet rolls
                self._add_fast_rolls(events['chenda'], current_time, beat_dur * 4, bpm)
                events['kombu'].append({"time": current_time, "sound": "KOMBU_MID_BLAST", "velocity": 0.9, "duration": beat_duration * 2})
                current_time += beat_dur * 4
                
            elif mode == 'climax':
                 # Dense hits
                 for b in range(16): # Double speed
                     t = current_time + b * (beat_dur / 2)
                     events['chenda'].append({"time": t, "sound": "CHENDA_URUTTU_ROLL_HI", "velocity": 0.9})
                     events['illathaalam'].append({"time": t, "sound": "ILA_CLOSE_FAST", "velocity": 0.85})
                 current_time += beat_dur * 8
                 
            elif mode == 'ending':
                events['chenda'].append({"time": current_time, "sound": "FINAL_CUT_UNISON_HIT", "velocity": 1.0})
                break
                
        return {
            "style": "Thayambaka (Solo Improv)",
            "bpm": f"{int(bpm)} (Variable)",
            "tala": "8-beat Chempada",
            "duration": duration,
            "stages": "Improvisation",
            "instruments": list(events.keys()),
            "tracks": events
        }

    def _compose_panchavadyam(self, duration: int) -> Dict[str, Any]:
        return self._compose_panchari_ultra_dense(duration, 1.1, 1.0)

    def _compose_mangalam(self, duration: int) -> Dict[str, Any]:
        return self._compose_panchari_ultra_dense(duration, 0.8, 0.8)
