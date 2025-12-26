#!/usr/bin/env python3
"""
Script para detectar cámaras IP en la red local
Útil cuando la IP de la cámara cambia
"""
import socket
import subprocess
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional
import concurrent.futures

# Add terry to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def get_local_ip_range():
    """Obtener el rango de IPs de la red local."""
    try:
        # Obtener IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Extraer base de red (ej: 192.168.1)
        ip_parts = local_ip.split('.')
        network_base = '.'.join(ip_parts[:3])

        return network_base, local_ip
    except Exception as e:
        print(f"❌ Error obteniendo IP local: {e}")
        return None, None

def scan_port(ip: str, port: int, timeout: float = 0.5) -> bool:
    """Verificar si un puerto está abierto."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def test_rtsp_url(url: str, timeout: int = 2) -> bool:
    """Probar si una URL RTSP responde."""
    try:
        import cv2
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, timeout * 1000)

        if cap.isOpened():
            ret, _ = cap.read()
            cap.release()
            return ret
        return False
    except:
        return False

def scan_ip_for_cameras(ip: str, ports: List[int], stream_paths: List[str]) -> List[Dict]:
    """Escanear una IP buscando cámaras en varios puertos y paths."""
    cameras = []

    for port in ports:
        if scan_port(ip, port):
            print(f"  🔍 Puerto {port} abierto en {ip}")

            for path in stream_paths:
                # Probar sin credenciales
                url = f"rtsp://{ip}:{port}{path}"
                print(f"    Probando: {url}")

                if test_rtsp_url(url):
                    cameras.append({
                        'ip': ip,
                        'port': port,
                        'path': path,
                        'url': url,
                        'requires_auth': False
                    })
                    print(f"    ✅ Funciona!")

    return cameras

def scan_network_for_cameras(network_base: str, start: int = 1, end: int = 254,
                            ports: Optional[List[int]] = None,
                            stream_paths: Optional[List[str]] = None) -> List[Dict]:
    """Escanear toda la red buscando cámaras."""
    if ports is None:
        ports = [554, 8554, 80, 8080]

    if stream_paths is None:
        stream_paths = [
            '/stream',
            '/live',
            '/cam/realmonitor?channel=1&subtype=0',
            '/video',
            '/h264',
            '/onvif1',
            '/Streaming/Channels/101'
        ]

    cameras = []
    ips_to_scan = [f"{network_base}.{i}" for i in range(start, end + 1)]

    print(f"🔍 Escaneando {len(ips_to_scan)} IPs en {network_base}.0/24")
    print(f"   Puertos: {ports}")
    print(f"   Buscando {len(stream_paths)} rutas de stream comunes...")
    print()

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {
            executor.submit(scan_ip_for_cameras, ip, ports, stream_paths): ip
            for ip in ips_to_scan
        }

        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            try:
                found = future.result()
                if found:
                    cameras.extend(found)
            except Exception as e:
                pass

    return cameras

def scan_arp_table() -> List[str]:
    """Obtener dispositivos activos de la tabla ARP."""
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        output = result.stdout

        # Extraer IPs (formato: device (192.168.1.100) at ...)
        ips = re.findall(r'\((\d+\.\d+\.\d+\.\d+)\)', output)
        return list(set(ips))
    except:
        return []

def quick_scan() -> List[str]:
    """Escaneo rápido de dispositivos activos en la red."""
    print("🔍 Escaneo rápido de dispositivos activos...")

    # Método 1: Tabla ARP
    devices = scan_arp_table()

    if devices:
        print(f"   Encontrados {len(devices)} dispositivos en tabla ARP")

    return devices

def main():
    print("╔════════════════════════════════════════════════════════╗")
    print("║     DETECCIÓN DE CÁMARAS IP - TERRY v6.1              ║")
    print("╚════════════════════════════════════════════════════════╝")
    print()

    # Verificar dependencias
    try:
        import cv2
    except ImportError:
        print("❌ Error: OpenCV no está instalado")
        print("   Instalar con: pip install opencv-python")
        return

    # Obtener red local
    network_base, local_ip = get_local_ip_range()
    if not network_base:
        return

    print(f"📡 Tu IP local: {local_ip}")
    print(f"📡 Red local: {network_base}.0/24")
    print()

    # Opciones de escaneo
    print("¿Cómo quieres buscar cámaras?")
    print("  1) Escaneo rápido (solo dispositivos activos en ARP)")
    print("  2) Escaneo completo (toda la red, más lento)")
    print("  3) Escanear IP específica")
    print()

    choice = input("Selecciona (1/2/3): ").strip()

    cameras = []

    if choice == "1":
        # Escaneo rápido
        devices = quick_scan()
        if not devices:
            print("❌ No se encontraron dispositivos activos")
            print("   Prueba el escaneo completo (opción 2)")
            return

        print(f"\n🔍 Probando {len(devices)} dispositivos...")
        print()

        for ip in devices:
            found = scan_ip_for_cameras(
                ip,
                ports=[554, 8554, 80, 8080],
                stream_paths=['/stream', '/live', '/cam/realmonitor?channel=1&subtype=0']
            )
            cameras.extend(found)

    elif choice == "2":
        # Escaneo completo
        print("\n⚠️  Esto puede tardar varios minutos...")
        print()
        cameras = scan_network_for_cameras(network_base)

    elif choice == "3":
        # IP específica
        ip = input("\nIP de la cámara: ").strip()
        print()
        cameras = scan_ip_for_cameras(
            ip,
            ports=[554, 8554, 80, 8080, 88],
            stream_paths=[
                '/stream', '/live', '/video', '/h264',
                '/cam/realmonitor?channel=1&subtype=0',
                '/onvif1', '/Streaming/Channels/101'
            ]
        )

    # Mostrar resultados
    print()
    print("═" * 60)
    if cameras:
        print(f"✅ Se encontraron {len(cameras)} cámara(s):")
        print()

        for i, cam in enumerate(cameras, 1):
            print(f"{i}. {cam['url']}")
            print(f"   IP: {cam['ip']}, Puerto: {cam['port']}, Path: {cam['path']}")
            if cam['requires_auth']:
                print(f"   ⚠️  Requiere autenticación")
            print()

        # Preguntar si configurar
        if len(cameras) == 1:
            config = input("¿Configurar Terry con esta cámara? (s/n): ").strip().lower()
            if config == 's':
                configure_terry(cameras[0])
        else:
            selection = input(f"¿Configurar Terry con alguna cámara? (1-{len(cameras)}/n): ").strip()
            if selection.isdigit() and 1 <= int(selection) <= len(cameras):
                configure_terry(cameras[int(selection) - 1])

    else:
        print("❌ No se encontraron cámaras IP")
        print()
        print("Posibles razones:")
        print("  - La cámara no está conectada a la red")
        print("  - La cámara usa un puerto o path diferente")
        print("  - La cámara requiere autenticación")
        print()
        print("Prueba configurar manualmente:")
        print("  python3 scripts/tools/configure_camera.py")

    print("═" * 60)

def configure_terry(camera: Dict):
    """Configurar Terry con la cámara encontrada."""
    try:
        import yaml

        settings_path = Path(__file__).parent.parent.parent / "terry" / "core" / "config" / "settings.yaml"

        with open(settings_path, 'r') as f:
            settings = yaml.safe_load(f)

        # Actualizar configuración
        if "camera_vision" not in settings:
            settings["camera_vision"] = {}

        settings["camera_vision"]["camera_url"] = camera['url']
        settings["camera_vision"]["use_webcam"] = False

        # Preguntar credenciales si se requieren
        if camera['requires_auth']:
            username = input("Usuario de la cámara: ").strip()
            password = input("Contraseña: ").strip()

            if username and password:
                settings["camera_vision"]["camera_username"] = username
                settings["camera_vision"]["camera_password"] = password

                # Actualizar URL con credenciales
                url_parts = camera['url'].split('://')
                if len(url_parts) == 2:
                    settings["camera_vision"]["camera_url"] = f"{url_parts[0]}://{username}:{password}@{url_parts[1]}"

        # Preguntar si auto-iniciar
        auto_start = input("¿Iniciar cámara automáticamente con Terry? (s/n) [n]: ").strip().lower()
        settings["camera_vision"]["auto_start"] = (auto_start == 's')

        # Guardar
        with open(settings_path, 'w') as f:
            yaml.dump(settings, f, default_flow_style=False, allow_unicode=True)

        print()
        print("✅ Configuración guardada")
        print()
        print("Para probar la cámara:")
        print("  1. Inicia Terry: ./bin/run_voice.sh")
        print("  2. Di: 'Terry, activa la cámara'")
        print("  3. Di: 'Terry, quién está aquí'")
        print()

    except Exception as e:
        print(f"❌ Error guardando configuración: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelado")
    except Exception as e:
        print(f"\n❌ Error: {e}")
