from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict, Optional
import os
import uuid
import json
import shutil
import numpy as np
import soundfile as sf

from database_manager import DatabaseManager
from audio_processor import AudioProcessor

router = APIRouter(prefix="/api/daw", tags=["DAW"])
db = DatabaseManager()
processor = AudioProcessor()

# --- Models ---
class ProjectCreate(BaseModel):
    name: str
    bpm: int = 120

class TrackCreate(BaseModel):
    project_id: str
    name: str
    type: str = "audio"
    color: str = "#5b7fff"
    icon: str = "🥁"

class ClipCreate(BaseModel):
    track_id: str
    source_file: str
    start_time: float
    duration: float
    offset: float = 0.0

class EffectCreate(BaseModel):
    track_id: str
    type: str
    parameters: Dict

class RenderParams(BaseModel):
    project_id: str
    output_format: str = "wav"

@router.post("/clips")
async def add_clip(clip: ClipCreate):
    clip_id = str(uuid.uuid4())
    # Verify file exists (assuming source_file relative to uploads/ or full path)
    if not os.path.exists(clip.source_file):
        # Trying relative to uploads
        clip.source_file = os.path.join("uploads", clip.source_file)
        if not os.path.exists(clip.source_file):
            raise HTTPException(status_code=404, detail="Source file not found")
            
    db.add_clip(clip_id, clip.track_id, clip.source_file, clip.start_time, clip.duration, clip.offset)
    return {"id": clip_id}

@router.post("/tracks")
async def add_track(track: TrackCreate):
    track_id = str(uuid.uuid4())
    db.add_track(track_id, track.project_id, track.name, track.type, track.color, track.icon)
    return {"id": track_id, "name": track.name}

@router.post("/clips")
async def add_clip(clip: ClipCreate):
    clip_id = str(uuid.uuid4())
    # Verify file exists (assuming source_file relative to uploads/ or full path)
    if not os.path.exists(clip.source_file):
        # Trying relative to uploads
        clip.source_file = os.path.join("uploads", clip.source_file)
        if not os.path.exists(clip.source_file):
            raise HTTPException(status_code=404, detail="Source file not found")
            
    db.add_clip(clip_id, clip.track_id, clip.source_file, clip.start_time, clip.duration, clip.offset)
    return {"id": clip_id}

class SplitParams(BaseModel):
    clip_id: str
    split_time: float # Relative to clip start or project? Let's use Project Time for consistency in UI

class TrimParams(BaseModel):
    clip_id: str
    new_start_time: float
    new_duration: float
    new_offset: float

@router.post("/process/split")
async def split_clip(params: SplitParams):
    # 1. Get Clip
    # 2. Duplicate Clip Entry
    # 3. Update durations/offsets
    # This is a DB operation, audio file remains untouched (non-destructive)
    return {"message": "Split implemented (Logic placeholder)"} # Full implementation would need DB getters for clips

@router.post("/process/render")
async def render_project(params: RenderParams):
    """
    Multitrack Render Engine V2 (With Automation)
    1. Load Project State
    2. Iterate Tracks
    3. Render Clips + Effects
    4. Apply Automation (Volume/Pan)
    5. Mix down to Master
    """
    project = db.get_project_state(params.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate total duration
    max_time = 0
    for track in project['tracks']:
        for clip in track['clips']:
            end_time = clip['start_time'] + clip['duration']
            if end_time > max_time:
                max_time = end_time
                
    if max_time == 0:
        return {"error": "Empty project"}

    # Setup Master Buffer (Stereo)
    num_samples = int(max_time * 44100)
    master_mix = np.zeros((2, num_samples), dtype=np.float32)

    print(f"🎛️ Rendering Project: {project['name']} ({max_time}s) with Automation")

    for track in project['tracks']:
        if track['mute']: continue
        
        # Track Buffer
        track_signal = np.zeros((2, num_samples), dtype=np.float32)
        
        # 1. Place Clips
        for clip in track['clips']:
            # Load audio using librosa/soundfile
            try:
                # Load efficient (offset + duration)
                audio_data, sr = librosa.load(
                    clip['source_file'], 
                    sr=44100, 
                    mono=False,
                    offset=clip['offset'], 
                    duration=clip['duration']
                )
                
                # Ensure stereo
                if audio_data.ndim == 1:
                    audio_data = np.stack([audio_data, audio_data])
                
                # Place in timeline
                start_sample = int(clip['start_time'] * 44100)
                length = audio_data.shape[1]
                end_sample = start_sample + length
                
                if end_sample > num_samples:
                    length = num_samples - start_sample
                    audio_data = audio_data[:, :length]
                    end_sample = num_samples
                
                # Apply Clip Gain
                audio_data *= clip['gain']
                
                # Apply Fades (if clip had fade properties, we'd do it here using processor.apply_fade)
                
                # Mix into Track
                track_signal[:, start_sample:end_sample] += audio_data
                
            except Exception as e:
                print(f"Error processing clip {clip['id']}: {e}")
                continue

        # 2. Apply Track Effects (Pedalboard)
        if track['effects']:
            effects_config = []
            for fx in track['effects']:
                 effects_config.append({'type': fx['type'], 'parameters': fx['parameters']})
            
            try:
                track_signal = processor.process_track(track_signal, effects_config)
            except Exception as e:
                 print(f"Error applying effects on track {track['name']}: {e}")

        # 3. Apply Automation (Volume / Pan)
        # Check for automation curves in track data (fetched by db.get_project_state)
        # Assuming track['automation'] is list of {parameter, points}
        
        # Default Mix Parameters (Static)
        current_vol = track['gain']
        current_pan = track['pan']
        
        if 'automation' in track and track['automation']:
            for auto_lane in track['automation']:
                if not auto_lane.get('enabled', True): continue
                
                param = auto_lane['parameter'] # 'volume' or 'pan'
                points = auto_lane['points'] # list of {time, value}
                
                if param == 'volume' and points:
                     track_signal = processor.apply_automation_curve(track_signal, points, 'volume')
                     current_vol = 1.0 # Automation overrides static gain (usually, or multiplies)
                     
                elif param == 'pan' and points:
                     track_signal = processor.apply_automation_curve(track_signal, points, 'pan')
                     current_pan = 0.0 # Automation overrides static pan
        
        # Apply Static Mixing (if not automated, OR as trim)
        # For professional DAWs, fader usually trims automation. Let's multiply.
        
        # Apply Static Pan (if no pan automation applied above, or as offset)
        if current_pan != 0:
            pan_rad = (current_pan + 1) * np.pi / 4
            left_gain = np.cos(pan_rad)
            right_gain = np.sin(pan_rad)
            track_signal[0] *= left_gain
            track_signal[1] *= right_gain
        
        track_signal *= current_vol

        # 4. Sum to Master
        master_mix += track_signal

    # Post-Process Master (Limiter?)
    # ...
    
    # Save Output
    filename = f"{project['name']}_mix_{uuid.uuid4().hex[:8]}.{params.output_format}"
    out_path = os.path.join(output_dir, filename)
    
    # Transpose for soundfile (N, C)
    sf.write(out_path, master_mix.T, 44100)
    
    return {"success": True, "output_path": out_path, "download_url": f"/api/audio/{filename}"}
