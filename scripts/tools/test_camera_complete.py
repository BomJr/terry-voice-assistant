#!/usr/bin/env python3
"""
Script MAESTRO para probar TODO el sistema de cámara
Ejecuta todas las verificaciones y pruebas en orden
"""
import sys
import subprocess
from pathlib import Path
import time

# Add terry to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def print_header(title):
    """Imprimir encabezado bonito."""
    print("\n" + "═" * 60)
    print(f"  {title}")
    print("═" * 60 + "\n")

def print_step(number, title):
    """Imprimir paso."""
    print(f"\n{'─' * 60}")
    print(f"  PASO {number}: {title}")
    print("─" * 60 + "\n")

def ask_yes_no(question, default="n"):
    """Preguntar sí/no al usuario."""
    choices = "s/n" if default == "n" else "S/n"
    response = input(f"{question} ({choices}): ").strip().lower()
    if not response:
        response = default
    return response == 's'

def run_command(cmd, description):
    """Ejecutar comando y mostrar resultado."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            if result.stdout.strip():
                print(f"   {result.stdout.strip()[:200]}")
            return True
        else:
            print(f"❌ {description} - ERROR")
            if result.stderr.strip():
                print(f"   {result.stderr.strip()[:200]}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEPCIÓN: {e}")
        return False

def main():
    print_header("🎬 PRUEBA COMPLETA DEL SISTEMA DE CÁMARA - TERRY v6.1")

    print("Este script va a:")
    print("  1. ✅ Verificar dependencias")
    print("  2. 📋 Mostrar configuración actual")
    print("  3. 🔍 Detectar cámaras (opcional)")
    print("  4. 🧪 Probar conexión de cámara")
    print("  5. 🌐 Verificar Web UI")
    print("  6. 📊 Resumen final")
    print()

    if not ask_yes_no("¿Continuar con las pruebas?", default="s"):
        print("\n❌ Prueba cancelada")
        return

    # ═══════════════════════════════════════════════════════
    # PASO 1: VERIFICAR DEPENDENCIAS
    # ═══════════════════════════════════════════════════════
    print_step(1, "VERIFICAR DEPENDENCIAS")

    dependencies_ok = True

    print("🔍 Verificando Python y módulos...")
    try:
        import cv2
        print("  ✅ opencv-python instalado")
    except ImportError:
        print("  ❌ opencv-python NO instalado")
        dependencies_ok = False

    try:
        import yaml
        print("  ✅ pyyaml instalado")
    except ImportError:
        print("  ❌ pyyaml NO instalado")
        dependencies_ok = False

    # Verificar face-recognition
    face_recog_path = Path.home() / "face-recognition"
    if face_recog_path.exists():
        print(f"  ✅ face-recognition encontrado en {face_recog_path}")
    else:
        print(f"  ⚠️  face-recognition NO encontrado en {face_recog_path}")
        print("     (Necesario para reconocimiento facial)")

    if not dependencies_ok:
        print("\n⚠️  Faltan dependencias. Instalar con:")
        print("   pip install opencv-python pyyaml")
        if not ask_yes_no("¿Continuar de todos modos?"):
            return

    # ═══════════════════════════════════════════════════════
    # PASO 2: CONFIGURACIÓN ACTUAL
    # ═══════════════════════════════════════════════════════
    print_step(2, "CONFIGURACIÓN ACTUAL")

    try:
        from terry.core.config.settings import get_settings
        settings = get_settings()
        camera_config = settings.get("camera_vision", {})

        print("📋 Configuración de cámara:")
        print(f"  • Habilitada: {camera_config.get('enabled', False)}")
        print(f"  • Auto-inicio: {camera_config.get('auto_start', False)}")
        print(f"  • Usar webcam: {camera_config.get('use_webcam', False)}")

        if camera_config.get('use_webcam'):
            print(f"  • Índice webcam: {camera_config.get('webcam_index', 0)}")
        else:
            camera_url = camera_config.get('camera_url', '(no configurada)')
            password = camera_config.get('camera_password', '')
            if password and password in camera_url:
                camera_url = camera_url.replace(password, '****')
            print(f"  • URL: {camera_url}")
            print(f"  • Usuario: {camera_config.get('camera_username', '(ninguno)')}")

        print(f"  • Intervalo detección: {camera_config.get('detection_interval', 1.0)}s")
        print(f"  • Timeout presencia: {camera_config.get('presence_timeout', 10.0)}s")
        print(f"  • Umbral confianza: {camera_config.get('confidence_threshold', 0.6)}")

        has_config = bool(camera_config.get('camera_url') or camera_config.get('use_webcam'))

    except Exception as e:
        print(f"❌ Error leyendo configuración: {e}")
        has_config = False

    # ═══════════════════════════════════════════════════════
    # PASO 3: DETECTAR CÁMARAS (OPCIONAL)
    # ═══════════════════════════════════════════════════════
    print_step(3, "DETECTAR CÁMARAS EN RED")

    if not has_config:
        print("⚠️  No hay cámara configurada")
        if ask_yes_no("¿Quieres buscar cámaras en la red ahora?", default="s"):
            print("\n🔍 Ejecutando detección de cámaras...")
            print("   (Esto puede tardar unos minutos)\n")
            subprocess.run([
                sys.executable,
                "scripts/tools/detect_cameras.py"
            ])
        else:
            print("\n💡 Puedes configurar manualmente con:")
            print("   python3 scripts/tools/configure_camera.py")
            print("\n   O editar: terry/core/config/settings.yaml")

            if not ask_yes_no("\n¿Continuar con las pruebas sin cámara configurada?"):
                return
    else:
        print("✅ Cámara ya configurada")
        if ask_yes_no("¿Quieres buscar otras cámaras en la red?"):
            print("\n🔍 Ejecutando detección de cámaras...\n")
            subprocess.run([
                sys.executable,
                "scripts/tools/detect_cameras.py"
            ])

    # ═══════════════════════════════════════════════════════
    # PASO 4: PROBAR CÁMARA
    # ═══════════════════════════════════════════════════════
    print_step(4, "PROBAR CONEXIÓN DE CÁMARA")

    if ask_yes_no("¿Probar la cámara ahora?", default="s"):
        print("\n🧪 Ejecutando prueba de cámara...\n")
        subprocess.run([
            sys.executable,
            "scripts/tools/test_camera.py"
        ])
    else:
        print("⏭️  Prueba de cámara omitida")

    # ═══════════════════════════════════════════════════════
    # PASO 5: WEB UI
    # ═══════════════════════════════════════════════════════
    print_step(5, "INTERFAZ WEB")

    print("🌐 La Web UI permite configurar la cámara visualmente")
    print()
    print("Para probar la Web UI:")
    print("  1. Ejecuta en otra terminal: ./bin/run_ui.sh")
    print("  2. Abre: http://localhost:8080")
    print("  3. Ve a: Configuración > Configuración de Cámara")
    print("  4. Cambia la IP, guarda, prueba")
    print()

    if ask_yes_no("¿Iniciar Web UI ahora?", default="n"):
        print("\n🚀 Iniciando Web UI...")
        print("   Accede a: http://localhost:8080")
        print("   Presiona Ctrl+C para detener")
        print()
        try:
            subprocess.run([
                "./bin/run_ui.sh"
            ])
        except KeyboardInterrupt:
            print("\n\n⏹️  Web UI detenida")
    else:
        print("⏭️  Web UI omitida")
        print("   Puedes iniciarla después con: ./bin/run_ui.sh")

    # ═══════════════════════════════════════════════════════
    # PASO 6: COMANDOS DE VOZ
    # ═══════════════════════════════════════════════════════
    print_step(6, "COMANDOS DE VOZ")

    print("🎤 Comandos de voz disponibles:")
    print()
    print("  Iniciar/Detener:")
    print("    • 'Terry, activa la cámara'")
    print("    • 'Terry, desactiva la cámara'")
    print()
    print("  Consultar presencia:")
    print("    • 'Terry, quién está aquí'")
    print("    • 'Terry, está [nombre] aquí'")
    print()
    print("  Estado:")
    print("    • 'Terry, estado de la cámara'")
    print("    • 'Terry, estadísticas de la cámara'")
    print()

    if ask_yes_no("¿Iniciar Terry con voz para probar comandos?", default="n"):
        print("\n🎤 Iniciando Terry con voz...")
        print("   Di: 'Terry, activa la cámara'")
        print("   Presiona Ctrl+C para detener")
        print()
        try:
            subprocess.run([
                "./bin/run_voice.sh"
            ])
        except KeyboardInterrupt:
            print("\n\n⏹️  Terry detenido")
    else:
        print("⏭️  Prueba de voz omitida")
        print("   Puedes iniciarla después con: ./bin/run_voice.sh")

    # ═══════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ═══════════════════════════════════════════════════════
    print_header("📊 RESUMEN FINAL")

    print("✅ Prueba completa finalizada")
    print()
    print("📚 DOCUMENTACIÓN:")
    print("  • Guía completa: docs/CONFIGURACION_CAMARA_FACIL.md")
    print("  • Resumen técnico: docs/CONFIGURACION_CAMARA_COMPLETADA.md")
    print()
    print("🔧 HERRAMIENTAS:")
    print("  • Configurar: python3 scripts/tools/configure_camera.py")
    print("  • Detectar: python3 scripts/tools/detect_cameras.py")
    print("  • Probar: python3 scripts/tools/test_camera.py")
    print("  • Web UI: ./bin/run_ui.sh → http://localhost:8080")
    print()
    print("🎤 USAR CON VOZ:")
    print("  1. ./bin/run_voice.sh")
    print("  2. Di: 'Terry, activa la cámara'")
    print("  3. Di: 'Terry, quién está aquí'")
    print()
    print("═" * 60)
    print("  ✨ ¡Todo listo para usar el sistema de cámara! ✨")
    print("═" * 60)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Prueba cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
