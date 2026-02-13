"""
Command Pattern Implementation for Undo/Redo System
"""

from typing import Any, Dict, Optional
import numpy as np

class Command:
    """Base class for all undoable commands"""
    
    def execute(self):
        """Execute the command"""
        raise NotImplementedError
        
    def undo(self):
        """Undo the command"""
        raise NotImplementedError
        
    def description(self) -> str:
        """Human-readable description of the command"""
        return "Command"


class AddClipCommand(Command):
    """Command to add a clip to a track"""
    
    def __init__(self, track, clip):
        self.track = track
        self.clip = clip
        
    def execute(self):
        self.track.add_clip(self.clip)
        
    def undo(self):
        self.track.view.clips.remove(self.clip)
        self.track.view.update()
        
    def description(self) -> str:
        return f"Add Clip: {self.clip.name}"


class DeleteClipCommand(Command):
    """Command to delete a clip from a track"""
    
    def __init__(self, track, clip):
        self.track = track
        self.clip = clip
        self.clip_index = None
        
    def execute(self):
        # Store position for undo
        if self.clip in self.track.view.clips:
            self.clip_index = self.track.view.clips.index(self.clip)
        self.track.view.delete_clip(self.clip)
        
    def undo(self):
        # Restore clip at original position
        if self.clip_index is not None:
            self.track.view.clips.insert(self.clip_index, self.clip)
        else:
            self.track.view.clips.append(self.clip)
        self.track.view.update()
        
    def description(self) -> str:
        return f"Delete Clip: {self.clip.name}"


class MoveClipCommand(Command):
    """Command to move a clip to a new time position"""
    
    def __init__(self, clip, old_time: float, new_time: float):
        self.clip = clip
        self.old_time = old_time
        self.new_time = new_time
        
    def execute(self):
        self.clip.start_time = self.new_time
        
    def undo(self):
        self.clip.start_time = self.old_time
        
    def description(self) -> str:
        return f"Move Clip: {self.clip.name}"


class SplitClipCommand(Command):
    """Command to split a clip at a specific time"""
    
    def __init__(self, track, original_clip, split_time: float):
        self.track = track
        self.original_clip = original_clip
        self.split_time = split_time
        
        # Store original state
        self.original_data = original_clip.data.copy()
        self.original_duration = original_clip.duration
        
        # These will be set during execute
        self.new_clip = None
        
    def execute(self):
        # Calculate split point
        local_split_sec = self.split_time - self.original_clip.start_time
        split_sample = int(local_split_sec * self.original_clip.sr)
        
        # Split data
        data1 = self.original_clip.data[:split_sample]
        data2 = self.original_clip.data[split_sample:]
        
        # Update original clip
        self.original_clip.data = data1
        
        # Create new clip (import here to avoid circular dependency)
        from ui_timeline import AudioClip
        self.new_clip = AudioClip(data2, self.original_clip.sr, self.original_clip.name, self.split_time)
        
        # Add to track
        self.track.view.clips.append(self.new_clip)
        self.track.view.update()
        
    def undo(self):
        # Restore original clip data
        self.original_clip.data = self.original_data
        
        # Remove the new clip
        if self.new_clip in self.track.view.clips:
            self.track.view.clips.remove(self.new_clip)
        
        self.track.view.update()
        
    def description(self) -> str:
        return f"Split Clip: {self.original_clip.name}"


class UndoStack:
    """Manages undo/redo command history"""
    
    def __init__(self, max_size: int = 100):
        self.undo_stack = []
        self.redo_stack = []
        self.max_size = max_size
        
    def execute(self, command: Command):
        """Execute a command and add it to the undo stack"""
        command.execute()
        self.undo_stack.append(command)
        
        # Clear redo stack when new command is executed
        self.redo_stack.clear()
        
        # Limit stack size
        if len(self.undo_stack) > self.max_size:
            self.undo_stack.pop(0)
            
    def undo(self) -> bool:
        """Undo the last command"""
        if not self.can_undo():
            return False
            
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True
        
    def redo(self) -> bool:
        """Redo the last undone command"""
        if not self.can_redo():
            return False
            
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        return True
        
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.undo_stack) > 0
        
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self.redo_stack) > 0
        
    def clear(self):
        """Clear both stacks"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        
    def get_undo_description(self) -> Optional[str]:
        """Get description of command that would be undone"""
        if self.can_undo():
            return self.undo_stack[-1].description()
        return None
        
    def get_redo_description(self) -> Optional[str]:
        """Get description of command that would be redone"""
        if self.can_redo():
            return self.redo_stack[-1].description()
        return None
