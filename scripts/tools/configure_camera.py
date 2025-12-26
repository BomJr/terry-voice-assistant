#!/usr/bin/env python3
"""
Script para configurar la cámara de Terry fácilmente
"""
import sys
from pathlib import Path
import yaml

# Add terry to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def load_settings():
    """Cargar settings.yaml"""
    settings_path = Path(__file__).parent.parent.parent / "terry" / "core" / "config" / "settings.yaml"
    with open(settings_path, 'r') as f:
        return yaml.safe_load(f)

def save_settings(settings):
    """Guardar settings.yaml"""
    settings_path = Path(__file__).parent.parent.parent / "terry" / "core" / "config" / "settings.yaml"
    with open(settings_path, 'w') as f:
        yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)

def configure_ip_camera():
    """Configurar cámara IP"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║     CONFIGURACIÓN DE CÁMARA - TERRY v6.1              ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    # Cargar configuración actual
    settings = load_settings()

    if "camera_vision" not in settings:
        settings["camera_vision"] = {}

    current_url = settings["camera_vision"].get("camera_url", "")
    current_username = settings["camera_vision"].get("camera_username", "")

    print(f"Configuración actual:")
    print(f"  URL: {current_url if current_url else '(no configurada)'}")
    print(f"  Usuario: {current_username if current_username else '(no configurado)'}")
    print()

    # Tipo de cámara
    print("¿Qué tipo de cámara quieres usar?")
    print("  1) Cámara IP (RTSP)")
    print("  2) Webcam local (USB o integrada)")
    print()

    choice = input("Selecciona (1/2): ").strip()

    if choice == "2":
        # Webcam
        settings["camera_vision"]["use_webcam"] = True
        webcam_index = input("Índice de webcam (0 = primera, 1 = segunda, etc.) [0]: ").strip() or "0"
        settings["camera_vision"]["webcam_index"] = int(webcam_index)
        print()
        print(f"✅ Webcam #{webcam_index} configurada")

    else:
        # Cámara IP
        settings["camera_vision"]["use_webcam"] = False

        print()
        print("Configuración de cámara IP:")
        print()

        # IP de la cámara
        print("IP de la cámara (ej: 192.168.1.100):")
        ip = input("IP: ").strip()

        if not ip:
            print("❌ IP requerida")
            return

        # Puerto (opcional)
        port = input("Puerto (ej: 554) [554]: ").strip() or "554"

        # Stream path (opcional)
        stream_path = input("Path del stream (ej: /stream, /cam/realmonitor?channel=1&subtype=0) [/stream]: ").strip() or "/stream"

        # Protocolo
        protocol = input("Protocolo (rtsp/http) [rtsp]: ").strip() or "rtsp"

        # Credenciales
        print()
        print("Credenciales (déjalas vacías si no se requieren):")
        username = input("Usuario: ").strip()
        password = input("Contraseña: ").strip()

        # Construir URL
        if username and password:
            camera_url = f"{protocol}://{username}:{password}@{ip}:{port}{stream_path}"
        else:
            camera_url = f"{protocol}://{ip}:{port}{stream_path}"

        settings["camera_vision"]["camera_url"] = camera_url
        settings["camera_vision"]["camera_username"] = username
        settings["camera_vision"]["camera_password"] = password

        print()
        print(f"✅ Cámara IP configurada:")
        print(f"   URL: {camera_url.replace(password, '****') if password else camera_url}")

    # Preguntar si auto-iniciar
    print()
    auto_start = input("¿Iniciar cámara automáticamente con Terry? (s/n) [n]: ").strip().lower()
    settings["camera_vision"]["auto_start"] = (auto_start == 's')

    # Guardar configuración
    save_settings(settings)

    print()
    print("╔════════════════════════════════════════════════════════╗")
    print("║           ✅ CONFIGURACIÓN GUARDADA                    ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()
    print("Para probar la cámara:")
    print("  1. Inicia Terry (./bin/run_voice.sh)")
    print("  2. Di: 'Terry, activa la cámara'")
    print("  3. Di: 'Terry, quién está aquí'")
    print()
    print("O ejecuta directamente:")
    print("  python3 scripts/tools/test_camera.py")
    print()

if __name__ == "__main__":
    try:
        configure_ip_camera()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
