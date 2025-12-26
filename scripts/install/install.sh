#!/bin/bash
# Home-Alexa - Script de Instalación
# Instala todas las dependencias y configura el sistema

set -e

echo "=== Home-Alexa - Instalación ===="
echo

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}Error: Este proyecto está diseñado para macOS${NC}"
    exit 1
fi

# Verificar Mac con Apple Silicon
ARCH=$(uname -m)
if [[ "$ARCH" != "arm64" ]]; then
    echo -e "${YELLOW}Advertencia: Este proyecto está optimizado para Apple Silicon (M1/M2/M3/M4)${NC}"
    echo -e "${YELLOW}Puede que algunas características no funcionen óptimamente${NC}"
    read -p "¿Continuar de todos modos? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar Python 3.10+
echo -e "${GREEN}[1/8]${NC} Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 no está instalado${NC}"
    echo "Instala Python 3.10+ desde https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo -e "${RED}Error: Se requiere Python 3.10 o superior (tienes $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION encontrado"

# Verificar Ollama
echo -e "${GREEN}[2/8]${NC} Verificando Ollama..."
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Advertencia: Ollama no está instalado${NC}"
    echo "Instala Ollama desde: https://ollama.ai"
    echo "Luego ejecuta: ollama pull llama3.1"
    read -p "¿Continuar sin Ollama? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Ollama encontrado"

    # Verificar si Ollama está corriendo
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ollama está corriendo"
    else
        echo -e "${YELLOW}Advertencia: Ollama no está corriendo${NC}"
        echo "Inicia Ollama con: ollama serve"
    fi
fi

# Crear entorno virtual
echo -e "${GREEN}[3/8]${NC} Creando entorno virtual..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓${NC} Entorno virtual creado"
else
    echo -e "${GREEN}✓${NC} Entorno virtual ya existe"
fi

# Activar entorno virtual
source .venv/bin/activate

# Actualizar pip
echo -e "${GREEN}[4/8]${NC} Actualizando pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip actualizado"

# Instalar dependencias
echo -e "${GREEN}[5/8]${NC} Instalando dependencias..."
echo "Esto puede tardar varios minutos..."
pip install -r requirements.txt

# Verificar instalación de dependencias clave
echo -e "${GREEN}[6/8]${NC} Verificando instalación..."

MISSING_DEPS=()

# Verificar mlx_whisper
if ! python3 -c "import mlx_whisper" 2>/dev/null; then
    MISSING_DEPS+=("mlx_whisper")
fi

# Verificar sounddevice
if ! python3 -c "import sounddevice" 2>/dev/null; then
    MISSING_DEPS+=("sounddevice")
fi

# Verificar pyyaml
if ! python3 -c "import yaml" 2>/dev/null; then
    MISSING_DEPS+=("pyyaml")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${RED}Error: Faltan dependencias: ${MISSING_DEPS[*]}${NC}"
    echo "Intenta instalarlas manualmente con: pip install ${MISSING_DEPS[*]}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Dependencias verificadas"

# Crear directorios necesarios
echo -e "${GREEN}[7/8]${NC} Creando directorios..."
mkdir -p logs data config/voices config/wakewords

echo -e "${GREEN}✓${NC} Directorios creados"

# Configuración inicial
echo -e "${GREEN}[8/8]${NC} Configuración inicial..."

if [ ! -f "config/settings.yaml" ]; then
    echo -e "${YELLOW}Advertencia: No se encontró config/settings.yaml${NC}"
    echo "Usando configuración por defecto"
fi

echo -e "${GREEN}✓${NC} Configuración completada"

# Resumen
echo
echo -e "${GREEN}=== Instalación Completada ===${NC}"
echo
echo "Pasos siguientes:"
echo "1. Asegúrate de que Ollama esté corriendo:"
echo "   $ ollama serve"
echo
echo "2. Descarga un modelo (si no lo has hecho):"
echo "   $ ollama pull llama3.1"
echo
echo "3. Descarga voces para Piper (opcional):"
echo "   Coloca los archivos .onnx en: config/voices/"
echo
echo "4. Inicia Home-Alexa:"
echo "   $ ./run.sh"
echo
echo "Para instalar como servicio de sistema (inicio automático):"
echo "   $ ./install_service.sh"
echo

exit 0
