"""
Home-Alexa - Media Control Actions
Acciones para control multimedia
"""

from typing import Dict, Any

from actions.action_base import (
    ActionBase, ActionResult, ActionMetadata,
    ActionCategory, RiskLevel
)
from utils.applescript_runner import run_applescript_sync, AppleScripts
from utils.media_detector import MediaDetector
from utils.logger import get_logger

logger = get_logger(__name__)


class MediaPlayAction(ActionBase):
    """Reproduce música."""

    metadata = ActionMetadata(
        name="media_play",
        description="Reproduce música",
        description_en="Plays music",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["reproducir", "play", "pon", "continuar", "reanudar"],
        keywords_en=["play", "resume", "continue"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        success, message = MediaDetector.play()

        return ActionResult(
            success=success,
            message=message,
            data={}
        )


class MediaPauseAction(ActionBase):
    """Pausa música."""

    metadata = ActionMetadata(
        name="media_pause",
        description="Pausa música",
        description_en="Pauses music",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["pausar", "pause", "para", "detener", "stop"],
        keywords_en=["pause", "stop"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        success, message = MediaDetector.pause()

        return ActionResult(
            success=success,
            message=message,
            data={}
        )


class MediaPlayPauseAction(ActionBase):
    """Alterna reproducción/pausa (toggle)."""

    metadata = ActionMetadata(
        name="media_play_pause",
        description="Alterna reproducción/pausa",
        description_en="Toggles play/pause",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["toggle", "alternar"],
        keywords_en=["toggle"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        # Detectar app
        app = MediaDetector.get_running_music_app()

        if not app:
            return ActionResult(
                success=False,
                message="No hay app de música abierta",
                error="NO_MUSIC_APP"
            )

        # Verificar si está reproduciendo
        is_playing = MediaDetector.is_music_playing(app)

        # Toggle: si está reproduciendo, pausar; si no, reproducir
        if is_playing:
            success, message = MediaDetector.pause(app)
        else:
            success, message = MediaDetector.play(app)

        return ActionResult(
            success=success,
            message=message,
            data={"was_playing": is_playing}
        )


class MediaNextAction(ActionBase):
    """Siguiente pista/video."""

    metadata = ActionMetadata(
        name="media_next",
        description="Pasa al siguiente contenido",
        description_en="Skips to next content",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["siguiente", "next", "adelante", "saltar"],
        keywords_en=["next", "skip", "forward"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        success, message = MediaDetector.next_track()

        return ActionResult(
            success=success,
            message=message,
            data={}
        )


class MediaPreviousAction(ActionBase):
    """Pista/video anterior."""

    metadata = ActionMetadata(
        name="media_previous",
        description="Vuelve al contenido anterior",
        description_en="Goes to previous content",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["anterior", "atrás", "previous", "volver"],
        keywords_en=["previous", "back", "rewind"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        success, message = MediaDetector.previous_track()

        return ActionResult(
            success=success,
            message=message,
            data={}
        )


class YouTubeSkipAdAction(ActionBase):
    """Salta el anuncio de YouTube."""

    metadata = ActionMetadata(
        name="youtube_skip_ad",
        description="Salta el anuncio de YouTube",
        description_en="Skips YouTube ad",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["saltar", "anuncio", "ad", "skip", "publicidad"],
        keywords_en=["skip", "ad", "advertisement"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        browser = params.get("browser", "Google Chrome")

        # Script para hacer clic en el botón de saltar anuncio
        script = f'''
            tell application "{browser}"
                activate
                tell active tab of front window
                    execute javascript "
                        var skipBtn = document.querySelector('.ytp-ad-skip-button, .ytp-skip-ad-button, .ytp-ad-skip-button-modern');
                        if (skipBtn) {{
                            skipBtn.click();
                            'skipped';
                        }} else {{
                            'no_button';
                        }}
                    "
                end tell
            end tell
        '''

        success, output, error = run_applescript_sync(script)

        if success:
            if "skipped" in str(output):
                return ActionResult(
                    success=True,
                    message="Anuncio saltado",
                    data={}
                )
            else:
                return ActionResult(
                    success=True,
                    message="No hay anuncio para saltar",
                    data={"note": "No skip button found"}
                )
        else:
            # Intentar método alternativo: presionar tecla
            script2 = '''
                tell application "System Events"
                    keystroke "l" using {shift down}
                end tell
            '''
            run_applescript_sync(script2)

            return ActionResult(
                success=True,
                message="Intentando saltar anuncio",
                data={}
            )


class SpotifyPlayAction(ActionBase):
    """Reproduce en Spotify."""

    metadata = ActionMetadata(
        name="spotify_play",
        description="Controla reproducción de Spotify",
        description_en="Controls Spotify playback",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["spotify", "música", "canción"],
        keywords_en=["spotify", "music", "song"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        action = params.get("action", "playpause")

        if action == "playpause":
            script = 'tell application "Spotify" to playpause'
        elif action == "next":
            script = 'tell application "Spotify" to next track'
        elif action == "previous":
            script = 'tell application "Spotify" to previous track'
        elif action == "play":
            script = 'tell application "Spotify" to play'
        elif action == "pause":
            script = 'tell application "Spotify" to pause'
        else:
            return ActionResult(
                success=False,
                message=f"Acción no reconocida: {action}",
                error="INVALID_ACTION"
            )

        success, _, error = run_applescript_sync(script)

        if success:
            return ActionResult(
                success=True,
                message=f"Spotify: {action}",
                data={"action": action}
            )
        else:
            return ActionResult(
                success=False,
                message="Error controlando Spotify",
                error=error
            )


class NowPlayingAction(ActionBase):
    """Muestra qué canción/video está sonando actualmente."""

    metadata = ActionMetadata(
        name="now_playing",
        description="Muestra la canción o video actual",
        description_en="Shows current song or video",
        category=ActionCategory.MEDIA,
        risk_level=RiskLevel.SAFE,
        keywords_es=["qué suena", "qué está sonando", "canción actual", "now playing"],
        keywords_en=["now playing", "current song", "what's playing"]
    )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        """Muestra qué está sonando."""
        from utils.media_detector import MediaDetector

        track = MediaDetector.get_current_track()

        if track:
            return ActionResult(
                success=True,
                message=f"🎵 Sonando: {track}",
                data={"track": track}
            )
        else:
            return ActionResult(
                success=True,
                message="No hay música reproduciéndose",
                data={"track": None}
            )
