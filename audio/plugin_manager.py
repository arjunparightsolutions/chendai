"""
Plugin Manager - VST3 Plugin Hosting using Pedalboard
"""

import os
import platform
from pedalboard import load_plugin, Pedalboard
from PyQt5.QtCore import QObject, pyqtSignal

class PluginManager(QObject):
    """
    Manages VST3 plugins scanning, loading, and processing.
    """
    
    plugin_scanned = pyqtSignal(str, str) # name, path
    scan_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.plugins = {} # name -> path
        self.loaded_plugins = {} # track_id -> list of plugin instances
        
        # Default VST3 paths
        if platform.system() == "Windows":
            self.vst_paths = [
                r"C:\Program Files\Common Files\VST3",
                r"C:\Program Files (x86)\Common Files\VST3"
            ]
        elif platform.system() == "Darwin": # macOS
            self.vst_paths = [
                "/Library/Audio/Plug-Ins/VST3",
                "~/Library/Audio/Plug-Ins/VST3"
            ]
        else: # Linux
            self.vst_paths = [
                "/usr/lib/vst3",
                "~/.vst3"
            ]
            
    def scan_plugins(self):
        """Scan for VST3 plugins"""
        print("🔍 Scanning for VST3 plugins...")
        self.plugins.clear()
        
        for path in self.vst_paths:
            path = os.path.expanduser(path)
            if not os.path.exists(path):
                continue
                
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".vst3"):
                        full_path = os.path.join(root, file)
                        name = os.path.splitext(file)[0]
                        self.plugins[name] = full_path
                        self.plugin_scanned.emit(name, full_path)
                        print(f"  Found: {name}")
                        
        # Add built-in Pedalboard plugins (for testing/standard use)
        builtin_plugins = {
            "Compressor": "builtin:Compressor",
            "Reverb": "builtin:Reverb",
            "Delay": "builtin:Delay",
            "Chorus": "builtin:Chorus",
            "Phaser": "builtin:Phaser", 
            "Limiter": "builtin:Limiter",
            "Clipping": "builtin:Clipping",
            "Gain": "builtin:Gain",
            "HighpassFilter": "builtin:HighpassFilter",
            "LowpassFilter": "builtin:LowpassFilter"
        }
        
        for name, path in builtin_plugins.items():
            self.plugins[name] = path
            self.plugin_scanned.emit(name, path)
            print(f"  Added Built-in: {name}")

        self.scan_finished.emit()
        print(f"✅ Scan complete. Found {len(self.plugins)} plugins.")
        
    def load_plugin(self, name, track_id):
        """Load a plugin instance for a track"""
        if name not in self.plugins:
            print(f"❌ Plugin not found: {name}")
            return None
            
        try:
            path = self.plugins[name]
            
            if path.startswith("builtin:"):
                # Load built-in Pedalboard plugin
                import pedalboard
                class_name = path.split(":")[1]
                plugin_class = getattr(pedalboard, class_name)
                plugin = plugin_class()
            else:
                # Load VST3
                plugin = load_plugin(path)
            
            if track_id not in self.loaded_plugins:
                self.loaded_plugins[track_id] = []
                
            self.loaded_plugins[track_id].append(plugin)
            print(f"🔌 Loaded {name} on track {track_id}")
            return plugin
            
        except Exception as e:
            print(f"❌ Failed to load plugin {name}: {e}")
            return None
            
    def get_chain(self, track_id):
        """Get Pedalboard chain for a track"""
        if track_id in self.loaded_plugins:
            return Pedalboard(self.loaded_plugins[track_id])
        return Pedalboard([])
    
    def open_editor(self, plugin):
        """Open plugin editor UI"""
        try:
            # Check if it's a VST3 with editor
            if hasattr(plugin, 'show_editor'):
                plugin.show_editor()
            else:
                print(f"ℹ️ No native editor for {type(plugin).__name__}. Use generic parameter controls (Sprint 6).")
                # TODO: Open generic parameter window
        except Exception as e:
            print(f"❌ Cannot open editor: {e}")
