#!/bin/bash
# Terry v6.0 - Launcher con DEBUG habilitado

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                ║${NC}"
echo -e "${BLUE}║         TERRY v6.0 - MODO DEBUG                ║${NC}"
echo -e "${BLUE}║                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo

# Activar entorno
source .venv/bin/activate

echo -e "${CYAN}🐛 MODO DEBUG ACTIVADO${NC}"
echo "  - Verás logs detallados de TTS"
echo "  - Verás logs de procesamiento"
echo "  - Podrás diagnosticar problemas"
echo

echo -e "${YELLOW}¿Qué modo quieres usar?${NC}"
echo "  1) Modo continuo (escucha siempre)"
echo "  2) Modo wake word (di 'terry')"
echo
read -p "Selecciona (1/2) [2]: " mode
mode=${mode:-2}

echo

# Crear archivo de log temporal
LOG_FILE="/tmp/terry_debug_$(date +%s).log"

if [ "$mode" = "1" ]; then
    echo -e "${CYAN}⚡ Modo Continuo con DEBUG${NC}"
    echo "Logs en: $LOG_FILE"
    echo
    python3 -m voice.voice_pipeline 2>&1 | tee "$LOG_FILE"
else
    echo -e "${CYAN}🔒 Modo Wake Word con DEBUG${NC}"
    echo "Logs en: $LOG_FILE"
    echo
    python3 -m voice.voice_pipeline --wake-word 2>&1 | tee "$LOG_FILE"
fi

echo
echo -e "${GREEN}Logs guardados en: $LOG_FILE${NC}"
