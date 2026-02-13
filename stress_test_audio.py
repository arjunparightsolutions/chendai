import time
import os
import uuid
import numpy as np
import soundfile as sf
import librosa
from database_manager import DatabaseManager
from audio_processor import AudioProcessor

def stress_test():
    print("🔥 STARTED: Audio Engine Stress Test")
    
    # Setup
    db_file = "stress_test.db"
    if os.path.exists(db_file): os.remove(db_file)
    db = DatabaseManager(db_file)
    
    processor = AudioProcessor()
    
    # 1. Create Dummy Audio Assets
    print("   Generating dummy audio assets...")
    os.makedirs("temp_stress_assets", exist_ok=True)
    
    sr = 44100
    duration = 10.0 # 10 seconds per clip
    t = np.linspace(0, duration, int(sr * duration))
    
    # Create 5 different dummy files
    asset_paths = []
    for i in range(5):
        freq = 220.0 * (i + 1)
        audio = 0.5 * np.sin(2 * np.pi * freq * t)
        # Stereo
        audio_stereo = np.stack([audio, audio]).T
        path = f"temp_stress_assets/test_tone_{i}.wav"
        sf.write(path, audio_stereo, sr)
        asset_paths.append(path)
        
    # 2. Setup Massive Project
    print("   Setting up project with 24 Tracks...")
    project_id = str(uuid.uuid4())
    db.create_project(project_id, "Stress Test Project")
    
    # Add 24 Tracks
    num_tracks = 24
    tracks = []
    for i in range(num_tracks):
        track_id = str(uuid.uuid4())
        db.add_track(track_id, project_id, f"Track {i}")
        tracks.append(track_id)
        
        # Add 4 Clips per track (40 seconds total audio per track, overlapping or sequential)
        # Let's do sequential to make a 40s song
        for j in range(4):
            clip_id = str(uuid.uuid4())
            source = asset_paths[j % len(asset_paths)]
            db.add_clip(clip_id, track_id, source, start_time=j*10.0, duration=10.0)
            
        # Add Effects to every other track
        if i % 2 == 0:
            import sqlite3
            import json
            # Connect to the SAME db file
            conn = sqlite3.connect(db_file)
            c = conn.cursor()
            fx_id = str(uuid.uuid4())
            params = json.dumps({'room_size': 0.5})
            c.execute("INSERT INTO effects (id, track_id, type, parameters) VALUES (?, ?, ?, ?)", 
                      (fx_id, track_id, 'reverb', params))
            conn.commit()
            conn.close()
            

    # 3. Benchmark Render
    print("   🚀 Starting Render Benchmark...")
    start_time = time.time()
    
    # --- RENDER LOGIC (Simplified from daw_routes.py) ---
    project = db.get_project_state(project_id)
    output_dir = "temp_stress_output"
    os.makedirs(output_dir, exist_ok=True)
    
    max_time = 40.0
    num_samples = int(max_time * 44100)
    master_mix = np.zeros((2, num_samples), dtype=np.float32)
    
    for track in project['tracks']:
        track_signal = np.zeros((2, num_samples), dtype=np.float32)
        
        # Clips
        for clip in track['clips']:
            try:
                # Load
                audio_data, _ = librosa.load(
                    clip['source_file'], sr=44100, mono=False,
                    offset=clip['offset'], duration=clip['duration']
                )
                if audio_data.ndim == 1: audio_data = np.stack([audio_data, audio_data])
                
                # Place
                start_sample = int(clip['start_time'] * 44100)
                length = audio_data.shape[1]
                end_sample = start_sample + length
                if end_sample > num_samples:
                    length = num_samples - start_sample
                    audio_data = audio_data[:, :length]
                    end_sample = num_samples
                    
                track_signal[:, start_sample:end_sample] += audio_data
            except Exception as e:
                print(f"Error: {e}")
                
        # Effects
        if track['effects']:
            fx_cfg = [{'type': fx['type'], 'parameters': fx['parameters']} for fx in track['effects']]
            track_signal = processor.process_track(track_signal, fx_cfg)
            
        master_mix += track_signal
        
    # Write
    out_path = os.path.join(output_dir, "stress_mix.wav")
    sf.write(out_path, master_mix.T, 44100)
    # ----------------------------------------------------
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"✅ Render Completed in {elapsed:.2f} seconds.")
    print(f"   Real-time factor: {elapsed / max_time:.2f}x (Lower is better, < 1.0 is faster than realtime)")
    
    # Cleanup
    import shutil
    try:
        shutil.rmtree("temp_stress_assets")
        shutil.rmtree("temp_stress_output")
        if os.path.exists(db_file): os.remove(db_file)
    except:
        pass
        
    if elapsed > max_time:
        print("⚠️ WARNING: Render took longer than real-time!")
    else:
        print("🎉 SUCCESS: Audio Engine is performant.")

if __name__ == "__main__":
    stress_test()
