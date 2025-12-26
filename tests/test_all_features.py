#!/usr/bin/env python3
"""
Home-Alexa - Test Completo de Todas las Funcionalidades
Prueba todas las acciones y features implementadas
"""

import sys
import asyncio
import time
from pathlib import Path

# Agregar ruta del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from terry.core.utils.permissions_checker import PermissionsChecker
from terry.core.utils.persistent_cache import get_persistent_cache
from terry.core.utils.session_state import get_session
from terry.core.llm.cache import ResponseCache
from terry.core.actions.routines.routine_manager import get_routine_manager
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


class TestRunner:
    """Ejecuta tests de todas las funcionalidades."""

    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.start_time = time.time()

    def test(self, name: str, test_func):
        """
        Ejecuta un test.

        Args:
            name: Nombre del test
            test_func: Función que retorna (success, message)
        """
        self.total_tests += 1
        print(f"\n[TEST {self.total_tests}] {name}")
        print("-" * 60)

        try:
            success, message = test_func()

            if success:
                self.passed_tests += 1
                print(f"✅ PASS: {message}")
            else:
                self.failed_tests += 1
                print(f"❌ FAIL: {message}")

            return success

        except Exception as e:
            self.failed_tests += 1
            print(f"❌ ERROR: {e}")
            return False

    def print_summary(self):
        """Imprime resumen de los tests."""
        duration = time.time() - self.start_time

        print("\n" + "=" * 60)
        print("RESUMEN DE TESTS")
        print("=" * 60)
        print(f"Total: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Tasa de éxito: {(self.passed_tests/self.total_tests*100):.1f}%")
        print(f"Duración: {duration:.2f}s")
        print("=" * 60)

        if self.failed_tests == 0:
            print("\n🎉 TODOS LOS TESTS PASARON!")
        else:
            print(f"\n⚠️  {self.failed_tests} tests fallaron")


def test_permissions():
    """Test: Verificar permisos del sistema."""
    checker = PermissionsChecker()
    checks = checker.check_all(verbose=False)

    critical_ok = all([
        checks["python"][0],
        checks["accessibility"][0]
    ])

    message = "Permisos críticos OK" if critical_ok else "Faltan permisos críticos"
    return critical_ok, message


def test_response_cache():
    """Test: Verificar caché de respuestas rápidas."""
    # Probar comandos comunes
    test_commands = [
        "para la música",
        "sigue",
        "siguiente",
        "hola"
    ]

    cached_count = 0
    for cmd in test_commands:
        result = ResponseCache.get_quick_response(cmd)
        if result:
            cached_count += 1

    success = cached_count == len(test_commands)
    message = f"{cached_count}/{len(test_commands)} comandos en caché"
    return success, message


def test_persistent_cache():
    """Test: Verificar caché persistente."""
    cache = get_persistent_cache()

    # Guardar y recuperar un valor de prueba
    test_input = "comando de prueba test_12345"
    test_response = {
        "intent": "test",
        "actions": [],
        "response": "test response"
    }

    cache.set(test_input, test_response)
    retrieved = cache.get(test_input)

    success = retrieved is not None and retrieved["intent"] == "test"
    message = "Caché persistente funciona correctamente" if success else "Error en caché persistente"
    return success, message


def test_session_state():
    """Test: Verificar estado de sesión."""
    session = get_session()

    # Registrar comando de prueba
    session.record_command(
        user_input="test command",
        intent="test",
        success=True,
        response="test response"
    )

    # Verificar que se registró
    recent = session.get_recent_commands(limit=1)
    success = len(recent) > 0 and recent[0].intent == "test"

    message = "Estado de sesión funciona" if success else "Error en estado de sesión"
    return success, message


def test_routines_loaded():
    """Test: Verificar que las rutinas se cargaron."""
    manager = get_routine_manager()
    routines = manager.list_routines()

    expected_routines = ["morning", "work", "study", "relax"]
    loaded_names = [r["name"] for r in routines]

    all_loaded = all(routine in loaded_names for routine in expected_routines)

    message = f"{len(routines)} rutinas cargadas" if all_loaded else "Faltan rutinas"
    return all_loaded, message


def test_routine_keywords():
    """Test: Verificar búsqueda de rutinas por keywords."""
    manager = get_routine_manager()

    test_cases = [
        ("modo trabajo", "work"),
        ("rutina de la mañana", "morning"),
        ("estudiar", "study")
    ]

    success_count = 0
    for user_input, expected_routine in test_cases:
        found = manager.find_routine_by_keyword(user_input)
        if found == expected_routine:
            success_count += 1

    success = success_count == len(test_cases)
    message = f"{success_count}/{len(test_cases)} keywords encontradas"
    return success, message


def test_media_detector_imports():
    """Test: Verificar que MediaDetector se importa correctamente."""
    try:
        from terry.core.utils.media_detector import MediaDetector
        success = True
        message = "MediaDetector importado correctamente"
    except Exception as e:
        success = False
        message = f"Error importando MediaDetector: {e}"

    return success, message


def test_action_imports():
    """Test: Verificar que las acciones se importan correctamente."""
    try:
        from terry.core.actions.media.youtube_actions import YouTubeSearchAndPlayAction
        from terry.core.actions.files.file_search import FileSearchAction
        from terry.core.actions.routines.routine_manager import RoutineAction

        success = True
        message = "Todas las nuevas acciones importadas correctamente"
    except Exception as e:
        success = False
        message = f"Error importando acciones: {e}"

    return success, message


def test_cache_stats():
    """Test: Verificar estadísticas del caché."""
    cache = get_persistent_cache()
    stats = cache.get_stats()

    has_stats = all(key in stats for key in ["total_queries", "cache_hits", "hit_rate"])

    message = f"Stats OK: {stats['hit_rate']} hit rate" if has_stats else "Faltan stats"
    return has_stats, message


def test_session_stats():
    """Test: Verificar estadísticas de sesión."""
    session = get_session()
    stats = session.get_stats()

    has_stats = all(key in stats for key in ["total_commands", "success_rate"])

    message = f"Stats OK: {stats['success_rate']} success" if has_stats else "Faltan stats"
    return has_stats, message


def main():
    """Ejecuta todos los tests."""
    print("=" * 60)
    print("HOME-ALEXA - TEST SUITE COMPLETA")
    print("=" * 60)

    runner = TestRunner()

    # Tests de sistema
    print("\n📋 TESTS DE SISTEMA")
    runner.test("Verificar permisos del sistema", test_permissions)

    # Tests de caché
    print("\n⚡ TESTS DE CACHÉ")
    runner.test("Caché de respuestas rápidas", test_response_cache)
    runner.test("Caché persistente en disco", test_persistent_cache)
    runner.test("Estadísticas de caché", test_cache_stats)

    # Tests de sesión
    print("\n📊 TESTS DE SESIÓN")
    runner.test("Estado de sesión", test_session_state)
    runner.test("Estadísticas de sesión", test_session_stats)

    # Tests de rutinas
    print("\n🔄 TESTS DE RUTINAS")
    runner.test("Rutinas cargadas correctamente", test_routines_loaded)
    runner.test("Búsqueda de rutinas por keywords", test_routine_keywords)

    # Tests de imports
    print("\n📦 TESTS DE MÓDULOS")
    runner.test("MediaDetector importable", test_media_detector_imports)
    runner.test("Nuevas acciones importables", test_action_imports)

    # Resumen
    runner.print_summary()

    # Exit code
    sys.exit(0 if runner.failed_tests == 0 else 1)


if __name__ == "__main__":
    main()
