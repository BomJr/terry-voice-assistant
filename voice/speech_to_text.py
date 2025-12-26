"""
Home-Alexa - Speech-to-Text con Whisper
Reconocimiento de voz mejorado con cancelación de ruido
"""

import speech_recognition as sr
import whisper
import numpy as np
from typing import Optional
from utils.logger import get_logger
import tempfile
import os

logger = get_logger(__name__)


class SpeechToText:
    """Speech-to-Text mejorado con Whisper y cancelación de ruido."""

    def __init__(
        self,
        language: str = "es",
        model_size: str = "tiny",  # tiny para speed (solo fallback)
        use_whisper: bool = False,  # Google primero (más rápido)
        energy_threshold: int = 300,
        dynamic_energy: bool = True,
        pause_threshold: float = 0.5,  # Más rápido
        microphone_index: Optional[int] = None  # v6.0 - Selección manual de micrófono
    ):
        """
        Inicializa STT con Whisper.

        Args:
            language: Idioma (es, en)
            model_size: Tamaño del modelo Whisper (tiny, base, small, medium, large)
            use_whisper: Si usar Whisper (más preciso) o Google API
            energy_threshold: Umbral de energía del micrófono (300-4000)
            dynamic_energy: Ajuste automático de energía
            pause_threshold: Segundos de silencio antes de procesar
            microphone_index: Índice del micrófono a usar (None = default)
        """
        self.language = language
        self.use_whisper = use_whisper
        self.microphone_index = microphone_index

        # Recognizer con configuración mejorada
        self.recognizer = sr.Recognizer()

        # Configuración de energía (más sensible para mejor detección)
        self.recognizer.energy_threshold = energy_threshold
        self.recognizer.dynamic_energy_threshold = dynamic_energy
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5

        # Configuración de pausas
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5

        # Cargar Whisper si está habilitado
        self.whisper_model = None
        if use_whisper:
            try:
                logger.info(f"Cargando Whisper modelo '{model_size}'...")
                self.whisper_model = whisper.load_model(model_size)
                logger.info("✅ Whisper cargado correctamente")
            except Exception as e:
                logger.error(f"Error cargando Whisper: {e}")
                logger.warning("Fallback a Google Speech Recognition")
                self.use_whisper = False

    def _reduce_noise(self, audio_data: sr.AudioData) -> sr.AudioData:
        """
        Reduce el ruido del audio.

        Args:
            audio_data: Audio original

        Returns:
            Audio con ruido reducido
        """
        try:
            # Convertir a numpy array
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)

            # Reducción de ruido simple (high-pass filter)
            # Elimina frecuencias bajas (ruido de fondo)
            from scipy import signal

            # High-pass filter at 80Hz (elimina ruido de bajo)
            sos = signal.butter(10, 80, 'hp', fs=audio_data.sample_rate, output='sos')
            filtered = signal.sosfilt(sos, audio_array)

            # Normalizar
            filtered = np.clip(filtered, -32768, 32767).astype(np.int16)

            # Convertir de vuelta a AudioData
            return sr.AudioData(
                filtered.tobytes(),
                audio_data.sample_rate,
                audio_data.sample_width
            )
        except Exception as e:
            logger.warning(f"Error en reducción de ruido: {e}")
            return audio_data

    def listen_once(
        self,
        timeout: Optional[int] = None,
        phrase_time_limit: Optional[int] = None,
        show_all: bool = False
    ) -> Optional[str]:
        """
        Escucha una vez y retorna el texto.

        Args:
            timeout: Tiempo máximo de espera (segundos)
            phrase_time_limit: Tiempo máximo de grabación (segundos)
            show_all: Si mostrar información de debug

        Returns:
            Texto reconocido o None si falla
        """
        try:
            # v6.0 - Usar micrófono específico si está configurado
            mic_kwargs = {"device_index": self.microphone_index} if self.microphone_index is not None else {}
            with sr.Microphone(**mic_kwargs) as source:
                # Ajuste de ruido ambiente (solo primera vez, ultra-rápido)
                if not hasattr(self, '_ambient_adjusted'):
                    original_threshold = self.recognizer.energy_threshold
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.2)  # Más rápido
                    auto_threshold = self.recognizer.energy_threshold

                    # v6.0 - Forzar threshold bajo para garantizar detección
                    # Si el auto-calibrado es muy alto (>200), forzar a 200 máximo
                    if auto_threshold > 200:
                        logger.info(f"Umbral auto muy alto: {auto_threshold:.0f}, limitando a 200")
                        self.recognizer.energy_threshold = 200
                    else:
                        logger.info(f"Umbral calibrado: {auto_threshold:.0f}")

                    self._ambient_adjusted = True

                print("🎤 Habla ahora...")

                # Escuchar
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                print("🔄 Procesando...")

                # Reducir ruido
                audio = self._reduce_noise(audio)

                # Reconocimiento: SIEMPRE Google primero (más rápido)
                # Solo Whisper si Google falla
                text = self._recognize_google(audio)
                if not text and self.whisper_model:
                    text = self._recognize_whisper(audio)

                if text:
                    return text.lower().strip()

                return None

        except sr.WaitTimeoutError:
            logger.warning("Timeout esperando audio")
            return None
        except sr.UnknownValueError:
            print("❌ No te entendí, intenta de nuevo")
            logger.warning("Audio no reconocido")
            return None
        except sr.RequestError as e:
            logger.error(f"Error en servicio de reconocimiento: {e}")
            return None
        except Exception as e:
            logger.error(f"Error en listen_once: {e}")
            return None

    def _recognize_whisper(self, audio: sr.AudioData) -> Optional[str]:
        """
        Reconoce audio usando Whisper.

        Args:
            audio: Audio a reconocer

        Returns:
            Texto reconocido
        """
        try:
            # Guardar audio temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                f.write(audio.get_wav_data())
                temp_file = f.name

            try:
                # Transcribir con Whisper
                result = self.whisper_model.transcribe(
                    temp_file,
                    language=self.language,
                    fp16=False,  # Para compatibilidad
                    task="transcribe"
                )

                text = result["text"].strip()
                logger.info(f"Whisper: '{text}'")
                return text

            finally:
                # Limpiar archivo temporal
                try:
                    os.unlink(temp_file)
                except:
                    pass

        except Exception as e:
            logger.error(f"Error en Whisper: {e}")
            # Fallback a Google
            return self._recognize_google(audio)

    def _recognize_google(self, audio: sr.AudioData) -> Optional[str]:
        """
        Reconoce audio usando Google Speech Recognition (RÁPIDO).

        Args:
            audio: Audio a reconocer

        Returns:
            Texto reconocido
        """
        try:
            language_code = "es-ES" if self.language == "es" else "en-US"
            text = self.recognizer.recognize_google(audio, language=language_code)
            return text
        except (sr.UnknownValueError, sr.RequestError):
            return None

    def listen_for_wake_word(
        self,
        wake_words: list[str],
        timeout: int = 10
    ) -> tuple[bool, Optional[str]]:
        """
        Escucha hasta detectar una wake word y extrae comando (tipo Alexa).

        Args:
            wake_words: Lista de palabras de activación (ej: ["terry", "hey mac"])
            timeout: Tiempo máximo de espera

        Returns:
            (wake_word_detected, comando_extraido)
            Ejemplos:
            - "terry pon música" → (True, "pon música")
            - "oye mac qué tiempo hace" → (True, "qué tiempo hace")
            - "hola" → (False, None)
        """
        try:
            text = self.listen_once(timeout=timeout, phrase_time_limit=10)

            if not text:
                return (False, None)

            # Comprobar si contiene alguna wake word
            text_lower = text.lower()
            for wake_word in wake_words:
                wake_word_lower = wake_word.lower()
                if wake_word_lower in text_lower:
                    logger.info(f"✅ Wake word detectada: '{wake_word}'")

                    # Extraer comando después del wake word (tipo Alexa)
                    # Ejemplo: "terry pon música" → "pon música"
                    parts = text_lower.split(wake_word_lower, 1)
                    if len(parts) > 1 and parts[1].strip():
                        comando = parts[1].strip()
                        logger.info(f"📝 Comando extraído: '{comando}'")
                        return (True, comando)
                    else:
                        # Solo wake word, sin comando
                        return (True, None)

            return (False, None)

        except Exception as e:
            logger.error(f"Error en listen_for_wake_word: {e}")
            return (False, None)


def test_stt():
    """Test de Speech-to-Text."""
    print("\n🎤 TEST DE SPEECH-TO-TEXT (WHISPER)")
    print("=" * 50)

    # Crear STT con Whisper
    stt = SpeechToText(
        language="es",
        model_size="base",
        use_whisper=True,
        energy_threshold=300
    )

    print("\n✅ Micrófono OK")
    print("\nPrueba hablando:")
    print("  - Di algo en español")
    print("  - Espera a que termine de procesar")
    print()

    # Probar
    text = stt.listen_once()

    if text:
        print(f"\n✅ Reconocido: '{text}'")
    else:
        print("\n❌ No se reconoció nada")


if __name__ == "__main__":
    test_stt()
