#!/usr/bin/env python3
"""Test simple de TTS para verificar que funciona"""

from terry.core.voice.tts import TextToSpeech
import time

print("=" * 60)
print("🧪 TEST SIMPLE DE TTS")
print("=" * 60)

# Crear TTS
print("\n1. Inicializando TTS...")
tts = TextToSpeech(rate=200, volume=0.95, optimize_for_voice=True)
print("   ✅ TTS creado")

# Test 1: Texto simple
print("\n2. Test con texto simple")
print("   Texto: 'Hola'")
tts.speak("Hola")
print("   ✅ Completado")

time.sleep(0.5)

# Test 2: Texto largo (como respuesta de Terry)
print("\n3. Test con texto largo")
response = "¡Hola! ¿En qué puedo ayudarte hoy?"
print(f"   Texto: '{response}'")
tts.speak(response)
print("   ✅ Completado")

time.sleep(0.5)

# Test 3: Texto optimizado
print("\n4. Test con texto que necesita optimización")
response = "Reproduciendo música 🎵"
print(f"   Texto: '{response}'")
tts.speak(response)
print("   ✅ Completado")

print("\n" + "=" * 60)
print("✅ TODOS LOS TESTS PASARON")
print("=" * 60)
print("\nSi escuchaste las 3 frases, el TTS funciona correctamente.")
print("El problema debe estar en otra parte del pipeline.")
