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
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import logger first (always needed)
from utils.logger import get_logger
logger = get_logger(__name__)

# Import Terry components
try:
    from notes.voice_notes import get_notes_manager
    from memory.memory_manager import MemoryManager
    from macros.macro_recorder import get_macro_recorder
    from utils.silent_mode import is_silent
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
    print("   Version: 6.1.0")
    print("   Access: http://localhost:8080")
    yield
    # Shutdown
    print("👋 Terry Web UI shutting down...")


# ═══════════════════════════════════════════════════════════
# FASTAPI APP SETUP
# ═══════════════════════════════════════════════════════════

app = FastAPI(
    title="Terry Web UI",
    description="Professional web interface for Terry voice assistant",
    version="6.1.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


# ═══════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════

class CommandRequest(BaseModel):
    command: str
    language: str = "es"
    context: Optional[str] = None  # Historial de conversación para memoria


class NoteRequest(BaseModel):
    content: str
    category: Optional[str] = "general"
    priority: int = 0


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

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main UI page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/status")
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


@app.get("/api/stats")
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


@app.post("/api/command")
async def execute_command(request: CommandRequest):
    """Execute a voice command through Terry's processor."""
    try:
        # Import Terry's command processor components
        from llm.command_processor import CommandProcessor
        from llm.ollama_client import OllamaClient

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


@app.post("/api/silent-mode")
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


@app.get("/api/notes")
async def get_notes(limit: int = 10, category: Optional[str] = None):
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


@app.post("/api/notes")
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


@app.get("/api/macros")
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
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
