import sqlite3
import datetime
import json
import os

class DatabaseManager:
    """
    Manages SQLite3 database for ChendAI DAW projects.
    Handles persistence for Tracks, Clips, Effects, and Automation.
    """
    def __init__(self, db_path="chendai_projects.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. Projects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                bpm INTEGER DEFAULT 120,
                master_volume FLOAT DEFAULT 1.0,
                master_plugins_json TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Tracks (Multitrack Organization)
        try:
            cursor.execute("ALTER TABLE tracks ADD COLUMN color TEXT DEFAULT '#5b7fff'")
            cursor.execute("ALTER TABLE tracks ADD COLUMN icon TEXT DEFAULT '🥁'")
        except sqlite3.OperationalError:
            pass # Columns already exist

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracks (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'audio', -- audio, midi, bus
                color TEXT DEFAULT '#5b7fff',
                icon TEXT DEFAULT '🥁',
                gain FLOAT DEFAULT 1.0,
                pan FLOAT DEFAULT 0.0,
                mute BOOLEAN DEFAULT 0,
                solo BOOLEAN DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        # 3. Clips (Audio Regions on Timeline)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clips (
                id TEXT PRIMARY KEY,
                track_id TEXT NOT NULL,
                source_file TEXT NOT NULL, -- Path to audio file
                start_time FLOAT NOT NULL, -- Position in project (seconds)
                duration FLOAT NOT NULL,   -- Length of clip usage (seconds)
                offset FLOAT DEFAULT 0.0,  -- Start offset in source file (seconds)
                gain FLOAT DEFAULT 1.0,    -- Clip gain
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        ''')
        
        # 4. Effects (Plugins/Processes)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS effects (
                id TEXT PRIMARY KEY,
                track_id TEXT NOT NULL,
                type TEXT NOT NULL, -- eq, compressor, reverb, delay, vst
                parameters TEXT NOT NULL, -- JSON string
                order_index INTEGER DEFAULT 0,
                enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        ''')

        # 5. Automation (Curves)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation (
                id TEXT PRIMARY KEY,
                track_id TEXT NOT NULL,
                parameter TEXT NOT NULL, -- volume, pan, fx_param
                points_json TEXT NOT NULL, -- Array of {time, val, curve}
                enabled BOOLEAN DEFAULT 1,
                FOREIGN KEY (track_id) REFERENCES tracks (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_project(self, project_id, name, bpm=120):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO projects (id, name, bpm, updated_at) VALUES (?, ?, ?, ?)",
            (project_id, name, bpm, datetime.datetime.now())
        )
        conn.commit()
        conn.close()
        return project_id

    def add_track(self, track_id, project_id, name, track_type='audio', color='#5b7fff', icon='🥁'):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tracks (id, project_id, name, type, color, icon) VALUES (?, ?, ?, ?, ?, ?)",
            (track_id, project_id, name, track_type, color, icon)
        )
        conn.commit()
        conn.close()
    
    def add_clip(self, clip_id, track_id, source_file, start_time, duration, offset=0.0):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO clips (id, track_id, source_file, start_time, duration, offset) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (clip_id, track_id, source_file, start_time, duration, offset)
        )
        conn.commit()
        conn.close()

    def get_project_state(self, project_id):
        """Retrieve full project state for rendering"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get Project Info
        project = dict(cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone())
        
        # Get Tracks
        tracks_data = cursor.execute("SELECT * FROM tracks WHERE project_id = ?", (project_id,)).fetchall()
        tracks = []
        
        for t_row in tracks_data:
            track = dict(t_row)
            
            # Get Clips for Track
            clips = [dict(c) for c in cursor.execute("SELECT * FROM clips WHERE track_id = ?", (track['id'],)).fetchall()]
            track['clips'] = clips
            
            # Get Effects for Track
            effects = [dict(e) for e in cursor.execute("SELECT * FROM effects WHERE track_id = ? ORDER BY order_index", (track['id'],)).fetchall()]
            # Parse JSON parameters
            for e in effects:
                try:
                    e['parameters'] = json.loads(e['parameters'])
                except:
                    e['parameters'] = {}
            track['effects'] = effects

            # Get Automation
            automation = [dict(a) for a in cursor.execute("SELECT * FROM automation WHERE track_id = ?", (track['id'],)).fetchall()]
            for a in automation:
                try:
                    a['points'] = json.loads(a['points_json'])
                except:
                    a['points'] = []
            track['automation'] = automation
            
            tracks.append(track)
            
        project['tracks'] = tracks
        conn.close()
        
        return project

    def update_track_mixer(self, track_id, updates):
        """Update volume, pan, mute, solo"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        valid_fields = ['gain', 'pan', 'mute', 'solo']
        set_clause = []
        params = []
        
        for k, v in updates.items():
            if k in valid_fields:
                set_clause.append(f"{k} = ?")
                params.append(v)
        
        if set_clause:
            params.append(track_id)
            sql = f"UPDATE tracks SET {', '.join(set_clause)} WHERE id = ?"
            cursor.execute(sql, params)
            conn.commit()
            
        conn.close()
