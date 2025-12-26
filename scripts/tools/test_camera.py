#!/usr/bin/env python3
"""
Script para probar la configuración de la cámara
"""
import sys
from pathlib import Path

# Add terry to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_camera():
    """Probar conexión y reconocimiento facial."""
    print("╔════════════════════════════════════════════════════════╗")
    print("║     TEST DE CÁMARA - TERRY v6.1                       ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    try:
        from terry.features.vision.camera import get_camera_vision_manager
        from terry.core.config.settings import get_settings
    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("   Verifica que estés en el directorio correcto")
        return

    # Verificar configuración
    settings = get_settings()
    camera_config = settings.get("camera_vision", {})

    print("📋 Configuración actual:")
    print(f"   Habilitada: {camera_config.get('enabled', False)}")
    print(f"   Auto-inicio: {camera_config.get('auto_start', False)}")

    use_webcam = camera_config.get("use_webcam", False)
    if use_webcam:
        print(f"   Tipo: Webcam local")
        print(f"   Índice: {camera_config.get('webcam_index', 0)}")
    else:
        camera_url = camera_config.get("camera_url", "")
        # Ocultar contraseña si existe
        password = camera_config.get("camera_password", "")
        if password and password in camera_url:
            camera_url = camera_url.replace(password, "****")
        print(f"   Tipo: Cámara IP")
        print(f"   URL: {camera_url}")

    print()
    print("🔧 Inicializando servicio de cámara...")

    try:
        manager = get_camera_vision_manager()
    except Exception as e:
        print(f"❌ Error inicializando: {e}")
        print()
        print("Posibles soluciones:")
        print("  1. Verifica que face-recognition esté instalado:")
        print("     cd ~/face-recognition")
        print("     pip install -r requirements.txt")
        print()
        print("  2. Verifica la URL de la cámara")
        print("  3. Ejecuta: python3 scripts/tools/configure_camera.py")
        return

    print("✅ Servicio inicializado")
    print()

    # Iniciar servicio
    print("🎥 Iniciando cámara...")
    try:
        if manager.start():
            print("✅ Cámara iniciada correctamente")
            print()

            # Esperar un momento para captura
            import time
            print("⏳ Capturando frames (5 segundos)...")
            time.sleep(5)

            # Verificar presencia
            print()
            print("👤 Verificando presencia...")
            people = manager.who_is_present()

            if people:
                print(f"✅ Detectadas {len(people)} persona(s):")
                for person in people:
                    print(f"   - {person}")
            else:
                print("ℹ️  No se detectó a nadie")
                print("   (Asegúrate de estar frente a la cámara)")

            # Estadísticas
            print()
            print("📊 Estadísticas:")
            stats = manager.get_stats()
            print(f"   Total detecciones: {stats.get('total_detections', 0)}")
            print(f"   Personas únicas: {stats.get('unique_people', 0)}")
            print(f"   Desconocidos: {stats.get('unknown_count', 0)}")

            # Detener
            print()
            print("🛑 Deteniendo cámara...")
            manager.stop()
            print("✅ Cámara detenida")

        else:
            print("❌ No se pudo iniciar la cámara")
            print()
            print("Posibles problemas:")
            print("  1. URL incorrecta")
            print("  2. Credenciales incorrectas")
            print("  3. Cámara no accesible en la red")
            print()
            print("Prueba:")
            print("  python3 scripts/tools/detect_cameras.py")

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("═" * 60)
    print("Para usar la cámara con voz:")
    print("  1. Inicia Terry: ./bin/run_voice.sh")
    print("  2. Habilita en settings.yaml: camera_vision.enabled = true")
    print("  3. Di: 'Terry, activa la cámara'")
    print("  4. Di: 'Terry, quién está aquí'")
    print("═" * 60)

if __name__ == "__main__":
    try:
        test_camera()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
