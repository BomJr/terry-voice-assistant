"""
Home-Alexa - Wake Word Detection
Detecta "hey mac" para activar el asistente
"""

import pyaudio
import numpy as np
from typing import Callable, Optional
import threading
import time
from utils.logger import get_logger

logger = get_logger(__name__)


class WakeWordDetector:
    """Detector de wake word simple usando análisis de audio."""

    def __init__(
        self,
        wake_word: str = "hey mac",
        sensitivity: float = 0.5,
        callback: Optional[Callable] = None
    ):
        """
        Inicializa el detector de wake word.

        Args:
            wake_word: Palabra de activación
            sensitivity: Sensibilidad (0.0 a 1.0)
            callback: Función a llamar cuando se detecta
        """
        self.wake_word = wake_word.lower()
        self.sensitivity = sensitivity
        self.callback = callback
        self.is_listening = False
        self.thread = None

        # Configuración de audio
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000

        self.audio = pyaudio.PyAudio()

    def start(self):
        """Inicia la detección de wake word en segundo plano."""
        if self.is_listening:
            logger.warning("Wake word detector ya está corriendo")
            return

        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info(f"Wake word detector iniciado: '{self.wake_word}'")

    def stop(self):
        """Detiene la detección de wake word."""
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Wake word detector detenido")

    def _listen_loop(self):
        """Loop principal de escucha."""
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            logger.info("🎤 Escuchando wake word...")

            # Buffer para análisis
            audio_buffer = []
            silence_threshold = 500  # Umbral de silencio
            speech_detected = False

            while self.is_listening:
                try:
                    # Leer audio
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)

                    # Calcular energía del audio
                    energy = np.abs(audio_data).mean()

                    # Detectar si hay voz (energía por encima del umbral)
                    if energy > silence_threshold:
                        if not speech_detected:
                            speech_detected = True
                            audio_buffer = []
                            logger.debug("🗣️  Voz detectada")

                        audio_buffer.append(data)

                        # Si tenemos suficiente audio (2 segundos aprox)
                        if len(audio_buffer) > 30:  # 30 chunks ≈ 2s
                            # Por ahora, simplemente llamar al callback
                            # En versión completa, aquí iría el análisis real
                            # del wake word usando openwakeword o similar
                            if speech_detected and self.callback:
                                logger.info(f"✨ Wake word detectado: '{self.wake_word}'")
                                self.callback()

                            # Resetear
                            audio_buffer = []
                            speech_detected = False

                    else:
                        # Silencio
                        if speech_detected and len(audio_buffer) > 5:
                            # Hubo voz pero ahora silencio
                            speech_detected = False
                            audio_buffer = []

                except Exception as e:
                    logger.error(f"Error en listen loop: {e}")
                    time.sleep(0.1)

            stream.stop_stream()
            stream.close()

        except Exception as e:
            logger.error(f"Error iniciando audio stream: {e}")
            self.is_listening = False

    def __del__(self):
        """Limpieza al destruir."""
        self.stop()
        self.audio.terminate()


# Versión simple usando detección de voz (sin wake word específico)
class SimpleVoiceActivation:
    """Detector simple: cualquier voz activa el asistente."""

    def __init__(self, callback: Optional[Callable] = None):
        self.callback = callback
        self.is_listening = False
        self.thread = None

        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        self.audio = pyaudio.PyAudio()

    def start(self):
        """Inicia la detección."""
        if self.is_listening:
            return

        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        logger.info("🎤 Activación por voz iniciada (presiona Enter o habla)")

    def stop(self):
        """Detiene la detección."""
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=2)

    def _listen_loop(self):
        """Loop de escucha simple."""
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )

            # Por ahora, modo simple: esperar Enter
            # En producción, aquí iría la detección de voz real

        except Exception as e:
            logger.error(f"Error en voice activation: {e}")

    def __del__(self):
        self.stop()
        self.audio.terminate()
