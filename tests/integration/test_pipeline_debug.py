#!/usr/bin/env python3
"""Test de pipeline completo con debug detallado"""

import asyncio
from terry.core.voice.pipeline import VoicePipeline

async def test_pipeline_debug():
    print("=" * 60)
    print("🧪 TEST DE PIPELINE CON DEBUG")
    print("=" * 60)

    # Crear pipeline en modo wake word
    print("\n1. Creando pipeline...")
    print("   wake_word_enabled=True")
    print("   tts_enabled=True")

    pipeline = VoicePipeline(
        wake_word_enabled=True,
        tts_enabled=True,
        language="es"
    )

    print(f"   ✅ Pipeline creado")
    print(f"   - TTS enabled: {pipeline.tts_enabled}")
    print(f"   - TTS object: {pipeline.tts is not None}")
    print(f"   - Wake word: {pipeline.wake_word_enabled}")

    # Test 1: Procesar comando de texto (sin voz)
    print("\n2. Test de procesamiento de comando")
    test_commands = [
        "hola",
        "pon música",
        "para"
    ]

    for cmd in test_commands:
        print(f"\n   Comando: '{cmd}'")

        # Procesar
        response = await pipeline.process_voice_command(cmd)
        print(f"   Respuesta: '{response}'")
        print(f"   Tipo: {type(response)}")
        print(f"   Longitud: {len(response) if response else 0}")
        print(f"   Bool: {bool(response)}")

        # Intentar TTS
        print(f"\n   Verificando condiciones para TTS:")
        print(f"   - tts_enabled: {pipeline.tts_enabled}")
        print(f"   - tts is not None: {pipeline.tts is not None}")
        print(f"   - response: {bool(response)}")
        print(f"   - Condición completa: {pipeline.tts_enabled and pipeline.tts and response}")

        if pipeline.tts_enabled and pipeline.tts and response:
            print(f"   ✅ Ejecutando TTS...")
            try:
                pipeline.tts.speak(response)
                print(f"   ✅ TTS completado")
            except Exception as e:
                print(f"   ❌ TTS falló: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ⚠️  TTS omitido")
            if not pipeline.tts_enabled:
                print(f"      Razón: tts_enabled es False")
            if not pipeline.tts:
                print(f"      Razón: tts es None")
            if not response:
                print(f"      Razón: response está vacío")

        print()

    print("=" * 60)
    print("✅ TEST COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_pipeline_debug())
