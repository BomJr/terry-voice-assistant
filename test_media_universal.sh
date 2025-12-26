#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   TEST: CONTROL UNIVERSAL DE MEDIOS      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo

echo -e "${YELLOW}Este test usa comandos UNIVERSALES que NO activan navegadores${NC}"
echo -e "${YELLOW}Solo controlan lo que ESTÁ REPRODUCIENDO${NC}"
echo

echo "📋 INSTRUCCIONES:"
echo "1. Abre YouTube en CUALQUIER navegador (Atlas, Safari, etc.)"
echo "2. Reproduce un video"
echo "3. NO cambies de ventana (mantente aquí en Terminal)"
echo

echo -e "${BLUE}Presiona Enter cuando el video esté reproduciendo...${NC}"
read

echo
echo -e "${GREEN}=== TEST 1: Media Key F8 (Play/Pause) ===${NC}"
echo "Enviando comando de media play/pause..."
osascript -e 'tell application "System Events" to key code 100'

echo
echo -e "${YELLOW}¿Se pausó el video SIN abrir el navegador? (s/n)${NC}"
read test1

echo
echo -e "${GREEN}=== TEST 2: Reproducir de nuevo ===${NC}"
echo "Presiona Enter para reproducir..."
read
osascript -e 'tell application "System Events" to key code 100'

echo
echo -e "${YELLOW}¿Se reprodujo el video SIN abrir el navegador? (s/n)${NC}"
read test2

echo
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  RESULTADOS${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

if [ "$test1" = "s" ] && [ "$test2" = "s" ]; then
    echo -e "${GREEN}✅ ¡PERFECTO! El método universal FUNCIONA${NC}"
    echo
    echo "Este método:"
    echo "  ✅ NO abre navegadores"
    echo "  ✅ NO escribe letras"
    echo "  ✅ Controla lo que ESTÁ reproduciendo"
    echo "  ✅ Funciona con YouTube, Spotify, Music, etc."
    echo
    echo "Voy a actualizar el código para usar esto."
    echo
    echo "Luego ejecuta: ${YELLOW}./run_test.sh${NC}"
    echo "Y prueba: ${YELLOW}para la música${NC}"
else
    echo -e "${RED}❌ El método F8 no funcionó${NC}"
    echo
    echo "Vamos a probar otros key codes..."
    echo

    # Test alternativo: key code 16 (otra media key)
    echo -e "${YELLOW}TEST ALTERNATIVO: Key code 16${NC}"
    echo "Presiona Enter..."
    read
    osascript -e 'tell application "System Events" to key code 16'

    echo -e "${YELLOW}¿Funcionó este? (s/n)${NC}"
    read test3

    if [ "$test3" = "s" ]; then
        echo -e "${GREEN}✅ Key code 16 funciona${NC}"
        echo "Voy a usar este en su lugar."
    else
        echo -e "${RED}❌ Tampoco funcionó${NC}"
        echo
        echo "Última opción: usar AppleScript para consultar qué está reproduciendo"
        echo "y controlarlo específicamente sin activar ventanas."
    fi
fi
