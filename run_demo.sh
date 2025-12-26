#!/bin/bash
# Terry v6.1 - Ejecutar Demo Interactivo

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                ║${NC}"
echo -e "${CYAN}║      TERRY v6.1 - DEMO INTERACTIVO            ║${NC}"
echo -e "${CYAN}║      20 Mejoras Sustanciales                   ║${NC}"
echo -e "${CYAN}║                                                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo

# Activar entorno virtual
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado${NC}"
    echo "   Ejecuta primero: python3 -m venv .venv"
    echo "   Luego: ./install_v6_1.sh"
    exit 1
fi

source .venv/bin/activate

# Verificar Rich library
python3 -c "import rich" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}📦 Instalando Rich library...${NC}"
    pip install -q rich
fi

# Ejecutar demo
echo -e "${GREEN}🚀 Iniciando demo...${NC}"
echo
python3 demo_v6_1.py

echo
echo -e "${GREEN}✨ Demo completada${NC}"
