"""
REST API - Terry v6.1
HTTP API for remote Terry control
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
from utils.logger import get_logger

logger = get_logger(__name__)


# Request/Response models
class CommandRequest(BaseModel):
    """Command execution request."""
    command: str
    language: Optional[str] = "es"


class CommandResponse(BaseModel):
    """Command execution response."""
    success: bool
    response: str
    data: Optional[Dict[str, Any]] = None


class StatusResponse(BaseModel):
    """API status response."""
    status: str
    version: str
    features: List[str]


class TerryAPI:
    """REST API for Terry control."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765,
                 allow_remote: bool = False):
        """
        Initialize Terry API.

        Args:
            host: Host to bind to
            port: Port to bind to
            allow_remote: Allow remote connections (security risk!)
        """
        self.host = host if not allow_remote else "0.0.0.0"
        self.port = port
        self.allow_remote = allow_remote

        # Create FastAPI app
        self.app = FastAPI(
            title="Terry API",
            description="Voice Assistant Remote Control API",
            version="6.1.0"
        )

        # CORS middleware
        if allow_remote:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # Command executor (set externally)
        self.command_executor = None

        # Register routes
        self._register_routes()

        logger.info(f"Terry API initialized on {self.host}:{self.port}")

    def set_command_executor(self, executor):
        """
        Set command executor function.

        Args:
            executor: Async function that executes commands
        """
        self.command_executor = executor
        logger.debug("Command executor set for API")

    def _register_routes(self):
        """Register API routes."""

        @self.app.get("/", response_model=StatusResponse)
        async def root():
            """API root - status and version."""
            return StatusResponse(
                status="running",
                version="6.1.0",
                features=[
                    "voice_commands",
                    "memory",
                    "patterns",
                    "context",
                    "suggestions",
                    "camera_vision",
                    "ocr",
                    "scheduler",
                    "triggers",
                    "macros",
                    "dictation",
                    "file_search",
                    "ide_control"
                ]
            )

        @self.app.post("/command", response_model=CommandResponse)
        async def execute_command(request: CommandRequest):
            """Execute a voice command."""
            if not self.command_executor:
                raise HTTPException(status_code=500, detail="Command executor not configured")

            try:
                # Execute command
                response = await self.command_executor(request.command)

                return CommandResponse(
                    success=True,
                    response=response,
                    data={"language": request.language}
                )

            except Exception as e:
                logger.error(f"API command error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/health")
        async def health():
            """Health check endpoint."""
            return {"status": "healthy"}

        @self.app.post("/silent-mode")
        async def toggle_silent():
            """Toggle silent mode."""
            try:
                from utils.silent_mode import toggle_silent as toggle
                state = toggle()
                return {"silent_mode": state, "message": "Modo silencioso activado" if state else "Modo silencioso desactivado"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/memory/stats")
        async def memory_stats():
            """Get memory statistics."""
            try:
                from memory.memory_manager import MemoryManager
                memory = MemoryManager()
                stats = memory.get_stats()
                return stats
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/patterns")
        async def get_patterns():
            """Get learned patterns."""
            try:
                from memory.pattern_learner import get_pattern_learner
                learner = get_pattern_learner()
                patterns = learner.patterns
                return patterns
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    async def start(self):
        """Start the API server."""
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)

        logger.info(f"Starting Terry API on {self.host}:{self.port}")

        if self.allow_remote:
            logger.warning("⚠️ API allows remote connections - security risk!")

        await server.serve()


# Singleton instance
_api: Optional[TerryAPI] = None


def get_api() -> TerryAPI:
    """
    Get the singleton TerryAPI instance.

    Returns:
        TerryAPI instance
    """
    global _api

    if _api is None:
        try:
            from config.settings import settings
            config = settings.get("rest_api", {})

            host = config.get("host", "127.0.0.1")
            port = config.get("port", 8765)
            allow_remote = config.get("allow_remote", False)

            _api = TerryAPI(
                host=host,
                port=port,
                allow_remote=allow_remote
            )

        except Exception as e:
            logger.warning(f"Could not load API settings: {e}")
            _api = TerryAPI()

    return _api
