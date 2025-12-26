#!/usr/bin/env python3
"""
Test de wake word + comando en una sola frase
"terry pon música" sin esperar
"""

from terry.core.voice.stt import SpeechToText
from terry.core.voice.tts import TextToSpeech


def main():
    print("\n" + "=" * 60)
    print("🧪 TEST DE WAKE WORD + COMANDO EN UNA FRASE")
    print("=" * 60)

    print("\n📋 OBJETIVO:")
    print("Verificar que puedes decir 'terry pon música' TODO DE UNA VEZ")
    print("sin tener que esperar después del wake word.\n")

    # Configuración igual al pipeline
    stt = SpeechToText(
        language="es",
        use_whisper=False,
        energy_threshold=150,
        pause_threshold=0.8  # v6.0.1 - Pausas más largas
    )

    tts = TextToSpeech(rate=200, volume=0.95)

    wake_words = ["terry", "teri", "terri", "terrie", "hey mac", "oye mac"]

    print("=" * 60)
    print("🎤 PRUEBAS")
    print("=" * 60)
    print("\nDi estas frases TODO DE UNA VEZ:\n")
    print("  1. 'terry pon música'")
    print("  2. 'hey mac qué hora es'")
    print("  3. 'oye mac sube volumen'")
    print("\nPresiona ENTER para comenzar...")
    input()

    for i in range(1, 4):
        print(f"\n{'='*60}")
        print(f"PRUEBA {i}/3")
        print(f"{'='*60}")
        print("💤 Esperando wake word + comando...")
        print("   (di TODO en una frase, ejemplo: 'terry pon música')")

        detected, comando = stt.listen_for_wake_word(
            wake_words=wake_words,
            timeout=10
        )

        if detected:
            if comando:
                print(f"\n✅ ¡PERFECTO! Wake word detectado Y comando extraído:")
                print(f"   📝 Comando: '{comando}'")
                tts.speak("Comando recibido")
            else:
                print(f"\n⚠️  Wake word detectado pero SIN comando")
                print(f"   (dijiste solo 'terry' sin comando después)")
                tts.play_beep()
        else:
            print(f"\n❌ NO se detectó wake word")

    print("\n" + "=" * 60)
    print("📊 RESULTADO")
    print("=" * 60)
    print("""
✅ Si viste "Comando: 'pon música'" (o similar):
   → ¡Funciona! Puedes usar Terry diciendo todo de una vez

⚠️  Si solo detecta wake word pero no comando:
   → Habla más rápido sin pausas largas entre wake word y comando
   → O habla más lento para que pause_threshold no corte

❌ Si no detecta el wake word:
   → Verifica que dices "terry", "hey mac" o "oye mac" claramente
    """)


if __name__ == "__main__":
    main()
