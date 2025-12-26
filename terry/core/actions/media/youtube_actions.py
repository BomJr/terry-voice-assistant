"""
Home-Alexa - YouTube Advanced Actions
Control avanzado de YouTube (búsqueda, volumen, saltar ads, etc.)
"""

import subprocess
import urllib.parse
from typing import Dict, Any, Optional, Tuple
from terry.core.actions.base import ActionBase, ActionMetadata, ActionResult, ActionCategory, RiskLevel
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class YouTubeSearchAndPlayAction(ActionBase):
    """Busca en YouTube y reproduce el primer resultado."""

    metadata = ActionMetadata(
        name="youtube_search_play",
        description="Busca en YouTube y reproduce el primer resultado",
        description_en="YouTube search and play",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["busca", "reproduce", "youtube", "video", "música"],
        keywords_en=["search", "play", "youtube", "video", "music"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Busca en YouTube y reproduce.

        Params esperados:
            query: str - Término de búsqueda
            browser: str - Navegador a usar (default: Safari)
        """
        query = params.get("query", "")
        browser = params.get("browser", "Safari")

        if not query:
            return ActionResult(
                success=False,
                message="Falta el término de búsqueda",
                data={}
            )

        try:
            # Construir URL de búsqueda de YouTube
            # /results?search_query= hace búsqueda
            # El primer video se puede reproducir directamente agregando &autoplay=1
            encoded_query = urllib.parse.quote_plus(query)
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"

            # Abrir en el navegador
            success, message = await self._open_url_in_browser(youtube_url, browser)

            if success:
                # Esperar un momento y hacer click en el primer resultado
                # Esto se hace con JavaScript si es posible
                await self._click_first_result(browser)
                return ActionResult(
                    success=True,
                    message=f"Buscando '{query}' en YouTube",
                    data={"query": query, "url": youtube_url}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error abriendo YouTube: {message}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en YouTube search & play: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )

    async def _open_url_in_browser(self, url: str, browser: str) -> Tuple[bool, str]:
        """Abre una URL en el navegador especificado."""
        try:
            script = f'''
                tell application "{browser}"
                    activate
                    open location "{url}"
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                return True, "OK"
            else:
                return False, result.stderr.strip()

        except Exception as e:
            return False, str(e)

    async def _click_first_result(self, browser: str):
        """Intenta hacer click en el primer resultado de YouTube."""
        try:
            # Esperar un poco para que cargue la página
            import asyncio
            await asyncio.sleep(1.5)

            # JavaScript para hacer click en el primer video
            js_code = '''
                var firstVideo = document.querySelector('a#video-title');
                if (firstVideo) { firstVideo.click(); }
            '''

            if browser in ["Safari", "Google Chrome", "Arc"]:
                script = f'''
                    tell application "{browser}"
                        tell front window
                            tell current tab
                                execute javascript "{js_code}"
                            end tell
                        end tell
                    end tell
                '''

                subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
        except Exception as e:
            logger.debug(f"No se pudo hacer click automático: {e}")


class YouTubeVolumeAction(ActionBase):
    """Controla el volumen de un video de YouTube."""

    metadata = ActionMetadata(
        name="youtube_volume",
        description="Controla el volumen de YouTube",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["volumen", "youtube", "video"],
        keywords_en=["volume", "youtube", "video"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Controla el volumen del video de YouTube.

        Params esperados:
            action: str - "up" o "down"
            browser: str - Navegador (default: Safari)
        """
        action = params.get("action", "up")
        browser = params.get("browser", "Safari")

        try:
            # YouTube responde a las teclas de flecha arriba/abajo para volumen
            key_code = 126 if action == "up" else 125  # 126=up, 125=down

            script = f'''
                tell application "{browser}"
                    activate
                end tell
                delay 0.1
                tell application "System Events"
                    key code {key_code}
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                action_text = "Subiendo" if action == "up" else "Bajando"
                return ActionResult(
                    success=True,
                    message=f"{action_text} volumen del video",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en YouTube volume: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class YouTubeFullscreenAction(ActionBase):
    """Activa/desactiva pantalla completa en YouTube."""

    metadata = ActionMetadata(
        name="youtube_fullscreen",
        description="Pantalla completa en YouTube",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["pantalla completa", "fullscreen", "youtube"],
        keywords_en=["fullscreen", "youtube"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Activa pantalla completa en YouTube.

        Params esperados:
            browser: str - Navegador (default: Safari)
        """
        browser = params.get("browser", "Safari")

        try:
            # YouTube usa la tecla 'f' para pantalla completa
            script = f'''
                tell application "{browser}"
                    activate
                end tell
                delay 0.1
                tell application "System Events"
                    keystroke "f"
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Pantalla completa activada",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en YouTube fullscreen: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class YouTubeQualityAction(ActionBase):
    """Cambia la calidad del video de YouTube."""

    metadata = ActionMetadata(
        name="youtube_quality",
        description="Cambia la calidad del video",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["calidad", "resolución", "youtube"],
        keywords_en=["quality", "resolution", "youtube"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Abre el menú de calidad de YouTube.

        Params esperados:
            browser: str - Navegador (default: Safari)
        """
        browser = params.get("browser", "Safari")

        try:
            # Shift+, abre el menú de configuración en YouTube
            # Luego se puede navegar con flechas
            script = f'''
                tell application "{browser}"
                    activate
                end tell
                delay 0.1
                tell application "System Events"
                    keystroke "," using {{shift down}}
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                return ActionResult(
                    success=True,
                    message="Abriendo configuración de calidad (usa flechas para navegar)",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en YouTube quality: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )


class YouTubeSpeedAction(ActionBase):
    """Cambia la velocidad de reproducción en YouTube."""

    metadata = ActionMetadata(
        name="youtube_speed",
        description="Cambia la velocidad de reproducción",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["velocidad", "rápido", "lento", "youtube"],
        keywords_en=["speed", "faster", "slower", "youtube"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """
        Cambia la velocidad de reproducción.

        Params esperados:
            action: str - "faster" (Shift+>) o "slower" (Shift+<)
            browser: str - Navegador (default: Safari)
        """
        action = params.get("action", "faster")
        browser = params.get("browser", "Safari")

        try:
            # Shift+> acelera, Shift+< desacelera
            key = ">" if action == "faster" else "<"

            script = f'''
                tell application "{browser}"
                    activate
                end tell
                delay 0.1
                tell application "System Events"
                    keystroke "{key}" using {{shift down}}
                end tell
            '''

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode == 0:
                action_text = "Acelerando" if action == "faster" else "Desacelerando"
                return ActionResult(
                    success=True,
                    message=f"{action_text} reproducción",
                    data={}
                )
            else:
                return ActionResult(
                    success=False,
                    message=f"Error: {result.stderr}",
                    data={}
                )

        except Exception as e:
            logger.error(f"Error en YouTube speed: {e}")
            return ActionResult(
                success=False,
                message=f"Error: {e}",
                data={}
            )
