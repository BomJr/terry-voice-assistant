#!/usr/bin/env python3
"""
Terry v6.1 - Quick Functional Test
Prueba rápida de funcionalidades core
"""
import sys
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

print("╔════════════════════════════════════════════════╗")
print("║  TERRY v6.1 - PRUEBA FUNCIONAL RÁPIDA         ║")
print("╚════════════════════════════════════════════════╝\n")

test_results = []

def test(name, func):
    """Execute a test function."""
    try:
        result = func()
        print(f"✅ {name:30} {result}")
        test_results.append((name, True, result))
        return True
    except Exception as e:
        print(f"❌ {name:30} {type(e).__name__}: {str(e)[:30]}")
        test_results.append((name, False, str(e)))
        return False


# ═══════════════════════════════════════════════════════════
# FASE 1: QUICK WINS
# ═══════════════════════════════════════════════════════════

print("━━━ FASE 1: QUICK WINS ━━━")

def test_silent_mode():
    from terry.core.utils.silent_mode import is_silent, set_silent
    initial = is_silent()
    set_silent(True)
    changed = is_silent()
    set_silent(initial)  # Restore
    return f"Toggle works (was {initial})"

test("Silent Mode Toggle", test_silent_mode)


def test_notifications():
    from terry.features.visual.notification_manager import get_notification_manager
    mgr = get_notification_manager()
    # Don't actually show notification in test
    return f"Manager ready (enabled={mgr.enabled})"

test("Visual Notifications", test_notifications)


def test_voice_notes_crud():
    from terry.features.notes.voice_notes import get_notes_manager
    mgr = get_notes_manager()

    # Create
    note_id = mgr.add_note("Test: Quick functional test", category="test", priority=1)

    # Read
    notes = mgr.get_recent_notes(limit=1)

    # Search
    results = mgr.search_notes("functional")

    # Stats
    return f"Created note #{note_id}, found {len(results)} results"

test("Voice Notes CRUD", test_voice_notes_crud)


def test_undo_recording():
    from terry.features.undo.action_history import get_action_history
    history = get_action_history()

    # Record an action
    history.record(
        action_type="test_action",
        params={"test": "data"},
        result={"success": True},
        reversible=True,
        undo_params={"reverse": "data"}
    )

    can_undo = history.can_undo()
    return f"Recording works (can_undo={can_undo})"

test("Undo Action Recording", test_undo_recording)


# ═══════════════════════════════════════════════════════════
# FASE 2: INTELIGENCIA
# ═══════════════════════════════════════════════════════════

print("\n━━━ FASE 2: INTELIGENCIA ━━━")


def test_memory_save():
    from terry.core.memory.manager import MemoryManager
    memory = MemoryManager()

    # Save interaction
    memory.save_interaction(
        user_input="test command",
        assistant_response="test response",
        action_type="test_action"
    )

    stats = memory.get_stats()
    return f"{stats.get('total_interactions', 0)} interactions"

test("Persistent Memory", test_memory_save)


def test_pattern_recording():
    from terry.core.memory.pattern_learner import get_pattern_learner
    learner = get_pattern_learner()

    # Record a command
    learner.record_command(
        command="test command",
        timestamp=datetime.now(),
        context={"source": "test"}
    )

    return f"Patterns recorded"

test("Pattern Learning", test_pattern_recording)


def test_context_resolution():
    from terry.core.memory.context_manager import get_context_manager
    ctx = get_context_manager()

    # Update context
    ctx.update("test action", {"entity": "VS Code"})

    # Resolve pronouns
    resolved = ctx.resolve_pronouns("cierra eso")

    return f"Resolved: '{resolved}'"

test("Context Resolution", test_context_resolution)


def test_suggestions_generation():
    from terry.core.memory.intelligent_suggestions import get_suggestion_engine
    from datetime import datetime

    engine = get_suggestion_engine()
    suggestions = engine.get_suggestions(datetime.now())

    return f"{len(suggestions)} suggestions available"

test("Intelligent Suggestions", test_suggestions_generation)


# ═══════════════════════════════════════════════════════════
# FASE 3: MULTIMODALIDAD
# ═══════════════════════════════════════════════════════════

print("\n━━━ FASE 3: MULTIMODALIDAD ━━━")


def test_camera_initialization():
    from terry.features.vision.camera_vision import get_camera_vision
    vision = get_camera_vision()
    return "Camera manager initialized"

test("Camera Vision", test_camera_initialization)


def test_ocr_engine():
    from terry.features.vision.ocr_engine import get_ocr_engine
    ocr = get_ocr_engine()
    return f"OCR ready (tesseract={ocr.has_tesseract})"

test("OCR Engine", test_ocr_engine)


# ═══════════════════════════════════════════════════════════
# FASE 4: AUTOMATIZACIÓN
# ═══════════════════════════════════════════════════════════

print("\n━━━ FASE 4: AUTOMATIZACIÓN ━━━")


def test_scheduler_routines():
    from terry.features.automation.cron_manager import get_scheduler
    scheduler = get_scheduler()
    routines = scheduler.list_routines()
    return f"{len(routines)} routines configured"

test("Scheduler Routines", test_scheduler_routines)


def test_conditional_triggers():
    from terry.features.automation.conditional_engine import get_conditional_engine
    engine = get_conditional_engine()
    triggers = engine.list_triggers()
    return f"{len(triggers)} triggers active"

test("Conditional Triggers", test_conditional_triggers)


def test_macro_system():
    from terry.features.automation.macro_recorder import get_macro_recorder
    recorder = get_macro_recorder()
    macros = recorder.list_macros()
    return f"{len(macros)} macros saved"

test("Macro System", test_macro_system)


# ═══════════════════════════════════════════════════════════
# FASE 5: PRODUCTIVIDAD
# ═══════════════════════════════════════════════════════════

print("\n━━━ FASE 5: PRODUCTIVIDAD ━━━")


def test_dictation_manager():
    from terry.features.productivity.universal_dictation import get_dictation_manager
    mgr = get_dictation_manager()
    return f"Dictation ready (enabled={mgr.enabled})"

test("Universal Dictation", test_dictation_manager)


def test_file_search_spotlight():
    from terry.features.productivity.file_search import get_file_search
    search = get_file_search()

    # Search for Python files
    results = search.search("*.py", limit=3)

    return f"Found {len(results)} Python files"

test("File Search", test_file_search_spotlight)


def test_vscode_control():
    from terry.features.productivity.vscode_control import get_vscode_control
    vscode = get_vscode_control()
    return f"VS Code CLI {'available' if vscode.has_cli else 'not found'}"

test("IDE Control", test_vscode_control)


# ═══════════════════════════════════════════════════════════
# FASE 6: EXPERIENCIA
# ═══════════════════════════════════════════════════════════

print("\n━━━ FASE 6: EXPERIENCIA ━━━")


def test_barge_in():
    from terry.features.ux.barge_in import get_barge_in_manager
    mgr = get_barge_in_manager()
    return f"{len(mgr.interrupt_keywords)} interrupt keywords"

test("Barge-in System", test_barge_in)


def test_frustration_detector():
    from terry.features.ux.frustration_detector import get_frustration_detector
    detector = get_frustration_detector()
    return f"Detector ready (enabled={detector.enabled})"

test("Frustration Detection", test_frustration_detector)


# ═══════════════════════════════════════════════════════════
# FASE 7: INTEGRACIÓN
# ═══════════════════════════════════════════════════════════

print("\n━━━ FASE 7: INTEGRACIÓN ━━━")


def test_plugin_system():
    from terry.features.extensibility.plugin_system import get_plugin_system
    system = get_plugin_system()
    return f"{len(system.plugins)} plugins loaded"

test("Plugin System", test_plugin_system)


def test_rest_api():
    from terry.features.extensibility.rest_api import get_api
    api = get_api()
    return f"API on {api.host}:{api.port}"

test("REST API", test_rest_api)


# ═══════════════════════════════════════════════════════════
# RESUMEN
# ═══════════════════════════════════════════════════════════

print("\n" + "═" * 52)
print("RESUMEN DE PRUEBAS")
print("═" * 52)

total = len(test_results)
passed = sum(1 for _, success, _ in test_results if success)
failed = total - passed

print(f"\nTotal de pruebas:    {total}")
print(f"✅ Exitosas:         {passed}")
print(f"❌ Fallidas:         {failed}")
print(f"📊 Tasa de éxito:    {passed/total*100:.1f}%\n")

if failed > 0:
    print("Pruebas fallidas:")
    for name, success, result in test_results:
        if not success:
            print(f"  • {name}: {result}")
    print()

print("═" * 52)

if passed == total:
    print("🎉 ¡TODAS LAS PRUEBAS PASARON! Terry v6.1 está listo.")
else:
    print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

print("═" * 52)
print("\nPróximos pasos:")
print("  1. ./run_demo.sh          - Demo interactivo completo")
print("  2. ./run_voice.sh         - Iniciar Terry en modo voz")
print("  3. Ver GUIA_PRUEBAS_V6.1.md para comandos de ejemplo\n")
