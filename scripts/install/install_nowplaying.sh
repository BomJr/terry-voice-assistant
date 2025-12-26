#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   INSTALANDO nowplaying-cli              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo

echo -e "${YELLOW}nowplaying-cli${NC} es una herramienta que controla medios"
echo "sin activar ventanas ni escribir texto."
echo

# Verificar si ya está instalado
if command -v nowplaying-cli &> /dev/null; then
    echo -e "${GREEN}✅ nowplaying-cli ya está instalado${NC}"
    echo "Versión: $(nowplaying-cli --version 2>&1 || echo 'desconocida')"
    exit 0
fi

# Verificar si Homebrew está instalado
if ! command -v brew &> /dev/null; then
    echo -e "${RED}❌ Homebrew no está instalado${NC}"
    echo
    echo "Necesitas Homebrew para instalar nowplaying-cli."
    echo
    echo "Instala Homebrew ejecutando:"
    echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo
    echo "O visita: https://brew.sh"
    exit 1
fi

echo -e "${YELLOW}Instalando nowplaying-cli con Homebrew...${NC}"
echo

brew install nowplaying-cli

if [ $? -eq 0 ]; then
    echo
    echo -e "${GREEN}✅ nowplaying-cli instalado correctamente${NC}"
    echo
    echo "Probando..."
    nowplaying-cli --version
    echo
    echo -e "${GREEN}Ahora ejecuta:${NC}"
    echo -e "${YELLOW}  ./run_test.sh${NC}"
    echo
    echo "Y prueba: ${YELLOW}para la música${NC}"
else
    echo
    echo -e "${RED}❌ Error instalando nowplaying-cli${NC}"
    echo
    echo "Intenta instalarlo manualmente:"
    echo "  brew install nowplaying-cli"
fi
