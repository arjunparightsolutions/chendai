"""
MIDI I/O - Import and Export MIDI files
"""

import mido
import os
from PyQt5.QtWidgets import QMessageBox

class MidiIO:
    """Handles reading and writing of MIDI files"""
    
    @staticmethod
    def import_midi(file_path):
        """
        Import MIDI file and return track data.
        Returns list of tracks with notes.
        """
        try:
            mid = mido.MidiFile(file_path)
            tracks = []
            
            for i, track in enumerate(mid.tracks):
                notes = []
                current_time = 0
                
                # Filter for note events
                active_notes = {} # note -> start_time
                
                for msg in track:
                    current_time += msg.time
                    
                    if msg.type == 'note_on' and msg.velocity > 0:
                        active_notes[msg.note] = {
                            'start': current_time, # currently ticks
                            'velocity': msg.velocity
                        }
                    elif (msg.type == 'note_off') or (msg.type == 'note_on' and msg.velocity == 0):
                        if msg.note in active_notes:
                            start_data = active_notes.pop(msg.note)
                            duration = current_time - start_data['start']
                            
                            # Convert ticks to seconds (approximate for now)
                            # Real implementations need tempo map
                            seconds_per_tick = mid.ticks_per_beat / 500000.0 # Default 120bpm
                            
                            notes.append({
                                'note': msg.note,
                                'start': start_data['start'],
                                'duration': duration,
                                'velocity': start_data['velocity']
                            })
                            
                if notes:
                    tracks.append({
                        'name': track.name or f"MIDI Track {i+1}",
                        'notes': notes,
                        'color': '#00ff55' # Green for MIDI
                    })
                    
            return tracks
            
        except Exception as e:
            print(f"Error importing MIDI: {e}")
            return []

    @staticmethod
    def export_midi(file_path, tracks, tempo=120):
        """
        Export tracks to MIDI file.
        tracks: List of dicts with 'notes' list
        """
        try:
            mid = mido.MidiFile(type=1)
            mid.ticks_per_beat = 480
            
            # Tempo track
            tempo_track = mido.MidiTrack()
            mid.tracks.append(tempo_track)
            tempo_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo)))
            
            for track_data in tracks:
                # Skip non-MIDI tracks (audio tracks)
                if 'notes' not in track_data:
                    continue
                    
                track = mido.MidiTrack()
                mid.tracks.append(track)
                track.name = track_data.get('name', 'Untitled')
                
                # Convert notes to events
                events = []
                for note in track_data['notes']:
                    # Note On
                    events.append({
                        'time': note['start'],
                        'type': 'note_on',
                        'note': note['note'],
                        'velocity': note['velocity']
                    })
                    # Note Off
                    events.append({
                        'time': note['start'] + note['duration'],
                        'type': 'note_off',
                        'note': note['note'],
                        'velocity': 0
                    })
                
                # Sort events by time
                events.sort(key=lambda x: x['time'])
                
                # Convert absolute time to delta time
                last_time = 0
                for event in events:
                    delta = int(event['time'] - last_time)
                    track.append(mido.Message(
                        event['type'],
                        note=event['note'],
                        velocity=event['velocity'],
                        time=delta
                    ))
                    last_time = event['time']
                    
            mid.save(file_path)
            return True
            
        except Exception as e:
            print(f"Error exporting MIDI: {e}")
            return False
