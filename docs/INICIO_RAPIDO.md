# 🚀 Terry v6.0 - Inicio Rápido

## ¿Qué es Terry?

Asistente de voz local tipo Alexa con IA superior, 100% privado, optimizado para macOS.

**Nuevas funciones v6.0:**
- ✅ LED visual de estado
- ✅ Conversación continua (8s sin wake word)
- ✅ Gestos de voz rápidos (ok, mmm, siguiente)
- ✅ Rutinas por voz (modo trabajo, buenas noches)
- ✅ Detección automática español/inglés
- ✅ Feedback inmediato

---

## 🏁 Inicio Rápido (3 pasos)

### 1️⃣ Verificar Sistema

```bash
./test_components.sh
```

Esto probará:
- ✅ TTS (deberías escuchar "Hola, soy Terry versión seis")
- ✅ STT (di algo cuando veas 🎤)
- ✅ LLM (procesamiento de comandos)

**Si TTS no se escucha**: Sube el volumen del sistema
**Si STT no detecta tu voz**: Lee `SOLUCION_MICROFONO.md`

---

### 2️⃣ Configurar Micrófono (solo si STT falló)

```bash
source .venv/bin/activate
python3 select_microphone.py
```

Sigue las instrucciones en pantalla. Micrófonos recomendados:
- **#2: External Microphone** (micrófono interno Mac)
- **#5: Echo Dot** (si tienes Amazon Echo conectado)

---

### 3️⃣ ¡Ejecutar Terry!

```bash
./run_voice.sh
```

Opciones:
1. **Modo Continuo** - Siempre escuchando (más rápido)
2. **Modo Wake Word** - Solo escucha después de "terry" (más privado)

**Recomendado**: Modo Wake Word (opción 2)

---

## 🗣️ Comandos de Ejemplo

### Saludo y Conversación
```
Tú:  "terry hola"
Terry: 🔔 "¡Hola! ¿En qué puedo ayudarte?"
💬 [Ventana de 8s activa - no necesitas decir "terry"]

Tú:  "pon música"  ← Sin wake word!
Terry: "Reproduciendo"
💬 [Ventana extendida 8s más]

Tú:  "más fuerte"  ← Sin wake word!
Terry: "Subiendo volumen"
```

### Gestos Rápidos
```
Tú:  "terry qué suena"
Terry: "Reproduciendo: Lofi Hip Hop Beats"

Tú:  "siguiente"      ← Gesto ultra-rápido
Tú:  "ok"             ← Play/pause context-aware
Tú:  "mmm"            ← Repite última respuesta
```

### Rutinas Multi-Acción
```
Tú:  "terry modo trabajo"
Terry: "Ejecutando rutina modo trabajo"
      [Abre Spotify → Lofi]
      [Abre VS Code]
      [Volumen 40%]
      [Activa No Molestar]
```

### Multi-Idioma
```
Tú:  "terry play music"  → Responde en inglés
Tú:  "terry para"        → Responde en español
```

---

## 🎯 Comandos Disponibles

### Media
- "pon música" / "play music"
- "para" / "pause"
- "siguiente" / "next"
- "anterior" / "previous"
- "qué suena" / "what's playing"

### Sistema
- "sube volumen" / "louder"
- "baja volumen" / "quieter"
- "abre Safari/Chrome/VS Code"
- "cierra Safari"

### Rutinas
- "modo trabajo" - Productividad
- "modo focus" - Concentración
- "buenas noches" - Rutina de noche
- "modo descanso" - Relax

### Conversación
- "hola" - Saludo
- "quién eres" - Identidad
- "qué puedes hacer" - Capacidades
- "gracias" - Agradecimiento

---

## 🐛 Solución de Problemas

### Problema: Micrófono no detecta voz
```bash
# 1. Verificar permisos macOS
Preferencias > Seguridad > Privacidad > Micrófono
→ Marcar Terminal ✅

# 2. Subir volumen de micrófono
Preferencias > Sonido > Entrada
→ Volumen al máximo

# 3. Ver guía completa
cat SOLUCION_MICROFONO.md
```

### Problema: No se escucha a Terry
```bash
# Subir volumen del sistema
# Verificar TTS:
./test_components.sh
```

### Problema: Terry se queda pensando/colgado
```bash
# Verificar Ollama está corriendo:
curl http://localhost:11434/api/tags

# Si no responde:
ollama serve
```

### Problema: LED satura el terminal
```bash
# Ya está arreglado en v6.0
# Si persiste, verifica:
grep "pulse_enabled=False" voice/voice_pipeline.py
```

---

## 📁 Scripts Útiles

```bash
./run_voice.sh              # Iniciar Terry
./test_components.sh        # Test rápido TTS/STT/LLM
./test_mic.sh              # Niveles de micrófono en tiempo real

source .venv/bin/activate && python3 select_microphone.py   # Cambiar micrófono
source .venv/bin/activate && python3 test_microphone.py     # Test completo
source .venv/bin/activate && python3 test_voice_loop.py     # Test automático
```

---

## 🔄 Actualización de Versiones

```bash
# Ver versión actual
./run_voice.sh  # Verás el banner con versión

# Changelog completo
cat TERRY_V6_MVP.md
```

---

## 📚 Documentación Completa

- **TERRY_V6_MVP.md** - Todas las nuevas funciones v6.0
- **SOLUCION_MICROFONO.md** - Guía de troubleshooting de micrófono
- **CLAUDE.md** - Arquitectura técnica
- **CAPACIDADES.md** - Lista completa de comandos

---

## ✨ Características v6.0

| Función | Descripción |
|---------|-------------|
| 🎨 LED Visual | Estado en tiempo real (escuchando/procesando/respondiendo) |
| 💬 Conversación | 8s sin wake word después de respuesta |
| 👌 Gestos | "ok", "mmm", "siguiente", "cancela" |
| 🔁 Rutinas | Multi-acción por voz |
| 🌍 Multi-idioma | ES/EN auto-detectado |
| ⚡ Feedback | "Procesando..." inmediato |

---

## 🎓 Tips

1. **Modo Wake Word + Conversación** = Mejor experiencia
   - Privacidad (solo escucha después de "terry")
   - Fluidez (8s sin wake word para follow-ups)

2. **Habla natural**
   - ✅ "terry pon música lofi"
   - ✅ "terry play some jazz"
   - ✅ "siguiente" (en conversación)

3. **Observa el LED**
   - ⚪ Esperando wake word
   - 🔵 Escuchando
   - 🟡 Procesando
   - 🟢 Respondiendo
   - 💬 En conversación

4. **Aprovecha rutinas**
   - Crea workflows personalizados en `config/routines.yaml`
   - Un comando → múltiples acciones

---

¡Disfruta Terry v6.0! 🎉
