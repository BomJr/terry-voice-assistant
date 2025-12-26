"""
Home-Alexa - State Machine
Máquina de estados finitos para controlar el flujo del asistente
"""

from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Set
from dataclasses import dataclass
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


class State(Enum):
    """Estados posibles del asistente."""
    IDLE = auto()           # Esperando wake word
    WAKE_DETECTED = auto()  # Wake word detectado, capturando comando
    LISTENING = auto()      # Procesando STT
    PROCESSING = auto()     # Procesando con LLM
    EXECUTING = auto()      # Ejecutando acciones
    SPEAKING = auto()       # Reproduciendo respuesta TTS
    CONFIRMING = auto()     # Esperando confirmación del usuario
    ERROR = auto()          # Estado de error


@dataclass
class StateTransition:
    """Representa una transición de estado."""
    from_state: State
    to_state: State
    timestamp: datetime
    reason: Optional[str] = None


# Tipo para callbacks de transición
TransitionCallback = Callable[[State, State], None]


class StateMachine:
    """
    Máquina de estados finitos del asistente.

    Estados y transiciones permitidas:
        IDLE → WAKE_DETECTED (wake word detectado)
        WAKE_DETECTED → LISTENING (captura completada)
        LISTENING → PROCESSING (transcripción completada)
        PROCESSING → EXECUTING (respuesta del LLM recibida)
        PROCESSING → CONFIRMING (acción requiere confirmación)
        CONFIRMING → EXECUTING (confirmación recibida)
        CONFIRMING → IDLE (confirmación rechazada)
        EXECUTING → SPEAKING (acciones completadas)
        SPEAKING → IDLE (respuesta reproducida)
        * → ERROR (cualquier error)
        ERROR → IDLE (recuperación)
    """

    # Definición de transiciones válidas
    VALID_TRANSITIONS: Dict[State, Set[State]] = {
        State.IDLE: {State.WAKE_DETECTED, State.ERROR},
        State.WAKE_DETECTED: {State.LISTENING, State.IDLE, State.ERROR},
        State.LISTENING: {State.PROCESSING, State.IDLE, State.ERROR},
        State.PROCESSING: {State.EXECUTING, State.CONFIRMING, State.SPEAKING, State.IDLE, State.ERROR},
        State.CONFIRMING: {State.EXECUTING, State.IDLE, State.ERROR},
        State.EXECUTING: {State.SPEAKING, State.IDLE, State.ERROR},
        State.SPEAKING: {State.IDLE, State.ERROR},
        State.ERROR: {State.IDLE},
    }

    def __init__(self, initial_state: State = State.IDLE):
        self._current_state = initial_state
        self._previous_state: Optional[State] = None
        self._history: List[StateTransition] = []
        self._on_enter_callbacks: Dict[State, List[TransitionCallback]] = {}
        self._on_exit_callbacks: Dict[State, List[TransitionCallback]] = {}
        self._on_any_transition: List[TransitionCallback] = []

        logger.info(f"StateMachine inicializada en estado: {initial_state.name}")

    @property
    def current_state(self) -> State:
        """Retorna el estado actual."""
        return self._current_state

    @property
    def previous_state(self) -> Optional[State]:
        """Retorna el estado anterior."""
        return self._previous_state

    @property
    def is_idle(self) -> bool:
        """Verifica si está en estado IDLE."""
        return self._current_state == State.IDLE

    @property
    def is_busy(self) -> bool:
        """Verifica si está procesando algo (no IDLE ni ERROR)."""
        return self._current_state not in (State.IDLE, State.ERROR)

    def can_transition(self, to_state: State) -> bool:
        """
        Verifica si una transición es válida.

        Args:
            to_state: Estado destino

        Returns:
            True si la transición es válida
        """
        valid_targets = self.VALID_TRANSITIONS.get(self._current_state, set())
        return to_state in valid_targets

    def transition(self, to_state: State, reason: Optional[str] = None) -> bool:
        """
        Realiza una transición de estado.

        Args:
            to_state: Estado destino
            reason: Razón opcional de la transición

        Returns:
            True si la transición fue exitosa
        """
        if not self.can_transition(to_state):
            logger.warning(
                f"Transición inválida: {self._current_state.name} → {to_state.name}"
            )
            return False

        from_state = self._current_state
        self._previous_state = from_state
        self._current_state = to_state

        # Registrar en historial
        transition = StateTransition(
            from_state=from_state,
            to_state=to_state,
            timestamp=datetime.now(),
            reason=reason
        )
        self._history.append(transition)

        # Mantener historial limitado
        if len(self._history) > 100:
            self._history = self._history[-50:]

        logger.info(f"Estado: {from_state.name} → {to_state.name}" +
                    (f" ({reason})" if reason else ""))

        # Ejecutar callbacks
        self._execute_callbacks(from_state, to_state)

        return True

    def force_state(self, state: State, reason: Optional[str] = None) -> None:
        """
        Fuerza un cambio de estado sin validar transiciones.
        Usar solo para recuperación de errores.

        Args:
            state: Estado destino
            reason: Razón del cambio forzado
        """
        from_state = self._current_state
        self._previous_state = from_state
        self._current_state = state

        logger.warning(f"Estado forzado: {from_state.name} → {state.name}" +
                       (f" ({reason})" if reason else ""))

        self._execute_callbacks(from_state, state)

    def reset(self) -> None:
        """Reinicia la máquina de estados a IDLE."""
        self.force_state(State.IDLE, "reset")

    def on_enter(self, state: State, callback: TransitionCallback) -> None:
        """
        Registra un callback para cuando se entra a un estado.

        Args:
            state: Estado a observar
            callback: Función a ejecutar (recibe from_state, to_state)
        """
        if state not in self._on_enter_callbacks:
            self._on_enter_callbacks[state] = []
        self._on_enter_callbacks[state].append(callback)

    def on_exit(self, state: State, callback: TransitionCallback) -> None:
        """
        Registra un callback para cuando se sale de un estado.

        Args:
            state: Estado a observar
            callback: Función a ejecutar (recibe from_state, to_state)
        """
        if state not in self._on_exit_callbacks:
            self._on_exit_callbacks[state] = []
        self._on_exit_callbacks[state].append(callback)

    def on_transition(self, callback: TransitionCallback) -> None:
        """
        Registra un callback para cualquier transición.

        Args:
            callback: Función a ejecutar (recibe from_state, to_state)
        """
        self._on_any_transition.append(callback)

    def _execute_callbacks(self, from_state: State, to_state: State) -> None:
        """Ejecuta los callbacks registrados."""
        # Callbacks de salida del estado anterior
        for callback in self._on_exit_callbacks.get(from_state, []):
            try:
                callback(from_state, to_state)
            except Exception as e:
                logger.error(f"Error en callback on_exit({from_state.name}): {e}")

        # Callbacks de entrada al nuevo estado
        for callback in self._on_enter_callbacks.get(to_state, []):
            try:
                callback(from_state, to_state)
            except Exception as e:
                logger.error(f"Error en callback on_enter({to_state.name}): {e}")

        # Callbacks de cualquier transición
        for callback in self._on_any_transition:
            try:
                callback(from_state, to_state)
            except Exception as e:
                logger.error(f"Error en callback on_transition: {e}")

    def get_history(self, limit: int = 10) -> List[StateTransition]:
        """
        Retorna el historial de transiciones.

        Args:
            limit: Número máximo de transiciones a retornar

        Returns:
            Lista de transiciones recientes
        """
        return self._history[-limit:]

    def get_state_duration(self) -> float:
        """
        Retorna cuánto tiempo lleva en el estado actual (segundos).

        Returns:
            Segundos en el estado actual
        """
        if not self._history:
            return 0.0

        last_transition = self._history[-1]
        return (datetime.now() - last_transition.timestamp).total_seconds()

    def __str__(self) -> str:
        return f"StateMachine(state={self._current_state.name})"

    def __repr__(self) -> str:
        return self.__str__()
