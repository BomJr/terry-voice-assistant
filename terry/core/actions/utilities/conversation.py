"""
Home-Alexa - Conversation Actions
Acciones para respuestas conversacionales
"""

from typing import Dict, Any

from terry.core.actions.base import (
    ActionBase, ActionResult, ActionMetadata,
    ActionCategory, RiskLevel
)
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class NoAction(ActionBase):
    """Respuesta conversacional sin acción."""

    metadata = ActionMetadata(
        name="no_action",
        description="Respuesta conversacional",
        description_en="Conversational response",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["hola", "gracias", "adiós"],
        keywords_en=["hello", "thanks", "goodbye"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        # No hace nada, solo permite que el asistente responda
        return ActionResult(
            success=True,
            message="",
            data={}
        )
