#!/usr/bin/env python3
"""
Terry v6.0 - Microphone Selector
Helps select the correct microphone for voice input
"""

import speech_recognition as sr


def select_microphone():
    """Interactive microphone selection."""
    print("\n" + "=" * 60)
    print("🎤 TERRY v6.0 - SELECCIÓN DE MICRÓFONO")
    print("=" * 60)

    # List all microphones
    print("\n📋 Micrófonos disponibles:\n")
    mics = sr.Microphone.list_microphone_names()

    for index, name in enumerate(mics):
        print(f"   {index}: {name}")

    # Get user selection
    print("\n💡 Recomendaciones:")
    print("   - 'External Microphone' suele ser el micrófono integrado del Mac")
    print("   - 'Echo Dot' si tienes un Amazon Echo conectado")
    print("   - Si no estás seguro, prueba con 0 (default)")

    while True:
        try:
            choice = input("\n¿Qué micrófono quieres usar? [0]: ").strip()
            choice = choice if choice else "0"
            mic_index = int(choice)

            if 0 <= mic_index < len(mics):
                print(f"\n✅ Seleccionado: {mics[mic_index]}")

                # Test the microphone
                print("\n🔍 Probando micrófono...")
                recognizer = sr.Recognizer()

                with sr.Microphone(device_index=mic_index) as source:
                    print("🔧 Calibrando (1 segundo de silencio)...")
                    recognizer.adjust_for_ambient_noise(source, duration=1)
                    threshold = recognizer.energy_threshold

                    print(f"✅ Umbral de energía: {threshold:.0f}")

                    # Quick voice test
                    print("\n🗣️  Di 'hola' para probar...")
                    try:
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
                        import audioop
                        rms = audioop.rms(audio.get_raw_data(), 2)

                        print(f"   Nivel de voz detectado: {rms:.0f}")

                        if rms > threshold * 0.5:
                            print("   ✅ ¡Micrófono funcionando bien!")

                            # Save configuration
                            config_file = ".terry_microphone"
                            with open(config_file, "w") as f:
                                f.write(f"{mic_index}\n")

                            print(f"\n✅ Configuración guardada en {config_file}")
                            print(f"   Terry usará el micrófono #{mic_index} automáticamente")
                            print("\n💡 Ahora ejecuta: ./run_voice.sh")
                        else:
                            print(f"   ⚠️  Nivel muy bajo (umbral: {threshold:.0f})")
                            print("   Intenta hablar más fuerte o prueba otro micrófono")

                    except sr.WaitTimeoutError:
                        print("   ⚠️  No se detectó voz (timeout)")
                        print("   Intenta de nuevo o prueba otro micrófono")

                break
            else:
                print(f"⚠️  Índice fuera de rango (0-{len(mics)-1})")

        except ValueError:
            print("⚠️  Ingresa un número válido")
        except KeyboardInterrupt:
            print("\n\n👋 Cancelado")
            return

    print("\n" + "=" * 60)


if __name__ == "__main__":
    select_microphone()
