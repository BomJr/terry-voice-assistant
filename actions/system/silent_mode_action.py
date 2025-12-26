"""
Silent Mode Action - Terry v6.1
Controla el modo silencioso (sin voz)
"""

from typing import Any, Dict
from actions.action_base import ActionBase, ActionResult
from utils.silent_mode import get_silent_mode
from utils.logger import get_logger

logger = get_logger(__name__)


class SilentModeAction(ActionBase):
    """Acción para controlar el modo silencioso."""

    def __init__(self):
        super().__init__(
            name="silent_mode",
            description="Activa o desactiva el modo silencioso (Terry responde solo visualmente, sin voz)",
            description_en="Enable or disable silent mode (Terry responds visually only, without voice)"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Ejecuta la acción de silent mode.

        Args:
            params: Parámetros con 'mode' = 'on'/'off'/'toggle'/'status'

        Returns:
            ActionResult con el resultado
        """
        mode_param = params.get('mode', 'toggle').lower()
        silent_mode = get_silent_mode()

        try:
            if mode_param in ['on', 'activar', 'enable', 'silencioso']:
                silent_mode.enable()
                return ActionResult(
                    success=True,
                    message="Modo silencioso activado. Terry solo responderá visualmente.",
                    data={'silent': True}
                )

            elif mode_param in ['off', 'desactivar', 'disable', 'normal']:
                silent_mode.disable()
                return ActionResult(
                    success=True,
                    message="Modo silencioso desactivado. Terry hablará normalmente.",
                    data={'silent': False}
                )

            elif mode_param in ['toggle', 'alternar', 'cambiar']:
                new_state = silent_mode.toggle()
                if new_state:
                    msg = "Modo silencioso activado"
                else:
                    msg = "Modo silencioso desactivado"

                return ActionResult(
                    success=True,
                    message=msg,
                    data={'silent': new_state}
                )

            elif mode_param in ['status', 'estado']:
                status = "activado" if silent_mode.is_silent else "desactivado"
                return ActionResult(
                    success=True,
                    message=f"Modo silencioso está {status}",
                    data={'silent': silent_mode.is_silent}
                )

            else:
                return ActionResult(
                    success=False,
                    message=f"Modo desconocido: {mode_param}. Usa: on/off/toggle/status"
                )

        except Exception as e:
            logger.error(f"Error en silent_mode action: {e}")
            return ActionResult(
                success=False,
                message=f"Error cambiando modo silencioso: {str(e)}"
            )
