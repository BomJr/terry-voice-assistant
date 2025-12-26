"""
Home-Alexa - Volume Control Actions
Acciones para control de volumen en macOS
"""

from typing import Dict, Any

from terry.core.actions.base import (
    ActionBase, ActionResult, ActionMetadata,
    ActionCategory, RiskLevel
)
from terry.core.utils.applescript_runner import run_applescript_sync, AppleScripts
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class VolumeSetAction(ActionBase):
    """Establece el volumen a un nivel específico."""

    metadata = ActionMetadata(
        name="volume_set",
        description="Establece el volumen a un nivel específico (0-100)",
        description_en="Sets volume to a specific level (0-100)",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["volumen", "nivel", "establecer", "poner"],
        keywords_en=["volume", "level", "set"],
        required_params=["level"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        level = params.get("level", 50)

        # Validar rango
        try:
            level = int(level)
            level = max(0, min(100, level))
        except (ValueError, TypeError):
            return ActionResult(
                success=False,
                message="Nivel de volumen inválido",
                error="INVALID_LEVEL"
            )

        script = AppleScripts.set_volume(level)
        success, output, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message=f"Volumen establecido a {level}%",
                data={"level": level}
            )
        else:
            return ActionResult(
                success=False,
                message="Error ajustando volumen",
                error=error
            )


class VolumeUpAction(ActionBase):
    """Sube el volumen."""

    metadata = ActionMetadata(
        name="volume_up",
        description="Sube el volumen",
        description_en="Increases the volume",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["subir", "aumentar", "más", "alto"],
        keywords_en=["up", "increase", "raise", "louder"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        amount = params.get("amount", 10)

        # Obtener volumen actual
        success, output, _ = run_applescript_sync(AppleScripts.get_volume())

        try:
            current = int(output) if success and output else 50
        except ValueError:
            current = 50

        new_level = min(100, current + amount)
        script = AppleScripts.set_volume(new_level)
        success, _, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message=f"Volumen subido a {new_level}%",
                data={"level": new_level}
            )
        else:
            return ActionResult(
                success=False,
                message="Error subiendo volumen",
                error=error
            )


class VolumeDownAction(ActionBase):
    """Baja el volumen."""

    metadata = ActionMetadata(
        name="volume_down",
        description="Baja el volumen",
        description_en="Decreases the volume",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["bajar", "reducir", "menos", "bajo"],
        keywords_en=["down", "decrease", "lower", "quieter"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        amount = params.get("amount", 10)

        # Obtener volumen actual
        success, output, _ = run_applescript_sync(AppleScripts.get_volume())

        try:
            current = int(output) if success and output else 50
        except ValueError:
            current = 50

        new_level = max(0, current - amount)
        script = AppleScripts.set_volume(new_level)
        success, _, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message=f"Volumen bajado a {new_level}%",
                data={"level": new_level}
            )
        else:
            return ActionResult(
                success=False,
                message="Error bajando volumen",
                error=error
            )


class VolumeMuteAction(ActionBase):
    """Silencia o activa el volumen."""

    metadata = ActionMetadata(
        name="volume_mute",
        description="Silencia o activa el volumen",
        description_en="Mutes or unmutes the volume",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["silenciar", "mute", "silencio", "callar"],
        keywords_en=["mute", "silence", "quiet", "unmute"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        # Toggle mute
        script = AppleScripts.toggle_mute()
        success, _, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message="Silencio alternado",
                data={}
            )
        else:
            return ActionResult(
                success=False,
                message="Error alternando silencio",
                error=error
            )
