"""
Home-Alexa - Command Processor
Procesa comandos del usuario integrando LLM + Prompt Templates
"""

import asyncio
from typing import Dict, Any, Optional

from terry.core.llm.ollama_client import OllamaClient
from terry.core.llm.prompt_templates import PromptTemplates, ParsedResponse
from terry.core.llm.cache import ResponseCache
from terry.core.utils.persistent_cache import get_persistent_cache
from terry.core.utils.session_state import get_session
from terry.core.utils.logger import get_logger
from terry.core.utils.language_detector import detect_language
from terry.core.actions.routines.routine_manager import RoutineManager

logger = get_logger(__name__)


class CommandProcessor:
    """
    Procesador de comandos que integra el LLM con los prompt templates.
    """

    def __init__(
        self,
        llm_client: OllamaClient,
        default_language: str = "es"
    ):
        self.llm = llm_client
        self.default_language = default_language
        self.routine_manager = RoutineManager()  # v6.0

    async def process_command(
        self,
        user_input: str,
        context: Optional[str] = None,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa un comando del usuario.

        Args:
            user_input: Texto del usuario
            context: Contexto de conversaciones previas
            language: Idioma del comando (auto-detectado si es None)

        Returns:
            Dict con intent, actions, response, etc.
        """
        # Detección automática de idioma (v6.0)
        if language is None:
            lang = detect_language(user_input)
            logger.debug(f"Idioma detectado automáticamente: {lang}")
        else:
            lang = language

        logger.debug(f"Procesando comando: {user_input} (idioma: {lang})")

        # Obtener session state para gestos de voz (v6.0)
        session = get_session()

        # NIVEL 1: Intentar respuesta rápida del caché (patrones predefinidos)
        cached = ResponseCache.get_quick_response(user_input, session_state=session)
        if cached:
            # Manejar gesto "ok" context-aware
            if cached.get("intent") == "gesture_ok":
                # Determinar acción según contexto (play si pausado, pause si playing)
                cached = self._handle_ok_gesture(cached, session)

            # Manejar rutinas por voz (v6.0)
            if cached.get("intent") == "activate_routine":
                cached = self._handle_routine(cached)

            logger.info("Respuesta desde caché rápido (0.00s)")
            return cached

        # NIVEL 2: Intentar caché persistente (respuestas LLM aprendidas)
        persistent_cache = get_persistent_cache()
        persistent_cached = persistent_cache.get(user_input)
        if persistent_cached:
            logger.info("Respuesta desde caché persistente (0.01s)")
            persistent_cached["cached"] = True
            return persistent_cached

        # NIVEL 3: Usar LLM si no hay caché
        # Construir prompt
        system_prompt = PromptTemplates.get_system_prompt(lang)
        user_prompt = PromptTemplates.build_prompt(
            user_input=user_input,
            context=context,
            language=lang
        )

        try:
            # Generar respuesta del LLM
            llm_response = await self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )

            # Parsear respuesta
            parsed = PromptTemplates.parse_response(llm_response.text)

            # Convertir a dict para retorno
            result = {
                "intent": parsed.intent,
                "actions": parsed.actions,
                "response": parsed.response_text,
                "requires_confirmation": parsed.requires_confirmation,
                "language": parsed.language,
                "raw_llm_response": parsed.raw_response,
                "cached": False
            }

            # Guardar en caché persistente para futuras consultas
            persistent_cache.set(user_input, result)

            return result

        except Exception as e:
            logger.error(f"Error procesando comando: {e}")
            return {
                "intent": "error",
                "actions": [],
                "response": "Lo siento, hubo un error procesando tu solicitud." if lang == "es" else "Sorry, there was an error processing your request.",
                "requires_confirmation": False,
                "language": lang,
                "error": str(e)
            }

    async def process_confirmation(
        self,
        user_response: str,
        language: Optional[str] = None
    ) -> bool:
        """
        Procesa una respuesta de confirmación del usuario.

        Args:
            user_response: Respuesta del usuario
            language: Idioma

        Returns:
            True si es confirmación positiva
        """
        return PromptTemplates.is_confirmation_positive(user_response)

    def _handle_ok_gesture(self, cached_response: Dict[str, Any], session) -> Dict[str, Any]:
        """
        Maneja el gesto "ok" de forma context-aware (v6.0).

        Determina si debe play o pause según contexto.

        Args:
            cached_response: Respuesta cacheada del gesto
            session: Estado de sesión

        Returns:
            Respuesta modificada con acción apropiada
        """
        # Por ahora, toggle play/pause (puede mejorarse con detección de estado real)
        # En el futuro, podría usar nowplaying-cli para detectar si está reproduciendo
        cached_response["actions"] = [
            {
                "type": "media_play",  # O media_pause según estado real
                "params": {}
            }
        ]
        cached_response["response"] = "OK"
        return cached_response

    def _handle_routine(self, cached_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maneja activación de rutinas por voz (v6.0).

        Args:
            cached_response: Respuesta cacheada con routine_name

        Returns:
            Respuesta con acciones de la rutina
        """
        # Extraer nombre de rutina de los actions
        routine_name = None
        if cached_response.get("actions"):
            for action in cached_response["actions"]:
                if "routine_name" in action.get("params", {}):
                    routine_name = action["params"]["routine_name"]
                    break

        if not routine_name:
            return cached_response

        # Normalizar nombre de rutina (mapear variaciones)
        routine_map = {
            "buenas noches": "buenas_noches",
            "buenos dias": "buenos_dias",
            "buenos días": "buenos_dias"
        }
        routine_name = routine_map.get(routine_name.lower(), routine_name)

        # Buscar rutina
        routine = self.routine_manager.get_routine(routine_name)

        if routine:
            # Reemplazar con acciones de la rutina
            cached_response["actions"] = routine.get("actions", [])
            cached_response["response"] = f"Ejecutando rutina {routine.get('description', routine_name)}"
        else:
            cached_response["response"] = f"No encontré la rutina '{routine_name}'"
            cached_response["actions"] = []

        return cached_response
