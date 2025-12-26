"""
Dictation Action - Terry v6.1
Universal dictation to active applications
"""
from typing import Any, Dict
from terry.core.actions.base import ActionBase, ActionResult
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class DictationAction(ActionBase):
    """Dictation action for typing to active applications."""

    def __init__(self):
        super().__init__(
            name="dictation",
            description="Dictar texto a la aplicación activa",
            description_en="Dictate text to active application"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute dictation action.

        Args:
            params: Action parameters
                - action: 'type', 'start', 'stop', 'delete_word', 'delete_sentence', 'new_line', 'new_paragraph'
                - text: Text to type (for 'type' action)

        Returns:
            ActionResult with operation result
        """
        try:
            from terry.features.productivity.universal_dictation import get_dictation
            dictation = get_dictation()

            action = params.get('action', 'type')

            if action == 'type':
                # Type text to active application
                text = params.get('text')

                if not text:
                    return ActionResult(
                        success=False,
                        message="Necesito texto para dictar"
                    )

                success = dictation.type_text(text)

                if success:
                    word_count = len(text.split())
                    return ActionResult(
                        success=True,
                        message=f"Dictado: {word_count} palabras",
                        data={'text': text, 'word_count': word_count}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude dictar el texto"
                    )

            elif action == 'start':
                # Start continuous dictation mode
                dictation.start_dictation()

                return ActionResult(
                    success=True,
                    message="Modo dictado activado. Di 'fin dictado' para terminar"
                )

            elif action == 'stop':
                # Stop continuous dictation mode
                dictation.stop_dictation()

                return ActionResult(
                    success=True,
                    message="Modo dictado desactivado"
                )

            elif action == 'delete_word':
                # Delete last word
                success = dictation.delete_last_word()

                if success:
                    return ActionResult(
                        success=True,
                        message="Palabra eliminada"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude eliminar la palabra"
                    )

            elif action == 'delete_sentence':
                # Delete last sentence
                success = dictation.delete_last_sentence()

                if success:
                    return ActionResult(
                        success=True,
                        message="Oración eliminada"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude eliminar la oración"
                    )

            elif action == 'new_line':
                # Insert new line
                success = dictation.new_line()

                if success:
                    return ActionResult(
                        success=True,
                        message="Nueva línea"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude insertar nueva línea"
                    )

            elif action == 'new_paragraph':
                # Insert new paragraph
                success = dictation.new_paragraph()

                if success:
                    return ActionResult(
                        success=True,
                        message="Nuevo párrafo"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude insertar nuevo párrafo"
                    )

            else:
                return ActionResult(
                    success=False,
                    message=f"Acción de dictado no reconocida: {action}"
                )

        except ImportError:
            return ActionResult(
                success=False,
                message="Dictado no está disponible. Revisa la configuración"
            )
        except Exception as e:
            logger.error(f"Error in dictation: {e}")
            return ActionResult(
                success=False,
                message=f"Error en dictado: {str(e)}"
            )
