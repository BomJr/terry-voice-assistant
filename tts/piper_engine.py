"""
Home-Alexa - Piper TTS Engine
Motor de Text-to-Speech usando Piper para voz natural offline
"""

import asyncio
import subprocess
import numpy as np
from typing import Optional, Dict
from pathlib import Path
import tempfile
import soundfile as sf
from io import BytesIO
import hashlib
import json

from utils.logger import get_logger

logger = get_logger(__name__)

# Intentar importar piper
try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logger.warning("piper-tts no disponible, usando macOS 'say' como fallback")


class PiperEngine:
    """
    Motor de Text-to-Speech usando Piper.
    Genera voz natural de alta calidad offline.
    """

    def __init__(
        self,
        voices: Dict[str, str] = None,
        speed: float = 1.0,
        cache_enabled: bool = True,
        cache_max_size_mb: int = 100
    ):
        """
        Args:
            voices: Dict con rutas a modelos por idioma {"es": "path/to.onnx", ...}
            speed: Velocidad de habla (0.5-2.0)
            cache_enabled: Si activar caché de audio
            cache_max_size_mb: Tamaño máximo de caché en MB
        """
        self.voices = voices or {}
        self.speed = speed
        self.cache_enabled = cache_enabled
        self.cache_max_size = cache_max_size_mb * 1024 * 1024

        self._voice_instances: Dict[str, PiperVoice] = {}
        self._cache: Dict[str, bytes] = {}
        self._cache_size = 0
        self._initialized = False

    async def initialize(self) -> None:
        """Inicializa el motor de TTS."""
        if not PIPER_AVAILABLE:
            logger.warning("Piper no disponible, usando fallback macOS")
            self._initialized = True
            return

        logger.info("Inicializando Piper TTS...")

        for lang, model_path in self.voices.items():
            try:
                path = Path(model_path)
                if path.exists():
                    voice = PiperVoice.load(str(path))
                    self._voice_instances[lang] = voice
                    logger.info(f"Voz cargada para {lang}: {path.name}")
                else:
                    logger.warning(f"Modelo de voz no encontrado: {model_path}")
            except Exception as e:
                logger.error(f"Error cargando voz {lang}: {e}")

        self._initialized = True
        logger.info(f"Piper inicializado con {len(self._voice_instances)} voces")

    async def synthesize(
        self,
        text: str,
        language: str = "es",
        speed: Optional[float] = None
    ) -> np.ndarray:
        """
        Sintetiza texto a audio.

        Args:
            text: Texto a sintetizar
            language: Código de idioma (es, en)
            speed: Velocidad (usa la predeterminada si no se especifica)

        Returns:
            Array numpy con el audio
        """
        if not text.strip():
            return np.array([], dtype=np.float32)

        # Verificar caché
        cache_key = self._get_cache_key(text, language, speed)
        if self.cache_enabled and cache_key in self._cache:
            logger.debug("Audio obtenido de caché")
            return self._bytes_to_audio(self._cache[cache_key])

        # Generar audio
        if PIPER_AVAILABLE and language in self._voice_instances:
            audio = await self._synthesize_piper(text, language, speed)
        else:
            audio = await self._synthesize_macos_say(text, language, speed)

        # Guardar en caché
        if self.cache_enabled and len(audio) > 0:
            self._add_to_cache(cache_key, self._audio_to_bytes(audio))

        return audio

    async def _synthesize_piper(
        self,
        text: str,
        language: str,
        speed: Optional[float]
    ) -> np.ndarray:
        """Sintetiza usando Piper."""
        voice = self._voice_instances.get(language)
        if not voice:
            logger.warning(f"Voz no disponible para {language}, usando fallback")
            return await self._synthesize_macos_say(text, language, speed)

        try:
            logger.debug(f"Sintetizando con Piper: '{text[:50]}...'")

            # Piper sintetiza a un buffer
            audio_data = []

            # Ejecutar síntesis en thread separado
            def synthesize_sync():
                for audio_bytes in voice.synthesize_stream_raw(text):
                    audio_data.append(np.frombuffer(audio_bytes, dtype=np.int16))

            await asyncio.get_event_loop().run_in_executor(None, synthesize_sync)

            if audio_data:
                audio = np.concatenate(audio_data).astype(np.float32) / 32768.0

                # Aplicar velocidad si es diferente de 1.0
                actual_speed = speed or self.speed
                if actual_speed != 1.0:
                    audio = self._change_speed(audio, actual_speed)

                return audio

            return np.array([], dtype=np.float32)

        except Exception as e:
            logger.error(f"Error en síntesis Piper: {e}")
            return await self._synthesize_macos_say(text, language, speed)

    async def _synthesize_macos_say(
        self,
        text: str,
        language: str,
        speed: Optional[float]
    ) -> np.ndarray:
        """Sintetiza usando el comando 'say' de macOS."""
        logger.debug(f"Sintetizando con macOS say: '{text[:50]}...'")

        # Seleccionar voz según idioma
        voice_map = {
            "es": "Monica",
            "en": "Samantha"
        }
        voice = voice_map.get(language, "Samantha")

        # Calcular rate (palabras por minuto)
        actual_speed = speed or self.speed
        rate = int(175 * actual_speed)  # 175 es el rate por defecto

        try:
            with tempfile.NamedTemporaryFile(suffix=".aiff", delete=True) as f:
                # Generar audio con 'say'
                process = await asyncio.create_subprocess_exec(
                    'say', '-v', voice, '-r', str(rate), '-o', f.name, text,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.PIPE
                )
                _, stderr = await process.communicate()

                if process.returncode != 0:
                    logger.error(f"Error en 'say': {stderr.decode()}")
                    return np.array([], dtype=np.float32)

                # Leer el archivo generado
                audio, sr = sf.read(f.name)

                # Convertir a mono si es estéreo
                if len(audio.shape) > 1:
                    audio = audio.mean(axis=1)

                return audio.astype(np.float32)

        except Exception as e:
            logger.error(f"Error en síntesis macOS: {e}")
            return np.array([], dtype=np.float32)

    async def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        language: str = "es",
        speed: Optional[float] = None
    ) -> bool:
        """
        Sintetiza texto y guarda en archivo.

        Args:
            text: Texto a sintetizar
            output_path: Ruta de salida
            language: Código de idioma
            speed: Velocidad

        Returns:
            True si se guardó correctamente
        """
        audio = await self.synthesize(text, language, speed)
        if len(audio) == 0:
            return False

        try:
            sf.write(output_path, audio, 22050)
            return True
        except Exception as e:
            logger.error(f"Error guardando audio: {e}")
            return False

    def _change_speed(self, audio: np.ndarray, speed: float) -> np.ndarray:
        """Cambia la velocidad del audio (simple resampling)."""
        if speed == 1.0:
            return audio

        # Resampling simple (no preserva pitch perfectamente)
        indices = np.arange(0, len(audio), speed)
        indices = indices[indices < len(audio)].astype(int)
        return audio[indices]

    def _get_cache_key(self, text: str, language: str, speed: Optional[float]) -> str:
        """Genera una clave de caché única."""
        data = f"{text}|{language}|{speed or self.speed}"
        return hashlib.md5(data.encode()).hexdigest()

    def _add_to_cache(self, key: str, audio_bytes: bytes) -> None:
        """Añade audio a la caché."""
        size = len(audio_bytes)

        # Si excede el límite, limpiar entradas antiguas
        while self._cache_size + size > self.cache_max_size and self._cache:
            oldest_key = next(iter(self._cache))
            removed = self._cache.pop(oldest_key)
            self._cache_size -= len(removed)

        self._cache[key] = audio_bytes
        self._cache_size += size

    def _audio_to_bytes(self, audio: np.ndarray) -> bytes:
        """Convierte audio a bytes."""
        buffer = BytesIO()
        sf.write(buffer, audio, 22050, format='WAV')
        return buffer.getvalue()

    def _bytes_to_audio(self, audio_bytes: bytes) -> np.ndarray:
        """Convierte bytes a audio."""
        buffer = BytesIO(audio_bytes)
        audio, _ = sf.read(buffer)
        return audio.astype(np.float32)

    def clear_cache(self) -> None:
        """Limpia la caché de audio."""
        self._cache.clear()
        self._cache_size = 0
        logger.debug("Caché de TTS limpiada")

    @property
    def is_ready(self) -> bool:
        """Verifica si el motor está listo."""
        return self._initialized

    @property
    def available_languages(self) -> list:
        """Lista de idiomas disponibles."""
        if PIPER_AVAILABLE:
            return list(self._voice_instances.keys())
        return ["es", "en"]  # Fallback macOS soporta estos


def create_tts_engine(
    engine_type: str = "piper",
    **kwargs
) -> PiperEngine:
    """
    Factory para crear el motor de TTS apropiado.

    Args:
        engine_type: Tipo de motor (piper)
        **kwargs: Argumentos adicionales

    Returns:
        Instancia del motor de TTS
    """
    if engine_type == "piper":
        return PiperEngine(**kwargs)
    else:
        raise ValueError(f"Motor TTS no soportado: {engine_type}")
