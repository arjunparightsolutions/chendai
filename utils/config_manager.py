"""
Config Manager - Application settings persistence
"""

from PyQt5.QtCore import QSettings
import json


class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self):
        self.settings = QSettings("Right Solutions AI", "ChendAI Studio")
    
    def save_window_geometry(self, geometry_data):
        """Save window geometry"""
        self.settings.setValue("window/geometry", geometry_data)
    
    def get_window_geometry(self):
        """Get saved window geometry"""
        return self.settings.value("window/geometry")
    
    def save_recent_project(self, project_id):
        """Save last opened project"""
        self.settings.setValue("project/last_opened", project_id)
    
    def get_recent_project(self):
        """Get last opened project ID"""
        return self.settings.value("project/last_opened", type=int)
    
    def get_value(self, key, default=None):
        """Get config value"""
        return self.settings.value(key, default)
    
    def set_value(self, key, value):
        """Set config value"""
        self.settings.setValue(key, value)
