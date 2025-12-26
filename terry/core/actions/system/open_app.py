"""
Home-Alexa - Open App Action
Acción para abrir aplicaciones en macOS
"""

import subprocess
from typing import Dict, Any

from terry.core.actions.base import (
    ActionBase, ActionResult, ActionMetadata,
    ActionCategory, RiskLevel
)
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAppAction(ActionBase):
    """Abre una aplicación en macOS."""

    metadata = ActionMetadata(
        name="open_app",
        description="Abre una aplicación",
        description_en="Opens an application",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.SAFE,
        keywords_es=["abrir", "abre", "lanzar", "iniciar", "ejecutar", "aplicación", "app"],
        keywords_en=["open", "launch", "start", "run", "application", "app"],
        required_params=["app_name"]
    )

    # Mapeo de nombres comunes a nombres de apps en macOS
    APP_ALIASES = {
        # Navegadores
        "safari": "Safari",
        "chrome": "Google Chrome",
        "google chrome": "Google Chrome",
        "firefox": "Firefox",
        "arc": "Arc",
        "atlas": "Atlas",
        "brave": "Brave Browser",
        "edge": "Microsoft Edge",

        # Sistema
        "terminal": "Terminal",
        "finder": "Finder",
        "configuración": "System Preferences",
        "configuracion": "System Preferences",
        "preferencias": "System Preferences",
        "settings": "System Preferences",
        "system preferences": "System Preferences",
        "ajustes": "System Preferences",

        # Productividad
        "notas": "Notes",
        "notes": "Notes",
        "recordatorios": "Reminders",
        "reminders": "Reminders",
        "calendario": "Calendar",
        "calendar": "Calendar",
        "mail": "Mail",
        "correo": "Mail",

        # Multimedia
        "música": "Music",
        "musica": "Music",
        "music": "Music",
        "fotos": "Photos",
        "photos": "Photos",
        "tv": "TV",

        # Comunicación
        "mensajes": "Messages",
        "messages": "Messages",
        "facetime": "FaceTime",

        # Desarrollo
        "vscode": "Visual Studio Code",
        "visual studio code": "Visual Studio Code",
        "code": "Visual Studio Code",
        "xcode": "Xcode",

        # Otros
        "spotify": "Spotify",
        "discord": "Discord",
        "slack": "Slack",
        "zoom": "zoom.us",
        "whatsapp": "WhatsApp",
        "telegram": "Telegram",
    }

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Ejecuta la apertura de la aplicación."""
        app_name = params.get("app_name", "")

        if not app_name:
            return ActionResult(
                success=False,
                message="No se especificó la aplicación",
                error="MISSING_APP_NAME"
            )

        # Resolver alias
        resolved_name = self.APP_ALIASES.get(
            app_name.lower(),
            app_name  # Si no hay alias, usar el nombre original
        )

        try:
            result = subprocess.run(
                ["open", "-a", resolved_name],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message=f"Aplicación {resolved_name} abierta",
                    data={"app_name": resolved_name}
                )
            else:
                # Intentar sin el flag -a (por si es un archivo)
                result2 = subprocess.run(
                    ["open", resolved_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result2.returncode == 0:
                    return ActionResult(
                        success=True,
                        message=f"Abierto: {resolved_name}",
                        data={"app_name": resolved_name}
                    )

                return ActionResult(
                    success=False,
                    message=f"No se pudo abrir {resolved_name}",
                    error=result.stderr or result2.stderr
                )

        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                message="Timeout al abrir la aplicación",
                error="TIMEOUT"
            )

        except Exception as e:
            logger.error(f"Error abriendo {resolved_name}: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {str(e)}",
                error="EXECUTION_ERROR"
            )

    def get_confirmation_message(self, params: Dict[str, Any], language: str = "es") -> str:
        app_name = params.get("app_name", "la aplicación")
        if language == "en":
            return f"Opening {app_name}"
        return f"Abriendo {app_name}"


class CloseAppAction(ActionBase):
    """Cierra una aplicación en macOS."""

    metadata = ActionMetadata(
        name="close_app",
        description="Cierra una aplicación",
        description_en="Closes an application",
        category=ActionCategory.SYSTEM,
        risk_level=RiskLevel.MODERATE,
        keywords_es=["cerrar", "cierra", "terminar", "salir", "quit"],
        keywords_en=["close", "quit", "exit", "terminate"],
        required_params=["app_name"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Ejecuta el cierre de la aplicación."""
        app_name = params.get("app_name", "")

        # Resolver alias
        resolved_name = OpenAppAction.APP_ALIASES.get(
            app_name.lower(), app_name
        )

        try:
            # Usar AppleScript para cerrar de forma elegante
            script = f'tell application "{resolved_name}" to quit'
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message=f"Aplicación {resolved_name} cerrada",
                    data={"app_name": resolved_name}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"No se pudo cerrar {resolved_name}",
                    error=result.stderr
                )

        except Exception as e:
            return ActionResult(
                success=False,
                message=f"Error: {str(e)}",
                error="EXECUTION_ERROR"
            )
