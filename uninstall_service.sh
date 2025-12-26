#!/bin/bash
# Home-Alexa - Desinstalación del Servicio

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

SERVICE_NAME="com.homealexa.assistant"
PLIST_FILE="$HOME/Library/LaunchAgents/$SERVICE_NAME.plist"

echo "=== Home-Alexa - Desinstalación del Servicio ===="
echo

if [ ! -f "$PLIST_FILE" ]; then
    echo -e "${RED}El servicio no está instalado${NC}"
    exit 1
fi

# Descargar servicio
echo "Deteniendo servicio..."
launchctl unload "$PLIST_FILE" 2>/dev/null || true

# Eliminar archivo plist
echo "Eliminando configuración..."
rm "$PLIST_FILE"

echo -e "${GREEN}✓${NC} Servicio desinstalado correctamente"
echo

exit 0
