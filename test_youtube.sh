#!/bin/bash
# Test de control de YouTube

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   TEST: CONTROL DE YOUTUBE EN NAVEGADOR  ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo

echo -e "${BLUE}📋 INSTRUCCIONES:${NC}"
echo "1. Abre YouTube en tu navegador (Chrome, Safari, Arc, Atlas, etc.)"
echo "2. Reproduce un video"
echo "3. Mantén esta ventana en primer plano"
echo "4. Ejecuta los comandos de prueba abajo"
echo

echo -e "${YELLOW}Presiona Enter para continuar...${NC}"
read

echo -e "${GREEN}Iniciando sistema...${NC}"
echo
source .venv/bin/activate
python3 test_simple.py
