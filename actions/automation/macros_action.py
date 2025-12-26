"""
Macros Action - Terry v6.1
Record and replay command macros
"""
from typing import Any, Dict
from actions.action_base import ActionBase, ActionResult
from utils.logger import get_logger

logger = get_logger(__name__)


class MacrosAction(ActionBase):
    """Macros action for recording and executing macros."""

    def __init__(self):
        super().__init__(
            name="macros",
            description="Grabar y ejecutar macros de comandos",
            description_en="Record and execute command macros"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute macros action.

        Args:
            params: Action parameters
                - action: 'start_recording', 'stop_recording', 'execute', 'list', 'delete', 'status'
                - name: Macro name (for start_recording, execute, delete)
                - macro_id: Macro ID (for execute, delete)

        Returns:
            ActionResult with operation result
        """
        try:
            from macros.macro_recorder import get_macro_recorder
            recorder = get_macro_recorder()

            action = params.get('action', 'list')

            if action == 'start_recording':
                # Start recording a new macro
                name = params.get('name')

                if not name:
                    return ActionResult(
                        success=False,
                        message="Necesito un nombre para el macro"
                    )

                success = recorder.start_recording(name)

                if success:
                    return ActionResult(
                        success=True,
                        message=f"Grabando macro '{name}'. Di 'detén grabación' cuando termines",
                        data={'recording': True, 'name': name}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude iniciar la grabación. Ya existe un macro con ese nombre?"
                    )

            elif action == 'stop_recording':
                # Stop recording and save
                if not recorder.is_recording():
                    return ActionResult(
                        success=False,
                        message="No estoy grabando ningún macro"
                    )

                macro_id = recorder.stop_recording(save=True)

                if macro_id:
                    status = recorder.get_recording_status()
                    return ActionResult(
                        success=True,
                        message=f"Macro guardado con {len(status['commands'])} comandos",
                        data={'macro_id': macro_id}
                    )
                else:
                    return ActionResult(
                        success=False,
                        message="No pude guardar el macro"
                    )

            elif action == 'cancel_recording':
                # Cancel recording without saving
                if not recorder.is_recording():
                    return ActionResult(
                        success=False,
                        message="No estoy grabando ningún macro"
                    )

                recorder.stop_recording(save=False)

                return ActionResult(
                    success=True,
                    message="Grabación cancelada"
                )

            elif action == 'execute':
                # Execute a macro
                name = params.get('name')
                macro_id = params.get('macro_id')

                if not name and not macro_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el nombre o ID del macro a ejecutar"
                    )

                success = await recorder.execute_macro(macro_id=macro_id, macro_name=name)

                if success:
                    return ActionResult(
                        success=True,
                        message=f"Ejecutando macro '{name or macro_id}'"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message=f"No encontré el macro '{name or macro_id}'"
                    )

            elif action == 'list':
                # List all macros
                macros = recorder.list_macros()

                if macros:
                    # Format macro list
                    lines = []
                    for macro in macros[:5]:  # Show first 5
                        cmd_count = len(macro['commands'])
                        lines.append(
                            f"• {macro['name']}: {cmd_count} comandos"
                        )

                    message = f"Tienes {len(macros)} macros:\n" + "\n".join(lines)

                    return ActionResult(
                        success=True,
                        message=message,
                        data={'macros': macros, 'count': len(macros)}
                    )
                else:
                    return ActionResult(
                        success=True,
                        message="No tienes macros guardados"
                    )

            elif action == 'delete':
                # Delete a macro
                name = params.get('name')
                macro_id = params.get('macro_id')

                if not name and not macro_id:
                    return ActionResult(
                        success=False,
                        message="Necesito el nombre o ID del macro a eliminar"
                    )

                success = recorder.delete_macro(macro_id=macro_id, macro_name=name)

                if success:
                    return ActionResult(
                        success=True,
                        message="Macro eliminado"
                    )
                else:
                    return ActionResult(
                        success=False,
                        message=f"No encontré el macro '{name or macro_id}'"
                    )

            elif action == 'status':
                # Get recording status
                status = recorder.get_recording_status()

                if status['recording']:
                    return ActionResult(
                        success=True,
                        message=f"Grabando '{status['name']}': {status['commands_count']} comandos",
                        data=status
                    )
                else:
                    return ActionResult(
                        success=True,
                        message="No estoy grabando",
                        data=status
                    )

            else:
                return ActionResult(
                    success=False,
                    message=f"Acción de macros no reconocida: {action}"
                )

        except ImportError:
            return ActionResult(
                success=False,
                message="Macros no está disponible. Revisa la configuración"
            )
        except Exception as e:
            logger.error(f"Error in macros: {e}")
            return ActionResult(
                success=False,
                message=f"Error en macros: {str(e)}"
            )
