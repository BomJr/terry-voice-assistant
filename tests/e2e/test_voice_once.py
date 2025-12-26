#!/usr/bin/env python3
"""
Test de una ronda completa de voz
"""

import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from terry.core.voice.pipeline import VoicePipeline

async def main():
    """Ejecuta un solo ciclo de voz."""
    pipeline = VoicePipeline(
        wake_word_enabled=False,
        tts_enabled=True,
        language="es"
    )

    print("=" * 60)
    print("🎤 TEST DE VOZ - UN SOLO COMANDO")
    print("=" * 60)
    print("Di un comando de prueba (ej: 'pon música')")
    print("=" * 60)

    # Saludo
    if pipeline.tts:
        pipeline.tts.speak("Hola, di un comando de prueba")

    # Un solo ciclo
    success = await pipeline.run_once()

    if success:
        print("\n✅ Test de voz completado correctamente")
    else:
        print("\n❌ Test de voz falló")

    # Despedida
    if pipeline.tts:
        pipeline.tts.speak("Test completado")

if __name__ == "__main__":
    asyncio.run(main())
