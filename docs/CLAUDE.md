# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Terry** is a local voice assistant for macOS with Alexa-style UX and superior local AI intelligence. Version 6.0 MVP delivers world-class UX with conversation continuation, visual feedback, voice gestures, routines, and multi-language support.

### Current Version: v6.0.1 UX

**v6.0 MVP**: Six critical UX improvements transform Terry from "functional" to "exceptional":
1. **LED Visual Feedback** - Terminal LED states (⚪ idle, 🔵 listening, 🟡 processing, 🟢 responding, 💬 conversation)
2. **Conversation Continuation** - 8s window without wake word for natural multi-turn conversations
3. **Voice Gestures** - Ultra-fast commands ("ok", "mmm", "qué?", "cancela", "siguiente")
4. **Voice-Activated Routines** - Multi-action workflows ("modo trabajo", "buenas noches")
5. **Immediate Feedback** - "Procesando..." response for slow commands
6. **Auto Multi-Language** - ES/EN auto-detection, responds in same language

**v6.0.1 UX ENHANCEMENTS** (latest): Six additional UX improvements for professional Alexa-like experience:
1. **Differentiated Beeps** - 5 contextual sounds (wake/listening/processing/success/error)
2. **Audible Confirmation** - Optional command confirmation before execution
3. **Auto-Retry** - Automatic retry (2x) with clear feedback if not heard
4. **Enhanced Messages** - Visual guidance with examples and tips
5. **Adjustable Timeout** - Configurable 3-30s wake word timeout
6. **Smart Error Handling** - Clear feedback for all error scenarios

**Key Technologies**: Google STT (0.5s) + Whisper fallback, pyttsx3 TTS, Ollama Llama 3.1, 200+ actions

## Common Commands

### Run Terry
```bash
# Interactive launcher (recommended)
./run_voice.sh
  # Option 1: Continuous mode (always listening)
  # Option 2: Wake word mode (say "terry" or "hey mac")

# Direct execution
python3 -m voice.voice_pipeline              # Continuous
python3 -m voice.voice_pipeline --wake-word  # Wake word (-w works too)
python3 -m voice.voice_pipeline --full-responses  # Frases completas (no simplificadas)
python3 -m voice.voice_pipeline --confirm-commands  # Confirmar comandos (v6.0.1 UX)
python3 -m voice.voice_pipeline --timeout 15        # Timeout 15s (v6.0.1 UX)

# v6.0.1 UX - Launcher mejorado con todas las opciones
./run_voice_ux.sh

# Debug mode (shows TTS/STT diagnostics)
./run_voice_debug.sh
```

### Testing & Diagnostics
```bash
# Quick component test (TTS + STT + LLM)
./test_components.sh

# Microphone diagnostics
./test_mic.sh                                 # Real-time audio levels
source .venv/bin/activate && python3 select_microphone.py  # Choose mic
source .venv/bin/activate && python3 test_microphone.py     # Full test

# Voice pipeline tests
source .venv/bin/activate && python3 test_voice_loop.py     # Automated tests
source .venv/bin/activate && python3 test_pipeline_debug.py # Debug output
source .venv/bin/activate && python3 test_tts_simple.py     # TTS only
source .venv/bin/activate && python3 test_tts_simplify.py   # Test simplificación ON/OFF
source .venv/bin/activate && python3 test_audio_diagnostics.py  # Diagnóstico completo audio

# Legacy tests
python3 test_stt.py          # STT (Google + Whisper)
python3 test_tts.py          # TTS voices
python3 test_voice_once.py   # Single voice command
python3 test_simple.py       # Action tests
python3 check_system.py      # Verify dependencies

# Utilities
python3 show_cache_stats.py  # Cache hit rates
python3 show_audit.py        # Command history
python3 list_routines.py     # Available routines
```

### Installation
```bash
./install.sh              # All dependencies
./install_voice.sh        # Voice-specific (ffmpeg, PyAudio, etc.)

# Prerequisites
brew install ffmpeg portaudio nowplaying-cli ollama

# Ollama setup
ollama serve
ollama pull llama3.1
```

## Core Architecture

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
- **Wake word mode**: Privacy-first, only listens after "terry"/"hey mac"/"oye mac"
  - **Opción A** (recomendado): Di todo de una vez: "terry pon música"
  - **Opción B**: En dos pasos: "terry" → beep → "pon música"
- **Continuous mode**: Always listening, faster response

### Critical Files (v6.0 MVP)

**Voice System**:
- `voice/voice_pipeline.py` - Main orchestrator with LED, conversation flow, immediate feedback
- `voice/conversation_manager.py` - State machine for 8s multi-turn windows
- `voice/speech_to_text.py` - Google STT + Whisper fallback, wake word detection (line 225), microphone selection
- `voice/text_to_speech.py` - pyttsx3 TTS with optimization, beep confirmation (line 231)

**UI**:
- `ui/terminal_led.py` - LED visual feedback using Rich library

**LLM & Processing**:
- `llm/command_processor.py` - 3-level caching, gesture handlers, routine handlers, auto language detection
- `llm/response_cache.py` - Pattern matching with gestures, routines, fuzzy matching
- `llm/ollama_client.py` - Ollama integration

**State & Utilities**:
- `utils/session_state.py` - Session context, gesture tracking (last_response, last_command)
- `utils/language_detector.py` - ES/EN auto-detection
- `utils/persistent_cache.py` - Disk-based LLM response cache with robust shutdown (v6.0 fix)
- `utils/audit_logger.py` - JSON Lines logging

**Actions**:
- `actions/action_executor.py` - Execution with retries, confirmations
- `actions/action_registry.py` - Central registration
- `actions/routines/routine_manager.py` - Voice-activated routines

### 3-Level Command Processing

1. **Pattern matching (0.00s)** - `llm/response_cache.py`
   - Regex patterns for instant responses
   - Includes gestures, routines, greetings
   - Fuzzy matching (85% threshold)
   - 90% of usage

2. **Persistent cache (0.01s)** - `cache/ollama_cache.json`
   - Previously seen command variations
   - 24-hour TTL

3. **LLM (1-2s)** - Ollama
   - Novel/complex requests only
   - Auto-cached for next time

### Conversation Manager (v6.0)

`voice/conversation_manager.py` implements state machine:
- **IDLE** - No active conversation
- **ACTIVE** - Within 8s window
- **EXPIRED** - Window timed out

After TTS response → `start_conversation()` → 8s window where wake word not required. User speaks → `extend_window()` → another 8s. Timeout → `expire_conversation()` → back to wake word mode.

### Voice Gestures (v6.0)

Ultra-short context-aware commands in `llm/response_cache.py`:
- `"ok"` - Play/pause (context-aware)
- `"siguiente"/"next"` - Next track
- `"mmm"/"repite"` - Repeat last response
- `"qué?"` - Repeat last command
- `"cancela"` - Cancel action

Session state tracks `last_response_text` and `last_command_text`.

### Voice-Activated Routines (v6.0)

Pattern: `r"(?:modo|rutina)\s+(trabajo|focus|descanso|noche)"` triggers routine lookup in `config/routines.yaml`. Single command executes multi-action sequence.

Example routines:
- **modo trabajo**: Spotify + VS Code + volume 40% + Do Not Disturb
- **buenas noches**: Pause all + dim screen + volume off + close apps

### LED Feedback (v6.0)

`ui/terminal_led.py` uses Rich library for colored terminal output:
- Renders current state with emoji + color
- States update in real-time during pipeline flow
- Pulse animation disabled (v6.0 fix) to prevent terminal saturation

## Configuration

### Performance Tuning (v6.0)

`voice/voice_pipeline.py`:
- **STT**: `use_whisper=False` (Google primary, 0.5s), `model_size="tiny"` (Whisper fallback, 1s)
- **Microphone**: `energy_threshold=150` (v6.0 - more sensitive, was 300), auto-limited to max 200, `pause_threshold=0.8s` (v6.0.1 - allows "terry pon música" without cutting)
- **TTS**: `rate=200` (Alexa-like speed), `volume=0.95`
- **Delays**: ambient 0.2s, inter-command 0.1s
- **Wake word timeout**: 10s (v6.0.1 - enough time to say full command)

### Microphone Configuration (v6.0)

`.terry_microphone` file stores selected mic index. Created by `select_microphone.py`. Auto-loaded by pipeline on startup.

Common mic issues:
- **macOS permissions**: System Preferences > Security > Privacy > Microphone → Enable Terminal
- **Volume**: System Preferences > Sound > Input → Max volume
- **Selection**: Use `./test_mic.sh` to verify, `select_microphone.py` to change

See `SOLUCION_MICROFONO.md` for full troubleshooting.

### Wake Words

`voice/voice_pipeline.py` line 73-77 (v6.0.1):
```python
self.wake_words = [
    "terry", "teri", "terri", "terrie",  # Variaciones de Terry
    "hey mac", "oye mac", "ok mac"       # Alternativas en español
]
```

Wake word + command extraction (v6.0.1): `voice/speech_to_text.py:241-288`
```python
"terry pon música" → extracts "pon música"  # Todo de una vez (recomendado)
"terry" → None                              # Solo wake word, espera comando
```
Returns: `(detected: bool, comando: Optional[str])`

**Uso**:
- **Modo rápido**: "terry pon música" (todo en una frase)
- **Modo paso a paso**: "terry" → beep → "pon música"

## Development Patterns

### Adding Actions

1. Create class in `actions/{category}/`:
```python
from actions.action_base import ActionBase, ActionResult

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

2. Register in `actions/action_registry.py`:
```python
registry.register("new_action", NewAction())
```

3. Add patterns to `llm/response_cache.py` for instant matching.

### Voice Optimization

- **TTS Response Styles** (v6.0 - configurable):
  - **Alexa-style (default)**: Auto-simplified ("Reproduciendo música" → "Reproduciendo")
  - **Full responses**: Complete phrases ("Reproduciendo música")
  - Toggle with `--full-responses` flag or in `./run_voice.sh` menu
- **No emojis in speech** - Automatically removed by TTS
- **Beep for simple confirmations** - `tts.play_beep()` instead of voice
- **Cache common patterns** - Add to `llm/response_cache.py`

### Multi-Language Support (v6.0)

`utils/language_detector.py` detects ES/EN via keyword matching. `llm/command_processor.py` auto-detects if not specified, passes to LLM, returns response in same language.

### Adding Gestures (v6.0)

In `llm/response_cache.py`, add pattern with dynamic placeholders:
```python
r"^(new_gesture)$": {
    "intent": "gesture_name",
    "action_type": "action",
    "response": "{dynamic_from_session}",
    "extract": "field_name"
}
```

Handler in `llm/command_processor.py` processes using session state.

## Known Issues & Solutions

### TTS Not Speaking

**Symptom**: Commands processed but no voice output
**Debug**: Look for "⚠️ TTS OMITIDO" in output (v6.0 fix adds visible print)
**Solution**: Check `tts_enabled=True`, TTS object initialized, response not empty

**Symptom v6.0 FIX**: TTS works first 2-3 times, then stops speaking
**Cause**: macOS pyttsx3 engine bug - engine gets stuck after multiple calls
**Solution**: FIXED in v6.0 - `voice/text_to_speech.py` now reinitializes engine before each speak() call
**Diagnostic**: Run `python3 test_audio_diagnostics.py` to verify TTS health

### Microphone Not Detecting Voice

**Most Common**: macOS permissions not granted
**Fix**: System Preferences > Security > Privacy > Microphone → Enable Terminal, then restart Terminal (Cmd+Q)
**Diagnostic**: `./test_components.sh` - if TTS works but STT doesn't, it's mic issue
**Full Guide**: `SOLUCION_MICROFONO.md`

### Terminal LED Saturation

**Fixed in v6.0**: `ui/terminal_led.py` line 73, `pulse_enabled=False`
**If persists**: Check `_render()` not using `end=""` parameter

### Cache Errors on Shutdown

**Fixed in v6.0**: `utils/persistent_cache.py` line 243-252, robust destructor checks builtins exist before saving

### Slow Response Time

**Target**: <1s for cached, 1-2s for LLM
**Check**:
1. Internet connection (Google STT needs it)
2. Ollama running: `curl http://localhost:11434/api/tags`
3. Add common commands to `llm/response_cache.py`

### Python 3.14 Compatibility

**Issue**: openwakeword incompatible
**Solution**: Simple text matching in `voice/speech_to_text.py:225-272` (works well, no advanced detection needed)

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
- Note: README mentions Piper but implementation uses pyttsx3

### Why Beep Confirmation?
- Speed: 0.1s vs voice "Sí" (~1s)
- Less intrusive
- Alexa-style familiar UX
- `voice/text_to_speech.py:231-247`

### Why Conversation Window?
- Natural multi-turn without repetitive wake word
- 8s balances fluidity vs accidental triggering
- Extends on each interaction
- Auto-expires on silence

## File Structure

**Active Implementation** (focus development here):
- `voice/` - Voice pipeline, STT, TTS, conversation manager
- `llm/` - Command processing, caching, Ollama client
- `actions/` - Action system (media, system, routines, etc.)
- `utils/` - Session, logging, language detection, fuzzy matching
- `ui/` - Terminal LED (v6.0)

**Planned but Unused** (from README, ignore):
- `core/audio_manager.py`, `memory/database.py`, `wakeword/openwakeword_detector.py`

## Documentation

**Essential Reading**:
- `TERRY_V6_MVP.md` - Complete v6.0 feature documentation with examples
- `INICIO_RAPIDO.md` - Quick start guide for users
- `SOLUCION_MICROFONO.md` - Microphone troubleshooting (most common issue)

**Legacy**:
- `CAMBIOS_V5_ESTILO_ALEXA.md` - v5.0 changelog
- `OPTIMIZACIONES_V5.md` - v5.0 performance improvements
- `MEJORAS_UX_PRIORITARIAS.md` - UX roadmap (v6.0 implements top 6 items)
- `VOZ_README.md`, `CAPACIDADES.md`, `COMANDOS_COMPLETOS.md` - Details

## Virtual Environment

**CRITICAL**: Always activate `.venv` before running Python scripts:
```bash
source .venv/bin/activate
python3 script.py
```

Scripts with automatic venv activation:
- `./test_components.sh`
- `./test_mic.sh`
- `./run_voice.sh`
- `./run_voice_debug.sh`

Direct Python execution requires manual activation.
