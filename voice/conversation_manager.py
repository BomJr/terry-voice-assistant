"""
Terry - Conversation Manager
Maneja ventanas de conversación para interacciones multi-turno sin wake word
"""

from enum import Enum
from typing import Optional
import time
import threading


class ConversationState(Enum):
    """Estados de la conversación."""
    IDLE = "idle"  # Sin conversación activa
    ACTIVE = "active"  # Conversación activa (esperando usuario)
    WINDOW = "window"  # Ventana de seguimiento activa
    EXPIRED = "expired"  # Ventana expirada


class ConversationManager:
    """
    Gestiona el estado de conversación para permitir múltiples turnos
    sin necesidad de wake word.

    Características:
    - Ventana de tiempo configurable (default 8s)
    - Extensión automática en cada interacción
    - Thread-safe
    - Callbacks para cambios de estado
    """

    def __init__(self, window_seconds: float = 8.0, auto_expire: bool = True):
        """
        Inicializa el gestor de conversación.

        Args:
            window_seconds: Duración de la ventana en segundos
            auto_expire: Si expirar automáticamente después de timeout
        """
        self.window_seconds = window_seconds
        self.auto_expire = auto_expire

        self._state = ConversationState.IDLE
        self._conversation_start: Optional[float] = None
        self._last_activity: Optional[float] = None
        self._lock = threading.Lock()
        self._expire_timer: Optional[threading.Timer] = None

    @property
    def state(self) -> ConversationState:
        """Estado actual de la conversación."""
        with self._lock:
            return self._state

    def start_conversation(self):
        """
        Inicia una nueva conversación o ventana de seguimiento.

        Llamar después de cada respuesta de TTS para permitir
        seguimiento sin wake word.
        """
        with self._lock:
            current_time = time.time()

            if self._state == ConversationState.IDLE:
                # Nueva conversación
                self._state = ConversationState.WINDOW
                self._conversation_start = current_time
            else:
                # Ya en conversación, pasar a ventana
                self._state = ConversationState.WINDOW

            self._last_activity = current_time

            # Cancelar timer anterior si existe
            if self._expire_timer:
                self._expire_timer.cancel()

            # Iniciar nuevo timer de expiración
            if self.auto_expire:
                self._expire_timer = threading.Timer(
                    self.window_seconds,
                    self._auto_expire
                )
                self._expire_timer.daemon = True
                self._expire_timer.start()

    def extend_window(self):
        """
        Extiende la ventana de conversación.

        Llamar cuando se recibe un nuevo comando del usuario
        para mantener la conversación activa.
        """
        with self._lock:
            if self._state in [ConversationState.WINDOW, ConversationState.ACTIVE]:
                current_time = time.time()
                self._last_activity = current_time
                self._state = ConversationState.WINDOW

                # Reiniciar timer
                if self._expire_timer:
                    self._expire_timer.cancel()

                if self.auto_expire:
                    self._expire_timer = threading.Timer(
                        self.window_seconds,
                        self._auto_expire
                    )
                    self._expire_timer.daemon = True
                    self._expire_timer.start()

    def expire_conversation(self):
        """
        Expira la conversación manualmente.

        Vuelve al estado IDLE y requiere wake word para nueva conversación.
        """
        with self._lock:
            self._state = ConversationState.IDLE
            self._conversation_start = None
            self._last_activity = None

            if self._expire_timer:
                self._expire_timer.cancel()
                self._expire_timer = None

    def is_in_conversation(self) -> bool:
        """
        Verifica si actualmente está en una conversación activa.

        Returns:
            True si está en ventana de conversación
        """
        with self._lock:
            if self._state not in [ConversationState.WINDOW, ConversationState.ACTIVE]:
                return False

            # Verificar si la ventana ha expirado
            if self._last_activity is None:
                return False

            elapsed = time.time() - self._last_activity
            if elapsed > self.window_seconds:
                # Expirado
                self._state = ConversationState.EXPIRED
                return False

            return True

    def get_remaining_time(self) -> float:
        """
        Obtiene el tiempo restante de la ventana.

        Returns:
            Segundos restantes, 0 si no hay conversación activa
        """
        with self._lock:
            if not self.is_in_conversation():
                return 0.0

            if self._last_activity is None:
                return 0.0

            elapsed = time.time() - self._last_activity
            remaining = max(0.0, self.window_seconds - elapsed)
            return remaining

    def get_conversation_duration(self) -> float:
        """
        Obtiene la duración total de la conversación actual.

        Returns:
            Segundos desde el inicio de la conversación, 0 si no hay activa
        """
        with self._lock:
            if self._conversation_start is None:
                return 0.0

            return time.time() - self._conversation_start

    def get_stats(self) -> dict:
        """
        Obtiene estadísticas de la conversación.

        Returns:
            Diccionario con estadísticas
        """
        with self._lock:
            return {
                "state": self._state.value,
                "in_conversation": self.is_in_conversation(),
                "remaining_time": self.get_remaining_time(),
                "conversation_duration": self.get_conversation_duration(),
                "window_seconds": self.window_seconds,
                "last_activity": self._last_activity,
            }

    def _auto_expire(self):
        """Callback interno para expiración automática."""
        with self._lock:
            if self._state in [ConversationState.WINDOW, ConversationState.ACTIVE]:
                # Verificar si realmente ha pasado el tiempo
                if self._last_activity:
                    elapsed = time.time() - self._last_activity
                    if elapsed >= self.window_seconds:
                        self._state = ConversationState.EXPIRED
                        # No limpiar completamente, permitir verificación

    def set_window_duration(self, seconds: float):
        """
        Ajusta la duración de la ventana.

        Args:
            seconds: Nueva duración en segundos
        """
        with self._lock:
            self.window_seconds = seconds

    def __repr__(self) -> str:
        """Representación en string."""
        return f"ConversationManager(state={self.state.value}, remaining={self.get_remaining_time():.1f}s)"
