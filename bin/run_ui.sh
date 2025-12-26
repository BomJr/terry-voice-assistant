#!/bin/bash
# Terry v6.1 - Ejecutar UI Web

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                ║${NC}"
echo -e "${CYAN}║      TERRY v6.1 - WEB UI                      ║${NC}"
echo -e "${CYAN}║      Professional Interface                    ║${NC}"
echo -e "${CYAN}║                                                ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════╝${NC}"
echo

# Activar entorno virtual
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Entorno virtual no encontrado${NC}"
    echo "   Creando entorno virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Verificar dependencias
echo -e "${YELLOW}📦 Verificando dependencias...${NC}"
python3 -c "import fastapi, uvicorn, jinja2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "   Instalando dependencias de la UI..."
    pip install -q fastapi uvicorn jinja2
fi

# Crear directorio de logs si no existe
mkdir -p logs

echo
echo -e "${GREEN}🚀 Iniciando UI Web...${NC}"
echo
echo -e "   🌐 URL: ${CYAN}http://localhost:8080${NC}"
echo -e "   📡 WebSocket: ${CYAN}ws://localhost:8080/ws${NC}"
echo
echo -e "${YELLOW}   Presiona Ctrl+C para detener${NC}"
echo

# Ejecutar aplicación
python3 -m terry.core.ui.web.app
