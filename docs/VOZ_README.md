# 🎤 Home-Alexa - Modo Voz v4.5 (MEJORADO)

## ✨ NUEVO: Sistema de Voz Ultra-Mejorado

Home-Alexa ahora incluye **el mejor sistema de voz posible** con:

### 🎯 Mejoras Principales:

#### 1. 🧠 Whisper AI - Reconocimiento Ultra-Preciso
- **OpenAI Whisper** para reconocimiento de voz de última generación
- 95%+ precisión en español
- Funciona offline
- Mucho mejor que Google Speech Recognition

#### 2. 🔇 Cancelación de Ruido Avanzada
- Filtro high-pass para eliminar ruido de fondo
- VAD (Voice Activity Detection) mejorado
- Ajuste automático a ruido ambiente
- Reconoce voz incluso con ruido moderado

#### 3. 🗣️ Voces Ultra-Naturales
- Selección automática de las mejores voces (Mónica, Paulina)
- Velocidad optimizada (190 wpm = natural)
- Respuestas simplificadas para TTS
- Pronunciación clara y profesional

#### 4. 🎯 Wake Word Funcional
- Di "hey mac" o "oye mac" para activar
- No escucha constantemente (privacidad)
- Confirmación sonora cuando te escucha
- Modo continuo también disponible

#### 5. ⚡ Optimizaciones de Rendimiento
- Respuestas más cortas y directas
- Removal automático de emojis en TTS
- Pausas naturales optimizadas
- Procesamiento ultra-rápido

---

## 🚀 INSTALACIÓN (MEJORADA)

### Paso 1: Instalar Whisper

```bash
./install_voice.sh
```

Esto instala:
- ✅ **Whisper** - AI de reconocimiento de voz
- ✅ **PyAudio** - Captura de audio
- ✅ **SpeechRecognition** - Framework STT
- ✅ **pyttsx3** - Text-to-Speech
- ✅ **scipy** - Cancelación de ruido

---

## 🎯 USO DEL MODO VOZ MEJORADO

### Iniciar Home-Alexa con Voz:

```bash
./run_voice.sh
```

Se te preguntará qué modo quieres:

#### Modo 1: Continuo (Recomendado)
- Escucha siempre que esté listo
- Di comandos cuando veas "🎤 Habla ahora..."
- Más rápido y directo
- Ideal para uso intensivo

#### Modo 2: Wake Word
- Solo escucha cuando dices "hey mac" o "oye mac"
- Más privado (no escucha todo el tiempo)
- Confirmación con "Sí" cuando te escucha
- Ideal para uso ocasional

---

## 💬 EJEMPLOS DE USO

### Sesión con Modo Continuo:

```
🎤 HOME-ALEXA - MODO VOZ MEJORADO
============================================================
⚡ Escucha continuamente
============================================================

============================================================
🎤 Habla ahora...
🔄 Procesando con Whisper...

💬 Tú: pon música
🤖 Mac: Reproduciendo
🔊 "Reproduciendo" (voz natural)

============================================================
🎤 Habla ahora...
🔄 Procesando con Whisper...

💬 Tú: qué suena
🤖 Mac: 🎵 Sonando: Bohemian Rhapsody - Queen
🔊 "Sonando Bohemian Rhapsody de Queen"

============================================================
🎤 Habla ahora...
🔄 Procesando con Whisper...

💬 Tú: pausa
🤖 Mac: Pausando
🔊 "Pausando"
```

### Sesión con Wake Word:

```
🎤 HOME-ALEXA - MODO VOZ MEJORADO
============================================================
🔒 Solo escucha cuando dices la palabra de activación
============================================================

💤 Esperando 'hey mac'...
🎤 Habla ahora...

✅ Wake word detectada: 'hey mac'
🔊 "Sí" (confirmación)

============================================================
🎤 Habla ahora...
🔄 Procesando con Whisper...

💬 Tú: abre safari
🤖 Mac: Abriendo aplicación
🔊 "Abriendo"

💤 Esperando 'hey mac'...
```

---

## 🎯 COMANDOS SOPORTADOS

### ¡Todos los 200+ comandos funcionan con voz!

#### Música:
```
"pon música"
"pausa" / "para"
"siguiente" / "anterior"
"qué suena" / "ahora sonando"
"sube volumen" / "baja volumen"
```

#### Control del Sistema:
```
"abre Safari" / "abre Chrome"
"cierra ventana"
"minimizar"
"pantalla completa"
"sube brillo" / "baja brillo"
```

#### Rutinas:
```
"rutina de la mañana"
"modo trabajo"
"modo gaming"
```

#### Búsqueda de Archivos:
```
"busca presupuesto"
"encuentra facturas"
"archivos recientes"
```

---

## ⚙️ CONFIGURACIÓN AVANZADA

### Ajustar Sensibilidad del Micrófono

Edita `voice/speech_to_text.py`:

```python
stt = SpeechToText(
    energy_threshold=300,  # 300 = sensible, 1000 = menos sensible
    pause_threshold=0.8     # Segundos de silencio antes de procesar
)
```

### Cambiar Voz

Edita `voice/text_to_speech.py`:

```python
# Ver voces disponibles
python3 test_tts.py

# Cambiar voz preferida
PREFERRED_VOICES_ES = [
    "Paulina",  # Si prefieres voz mexicana primero
    "Mónica",   # Español España
    ...
]
```

### Ajustar Velocidad de Voz

```python
tts = TextToSpeech(
    rate=190,  # 150 = lento, 190 = natural, 220 = rápido
    volume=0.95
)
```

### Cambiar Wake Words

Edita `voice/voice_pipeline.py`:

```python
self.wake_words = ["hey mac", "oye mac", "ok mac", "alexa"]
# Añade las que quieras
```

---

## 🔧 TROUBLESHOOTING

### "No se detecta el micrófono"

**Solución**:
1. Verifica permisos:
   - Preferencias → Privacidad → Micrófono → Terminal ✅
2. Prueba: `python3 test_stt.py`
3. Si falla: `brew reinstall portaudio && pip install --force-reinstall pyaudio`

### "Whisper muy lento"

**Solución**:
Usa modelo más pequeño en `voice/voice_pipeline.py`:

```python
self.stt = SpeechToText(
    model_size="tiny",  # tiny < base < small < medium
    ...
)
```

**Tiempos**:
- `tiny`: ~0.5s (menos preciso)
- `base`: ~2s (recomendado, buen balance)
- `small`: ~5s (muy preciso)

### "La voz suena robótica"

**Solución**:
1. Verifica que esté usando Mónica o Paulina:
   ```bash
   python3 test_tts.py
   ```
2. Ajusta velocidad:
   ```python
   rate=170  # Más lento = más natural
   ```

### "No reconoce mi voz"

**Posibles causas**:
1. **Ruido ambiente** - Busca lugar más silencioso
2. **Micrófono malo** - Usa micrófono USB o headset
3. **Hablas muy rápido** - Habla más despacio y claro

**Solución**:
- Ajusta `energy_threshold` a 500-1000 (menos sensible)
- Habla más cerca del micrófono
- Usa headset con micrófono

---

## 📊 RENDIMIENTO

| Componente | Tiempo | Notas |
|------------|--------|-------|
| **Captura de audio** | Tiempo real | Mientras hablas |
| **Whisper (tiny)** | 0.5-1s | Rápido, menos preciso |
| **Whisper (base)** | 1-2s | **RECOMENDADO** ✅ |
| **Whisper (small)** | 3-5s | Muy preciso, más lento |
| **Cancelación de ruido** | 0.1s | Automático |
| **Procesamiento LLM** | 0.01-2s | Según comando |
| **Text-to-Speech** | Instantáneo | Voces del sistema |

**Total**: ~2-4 segundos desde que hablas hasta que escuchas respuesta

---

## ✅ VERIFICACIÓN RÁPIDA

```bash
# 1. Sistema base OK
./check_system.py

# 2. Dependencias de voz OK
source .venv/bin/activate
pip list | grep -E "whisper|pyaudio|SpeechRecognition|pyttsx3"

# 3. Test de micrófono y Whisper
python3 test_stt.py

# 4. Test de voces naturales
python3 test_tts.py

# 5. Iniciar con voz mejorada
./run_voice.sh
```

---

## 🎉 COMPARACIÓN v3.2 vs v4.5

### Antes (v3.2 - Sin Voz)
- ❌ Solo texto (escribir)
- ❌ Sin reconocimiento de voz
- ❌ Sin respuestas habladas

### Ahora (v4.5 - VOZ ULTRA-MEJORADA)
- ✅ **Whisper AI** (reconocimiento 95%+)
- ✅ **Cancelación de ruido avanzada**
- ✅ **Voces ultra-naturales** (Mónica/Paulina)
- ✅ **Wake word funcional** ("hey mac")
- ✅ **Respuestas optimizadas**
- ✅ **100% manos libres**
- ✅ **Funciona offline**
- ✅ **200+ comandos por voz**

---

## 🎯 CARACTERÍSTICAS DESTACADAS

### 🧠 Inteligencia
- Whisper de OpenAI (estado del arte)
- Reconocimiento contextual
- Tolera acentos y variaciones

### 🔊 Audio
- Cancelación de ruido high-pass filter
- VAD (Voice Activity Detection)
- Ajuste automático a ambiente
- Voces más naturales del sistema

### ⚡ Rendimiento
- Procesamiento en ~2-4s totales
- Respuestas optimizadas (cortas)
- Cache de comandos comunes
- Múltiples tamaños de modelo Whisper

### 🔒 Privacidad
- Funciona 100% offline (con Whisper)
- Wake word para no escuchar siempre
- No envía datos a la nube (modo offline)
- Todo local en tu Mac

---

## 💡 TIPS DE USO

### 1. Para Mejor Reconocimiento:
```
✅ Habla claro y natural
✅ Espera la señal "🎤 Habla ahora"
✅ Usa frases cortas
❌ No grites
❌ No hables muy rápido
```

### 2. Para Mejor Respuesta:
```
✅ Comandos cortos: "pon música", "siguiente", "para"
✅ Naturales: "qué suena", "abre safari"
❌ Evita comandos largos y complejos por voz
```

### 3. Para Mejor Experiencia:
```
✅ Usa headset con micrófono
✅ Ambiente silencioso
✅ Modo continuo para uso intensivo
✅ Modo wake word para uso ocasional
```

---

## 🔮 PRÓXIMAS MEJORAS POSIBLES

- ⏳ Whisper large (máxima precisión)
- ⏳ Piper-TTS (voces aún más naturales)
- ⏳ Streaming STT (respuesta en tiempo real)
- ⏳ Múltiples wake words personalizadas
- ⏳ Ajuste dinámico de ruido en tiempo real

---

## 🎤 ¡LISTO PARA USAR!

```bash
# Instalar (ya hecho)
./install_voice.sh

# Probar
./test_stt.py  # Test Whisper
./test_tts.py  # Test voces

# Usar
./run_voice.sh

# ¡Habla y disfruta! 🎉
```

---

**Home-Alexa v4.5** - Tu asistente de voz local ultra-mejorado 🚀

Reconocimiento: Whisper AI
Voces: Mónica / Paulina (Ultra-naturales)
Privacidad: 100% Local y Offline
Comandos: 200+ por voz
