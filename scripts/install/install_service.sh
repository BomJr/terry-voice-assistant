#!/bin/bash
# Home-Alexa - Instalación como Servicio de macOS (LaunchAgent)

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=== Home-Alexa - Instalación como Servicio ===="
echo

# Obtener ruta absoluta del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Nombre del servicio
SERVICE_NAME="com.homealexa.assistant"
PLIST_FILE="$HOME/Library/LaunchAgents/$SERVICE_NAME.plist"

# Verificar que el proyecto esté instalado
if [ ! -f "$PROJECT_DIR/main.py" ]; then
    echo -e "${RED}Error: No se encontró main.py${NC}"
    echo "Asegúrate de estar en el directorio del proyecto"
    exit 1
fi

if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo -e "${RED}Error: Entorno virtual no encontrado${NC}"
    echo "Ejecuta primero: ./install.sh"
    exit 1
fi

# Crear directorio LaunchAgents si no existe
mkdir -p "$HOME/Library/LaunchAgents"

# Crear archivo plist
echo -e "${GREEN}[1/4]${NC} Creando LaunchAgent..."

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$SERVICE_NAME</string>

    <key>ProgramArguments</key>
    <array>
        <string>$PROJECT_DIR/.venv/bin/python3</string>
        <string>$PROJECT_DIR/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/service.log</string>

    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/service_error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>

    <key>ThrottleInterval</key>
    <integer>30</integer>
</dict>
</plist>
EOF

echo -e "${GREEN}✓${NC} LaunchAgent creado: $PLIST_FILE"

# Cargar el servicio
echo -e "${GREEN}[2/4]${NC} Cargando servicio..."

# Descargar si ya existe
if launchctl list | grep -q "$SERVICE_NAME"; then
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
fi

# Cargar nuevo servicio
launchctl load "$PLIST_FILE"

echo -e "${GREEN}✓${NC} Servicio cargado"

# Verificar estado
echo -e "${GREEN}[3/4]${NC} Verificando estado..."
sleep 2

if launchctl list | grep -q "$SERVICE_NAME"; then
    echo -e "${GREEN}✓${NC} Servicio activo"
else
    echo -e "${RED}✗${NC} Error: El servicio no está activo"
    echo "Revisa los logs en: $PROJECT_DIR/logs/"
    exit 1
fi

# Información
echo -e "${GREEN}[4/4]${NC} Completado"
echo
echo -e "${GREEN}=== Servicio Instalado ===${NC}"
echo
echo "El asistente se iniciará automáticamente al iniciar sesión."
echo
echo "Comandos útiles:"
echo "  Ver estado:       launchctl list | grep homealexa"
echo "  Detener servicio: launchctl unload ~/Library/LaunchAgents/$SERVICE_NAME.plist"
echo "  Iniciar servicio: launchctl load ~/Library/LaunchAgents/$SERVICE_NAME.plist"
echo "  Ver logs:         tail -f $PROJECT_DIR/logs/service.log"
echo "  Ver errores:      tail -f $PROJECT_DIR/logs/service_error.log"
echo
echo "Para desinstalar el servicio:"
echo "  $ ./uninstall_service.sh"
echo

exit 0
