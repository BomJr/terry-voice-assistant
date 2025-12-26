"""
Home-Alexa - Media Detector V4
Detecta QUÉ app está reproduciendo audio (no solo qué está abierta)
"""

import subprocess
from typing import Optional, Tuple
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class MediaDetectorV4:
    """Detecta y controla la app que ESTÁ REPRODUCIENDO audio."""

    @classmethod
    def get_playing_app(cls) -> Optional[str]:
        """
        Detecta QUÉ aplicación está reproduciendo audio AHORA.

        Returns:
            Nombre de la app reproduciendo o None
        """
        try:
            # Usar 'nowplayingctl' si está disponible (macOS 12+)
            # O verificar el centro de control de medios
            script = '''
                tell application "System Events"
                    set playingApps to {}

                    -- Verificar Music
                    try
                        tell application "Music"
                            if player state is playing then
                                set end of playingApps to "Music"
                            end if
                        end tell
                    end try

                    -- Verificar Spotify
                    try
                        tell application "Spotify"
                            if player state is playing then
                                set end of playingApps to "Spotify"
                            end if
                        end tell
                    end try

                    return playingApps
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0 and result.stdout.strip():
                apps = result.stdout.strip()
                if apps:
                    # Retornar la primera app que esté reproduciendo
                    logger.info(f"App reproduciendo: {apps}")
                    return apps.split(", ")[0]

            return None

        except Exception as e:
            logger.error(f"Error detectando app reproduciendo: {e}")
            return None

    @classmethod
    def toggle_playback_universal(cls) -> Tuple[bool, str]:
        """
        Alterna play/pause usando el atajo UNIVERSAL de macOS.
        No requiere detectar qué app está reproduciendo.
        Funciona con CUALQUIER app que tenga audio.

        Returns:
            (éxito, mensaje)
        """
        try:
            # Usar el atajo de teclado F8 (media play/pause)
            # Este es el equivalente a presionar la tecla de play/pause del teclado
            script = '''
                tell application "System Events"
                    -- Simular la tecla F8 (play/pause de media)
                    -- Key code 100 = F8
                    key code 100
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                return True, "Play/Pause ejecutado"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Error desconocido"
                logger.error(f"Error en toggle_playback_universal: {error_msg}")
                return False, f"Error: {error_msg}"

        except Exception as e:
            logger.error(f"Error en toggle_playback_universal: {e}")
            return False, str(e)

    @classmethod
    def play(cls) -> Tuple[bool, str]:
        """Toggle play/pause (universal)."""
        return cls.toggle_playback_universal()

    @classmethod
    def pause(cls) -> Tuple[bool, str]:
        """Toggle play/pause (universal)."""
        return cls.toggle_playback_universal()
