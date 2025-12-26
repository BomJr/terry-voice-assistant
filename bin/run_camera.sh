#!/bin/bash

# Script para ejecutar el sistema de cámara de Terry
# Activa la cámara y muestra el reconocimiento facial en tiempo real

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     SISTEMA DE CÁMARA - TERRY v6.1                    ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Verificar que existe el venv
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ No se encontró el entorno virtual (.venv)${NC}"
    echo "Ejecuta: ./scripts/install/install.sh"
    exit 1
fi

# Activar entorno virtual
echo -e "${YELLOW}🔧 Activando entorno virtual...${NC}"
source .venv/bin/activate

# Verificar configuración
echo -e "${YELLOW}📋 Configuración actual:${NC}"
CAMERA_URL=$(grep "camera_url:" terry/core/config/settings.yaml | awk '{print $2}')
echo -e "   URL: ${GREEN}$CAMERA_URL${NC}"
echo ""

# Preguntar si quiere probar primero
echo -e "${YELLOW}¿Quieres probar la conexión primero? (S/n):${NC} "
read -r TEST_FIRST

if [[ ! "$TEST_FIRST" =~ ^[Nn]$ ]]; then
    echo -e "${BLUE}🧪 Probando conexión...${NC}"
    python3 scripts/tools/test_camera.py
    echo ""
    echo -e "${YELLOW}¿Continuar con el sistema de cámara? (S/n):${NC} "
    read -r CONTINUE
    if [[ "$CONTINUE" =~ ^[Nn]$ ]]; then
        echo -e "${RED}Cancelado${NC}"
        exit 0
    fi
fi

# Ejecutar sistema de cámara
echo ""
echo -e "${GREEN}🎥 Iniciando sistema de cámara...${NC}"
echo -e "${YELLOW}Presiona Ctrl+C para detener${NC}"
echo ""

# Ir al directorio de face-recognition y ejecutar
cd ~/face-recognition
python3 src/main.py

echo ""
echo -e "${GREEN}✅ Sistema de cámara detenido${NC}"
