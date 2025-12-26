"""
Home-Alexa - Session State
Mantiene el estado de la sesión actual (contexto, última app usada, etc.)
"""

import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from collections import deque
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CommandHistory:
    """Historial de un comando ejecutado."""
    timestamp: float
    user_input: str
    intent: str
    success: bool
    response: str


class SessionState:
    """
    Mantiene el estado de la sesión actual.

    Incluye:
    - Última app de música usada
    - Historial de comandos recientes
    - Contexto de conversación
    - Variables de sesión personalizadas
    """

    def __init__(self, max_history: int = 10):
        """
        Inicializa el estado de sesión.

        Args:
            max_history: Número máximo de comandos a recordar
        """
        self.max_history = max_history

        # Estado de aplicaciones
        self.last_music_app: Optional[str] = None
        self.last_browser: Optional[str] = None

        # Historial de comandos (FIFO)
        self.command_history: deque = deque(maxlen=max_history)

        # Contexto de conversación
        self.conversation_context: List[str] = []

        # Variables de sesión personalizadas
        self.variables: Dict[str, Any] = {}

        # Para gestos de voz (v6.0)
        self.last_response_text: Optional[str] = None
        self.last_command_text: Optional[str] = None
        self.action_in_progress: bool = False

        # Estadísticas de sesión
        self.session_start_time = time.time()
        self.total_commands = 0
        self.successful_commands = 0
        self.failed_commands = 0

    def record_command(
        self,
        user_input: str,
        intent: str,
        success: bool,
        response: str
    ):
        """
        Registra un comando ejecutado.

        Args:
            user_input: Texto del usuario
            intent: Intención detectada
            success: Si el comando tuvo éxito
            response: Respuesta generada
        """
        history_entry = CommandHistory(
            timestamp=time.time(),
            user_input=user_input,
            intent=intent,
            success=success,
            response=response
        )

        self.command_history.append(history_entry)
        self.total_commands += 1

        if success:
            self.successful_commands += 1
        else:
            self.failed_commands += 1

        # Guardar para gestos de voz (v6.0)
        self.last_command_text = user_input
        self.last_response_text = response

        # Actualizar contexto de conversación
        self.conversation_context.append(f"User: {user_input}")
        self.conversation_context.append(f"Assistant: {response}")

        # Mantener solo últimas 5 interacciones (10 líneas)
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]

        logger.debug(f"Comando registrado: {intent} - Success: {success}")

    def set_last_music_app(self, app_name: str):
        """
        Registra la última app de música usada.

        Args:
            app_name: Nombre de la app
        """
        self.last_music_app = app_name
        logger.debug(f"Última app de música: {app_name}")

    def get_last_music_app(self) -> Optional[str]:
        """Obtiene la última app de música usada."""
        return self.last_music_app

    def set_last_browser(self, browser_name: str):
        """
        Registra el último navegador usado.

        Args:
            browser_name: Nombre del navegador
        """
        self.last_browser = browser_name
        logger.debug(f"Último navegador: {browser_name}")

    def get_last_browser(self) -> Optional[str]:
        """Obtiene el último navegador usado."""
        return self.last_browser

    def get_conversation_context(self) -> str:
        """
        Obtiene el contexto de conversación para el LLM.

        Returns:
            String con el contexto reciente
        """
        if not self.conversation_context:
            return ""

        return "\n".join(self.conversation_context)

    def get_recent_commands(self, limit: int = 5) -> List[CommandHistory]:
        """
        Obtiene los comandos recientes.

        Args:
            limit: Número máximo de comandos a retornar

        Returns:
            Lista de comandos recientes
        """
        return list(self.command_history)[-limit:]

    def set_variable(self, key: str, value: Any):
        """
        Establece una variable de sesión.

        Args:
            key: Nombre de la variable
            value: Valor a guardar
        """
        self.variables[key] = value
        logger.debug(f"Variable '{key}' establecida")

    def get_variable(self, key: str, default: Any = None) -> Any:
        """
        Obtiene una variable de sesión.

        Args:
            key: Nombre de la variable
            default: Valor por defecto si no existe

        Returns:
            Valor de la variable o default
        """
        return self.variables.get(key, default)

    def clear_context(self):
        """Limpia el contexto de conversación."""
        self.conversation_context.clear()
        logger.info("Contexto de conversación limpiado")

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la sesión.

        Returns:
            Diccionario con estadísticas
        """
        session_duration = time.time() - self.session_start_time
        success_rate = (
            (self.successful_commands / self.total_commands * 100)
            if self.total_commands > 0
            else 0
        )

        return {
            "session_duration": f"{session_duration:.0f}s",
            "total_commands": self.total_commands,
            "successful": self.successful_commands,
            "failed": self.failed_commands,
            "success_rate": f"{success_rate:.1f}%",
            "last_music_app": self.last_music_app or "Ninguna",
            "last_browser": self.last_browser or "Ninguno",
        }

    def print_stats(self):
        """Imprime estadísticas de la sesión."""
        stats = self.get_stats()

        print("\n📊 ESTADÍSTICAS DE LA SESIÓN")
        print("=" * 50)
        print(f"  Duración: {stats['session_duration']}")
        print(f"  Comandos totales: {stats['total_commands']}")
        print(f"  Exitosos: {stats['successful']}")
        print(f"  Fallidos: {stats['failed']}")
        print(f"  Tasa de éxito: {stats['success_rate']}")
        print(f"  Última app música: {stats['last_music_app']}")
        print(f"  Último navegador: {stats['last_browser']}")
        print("=" * 50)

    def reset(self):
        """Reinicia el estado de sesión."""
        self.__init__(max_history=self.max_history)
        logger.info("Estado de sesión reiniciado")


# Instancia global
_session_instance: Optional[SessionState] = None


def get_session() -> SessionState:
    """Obtiene la instancia global de sesión."""
    global _session_instance
    if _session_instance is None:
        _session_instance = SessionState()
    return _session_instance


def reset_session():
    """Reinicia la sesión global."""
    global _session_instance
    if _session_instance:
        _session_instance.reset()
    else:
        _session_instance = SessionState()
