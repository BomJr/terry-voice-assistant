"""
Silent Mode Manager - Terry v6.1
Controla el modo silencioso (sin voz, solo visual)
"""

import json
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


class SilentMode:
    """Administrador de modo silencioso."""

    CONFIG_FILE = Path.home() / ".terry_silent_mode"

    def __init__(self):
        """Inicializa el modo silencioso."""
        self._silent = self._load_state()

    def _load_state(self) -> bool:
        """Carga el estado persistente."""
        try:
            if self.CONFIG_FILE.exists():
                with open(self.CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('silent', False)
        except:
            pass
        return False

    def _save_state(self):
        """Guarda el estado persistente."""
        try:
            with open(self.CONFIG_FILE, 'w') as f:
                json.dump({'silent': self._silent}, f)
        except Exception as e:
            logger.error(f"Error saving silent mode state: {e}")

    @property
    def is_silent(self) -> bool:
        """Retorna True si está en modo silencioso."""
        return self._silent

    def enable(self):
        """Activa modo silencioso."""
        self._silent = True
        self._save_state()
        logger.info("🔇 Modo silencioso ACTIVADO")

    def disable(self):
        """Desactiva modo silencioso."""
        self._silent = False
        self._save_state()
        logger.info("🔊 Modo silencioso DESACTIVADO")

    def toggle(self) -> bool:
        """Alterna modo silencioso."""
        if self._silent:
            self.disable()
        else:
            self.enable()
        return self._silent

    def status(self) -> str:
        """Retorna el estado actual como texto."""
        return "silencioso" if self._silent else "normal"


# Instancia global
_silent_mode = SilentMode()


def get_silent_mode() -> SilentMode:
    """Obtiene la instancia global de silent mode."""
    return _silent_mode


def is_silent() -> bool:
    """Shortcut para verificar si está en modo silencioso."""
    return _silent_mode.is_silent
