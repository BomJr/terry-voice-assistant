"""
OCR Action - Terry v6.1
Universal OCR for text extraction from screen
"""
from typing import Any, Dict
from actions.action_base import ActionBase, ActionResult
from utils.logger import get_logger

logger = get_logger(__name__)


class OCRAction(ActionBase):
    """OCR action for text extraction from screen."""

    def __init__(self):
        super().__init__(
            name="ocr",
            description="Extraer texto de la pantalla usando OCR",
            description_en="Extract text from screen using OCR"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute OCR action.

        Args:
            params: Action parameters
                - action: 'read', 'copy', 'extract' (default: 'read')
                - image_path: Optional path to image file

        Returns:
            ActionResult with extracted text
        """
        try:
            from vision.ocr_engine import get_ocr_engine
            ocr = get_ocr_engine()

            action = params.get('action', 'read')
            image_path = params.get('image_path')

            if action == 'copy':
                # Read screen and copy to clipboard
                text = await ocr.read_and_copy()

                if text:
                    # Truncate for voice response
                    preview = text[:100] + "..." if len(text) > 100 else text
                    word_count = len(text.split())

                    return ActionResult(
                        success=True,
                        message=f"Texto copiado al portapapeles: {word_count} palabras",
                        data={
                            'text': text,
                            'word_count': word_count,
                            'char_count': len(text),
                            'preview': preview
                        }
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré texto en la pantalla"
                    )

            elif action == 'read':
                # Read text from screen
                text = await ocr.read_screen()

                if text:
                    # Truncate for voice response
                    preview = text[:200] + "..." if len(text) > 200 else text
                    word_count = len(text.split())

                    return ActionResult(
                        success=True,
                        message=f"Leí {word_count} palabras: {preview}",
                        data={
                            'text': text,
                            'word_count': word_count,
                            'char_count': len(text)
                        }
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré texto en la pantalla"
                    )

            elif action == 'extract':
                # Extract text from specific image
                if not image_path:
                    return ActionResult(
                        success=False,
                        message="Necesito la ruta de una imagen"
                    )

                text = await ocr.extract_text(image_path)

                if text:
                    word_count = len(text.split())

                    return ActionResult(
                        success=True,
                        message=f"Extraje {word_count} palabras de la imagen",
                        data={
                            'text': text,
                            'word_count': word_count,
                            'char_count': len(text),
                            'image_path': image_path
                        }
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No encontré texto en la imagen"
                    )

            else:
                return ActionResult(
                    success=False,
                    message=f"Acción OCR no reconocida: {action}"
                )

        except ImportError:
            return ActionResult(
                success=False,
                message="OCR no está disponible. Revisa la configuración en settings.yaml"
            )
        except Exception as e:
            logger.error(f"Error in OCR: {e}")
            return ActionResult(
                success=False,
                message=f"Error en OCR: {str(e)}"
            )
