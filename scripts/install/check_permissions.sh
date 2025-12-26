#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo "═══════════════════════════════════════"
echo "  VERIFICACIÓN DE PERMISOS"
echo "═══════════════════════════════════════"
echo

echo "Probando si Terminal puede controlar otras apps..."
echo

# Test 1: Verificar si puede obtener lista de procesos
echo "Test 1: Leer lista de procesos..."
result=$(osascript -e 'tell application "System Events" to get name of first process' 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Terminal puede leer procesos${NC}"
    echo "   (Proceso detectado: $result)"
else
    echo -e "${RED}❌ Terminal NO puede leer procesos${NC}"
    echo "   Error: $result"
    echo
    echo -e "${YELLOW}SOLUCIÓN:${NC}"
    echo "1. Abre: Preferencias del Sistema"
    echo "2. Ve a: Privacidad y Seguridad"
    echo "3. Click en: Accesibilidad (en el menú izquierdo)"
    echo "4. Click en el candado 🔒 para desbloquear"
    echo "5. Busca 'Terminal' en la lista"
    echo "6. Activa el checkbox ✅ junto a Terminal"
    echo "7. Si no está en la lista, click en '+' y añade Terminal"
    echo
    echo "Terminal está en: /System/Applications/Utilities/Terminal.app"
    echo
    echo "Después ejecuta este script de nuevo."
    exit 1
fi

echo

# Test 2: Verificar si puede enviar teclas
echo "Test 2: Enviar tecla de prueba..."
result=$(osascript -e 'tell application "System Events" to keystroke "test"' 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Terminal puede enviar teclas${NC}"
else
    echo -e "${RED}❌ Terminal NO puede enviar teclas${NC}"
    echo "   Error: $result"
    exit 1
fi

echo

# Test 3: Verificar si puede activar Safari
echo "Test 3: Activar Safari..."
result=$(osascript -e 'tell application "Safari" to activate' 2>&1)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Terminal puede activar Safari${NC}"
else
    echo -e "${YELLOW}⚠️  Safari no está corriendo o hay un error${NC}"
    echo "   Error: $result"
fi

echo
echo "═══════════════════════════════════════"
echo -e "${GREEN}✅ PERMISOS CORRECTOS${NC}"
echo "═══════════════════════════════════════"
echo
echo "Ahora prueba el control de música:"
echo -e "${YELLOW}./test_youtube_manual.sh${NC}"
