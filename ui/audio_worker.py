"""
Audio Worker - Background thread for music generation
"""

from PyQt5.QtCore import QThread, pyqtSignal
import traceback


class AudioGenerationWorker(QThread):
    """Worker thread for non-blocking audio generation"""
    
    # Signals
    progress_updated = pyqtSignal(int, str)  # progress (0-100), status message
    generation_complete = pyqtSignal(str)     # audio file path
    generation_failed = pyqtSignal(str)       # error message
    
    def __init__(self, chendai_system, params):
        super().__init__()
        self.chendai_system = chendai_system
        self.params = params
        self.is_cancelled = False
        
    def run(self):
        """Run audio generation in background"""
        try:
            self.progress_updated.emit(10, "Initializing AI composer...")
            
            # Extract parameters
            use_prompt = self.params.get('use_prompt', False)
            duration = self.params.get('duration', 30)
            
            if self.is_cancelled:
                return
                
            self.progress_updated.emit(30, "Generating composition...")
            
            def log_callback(message):
                self.progress_updated.emit(-1, message) # Use -1 to indicate a log message
                
            # Generate music
            if use_prompt:
                prompt = self.params.get('prompt', '')
                audio_path = self.chendai_system.generate_melam(
                    prompt=prompt,
                    duration=duration,
                    orchestration_strategy="dynamic",
                    log_callback=log_callback
                )
            else:
                pattern = self.params.get('pattern', 'panchari')
                strategy = self.params.get('strategy', 'traditional')
                
                # Map to actual method
                audio_path = self.chendai_system.generate_melam(
                    prompt=f"Generate {pattern} melam with {strategy} orchestration",
                    duration=duration,
                    orchestration_strategy=strategy,
                    log_callback=log_callback
                )
            
            if self.is_cancelled:
                return
                
            self.progress_updated.emit(80, "Rendering audio...")
            
            # Simulate final rendering steps
            import time
            time.sleep(0.5)
            
            self.progress_updated.emit(100, "Complete!")
            self.generation_complete.emit(audio_path)
            
        except Exception as e:
            error_msg = f"Generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            self.generation_failed.emit(error_msg)
            
    def cancel(self):
        """Cancel generation"""
        self.is_cancelled = True
