"""
Home-Alexa - Verificador de Permisos
Verifica y solicita permisos necesarios en macOS
"""

import subprocess
import sys
from terry.core.utils.logger import get_logger

logger = get_logger(__name__)


def check_accessibility_permissions() -> bool:
    """
    Verifica si tenemos permisos de accesibilidad.

    Returns:
        True si tenemos permisos, False si no
    """
    try:
        # Intentar ejecutar un AppleScript simple
        result = subprocess.run(
            ['osascript', '-e', 'tell application "System Events" to get name of first process'],
            capture_output=True,
            timeout=2
        )
        return result.returncode == 0
    except Exception:
        return False


def request_accessibility_permissions():
    """Solicita permisos de accesibilidad al usuario."""
    print("\n" + "="*60)
    print("⚠️  PERMISOS REQUERIDOS")
    print("="*60)
    print("\nHome-Alexa necesita permisos de Accesibilidad para:")
    print("  • Controlar volumen")
    print("  • Control de multimedia (play/pause)")
    print("  • Atajos de teclado")
    print("\nPasos:")
    print("  1. Ve a: Preferencias del Sistema")
    print("  2. → Privacidad y Seguridad")
    print("  3. → Accesibilidad")
    print("  4. Activa la casilla para 'Terminal' (o tu app)")
    print("  5. Reinicia este programa")
    print("\n" + "="*60)

    # Abrir preferencias automáticamente
    try:
        subprocess.run([
            'open',
            'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
        ])
        print("\n✓ Abriendo Preferencias del Sistema...")
    except Exception:
        pass


def check_and_request_permissions() -> bool:
    """
    Verifica permisos y los solicita si es necesario.

    Returns:
        True si tenemos permisos, False si no
    """
    if check_accessibility_permissions():
        logger.info("Permisos de accesibilidad: OK")
        return True

    logger.warning("Permisos de accesibilidad no concedidos")
    request_accessibility_permissions()

    # Preguntar si quiere continuar sin permisos
    print("\n¿Continuar sin permisos? (algunas funciones no funcionarán)")
    print("  y = Sí, continuar")
    print("  n = No, salir")

    try:
        choice = input("\nOpción [y/n]: ").strip().lower()
        return choice == 'y'
    except (KeyboardInterrupt, EOFError):
        return False


def get_permission_status() -> dict:
    """
    Obtiene el estado de todos los permisos.

    Returns:
        Dict con el estado de cada permiso
    """
    return {
        "accessibility": check_accessibility_permissions(),
        "microphone": True,  # No podemos verificar esto fácilmente
        "automation": True   # No podemos verificar esto fácilmente
    }
