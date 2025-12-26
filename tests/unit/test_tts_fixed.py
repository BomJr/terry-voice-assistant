#!/usr/bin/env python3
"""
Test del TTS con el fix de reinicialización implementado
Debe funcionar correctamente en todas las llamadas
"""

from terry.core.voice.tts import TextToSpeech
import time


def test_fixed_tts():
    """Prueba 10 llamadas consecutivas al TTS con el fix."""
    print("\n" + "=" * 60)
    print("🧪 TEST DE TTS ARREGLADO - 10 LLAMADAS")
    print("=" * 60)

    print("\n🔧 Creando instancia de TTS con fix v6.0...")
    tts = TextToSpeech(rate=200, volume=0.95, optimize_for_voice=True)
    print("✅ TTS creado\n")

    frases = [
        "Prueba uno",
        "Prueba dos",
        "Prueba tres",
        "Prueba cuatro",
        "Prueba cinco",
        "Reproduciendo música",
        "Subiendo volumen",
        "Siguiente canción",
        "Pausando música",
        "Todo funcionando"
    ]

    fallos = 0
    exitos = 0

    for i, frase in enumerate(frases, 1):
        print(f"{i}. Hablando: '{frase}'")

        try:
            tts.speak(frase)
            print(f"   ✅ Completado sin errores")

            respuesta = input(f"   ¿Escuchaste? (s/n): ").lower()
            if respuesta == 's':
                exitos += 1
            else:
                fallos += 1
                print(f"   ⚠️  Fallo #{fallos}")

        except Exception as e:
            print(f"   ❌ Error en código: {e}")
            fallos += 1

        # Pequeña pausa
        time.sleep(0.3)

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESULTADOS")
    print("=" * 60)
    print(f"✅ Éxitos: {exitos}/10")
    print(f"❌ Fallos: {fallos}/10")

    if fallos == 0:
        print("\n🎉 ¡PERFECTO! El TTS funciona en TODAS las llamadas")
        print("El bug de macOS está completamente arreglado")
    elif exitos >= 8:
        print("\n✅ Muy bien! El TTS funciona en la mayoría de llamadas")
        print("Mejora significativa sobre el problema anterior")
    elif exitos >= 5:
        print("\n⚠️  Funciona parcialmente")
        print("Mejor que antes, pero aún hay fallos intermitentes")
    else:
        print("\n❌ Problema persiste")
        print("El fix no solucionó el problema completamente")

    return fallos == 0


if __name__ == "__main__":
    exito = test_fixed_tts()
    exit(0 if exito else 1)
