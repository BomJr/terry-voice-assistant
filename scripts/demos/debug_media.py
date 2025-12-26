#!/usr/bin/env python3
"""
Debug del control de música - Ver exactamente qué pasa
"""

import asyncio
import subprocess
from terry.core.actions.registry import ActionRegistry
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    print("=== DEBUG: Control de Música ===\n")

    # Test 1: Verificar que la acción existe
    print("1. Verificando acción media_pause...")
    registry = ActionRegistry()
    action = registry.get("media_pause")

    if not action:
        print("   ❌ Acción no encontrada")
        return
    print("   ✅ Acción encontrada\n")

    # Test 2: Ejecutar la acción y ver el resultado
    print("2. Ejecutando media_pause...")
    result = await action.execute({})

    print(f"   Success: {result.success}")
    print(f"   Message: {result.message}")
    if result.error:
        print(f"   Error: {result.error}")
    if result.data:
        print(f"   Data: {result.data}")
    print()

    # Test 3: Probar el comando AppleScript directamente
    print("3. Probando AppleScript directamente...")
    print("   Comando: osascript -e 'tell application \"System Events\" to key code 16'")

    try:
        result = subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to key code 16'],
            capture_output=True,
            text=True,
            timeout=2
        )

        print(f"   Return code: {result.returncode}")
        print(f"   Stdout: {result.stdout}")
        print(f"   Stderr: {result.stderr}")

        if result.returncode == 0:
            print("   ✅ Comando ejecutado sin errores")
        else:
            print("   ❌ Comando falló")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()

    # Test 4: Probar con key code 49 (espacio)
    print("4. Probando con key code 49 (espacio)...")
    try:
        result = subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to key code 49'],
            capture_output=True,
            text=True,
            timeout=2
        )

        print(f"   Return code: {result.returncode}")
        if result.returncode == 0:
            print("   ✅ Key code 49 ejecutado")
        else:
            print("   ❌ Key code 49 falló")
            print(f"   Error: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
    print()

    # Test 5: Verificar permisos
    print("5. Verificando permisos de Accesibilidad...")
    try:
        result = subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to get name of first process'],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode == 0:
            print("   ✅ Permisos de Accesibilidad OK")
        else:
            print("   ❌ FALTA PERMISO DE ACCESIBILIDAD")
            print("   → Ve a: Preferencias → Privacidad → Accesibilidad → Terminal ✅")
    except Exception as e:
        print(f"   ❌ No se pudo verificar: {e}")


if __name__ == "__main__":
    print("\n🎵 ANTES DE EJECUTAR:")
    print("1. Abre YouTube en tu navegador")
    print("2. Reproduce un video")
    print("3. Presiona Enter para continuar...")
    input()

    asyncio.run(main())

    print("\n📝 ¿El video se pausó?")
    print("Si NO se pausó, el problema puede ser:")
    print("  1. Permisos de Accesibilidad")
    print("  2. Key code incorrecto")
    print("  3. El navegador necesita estar en primer plano")
