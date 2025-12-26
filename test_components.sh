#!/bin/bash
# Terry v6.0 - Test de Componentes (con virtualenv)

source .venv/bin/activate
python3 -c "
from voice.text_to_speech import TextToSpeech
from voice.speech_to_text import SpeechToText
import asyncio

print('=' * 60)
print('🧪 TERRY v6.0 - TEST RÁPIDO DE COMPONENTES')
print('=' * 60)

# Test 1: TTS
print('\n1️⃣  TEST TTS')
print('-' * 60)
try:
    tts = TextToSpeech(rate=200, volume=0.95)
    print('✅ TTS inicializado')
    print('🔊 Reproduciendo: Hola, soy Terry versión seis')
    tts.speak('Hola, soy Terry versión seis')
    print('✅ TTS funcionó correctamente')
except Exception as e:
    print(f'❌ TTS falló: {e}')

# Test 2: STT
print('\n2️⃣  TEST STT')
print('-' * 60)
try:
    # Cargar micrófono configurado
    mic_index = None
    try:
        with open('.terry_microphone', 'r') as f:
            mic_index = int(f.read().strip())
            print(f'✅ Usando micrófono configurado: #{mic_index}')
    except:
        print('⚠️  Usando micrófono default')

    stt = SpeechToText(language='es', energy_threshold=150, microphone_index=mic_index)
    print('✅ STT inicializado')
    print(f'   Umbral de energía: {stt.recognizer.energy_threshold}')
    print('\n🎤 Di algo (5 segundos)...')

    text = stt.listen_once(timeout=5)
    if text:
        print(f'✅ STT reconoció: \"{text}\"')
    else:
        print('⚠️  STT no reconoció nada')
        print('💡 Soluciones:')
        print('   1. Sube el volumen del micrófono')
        print('   2. Habla más cerca')
        print('   3. Prueba: python3 test_mic_levels.py')

except Exception as e:
    print(f'❌ STT falló: {e}')
    import traceback
    traceback.print_exc()

# Test 3: Pipeline completo
print('\n3️⃣  TEST PIPELINE COMPLETO')
print('-' * 60)
async def test_pipeline():
    try:
        from llm.command_processor import CommandProcessor
        from llm.ollama_client import OllamaClient

        llm = OllamaClient()
        processor = CommandProcessor(llm)
        print('✅ LLM inicializado')

        print('🔄 Procesando: \"hola\"')
        result = await processor.process_command('hola')
        response = result.get('response', 'N/A')
        print(f'✅ Respuesta: \"{response}\"')

        # Hablar la respuesta
        tts = TextToSpeech(rate=200, volume=0.95)
        print('🔊 Reproduciendo respuesta...')
        tts.speak(response)
        print('✅ Pipeline completo funcionó')

    except Exception as e:
        print(f'❌ Pipeline falló: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test_pipeline())

print('\n' + '=' * 60)
print('🏁 Tests completados')
print('=' * 60)
print('\n💡 Si todo funciona, ejecuta: ./run_voice.sh')
"
