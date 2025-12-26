"""
Home-Alexa - Ejecutor de AppleScript
Permite ejecutar scripts de AppleScript de forma asíncrona
"""

import asyncio
import subprocess
from typing import Tuple, Optional
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


async def run_applescript(script: str, timeout: float = 10.0) -> Tuple[bool, str, Optional[str]]:
    """
    Ejecuta un script de AppleScript de forma asíncrona.

    Args:
        script: Código AppleScript a ejecutar
        timeout: Timeout en segundos

    Returns:
        Tupla (éxito, salida, error)
    """
    try:
        process = await asyncio.create_subprocess_exec(
            'osascript', '-e', script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        success = process.returncode == 0
        output = stdout.decode('utf-8').strip() if stdout else ""
        error = stderr.decode('utf-8').strip() if stderr and not success else None

        if not success:
            logger.warning(f"AppleScript error: {error}")

        return success, output, error

    except asyncio.TimeoutError:
        logger.error(f"AppleScript timeout después de {timeout}s")
        return False, "", f"Timeout después de {timeout} segundos"

    except Exception as e:
        logger.error(f"Error ejecutando AppleScript: {e}")
        return False, "", str(e)


def run_applescript_sync(script: str, timeout: float = 10.0) -> Tuple[bool, str, Optional[str]]:
    """
    Ejecuta un script de AppleScript de forma síncrona.

    Args:
        script: Código AppleScript a ejecutar
        timeout: Timeout en segundos

    Returns:
        Tupla (éxito, salida, error)
    """
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        success = result.returncode == 0
        output = result.stdout.strip() if result.stdout else ""
        error = result.stderr.strip() if result.stderr and not success else None

        if not success:
            logger.warning(f"AppleScript error: {error}")

        return success, output, error

    except subprocess.TimeoutExpired:
        logger.error(f"AppleScript timeout después de {timeout}s")
        return False, "", f"Timeout después de {timeout} segundos"

    except Exception as e:
        logger.error(f"Error ejecutando AppleScript: {e}")
        return False, "", str(e)


async def run_applescript_file(file_path: str, timeout: float = 30.0) -> Tuple[bool, str, Optional[str]]:
    """
    Ejecuta un archivo de AppleScript.

    Args:
        file_path: Ruta al archivo .scpt o .applescript
        timeout: Timeout en segundos

    Returns:
        Tupla (éxito, salida, error)
    """
    try:
        process = await asyncio.create_subprocess_exec(
            'osascript', file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=timeout
        )

        success = process.returncode == 0
        output = stdout.decode('utf-8').strip() if stdout else ""
        error = stderr.decode('utf-8').strip() if stderr and not success else None

        return success, output, error

    except asyncio.TimeoutError:
        return False, "", f"Timeout después de {timeout} segundos"

    except Exception as e:
        return False, "", str(e)


# Scripts comunes pre-definidos
class AppleScripts:
    """Colección de scripts de AppleScript comunes."""

    @staticmethod
    def open_app(app_name: str) -> str:
        """Abre una aplicación."""
        return f'tell application "{app_name}" to activate'

    @staticmethod
    def close_app(app_name: str) -> str:
        """Cierra una aplicación."""
        return f'tell application "{app_name}" to quit'

    @staticmethod
    def get_frontmost_app() -> str:
        """Obtiene la aplicación en primer plano."""
        return '''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            return frontApp
        '''

    @staticmethod
    def set_volume(level: int) -> str:
        """Establece el volumen del sistema (0-100)."""
        # macOS usa escala 0-7 internamente
        mac_level = int(level * 7 / 100)
        return f'set volume output volume {level}'

    @staticmethod
    def get_volume() -> str:
        """Obtiene el volumen actual."""
        return 'output volume of (get volume settings)'

    @staticmethod
    def mute() -> str:
        """Silencia el sistema."""
        return 'set volume with output muted'

    @staticmethod
    def unmute() -> str:
        """Quita el silencio del sistema."""
        return 'set volume without output muted'

    @staticmethod
    def toggle_mute() -> str:
        """Alterna silencio."""
        return '''
            set currentMute to output muted of (get volume settings)
            if currentMute then
                set volume without output muted
            else
                set volume with output muted
            end if
        '''

    @staticmethod
    def press_key(key_code: int, modifiers: list = None) -> str:
        """Simula presionar una tecla."""
        if modifiers:
            mod_str = " using {" + ", ".join(modifiers) + "}"
        else:
            mod_str = ""
        return f'''
            tell application "System Events"
                key code {key_code}{mod_str}
            end tell
        '''

    @staticmethod
    def keystroke(text: str, modifiers: list = None) -> str:
        """Simula escribir texto."""
        if modifiers:
            mod_str = " using {" + ", ".join(modifiers) + "}"
        else:
            mod_str = ""
        return f'''
            tell application "System Events"
                keystroke "{text}"{mod_str}
            end tell
        '''

    @staticmethod
    def open_url(url: str, browser: str = "Safari") -> str:
        """Abre una URL en el navegador especificado."""
        return f'''
            tell application "{browser}"
                activate
                open location "{url}"
            end tell
        '''

    @staticmethod
    def new_browser_tab(browser: str = "Safari") -> str:
        """Abre una nueva pestaña en el navegador."""
        if browser in ["Google Chrome", "Arc", "Atlas"]:
            return f'''
                tell application "{browser}"
                    activate
                    tell front window to make new tab
                end tell
            '''
        else:  # Safari
            return f'''
                tell application "{browser}"
                    activate
                    tell front window to set current tab to (make new tab)
                end tell
            '''

    @staticmethod
    def close_browser_tab(browser: str = "Safari") -> str:
        """Cierra la pestaña actual del navegador."""
        return f'''
            tell application "{browser}"
                tell front window to close current tab
            end tell
        '''

    @staticmethod
    def browser_search(query: str, browser: str = "Safari") -> str:
        """Realiza una búsqueda en el navegador."""
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return AppleScripts.open_url(search_url, browser)

    @staticmethod
    def media_play_pause() -> str:
        """Play/Pause multimedia."""
        return '''
            tell application "System Events"
                key code 49
            end tell
        '''

    @staticmethod
    def media_next() -> str:
        """Siguiente pista."""
        return '''
            tell application "System Events"
                key code 124 using command down
            end tell
        '''

    @staticmethod
    def media_previous() -> str:
        """Pista anterior."""
        return '''
            tell application "System Events"
                key code 123 using command down
            end tell
        '''

    @staticmethod
    def get_clipboard() -> str:
        """Obtiene el contenido del portapapeles."""
        return 'the clipboard'

    @staticmethod
    def set_clipboard(text: str) -> str:
        """Establece el contenido del portapapeles."""
        escaped = text.replace('"', '\\"')
        return f'set the clipboard to "{escaped}"'

    @staticmethod
    def display_notification(title: str, message: str) -> str:
        """Muestra una notificación del sistema."""
        return f'display notification "{message}" with title "{title}"'

    @staticmethod
    def speak(text: str, voice: str = None) -> str:
        """Habla el texto usando la voz del sistema."""
        if voice:
            return f'say "{text}" using "{voice}"'
        return f'say "{text}"'
