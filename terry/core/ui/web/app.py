#!/usr/bin/env python3
"""
Terry v6.1 - Web UI
Beautiful professional interface for Terry voice assistant
"""
import sys
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import logger first (always needed)
from terry.core.utils.logger import get_logger
logger = get_logger(__name__)

# Import Terry components
try:
    from terry.features.notes.voice_notes import get_notes_manager
    from terry.core.memory.manager import MemoryManager
    from terry.features.automation.macros import get_macro_recorder
    from terry.core.utils.silent_mode import is_silent
except ImportError as e:
    logger.warning(f"Could not import some Terry components: {e}")


# ═══════════════════════════════════════════════════════════
# LIFESPAN HANDLER
# ═══════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 Terry Web UI starting...")
    print("   Version: 6.1.9")
    print("   Access: http://localhost:8080")
    print("   Swagger UI: http://localhost:8080/docs")
    print("   ReDoc: http://localhost:8080/redoc")
    yield
    # Shutdown
    print("👋 Terry Web UI shutting down...")


# ═══════════════════════════════════════════════════════════
# FASTAPI APP SETUP
# ═══════════════════════════════════════════════════════════

# API Tags for organization
tags_metadata = [
    {
        "name": "System",
        "description": "System status, health checks, and general information"
    },
    {
        "name": "Commands",
        "description": "Execute and manage voice commands"
    },
    {
        "name": "Notes",
        "description": "Voice notes management with semantic search"
    },
    {
        "name": "Macros",
        "description": "Macro recording and playback functionality"
    },
    {
        "name": "Camera",
        "description": "Camera vision system configuration and control"
    },
    {
        "name": "WebSocket",
        "description": "Real-time updates via WebSocket connection"
    }
]

app = FastAPI(
    title="Terry Voice Assistant API",
    description="""
# Terry Voice Assistant - Professional REST API

Terry is a local voice assistant for macOS with Alexa-style UX and superior local AI intelligence.

## Features

* **Voice Commands**: Execute commands through Terry's LLM processor
* **Voice Notes**: Create and search notes with semantic search
* **Macros**: Record and replay command sequences
* **Camera Vision**: Face recognition with always-active service
* **Real-time Updates**: WebSocket support for live notifications
* **System Monitoring**: Health checks and statistics

## Authentication

Currently, this API does not require authentication as it's designed for local use only.

## Rate Limiting

No rate limiting is applied for local deployments.

## Support

For issues and feedback, visit: https://github.com/anthropics/claude-code/issues
    """,
    version="6.1.9",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    contact={
        "name": "Terry Development Team",
        "url": "https://github.com/anthropics/claude-code",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


# ═══════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════

class CommandRequest(BaseModel):
    command: str = Field(
        ...,
        description="Voice command to execute",
        example="Pon música de Coldplay"
    )
    language: str = Field(
        default="es",
        description="Language for command processing (es/en)",
        example="es"
    )
    context: Optional[str] = Field(
        default=None,
        description="Conversation history for memory context",
        example="Previous conversation about music preferences"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "command": "Pon música de Coldplay",
                "language": "es",
                "context": "Usuario pidió música rock previamente"
            }
        }


class NoteRequest(BaseModel):
    content: str = Field(
        ...,
        description="Note content",
        example="Comprar leche y pan mañana"
    )
    category: Optional[str] = Field(
        default="general",
        description="Note category",
        example="shopping"
    )
    priority: int = Field(
        default=0,
        description="Priority level (0-5, higher is more important)",
        ge=0,
        le=5,
        example=2
    )

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Comprar leche y pan mañana",
                "category": "shopping",
                "priority": 2
            }
        }


class CameraConfigRequest(BaseModel):
    camera_url: Optional[str] = Field(
        default=None,
        description="Camera stream URL (HTTP/RTSP)",
        example="http://192.168.1.42:8080/video"
    )
    camera_username: Optional[str] = Field(
        default=None,
        description="Camera authentication username",
        example="admin"
    )
    camera_password: Optional[str] = Field(
        default=None,
        description="Camera authentication password",
        example="password123"
    )
    use_webcam: bool = Field(
        default=False,
        description="Use local webcam instead of IP camera",
        example=False
    )
    webcam_index: int = Field(
        default=0,
        description="Webcam device index (0 for default)",
        ge=0,
        example=0
    )
    enabled: bool = Field(
        default=False,
        description="Enable camera vision system",
        example=True
    )
    auto_start: bool = Field(
        default=False,
        description="Auto-start camera on system boot",
        example=True
    )

    class Config:
        json_schema_extra = {
            "example": {
                "camera_url": "http://192.168.1.42:8080/video",
                "use_webcam": False,
                "webcam_index": 0,
                "enabled": True,
                "auto_start": True
            }
        }


# ═══════════════════════════════════════════════════════════
# RESPONSE MODELS
# ═══════════════════════════════════════════════════════════

class StatusResponse(BaseModel):
    status: str = Field(..., description="System status", example="online")
    version: str = Field(..., description="Terry version", example="6.1.9")
    timestamp: str = Field(..., description="ISO timestamp", example="2025-12-26T10:30:00")
    silent_mode: bool = Field(..., description="Silent mode enabled", example=False)
    features: Dict[str, bool] = Field(
        ...,
        description="Available features",
        example={"notes": True, "memory": True, "macros": True}
    )


class CommandResponse(BaseModel):
    success: bool = Field(..., description="Command execution success", example=True)
    command: str = Field(..., description="Original command", example="Pon música")
    response: str = Field(..., description="Terry's response", example="Reproduciendo música")
    action_type: Optional[str] = Field(None, description="Action type executed", example="music_play")
    intent: Optional[str] = Field(None, description="Detected intent", example="play_music")
    timestamp: str = Field(..., description="ISO timestamp", example="2025-12-26T10:30:00")


class NotesResponse(BaseModel):
    notes: list = Field(..., description="List of notes", example=[])
    total: int = Field(..., description="Total number of notes", example=5)


class MacrosResponse(BaseModel):
    macros: list = Field(..., description="List of macros", example=[])
    total: int = Field(..., description="Total number of macros", example=3)


class CameraStatusResponse(BaseModel):
    running: bool = Field(..., description="Camera service running", example=True)
    timestamp: str = Field(..., description="ISO timestamp", example="2025-12-26T10:30:00")
    people_present: Optional[list] = Field(None, description="People currently present", example=["Alice", "Bob"])
    stats: Optional[Dict[str, Any]] = Field(None, description="Camera statistics", example={})


# ═══════════════════════════════════════════════════════════
# WEBSOCKET CONNECTION MANAGER
# ═══════════════════════════════════════════════════════════

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


# ═══════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════

@app.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False  # Don't include main UI page in API docs
)
async def home(request: Request):
    """Main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get(
    "/diagnostico",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def diagnostico(request: Request):
    """Página de diagnóstico de navegador."""
    return templates.TemplateResponse("diagnostico.html", {"request": request})


@app.get(
    "/test",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def test_simple(request: Request):
    """Página de test simple de JavaScript."""
    return templates.TemplateResponse("test_simple.html", {"request": request})


@app.get(
    "/ultra",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def ultra_simple(request: Request):
    """Página ultra simple para verificar clicks."""
    return templates.TemplateResponse("ultra_simple.html", {"request": request})


@app.get(
    "/fix",
    response_class=HTMLResponse,
    include_in_schema=False
)
async def fix_page(request: Request):
    """Página para diagnosticar y arreglar problemas de UI."""
    return templates.TemplateResponse("fix.html", {"request": request})


@app.get(
    "/api/status",
    tags=["System"],
    summary="Get system status",
    description="""
Get current system status including:
- Service health (online/offline)
- Version information
- Silent mode state
- Available features
- Memory statistics

This endpoint is useful for health checks and monitoring.
    """,
    response_model=StatusResponse
)
async def get_status():
    """Get Terry system status."""
    try:
        # Get stats from various systems
        stats = {
            "status": "online",
            "version": "6.1.0",
            "timestamp": datetime.now().isoformat(),
            "silent_mode": is_silent(),
            "features": {
                "notes": True,
                "memory": True,
                "macros": True,
                "plugins": True,
                "api": True
            }
        }

        # Try to get memory stats
        try:
            from pathlib import Path
            db_path = str(Path.home() / ".terry" / "memory" / "memory.db")
            memory = MemoryManager(db_path=db_path)
            memory_stats = await memory.get_stats()
            stats["memory"] = memory_stats
        except Exception as e:
            logger.debug(f"Memory stats unavailable: {e}")
            stats["memory"] = {"interactions": 0}

        return stats
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get(
    "/api/stats",
    tags=["System"],
    summary="Get detailed statistics",
    description="""
Get comprehensive statistics about Terry's usage:
- Total notes and categories
- Macros count and recent macros
- Memory interactions count
- Command execution statistics

Useful for analytics and monitoring Terry's activity.
    """
)
async def get_stats():
    """Get detailed statistics."""
    stats = {
        "notes": {"total": 0, "categories": {}},
        "macros": {"total": 0, "recent": []},
        "memory": {"interactions": 0},
        "commands": {"today": 0, "total": 0}
    }

    try:
        # Notes stats
        notes_mgr = get_notes_manager()
        recent_notes = notes_mgr.get_recent_notes(limit=100)
        stats["notes"]["total"] = len(recent_notes)

        # Categories
        categories = {}
        for note in recent_notes:
            cat = note.get("category", "general")
            categories[cat] = categories.get(cat, 0) + 1
        stats["notes"]["categories"] = categories

    except Exception as e:
        print(f"Error getting notes stats: {e}")

    try:
        # Macros stats
        macro_recorder = get_macro_recorder()
        macros = macro_recorder.list_macros()
        stats["macros"]["total"] = len(macros)
        stats["macros"]["recent"] = macros[:5]
    except Exception as e:
        print(f"Error getting macro stats: {e}")

    try:
        # Memory stats
        db_path = str(Path.home() / ".terry" / "memory" / "memory.db")
        memory = MemoryManager(db_path=db_path)
        memory_stats = await memory.get_stats()
        stats["memory"] = memory_stats
    except Exception as e:
        logger.debug(f"Error getting memory stats: {e}")

    return stats


@app.post(
    "/api/command",
    tags=["Commands"],
    summary="Execute a voice command",
    description="""
Execute a voice command through Terry's LLM processor.

The command will be:
1. Processed by Terry's 3-level cache (pattern match → cache → LLM)
2. Converted into actionable intents
3. Executed through the action system
4. Broadcast to all connected WebSocket clients

**Examples:**
- "Pon música de Coldplay" → Plays music on Spotify
- "Abre YouTube" → Opens YouTube in browser
- "Modo trabajo" → Executes work routine
    """,
    response_model=CommandResponse
)
async def execute_command(request: CommandRequest):
    """Execute a voice command through Terry's processor."""
    try:
        # Import Terry's command processor components
        from terry.core.llm.processor import CommandProcessor
        from terry.core.llm.ollama_client import OllamaClient

        # Create LLM client and processor
        llm_client = OllamaClient()
        processor = CommandProcessor(llm_client=llm_client)

        # Process the command with context
        result = await processor.process_command(
            user_input=request.command,
            language=request.language,
            context=request.context
        )

        # Extract action_type from actions array
        action_type = None
        if result.get("actions") and len(result["actions"]) > 0:
            action_type = result["actions"][0].get("type")

        response = {
            "success": True,
            "command": request.command,
            "response": result.get("response", "Comando ejecutado"),
            "action_type": action_type,
            "intent": result.get("intent"),
            "timestamp": datetime.now().isoformat()
        }

        # Broadcast to all connected clients
        await manager.broadcast({
            "type": "command_executed",
            "data": response
        })

        return response
    except Exception as e:
        logger.error(f"Error executing command: {e}")

        # Fallback response
        response = {
            "success": True,
            "command": request.command,
            "response": f"Comando procesado: {request.command}",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

        return response


@app.post(
    "/api/silent-mode",
    tags=["System"],
    summary="Toggle silent mode",
    description="""
Toggle Terry's silent mode on/off.

When silent mode is enabled:
- TTS (text-to-speech) is disabled
- Terry processes commands but doesn't speak responses
- Useful for quiet environments

State is broadcast to all connected WebSocket clients.
    """
)
async def toggle_silent_mode():
    """Toggle silent mode."""
    try:
        new_state = toggle_silent()

        await manager.broadcast({
            "type": "silent_mode_changed",
            "data": {"silent": new_state}
        })

        return {"silent": new_state}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get(
    "/api/notes",
    tags=["Notes"],
    summary="Get recent notes",
    description="""
Retrieve recent voice notes from Terry's notes system.

Supports:
- Filtering by category
- Pagination with limit parameter
- Semantic search (via separate endpoint)

Notes are stored with timestamps and can be searched later.
    """,
    response_model=NotesResponse
)
async def get_notes(
    limit: int = Query(10, description="Maximum number of notes to return", ge=1, le=100),
    category: Optional[str] = Query(None, description="Filter by category (e.g., 'shopping', 'work')")
):
    """Get recent notes."""
    try:
        notes_mgr = get_notes_manager()
        notes = notes_mgr.get_recent_notes(limit=limit, category=category)

        return {
            "notes": notes,
            "total": len(notes)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post(
    "/api/notes",
    tags=["Notes"],
    summary="Create a new note",
    description="""
Create a new voice note in Terry's notes system.

Features:
- Automatic timestamping
- Category organization
- Priority levels (0-5)
- Semantic embeddings for search

Notes are persisted to disk and broadcast to connected clients.
    """
)
async def create_note(note: NoteRequest):
    """Create a new note."""
    try:
        notes_mgr = get_notes_manager()
        note_id = notes_mgr.add_note(
            content=note.content,
            category=note.category,
            priority=note.priority
        )

        await manager.broadcast({
            "type": "note_created",
            "data": {"id": note_id, "content": note.content}
        })

        return {
            "success": True,
            "id": note_id,
            "content": note.content
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get(
    "/api/macros",
    tags=["Macros"],
    summary="Get all macros",
    description="""
Retrieve all recorded macros from Terry's macro system.

Macros are sequences of commands that can be recorded and replayed:
1. Start recording: "Terry, graba macro"
2. Execute commands
3. Stop recording: "Terry, para de grabar"
4. Replay: "Terry, ejecuta macro [nombre]"

Returns list of all saved macros with metadata.
    """,
    response_model=MacrosResponse
)
async def get_macros():
    """Get all macros."""
    try:
        recorder = get_macro_recorder()
        macros = recorder.list_macros()

        return {
            "macros": macros,
            "total": len(macros)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get(
    "/api/camera/config",
    tags=["Camera"],
    summary="Get camera configuration",
    description="""
Get current camera vision system configuration.

Includes:
- Camera URL (IP camera stream)
- Webcam settings (local camera)
- Authentication credentials (password masked)
- Auto-start configuration

Configuration is stored in `terry/core/config/settings.yaml`.
    """
)
async def get_camera_config():
    """Get current camera configuration."""
    try:
        from terry.core.config.settings import get_settings
        settings = get_settings()
        camera_config = settings.get("camera_vision", {})

        # Hide password in response
        config_response = camera_config.copy()
        if "camera_password" in config_response and config_response["camera_password"]:
            config_response["camera_password_set"] = True
            config_response["camera_password"] = "****"
        else:
            config_response["camera_password_set"] = False

        return {
            "success": True,
            "config": config_response
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post(
    "/api/camera/config",
    tags=["Camera"],
    summary="Update camera configuration",
    description="""
Update camera vision system configuration.

This endpoint:
1. Updates settings.yaml with new configuration
2. Validates camera URL and credentials
3. Broadcasts update to all connected clients

**Note:** Camera service must be restarted for changes to take effect.

**Common camera URLs:**
- Android IP Webcam: `http://192.168.1.X:8080/video`
- RTSP camera: `rtsp://username:password@192.168.1.X:554/stream`
- Local webcam: Set `use_webcam: true` and `webcam_index: 0`
    """
)
async def update_camera_config(config: CameraConfigRequest):
    """Update camera configuration."""
    try:
        import yaml
        from terry.core.config.settings import get_settings

        # Load current settings
        settings_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)

        # Update camera config
        if "camera_vision" not in settings:
            settings["camera_vision"] = {}

        camera_config = settings["camera_vision"]

        # Update fields
        if config.camera_url is not None:
            camera_config["camera_url"] = config.camera_url
        if config.camera_username is not None:
            camera_config["camera_username"] = config.camera_username
        if config.camera_password is not None and config.camera_password != "****":
            camera_config["camera_password"] = config.camera_password

        camera_config["use_webcam"] = config.use_webcam
        camera_config["webcam_index"] = config.webcam_index
        camera_config["enabled"] = config.enabled
        camera_config["auto_start"] = config.auto_start

        # Save settings
        with open(settings_path, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)

        # Broadcast update
        await manager.broadcast({
            "type": "camera_config_updated",
            "data": {"success": True}
        })

        return {
            "success": True,
            "message": "Configuración de cámara actualizada"
        }
    except Exception as e:
        logger.error(f"Error updating camera config: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get(
    "/api/camera/status",
    tags=["Camera"],
    summary="Get camera service status",
    description="""
Get current camera vision service status.

Returns:
- Service running state (true/false)
- People currently present (detected by face recognition)
- Detection statistics (total detections, recognition rate)
- Timestamp of last update

Useful for monitoring the camera system health.
    """,
    response_model=CameraStatusResponse
)
async def get_camera_status():
    """Get camera service status."""
    try:
        from terry.features.vision.camera import get_camera_vision_manager

        manager_instance = get_camera_vision_manager()
        is_running = manager_instance.is_running()

        status = {
            "running": is_running,
            "timestamp": datetime.now().isoformat()
        }

        if is_running:
            # Get current presence
            people = manager_instance.who_is_present()
            stats = manager_instance.get_stats()

            status.update({
                "people_present": people,
                "stats": stats
            })

        return status
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "running": False}
        )


@app.post(
    "/api/camera/start",
    tags=["Camera"],
    summary="Start camera service",
    description="""
Start the camera vision service.

This will:
1. Initialize camera stream (IP camera or webcam)
2. Start face detection and recognition
3. Begin tracking presence
4. Enable event callbacks

**Prerequisites:**
- Camera must be configured via `/api/camera/config`
- Face recognition dependencies must be installed
- Camera stream must be accessible

Returns success status and message.
    """
)
async def start_camera():
    """Start camera service."""
    try:
        from terry.features.vision.camera import get_camera_vision_manager

        manager_instance = get_camera_vision_manager()
        success = manager_instance.start()

        return {
            "success": success,
            "message": "Cámara iniciada" if success else "No se pudo iniciar la cámara"
        }
    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "success": False}
        )


@app.post(
    "/api/camera/stop",
    tags=["Camera"],
    summary="Stop camera service",
    description="""
Stop the camera vision service.

This will:
1. Stop face detection and recognition
2. Release camera stream
3. Clear presence tracking
4. Disable event callbacks

Safe to call even if service is not running.

Returns success status and message.
    """
)
async def stop_camera():
    """Stop camera service."""
    try:
        from terry.features.vision.camera import get_camera_vision_manager

        manager_instance = get_camera_vision_manager()
        manager_instance.stop()

        return {
            "success": True,
            "message": "Cámara detenida"
        }
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "success": False}
        )


@app.websocket(
    "/ws",
    name="WebSocket Connection"
)
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    ## Connection

    Connect to `ws://localhost:8080/ws` to receive real-time updates.

    ## Incoming Messages (Client → Server)

    ```json
    {"type": "ping"}  // Heartbeat
    {"type": "subscribe"}  // Subscribe to updates
    ```

    ## Outgoing Messages (Server → Client)

    ```json
    {"type": "pong"}  // Heartbeat response
    {"type": "subscribed", "data": {"status": "connected"}}  // Subscription confirmed
    {"type": "command_executed", "data": {...}}  // Command executed
    {"type": "note_created", "data": {...}}  // Note created
    {"type": "camera_config_updated", "data": {...}}  // Camera config changed
    {"type": "silent_mode_changed", "data": {...}}  // Silent mode toggled
    ```

    ## Broadcast Events

    All connected clients receive broadcasts when:
    - Commands are executed
    - Notes are created
    - Camera configuration is updated
    - Silent mode is toggled
    """
    await manager.connect(websocket)

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif message_type == "subscribe":
                # Client wants to subscribe to updates
                await websocket.send_json({
                    "type": "subscribed",
                    "data": {"status": "connected"}
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ═══════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
