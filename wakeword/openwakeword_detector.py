"""
Home-Alexa - Wake Word Detector
Detección de wake word usando openWakeWord
"""

import asyncio
import numpy as np
from typing import Optional, Callable
from pathlib import Path
import time

from utils.logger import get_logger

logger = get_logger(__name__)

# Intentar importar openwakeword
try:
    import openwakeword
    from openwakeword.model import Model as OWWModel
    OPENWAKEWORD_AVAILABLE = True
except ImportError:
    OPENWAKEWORD_AVAILABLE = False
    logger.warning("openwakeword no disponible. Usando detector simple basado en energía.")


class SimpleEnergyDetector:
    """
    Detector simple basado en energía del audio.
    Usado como fallback cuando openwakeword no está disponible.
    """

    def __init__(self, threshold: float = 0.02, min_duration: float = 0.3):
        self.threshold = threshold
        self.min_duration = min_duration
        self.sample_rate = 16000
        self._energy_history = []
        self._speech_start: Optional[float] = None

    def process(self, audio_chunk: np.ndarray) -> bool:
        """Procesa un chunk de audio y detecta actividad."""
        # Calcular energía RMS
        energy = np.sqrt(np.mean(audio_chunk ** 2))
        self._energy_history.append(energy)

        # Mantener historial limitado
        if len(self._energy_history) > 50:
            self._energy_history = self._energy_history[-50:]

        # Calcular umbral dinámico basado en el ruido de fondo
        if len(self._energy_history) > 10:
            noise_floor = np.percentile(self._energy_history, 20)
            dynamic_threshold = max(self.threshold, noise_floor * 3)
        else:
            dynamic_threshold = self.threshold

        # Detectar inicio de habla
        if energy > dynamic_threshold:
            if self._speech_start is None:
                self._speech_start = time.time()
            elif time.time() - self._speech_start > self.min_duration:
                self._speech_start = None
                return True
        else:
            self._speech_start = None

        return False


class WakeWordDetector:
    """
    Detector de wake word que usa openWakeWord cuando está disponible,
    con fallback a detección por energía.
    """

    def __init__(
        self,
        wake_phrase: str = "hey mac",
        threshold: float = 0.5,
        cooldown_seconds: float = 2.0,
        sample_rate: int = 16000
    ):
        """
        Args:
            wake_phrase: Frase de activación
            threshold: Umbral de detección (0-1)
            cooldown_seconds: Tiempo entre detecciones
            sample_rate: Tasa de muestreo del audio
        """
        self.wake_phrase = wake_phrase.lower()
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.sample_rate = sample_rate

        self._last_detection: float = 0
        self._model: Optional[OWWModel] = None
        self._fallback_detector = SimpleEnergyDetector()
        self._use_fallback = not OPENWAKEWORD_AVAILABLE

        # Callback para notificar detección
        self._on_wake_callback: Optional[Callable] = None

    async def initialize(self) -> None:
        """Inicializa el detector de wake word."""
        if OPENWAKEWORD_AVAILABLE:
            try:
                # Descargar modelos si es necesario
                logger.info("Inicializando openWakeWord...")

                # Cargar modelo preentrenado
                # openWakeWord tiene modelos para "hey mycroft", "alexa", etc.
                # Para "hey mac" necesitaríamos entrenar uno personalizado
                # Por ahora usamos detección genérica
                self._model = OWWModel(
                    wakeword_models=["hey_mycroft"],  # Modelo similar
                    inference_framework="onnx"
                )
                logger.info("openWakeWord inicializado correctamente")
            except Exception as e:
                logger.warning(f"Error inicializando openWakeWord: {e}")
                logger.info("Usando detector de fallback basado en energía")
                self._use_fallback = True
        else:
            logger.info("Usando detector de fallback basado en energía")
            self._use_fallback = True

    async def process(self, audio_chunk: np.ndarray) -> bool:
        """
        Procesa un chunk de audio y detecta el wake word.

        Args:
            audio_chunk: Array de audio (float32, 16kHz, mono)

        Returns:
            True si se detectó el wake word
        """
        # Verificar cooldown
        current_time = time.time()
        if current_time - self._last_detection < self.cooldown_seconds:
            return False

        detected = False

        if self._use_fallback:
            detected = self._fallback_detector.process(audio_chunk)
        else:
            try:
                # openWakeWord espera int16
                if audio_chunk.dtype == np.float32:
                    audio_int16 = (audio_chunk * 32767).astype(np.int16)
                else:
                    audio_int16 = audio_chunk

                # Procesar con openWakeWord
                prediction = self._model.predict(audio_int16)

                # Verificar si algún modelo superó el umbral
                for model_name, scores in prediction.items():
                    if any(score > self.threshold for score in scores):
                        detected = True
                        break

            except Exception as e:
                logger.error(f"Error en detección de wake word: {e}")
                # Usar fallback si hay error
                detected = self._fallback_detector.process(audio_chunk)

        if detected:
            self._last_detection = current_time
            logger.info(f"Wake word detectado: '{self.wake_phrase}'")

            # Ejecutar callback si existe
            if self._on_wake_callback:
                try:
                    if asyncio.iscoroutinefunction(self._on_wake_callback):
                        await self._on_wake_callback()
                    else:
                        self._on_wake_callback()
                except Exception as e:
                    logger.error(f"Error en callback de wake word: {e}")

        return detected

    def on_wake(self, callback: Callable) -> None:
        """
        Registra un callback para cuando se detecte el wake word.

        Args:
            callback: Función a ejecutar cuando se detecte
        """
        self._on_wake_callback = callback

    def reset_cooldown(self) -> None:
        """Reinicia el cooldown permitiendo detección inmediata."""
        self._last_detection = 0

    @property
    def is_ready(self) -> bool:
        """Verifica si el detector está listo."""
        return self._model is not None or self._use_fallback

    @property
    def using_fallback(self) -> bool:
        """Indica si está usando el detector de fallback."""
        return self._use_fallback


class ContinuousWakeWordDetector:
    """
    Detector continuo que procesa audio en tiempo real.
    Diseñado para funcionar con el AudioManager.
    """

    def __init__(
        self,
        wake_phrase: str = "hey mac",
        threshold: float = 0.5,
        cooldown_seconds: float = 2.0,
        post_wake_buffer_seconds: float = 0.5
    ):
        self.detector = WakeWordDetector(
            wake_phrase=wake_phrase,
            threshold=threshold,
            cooldown_seconds=cooldown_seconds
        )
        self.post_wake_buffer_seconds = post_wake_buffer_seconds
        self._running = False
        self._audio_buffer = []
        self._buffer_lock = asyncio.Lock()

    async def initialize(self) -> None:
        """Inicializa el detector."""
        await self.detector.initialize()

    async def start(
        self,
        audio_stream,
        on_wake_detected: Callable
    ) -> None:
        """
        Inicia la detección continua.

        Args:
            audio_stream: AsyncIterator de chunks de audio
            on_wake_detected: Callback cuando se detecta wake word
        """
        self._running = True
        self.detector.on_wake(on_wake_detected)

        logger.info("Detector de wake word iniciado")

        async for chunk in audio_stream:
            if not self._running:
                break

            # Mantener buffer pequeño para contexto
            async with self._buffer_lock:
                self._audio_buffer.append(chunk)
                # Mantener solo los últimos segundos
                max_chunks = int(self.post_wake_buffer_seconds * 16000 / len(chunk))
                if len(self._audio_buffer) > max_chunks:
                    self._audio_buffer = self._audio_buffer[-max_chunks:]

            # Procesar
            await self.detector.process(chunk)

    def stop(self) -> None:
        """Detiene la detección."""
        self._running = False
        logger.info("Detector de wake word detenido")

    async def get_pre_buffer(self) -> np.ndarray:
        """Obtiene el audio capturado justo antes de la detección."""
        async with self._buffer_lock:
            if self._audio_buffer:
                return np.concatenate(self._audio_buffer)
            return np.array([], dtype=np.float32)
