#!/bin/bash
# Home-Alexa - Modo Test Rápido

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo -e "${GREEN}=== Home-Alexa ULTRA-RÁPIDO ===${NC}"
echo

# Verificar sistema
source .venv/bin/activate
python3 check_system.py
if [ $? -ne 0 ]; then
    echo
    echo -e "${YELLOW}⚠️  Corrige los requisitos faltantes y vuelve a intentar${NC}"
    exit 1
fi

echo
echo "Optimizaciones activadas:"
echo "  ⚡ Caché de respuestas comunes (0.00s)"
echo "  🤖 LLM optimizado (1-2s)"
echo "  🔥 Prompts comprimidos (70% más rápido)"
echo
echo -e "${YELLOW}Nota:${NC} Comandos comunes usan caché instantáneo"
echo

python3 test_simple.py
