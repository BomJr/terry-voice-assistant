"""
Camera Vision Action - Terry v6.1
Face recognition and screenshot analysis
"""
from typing import Any, Dict
from actions.action_base import ActionBase, ActionResult
from utils.logger import get_logger

logger = get_logger(__name__)


class CameraVisionAction(ActionBase):
    """Camera vision action with face recognition and screen analysis."""

    def __init__(self):
        super().__init__(
            name="camera_vision",
            description="Reconocimiento facial y análisis de pantalla",
            description_en="Face recognition and screen analysis"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute camera vision action.

        Args:
            params: Action parameters
                - action: 'recognize', 'screenshot', 'describe_screen', 'stats'

        Returns:
            ActionResult with vision data
        """
        try:
            from vision.camera_vision import get_camera_vision
            camera = get_camera_vision()

            action = params.get('action', 'recognize')

            if action == 'recognize':
                # Recognize person using camera
                result = await camera.recognize_person()

                if result.get('success'):
                    person = result.get('person', 'Unknown')
                    confidence = result.get('confidence', 0.0)
                    face_count = result.get('face_count', 0)

                    if person == 'Unknown':
                        message = f"Veo {face_count} {'persona' if face_count == 1 else 'personas'}, pero no la reconozco"
                    else:
                        message = f"Veo a {person}"
                        if confidence < 0.7:
                            message += " (no estoy muy seguro)"

                    return ActionResult(
                        success=True,
                        message=message,
                        data={
                            'person': person,
                            'confidence': confidence,
                            'face_count': face_count
                        }
                    )
                else:
                    error_msg = result.get('message', 'No pude acceder a la cámara')
                    return ActionResult(
                        success=False,
                        message=error_msg
                    )

            elif action == 'screenshot':
                # Capture screenshot
                screenshot_path = await camera.capture_screenshot()

                if screenshot_path:
                    return ActionResult(
                        success=True,
                        message="Captura de pantalla guardada",
                        data={'screenshot_path': screenshot_path}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude capturar la pantalla"
                    )

            elif action == 'describe_screen':
                # Describe what's on screen
                description = await camera.describe_screen()

                return ActionResult(
                    success=True,
                    message=description,
                    data={'description': description}
                )

            elif action == 'stats':
                # Get face recognition stats from API
                stats = await camera.get_stats()

                if stats.get('success'):
                    total_persons = stats.get('total_persons', 0)
                    total_images = stats.get('total_images', 0)

                    message = f"Tengo {total_persons} personas registradas con {total_images} imágenes"

                    return ActionResult(
                        success=True,
                        message=message,
                        data=stats
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude obtener estadísticas. ¿Está el servidor de face-recognition corriendo?"
                    )

            else:
                return ActionResult(
                    success=False,
                    message=f"Acción no reconocida: {action}"
                )

        except ImportError:
            return ActionResult(
                success=False,
                message="Camera vision no está disponible. Revisa la configuración en settings.yaml"
            )
        except Exception as e:
            logger.error(f"Error in camera vision: {e}")
            return ActionResult(
                success=False,
                message=f"Error en visión: {str(e)}"
            )
