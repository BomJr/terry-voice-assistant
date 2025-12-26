#!/usr/bin/env python3
"""
Test para verificar la configuración de simplify_responses
"""

from terry.core.voice.tts import TextToSpeech


def test_simplified():
    """Prueba con simplificación activada (estilo Alexa)."""
    print("\n" + "=" * 60)
    print("⚡ TEST CON SIMPLIFICACIÓN (ESTILO ALEXA)")
    print("=" * 60)

    tts = TextToSpeech(
        rate=200,
        volume=0.95,
        optimize_for_voice=True,
        simplify_responses=True  # Activado
    )

    frases = [
        "Reproduciendo música",
        "Subiendo volumen",
        "Siguiente canción",
        "Pausando música"
    ]

    print("\n✅ Debería decir versión CORTA (Alexa-style):\n")

    for i, frase in enumerate(frases, 1):
        print(f"{i}. Original: '{frase}'")
        # Simular optimización
        optimized = tts._optimize_text_for_speech(frase)
        print(f"   Optimizado: '{optimized}'")
        print(f"   Hablando...")
        tts.speak(frase)
        print()


def test_full():
    """Prueba con simplificación desactivada (completo)."""
    print("\n" + "=" * 60)
    print("🗣️  TEST SIN SIMPLIFICACIÓN (COMPLETO)")
    print("=" * 60)

    tts = TextToSpeech(
        rate=200,
        volume=0.95,
        optimize_for_voice=True,
        simplify_responses=False  # Desactivado
    )

    frases = [
        "Reproduciendo música",
        "Subiendo volumen",
        "Siguiente canción",
        "Pausando música"
    ]

    print("\n✅ Debería decir versión COMPLETA:\n")

    for i, frase in enumerate(frases, 1):
        print(f"{i}. Original: '{frase}'")
        # Simular optimización
        optimized = tts._optimize_text_for_speech(frase)
        print(f"   Optimizado: '{optimized}'")
        print(f"   Hablando...")
        tts.speak(frase)
        print()


def main():
    print("\n" + "=" * 70)
    print("🧪 TEST DE CONFIGURACIÓN simplify_responses")
    print("=" * 70)

    print("\n📋 COMPARACIÓN:")
    print("  simplify_responses=True  → 'Reproduciendo música' → 'Reproduciendo'")
    print("  simplify_responses=False → 'Reproduciendo música' → 'Reproduciendo música'")

    # Test 1: Con simplificación
    test_simplified()

    input("\nPresiona ENTER para probar SIN simplificación...")

    # Test 2: Sin simplificación
    test_full()

    print("\n" + "=" * 70)
    print("✅ TESTS COMPLETADOS")
    print("=" * 70)
    print("\nPara usar en Terry:")
    print("  🔹 Estilo Alexa (rápido):  ./run_voice.sh → Opción 1")
    print("  🔹 Completo (informativo): ./run_voice.sh → Opción 2")
    print()


if __name__ == "__main__":
    main()
