"""
Home-Alexa - Audio Manager
Gestión de entrada/salida de audio con buffer circular y VAD
"""

import asyncio
import numpy as np
from collections import deque
from typing import AsyncIterator, Optional, Callable
from dataclasses import dataclass
import threading
import queue
import sounddevice as sd
import soundfile as sf
from io import BytesIO
import webrtcvad

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class AudioConfig:
    """Configuración de audio."""
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024  # frames por chunk
    buffer_seconds: int = 30
    vad_aggressiveness: int = 2  # 0-3


class CircularBuffer:
    """Buffer circular thread-safe para audio."""

    def __init__(self, max_seconds: int, sample_rate: int):
        self.max_samples = max_seconds * sample_rate
        self._buffer = deque(maxlen=self.max_samples)
        self._lock = threading.Lock()

    def append(self, data: np.ndarray) -> None:
        """Añade datos al buffer."""
        with self._lock:
            for sample in data.flatten():
                self._buffer.append(sample)

    def get_last(self, seconds: float, sample_rate: int) -> np.ndarray:
        """Obtiene los últimos N segundos de audio."""
        num_samples = int(seconds * sample_rate)
        with self._lock:
            if len(self._buffer) < num_samples:
                return np.array(list(self._buffer), dtype=np.float32)
            return np.array(list(self._buffer)[-num_samples:], dtype=np.float32)

    def get_all(self) -> np.ndarray:
        """Obtiene todo el contenido del buffer."""
        with self._lock:
            return np.array(list(self._buffer), dtype=np.float32)

    def clear(self) -> None:
        """Limpia el buffer."""
        with self._lock:
            self._buffer.clear()

    def __len__(self) -> int:
        return len(self._buffer)


class VADProcessor:
    """Procesador de Voice Activity Detection."""

    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 2):
        """
        Args:
            sample_rate: Tasa de muestreo (8000, 16000, 32000, 48000)
            aggressiveness: Nivel de agresividad (0-3)
        """
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(aggressiveness)
        # webrtcvad necesita frames de 10, 20 o 30 ms
        self.frame_duration_ms = 30
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)

    def is_speech(self, audio_chunk: np.ndarray) -> bool:
        """
        Detecta si hay voz en el chunk de audio.

        Args:
            audio_chunk: Array de audio (float32 o int16)

        Returns:
            True si se detecta voz
        """
        # Convertir a int16 si es float
        if audio_chunk.dtype == np.float32:
            audio_int16 = (audio_chunk * 32767).astype(np.int16)
        else:
            audio_int16 = audio_chunk.astype(np.int16)

        # Procesar en frames del tamaño correcto
        speech_frames = 0
        total_frames = 0

        for i in range(0, len(audio_int16) - self.frame_size, self.frame_size):
            frame = audio_int16[i:i + self.frame_size]
            try:
                if self.vad.is_speech(frame.tobytes(), self.sample_rate):
                    speech_frames += 1
                total_frames += 1
            except Exception:
                continue

        # Considerar que hay voz si más del 30% de los frames tienen voz
        if total_frames == 0:
            return False
        return (speech_frames / total_frames) > 0.3


class AudioManager:
    """
    Gestor de audio para captura y reproducción.

    Proporciona:
    - Captura de audio en streaming
    - Buffer circular para historial
    - Voice Activity Detection
    - Reproducción de audio
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        buffer_seconds: int = 30,
        vad_aggressiveness: int = 2,
        input_device: Optional[int] = None,
        output_device: Optional[int] = None
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.input_device = input_device
        self.output_device = output_device

        # Buffer circular
        self.buffer = CircularBuffer(buffer_seconds, sample_rate)

        # VAD
        self.vad = VADProcessor(sample_rate, vad_aggressiveness)

        # Estado
        self._running = False
        self._input_stream: Optional[sd.InputStream] = None
        self._audio_queue: queue.Queue = queue.Queue()
        self._stream_lock = threading.Lock()

        # Para reproducción
        self._is_playing = False

    async def initialize(self) -> None:
        """Inicializa el sistema de audio."""
        # Verificar dispositivos disponibles
        devices = sd.query_devices()
        logger.info(f"Dispositivos de audio disponibles: {len(devices)}")

        # Mostrar dispositivo de entrada predeterminado
        default_input = sd.query_devices(kind='input')
        logger.info(f"Dispositivo de entrada: {default_input['name']}")

        # Mostrar dispositivo de salida predeterminado
        default_output = sd.query_devices(kind='output')
        logger.info(f"Dispositivo de salida: {default_output['name']}")

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags
    ) -> None:
        """Callback para el stream de audio."""
        if status:
            logger.warning(f"Estado del stream de audio: {status}")

        # Copiar datos al buffer y cola
        audio_data = indata.copy().flatten()
        self.buffer.append(audio_data)
        self._audio_queue.put(audio_data)

    async def start_capture(self) -> None:
        """Inicia la captura de audio."""
        if self._running:
            return

        with self._stream_lock:
            self._running = True
            self._input_stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype=np.float32,
                blocksize=self.chunk_size,
                device=self.input_device,
                callback=self._audio_callback
            )
            self._input_stream.start()
            logger.info("Captura de audio iniciada")

    async def stop_capture(self) -> None:
        """Detiene la captura de audio."""
        if not self._running:
            return

        with self._stream_lock:
            self._running = False
            if self._input_stream:
                self._input_stream.stop()
                self._input_stream.close()
                self._input_stream = None
            logger.info("Captura de audio detenida")

    async def stream(self) -> AsyncIterator[np.ndarray]:
        """
        Genera chunks de audio de forma asíncrona.

        Yields:
            Arrays de audio numpy
        """
        while self._running:
            try:
                # Obtener chunk de la cola con timeout
                chunk = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._audio_queue.get(timeout=0.1)
                )
                yield chunk
            except queue.Empty:
                continue

    async def capture_until_silence(
        self,
        max_seconds: float = 10.0,
        silence_threshold_seconds: float = 1.5,
        pre_buffer_seconds: float = 0.5
    ) -> np.ndarray:
        """
        Captura audio hasta detectar silencio.

        Args:
            max_seconds: Máximo de segundos a capturar
            silence_threshold_seconds: Segundos de silencio para terminar
            pre_buffer_seconds: Segundos de audio previo a incluir

        Returns:
            Array de audio capturado
        """
        captured = []
        silence_samples = 0
        silence_threshold = int(silence_threshold_seconds * self.sample_rate)
        max_samples = int(max_seconds * self.sample_rate)
        total_samples = 0

        # Incluir audio previo del buffer si existe
        if pre_buffer_seconds > 0:
            pre_audio = self.buffer.get_last(pre_buffer_seconds, self.sample_rate)
            if len(pre_audio) > 0:
                captured.append(pre_audio)
                total_samples += len(pre_audio)

        logger.debug("Capturando audio hasta silencio...")

        async for chunk in self.stream():
            captured.append(chunk)
            total_samples += len(chunk)

            # Verificar VAD
            if not self.vad.is_speech(chunk):
                silence_samples += len(chunk)
            else:
                silence_samples = 0

            # Verificar condiciones de terminación
            if silence_samples >= silence_threshold:
                logger.debug(f"Silencio detectado después de {total_samples / self.sample_rate:.1f}s")
                break

            if total_samples >= max_samples:
                logger.debug(f"Máximo de captura alcanzado: {max_seconds}s")
                break

        return np.concatenate(captured) if captured else np.array([], dtype=np.float32)

    async def capture_duration(self, seconds: float) -> np.ndarray:
        """
        Captura una duración específica de audio.

        Args:
            seconds: Segundos a capturar

        Returns:
            Array de audio
        """
        samples_needed = int(seconds * self.sample_rate)
        captured = []
        total_samples = 0

        async for chunk in self.stream():
            captured.append(chunk)
            total_samples += len(chunk)

            if total_samples >= samples_needed:
                break

        result = np.concatenate(captured)
        return result[:samples_needed]

    async def play(self, audio_data: np.ndarray, sample_rate: Optional[int] = None) -> None:
        """
        Reproduce audio.

        Args:
            audio_data: Array de audio a reproducir
            sample_rate: Tasa de muestreo (usa la predeterminada si no se especifica)
        """
        if self._is_playing:
            logger.warning("Ya hay audio reproduciéndose")
            return

        sr = sample_rate or self.sample_rate
        self._is_playing = True

        try:
            # Usar run_in_executor para no bloquear
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: sd.play(audio_data, sr, device=self.output_device)
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                sd.wait
            )
        finally:
            self._is_playing = False

    async def play_file(self, file_path: str) -> None:
        """
        Reproduce un archivo de audio.

        Args:
            file_path: Ruta al archivo de audio
        """
        data, sr = sf.read(file_path)
        await self.play(data, sr)

    async def play_bytes(self, audio_bytes: bytes, sample_rate: Optional[int] = None) -> None:
        """
        Reproduce audio desde bytes.

        Args:
            audio_bytes: Bytes de audio (WAV)
            sample_rate: Tasa de muestreo
        """
        data, sr = sf.read(BytesIO(audio_bytes))
        await self.play(data, sample_rate or sr)

    def get_buffer_audio(self, seconds: float) -> np.ndarray:
        """
        Obtiene audio del buffer circular.

        Args:
            seconds: Segundos de audio a obtener

        Returns:
            Array de audio
        """
        return self.buffer.get_last(seconds, self.sample_rate)

    def clear_buffer(self) -> None:
        """Limpia el buffer de audio."""
        self.buffer.clear()

    @property
    def is_capturing(self) -> bool:
        """Verifica si se está capturando audio."""
        return self._running

    @property
    def is_playing(self) -> bool:
        """Verifica si se está reproduciendo audio."""
        return self._is_playing

    async def close(self) -> None:
        """Cierra el gestor de audio."""
        await self.stop_capture()
        logger.info("AudioManager cerrado")

    @staticmethod
    def list_devices() -> list:
        """Lista todos los dispositivos de audio disponibles."""
        return sd.query_devices()

    @staticmethod
    def audio_to_bytes(audio: np.ndarray, sample_rate: int = 16000) -> bytes:
        """Convierte audio numpy a bytes WAV."""
        buffer = BytesIO()
        sf.write(buffer, audio, sample_rate, format='WAV')
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def bytes_to_audio(audio_bytes: bytes) -> tuple:
        """Convierte bytes WAV a audio numpy."""
        buffer = BytesIO(audio_bytes)
        data, sr = sf.read(buffer)
        return data, sr
