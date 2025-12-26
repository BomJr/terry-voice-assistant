# 📁 PLAN DE REORGANIZACIÓN - TERRY v6.1

**Fecha**: 25 de diciembre de 2025
**Objetivo**: Organizar estructura del proyecto para mejor mantenibilidad

---

## 📊 ANÁLISIS ACTUAL

### Problemas identificados:
1. ❌ **30 archivos .py en raíz** (mayoría tests)
2. ❌ **20+ scripts .sh en raíz** (mezcla de instalación, tests, ejecución)
3. ❌ **Directorios duplicados**: `stt/` + `voice/speech_to_text.py`, `tts/` + `voice/text_to_speech.py`
4. ❌ **Directorios planificados pero vacíos**: algunos tienen solo 2 archivos placeholder
5. ❌ **No hay separación clara** entre código activo y experimental

### Estructura actual (resumida):
```
Home-Alexa/
├── main.py
├── config.py
├── test_*.py (22 archivos)
├── demo_*.py (1 archivo)
├── debug_*.py (1 archivo)
├── check_system.py
├── list_routines.py
├── select_microphone.py
├── show_audit.py
├── show_cache_stats.py
├── *.sh (20+ scripts)
├── actions/ (34 archivos en subdirectorios)
├── llm/ (5 archivos)
├── voice/ (6 archivos) ✅ ACTIVO
├── ui_web/ (1 archivo + static/templates) ✅ ACTIVO
├── memory/ (8 archivos)
├── utils/ (15 archivos) ✅ ACTIVO
├── config/ (1 archivo .py + YAML)
├── stt/ (2 archivos) ⚠️ DUPLICADO con voice/speech_to_text.py
├── tts/ (2 archivos) ⚠️ DUPLICADO con voice/text_to_speech.py
├── ui/ (2 archivos) ⚠️ DIFERENTE de ui_web/
├── vision/ (3 archivos) 🔜 PARA CÁMARA
├── visual/ (2 archivos) 🔜 PARA NOTIFICACIONES
├── notes/ (2 archivos)
├── macros/ (2 archivos)
├── plugins/ (2 archivos)
├── scheduler/ (2 archivos)
├── triggers/ (2 files)
├── dictation/ (2 archivos)
├── search/ (2 archivos)
├── ide/ (2 archivos)
├── interruption/ (2 archivos)
├── emotion/ (2 archivos)
├── undo/ (2 archivos)
├── api/ (2 archivos)
├── automation/ (sin archivos?)
├── core/ (4 archivos)
├── wakeword/ (2 archivos)
└── tests/ (1 archivo + subdirectorios)
```

---

## 🎯 ESTRUCTURA PROPUESTA

### Principios:
1. ✅ **Raíz limpia**: Solo archivos esenciales (main.py, README, requirements.txt)
2. ✅ **Scripts separados**: `scripts/` para utilidades, `bin/` para ejecutables
3. ✅ **Tests organizados**: `tests/` con estructura clara
4. ✅ **Módulos core vs features**: Separar esenciales de mejoras v6.1
5. ✅ **Sin duplicados**: Eliminar stt/, tts/, consolidar en voice/

### Nueva estructura:
```
Home-Alexa/
├── README.md
├── requirements.txt
├── .env.example
├── main.py                          # Entry point principal
│
├── bin/                             # Scripts ejecutables
│   ├── run_terry.sh                # Launcher principal
│   ├── run_ui.sh                   # Web UI
│   ├── run_voice.sh                # Voice mode
│   └── run_voice_debug.sh          # Debug mode
│
├── scripts/                         # Utilidades y herramientas
│   ├── install/
│   │   ├── install.sh
│   │   ├── install_voice.sh
│   │   ├── install_v6_1.sh
│   │   └── install_service.sh
│   ├── diagnostics/
│   │   ├── check_system.py
│   │   ├── diagnostic_completo.sh
│   │   ├── test_components.sh
│   │   └── test_mic.sh
│   ├── tools/
│   │   ├── select_microphone.py
│   │   ├── list_routines.py
│   │   ├── show_audit.py
│   │   └── show_cache_stats.py
│   └── demos/
│       └── demo_v6_1.py
│
├── tests/                           # Tests organizados
│   ├── unit/
│   │   ├── test_stt.py
│   │   ├── test_tts.py
│   │   ├── test_actions.py
│   │   ├── test_command_processor.py
│   │   └── ...
│   ├── integration/
│   │   ├── test_voice_pipeline.py
│   │   ├── test_voice_loop.py
│   │   └── test_websocket.py
│   ├── e2e/
│   │   ├── test_voice_once.py
│   │   └── test_wake_word_combined.py
│   └── ui/
│       ├── test_chat_memory.sh
│       └── test_chat_advanced.sh
│
├── terry/                           # Código principal (módulo Python)
│   ├── __init__.py
│   │
│   ├── core/                        # Núcleo esencial v6.0
│   │   ├── __init__.py
│   │   ├── voice/                   # Sistema de voz CONSOLIDADO
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py         # voice_pipeline.py → renombrado
│   │   │   ├── stt.py              # speech_to_text.py + stt/ → consolidado
│   │   │   ├── tts.py              # text_to_speech.py + tts/ → consolidado
│   │   │   ├── conversation.py     # conversation_manager.py
│   │   │   └── wake_word.py
│   │   │
│   │   ├── llm/                    # Sistema LLM
│   │   │   ├── __init__.py
│   │   │   ├── processor.py        # command_processor.py
│   │   │   ├── cache.py            # response_cache.py
│   │   │   ├── ollama_client.py
│   │   │   └── prompt_templates.py
│   │   │
│   │   ├── actions/                # Sistema de acciones
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # action_base.py
│   │   │   ├── executor.py         # action_executor.py
│   │   │   ├── registry.py         # action_registry.py
│   │   │   │
│   │   │   ├── media/              # Acciones por categoría
│   │   │   ├── system/
│   │   │   ├── browser/
│   │   │   ├── files/
│   │   │   ├── terminal/
│   │   │   ├── utilities/
│   │   │   ├── productivity/
│   │   │   └── routines/
│   │   │
│   │   ├── ui/                     # Interfaces de usuario
│   │   │   ├── __init__.py
│   │   │   ├── terminal_led.py
│   │   │   └── web/                # Web UI
│   │   │       ├── __init__.py
│   │   │       ├── app.py
│   │   │       ├── static/
│   │   │       └── templates/
│   │   │
│   │   ├── memory/                 # Sistema de memoria
│   │   │   ├── __init__.py
│   │   │   ├── manager.py          # memory_manager.py
│   │   │   ├── database.py
│   │   │   ├── context_builder.py
│   │   │   └── cleanup_scheduler.py
│   │   │
│   │   └── utils/                  # Utilidades core
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── session_state.py
│   │       ├── language_detector.py
│   │       ├── persistent_cache.py
│   │       ├── audit_logger.py
│   │       └── silent_mode.py
│   │
│   ├── features/                   # Mejoras v6.1 (20 features)
│   │   ├── __init__.py
│   │   │
│   │   ├── vision/                 # #5 Cámara + #7 OCR
│   │   │   ├── __init__.py
│   │   │   ├── camera.py
│   │   │   └── ocr.py
│   │   │
│   │   ├── visual/                 # #6 Notificaciones
│   │   │   ├── __init__.py
│   │   │   └── notifications.py
│   │   │
│   │   ├── notes/                  # #12 Notas por voz
│   │   │   ├── __init__.py
│   │   │   └── voice_notes.py
│   │   │
│   │   ├── automation/             # #8 Scheduler, #9 Triggers, #10 Macros
│   │   │   ├── __init__.py
│   │   │   ├── scheduler.py
│   │   │   ├── triggers.py
│   │   │   └── macros.py
│   │   │
│   │   ├── productivity/           # #11 Dictado, #13 Search, #14 IDE
│   │   │   ├── __init__.py
│   │   │   ├── dictation.py
│   │   │   ├── file_search.py
│   │   │   └── ide_control.py
│   │   │
│   │   ├── ux/                     # #15 Barge-in, #18 Frustration
│   │   │   ├── __init__.py
│   │   │   ├── interruption.py
│   │   │   └── emotion.py
│   │   │
│   │   ├── extensibility/          # #19 Plugins, #20 API
│   │   │   ├── __init__.py
│   │   │   ├── plugins.py
│   │   │   └── rest_api.py
│   │   │
│   │   └── undo/                   # #16 Undo
│   │       ├── __init__.py
│   │       └── action_history.py
│   │
│   └── config/                     # Configuración
│       ├── __init__.py
│       ├── settings.py
│       ├── settings.yaml
│       ├── routines.yaml
│       └── voices/
│
├── cache/                          # Cache y datos temporales
├── logs/                           # Logs
├── data/                           # Datos persistentes
└── docs/                           # Documentación
    ├── UI_WEB_ERRORES_COMPLETO.md
    ├── ARREGLOS_COMPLETOS.md
    ├── MEMORIA_CHAT_AGREGADA.md
    ├── RESUMEN_FINAL_UI_WEB.md
    └── ...
```

---

## 🔄 PLAN DE MIGRACIÓN

### Fase 1: Preparación (sin romper nada)
1. ✅ Crear directorio `terry/` con estructura nueva
2. ✅ Crear `bin/` y `scripts/`
3. ✅ Copiar (no mover) archivos a nueva estructura
4. ✅ Actualizar imports en archivos copiados

### Fase 2: Consolidación
1. ✅ Consolidar `stt/` + `voice/speech_to_text.py` → `terry/core/voice/stt.py`
2. ✅ Consolidar `tts/` + `voice/text_to_speech.py` → `terry/core/voice/tts.py`
3. ✅ Mover `voice/` → `terry/core/voice/`
4. ✅ Mover `llm/` → `terry/core/llm/`
5. ✅ Mover `actions/` → `terry/core/actions/`
6. ✅ Mover `ui_web/` → `terry/core/ui/web/`
7. ✅ Mover `memory/` → `terry/core/memory/`
8. ✅ Mover `utils/` (core) → `terry/core/utils/`

### Fase 3: Features v6.1
1. ✅ Mover `vision/` → `terry/features/vision/`
2. ✅ Mover `visual/` → `terry/features/visual/`
3. ✅ Mover `notes/` → `terry/features/notes/`
4. ✅ Mover `scheduler/`, `triggers/`, `macros/` → `terry/features/automation/`
5. ✅ Mover `dictation/`, `search/`, `ide/` → `terry/features/productivity/`
6. ✅ Mover `interruption/`, `emotion/` → `terry/features/ux/`
7. ✅ Mover `plugins/`, `api/` → `terry/features/extensibility/`
8. ✅ Mover `undo/` → `terry/features/undo/`

### Fase 4: Scripts y tests
1. ✅ Mover tests → `tests/` con subcategorías
2. ✅ Mover scripts de instalación → `scripts/install/`
3. ✅ Mover scripts de diagnóstico → `scripts/diagnostics/`
4. ✅ Mover utilidades → `scripts/tools/`
5. ✅ Mover ejecutables principales → `bin/`

### Fase 5: Actualización de imports
1. ✅ Actualizar todos los imports en código
2. ✅ Actualizar paths en configuración
3. ✅ Actualizar scripts de ejecución

### Fase 6: Limpieza
1. ✅ Eliminar directorios antiguos vacíos
2. ✅ Verificar que todo funciona
3. ✅ Actualizar documentación

### Fase 7: Verificación final
1. ✅ Ejecutar tests
2. ✅ Probar voice pipeline
3. ✅ Probar Web UI
4. ✅ Probar comandos principales

---

## 📝 MAPEO DE IMPORTS

### Cambios de imports (ejemplos):

**Antes**:
```python
from voice.voice_pipeline import VoicePipeline
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from llm.command_processor import CommandProcessor
from actions.action_executor import ActionExecutor
from ui_web.app import app
from utils.logger import get_logger
from memory.memory_manager import MemoryManager
```

**Después**:
```python
from terry.core.voice.pipeline import VoicePipeline
from terry.core.voice.stt import SpeechToText
from terry.core.voice.tts import TextToSpeech
from terry.core.llm.processor import CommandProcessor
from terry.core.actions.executor import ActionExecutor
from terry.core.ui.web.app import app
from terry.core.utils.logger import get_logger
from terry.core.memory.manager import MemoryManager
```

**Features v6.1**:
```python
from terry.features.vision.camera import CameraVisionManager
from terry.features.visual.notifications import NotificationManager
from terry.features.notes.voice_notes import VoiceNotesManager
from terry.features.undo.action_history import ActionHistory
```

---

## ✅ BENEFICIOS

1. ✅ **Raíz limpia**: Solo archivos esenciales
2. ✅ **Separación clara**: Core vs Features
3. ✅ **Sin duplicados**: Consolidación de stt/, tts/
4. ✅ **Tests organizados**: Por tipo (unit/integration/e2e/ui)
5. ✅ **Scripts separados**: Instalación, diagnóstico, herramientas
6. ✅ **Escalabilidad**: Fácil agregar nuevas features
7. ✅ **Mantenibilidad**: Estructura clara y lógica
8. ✅ **Imports claros**: `terry.core.*` vs `terry.features.*`

---

## ⚠️ CONSIDERACIONES

### Compatibilidad:
- Mantener archivos viejos temporalmente como "deprecated"
- Crear aliases de compatibilidad si es necesario
- Migración gradual para no romper nada

### Testing:
- Ejecutar todos los tests después de cada fase
- Verificar voice pipeline funciona
- Verificar Web UI funciona

### Documentación:
- Actualizar todos los READMEs
- Actualizar CLAUDE.md con nueva estructura
- Crear guía de migración para desarrolladores

---

## 🚀 EJECUCIÓN

¿Proceder con la reorganización?

**Fases sugeridas**:
1. Crear estructura nueva (Fase 1-2)
2. Consolidar y mover core (Fase 3)
3. Mover features (Fase 4)
4. Actualizar imports (Fase 5)
5. Limpiar y verificar (Fase 6-7)

**Tiempo estimado**: 2-3 horas
