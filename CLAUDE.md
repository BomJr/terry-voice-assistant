# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Terry** is a local voice assistant for macOS with Alexa-style UX and superior local AI intelligence. Current version: **v6.1.9** (reorganized Dec 2025).

### Key Features

**v6.0 MVP** - Six critical UX improvements:
1. **LED Visual Feedback** - Terminal LED states (⚪ idle, 🔵 listening, 🟡 processing, 🟢 responding, 💬 conversation)
2. **Conversation Continuation** - 8s window without wake word for natural multi-turn conversations
3. **Voice Gestures** - Ultra-fast commands ("ok", "mmm", "qué?", "cancela", "siguiente")
4. **Voice-Activated Routines** - Multi-action workflows ("modo trabajo", "buenas noches")
5. **Immediate Feedback** - "Procesando..." response for slow commands
6. **Auto Multi-Language** - ES/EN auto-detection, responds in same language

**v6.1** - 20 substantial improvements including:
- **Camera Vision** - Face recognition with always-active service
- **Voice Notes** - Note-taking with semantic search
- **Undo System** - Revert last action
- **Web UI** - Professional FastAPI interface with chat memory

**Key Technologies**: Google STT (0.5s) + Whisper fallback, pyttsx3 TTS, Ollama Llama 3.1, 20+ actions

## Common Commands

### Run Terry

```bash
# Interactive launcher (recommended)
./bin/run_voice.sh
  # Option 1: Continuous mode (always listening, ultra-fast)
  # Option 2: Wake word mode (say "terry" or "hey mac")
  # Option 3: Alexa-fast responses (simplified TTS)
  # Option 4: Full responses (verbose TTS)

# Web UI (professional interface)
./bin/run_ui.sh
# Access at http://localhost:8080

# Direct execution
python3 -m terry.core.voice.pipeline              # Continuous
python3 -m terry.core.voice.pipeline --wake-word  # Wake word (-w)
python3 -m terry.core.voice.pipeline --full-responses  # Verbose TTS

# Debug mode (shows TTS/STT diagnostics)
./bin/run_voice_debug.sh
```

### Testing & Diagnostics

```bash
# Quick component test (TTS + STT + LLM)
./scripts/diagnostics/test_components.sh

# Microphone diagnostics
./scripts/diagnostics/test_mic.sh                                 # Real-time audio levels
source .venv/bin/activate && python3 scripts/tools/select_microphone.py  # Choose mic
source .venv/bin/activate && python3 scripts/diagnostics/test_microphone.py  # Full test

# Camera system
./bin/test_camera.sh                    # Complete camera test suite
python3 scripts/tools/test_camera.py    # Test camera connection
python3 scripts/tools/detect_cameras.py # Auto-detect IP cameras
python3 scripts/tools/configure_camera.py  # Interactive config

# Voice pipeline tests
python3 tests/integration/test_voice_loop.py     # Automated tests
python3 tests/integration/test_pipeline_debug.py # Debug output
python3 tests/e2e/test_voice_once.py            # Single voice command

# Utilities
python3 scripts/tools/show_cache_stats.py  # Cache hit rates
python3 scripts/tools/show_audit.py        # Command history
python3 scripts/tools/list_routines.py     # Available routines
```

### Installation

```bash
./scripts/install/install.sh              # All dependencies
./scripts/install/install_voice.sh        # Voice-specific (ffmpeg, PyAudio, etc.)
./scripts/install/install_v6_1.sh         # v6.1 features

# Prerequisites
brew install ffmpeg portaudio nowplaying-cli ollama

# Ollama setup
ollama serve
ollama pull llama3.1
```

## Core Architecture

### Project Structure (v6.1 Reorganization)

```
Home-Alexa/
├── main.py                  # Entry point
├── bin/                     # Executable scripts (run_voice.sh, run_ui.sh)
├── scripts/                 # Utilities
│   ├── install/            # Installation scripts
│   ├── diagnostics/        # Testing/debugging tools
│   ├── tools/              # Utilities (camera config, etc.)
│   └── demos/              # Demo scripts
├── tests/                   # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/               # End-to-end tests
│   └── ui/                # Web UI tests
├── docs/                    # Documentation
└── terry/                   # 🎯 MAIN MODULE
    ├── core/               # v6.0 production-ready nucleus
    │   ├── voice/         # CONSOLIDATED (STT + TTS + pipeline + conversation)
    │   ├── llm/           # Command processor, caching, Ollama client
    │   ├── actions/       # Action system (20+ actions)
    │   ├── ui/            # Terminal LED + Web UI (FastAPI)
    │   ├── memory/        # Persistent storage (SQLite)
    │   ├── utils/         # Session, logging, language detection
    │   └── config/        # Settings (YAML) + routines
    └── features/           # v6.1 experimental features
        ├── vision/        # Camera + face recognition ⭐ NEW
        ├── notes/         # Voice notes with search
        ├── automation/    # Scheduler, triggers, macros
        ├── productivity/  # Dictation, file search, IDE control
        ├── ux/            # Barge-in, emotion detection
        └── extensibility/ # Plugins, REST API
```

### Voice Pipeline Flow (v6.0)

```
Wake Word → STT → LLM (3-level cache) → Actions → TTS
    ↓        ↓            ↓                ↓        ↓
  Beep    Google/   Pattern/Cache/   Executor   Speak
          Whisper     LLM (0s/0.01s/1-2s)    with LED
                                                  ↓
                                        Conversation Window (8s)
```

**Two Modes**:
- **Wake word mode**: Privacy-first, only listens after "terry"/"hey mac"
- **Continuous mode**: Always listening, faster response

### Critical Files (v6.1 Updated Paths)

**Voice System**:
- `terry/core/voice/pipeline.py` - Main orchestrator with LED, conversation flow, immediate feedback
- `terry/core/voice/conversation.py` - State machine for 8s multi-turn windows
- `terry/core/voice/stt.py` - Google STT + Whisper fallback, wake word detection
- `terry/core/voice/tts.py` - pyttsx3 TTS with optimization, beep confirmation

**UI**:
- `terry/core/ui/terminal_led.py` - LED visual feedback using Rich library
- `terry/core/ui/web/app.py` - FastAPI web interface with WebSocket

**LLM & Processing**:
- `terry/core/llm/processor.py` - 3-level caching, gesture handlers, routine handlers, auto language detection
- `terry/core/llm/cache.py` - Pattern matching with gestures, routines, fuzzy matching
- `terry/core/llm/ollama_client.py` - Ollama integration

**State & Utilities**:
- `terry/core/utils/session_state.py` - Session context, gesture tracking (last_response, last_command)
- `terry/core/utils/language_detector.py` - ES/EN auto-detection
- `terry/core/utils/persistent_cache.py` - Disk-based LLM response cache with robust shutdown
- `terry/core/utils/audit_logger.py` - JSON Lines logging

**Actions**:
- `terry/core/actions/executor.py` - Execution with retries, confirmations
- `terry/core/actions/registry.py` - Central registration
- `terry/core/actions/routines/routine_manager.py` - Voice-activated routines

**Camera Vision (v6.1)**:
- `terry/features/vision/camera.py` - CameraVisionManager with always-active service
- `terry/core/actions/vision/camera_action.py` - Voice commands for camera

### 3-Level Command Processing

The most important architectural pattern for speed:

1. **Pattern matching (0.00s)** - `terry/core/llm/cache.py`
   - Regex patterns for instant responses
   - Includes gestures, routines, greetings
   - Fuzzy matching (85% threshold)
   - Handles 90% of commands

2. **Persistent cache (0.01s)** - `cache/ollama_cache.json`
   - Previously seen command variations
   - 24-hour TTL

3. **LLM (1-2s)** - Ollama
   - Novel/complex requests only
   - Auto-cached for next time

### Conversation Manager (v6.0)

`terry/core/voice/conversation.py` implements state machine:
- **IDLE** - No active conversation
- **ACTIVE** - Within 8s window
- **EXPIRED** - Window timed out

After TTS response → `start_conversation()` → 8s window where wake word not required. User speaks → `extend_window()` → another 8s. Timeout → `expire_conversation()` → back to wake word mode.

### Voice Gestures (v6.0)

Ultra-short context-aware commands in `terry/core/llm/cache.py`:
- `"ok"` - Play/pause (context-aware)
- `"siguiente"/"next"` - Next track
- `"mmm"/"repite"` - Repeat last response
- `"qué?"` - Repeat last command
- `"cancela"` - Cancel action

Session state tracks `last_response_text` and `last_command_text`.

### Voice-Activated Routines (v6.0)

Pattern: `r"(?:modo|rutina)\s+(trabajo|focus|descanso|noche)"` triggers routine lookup in `terry/core/config/routines.yaml`. Single command executes multi-action sequence.

Example routines:
- **modo trabajo**: Spotify + VS Code + volume 40% + Do Not Disturb
- **buenas noches**: Pause all + dim screen + volume off + close apps

### Camera Vision System (v6.1)

**External Integration**: Terry integrates with `~/face-recognition` project via path injection:
```python
sys.path.insert(0, "~/face-recognition")
from src.camera.stream import CameraStream
from src.face_recognition.detector import create_detector
```

**Always-Active Service**:
- Thread-based background processing
- Real-time face detection and recognition
- Presence tracking with configurable timeout
- Event callbacks: `on_person_detected`, `on_person_left`, `on_presence_changed`

**Voice Commands**:
- "Terry, quién está aquí" - List present people
- "Terry, está Bruno aquí" - Check specific person
- "Terry, activa la cámara" - Start service
- "Terry, estado de la cámara" - Get status

**Configuration**:
- Settings in `terry/core/config/settings.yaml` under `camera_vision:`
- Easy IP change via Web UI, interactive script, or direct YAML edit
- Supports IP cameras (RTSP/HTTP) and local webcams

## Configuration

### Performance Tuning (v6.0)

`terry/core/voice/pipeline.py`:
- **STT**: `use_whisper=False` (Google primary, 0.5s), `model_size="tiny"` (Whisper fallback, 1s)
- **Microphone**: `energy_threshold=150` (v6.0 - more sensitive), auto-limited to max 200, `pause_threshold=0.5s`
- **TTS**: `rate=200` (Alexa-like speed), `volume=0.95`
- **Delays**: ambient 0.2s, inter-command 0.1s

### Microphone Configuration (v6.0)

`.terry_microphone` file stores selected mic index. Created by `select_microphone.py`. Auto-loaded by pipeline on startup.

Common mic issues:
- **macOS permissions**: System Preferences > Security > Privacy > Microphone → Enable Terminal
- **Volume**: System Preferences > Sound > Input → Max volume
- **Selection**: Use `./scripts/diagnostics/test_mic.sh` to verify, `scripts/tools/select_microphone.py` to change

See `docs/SOLUCION_MICROFONO.md` for full troubleshooting.

### Wake Words

`terry/core/voice/pipeline.py` line 60:
```python
self.wake_words = ["terry", "hey mac", "oye mac", "ok mac"]
```

Wake word + command extraction: `terry/core/voice/stt.py:225-272`
```python
"terry pon música" → extracts "pon música"
```

### Camera Configuration

Multiple easy ways to configure (IP not static):

1. **Web UI** (easiest):
   ```bash
   ./bin/run_ui.sh
   # http://localhost:8080 → Settings → Camera Configuration
   ```

2. **Interactive script**:
   ```bash
   python3 scripts/tools/configure_camera.py
   ```

3. **Auto-detection**:
   ```bash
   python3 scripts/tools/detect_cameras.py
   ```

4. **Direct YAML edit**:
   ```yaml
   # terry/core/config/settings.yaml
   camera_vision:
     camera_url: "http://192.168.1.42:8080/video"  # Change IP here
     use_webcam: false  # or true for local webcam
     webcam_index: 0    # if using webcam
   ```

See `docs/CONFIGURACION_CAMARA_FACIL.md` for complete guide.

## Development Patterns

### Adding Actions

1. Create class in `terry/core/actions/{category}/`:
```python
from terry.core.actions.base import ActionBase, ActionResult

class NewAction(ActionBase):
    def __init__(self):
        super().__init__(
            name="new_action",
            description="Descripción en español",
            description_en="Description in English"
        )

    async def execute(self, params: Dict[str, Any]) -> ActionResult:
        return ActionResult(success=True, message="Done")
```

2. Register in `terry/core/actions/registry.py`:
```python
from terry.core.actions.{category}.new_action import NewAction
# In actions_to_register list:
NewAction,
```

3. Add patterns to `terry/core/llm/cache.py` for instant matching.

### Voice Optimization

- **Keep TTS short** - Auto-simplified (e.g., "Reproduciendo música" → "Reproduciendo")
- **No emojis in speech** - Automatically removed by TTS
- **Beep for simple confirmations** - `tts.play_beep()` instead of voice
- **Cache common patterns** - Add to `terry/core/llm/cache.py`

### Multi-Language Support (v6.0)

`terry/core/utils/language_detector.py` detects ES/EN via keyword matching. `terry/core/llm/processor.py` auto-detects if not specified, passes to LLM, returns response in same language.

### Adding Gestures (v6.0)

In `terry/core/llm/cache.py`, add pattern with dynamic placeholders:
```python
r"^(new_gesture)$": {
    "intent": "gesture_name",
    "action_type": "action",
    "response": "{dynamic_from_session}",
    "extract": "field_name"
}
```

Handler in `terry/core/llm/processor.py` processes using session state.

## Known Issues & Solutions

### TTS Not Speaking

**Symptom**: Commands processed but no voice output
**Debug**: Look for "⚠️ TTS OMITIDO" in output
**Solution**: Check `tts_enabled=True`, TTS object initialized, response not empty

### Microphone Not Detecting Voice

**Most Common**: macOS permissions not granted
**Fix**: System Preferences > Security > Privacy > Microphone → Enable Terminal, then restart Terminal (Cmd+Q)
**Diagnostic**: `./scripts/diagnostics/test_components.sh` - if TTS works but STT doesn't, it's mic issue
**Full Guide**: `docs/SOLUCION_MICROFONO.md`

### Terminal LED Saturation

**Fixed in v6.0**: `terry/core/ui/terminal_led.py` line 73, `pulse_enabled=False`
**If persists**: Check `_render()` not using `end=""` parameter

### Cache Errors on Shutdown

**Fixed in v6.0**: `terry/core/utils/persistent_cache.py` line 243-252, robust destructor checks builtins exist before saving

### Slow Response Time

**Target**: <1s for cached, 1-2s for LLM
**Check**:
1. Internet connection (Google STT needs it)
2. Ollama running: `curl http://localhost:11434/api/tags`
3. Add common commands to `terry/core/llm/cache.py`

### Camera Connection Issues

**IP Webcam (Android)**: Use `http://` not `https://`, ensure same WiFi network
**DroidCam/EpocCam**: Connect via USB for stability, not WiFi
**Face Recognition**: Install dependencies:
```bash
cd ~/face-recognition
pip install -r requirements.txt
```
**Full Guide**: `docs/IP_WEBCAM_ANDROID.md`

### Python 3.14 Compatibility

**Issue**: openwakeword incompatible
**Solution**: Simple text matching in `terry/core/voice/stt.py:225-272` (works well, no advanced detection needed)

## Architecture Decisions

### Why 3-Level Caching?
- Pattern matching (90% of commands, instant)
- Persistent cache (previously seen variations, 0.01s)
- LLM (novel requests only, 1-2s)
- Result: <0.5s average response time

### Why Google STT + Whisper?
- **Google**: Fast (0.5s), accurate, needs internet → PRIMARY
- **Whisper**: Slower (1-2s), offline, better accents → FALLBACK
- Auto fallback ensures always works

### Why pyttsx3 not Piper?
- Uses macOS system voices (Mónica, Paulina)
- Instant (no model loading)
- Native macOS, no external dependencies

### Why Beep Confirmation?
- Speed: 0.1s vs voice "Sí" (~1s)
- Less intrusive
- Alexa-style familiar UX
- `terry/core/voice/tts.py:231-247`

### Why Conversation Window?
- Natural multi-turn without repetitive wake word
- 8s balances fluidity vs accidental triggering
- Extends on each interaction
- Auto-expires on silence

### Why Modular Reorganization (v6.1)?
- Clear separation: core (stable) vs features (experimental)
- Easier to maintain and test
- Professional structure for open source
- Consolidated duplicates (stt/, tts/ → voice/)

### Why External Face Recognition Integration?
- Reuses existing well-tested codebase
- Separation of concerns (Terry = voice, face-recognition = vision)
- Path injection allows independent development
- Event-driven callbacks for loose coupling

## Documentation

**Essential Reading**:
- `CLAUDE.md` - This file (complete guide)
- `docs/CONFIGURACION_CAMARA_FACIL.md` - Camera setup guide
- `docs/SOLUCION_MICROFONO.md` - Microphone troubleshooting (most common issue)
- `docs/REORGANIZACION_COMPLETADA.md` - v6.1 reorganization details

**Feature Documentation**:
- `docs/CAMARA_VISION_IMPLEMENTADA.md` - Camera system complete docs
- `docs/IP_WEBCAM_ANDROID.md` - Using Android as camera
- `RESUMEN_SESION_COMPLETO.md` - Session summary with all changes

**Testing**:
- `PRUEBA_CAMARA.md` - Quick start for camera testing
- `docs/COMO_PROBAR.md` - General testing guide

## Virtual Environment

**CRITICAL**: Always activate `.venv` before running Python scripts:
```bash
source .venv/bin/activate
python3 script.py
```

Scripts with automatic venv activation:
- `./bin/test_components.sh`
- `./bin/test_mic.sh`
- `./bin/run_voice.sh`
- `./bin/run_ui.sh`
- `./bin/test_camera.sh`

Direct Python execution requires manual activation.

## Web UI Features (v6.1+)

Professional FastAPI interface at `http://localhost:8080`:

### ✅ **Implemented (v6.1.9 - Dec 2025)**

**Core Features:**
- **Chat Interface**: Conversational UI with memory
- **History**: Command history with timestamps, search, export
- **Notes**: Voice notes management
- **Macros**: Macro recording and playback
- **Settings**: Camera configuration, theme toggle, silent mode
- **Real-time**: WebSocket for live updates

**Recent Additions (v6.1.3-v6.1.6):**
- ✅ **Orange Theme**: Vibrant orange as primary color (#ff6b35)
- ✅ **Search & Export**: Real-time search in history, export to JSON/CSV
- ✅ **Keyboard Shortcuts**: Ctrl+K (search), Ctrl+E (export), Ctrl+Enter (send), ESC (close)
- ✅ **Copy to Clipboard**: Copy responses with one click
- ✅ **Relative Timestamps**: "hace 5 min" instead of full datetime
- ✅ **Auto-refresh Stats**: Stats update every 10 seconds automatically
- ✅ **Loading States**: Clear spinners and disabled states
- ✅ **Voice Recognition**: Browser-based speech recognition (Chrome/Edge/Safari)
- ✅ **Quick Commands**: Customizable command buttons with keyboard shortcuts (1-9)
  - Default: Música, Pausar, YouTube, Trabajo, Buenas Noches
  - Add/edit via modal
  - Stored in localStorage
- ✅ **History Replay**: Re-execute, edit, copy, or add to quick commands from history
  - 4 actions per history item (hover to show)
- ✅ **Command Templates**: Reusable command templates with dynamic variables
  - Create templates with {{variable}} syntax
  - Dynamic form generation for variable input
  - Categories: general, web, music, system, productivity
  - Full CRUD: Create, read, edit, delete
  - localStorage persistence
  - 2 default templates included
- ✅ **Push Notifications System**: Complete notification center with browser integration (v6.1.4)
  - Slide-in notifications panel from right
  - 5 notification types: success, error, warning, info, command
  - Browser notifications (Notification API)
  - Sound system with Web Audio API (unique frequencies per type)
  - Unread badge with counter
  - Mark as read functionality
  - Configurable settings (browser notifications, sounds, commands, errors)
  - localStorage persistence
  - Mobile responsive
- ✅ **Real-Time Logs System**: Terminal-style log viewer with filtering (v6.1.5) ⭐ **NEW**
  - 4 log levels: debug, info, warn, error
  - Color coding by level
  - Filter by level with toggle buttons
  - Auto-scroll with on/off toggle
  - Export logs to .txt file
  - Limit 1000 entries (FIFO)
  - Custom scrollbar styling
  - Terminal-like appearance with dark background
- ✅ **Multi-Theme System**: Complete theming with customization (v6.1.5) ⭐ **NEW**
  - 6 built-in themes: Orange, Blue, Green, Purple, Pink, Dark
  - Custom theme editor with 6 color pickers
  - Live preview on theme cards
  - Import/export themes as JSON
  - Instant application without page reload
  - localStorage persistence
  - Color manipulation algorithms (lighten/darken)
- ✅ **Intelligent Autocomplete**: Smart command suggestions with fuzzy matching (v6.1.6) ⭐ **NEW**
  - Fuzzy matching with 2-level scoring algorithm
  - Keyboard navigation (↑↓ arrows, Enter, Escape)
  - Multiple data sources (history + templates)
  - Visual highlighting of matching text
  - Relative timestamps ("hace 5 min")
  - Max 8 suggestions, sorted by relevance
  - Glassmorphism dropdown design
  - Click outside to close
  - Auto-scroll to selected item
- ✅ **Performance Profiler**: Real-time performance analysis with bottleneck detection (v6.1.7)
  - Automatic capture of command execution times
  - 4 summary cards: avg time, fastest, slowest, total commands
  - Interactive Chart.js bar chart (last 20 commands)
  - Color coding: green (<500ms), yellow (500-1500ms), red (>1500ms)
  - Top 10 slowest commands table
  - Intelligent bottleneck detection (3+ executions, 2x+ slower than average)
  - Context-aware optimization suggestions
  - Export to JSON with full statistics
  - FIFO queue (max 1000 entries)
  - Performance badges and visual warnings
- ✅ **System Monitor**: Complete real-time system monitoring dashboard (v6.1.8)
  - 4 health cards: CPU, RAM, Uptime, Commands/min
  - Animated progress bars with color coding (normal/warning/danger)
  - 6 services status: LLM, STT, TTS, Camera, WebSocket, Database
  - Pulse animation on online services
  - Unified activity timeline (commands + error logs)
  - System info grid (platform, Python version, IP, resolution)
  - Auto-refresh every 5 seconds (only when tab active)
  - Manual refresh button
  - Intelligent metric simulation based on real data
  - Glassmorphism design with responsive layout
- ✅ **Interactive API Documentation (Swagger UI)**: Professional OpenAPI documentation (v6.1.9) ⭐ **NEW**
  - Full OpenAPI 3.0 schema auto-generated
  - Swagger UI at `/docs` with try-it-out functionality
  - ReDoc alternative at `/redoc` with clean design
  - 13 endpoints fully documented across 6 tags
  - Request/Response models with Pydantic validation
  - Field-level descriptions and examples
  - Query parameter validation (ranges, types)
  - Markdown descriptions with code examples
  - Schema download at `/openapi.json`
  - Quick access button in Web UI header
  - Ready for client generation (Python, JS, Go, etc.)
  - Postman/Insomnia compatible

### 🚀 **Roadmap: Next Improvements**

**✅ COMPLETED (v6.1.1-v6.1.9):**
- Dashboard con métricas en tiempo real (v6.1.2)
- Gráficos interactivos con Chart.js (v6.1.2)
- Templates de comandos (v6.1.3)
- Sistema de notificaciones push (v6.1.4)
- Logs en tiempo real (v6.1.5)
- Temas múltiples (v6.1.5)
- Autocompletado inteligente (v6.1.6)
- Performance Profiler (v6.1.7)
- System Monitor (v6.1.8)
- Interactive API Documentation / Swagger UI (v6.1.9) ⭐ **NEW**

**Category A: Visualization & Analytics**

1. **📊 Dashboard con Métricas en Tiempo Real** ✅ COMPLETADO
   - Comandos ejecutados por hora/día/semana
   - Tiempo promedio de respuesta
   - Tasa de éxito/error
   - Comandos más usados (top 10)
   - Gráficos interactivos con Chart.js

2. **📈 Gráficos Interactivos (Chart.js)** ✅ COMPLETADO
   - Line charts: uso por tiempo
   - Bar charts: comandos más frecuentes
   - Pie charts: distribución por categoría
   - Real-time updates via WebSocket

3. **⚡ Autocompletado Inteligente** ✅ COMPLETADO
   - Autocomplete basado en historial
   - Sugerencias inteligentes
   - Historial navegable (flecha arriba/abajo)
   - Syntax highlighting para comandos
   - Snippets para comandos comunes

4. **📝 Templates de Comandos** ✅ COMPLETADO
   - Plantillas con variables: "Pon música de {{artista}}"
   - Formularios para rellenar variables
   - Guardado de templates personalizados
   - Categorización de templates
   - CRUD completo (crear, editar, eliminar)

5. **🔍 Logs en Tiempo Real** ✅ COMPLETADO (v6.1.5)
   - Tail -f style log viewer
   - Filtros por nivel (INFO, ERROR, DEBUG, WARN)
   - Color coding por tipo
   - Download logs functionality (.txt)
   - Auto-scroll con pause button
   - Terminal-style con Monaco font
   - FIFO queue (max 1000 entries)

6. **🎭 Visualizador de Estado del Sistema** ✅ COMPLETADO (v6.1.8)
   - CPU/RAM usage de Terry
   - Estado de servicios (LLM, STT, TTS, Camera, WebSocket, Database)
   - Timeline de actividad reciente
   - Uptime y health checks
   - Auto-refresh cada 5 segundos

**Category B: Productivity & Automation**

5. **📝 Editor de Comandos con Autocompletado**
   - Autocomplete basado en historial
   - Sugerencias inteligentes
   - Historial navegable (flecha arriba/abajo)
   - Syntax highlighting para comandos
   - Snippets para comandos comunes

6. **📋 Templates de Comandos**
   - Plantillas con variables: "Pon música de {artista}"
   - Formularios para rellenar variables
   - Guardado de templates personalizados
   - Categorización de templates
   - Import/export templates

7. **🎨 Constructor Visual de Rutinas**
   - Drag & drop para crear rutinas
   - Preview de acciones antes de ejecutar
   - Editor visual de parámetros
   - Testing individual de acciones
   - Save/load rutinas sin editar YAML

8. **🤖 Modo Conversación Mejorado**
   - Visualización del contexto actual
   - Editar contexto manualmente
   - Reiniciar conversación con botón
   - Historial de conversaciones
   - Export de conversaciones completas

**Category C: Advanced Features**

9. **🔔 Sistema de Notificaciones Push** ✅ COMPLETADO (v6.1.4)
   - Browser notifications cuando Terry completa acciones
   - Alertas de errores importantes
   - Integración con Notification API
   - Configuración de qué notificar (4 toggles)
   - Sound system con Web Audio API
   - Badge con contador de no leídas
   - Centro de notificaciones slide-in
   - 5 tipos con colores y sonidos únicos

10. **🌐 API REST Interactiva (Swagger UI)** ✅ COMPLETADO (v6.1.9)
    - Documentación automática con FastAPI (OpenAPI 3.0)
    - Probar endpoints desde navegador (Swagger UI + ReDoc)
    - Generar código de ejemplo (Python, JS, cURL)
    - 13 endpoints documentados across 6 tags
    - Request/Response models con Pydantic
    - Listo para client generation

11. **📤 Compartir & Exportar**
    - Exportar rutinas como JSON
    - Importar rutinas de archivos
    - Marketplace local de rutinas
    - QR codes para compartir comandos
    - Backup completo de configuración

12. **🐛 Modo Debug Visual**
    - Ver flow de procesamiento en tiempo real
    - Tiempo de cada paso (STT → LLM → Action → TTS)
    - Qué nivel de caché se usó
    - Errores detallados con stack traces
    - Timeline visual de ejecución

13. **📊 Performance Profiler** ✅ COMPLETADO (v6.1.7)
    - Identificar comandos lentos
    - Bottlenecks en el pipeline (detección automática)
    - Comparativas before/after (via export)
    - Sugerencias de optimización (contextuales)
    - Export de profiling data (JSON)
    - Chart.js bar chart con color coding
    - Top 10 slowest commands table
    - 4 summary cards con métricas clave

**Category D: UX & Customization**

14. **🎨 Temas Múltiples** ✅ COMPLETADO (v6.1.5)
    - 6 temas predefinidos: Orange, Blue, Green, Purple, Pink, Dark
    - Customización completa de colores con editor
    - Guardar temas personalizados con color pickers
    - Import/export temas como JSON
    - Aplicación instantánea sin reload
    - localStorage persistence
    - Import/export temas
    - Preview antes de aplicar

15. **📱 PWA (Progressive Web App)**
    - Instalar como app nativa en macOS
    - Funciona offline (con cache)
    - Icono en Dock/Escritorio
    - Push notifications nativas
    - Sincronización cuando vuelve online

16. **🌍 Multi-idioma Completo**
    - UI en Español/English/otros
    - Detección automática del navegador
    - Traducción de mensajes del sistema
    - Configuración por usuario
    - Fallback a idioma default

17. **♿ Accesibilidad Completa**
    - Screen reader support (ARIA labels)
    - Alto contraste mode
    - Navegación completa por teclado
    - Focus visible en todos los elementos
    - Shortcuts customizables

**Category E: Intelligence & AI**

18. **🧠 Sugerencias Inteligentes**
    - "Sueles hacer X después de Y"
    - Comandos contextuales según hora del día
    - Predicción de siguiente comando
    - Aprendizaje de patrones de uso
    - Recommendations proactivas

19. **📊 Análisis de Sentimiento & UX**
    - Detectar frustración del usuario
    - Comandos que causan más errores
    - Sugerir mejoras de UX
    - Happy path vs friction points
    - User satisfaction metrics

20. **🔗 Webhooks & Integraciones**
    - Recibir comandos desde servicios externos
    - Disparar webhooks cuando pasan cosas
    - IFTTT-style automations
    - Logs de webhooks ejecutados
    - Testing de webhooks desde UI

### 🛠️ **Implementation Priority**

**Phase 1 (Immediate Value):** ✅ **COMPLETADO**
1. ✅ Dashboard con métricas (v6.1.2)
2. ✅ Gráficos interactivos (v6.1.2)
3. ✅ Autocompletado en comandos (v6.1.2)
4. ✅ Templates de comandos (v6.1.3)

**Phase 2 (Enhanced UX):**
5. ✅ Notificaciones push (v6.1.4)
6. ⏭️ Constructor visual de rutinas
7. ⏭️ Logs en tiempo real
8. ⏭️ Modo debug visual

**Phase 3 (Advanced):**
9. PWA installation
10. Temas múltiples
11. Swagger API docs
12. Performance profiler

**Phase 4 (Intelligence):**
13. Sugerencias inteligentes
14. Análisis de sentimiento
15. Webhooks & integraciones

### 📝 **Development Notes for Web UI**

**Tech Stack:**
- **Frontend**: Vanilla JS (no frameworks needed), Font Awesome icons
- **Backend**: FastAPI with WebSocket support
- **Styling**: CSS custom properties (variables), glassmorphism design
- **Storage**: localStorage for client-side, SQLite for server-side
- **Real-time**: WebSocket manager for live updates

**Key Files:**
- `terry/core/ui/web/app.py` - FastAPI backend with all endpoints
- `terry/core/ui/web/static/js/app.js` - Main JavaScript app (TerryUI class)
- `terry/core/ui/web/static/css/style.css` - Complete styling with orange theme
- `terry/core/ui/web/templates/index.html` - Single-page application HTML

**Design Principles:**
- **100% Functional**: Every feature must have real utility
- **No Bloat**: Avoid decoration without function
- **Performance**: Fast loading, minimal dependencies
- **Accessibility**: Keyboard shortcuts, ARIA labels, responsive
- **Progressive Enhancement**: Works without JS for basics

**Adding New Features:**
1. Add HTML structure to `index.html`
2. Add CSS styling to `style.css` (use CSS variables)
3. Add JavaScript methods to TerryUI class in `app.js`
4. Add backend API endpoints to `app.py` if needed
5. Update WebSocket handlers for real-time if needed
6. Test with `./bin/run_ui.sh`

Camera features in Web UI:
- Visual camera configuration
- Test camera connection
- View live presence status
- See detection statistics
