from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sys
import os
import asyncio
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect

# Add parent directory to path to import chendai modules
sys.path.insert(0, str(Path(__file__).parent))

from chendai_6player import ChendAI6Player

app = FastAPI(title="ChendAI Studio API", version="1.0.0")

# Enable CORS for Web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WebSocket Logging Infrastructure ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"📡 New log client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"📡 Log client disconnected. Remaining: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        if not self.active_connections:
            return
        
        # We use asyncio.gather to broadcast to all clients
        await asyncio.gather(
            *[connection.send_text(message) for connection in self.active_connections],
            return_exceptions=True
        )

manager = ConnectionManager()

def broadcast_log(message: str):
    """Sync wrapper for broadcasting logs from async or sync code"""
    print(message) # Still print to console
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(manager.broadcast(message))
    except Exception:
        pass

# --- End WebSocket Infrastructure ---

# Initialize ChendAI system
chendai_system = None

from typing import List, Optional, Dict, Any

class PlayerParams(BaseModel):
    id: str
    volume: Optional[float] = None
    pan: Optional[float] = None
    mute: Optional[bool] = None
    solo: Optional[bool] = None

class GenerationParams(BaseModel):
    pattern: Optional[str] = None
    prompt: Optional[str] = None
    duration: int = 30
    strategy: str = "traditional"
    enable_spatial: bool = True
    players: Optional[List[PlayerParams]] = None

class GenerationResponse(BaseModel):
    success: bool
    audioPath: Optional[str] = None
    stems: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    duration: Optional[float] = None
    players: Optional[int] = None

@app.on_event("startup")
async def startup_event():
    """Initialize ChendAI system on startup"""
    global chendai_system
    try:
        chendai_system = ChendAI6Player(
            enable_spatial=True,
            orchestration_strategy="traditional"
        )
        print("✅ ChendAI 6-Player System Initialized")
    except Exception as e:
        print(f"❌ Failed to initialize ChendAI system: {e}")

@app.get("/")
async def root():
    return {
        "name": "ChendAI Studio API",
        "version": "1.0.0",
        "status": "running"
    }

@app.post("/api/generate", response_model=GenerationResponse)
async def generate_melam(params: GenerationParams):
    """
    Generate a new Chendamelam composition
    Supports both natural language prompts and traditional pattern selection
    """
    if not chendai_system:
        raise HTTPException(status_code=500, detail="ChendAI system not initialized")
    
    try:
        # Update player settings if provided
        if params.players:
            print("🎛️ Updating player settings...")
            for p_update in params.players:
                player = chendai_system.ensemble.get_player(p_update.id)
                if player:
                    if p_update.volume is not None:
                        player.gain = p_update.volume
                    if p_update.pan is not None:
                        player.pan = p_update.pan
                    if p_update.mute is not None:
                        player.mute = p_update.mute
                    if p_update.solo is not None:
                        player.solo = p_update.solo
                    print(f"   ✓ Updated {player.name}: Gain={player.gain:.2f}, Pan={player.pan:.2f}, Mute={player.mute}, Solo={player.solo}")

        # Use prompt if provided, otherwise use pattern
        request_text = params.prompt if params.prompt else f"a {params.pattern} melam"
        
        print(f"🎵 Generating: '{request_text}' - {params.duration}s - {params.strategy}")
        
        # Generate the melam
        broadcast_log(f"🤖 AI Composition Phase for: {request_text}")
        result = chendai_system.generate_melam(
            prompt=request_text,
            duration=params.duration,
            orchestration_strategy=params.strategy,
            log_callback=broadcast_log
        )
        
        # Handle new return format
        if isinstance(result, dict):
             output_path = result.get("master")
             stems = result.get("stems", {})
             metadata = result.get("metadata", {})
        else:
             output_path = result
             stems = {}
             metadata = {}
        
        # Convert path to absolute path
        abs_path = str(Path(output_path).absolute())
        
        # Convert stems to absolute paths and map to web URLs if needed
        # For local electron, absolute paths are fine if we disable web security or use file:// protocol properly
        # But server serves /api/audio/{filename}.
        
        # Let's verify we can serve them via /api/audio
        # The /api/audio endpoint serves from "output" directory.
        # Stems are in "output/subdir/stem.wav".
        # We need to ensure /api/audio can serve subdirectories or just return absolute paths and let Electron load them via file:// protocol (if allowed).
        # Since we use "ChendAI Studio" (electron), file:// is usually allowed with webSecurity: false or proper CSP.
        # But serving via HTTP is safer.
        
        # Let's assume absolute paths for Electron for now as per `abs_path` above.
        
        abs_stems = {k: str(Path(v).absolute()) for k, v in stems.items()}
        
        return GenerationResponse(
            success=True,
            audioPath=abs_path,
            stems=abs_stems,
            metadata=metadata,
            duration=params.duration,
            players=4  # 6-player system has 4 active players by default
        )
    
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return GenerationResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/patterns")
async def list_patterns():
    """List available melam patterns"""
    return {
        "patterns": [
            {"id": "panchari", "name": "Panchari Melam", "description": "Traditional 6-beat pattern"},
            {"id": "pandi", "name": "Pandi Melam", "description": "Powerful outdoor style"},
            {"id": "thayambaka", "name": "Thayambaka", "description": "Solo chenda performance"},
            {"id": "panchavadyam", "name": "Panchavadyam", "description": "Five instrument ensemble"}
        ]
    }

@app.get("/api/strategies")
async def list_strategies():
    """List available orchestration strategies"""
    return {
        "strategies": [
            {"id": "traditional", "name": "Traditional", "description": "Authentic temple style"},
            {"id": "dynamic", "name": "Dynamic", "description": "AI-driven variations"},
            {"id": "unison", "name": "Unison", "description": "Synchronized ensemble"},
            {"id": "antiphonal", "name": "Antiphonal", "description": "Call and response"},
            {"id": "layered", "name": "Layered", "description": "Progressive density"}
        ]
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "system_ready": chendai_system is not None
    }

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.get("/api/audio/{filename}")
async def serve_audio(filename: str):
    """Serve generated audio files (wav, mp3, etc)"""
    audio_path = Path("output") / filename
    
    print(f"📁 Serving audio: {filename}")
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail=f"Audio file not found: {filename}")
    
    # Determine media type
    ext = audio_path.suffix.lower()
    media_table = {
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        '.bgm': 'audio/mpeg',
        '.m4a': 'audio/mp4'
    }
    media_type = media_table.get(ext, 'application/octet-stream')

    return FileResponse(
        audio_path, 
        media_type=media_type,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "*",
            "Cache-Control": "no-cache"
        }
    )

from audio_exporter import AudioExporter
exporter = AudioExporter()

class ExportParams(BaseModel):
    filename: str
    format: str
    bit_depth: int = 16
    sample_rate: int = 44100
    normalize: bool = False

@app.get("/api/formats")
async def list_formats():
    """List supported export formats"""
    return {"formats": exporter.get_supported_formats()}

@app.post("/api/export")
async def export_audio(params: ExportParams):
    """Export generated audio to a specific format"""
    try:
        # Find input file (assume in output/ directory)
        input_filename = params.filename
        if not input_filename.endswith('.wav'):
             input_filename += '.wav'
             
        input_path = os.path.join("output", input_filename)
        
        if not os.path.exists(input_path):
            # Try finding it without directory prefix if passed as full path or just name
            possible_name = os.path.basename(input_filename)
            input_path = os.path.join("output", possible_name)
            
            if not os.path.exists(input_path):
                 raise HTTPException(status_code=404, detail=f"Source file not found: {input_filename}")

        print(f"💾 Exporting {input_filename} to {params.format}...")
        
        # Perform export
        output_path = exporter.export(
            input_path=input_path,
            output_format=params.format,
            output_dir="output",
            sample_rate=params.sample_rate,
            normalize=params.normalize
        )
        
        # Return download URL
        filename_only = os.path.basename(output_path)
        download_url = f"http://localhost:8000/api/audio/{filename_only}"
        
        return {
            "success": True,
            "download_url": download_url,
            "filename": filename_only,
            "format": params.format
        }
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from daw_routes import router as daw_router
app.include_router(daw_router)

if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print("🚀 ChendAI Studio API Server")
    print("=" * 70)
    print("Starting server on http://127.0.0.1:8000")
    print("Press Ctrl+C to stop")
    print("=" * 70)
    
    try:
        uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import sys
        sys.exit(1)
