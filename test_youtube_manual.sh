#!/bin/bash

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo -e "${GREEN}╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   PRUEBA MANUAL: CONTROL DE YOUTUBE      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════╝${NC}"
echo

echo -e "${YELLOW}📋 INSTRUCCIONES:${NC}"
echo "1. Abre YouTube en tu navegador (Atlas, Chrome, Safari, etc.)"
echo "2. Reproduce un video"
echo "3. Vuelve a esta terminal"
echo

echo -e "${BLUE}Presiona Enter cuando tengas el video reproduciendo...${NC}"
read

echo
echo -e "${GREEN}=== PRUEBA 1: PAUSAR ===${NC}"
echo "Ejecutando: osascript para PAUSAR..."

# Detectar navegador (prioridad: Atlas primero)
BROWSER="Safari"
if pgrep -x "Atlas" > /dev/null; then
    BROWSER="Atlas"
elif pgrep -x "Arc" > /dev/null; then
    BROWSER="Arc"
elif pgrep -x "Google Chrome" > /dev/null; then
    BROWSER="Google Chrome"
elif pgrep -x "Safari" > /dev/null; then
    BROWSER="Safari"
fi

echo "Navegador detectado: $BROWSER"

osascript -e "
tell application \"$BROWSER\" to activate
delay 0.5
tell application \"System Events\"
    keystroke \"k\"
end tell
"

echo
echo -e "${YELLOW}¿Se pausó el video? (s/n)${NC}"
read response1

if [ "$response1" = "s" ]; then
    echo -e "${GREEN}✅ PAUSAR funciona!${NC}"
else
    echo -e "${RED}❌ PAUSAR no funciona${NC}"
fi

echo
echo -e "${BLUE}Presiona Enter para probar REPRODUCIR...${NC}"
read

echo
echo -e "${GREEN}=== PRUEBA 2: REPRODUCIR ===${NC}"
echo "Ejecutando: osascript para REPRODUCIR..."

osascript -e "
tell application \"$BROWSER\" to activate
delay 0.5
tell application \"System Events\"
    keystroke \"k\"
end tell
"

echo
echo -e "${YELLOW}¿Se reprodujo el video? (s/n)${NC}"
read response2

if [ "$response2" = "s" ]; then
    echo -e "${GREEN}✅ REPRODUCIR funciona!${NC}"
else
    echo -e "${RED}❌ REPRODUCIR no funciona${NC}"
fi

echo
echo -e "${BLUE}Presiona Enter para probar SIGUIENTE VIDEO...${NC}"
read

echo
echo -e "${GREEN}=== PRUEBA 3: SIGUIENTE ===${NC}"
echo "Ejecutando: osascript para SIGUIENTE..."

osascript -e "
tell application \"$BROWSER\" to activate
delay 0.1
tell application \"System Events\"
    keystroke \"n\" using {shift down}
end tell
"

echo
echo -e "${YELLOW}¿Pasó al siguiente video? (s/n)${NC}"
read response3

if [ "$response3" = "s" ]; then
    echo -e "${GREEN}✅ SIGUIENTE funciona!${NC}"
else
    echo -e "${RED}❌ SIGUIENTE no funciona${NC}"
fi

echo
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  RESUMEN${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"

if [ "$response1" = "s" ]; then
    echo -e "✅ Pausar"
else
    echo -e "❌ Pausar"
fi

if [ "$response2" = "s" ]; then
    echo -e "✅ Reproducir"
else
    echo -e "❌ Reproducir"
fi

if [ "$response3" = "s" ]; then
    echo -e "✅ Siguiente"
else
    echo -e "❌ Siguiente"
fi

echo
if [ "$response1" = "s" ] && [ "$response2" = "s" ]; then
    echo -e "${GREEN}🎉 ¡TODO FUNCIONA! Ahora prueba:${NC}"
    echo -e "${BLUE}   ./run_test.sh${NC}"
    echo
    echo -e "Y escribe: ${YELLOW}para la música${NC}"
else
    echo -e "${RED}⚠️  Hay problemas. Posibles causas:${NC}"
    echo "1. Permisos de Accesibilidad no otorgados"
    echo "   → Preferencias → Privacidad → Accesibilidad → Terminal ✅"
    echo
    echo "2. El navegador no está en primer plano"
    echo "   → El script activa el navegador automáticamente"
    echo
    echo "3. YouTube tiene controles diferentes"
    echo "   → Intenta presionar ESPACIO manualmente primero"
fi
