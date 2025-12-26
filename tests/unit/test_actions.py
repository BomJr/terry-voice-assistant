#!/usr/bin/env python3
"""
Test individual de cada acción
"""

import asyncio
from terry.core.actions.registry import ActionRegistry
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


async def test_action(action_type: str, params: dict):
    """Prueba una acción individual"""
    registry = ActionRegistry()
    action = registry.get(action_type)

    if not action:
        print(f"❌ Acción no encontrada: {action_type}")
        return False

    print(f"\n🔍 Probando: {action_type}")
    print(f"   Params: {params}")

    try:
        result = await action.execute(params)
        if result.success:
            print(f"   ✅ {result.message}")
            return True
        else:
            print(f"   ❌ {result.message}")
            if result.error:
                print(f"   Error: {result.error}")
            return False
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False


async def main():
    """Prueba todas las acciones"""
    print("=== Test de Todas las Acciones ===\n")

    registry = ActionRegistry()
    all_actions = registry.list_all()

    print(f"Total de acciones registradas: {len(all_actions)}")
    print(f"Acciones: {', '.join(all_actions)}\n")

    tests = {
        # System
        "open_app": {"app_name": "Calculator"},
        "volume_up": {"amount": 5},
        "volume_down": {"amount": 5},
        "volume_mute": {},

        # Browser
        "browser_open_url": {"url": "https://www.google.com", "browser": "Safari"},
        "browser_search": {"query": "test", "browser": "Safari"},

        # Media
        "media_play_pause": {},
        "media_next": {},
        "media_previous": {},

        # Utilities
        "timer_set": {"minutes": 1, "label": "Test"},
    }

    results = {}
    for action_type, params in tests.items():
        result = await test_action(action_type, params)
        results[action_type] = result
        await asyncio.sleep(0.5)

    # Resumen
    print("\n" + "="*50)
    print("RESUMEN")
    print("="*50)

    success_count = sum(1 for v in results.values() if v)
    total = len(results)

    for action, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {action}")

    print(f"\nTotal: {success_count}/{total} exitosas")

    if success_count < total:
        print("\n⚠️  Algunas acciones fallaron. Posibles causas:")
        print("   1. Permisos de Accesibilidad no concedidos")
        print("   2. Aplicaciones necesarias no instaladas")
        print("   3. Errores en la implementación")


if __name__ == "__main__":
    asyncio.run(main())
