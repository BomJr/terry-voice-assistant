"""
Home-Alexa - Text to Speech mejorado
Voces más naturales y optimización de respuestas
"""

import pyttsx3
from typing import Optional
import threading
import re
from utils.logger import get_logger

logger = get_logger(__name__)


class TextToSpeech:
    """Text-to-Speech mejorado con voces más naturales."""

    # Voces preferidas en orden (macOS)
    PREFERRED_VOICES_ES = [
        "Mónica",      # Español España - Muy natural
        "Paulina",     # Español México - Muy natural
        "Jorge",       # Español España (Masculina)
        "Juan",        # Español México (Masculina)
        "Diego"        # Español Latinoamérica
    ]

    def __init__(
        self,
        rate: int = 190,  # Más lento = más natural
        volume: float = 0.95,
        voice_name: Optional[str] = None,
        optimize_for_voice: bool = True,
        simplify_responses: bool = True  # v6.0 - Simplificar tipo Alexa
    ):
        """
        Inicializa Text-to-Speech mejorado.

        Args:
            rate: Velocidad de habla (150-200 = natural, 200+ = rápido)
            volume: Volumen (0.0 a 1.0)
            voice_name: Nombre de voz específica o None para automático
            optimize_for_voice: Si optimizar respuestas para TTS
            simplify_responses: Si simplificar respuestas (Alexa-style: "Reproduciendo música" → "Reproduciendo")
        """
        # Guardar configuración (v6.0 fix - para reinicialización)
        self.rate = rate
        self.volume = volume
        self.optimize_for_voice = optimize_for_voice
        self.simplify_responses = simplify_responses
        self.voice_name = voice_name
        self.selected_voice_id = None  # Se guardará después de seleccionar

        # Inicializar engine
        self.engine = None
        self._init_engine()

    def _init_engine(self):
        """
        Inicializa o reinicializa el engine de pyttsx3 (v6.0 fix).

        Fix para bug de macOS donde el engine se atasca después de 2-3 llamadas.
        """
        # Destruir engine anterior si existe
        if self.engine is not None:
            try:
                self.engine.stop()
                del self.engine
            except:
                pass

        # Crear nuevo engine
        self.engine = pyttsx3.init()

        # Aplicar configuración
        self.engine.setProperty('rate', self.rate)
        self.engine.setProperty('volume', self.volume)

        # Seleccionar voz
        if self.selected_voice_id:
            # Reutilizar voz previamente seleccionada
            try:
                self.engine.setProperty('voice', self.selected_voice_id)
            except:
                # Si falla, reseleccionar
                if self.voice_name:
                    self.set_voice(self.voice_name)
                else:
                    self._set_best_spanish_voice()
        else:
            # Primera vez: seleccionar voz
            if self.voice_name:
                self.set_voice(self.voice_name)
            else:
                self._set_best_spanish_voice()

    def _set_best_spanish_voice(self):
        """Selecciona la mejor voz en español disponible."""
        voices = self.engine.getProperty('voices')

        # Intentar voces preferidas en orden
        for preferred in self.PREFERRED_VOICES_ES:
            for voice in voices:
                if preferred.lower() in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    self.selected_voice_id = voice.id  # Guardar para reinicialización
                    logger.info(f"✅ Voz seleccionada: {voice.name}")
                    return

        # Si no encuentra preferidas, buscar cualquier voz en español
        for voice in voices:
            # Buscar voces con español en el nombre o idioma
            if any(marker in voice.name.lower() for marker in ['monica', 'paulina', 'spanish', 'español']):
                self.engine.setProperty('voice', voice.id)
                self.selected_voice_id = voice.id  # Guardar para reinicialización
                logger.info(f"Voz en español: {voice.name}")
                return

            # Buscar por código de idioma
            if hasattr(voice, 'languages') and voice.languages:
                for lang in voice.languages:
                    if 'es_' in lang.lower() or 'spanish' in lang.lower():
                        self.engine.setProperty('voice', voice.id)
                        self.selected_voice_id = voice.id  # Guardar para reinicialización
                        logger.info(f"Voz español encontrada: {voice.name}")
                        return

        # Última opción: usar voz por defecto
        if voices:
            self.engine.setProperty('voice', voices[0].id)
            self.selected_voice_id = voices[0].id  # Guardar para reinicialización
            logger.warning(f"Usando voz por defecto: {voices[0].name}")

    def set_voice(self, voice_name: str):
        """
        Establece una voz específica.

        Args:
            voice_name: Nombre de la voz
        """
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if voice_name.lower() in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                self.selected_voice_id = voice.id  # Guardar para reinicialización
                logger.info(f"Voz cambiada a: {voice.name}")
                return

        logger.warning(f"Voz '{voice_name}' no encontrada")

    def _optimize_text_for_speech(self, text: str) -> str:
        """
        Optimiza el texto para que suene más natural al hablar.

        Args:
            text: Texto original

        Returns:
            Texto optimizado
        """
        if not self.optimize_for_voice:
            return text

        # 1. Remover emojis y símbolos especiales
        text = re.sub(r'[🎵🔊🎤🤖💬📁🔍⚡🔒❌✅🎯🎉💡📊🔧⚙️🎮🎨🎬🎭🎪🎺🎸🎹🎼🎧📻📺📷📸📹📽️🎥🎬]', '', text)

        # 2. Simplificar respuestas largas
        # Remover explicaciones técnicas entre paréntesis
        text = re.sub(r'\([^)]+\)', '', text)

        # 3. Convertir abreviaciones comunes
        replacements = {
            'ej.': 'ejemplo',
            'pág.': 'página',
            'etc.': 'etcétera',
            'vs.': 'versus',
            'Dr.': 'Doctor',
            'Sr.': 'Señor',
            'Sra.': 'Señora',
        }

        for abbr, full in replacements.items():
            text = text.replace(abbr, full)

        # 4. Mejorar puntuación para pausas naturales
        # Añadir pausas después de frases
        text = text.replace('. ', ', ')  # Pausas más cortas
        text = text.replace('...', '.')  # Remover puntos suspensivos

        # 5. Simplificar respuestas comunes (v6.0 - configurable)
        if self.simplify_responses:
            simple_responses = {
                'Reproduciendo música': 'Reproduciendo',
                'Pausando música': 'Pausando',
                'Siguiente canción': 'Siguiente',
                'Canción anterior': 'Anterior',
                'Subiendo volumen': 'Subiendo',
                'Bajando volumen': 'Bajando',
                'Abriendo aplicación': 'Abriendo',
                'Cerrando ventana': 'Cerrando',
            }

            for long, short in simple_responses.items():
                if long in text:
                    text = text.replace(long, short)

        # 6. Limpiar espacios extras
        text = ' '.join(text.split())

        return text.strip()

    def speak(self, text: str, wait: bool = True, force: bool = False):
        """
        Habla el texto de forma optimizada.

        Args:
            text: Texto a decir
            wait: Si esperar a que termine de hablar
            force: Si True, ignora silent mode (v6.1)
        """
        if not text:
            return

        # v6.1 - Silent Mode Support
        from utils.silent_mode import is_silent

        # Optimizar texto primero
        optimized_text = self._optimize_text_for_speech(text)

        # v6.1 - Visual Notifications
        try:
            from visual.notification_manager import get_notification_manager
            notification_mgr = get_notification_manager()
            notification_mgr.show(optimized_text, title="Terry", sound=False)
        except Exception as e:
            logger.debug(f"Notification error: {e}")

        if is_silent() and not force:
            logger.info(f"🔇 Silent mode: '{optimized_text}' (solo visual)")
            # Mostrar en pantalla en lugar de hablar
            print(f"   💬 Terry: {optimized_text}")
            return

        logger.info(f"🔊 Diciendo: {optimized_text}")

        try:
            # v6.0 FIX: Reinicializar engine antes de hablar
            # Soluciona bug de macOS donde engine se atasca después de 2-3 llamadas
            self._init_engine()

            if wait:
                # Modo síncrono
                self.engine.say(optimized_text)
                self.engine.runAndWait()
            else:
                # Modo asíncrono (en segundo plano)
                thread = threading.Thread(
                    target=lambda: (
                        self.engine.say(optimized_text),
                        self.engine.runAndWait()
                    ),
                    daemon=True
                )
                thread.start()

        except Exception as e:
            logger.error(f"Error en TTS: {e}")

    def speak_fast(self, text: str):
        """
        Habla el texto más rápido (para comandos simples).

        Args:
            text: Texto a decir
        """
        # Guardar velocidad original
        original_rate = self.engine.getProperty('rate')

        try:
            # Aumentar velocidad temporalmente
            self.engine.setProperty('rate', original_rate + 30)
            self.speak(text, wait=True)
        finally:
            # Restaurar velocidad
            self.engine.setProperty('rate', original_rate)

    def list_voices(self):
        """Lista todas las voces disponibles."""
        voices = self.engine.getProperty('voices')
        print("\n🔊 VOCES DISPONIBLES:")
        print("=" * 60)
        for i, voice in enumerate(voices, 1):
            print(f"{i}. {voice.name}")
            print(f"   ID: {voice.id}")
            print(f"   Idiomas: {voice.languages}")
            print()

    def play_beep(self, beep_type: str = "wake"):
        """
        Reproduce diferentes pitidos según contexto (v6.0.1 UX).

        Args:
            beep_type: Tipo de beep
                - "wake": Wake word detectado (tono ascendente)
                - "listening": Escuchando comando (tono neutral)
                - "processing": Procesando (tono bajo)
                - "success": Acción exitosa (tono alto)
                - "error": Error (tono descendente)
        """
        try:
            import os
            import subprocess

            # Mapeo de beeps a sonidos del sistema macOS
            beep_sounds = {
                "wake": "/System/Library/Sounds/Tink.aiff",           # Agudo - wake word
                "listening": "/System/Library/Sounds/Pop.aiff",       # Neutral - escuchando
                "processing": "/System/Library/Sounds/Submarine.aiff", # Bajo - procesando
                "success": "/System/Library/Sounds/Glass.aiff",       # Alto - éxito
                "error": "/System/Library/Sounds/Basso.aiff"          # Descendente - error
            }

            sound_file = beep_sounds.get(beep_type, beep_sounds["wake"])

            # Reproducir sin bloquear (en background)
            subprocess.Popen(
                ["afplay", sound_file],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

        except Exception as e:
            # Fallback visual
            beep_emojis = {
                "wake": "🔔",
                "listening": "👂",
                "processing": "⚙️",
                "success": "✅",
                "error": "❌"
            }
            print(beep_emojis.get(beep_type, "🔔"))

    def stop(self):
        """Detiene el habla actual."""
        try:
            self.engine.stop()
        except:
            pass


def test_tts():
    """Función de prueba."""
    print("\n🔊 TEST DE TEXT-TO-SPEECH MEJORADO")
    print("=" * 50)

    tts = TextToSpeech(optimize_for_voice=True)

    # Listar voces
    tts.list_voices()

    print("\n✅ Probando voz optimizada:")
    tts.speak("Hola, soy tu asistente de Home-Alexa")

    print("\n✅ Test de comandos optimizados:")
    tts.speak("🎵 Reproduciendo música")
    tts.speak("⏸️ Pausando música")
    tts.speak("⏭️ Siguiente canción")

    print("\n✅ Test de respuesta compleja:")
    tts.speak("🎵 Sonando: Bohemian Rhapsody - Queen (Álbum: A Night at the Opera)")

    print("\n✅ Test completado")


if __name__ == "__main__":
    test_tts()
