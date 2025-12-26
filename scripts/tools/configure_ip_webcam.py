#!/usr/bin/env python3
"""
Configuración específica para IP Webcam (Android app)
"""
import sys
import requests
from pathlib import Path
import yaml

# Add terry to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def print_header(title):
    print("╔════════════════════════════════════════════════════════╗")
    print(f"║ {title:^54} ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

def test_ip_webcam_url(url):
    """Probar si la URL de IP Webcam funciona."""
    print(f"🔍 Probando: {url}")

    try:
        # Probar con timeout corto
        response = requests.get(url, timeout=5, stream=True)

        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            print(f"✅ Conexión exitosa!")
            print(f"   Content-Type: {content_type}")
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ Timeout - La app no responde")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ No se puede conectar - Verifica IP y puerto")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def configure_ip_webcam():
    """Configurar IP Webcam para Terry."""
    print_header("CONFIGURACIÓN IP WEBCAM - TERRY v6.1")

    print("📱 IP Webcam es una app de Android que convierte tu móvil en cámara IP")
    print()
    print("ℹ️  ANTES DE CONTINUAR:")
    print("   1. Abre IP Webcam en tu Android")
    print("   2. Presiona 'Iniciar servidor'")
    print("   3. La app mostrará una URL como: http://192.168.1.42:8080")
    print()

    # Obtener IP y puerto
    print("📋 Configuración:")
    print()

    default_ip = "192.168.1.42"
    ip = input(f"IP del móvil [{default_ip}]: ").strip() or default_ip

    default_port = "8080"
    port = input(f"Puerto [{default_port}]: ").strip() or default_port

    # Usuario y contraseña (opcional)
    print()
    print("🔐 Autenticación (opcional, si la configuraste en la app):")
    username = input("Usuario (Enter para omitir): ").strip()
    password = ""
    if username:
        password = input("Contraseña: ").strip()

    print()
    print("=" * 60)
    print("🧪 PROBANDO CONEXIONES...")
    print("=" * 60)
    print()

    # Construir URLs para probar
    base_url = f"http://{ip}:{port}"
    if username and password:
        base_url = f"http://{username}:{password}@{ip}:{port}"

    urls_to_test = [
        (f"{base_url}/video", "Video feed principal"),
        (f"{base_url}/videofeed", "Video feed alternativo"),
        (f"{base_url}/shot.jpg", "Captura de imagen"),
    ]

    working_url = None

    for url, description in urls_to_test:
        print(f"📹 {description}")
        if test_ip_webcam_url(url):
            if working_url is None:
                working_url = url
        print()

    if not working_url:
        print()
        print("❌ NO SE PUDO CONECTAR A IP WEBCAM")
        print()
        print("🔧 SOLUCIONES:")
        print()
        print("1. Verifica que IP Webcam esté ejecutándose:")
        print("   • Abre la app en Android")
        print("   • Presiona 'Iniciar servidor'")
        print("   • Verifica la URL que muestra")
        print()
        print("2. Verifica que estén en la misma red WiFi:")
        print("   • Tu Mac y tu Android deben estar en la misma red")
        print()
        print("3. Prueba desde el navegador:")
        print(f"   • Abre en Chrome: http://{ip}:{port}")
        print("   • Deberías ver la interfaz de IP Webcam")
        print()
        print("4. Verifica el firewall del móvil:")
        print("   • Algunas apps de seguridad bloquean conexiones")
        print()
        return

    print()
    print("=" * 60)
    print("✅ CONEXIÓN EXITOSA")
    print("=" * 60)
    print()
    print(f"URL que funciona: {working_url}")
    print()

    # Guardar configuración
    if input("¿Guardar esta configuración en Terry? (s/n): ").strip().lower() == 's':
        try:
            settings_path = Path(__file__).parent.parent.parent / "terry" / "core" / "config" / "settings.yaml"

            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)

            if "camera_vision" not in settings:
                settings["camera_vision"] = {}

            settings["camera_vision"]["camera_url"] = working_url
            settings["camera_vision"]["use_webcam"] = False
            settings["camera_vision"]["enabled"] = True

            if username:
                settings["camera_vision"]["camera_username"] = username
                settings["camera_vision"]["camera_password"] = password

            # Preguntar auto-start
            auto_start = input("¿Iniciar cámara automáticamente con Terry? (s/n) [n]: ").strip().lower()
            settings["camera_vision"]["auto_start"] = (auto_start == 's')

            with open(settings_path, 'w') as f:
                yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)

            print()
            print("✅ Configuración guardada en settings.yaml")
            print()
            print("=" * 60)
            print("🎉 TODO LISTO")
            print("=" * 60)
            print()
            print("📋 PRÓXIMOS PASOS:")
            print()
            print("1. Probar la cámara:")
            print("   python3 scripts/tools/test_camera.py")
            print()
            print("2. Usar con comandos de voz:")
            print("   ./bin/run_voice.sh")
            print("   Di: 'Terry, activa la cámara'")
            print("   Di: 'Terry, quién está aquí'")
            print()
            print("3. Configurar en Web UI:")
            print("   ./bin/run_ui.sh")
            print("   Abre: http://localhost:8080")
            print()
            print("⚠️  IMPORTANTE:")
            print("   • Mantén IP Webcam ejecutándose en tu Android")
            print("   • No bloquees la pantalla (o configura 'keep screen on')")
            print("   • Ambos dispositivos deben estar en la misma WiFi")
            print()

        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
    else:
        print("⏭️  Configuración no guardada")

def main():
    try:
        configure_ip_webcam()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
