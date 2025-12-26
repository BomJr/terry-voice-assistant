"""
Terry - Terminal LED Feedback
Visual state indicator in terminal using Rich library
"""

from rich.console import Console
from rich.text import Text
from enum import Enum
from typing import Optional
import threading
import time


class LEDState(Enum):
    """Estados del LED visual."""
    IDLE = ("⚪", "white", "Esperando wake word")
    LISTENING = ("🔵", "blue", "Escuchando...")
    PROCESSING = ("🟡", "yellow", "Procesando...")
    RESPONDING = ("🟢", "green", "Respondiendo...")
    ERROR = ("🔴", "red", "Error")
    CONVERSATION = ("💬", "cyan", "En conversación")


class TerminalLED:
    """
    LED visual en terminal para mostrar el estado de Terry.
    Utiliza Rich library para renderizar con colores y emojis.
    """

    def __init__(self, enabled: bool = True, pulse_enabled: bool = True):
        """
        Inicializa el LED terminal.

        Args:
            enabled: Si está habilitado el LED
            pulse_enabled: Si habilitar animación de pulsado
        """
        self.console = Console()
        self.enabled = enabled
        self.pulse_enabled = pulse_enabled
        self.current_state = LEDState.IDLE
        self._pulse_thread: Optional[threading.Thread] = None
        self._pulse_running = False
        self._lock = threading.Lock()

    def set_state(self, state: LEDState, pulse: bool = False):
        """
        Establece el estado del LED.

        Args:
            state: Nuevo estado
            pulse: Si aplicar animación de pulsado
        """
        if not self.enabled:
            return

        with self._lock:
            # Detener pulsado anterior si existe
            self._stop_pulse()

            self.current_state = state

            # Renderizar estado
            if pulse and self.pulse_enabled:
                self._start_pulse()
            else:
                self._render()

    def _render(self, brightness: float = 1.0):
        """
        Renderiza el LED en la terminal.

        Args:
            brightness: Nivel de brillo (0.0 a 1.0) para animación
        """
        if not self.enabled:
            return

        emoji, color, text = self.current_state.value

        # Crear texto con estilo
        led_text = Text()
        led_text.append(emoji, style=f"bold {color}")
        led_text.append(f" {text}", style=f"{color}")

        # Renderizar en la terminal - SIN end="" para evitar saturación
        self.console.print(f"\r{' ' * 100}\r", end="")  # Clear line completamente
        self.console.print(led_text)

    def _start_pulse(self):
        """Inicia animación de pulsado."""
        if not self.pulse_enabled:
            return

        self._pulse_running = True
        self._pulse_thread = threading.Thread(target=self._pulse_loop, daemon=True)
        self._pulse_thread.start()

    def _stop_pulse(self):
        """Detiene animación de pulsado."""
        if self._pulse_thread and self._pulse_running:
            self._pulse_running = False
            # No esperamos al thread, es daemon

    def _pulse_loop(self):
        """Loop de animación de pulsado."""
        while self._pulse_running:
            # Pulsado: 1.0 → 0.3 → 1.0
            for brightness in [1.0, 0.8, 0.6, 0.4, 0.6, 0.8]:
                if not self._pulse_running:
                    break
                with self._lock:
                    self._render(brightness)
                time.sleep(0.15)

    def clear(self):
        """Limpia el LED de la terminal."""
        if not self.enabled:
            return

        self.console.print("\r" + " " * 80 + "\r", end="")

    def newline(self):
        """Imprime nueva línea (útil después de comandos)."""
        if not self.enabled:
            return

        self.console.print()

    def stop(self):
        """Detiene el LED y limpia."""
        self._stop_pulse()
        self.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False
