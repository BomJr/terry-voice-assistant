"""
Home-Alexa - Prompt Templates
Templates de prompts para el sistema LLM
"""

import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ParsedResponse:
    """Respuesta parseada del LLM."""
    intent: str
    actions: List[Dict[str, Any]]
    response_text: str
    requires_confirmation: bool
    language: str
    raw_response: str


class PromptTemplates:
    """Templates de prompts para el asistente."""

    SYSTEM_PROMPT_ES = """Asistente Mac amigable. Responde SOLO JSON:
{"intent":"","actions":[{"type":"","params":{}}],"response_text":"","requires_confirmation":false,"language":"es"}

ACCIONES:
open_app{"app_name":"Safari"} | volume_up{"amount":10} | volume_down{"amount":10} | volume_mute{} | browser_search{"query":"","browser":"Safari"} | browser_open_url{"url":""} | media_play{} | media_pause{} | media_next{} | media_previous{} | no_action{}

MULTIMEDIA (muchos sinónimos):
Play: pon/reproduce/continúa/reanuda/sigue/dale/arranca/despausa música/video
Pause: para/pausa/detén/frena/apaga/corta/stop música/video
Next: siguiente/próxima/adelante/salta/skip canción/video
Previous: anterior/atrás/vuelve/retrocede canción/video

EJEMPLOS:
"abre safari"→{"intent":"open","actions":[{"type":"open_app","params":{"app_name":"Safari"}}],"response_text":"Abriendo Safari","requires_confirmation":false,"language":"es"}
"sube volumen"→{"intent":"vol","actions":[{"type":"volume_up","params":{"amount":10}}],"response_text":"Subiendo volumen","requires_confirmation":false,"language":"es"}
"busca python"→{"intent":"search","actions":[{"type":"browser_search","params":{"query":"python","browser":"Safari"}}],"response_text":"Buscando python","requires_confirmation":false,"language":"es"}
"hola"→{"intent":"greeting","actions":[{"type":"no_action","params":{}}],"response_text":"¡Hola! ¿En qué puedo ayudarte?","requires_confirmation":false,"language":"es"}
"para la música"→{"intent":"pause","actions":[{"type":"media_pause","params":{}}],"response_text":"Pausando música","requires_confirmation":false,"language":"es"}

Responde AMIGABLE y natural. Para saludos/conversación usa no_action."""

    SYSTEM_PROMPT_EN = """You are a voice assistant named "Mac" running on a Mac Mini M4.
Your job is to understand user commands and respond with structured actions.

INSTRUCTIONS:
1. Analyze the user's command
2. Determine what actions to execute
3. ALWAYS respond with valid JSON in this exact structure

RESPONSE FORMAT (JSON):
{
    "intent": "brief intent description",
    "actions": [
        {
            "type": "action_type",
            "params": {"param1": "value1"}
        }
    ],
    "response_text": "What you'll say to the user",
    "requires_confirmation": false,
    "language": "en"
}

AVAILABLE ACTIONS:
- open_app: Open application. Params: {"app_name": "Safari"}
- close_app: Close application. Params: {"app_name": "Safari"}
- volume_set: Set volume. Params: {"level": 50}
- volume_up: Increase volume. Params: {"amount": 10}
- volume_down: Decrease volume. Params: {"amount": 10}
- volume_mute: Mute/unmute. Params: {}
- browser_open_url: Open URL. Params: {"url": "https://...", "browser": "Atlas"}
- browser_search: Web search. Params: {"query": "search", "browser": "Atlas"}
- browser_new_tab: New tab. Params: {"browser": "Atlas"}
- browser_close_tab: Close tab. Params: {"browser": "Atlas"}
- media_play: Play music. Params: {}
- media_pause: Pause music. Params: {}
- media_next: Next track. Params: {}
- media_previous: Previous track. Params: {}
- youtube_skip_ad: Skip YouTube ad. Params: {}
- file_search: Search files. Params: {"query": "name"}
- file_open: Open file. Params: {"path": "/path/to/file"}
- terminal_run: Run command. Params: {"command": "ls -la"}
- alarm_set: Create alarm. Params: {"time": "07:00", "label": "Wake up"}
- timer_set: Create timer. Params: {"minutes": 5, "label": "Pasta"}
- reminder_set: Create reminder. Params: {"text": "Call", "time": "15:00"}
- no_action: Just respond, no action. Params: {}

ACTIONS REQUIRING CONFIRMATION (requires_confirmation: true):
- terminal_run
- file_delete
- file_move (to trash)
- close_app (apps with unsaved work)

RULES:
- Respond ONLY with JSON, no additional text
- response_text should be natural and concise
- If you don't understand, use intent: "unknown" and no_action
- You can execute multiple actions in sequence
- Detect user's language (es/en) and respond in the same language
"""

    @classmethod
    def get_system_prompt(cls, language: str = "es") -> str:
        """Obtiene el prompt del sistema según el idioma."""
        if language == "en":
            return cls.SYSTEM_PROMPT_EN
        return cls.SYSTEM_PROMPT_ES

    @classmethod
    def build_prompt(
        cls,
        user_input: str,
        context: Optional[str] = None,
        available_actions: Optional[str] = None,
        language: str = "es"
    ) -> str:
        """
        Construye el prompt completo para el LLM.

        Args:
            user_input: Entrada del usuario
            context: Contexto de conversaciones anteriores
            available_actions: Lista de acciones disponibles
            language: Idioma preferido

        Returns:
            Prompt construido
        """
        parts = []

        if context:
            parts.append(f"CONTEXTO PREVIO:\n{context}\n")

        parts.append(f"COMANDO DEL USUARIO: {user_input}")

        return "\n".join(parts)

    @classmethod
    def parse_response(cls, response_text: str) -> ParsedResponse:
        """
        Parsea la respuesta del LLM a una estructura utilizable.

        Args:
            response_text: Respuesta cruda del LLM

        Returns:
            ParsedResponse con los datos estructurados
        """
        # Intentar extraer JSON de la respuesta
        json_str = response_text.strip()

        # Si la respuesta tiene texto antes o después del JSON, intentar extraerlo
        if not json_str.startswith("{"):
            start = json_str.find("{")
            end = json_str.rfind("}") + 1
            if start != -1 and end > start:
                json_str = json_str[start:end]

        try:
            data = json.loads(json_str)

            # Filtrar acciones inválidas (que no sean diccionarios válidos)
            actions = data.get("actions", [])
            valid_actions = []
            for action in actions:
                if isinstance(action, dict) and "type" in action:
                    valid_actions.append(action)
                else:
                    logger.warning(f"Acción inválida ignorada: {action}")

            return ParsedResponse(
                intent=data.get("intent", "unknown"),
                actions=valid_actions,
                response_text=data.get("response_text", ""),
                requires_confirmation=data.get("requires_confirmation", False),
                language=data.get("language", "es"),
                raw_response=response_text
            )

        except json.JSONDecodeError as e:
            logger.warning(f"Error parseando respuesta LLM: {e}")
            logger.debug(f"Respuesta raw: {response_text}")

            # Intentar extraer al menos el texto de respuesta
            return ParsedResponse(
                intent="unknown",
                actions=[{"type": "no_action", "params": {}}],
                response_text=cls._extract_response_text(response_text),
                requires_confirmation=False,
                language="es",
                raw_response=response_text
            )

    @classmethod
    def _extract_response_text(cls, text: str) -> str:
        """Intenta extraer texto de respuesta de una respuesta mal formateada."""
        # Si no es JSON válido, usar el texto directamente
        # Limpiar caracteres de JSON parcial
        cleaned = text.strip()
        for char in ["{", "}", "[", "]", '"']:
            cleaned = cleaned.replace(char, "")
        return cleaned[:200] if cleaned else "No pude procesar tu solicitud."

    @classmethod
    def build_confirmation_prompt(
        cls,
        action_description: str,
        language: str = "es"
    ) -> str:
        """
        Construye un prompt para solicitar confirmación.

        Args:
            action_description: Descripción de la acción
            language: Idioma

        Returns:
            Prompt de confirmación
        """
        if language == "en":
            return f"I'm about to {action_description}. Do you confirm?"
        return f"Voy a {action_description}. ¿Confirmas?"

    @classmethod
    def is_confirmation_positive(cls, response: str) -> bool:
        """
        Determina si una respuesta es una confirmación positiva.

        Args:
            response: Respuesta del usuario

        Returns:
            True si es confirmación positiva
        """
        response_lower = response.lower().strip()

        positive_words = [
            # Español
            "sí", "si", "ok", "vale", "confirmo", "adelante", "hazlo",
            "correcto", "afirmativo", "claro", "por supuesto", "dale",
            # Inglés
            "yes", "yeah", "yep", "sure", "confirm", "do it", "go ahead",
            "correct", "affirmative", "absolutely", "of course"
        ]

        return any(word in response_lower for word in positive_words)

    @classmethod
    def is_confirmation_negative(cls, response: str) -> bool:
        """
        Determina si una respuesta es una confirmación negativa.

        Args:
            response: Respuesta del usuario

        Returns:
            True si es confirmación negativa
        """
        response_lower = response.lower().strip()

        negative_words = [
            # Español
            "no", "cancelar", "cancela", "para", "detente", "olvídalo",
            "negativo", "nada", "dejalo", "déjalo",
            # Inglés
            "no", "cancel", "stop", "forget it", "negative", "never mind",
            "don't", "abort"
        ]

        return any(word in response_lower for word in negative_words)
