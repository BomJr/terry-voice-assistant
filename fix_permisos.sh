#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${RED}╔══════════════════════════════════════════╗${NC}"
echo -e "${RED}║   ❌ PROBLEMA: FALTAN PERMISOS           ║${NC}"
echo -e "${RED}╚══════════════════════════════════════════╝${NC}"
echo

echo -e "${YELLOW}El control de música NO funciona porque Terminal${NC}"
echo -e "${YELLOW}no tiene permisos de Accesibilidad.${NC}"
echo

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  SIGUE ESTOS PASOS:${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo

echo -e "${YELLOW}1.${NC} Abre: ${GREEN}Preferencias del Sistema${NC}"
echo "   (Click en  en la barra superior)"
echo

echo -e "${YELLOW}2.${NC} Ve a: ${GREEN}Privacidad y Seguridad${NC}"
echo

echo -e "${YELLOW}3.${NC} Click en: ${GREEN}Accesibilidad${NC}"
echo "   (En el menú izquierdo)"
echo

echo -e "${YELLOW}4.${NC} Click en el ${GREEN}candado 🔒${NC} para desbloquear"
echo "   (Ingresa tu contraseña)"
echo

echo -e "${YELLOW}5.${NC} Busca ${GREEN}Terminal${NC} en la lista"
echo "   Si NO está, click en '+' y añádela desde:"
echo "   ${BLUE}/System/Applications/Utilities/Terminal.app${NC}"
echo

echo -e "${YELLOW}6.${NC} ${GREEN}Marca el checkbox ✅${NC} junto a Terminal"
echo

echo -e "${YELLOW}7.${NC} Cierra Preferencias"
echo

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo

echo -e "${YELLOW}Presiona Enter cuando hayas terminado...${NC}"
read

echo
echo "Verificando permisos..."
sleep 1

# Probar permisos
result=$(osascript -e 'tell application "System Events" to get name of first process' 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ ¡PERMISOS OTORGADOS CORRECTAMENTE!${NC}"
    echo
    echo -e "${BLUE}Ahora prueba el control de música:${NC}"
    echo -e "${YELLOW}./test_youtube_manual.sh${NC}"
else
    echo -e "${RED}❌ Todavía no hay permisos${NC}"
    echo
    echo "Posibles causas:"
    echo "1. No marcaste el checkbox de Terminal"
    echo "2. Terminal debe estar en la lista de Accesibilidad"
    echo "3. Necesitas reiniciar Terminal (Cmd+Q y ábrela de nuevo)"
    echo
    echo "Intenta de nuevo o lee:"
    echo -e "${YELLOW}cat OTORGAR_PERMISOS.md${NC}"
fi
