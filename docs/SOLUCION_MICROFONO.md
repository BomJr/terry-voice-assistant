# 🎤 Solución: Micrófono No Detecta Voz

## Problema Identificado

Terry v6.0 funciona perfectamente EXCEPTO que el micrófono no detecta tu voz:

- ✅ TTS funciona (se escucha)
- ✅ LLM funciona (procesa comandos)
- ✅ Pipeline funciona
- ❌ STT no detecta voz del micrófono

## 🔧 Soluciones (en orden de probabilidad)

### 1️⃣ Verificar Permisos de Micrófono en macOS (MÁS COMÚN)

macOS requiere que des permiso explícito para usar el micrófono:

```bash
1. Abre: Preferencias del Sistema > Seguridad y Privacidad
2. Ve a la pestaña "Privacidad"
3. Selecciona "Micrófono" en la lista izquierda
4. Asegúrate que Terminal.app tiene ✅ marcado
5. Si Python está en la lista, también márcalo ✅
```

**IMPORTANTE**: Si acabas de dar permisos, REINICIA Terminal:
```bash
# Cierra Terminal completamente (Cmd+Q)
# Abre Terminal de nuevo
cd ~/Home-Alexa
./test_components.sh
```

---

### 2️⃣ Subir Volumen del Micrófono

```bash
1. Abre: Preferencias del Sistema > Sonido > Entrada
2. Selecciona "External Microphone" (o el que uses)
3. Sube el control de "Volumen de entrada" al MÁXIMO
4. Habla cerca del Mac y observa la barra de nivel
   - Si la barra se mueve → micrófono funciona
   - Si no se mueve → micrófono no está activo
```

---

### 3️⃣ Probar Otro Micrófono

Tienes 6 micrófonos disponibles. Probemos cada uno:

```bash
source .venv/bin/activate
python3 << EOF
import speech_recognition as sr

print("\n🎤 MICRÓFONOS DISPONIBLES:\n")
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"   {i}: {name}")

print("\n💡 RECOMENDACIONES:")
print("   • Prueba: #2 External Microphone (configurado)")
print("   • Prueba: #5 Echo Dot-E3N (si tienes Amazon Echo)")
print("   • Prueba: #0 o #1 (monitores con micrófono)")
EOF
```

Para cambiar de micrófono:
```bash
# Método 1: Manual
echo "5" > .terry_microphone  # Cambia 5 por el índice que quieras

# Método 2: Interactivo
source .venv/bin/activate
python3 select_microphone.py
```

Luego prueba de nuevo:
```bash
./test_components.sh
```

---

### 4️⃣ Test de Niveles en Tiempo Real

Para ver si el micrófono está detectando ALGO:

```bash
./test_mic.sh
```

Esto te mostrará niveles de audio en tiempo real:
```
   Tiempo  | Nivel  | Estado
   -----------------------------------
   001.2s  |   145  | ⚪ Silencio
   002.5s  |   820  | 🟢 VOZ FUERTE    ████████
   003.1s  |   320  | 🟡 Voz detectada ███
```

**Si ves niveles subir cuando hablas** → micrófono funciona, solo necesita ajuste de threshold
**Si ves solo "Sin audio"** → problema de permisos o micrófono incorrecto

---

### 5️⃣ Verificar que PyAudio está instalado

```bash
source .venv/bin/activate
python3 -c "import pyaudio; print('✅ PyAudio OK')"
```

Si falla:
```bash
# Reinstalar PyAudio
brew install portaudio
pip install --force-reinstall pyaudio
```

---

## 🧪 Tests Disponibles

Ejecuta estos scripts (ya tienen virtualenv activado automáticamente):

```bash
# Test rápido de componentes (TTS, STT, LLM)
./test_components.sh

# Test de niveles de micrófono en tiempo real
./test_mic.sh

# Cambiar de micrófono
source .venv/bin/activate
python3 select_microphone.py

# Ver lista de micrófonos
source .venv/bin/activate
python3 test_microphone.py
```

---

## ✅ Una Vez que el Micrófono Funcione

```bash
./run_voice.sh
```

Selecciona opción 2 (Wake word mode) y di:
```
"terry hola"          → Saludo
"terry pon música"    → Reproduce música
"para"                → Pausa (sin wake word, ventana de 8s)
"siguiente"           → Siguiente canción
```

---

## 🎯 Checklist de Diagnóstico

- [ ] ✅ Permisos de micrófono en macOS otorgados
- [ ] ✅ Terminal reiniciado después de dar permisos
- [ ] ✅ Volumen de entrada del micrófono al máximo
- [ ] ✅ Barra de nivel se mueve cuando hablas en Preferencias
- [ ] ✅ `./test_mic.sh` muestra niveles cuando hablas
- [ ] ✅ Probé con diferentes micrófonos (#0, #2, #5)
- [ ] ✅ PyAudio instalado correctamente

---

## 🆘 Si Nada Funciona

Última opción - usar modo texto para probar la lógica:

```bash
source .venv/bin/activate
python3 -c "
import asyncio
from voice.voice_pipeline import VoicePipeline

async def test():
    pipeline = VoicePipeline(wake_word_enabled=False, tts_enabled=True)

    # Simular comandos sin micrófono
    for cmd in ['hola', 'pon música', 'para']:
        print(f'\n> Comando: {cmd}')
        response = await pipeline.process_voice_command(cmd)
        print(f'< Respuesta: {response}')
        pipeline.tts.speak(response)

asyncio.run(test())
"
```

Esto verifica que todo el resto funciona (y debería escucharse las respuestas).

---

## 📞 Información de Debug

Si sigues teniendo problemas, ejecuta esto y comparte el resultado:

```bash
source .venv/bin/activate
python3 << EOF
import speech_recognition as sr
import platform

print("📋 DEBUG INFO:")
print(f"   macOS: {platform.mac_ver()[0]}")
print(f"   Python: {platform.python_version()}")

try:
    with sr.Microphone(device_index=2) as mic:
        print(f"   Micrófono #2: {mic.device_index}")
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(mic, duration=1)
        print(f"   Umbral: {r.energy_threshold:.0f}")
except Exception as e:
    print(f"   Error: {e}")
EOF
```
