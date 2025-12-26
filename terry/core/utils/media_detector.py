"""
Home-Alexa - Media Detector
Detecta y controla aplicaciones de música automáticamente
"""

import subprocess
import shutil
import time
from typing import Optional, Tuple, Callable
from functools import wraps
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


def retry_on_failure(max_retries: int = 2, delay: float = 0.5):
    """
    Decorador para reintentar automáticamente operaciones que fallan.

    Args:
        max_retries: Número máximo de reintentos
        delay: Segundos de espera entre reintentos
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)

                    # Si es una tupla (success, message)
                    if isinstance(result, tuple) and len(result) == 2:
                        success, message = result
                        if success or attempt == max_retries:
                            return result
                        # Si falló y hay reintentos, continuar
                        last_error = message
                        logger.debug(f"Intento {attempt + 1}/{max_retries + 1} falló: {message}")
                    else:
                        return result

                except Exception as e:
                    last_error = str(e)
                    logger.debug(f"Intento {attempt + 1}/{max_retries + 1} error: {e}")

                    if attempt == max_retries:
                        return False, f"Error después de {max_retries + 1} intentos: {e}"

                # Esperar antes del siguiente intento
                if attempt < max_retries:
                    time.sleep(delay)

            return False, f"Falló después de {max_retries + 1} intentos: {last_error}"

        return wrapper
    return decorator


def _has_nowplaying_cli() -> bool:
    """Verifica si nowplaying-cli está instalado."""
    return shutil.which("nowplaying-cli") is not None


class MediaDetector:
    """Detecta y controla aplicaciones de música."""

    # Apps de música soportadas (en orden de prioridad)
    # IMPORTANTE: Atlas PRIMERO porque es el navegador preferido
    MUSIC_APPS = [
        "Atlas",  # Navegador Atlas (OpenAI) - PRIMERO
        "Arc",  # Navegador Arc
        "Spotify",
        "Music",
        "Google Chrome",  # Puede reproducir audio
        "Safari",  # Puede reproducir audio
        "YouTube",
        "VLC",
        "Brave Browser",  # Brave
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
    def is_music_playing(cls, app_name: str) -> bool:
        """
        Verifica si la música está reproduciéndose.

        Args:
            app_name: Nombre de la app

        Returns:
            True si está reproduciendo
        """
        try:
            if app_name == "Music":
                script = '''
                    tell application "Music"
                        return player state as string
                    end tell
                '''
            elif app_name == "Spotify":
                script = '''
                    tell application "Spotify"
                        return player state as string
                    end tell
                '''
            else:
                return False

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                state = result.stdout.strip().lower()
                return "playing" in state

            return False

        except Exception as e:
            logger.debug(f"No se pudo verificar estado: {e}")
            return False

    @classmethod
    @retry_on_failure(max_retries=2, delay=0.3)
    def play(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Reproduce música.
        Usa nowplaying-cli si está disponible (recomendado).

        Args:
            app_name: Ignorado (mantiene compatibilidad)

        Returns:
            (éxito, mensaje)
        """
        try:
            # MÉTODO 1: nowplaying-cli (MEJOR - no activa ventanas)
            if _has_nowplaying_cli():
                result = subprocess.run(
                    ['nowplaying-cli', 'play'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    logger.info("Play ejecutado con nowplaying-cli")
                    return True, "Reproduciendo"
                else:
                    logger.warning(f"nowplaying-cli falló: {result.stderr}")
                    # Continuar al método fallback

            # MÉTODO 2: Fallback a tecla de media F8
            logger.info("Usando fallback: tecla de media")
            script = '''
                tell application "System Events"
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
                return True, "Reproduciendo"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Error desconocido"
                logger.error(f"Error en play: {error_msg}")
                return False, f"Error: {error_msg}"

        except Exception as e:
            logger.error(f"Error en play: {e}")
            return False, str(e)

    @classmethod
    @retry_on_failure(max_retries=2, delay=0.3)
    def pause(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Pausa música.
        Usa nowplaying-cli si está disponible (recomendado).

        Args:
            app_name: Ignorado (mantiene compatibilidad)

        Returns:
            (éxito, mensaje)
        """
        try:
            # MÉTODO 1: nowplaying-cli (MEJOR - no activa ventanas)
            if _has_nowplaying_cli():
                result = subprocess.run(
                    ['nowplaying-cli', 'pause'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    logger.info("Pause ejecutado con nowplaying-cli")
                    return True, "Pausado"
                else:
                    logger.warning(f"nowplaying-cli falló: {result.stderr}")
                    # Continuar al método fallback

            # MÉTODO 2: Fallback a tecla de media F8
            logger.info("Usando fallback: tecla de media")
            script = '''
                tell application "System Events"
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
                return True, "Pausado"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Error desconocido"
                logger.error(f"Error en pause: {error_msg}")
                return False, f"Error: {error_msg}"

        except Exception as e:
            logger.error(f"Error en pause: {e}")
            return False, str(e)

    @classmethod
    @retry_on_failure(max_retries=2, delay=0.3)
    def next_track(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Siguiente pista.
        Usa nowplaying-cli si está disponible (recomendado).

        Args:
            app_name: Ignorado (mantiene compatibilidad)

        Returns:
            (éxito, mensaje)
        """
        try:
            # MÉTODO 1: nowplaying-cli (MEJOR)
            if _has_nowplaying_cli():
                result = subprocess.run(
                    ['nowplaying-cli', 'next'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    logger.info("Next ejecutado con nowplaying-cli")
                    return True, "Siguiente"
                else:
                    logger.warning(f"nowplaying-cli falló: {result.stderr}")
                    # Continuar al método fallback

            # MÉTODO 2: Fallback a tecla de media F9
            logger.info("Usando fallback: tecla de media")
            script = '''
                tell application "System Events"
                    key code 101
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                return True, "Siguiente"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Error desconocido"
                return False, f"Error: {error_msg}"

        except Exception as e:
            logger.error(f"Error en next: {e}")
            return False, str(e)

    @classmethod
    @retry_on_failure(max_retries=2, delay=0.3)
    def previous_track(cls, app_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        Pista anterior.
        Usa nowplaying-cli si está disponible (recomendado).

        Args:
            app_name: Ignorado (mantiene compatibilidad)

        Returns:
            (éxito, mensaje)
        """
        try:
            # MÉTODO 1: nowplaying-cli (MEJOR)
            if _has_nowplaying_cli():
                result = subprocess.run(
                    ['nowplaying-cli', 'previous'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    logger.info("Previous ejecutado con nowplaying-cli")
                    return True, "Anterior"
                else:
                    logger.warning(f"nowplaying-cli falló: {result.stderr}")
                    # Continuar al método fallback

            # MÉTODO 2: Fallback a tecla de media F7
            logger.info("Usando fallback: tecla de media")
            script = '''
                tell application "System Events"
                    key code 99
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                return True, "Anterior"
            else:
                error_msg = result.stderr.strip() if result.stderr else "Error desconocido"
                return False, f"Error: {error_msg}"

        except Exception as e:
            logger.error(f"Error en previous: {e}")
            return False, str(e)

    @classmethod
    def get_current_track(cls, app_name: Optional[str] = None) -> Optional[str]:
        """
        Obtiene la canción actual.
        Intenta primero nowplaying-cli, luego AppleScript.

        Args:
            app_name: App específica o None para auto-detectar

        Returns:
            Nombre de la canción o None
        """
        try:
            # MÉTODO 1: nowplaying-cli (MEJOR - funciona con todo)
            if _has_nowplaying_cli():
                result = subprocess.run(
                    ['nowplaying-cli', 'get', 'title', 'artist'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    output = result.stdout.strip()
                    if output and output != "null":
                        lines = output.split('\n')
                        if len(lines) >= 2:
                            title = lines[0].strip()
                            artist = lines[1].strip()
                            if title and artist:
                                logger.info(f"Canción actual: {title} - {artist}")
                                return f"{title} - {artist}"
                        elif len(lines) == 1 and lines[0]:
                            return lines[0].strip()

        except Exception as e:
            logger.debug(f"nowplaying-cli falló: {e}")

        # MÉTODO 2: AppleScript (Fallback para Music/Spotify)
        app = app_name or cls.get_running_music_app()

        if not app:
            return None

        try:
            if app == "Music":
                script = '''
                    tell application "Music"
                        if player state is playing then
                            return name of current track & " - " & artist of current track
                        end if
                    end tell
                '''
            elif app == "Spotify":
                script = '''
                    tell application "Spotify"
                        if player state is playing then
                            return name of current track & " - " & artist of current track
                        end if
                    end tell
                '''
            else:
                return None

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                track = result.stdout.strip()
                if track:
                    logger.info(f"Canción actual: {track}")
                    return track

            return None

        except Exception as e:
            logger.debug(f"No se pudo obtener canción: {e}")
            return None
