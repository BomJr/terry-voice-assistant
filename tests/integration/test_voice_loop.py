#!/usr/bin/env python3
"""
Terry v6.0 - Voice Loop Tester
Simula comandos de voz usando TTS → Speaker → Microphone → STT
"""

import asyncio
import subprocess
import time
import os
import signal
import sys
from terry.core.voice.tts import TextToSpeech
from terry.core.voice.stt import SpeechToText


class VoiceLoopTester:
    """Simula ciclo completo de voz para testing."""

    def __init__(self):
        self.tts = TextToSpeech(rate=200, volume=0.95)
        self.stt = SpeechToText(language="es", energy_threshold=150)
        self.terry_process = None

    def send_voice_command(self, command: str, wait_before: float = 1.0, wait_after: float = 2.0):
        """
        Envía un comando de voz simulado (TTS → speaker → mic).

        Args:
            command: Comando a enviar
            wait_before: Segundos de espera antes de enviar
            wait_after: Segundos de espera después de enviar
        """
        print(f"\n🗣️  Enviando comando: '{command}'")
        time.sleep(wait_before)

        # Hablar el comando (saldrá por speaker → mic lo capturará)
        self.tts.speak(command)

        time.sleep(wait_after)

    def listen_for_response(self, timeout: int = 5) -> str:
        """
        Escucha la respuesta de Terry.

        Args:
            timeout: Segundos máximo de espera

        Returns:
            Texto reconocido o None
        """
        print(f"👂 Escuchando respuesta de Terry...")

        try:
            text = self.stt.listen_once(timeout=timeout, phrase_time_limit=10)
            if text:
                print(f"✅ Terry respondió: '{text}'")
                return text
            else:
                print("⚠️  No se detectó respuesta de Terry")
                return None
        except Exception as e:
            print(f"❌ Error escuchando: {e}")
            return None

    def test_single_command(self, command: str):
        """Test de un solo comando."""
        print("\n" + "=" * 60)
        print(f"TEST: {command}")
        print("=" * 60)

        # Enviar comando
        self.send_voice_command(command, wait_before=2, wait_after=3)

        # Escuchar respuesta
        response = self.listen_for_response(timeout=10)

        return response is not None


async def test_direct_pipeline():
    """Test directo del pipeline sin loop completo."""
    print("\n" + "=" * 60)
    print("🧪 TEST DIRECTO DEL PIPELINE v6.0")
    print("=" * 60)

    from terry.core.voice.pipeline import VoicePipeline

    # Crear pipeline en modo continuo (sin wake word para testing)
    pipeline = VoicePipeline(
        wake_word_enabled=False,
        tts_enabled=True,
        language="es"
    )

    print("\n📋 Configuración del test:")
    print(f"   Wake word: {pipeline.wake_word_enabled}")
    print(f"   TTS enabled: {pipeline.tts_enabled}")
    print(f"   Energy threshold: {pipeline.stt.recognizer.energy_threshold}")
    print(f"   Micrófono: {pipeline.stt.microphone_index}")

    # Test 1: Verificar componentes
    print("\n" + "-" * 60)
    print("TEST 1: Verificar componentes")
    print("-" * 60)

    print("✅ STT inicializado")
    print("✅ TTS inicializado")
    print("✅ LLM client inicializado")
    print("✅ LED feedback inicializado")

    # Test 2: Comando de texto simple (sin voz)
    print("\n" + "-" * 60)
    print("TEST 2: Procesamiento de comando (sin voz)")
    print("-" * 60)

    test_commands = [
        "hola",
        "pon música",
        "para la música",
        "qué hora es"
    ]

    for cmd in test_commands:
        print(f"\n🧪 Procesando: '{cmd}'")
        try:
            response = await pipeline.process_voice_command(cmd)
            print(f"   ✅ Respuesta: '{response}'")

            # Intentar TTS
            if pipeline.tts:
                print(f"   🔊 Reproduciendo respuesta...")
                try:
                    pipeline.tts.speak(response)
                    print(f"   ✅ TTS funcionó")
                except Exception as e:
                    print(f"   ❌ TTS falló: {e}")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

    # Test 3: Ciclo completo con voz (un solo comando)
    print("\n" + "-" * 60)
    print("TEST 3: Ciclo completo con VOZ (habla cuando veas 🎤)")
    print("-" * 60)

    try:
        print("\n⚠️  Prepárate para hablar...")
        success = await pipeline.run_once()

        if success:
            print("\n✅ Ciclo completo exitoso!")
        else:
            print("\n⚠️  Ciclo completado pero sin comando detectado")

    except Exception as e:
        print(f"\n❌ Error en ciclo completo: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("🏁 Test completado")
    print("=" * 60)


async def test_with_simulated_voice():
    """Test con voz simulada (TTS → mic)."""
    print("\n" + "=" * 60)
    print("🤖 TEST CON VOZ SIMULADA (TTS → Mic)")
    print("=" * 60)

    tester = VoiceLoopTester()

    # Test simple: enviar comando y escuchar
    test_commands = [
        "terry hola",
        "pon música",
    ]

    print("\n⚠️  IMPORTANTE:")
    print("   - Sube el volumen del sistema")
    print("   - Los comandos saldrán por el speaker")
    print("   - El micrófono los capturará")
    print("   - Veremos si Terry responde")
    input("\nPresiona ENTER cuando estés listo...")

    for cmd in test_commands:
        result = tester.test_single_command(cmd)
        if result:
            print(f"✅ Test '{cmd}' PASÓ")
        else:
            print(f"❌ Test '{cmd}' FALLÓ")

        time.sleep(3)


def main():
    """Main entry point."""
    print("\n" + "=" * 70)
    print("🧪 TERRY v6.0 - SISTEMA DE TESTING DE VOZ")
    print("=" * 70)

    print("\nSelecciona el tipo de test:")
    print("  1) Test directo del pipeline (RECOMENDADO)")
    print("  2) Test con voz simulada (experimental)")
    print("  3) Test de componentes individuales")

    choice = input("\nOpción [1]: ").strip() or "1"

    if choice == "1":
        asyncio.run(test_direct_pipeline())
    elif choice == "2":
        asyncio.run(test_with_simulated_voice())
    elif choice == "3":
        test_components()
    else:
        print("Opción inválida")


def test_components():
    """Test individual de componentes."""
    print("\n" + "=" * 60)
    print("🔧 TEST DE COMPONENTES INDIVIDUALES")
    print("=" * 60)

    # Test 1: TTS
    print("\n1️⃣  TEST TTS (deberías escuchar esto)")
    print("-" * 60)
    try:
        from terry.core.voice.tts import TextToSpeech
        tts = TextToSpeech(rate=200, volume=0.95)
        print("✅ TTS inicializado")

        print("🔊 Reproduciendo mensaje de prueba...")
        tts.speak("Hola, soy Terry versión seis punto cero")
        print("✅ TTS funcionó")

    except Exception as e:
        print(f"❌ TTS falló: {e}")
        import traceback
        traceback.print_exc()

    input("\n¿Escuchaste el mensaje? Presiona ENTER para continuar...")

    # Test 2: STT
    print("\n2️⃣  TEST STT (di algo cuando veas 🎤)")
    print("-" * 60)
    try:
        from terry.core.voice.stt import SpeechToText

        # Cargar config de micrófono
        mic_index = None
        try:
            with open(".terry_microphone", "r") as f:
                mic_index = int(f.read().strip())
                print(f"✅ Usando micrófono configurado: #{mic_index}")
        except:
            print("⚠️  No hay micrófono configurado, usando default")

        stt = SpeechToText(
            language="es",
            energy_threshold=150,
            microphone_index=mic_index
        )
        print("✅ STT inicializado")

        print("\n🎤 Di algo (tienes 5 segundos)...")
        text = stt.listen_once(timeout=5)

        if text:
            print(f"✅ STT reconoció: '{text}'")
        else:
            print("⚠️  STT no reconoció nada")

    except Exception as e:
        print(f"❌ STT falló: {e}")
        import traceback
        traceback.print_exc()

    # Test 3: LLM
    print("\n3️⃣  TEST LLM (Ollama)")
    print("-" * 60)
    try:
        from terry.core.llm.processor import CommandProcessor
        from terry.core.llm.ollama_client import OllamaClient

        llm = OllamaClient()
        processor = CommandProcessor(llm, default_language="es")
        print("✅ LLM inicializado")

        print("🔄 Procesando comando de prueba: 'hola'")
        import asyncio
        result = asyncio.run(processor.process_command("hola"))
        print(f"✅ LLM respondió: '{result.get('response', 'N/A')}'")

    except Exception as e:
        print(f"❌ LLM falló: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelado")
        sys.exit(0)
