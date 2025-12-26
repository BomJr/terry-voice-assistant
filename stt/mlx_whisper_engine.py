"""
Home-Alexa - MLX Whisper STT Engine
Motor de Speech-to-Text usando MLX Whisper optimizado para Apple Silicon
"""

import asyncio
import numpy as np
from typing import Tuple, Optional
from pathlib import Path
import tempfile
import soundfile as sf

from utils.logger import get_logger

logger = get_logger(__name__)

# Intentar importar mlx_whisper
try:
    import mlx_whisper
    MLX_WHISPER_AVAILABLE = True
except ImportError:
    MLX_WHISPER_AVAILABLE = False
    logger.warning("mlx_whisper no disponible")


class MLXWhisperEngine:
    """
    Motor de Speech-to-Text usando MLX Whisper.
    Optimizado para Apple Silicon (M1/M2/M3/M4).
    """

    # Mapeo de modelos a sus repos en Hugging Face
    # Usar modelos directos que no requieren auth
    MODEL_REPOS = {
        "tiny": "openai/whisper-tiny",
        "base": "openai/whisper-base",
        "small": "openai/whisper-small",
        "medium": "openai/whisper-medium",
        "large": "openai/whisper-large-v3",
        "large-v3": "openai/whisper-large-v3",
    }

    def __init__(
        self,
        model: str = "base",
        compute_type: str = "float16",
        language: Optional[str] = None
    ):
        """
        Args:
            model: Tamaño del modelo (tiny, base, small, medium, large)
            compute_type: Tipo de precisión (float16, float32)
            language: Idioma forzado (None para detección automática)
        """
        self.model_name = model
        self.model_path = self.MODEL_REPOS.get(model, model)
        self.compute_type = compute_type
        self.default_language = language
        self._model_loaded = False

    async def load_model(self) -> None:
        """Carga el modelo de Whisper."""
        if not MLX_WHISPER_AVAILABLE:
            logger.error("mlx_whisper no está instalado")
            return

        logger.info(f"Cargando modelo Whisper: {self.model_name}...")

        try:
            # mlx_whisper descarga y cachea el modelo automáticamente
            # Solo verificamos que funciona haciendo una transcripción dummy
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._test_model
            )
            self._model_loaded = True
            logger.info(f"Modelo Whisper '{self.model_name}' cargado correctamente")
        except Exception as e:
            logger.error(f"Error cargando modelo Whisper: {e}")
            raise

    def _test_model(self) -> None:
        """Prueba que el modelo funcione."""
        # Crear audio de silencio para test
        test_audio = np.zeros(16000, dtype=np.float32)  # 1 segundo de silencio

        # Guardar temporalmente
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
            sf.write(f.name, test_audio, 16000)
            # Intentar transcribir
            mlx_whisper.transcribe(
                f.name,
                path_or_hf_repo=self.model_path,
            )

    async def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
        sample_rate: int = 16000
    ) -> Tuple[str, str]:
        """
        Transcribe audio a texto.

        Args:
            audio: Array de audio (float32)
            language: Idioma (None para detección automática)
            sample_rate: Tasa de muestreo del audio

        Returns:
            Tupla (texto transcrito, idioma detectado)
        """
        if not MLX_WHISPER_AVAILABLE:
            logger.error("mlx_whisper no disponible")
            return "", "unknown"

        if len(audio) == 0:
            return "", "unknown"

        logger.debug(f"Transcribiendo audio de {len(audio)/sample_rate:.2f}s...")

        try:
            # mlx_whisper necesita un archivo, no array directo
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                sf.write(f.name, audio, sample_rate)

                # Transcribir
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: mlx_whisper.transcribe(
                        f.name,
                        path_or_hf_repo=self.model_path,
                        language=language or self.default_language,
                        fp16=(self.compute_type == "float16"),
                    )
                )

            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")

            logger.info(f"Transcripción: '{text}' (idioma: {detected_language})")
            return text, detected_language

        except Exception as e:
            logger.error(f"Error en transcripción: {e}")
            return "", "unknown"

    async def transcribe_file(
        self,
        file_path: str,
        language: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Transcribe un archivo de audio.

        Args:
            file_path: Ruta al archivo de audio
            language: Idioma (None para detección automática)

        Returns:
            Tupla (texto transcrito, idioma detectado)
        """
        if not MLX_WHISPER_AVAILABLE:
            return "", "unknown"

        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: mlx_whisper.transcribe(
                    file_path,
                    path_or_hf_repo=self.model_path,
                    language=language or self.default_language,
                    fp16=(self.compute_type == "float16"),
                )
            )

            text = result.get("text", "").strip()
            detected_language = result.get("language", "unknown")

            return text, detected_language

        except Exception as e:
            logger.error(f"Error transcribiendo archivo: {e}")
            return "", "unknown"

    @property
    def is_ready(self) -> bool:
        """Verifica si el motor está listo."""
        return MLX_WHISPER_AVAILABLE and self._model_loaded


class MacOSSayFallback:
    """
    Fallback usando el comando 'say' de macOS para STT.
    En realidad macOS no tiene STT nativo fácil de usar,
    así que esto es solo un placeholder.
    """

    def __init__(self):
        logger.warning("MacOSSayFallback no es un STT real, solo placeholder")

    async def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
        sample_rate: int = 16000
    ) -> Tuple[str, str]:
        """Placeholder - no hace transcripción real."""
        logger.warning("STT fallback: no hay transcripción disponible")
        return "", "unknown"


def create_stt_engine(
    engine_type: str = "mlx_whisper",
    model: str = "base",
    **kwargs
) -> MLXWhisperEngine:
    """
    Factory para crear el motor de STT apropiado.

    Args:
        engine_type: Tipo de motor (mlx_whisper)
        model: Modelo a usar
        **kwargs: Argumentos adicionales

    Returns:
        Instancia del motor de STT
    """
    if engine_type == "mlx_whisper":
        if MLX_WHISPER_AVAILABLE:
            return MLXWhisperEngine(model=model, **kwargs)
        else:
            logger.warning("mlx_whisper no disponible, retornando engine sin funcionalidad")
            return MLXWhisperEngine(model=model, **kwargs)
    else:
        raise ValueError(f"Motor STT no soportado: {engine_type}")
