#!/bin/bash

# Script para iniciar directamente el sistema de cámara (sin preguntas)

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🎥 INICIANDO CÁMARA DE TERRY...${NC}\n"

# Directorio del proyecto
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Activar entorno virtual
source .venv/bin/activate

# Mostrar configuración
CAMERA_URL=$(grep "camera_url:" terry/core/config/settings.yaml | awk '{print $2}')
echo -e "${YELLOW}📋 URL:${NC} $CAMERA_URL"
echo -e "${YELLOW}⌨️  Presiona Ctrl+C para detener${NC}\n"

# Ejecutar
cd ~/face-recognition
python3 src/main.py
