# 🏠 Home-Alexa v3.1

> Asistente personal **100% local** para macOS con control por texto (voz próximamente)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![macOS](https://img.shields.io/badge/macOS-12.0+-green.svg)](https://www.apple.com/macos/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Características Principales

- ⚡ **Ultra-rápido**: 0.00-0.20s para comandos comunes (más rápido que Alexa)
- 🔒 **100% Privado**: Todo offline, sin cloud, sin telemetría
- 🎵 **Control de Música**: ~200 variaciones de comandos para YouTube/Spotify/Music
- 🔄 **Rutinas/Macros**: 10 rutinas predefinidas + personalizable
- 🔍 **Búsqueda de Archivos**: Spotlight integrado
- 📊 **Sistema Robusto**: Tests, benchmark, auditoría completa
- 🤖 **LLM Local**: Ollama con Llama 3.1
- 🇪🇸 **Español**: Lenguaje natural en español (también inglés)

---

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
# Ollama (LLM local)
brew install ollama
ollama serve &
ollama pull llama3.1:latest

# nowplaying-cli (control de música)
./install_nowplaying.sh
```

### 2. Configurar Entorno

```bash
# Crear entorno virtual e instalar
./install.sh
```

### 3. Verificar Sistema

```bash
./check_system.py
```

### 4. Tutorial Interactivo (Recomendado)

```bash
./tutorial.sh
```

### 5. Usar el Asistente

```bash
./run_test.sh
```

---

## 🎯 Ejemplos de Uso

### Control de Música (~200 Comandos)

```
Tú: pon música
Mac: Reproduciendo [⚡ CACHÉ 0.00s]

Tú: para el video
Mac: Pausando [⚡ CACHÉ 0.00s]

Tú: siguiente
Mac: Siguiente [⚡ CACHÉ 0.00s]

Tú: despausa
Mac: Reproduciendo [⚡ CACHÉ 0.00s]

Tú: apaga la música
Mac: Pausando [⚡ CACHÉ 0.00s]
```

**Funciona con**: YouTube, Spotify, Apple Music, VLC, etc.

### Rutinas Inteligentes

```
Tú: rutina de la mañana
Mac: Ejecutando rutina...
     ✓ Abriendo Safari
     ✓ Volumen a 30%
     ✓ Reproduciendo música

Tú: modo trabajo
Mac: Ejecutando rutina...
     ✓ Abriendo Safari
     ✓ Abriendo Gmail
     ✓ Volumen bajo

Tú: modo estudio
Mac: Ejecutando rutina...
     ✓ Volumen 25%
     ✓ Música lo-fi en YouTube
```

### Control del Sistema

```
Tú: abre Safari
Mac: Abriendo Safari [⚡ CACHÉ 0.00s]

Tú: sube el volumen
Mac: Subiendo volumen [⚡ CACHÉ 0.00s]

Tú: busca Python en Google
Mac: Buscando Python [⚡ CACHÉ 0.00s]
```

### Búsqueda de Archivos

```
Tú: busca el archivo presupuesto
Mac: Encontrados 3 archivos
     • ~/Documents/presupuesto_2024.xlsx
     • ~/Downloads/presupuesto.pdf
     • ~/Desktop/presupuesto_final.docx

Tú: muestra archivos recientes
Mac: Últimos 10 archivos modificados...

Tú: últimas descargas
Mac: Archivos en Downloads...
```

---

## 📊 Rendimiento

### Velocidad de Respuesta

| Tipo de Comando | Tiempo | Método |
|----------------|--------|--------|
| Comunes (música, apps) | **0.00-0.20s** | ⚡ Caché instantáneo |
| Repetidos (aprendidos) | **0.01-0.05s** | 🚀 Caché persistente |
| Nuevos/Complejos | **1-4s** | 🤖 LLM |

### Comparación con Alexa

| Métrica | Alexa | Home-Alexa |
|---------|-------|------------|
| Velocidad comandos simples | 1-3s | **0.04-0.3s** ⚡ |
| Velocidad comandos medios | 2-4s | **1-2s** 🚀 |
| Privacidad | ❌ Cloud | ✅ 100% Local |
| Costo | Hardware $$ | ✅ Gratis |
| Personalizable | ❌ Limitado | ✅ Código abierto |
| Funciona sin internet | ❌ No | ✅ Sí |

---

## 🎵 Control de Música - Sinónimos Completos

### ▶️ Reproducir (70+ formas)
```
pon | reproduce | play | continúa | reanuda | sigue | dale |
arranca | inicia | activa | prende | despausa
+ música/video/canción/tema/audio
```

### ⏸️ Pausar (60+ formas)
```
para | pausa | pause | detén | frena | apaga | corta |
silencia | stop
+ música/video/canción/tema/audio
```

### ⏭️ Siguiente (35+ formas)
```
siguiente | next | próxima | adelante | salta | skip |
cambia | avanza
+ canción/video/pista/track
```

### ⏮️ Anterior (30+ formas)
```
anterior | previous | atrás | vuelve | retrocede | back
+ canción/video/pista/track
```

**Total: ~200 variaciones** ✅

Ver lista completa: `cat COMANDOS_COMPLETOS.md`

---

## 🔄 Rutinas Predefinidas

| Rutina | Comando | Descripción |
|--------|---------|-------------|
| **morning** | "rutina de la mañana" | Abre Safari, volumen 30%, música |
| **work** | "modo trabajo" | Configura entorno de trabajo |
| **study** | "modo estudio" | Música lo-fi, volumen bajo |
| **break** | "descanso" | Pausa todo, silencia |
| **presentation** | "modo presentación" | Volumen alto, pausa notificaciones |
| **gaming** | "modo gaming" | Volumen 60%, cierra apps |
| **cooking** | "música cocina" | Música alegre para cocinar |
| **fitness** | "modo gym" | Música energética para ejercicio |
| **relax** | "modo zen" | Música relajante, volumen bajo |
| **shutdown** | "fin del día" | Cierra todo, apaga música |

**Personalizar**: Edita `config/routines.yaml`

Ver todas: `./list_routines.py`

---

## 🛠️ Scripts Útiles

| Script | Descripción |
|--------|-------------|
| `./run_test.sh` | **Iniciar el asistente** |
| `./tutorial.sh` | Tutorial interactivo |
| `./check_system.py` | Verificar requisitos |
| `./show_cache_stats.py` | Estadísticas de caché |
| `./show_audit.py` | Registro de comandos |
| `./list_routines.py` | Ver rutinas disponibles |
| `python3 tests/test_all_features.py` | Suite de tests |
| `python3 utils/benchmark.py` | Benchmark de velocidad |

---

## 📁 Estructura del Proyecto

```
Home-Alexa/
├── actions/              # Acciones del sistema
│   ├── media/           # Control de música/video
│   ├── files/           # Búsqueda de archivos
│   ├── routines/        # Sistema de rutinas
│   └── system/          # Control del sistema
├── llm/                 # Motor LLM
│   ├── ollama_client.py
│   ├── command_processor.py
│   └── response_cache.py
├── utils/               # Utilidades
│   ├── permissions_checker.py
│   ├── persistent_cache.py
│   ├── session_state.py
│   ├── audit_logger.py
│   ├── media_detector.py
│   └── benchmark.py
├── config/              # Configuración
│   ├── settings.yaml
│   └── routines.yaml
├── tests/               # Tests automáticos
├── cache/               # Caché persistente
├── logs/                # Logs y auditoría
└── docs/                # Documentación

```

---

## 🧪 Testing y Calidad

### Tests Automáticos

```bash
python3 tests/test_all_features.py
```

**Tests incluidos**:
- ✅ Verificación de permisos
- ✅ Caché rápido y persistente
- ✅ Estado de sesión
- ✅ Rutinas
- ✅ Imports de módulos

### Benchmark de Velocidad

```bash
python3 utils/benchmark.py
```

**Mide**:
- Velocidad de caché rápido
- Velocidad de caché persistente
- Velocidad de imports
- Estadísticas completas

---

## 📊 Monitoreo y Auditoría

### Estadísticas de Caché

```bash
./show_cache_stats.py
```

Muestra:
- Total de consultas
- Cache hits/misses
- Tasa de aciertos
- Comandos más frecuentes

### Auditoría de Comandos

```bash
./show_audit.py
```

Muestra:
- Todos los comandos ejecutados
- Éxito/fallo
- Tiempos de ejecución
- Estadísticas de uso

---

## ⚙️ Configuración

### Permisos Necesarios (macOS)

1. **Accesibilidad**: Para control de teclado/volumen
   - Preferencias → Privacidad → Accesibilidad → Terminal ✅

2. **Ollama**: Para procesamiento de lenguaje
   ```bash
   ollama serve
   ollama pull llama3.1
   ```

3. **nowplaying-cli** (Opcional, recomendado):
   ```bash
   ./install_nowplaying.sh
   ```

### Personalización

```yaml
# config/settings.yaml
model: "llama3.1:latest"
temperature: 0.3
max_tokens: 150

# config/routines.yaml
my_custom_routine:
  name: "Mi rutina personalizada"
  keywords:
    - "mi rutina"
  actions:
    - type: open_app
      params:
        app_name: "Spotify"
    - type: media_play
      params: {}
```

---

## 🐛 Troubleshooting

### "Control de música no funciona"

**Solución**:
1. Instala nowplaying-cli: `./install_nowplaying.sh`
2. Abre Music/Spotify/YouTube primero
3. Inicia reproducción manualmente una vez
4. Ahora los comandos funcionarán

### "Error de permisos"

**Solución**:
1. Preferencias del Sistema
2. → Privacidad y Seguridad
3. → Accesibilidad
4. → Activa Terminal ✅

### "Muy lento"

**Solución**:
```bash
# Usar modelo más rápido
ollama pull llama3:7b

# Editar config/settings.yaml
model: "llama3:latest"
```

### "Ollama no responde"

**Solución**:
```bash
# Reiniciar Ollama
pkill ollama
ollama serve &
```

---

## 📖 Documentación

- [README_V3.1.md](README_V3.1.md) - Este archivo
- [LISTO_PARA_USAR.md](LISTO_PARA_USAR.md) - Guía de inicio rápido
- [MEJORAS_V3.1.md](MEJORAS_V3.1.md) - Nuevas funcionalidades v3.1
- [CAPACIDADES.md](CAPACIDADES.md) - Lista completa de capacidades
- [COMANDOS_COMPLETOS.md](COMANDOS_COMPLETOS.md) - ~200 comandos de música
- [SOLUCION_NOWPLAYING.md](SOLUCION_NOWPLAYING.md) - Detalles técnicos

---

## 🔮 Próximos Pasos (Voz)

Home-Alexa v3.1 está **100% listo** para agregar funcionalidad de voz.

**Próxima versión (v4.0)**:
- 🎤 Wake Word ("hey mac")
- 🗣️ Speech-to-Text (Whisper)
- 🔊 Text-to-Speech (Piper)
- 🎙️ Control por voz completo

**Requisitos para voz**:
- Python 3.11/3.12 (para openwakeword y piper-tts)
- Micrófono decente
- Altavoces

---

## 🤝 Contribuir

Este es un proyecto personal, pero las sugerencias son bienvenidas.

**Ideas de mejoras**:
- Integración con Home Kit
- Más rutinas predefinidas
- Soporte para más aplicaciones
- Comandos multi-idioma
- Plugin system

---

## 📄 Licencia

MIT License - Ver [LICENSE](LICENSE)

---

## 🙏 Agradecimientos

- [Ollama](https://ollama.ai) - LLM local
- [nowplaying-cli](https://github.com/kirtan-shah/nowplaying-cli) - Control de música
- Comunidad de Python y macOS

---

## 📞 Soporte

¿Problemas? ¿Preguntas?

1. Revisa la documentación
2. Ejecuta `./check_system.py`
3. Revisa los logs: `tail -f logs/home_alexa.log`
4. Revisa auditoría: `./show_audit.py`

---

**¡Disfruta de tu asistente local!** 🎉

*Home-Alexa v3.1 - Tu asistente, tus reglas, tu privacidad*
