"""
Home-Alexa - Action Executor
Ejecutor de acciones con manejo de confirmación
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from terry.core.actions.registry import ActionRegistry
from terry.core.actions.base import ActionBase, ActionResult, RiskLevel
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Resultado de la ejecución de múltiples acciones."""
    success: bool
    actions_executed: List[Dict[str, Any]]
    total_time: float
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None


class ActionExecutor:
    """
    Ejecutor de acciones del asistente.
    Maneja confirmaciones, timeouts y ejecución secuencial/paralela.
    """

    def __init__(
        self,
        confirmation_level: str = "critical",
        execution_timeout: int = 30,
        tts_engine=None,
        stt_engine=None,
        audio_manager=None
    ):
        """
        Args:
            confirmation_level: Nivel de confirmación ('none', 'critical', 'all')
            execution_timeout: Timeout en segundos para cada acción
            tts_engine: Motor TTS para confirmaciones por voz
            stt_engine: Motor STT para escuchar confirmaciones
            audio_manager: Gestor de audio
        """
        self.confirmation_level = confirmation_level
        self.execution_timeout = execution_timeout
        self.tts = tts_engine
        self.stt = stt_engine
        self.audio = audio_manager
        self.registry = ActionRegistry()

    async def execute_actions(
        self,
        actions: List[Dict[str, Any]],
        language: str = "es"
    ) -> ExecutionResult:
        """
        Ejecuta una lista de acciones.

        Args:
            actions: Lista de acciones con tipo y parámetros
            language: Idioma para mensajes

        Returns:
            ExecutionResult con los resultados
        """
        import time
        start_time = time.time()
        results = []
        all_success = True

        for action_spec in actions:
            action_type = action_spec.get("type")
            params = action_spec.get("params", {})

            if action_type == "no_action":
                continue

            result = await self.execute_single(action_type, params, language)
            results.append({
                "type": action_type,
                "params": params,
                "result": result.to_dict()
            })

            if not result.success:
                all_success = False
                # Continuar con las demás acciones aunque una falle

        total_time = time.time() - start_time

        return ExecutionResult(
            success=all_success,
            actions_executed=results,
            total_time=total_time
        )

    async def execute_single(
        self,
        action_type: str,
        params: Dict[str, Any],
        language: str = "es"
    ) -> ActionResult:
        """
        Ejecuta una sola acción.

        Args:
            action_type: Tipo de acción
            params: Parámetros
            language: Idioma

        Returns:
            ActionResult
        """
        logger.info(f"Ejecutando acción: {action_type} con params: {params}")

        # Obtener la acción del registro
        action = self.registry.get(action_type)
        if not action:
            logger.warning(f"Acción no encontrada: {action_type}")
            return ActionResult(
                success=False,
                message=f"Acción no reconocida: {action_type}",
                error="ACTION_NOT_FOUND"
            )

        # Validar parámetros
        is_valid, error_msg = action.validate_params(params)
        if not is_valid:
            return ActionResult(
                success=False,
                message=error_msg,
                error="INVALID_PARAMS"
            )

        # Verificar si necesita confirmación
        if self._needs_confirmation(action):
            confirmed = await self._request_confirmation(action, params, language)
            if not confirmed:
                return ActionResult(
                    success=False,
                    message="Acción cancelada por el usuario",
                    error="USER_CANCELLED"
                )

        # Ejecutar con timeout
        try:
            result = await asyncio.wait_for(
                action.execute(params),
                timeout=self.execution_timeout
            )
            logger.info(f"Acción {action_type} completada: {result.success}")

            # v6.1 - Record in action history for undo functionality
            if result.success and action_type != "undo":  # Don't record undo actions
                try:
                    from terry.features.undo.action_history import get_action_history, determine_undo_params

                    history = get_action_history()
                    reversible, undo_params = determine_undo_params(
                        action_type, params, result.data or {}
                    )

                    history.record(
                        action_type=action_type,
                        params=params,
                        result=result.to_dict(),
                        reversible=reversible,
                        undo_params=undo_params
                    )

                except Exception as e:
                    logger.debug(f"Could not record action in history: {e}")

            return result

        except asyncio.TimeoutError:
            logger.error(f"Timeout ejecutando {action_type}")
            return ActionResult(
                success=False,
                message=f"Timeout ejecutando {action_type}",
                error="TIMEOUT"
            )

        except Exception as e:
            logger.error(f"Error ejecutando {action_type}: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {str(e)}",
                error="EXECUTION_ERROR"
            )

    def _needs_confirmation(self, action: ActionBase) -> bool:
        """Determina si una acción necesita confirmación."""
        if self.confirmation_level == "none":
            return False

        if self.confirmation_level == "all":
            return True

        # confirmation_level == "critical"
        return action.risk_level == RiskLevel.CRITICAL

    async def _request_confirmation(
        self,
        action: ActionBase,
        params: Dict[str, Any],
        language: str
    ) -> bool:
        """
        Solicita confirmación al usuario por voz.

        Returns:
            True si el usuario confirma
        """
        # Si no hay TTS/STT, asumir confirmación
        if not self.tts or not self.stt or not self.audio:
            logger.warning("No hay TTS/STT disponible, asumiendo confirmación")
            return True

        try:
            # Generar mensaje de confirmación
            message = action.get_confirmation_message(params, language)

            # Reproducir pregunta
            audio_data = await self.tts.synthesize(message, language)
            await self.audio.play(audio_data)

            # Esperar respuesta
            await asyncio.sleep(0.5)  # Pequeña pausa
            response_audio = await self.audio.capture_until_silence(
                max_seconds=5.0,
                silence_threshold_seconds=1.0
            )

            # Transcribir respuesta
            response_text, _ = await self.stt.transcribe(response_audio)

            # Analizar respuesta
            from terry.core.llm.prompt_templates import PromptTemplates
            if PromptTemplates.is_confirmation_positive(response_text):
                logger.info("Confirmación positiva recibida")
                return True
            elif PromptTemplates.is_confirmation_negative(response_text):
                logger.info("Confirmación negativa recibida")
                return False
            else:
                # Respuesta ambigua, pedir de nuevo
                retry_msg = "No entendí. ¿Sí o no?" if language == "es" else "I didn't understand. Yes or no?"
                audio_data = await self.tts.synthesize(retry_msg, language)
                await self.audio.play(audio_data)

                response_audio = await self.audio.capture_until_silence(
                    max_seconds=3.0,
                    silence_threshold_seconds=1.0
                )
                response_text, _ = await self.stt.transcribe(response_audio)

                return PromptTemplates.is_confirmation_positive(response_text)

        except Exception as e:
            logger.error(f"Error en confirmación: {e}")
            return False

    async def execute_with_retry(
        self,
        action_type: str,
        params: Dict[str, Any],
        max_retries: int = 2,
        language: str = "es"
    ) -> ActionResult:
        """
        Ejecuta una acción con reintentos.

        Args:
            action_type: Tipo de acción
            params: Parámetros
            max_retries: Número máximo de reintentos
            language: Idioma

        Returns:
            ActionResult
        """
        last_result = None

        for attempt in range(max_retries + 1):
            result = await self.execute_single(action_type, params, language)

            if result.success:
                return result

            last_result = result
            if attempt < max_retries:
                logger.info(f"Reintentando {action_type} (intento {attempt + 2})")
                await asyncio.sleep(0.5)

        return last_result
