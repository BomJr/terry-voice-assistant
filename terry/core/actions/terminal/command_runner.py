"""
Home-Alexa - Terminal Command Runner
Acción para ejecutar comandos en terminal (CRÍTICO)
"""

import subprocess
import shlex
from typing import Dict, Any

from terry.core.actions.base import (
    ActionBase, ActionResult, ActionMetadata,
    ActionCategory, RiskLevel
)
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)

# Comandos peligrosos que NO deben ejecutarse nunca
FORBIDDEN_COMMANDS = [
    "rm -rf /",
    "rm -rf ~",
    "rm -rf /*",
    "mkfs",
    "dd if=",
    "> /dev/sda",
    "chmod -R 777 /",
    ":(){ :|:& };:",  # Fork bomb
]

# Comandos que requieren confirmación adicional
DANGEROUS_PATTERNS = [
    "rm ",
    "sudo ",
    "mv ",
    "chmod ",
    "chown ",
    "kill ",
    "pkill ",
    "shutdown",
    "reboot",
]


class TerminalRunAction(ActionBase):
    """Ejecuta un comando en terminal (requiere confirmación)."""

    metadata = ActionMetadata(
        name="terminal_run",
        description="Ejecuta un comando en la terminal",
        description_en="Runs a command in the terminal",
        category=ActionCategory.TERMINAL,
        risk_level=RiskLevel.CRITICAL,  # Siempre requiere confirmación
        keywords_es=["terminal", "comando", "ejecutar", "correr", "shell"],
        keywords_en=["terminal", "command", "run", "execute", "shell"],
        required_params=["command"]
    )

    def validate_params(self, params: Dict[str, Any]) -> tuple:
        """Valida el comando antes de ejecutar."""
        command = params.get("command", "")

        if not command:
            return False, "No se especificó el comando"

        # Verificar comandos prohibidos
        command_lower = command.lower()
        for forbidden in FORBIDDEN_COMMANDS:
            if forbidden.lower() in command_lower:
                return False, f"Comando prohibido por seguridad: {forbidden}"

        return True, ""

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        command = params.get("command", "")
        timeout = params.get("timeout", 30)

        logger.warning(f"Ejecutando comando de terminal: {command}")

        try:
            # Ejecutar el comando
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=params.get("cwd", None)
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                # Limitar output largo
                if len(output) > 500:
                    output = output[:500] + "... (truncado)"

                return ActionResult(
                    success=True,
                    message=f"Comando ejecutado correctamente",
                    data={
                        "output": output,
                        "command": command,
                        "return_code": result.returncode
                    }
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Comando falló con código {result.returncode}",
                    error=result.stderr.strip() or "Error desconocido",
                    data={"return_code": result.returncode}
                )

        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                message=f"Timeout ejecutando comando ({timeout}s)",
                error="TIMEOUT"
            )

        except Exception as e:
            logger.error(f"Error ejecutando comando: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {str(e)}",
                error="EXECUTION_ERROR"
            )

    def get_confirmation_message(self, params: Dict[str, Any], language: str = "es") -> str:
        command = params.get("command", "el comando")
        if language == "en":
            return f"I'm about to run this command: {command}. Do you confirm?"
        return f"Voy a ejecutar este comando: {command}. ¿Confirmas?"


class ScriptRunAction(ActionBase):
    """Ejecuta un script (requiere confirmación)."""

    metadata = ActionMetadata(
        name="script_run",
        description="Ejecuta un script",
        description_en="Runs a script",
        category=ActionCategory.TERMINAL,
        risk_level=RiskLevel.CRITICAL,
        keywords_es=["script", "ejecutar", "correr"],
        keywords_en=["script", "run", "execute"],
        required_params=["path"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        path = params.get("path", "")
        args = params.get("args", [])
        timeout = params.get("timeout", 60)

        if not path:
            return ActionResult(
                success=False,
                message="No se especificó la ruta del script",
                error="MISSING_PATH"
            )

        logger.warning(f"Ejecutando script: {path}")

        try:
            cmd = [path] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Script ejecutado correctamente",
                    data={
                        "output": result.stdout.strip()[:500],
                        "path": path
                    }
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Script falló con código {result.returncode}",
                    error=result.stderr.strip()
                )

        except FileNotFoundError:
            return ActionResult(
                success=False,
                message=f"Script no encontrado: {path}",
                error="FILE_NOT_FOUND"
            )

        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error: {str(e)}",
                error="EXECUTION_ERROR"
            )
