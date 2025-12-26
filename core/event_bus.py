"""
Home-Alexa - Event Bus
Sistema Pub/Sub asíncrono para comunicación desacoplada entre módulos
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Coroutine
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Event:
    """Representa un evento en el sistema."""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    source: Optional[str] = None

    def __str__(self):
        return f"Event({self.type}, data={self.data})"


# Tipo para handlers de eventos
EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """
    Bus de eventos asíncrono para comunicación entre módulos.

    Ejemplo de uso:
        bus = EventBus()

        async def handler(event):
            print(f"Received: {event}")

        bus.subscribe("user_input", handler)
        await bus.emit(Event(type="user_input", data={"text": "hello"}))
    """

    _instance: Optional['EventBus'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._processor_task: Optional[asyncio.Task] = None
        self._initialized = True

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Suscribe un handler a un tipo de evento.

        Args:
            event_type: Tipo de evento a escuchar
            handler: Función async que procesa el evento
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.debug(f"Handler suscrito a '{event_type}'")

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Desuscribe un handler de un tipo de evento.

        Args:
            event_type: Tipo de evento
            handler: Handler a remover
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Handler desuscrito de '{event_type}'")
            except ValueError:
                pass

    def subscribe_all(self, handler: EventHandler) -> None:
        """
        Suscribe un handler a todos los eventos.

        Args:
            handler: Handler que recibirá todos los eventos
        """
        self.subscribe("*", handler)

    async def emit(self, event: Event) -> None:
        """
        Emite un evento a todos los handlers suscritos.

        Args:
            event: Evento a emitir
        """
        logger.debug(f"Emitiendo evento: {event.type}")

        # Handlers específicos para este tipo de evento
        handlers = self._subscribers.get(event.type, [])

        # Handlers globales (*) que escuchan todos los eventos
        global_handlers = self._subscribers.get("*", [])

        all_handlers = handlers + global_handlers

        if not all_handlers:
            logger.debug(f"No hay handlers para evento '{event.type}'")
            return

        # Ejecutar handlers en paralelo
        tasks = [self._safe_call(handler, event) for handler in all_handlers]
        await asyncio.gather(*tasks)

    async def emit_queued(self, event: Event) -> None:
        """
        Encola un evento para procesamiento asíncrono.

        Args:
            event: Evento a encolar
        """
        await self._event_queue.put(event)

    async def _safe_call(self, handler: EventHandler, event: Event) -> None:
        """Ejecuta un handler de forma segura, capturando errores."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error en handler para '{event.type}': {e}")

    async def start_processor(self) -> None:
        """Inicia el procesador de cola de eventos."""
        if self._running:
            return

        self._running = True
        self._processor_task = asyncio.create_task(self._process_queue())
        logger.info("Procesador de eventos iniciado")

    async def _process_queue(self) -> None:
        """Procesa eventos de la cola."""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                await self.emit(event)
                self._event_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error procesando cola de eventos: {e}")

    async def stop_processor(self) -> None:
        """Detiene el procesador de cola de eventos."""
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass
        logger.info("Procesador de eventos detenido")

    def clear(self) -> None:
        """Limpia todos los suscriptores."""
        self._subscribers.clear()
        logger.debug("Todos los suscriptores eliminados")

    @property
    def event_types(self) -> List[str]:
        """Retorna la lista de tipos de eventos con suscriptores."""
        return list(self._subscribers.keys())


# Tipos de eventos estándar del sistema
class EventTypes:
    """Constantes para tipos de eventos del sistema."""

    # Audio
    AUDIO_CHUNK = "audio_chunk"
    AUDIO_STARTED = "audio_started"
    AUDIO_STOPPED = "audio_stopped"

    # Wake Word
    WAKE_DETECTED = "wake_detected"
    WAKE_TIMEOUT = "wake_timeout"

    # STT
    TRANSCRIPTION_STARTED = "transcription_started"
    TRANSCRIPTION_COMPLETE = "transcription_complete"
    TRANSCRIPTION_ERROR = "transcription_error"

    # LLM
    LLM_PROCESSING = "llm_processing"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"

    # TTS
    TTS_STARTED = "tts_started"
    TTS_COMPLETE = "tts_complete"
    TTS_ERROR = "tts_error"

    # Actions
    ACTION_STARTED = "action_started"
    ACTION_COMPLETE = "action_complete"
    ACTION_ERROR = "action_error"
    CONFIRMATION_REQUIRED = "confirmation_required"
    CONFIRMATION_RECEIVED = "confirmation_received"

    # State
    STATE_CHANGED = "state_changed"

    # System
    SYSTEM_READY = "system_ready"
    SYSTEM_SHUTDOWN = "system_shutdown"
    SYSTEM_ERROR = "system_error"
