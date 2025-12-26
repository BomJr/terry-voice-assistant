#!/usr/bin/env python3
"""
Test de wake word detection con debug detallado
"""

from terry.core.voice.stt import SpeechToText
from terry.core.voice.tts import TextToSpeech
import time


def test_wake_word_detection():
    """Test de detección de wake word."""
    print("\n" + "=" * 60)
    print("🧪 TEST DE WAKE WORD DETECTION")
    print("=" * 60)

    # Inicializar STT
    print("\n1. Inicializando STT...")
    stt = SpeechToText(
        language="es",
        model_size="tiny",
        use_whisper=False,
        energy_threshold=150
    )
    print("   ✅ STT listo")

    # Inicializar TTS
    print("\n2. Inicializando TTS...")
    tts = TextToSpeech(rate=200, volume=0.95)
    print("   ✅ TTS listo")

    wake_words = ["terry", "hey mac", "oye mac"]

    print("\n" + "=" * 60)
    print("📋 INSTRUCCIONES:")
    print("=" * 60)
    print("Voy a escuchar 5 veces.")
    print("Prueba diferentes combinaciones:\n")
    print("  1. Solo wake word: 'terry'")
    print("  2. Wake word + comando: 'terry hola'")
    print("  3. Wake word + comando: 'hey mac qué hora es'")
    print("  4. Sin wake word: 'hola' (no debería detectar)")
    print("  5. Wake word al final: 'hola terry' (debería detectar)")
    print("\nPresiona ENTER para comenzar...")
    input()

    for i in range(1, 6):
        print("\n" + "=" * 60)
        print(f"TEST {i}/5")
        print("=" * 60)
        print("💤 Esperando wake word...")
        print(f"   Wake words válidos: {wake_words}")
        print("   (habla ahora...)")

        detected, comando = stt.listen_for_wake_word(
            wake_words=wake_words,
            timeout=10
        )

        print("\n📊 RESULTADO:")
        print(f"   Wake word detectado: {detected}")
        print(f"   Comando extraído: {comando if comando else 'None'}")

        if detected:
            print("\n✅ WAKE WORD DETECTADO!")
            # Reproducir beep de confirmación
            print("   🔔 Reproduciendo beep...")
            tts.play_beep()

            if comando:
                print(f"   📝 Comando a procesar: '{comando}'")
                # Simular respuesta
                tts.speak("Comando recibido")
            else:
                print("   ℹ️  Solo wake word, esperando comando...")
        else:
            print("\n❌ NO SE DETECTÓ WAKE WORD")
            print("   (o timeout)")

        time.sleep(1)

    print("\n" + "=" * 60)
    print("✅ TEST COMPLETADO")
    print("=" * 60)


def test_continuous_listening():
    """Test de escucha continua sin wake word."""
    print("\n" + "=" * 60)
    print("🧪 TEST DE ESCUCHA CONTINUA (SIN WAKE WORD)")
    print("=" * 60)

    print("\n1. Inicializando componentes...")
    stt = SpeechToText(
        language="es",
        model_size="tiny",
        use_whisper=False,
        energy_threshold=150
    )
    tts = TextToSpeech(rate=200, volume=0.95)
    print("   ✅ Listo")

    print("\n📋 INSTRUCCIONES:")
    print("Habla 3 veces sin wake word.")
    print("Debería escuchar todo lo que dices.\n")
    input("Presiona ENTER para comenzar...")

    for i in range(1, 4):
        print(f"\n{i}/3 - 🎤 Habla ahora...")

        text = stt.listen_once(timeout=10)

        if text:
            print(f"   ✅ Escuché: '{text}'")
            tts.speak(f"Escuché {text}")
        else:
            print("   ❌ No se detectó voz")

        time.sleep(1)

    print("\n✅ TEST COMPLETADO")


def main():
    print("\n" + "=" * 70)
    print("🔍 DIAGNÓSTICO DE WAKE WORD")
    print("=" * 70)

    print("\n¿Qué quieres probar?")
    print("  1) Wake word detection (recomendado)")
    print("  2) Escucha continua (sin wake word)")
    print("  3) Ambos")

    choice = input("\nSelecciona (1/2/3) [1]: ").strip() or "1"

    if choice in ["1", "3"]:
        test_wake_word_detection()

    if choice in ["2", "3"]:
        if choice == "3":
            input("\n\nPresiona ENTER para continuar con test continuo...")
        test_continuous_listening()

    print("\n" + "=" * 70)
    print("📋 RESUMEN")
    print("=" * 70)
    print("""
Si wake word NO funciona:
  → Verifica que dices claramente "terry", "hey mac" o "oye mac"
  → El wake word puede estar en cualquier parte: "terry hola" o "hola terry"
  → Verifica que el micrófono está captando bien

Si wake word funciona pero NO hace beep:
  → Problema con TTS beep (secundario, no afecta funcionalidad)

Si escucha continua funciona pero wake word NO:
  → Problema con la lógica de detección en listen_for_wake_word()
    """)


if __name__ == "__main__":
    main()
