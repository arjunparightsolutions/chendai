"""
Project Manager - SQLite database for project management
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict


class ProjectManager:
    """Manages ChendAI Studio projects using SQLite"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to user's documents folder
            docs_folder = os.path.expanduser("~/Documents/ChendAI Studio")
            os.makedirs(docs_folder, exist_ok=True)
            db_path = os.path.join(docs_folder, "projects.db")
        
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Initialize database with schema"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_path TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sample_rate INTEGER DEFAULT 44100,
                bpm INTEGER DEFAULT 120,
                last_opened TIMESTAMP
            )
        """)
        
        # Tracks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'audio',
                color TEXT DEFAULT '#00d4ff',
                volume REAL DEFAULT 1.0,
                pan REAL DEFAULT 0.0,
                mute INTEGER DEFAULT 0,
                solo INTEGER DEFAULT 0,
                order_index INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)
        
        # Clips table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                audio_path TEXT NOT NULL,
                start_time REAL DEFAULT 0.0,
                duration REAL NOT NULL,
                clip_offset REAL DEFAULT 0.0,
                volume REAL DEFAULT 1.0,
                fade_in REAL DEFAULT 0.0,
                fade_out REAL DEFAULT 0.0,
                FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
            )
        """)
        
        # Mixer states (FX settings)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mixer_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                effect_type TEXT NOT NULL,
                parameters TEXT,
                enabled INTEGER DEFAULT 1,
                order_index INTEGER DEFAULT 0,
                FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
    
    def create_project(self, name: str, file_path: str, sample_rate: int = 44100, bpm: int = 120) -> int:
        """Create new project"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (name, file_path, sample_rate, bpm, last_opened)
            VALUES (?, ?, ?, ?, ?)
        """, (name, file_path, sample_rate, bpm, datetime.now()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get project by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_project_by_path(self, file_path: str) -> Optional[Dict]:
        """Get project by file path"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_recent_projects(self, limit: int = 10) -> List[Dict]:
        """Get recent projects"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM projects 
            ORDER BY last_opened DESC 
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_project(self, project_id: int, **kwargs):
        """Update project fields"""
        kwargs['modified_at'] = datetime.now()
        
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [project_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE projects SET {fields} WHERE id = ?", values)
        self.conn.commit()
    
    def update_last_opened(self, project_id: int):
        """Update last opened timestamp"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE projects SET last_opened = ? WHERE id = ?
        """, (datetime.now(), project_id))
        self.conn.commit()
    
    def delete_project(self, project_id: int):
        """Delete project and all associated data"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()
    
    # Track operations
    def create_track(self, project_id: int, name: str, track_type: str = 'audio', **kwargs) -> int:
        """Create new track"""
        cursor = self.conn.cursor()
        
        # Get next order index
        cursor.execute("SELECT MAX(order_index) FROM tracks WHERE project_id = ?", (project_id,))
        max_order = cursor.fetchone()[0]
        order_index = (max_order or 0) + 1
        
        cursor.execute("""
            INSERT INTO tracks (project_id, name, type, order_index, color, volume, pan)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, name, track_type, order_index,
            kwargs.get('color', '#00d4ff'),
            kwargs.get('volume', 1.0),
            kwargs.get('pan', 0.0)
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_tracks(self, project_id: int) -> List[Dict]:
        """Get all tracks for project"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tracks 
            WHERE project_id = ? 
            ORDER BY order_index
        """, (project_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_track(self, track_id: int, **kwargs):
        """Update track fields"""
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [track_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE tracks SET {fields} WHERE id = ?", values)
        self.conn.commit()
    
    def delete_track(self, track_id: int):
        """Delete track"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tracks WHERE id = ?", (track_id,))
        self.conn.commit()
    
    # Clip operations
    def create_clip(self, track_id: int, audio_path: str, start_time: float, duration: float, **kwargs) -> int:
        """Create new audio clip"""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO clips (track_id, audio_path, start_time, duration, clip_offset, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            track_id, audio_path, start_time, duration,
            kwargs.get('clip_offset', 0.0),
            kwargs.get('volume', 1.0)
        ))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_clips(self, track_id: int) -> List[Dict]:
        """Get all clips for track"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM clips 
            WHERE track_id = ? 
            ORDER BY start_time
        """, (track_id,))
        return [dict(row) for row in cursor.fetchall()]
    
    def update_clip(self, clip_id: int, **kwargs):
        """Update clip fields"""
        fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [clip_id]
        
        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE clips SET {fields} WHERE id = ?", values)
        self.conn.commit()
    
    def delete_clip(self, clip_id: int):
        """Delete clip"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM clips WHERE id = ?", (clip_id,))
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
