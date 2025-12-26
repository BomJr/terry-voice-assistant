#!/usr/bin/env python3
"""
Test que simula cómo el pipeline usa el TTS - una sola instancia reutilizada
"""

from terry.core.voice.tts import TextToSpeech
import time


def test_multiple_calls():
    """Simula múltiples llamadas al TTS como en el pipeline."""
    print("\n" + "=" * 60)
    print("🧪 TEST DE TTS CON REUTILIZACIÓN (como en pipeline)")
    print("=" * 60)

    # Crear UNA sola instancia (como en VoicePipeline)
    print("\n1. Creando instancia de TTS...")
    tts = TextToSpeech(rate=200, volume=0.95, optimize_for_voice=True)
    print("   ✅ TTS creado")

    # Simular 5 interacciones seguidas
    frases = [
        "Hola, ¿en qué puedo ayudarte?",
        "Reproduciendo música",
        "Subiendo volumen",
        "Siguiente canción",
        "Pausando música"
    ]

    for i, frase in enumerate(frases, 1):
        print(f"\n{i}. Hablando: '{frase}'")
        print(f"   Llamando a tts.speak()...")

        try:
            tts.speak(frase)
            print(f"   ✅ Completado")

            # Pequeña pausa entre frases (como en el pipeline)
            time.sleep(0.5)

        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Preguntar si se escuchó
        respuesta = input(f"   ¿Escuchaste la frase #{i}? (s/n): ").lower()
        if respuesta != 's':
            print(f"   ⚠️  ¡Fallo en frase #{i}!")
            print(f"   El TTS se atascó después de {i-1} llamadas exitosas")
            return i

    print("\n✅ TODAS las frases se escucharon correctamente!")
    print("   El TTS funciona bien con reutilización")
    return 0


def test_with_engine_reset():
    """Test con reinicialización del engine entre llamadas."""
    print("\n" + "=" * 60)
    print("🔧 TEST CON REINICIALIZACIÓN DEL ENGINE")
    print("=" * 60)

    import pyttsx3

    print("\nIntentando hablar 3 veces, reinicializando el engine cada vez:")

    for i in range(1, 4):
        print(f"\n{i}. Creando NUEVO engine...")
        engine = pyttsx3.init()
        engine.setProperty('rate', 200)
        engine.setProperty('volume', 0.95)

        # Seleccionar voz Paulina
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'paulina' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        frase = f"Prueba número {i}"
        print(f"   Hablando: '{frase}'")

        try:
            engine.say(frase)
            engine.runAndWait()
            # IMPORTANTE: Destruir el engine
            del engine
            print(f"   ✅ Completado")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        respuesta = input(f"   ¿Escuchaste? (s/n): ").lower()
        if respuesta != 's':
            print(f"   ⚠️  Fallo en intento #{i}")
            return False

    print("\n✅ TODAS las frases funcionaron con reinicialización!")
    return True


def main():
    print("\n" + "=" * 70)
    print("🔍 DIAGNÓSTICO DE PROBLEMA INTERMITENTE DE TTS")
    print("=" * 70)

    # Test 1: Reutilización (como hace el pipeline ahora)
    fallo_en = test_multiple_calls()

    if fallo_en > 0:
        print("\n" + "=" * 70)
        print("❌ PROBLEMA IDENTIFICADO:")
        print("=" * 70)
        print(f"El TTS funciona las primeras {fallo_en-1} veces pero luego falla.")
        print("Esto sugiere que el engine de pyttsx3 necesita reinicializarse.")
        print("\nProbando solución...")

        # Test 2: Con reinicialización
        if test_with_engine_reset():
            print("\n" + "=" * 70)
            print("✅ SOLUCIÓN ENCONTRADA:")
            print("=" * 70)
            print("Reinicializar el engine de pyttsx3 entre llamadas soluciona el problema.")
            print("\nVoy a modificar el código para implementar esto.")
    else:
        print("\n" + "=" * 70)
        print("🤔 RESULTADO INESPERADO:")
        print("=" * 70)
        print("El TTS funcionó perfectamente con reutilización.")
        print("El problema debe estar en otro lugar del pipeline.")


if __name__ == "__main__":
    main()
