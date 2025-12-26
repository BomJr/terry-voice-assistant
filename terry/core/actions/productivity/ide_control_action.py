"""
IDE Control Action - Terry v6.1
Control VS Code via voice
"""
from typing import Any, Dict
from terry.core.actions.base import ActionBase, ActionResult
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class IDEControlAction(ActionBase):
    """IDE control action for VS Code."""

    def __init__(self):
        super().__init__(
            name="ide_control",
            description="Controlar VS Code por voz",
            description_en="Control VS Code by voice"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Execute IDE control action.

        Args:
            params: Action parameters
                - action: 'open_file', 'open_folder', 'run_tests', 'git_status', 'git_commit', 'git_push', 'terminal'
                - path: File or folder path
                - command: Terminal command
                - message: Git commit message

        Returns:
            ActionResult with operation result
        """
        try:
            from terry.features.productivity.vscode_control import get_vscode_control
            vscode = get_vscode_control()

            action = params.get('action', 'open_file')

            if action == 'open_file':
                path = params.get('path')
                if not path:
                    return ActionResult(success=False, message="Necesito la ruta del archivo")

                success = vscode.open_file(path)
                return ActionResult(
                    success=success,
                    message=f"Abriendo {path} en VS Code" if success else "No pude abrir el archivo"
                )

            elif action == 'open_folder':
                path = params.get('path')
                if not path:
                    return ActionResult(success=False, message="Necesito la ruta de la carpeta")

                success = vscode.open_folder(path)
                return ActionResult(
                    success=success,
                    message=f"Abriendo carpeta en VS Code" if success else "No pude abrir la carpeta"
                )

            elif action == 'run_tests':
                success = vscode.run_tests()
                return ActionResult(
                    success=success,
                    message="Ejecutando tests..." if success else "No pude ejecutar los tests"
                )

            elif action == 'git_status':
                success = vscode.git_status()
                return ActionResult(
                    success=success,
                    message="Mostrando git status..." if success else "No pude ejecutar git status"
                )

            elif action == 'git_commit':
                message = params.get('message', 'Update')
                success = vscode.git_commit(message)
                return ActionResult(
                    success=success,
                    message=f"Commit: {message}" if success else "No pude hacer commit"
                )

            elif action == 'git_push':
                success = vscode.git_push()
                return ActionResult(
                    success=success,
                    message="Pushing..." if success else "No pude hacer push"
                )

            elif action == 'terminal':
                command = params.get('command')
                if not command:
                    return ActionResult(success=False, message="Necesito un comando")

                success = vscode.run_terminal_command(command)
                return ActionResult(
                    success=success,
                    message=f"Ejecutando: {command}" if success else "No pude ejecutar el comando"
                )

            else:
                return ActionResult(success=False, message=f"Acción IDE no reconocida: {action}")

        except ImportError:
            return ActionResult(success=False, message="IDE control no está disponible")
        except Exception as e:
            logger.error(f"Error in IDE control: {e}")
            return ActionResult(success=False, message=f"Error: {str(e)}")
