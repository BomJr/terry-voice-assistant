"""
Home-Alexa - Window Control Actions
Control de ventanas (minimizar, maximizar, cerrar, etc.)
"""

import subprocess
from typing import Dict, Any
from actions.action_base import ActionBase, ActionMetadata, ActionResult, ActionCategory, RiskLevel
from utils.logger import get_logger

logger = get_logger(__name__)


class MinimizeWindowAction(ActionBase):
    """Minimiza la ventana actual."""

    metadata = ActionMetadata(
        name="minimize_window",
        description="Minimiza la ventana activa",
        description_en="Minimize active window",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["minimizar", "minimiza", "ocultar ventana"],
        keywords_en=["minimize", "hide window"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Minimiza la ventana actual."""
        try:
            script = '''
                tell application "System Events"
                    tell (first application process whose frontmost is true)
                        set miniaturized of front window to true
                    end tell
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Ventana minimizada",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en minimize_window: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class MaximizeWindowAction(ActionBase):
    """Maximiza/pantalla completa la ventana actual."""

    metadata = ActionMetadata(
        name="maximize_window",
        description="Maximiza la ventana activa",
        description_en="Maximize active window",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["maximizar", "pantalla completa", "fullscreen"],
        keywords_en=["maximize", "fullscreen"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Maximiza la ventana (Cmd+Ctrl+F)."""
        try:
            # macOS: Cmd+Ctrl+F para fullscreen
            script = '''
                tell application "System Events"
                    keystroke "f" using {control down, command down}
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Pantalla completa activada/desactivada",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en maximize_window: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class CloseWindowAction(ActionBase):
    """Cierra la ventana actual."""

    metadata = ActionMetadata(
        name="close_window",
        description="Cierra la ventana activa",
        description_en="Close active window",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.MODERATE,  # Puede cerrar trabajo sin guardar
        keywords_es=["cerrar ventana", "cierra ventana"],
        keywords_en=["close window"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Cierra la ventana actual (Cmd+W)."""
        try:
            script = '''
                tell application "System Events"
                    keystroke "w" using {command down}
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Ventana cerrada",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en close_window: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class SwitchWindowAction(ActionBase):
    """Cambiar entre ventanas (Cmd+Tab)."""

    metadata = ActionMetadata(
        name="switch_window",
        description="Cambia entre ventanas/aplicaciones",
        description_en="Switch between windows/apps",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["cambiar ventana", "siguiente ventana", "app siguiente"],
        keywords_en=["switch window", "next window", "next app"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Cambia a la siguiente ventana/app."""
        try:
            script = '''
                tell application "System Events"
                    keystroke tab using {command down}
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Cambiando ventana",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en switch_window: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )
