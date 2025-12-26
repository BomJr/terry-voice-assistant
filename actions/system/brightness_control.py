"""
Home-Alexa - Brightness Control
Control de brillo de pantalla
"""

import subprocess
from typing import Dict, Any
from actions.action_base import ActionBase, ActionMetadata, ActionResult, ActionCategory, RiskLevel
from utils.logger import get_logger

logger = get_logger(__name__)


class BrightnessUpAction(ActionBase):
    """Sube el brillo de la pantalla."""

    metadata = ActionMetadata(
        name="brightness_up",
        description="Aumenta el brillo de la pantalla",
        description_en="Increase screen brightness",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["brillo", "más brillo", "sube brillo", "aumenta brillo"],
        keywords_en=["brightness", "brighter", "increase brightness"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Sube el brillo (tecla F2)."""
        try:
            # F2 = brightness up en macOS
            script = '''
                tell application "System Events"
                    key code 145
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Subiendo brillo",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en brightness_up: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class BrightnessDownAction(ActionBase):
    """Baja el brillo de la pantalla."""

    metadata = ActionMetadata(
        name="brightness_down",
        description="Disminuye el brillo de la pantalla",
        description_en="Decrease screen brightness",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["menos brillo", "baja brillo", "disminuye brillo", "oscurecer"],
        keywords_en=["less brightness", "decrease brightness", "dimmer"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Baja el brillo (tecla F1)."""
        try:
            # F1 = brightness down en macOS
            script = '''
                tell application "System Events"
                    key code 144
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Bajando brillo",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en brightness_down: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )
