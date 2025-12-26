"""
Home-Alexa - Media Detector V3
Versión alternativa usando enfoque de "activar app + enviar espacio"
"""

import subprocess
from typing import Optional, Tuple
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class MediaDetectorV3:
    """Detecta y controla aplicaciones de música usando activación + espacio."""

    # Apps de música soportadas (en orden de prioridad)
    MUSIC_APPS = [
        "Music",
        "Spotify",
        "Atlas",
        "YouTube",
        "VLC",
        "Safari",
        "Google Chrome",
        "Arc",
        "Brave Browser",
    ]

    @classmethod
    def get_running_music_app(cls) -> Optional[str]:
        """
        Detecta qué aplicación de música está corriendo.

        Returns:
            Nombre de la app o None
        """
        try:
            # Obtener apps corriendo
            result = subprocess.run(
                ['osascript', '-e', '''
                    tell application "System Events"
                        get name of every process whose background only is false
                    end tell
                '''],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                running_apps = result.stdout.strip().split(", ")

                # Buscar primera app de música que esté corriendo
                for music_app in cls.MUSIC_APPS:
                    if music_app in running_apps:
                        logger.info(f"App de música detectada: {music_app}")
                        return music_app

            return None

        except Exception as e:
            logger.error(f"Error detectando app de música: {e}")
            return None

    @classmethod
    def toggle_playback(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Alterna play/pause activando la app y enviando espacio.
        Este método es más confiable que usar key codes de media.

        Args:
            app_name: App específica o None para auto-detectar

        Returns:
            (éxito, mensaje)
        """
        app = app_name or cls.get_running_music_app()

        if not app:
            return False, "No hay app de música abierta"

        try:
            # Apps con AppleScript nativo (más confiable)
            if app == "Music":
                script = 'tell application "Music" to playpause'
            elif app == "Spotify":
                script = 'tell application "Spotify" to playpause'
            else:
                # Para navegadores y otras apps:
                # 1. Activar la app (traerla al frente)
                # 2. Enviar tecla de espacio
                script = f'''
                    tell application "{app}" to activate
                    delay 0.1
                    tell application "System Events"
                        keystroke " "
                    end tell
                '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return True, f"Play/Pause en {app}"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Error desconocido"
                logger.error(f"Error en toggle_playback: {error_msg}")
                return False, f"Error controlando {app}: {error_msg}"

        except Exception as e:
            logger.error(f"Error en toggle_playback: {e}")
            return False, str(e)

    @classmethod
    def play(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """Reproduce música (usa toggle ya que no podemos detectar estado fácilmente)."""
        return cls.toggle_playback(app_name)

    @classmethod
    def pause(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """Pausa música (usa toggle ya que no podemos detectar estado fácilmente)."""
        return cls.toggle_playback(app_name)

    @classmethod
    def next_track(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """Siguiente pista."""
        app = app_name or cls.get_running_music_app()

        if not app:
            return False, "No hay app de música abierta"

        try:
            if app == "Music":
                script = 'tell application "Music" to next track'
            elif app == "Spotify":
                script = 'tell application "Spotify" to next track'
            else:
                # Shift + Cmd + Right Arrow (siguiente en YouTube)
                script = f'''
                    tell application "{app}" to activate
                    delay 0.1
                    tell application "System Events"
                        key code 124 using {{shift down, command down}}
                    end tell
                '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return True, f"Siguiente en {app}"
            else:
                return False, f"Error controlando {app}"

        except Exception as e:
            logger.error(f"Error en next: {e}")
            return False, str(e)

    @classmethod
    def previous_track(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """Pista anterior."""
        app = app_name or cls.get_running_music_app()

        if not app:
            return False, "No hay app de música abierta"

        try:
            if app == "Music":
                script = 'tell application "Music" to previous track'
            elif app == "Spotify":
                script = 'tell application "Spotify" to previous track'
            else:
                # Shift + Cmd + Left Arrow (anterior en YouTube)
                script = f'''
                    tell application "{app}" to activate
                    delay 0.1
                    tell application "System Events"
                        key code 123 using {{shift down, command down}}
                    end tell
                '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return True, f"Anterior en {app}"
            else:
                return False, f"Error controlando {app}"

        except Exception as e:
            logger.error(f"Error en previous: {e}")
            return False, str(e)
