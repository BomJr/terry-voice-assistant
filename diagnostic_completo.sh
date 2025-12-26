#!/bin/bash

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   DIAGNÓSTICO COMPLETO DEL SISTEMA       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo

# Test 1: Permisos básicos
echo -e "${YELLOW}Test 1: Permisos de Accesibilidad${NC}"
result=$(osascript -e 'tell application "System Events" to get name of first process' 2>&1)
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✅ Terminal tiene permisos básicos${NC}"
else
    echo -e "  ${RED}❌ NO HAY PERMISOS DE ACCESIBILIDAD${NC}"
    echo "  Error: $result"
    echo
    echo -e "${YELLOW}SOLUCIÓN:${NC}"
    echo "  1. Preferencias del Sistema"
    echo "  2. Privacidad y Seguridad → Accesibilidad"
    echo "  3. Marca ✅ Terminal"
    exit 1
fi
echo

# Test 2: Detectar navegadores
echo -e "${YELLOW}Test 2: Navegadores en ejecución${NC}"
BROWSERS=("Safari" "Google Chrome" "Arc" "Atlas" "Brave Browser")
RUNNING_BROWSER=""

for browser in "${BROWSERS[@]}"; do
    if pgrep -x "$browser" > /dev/null; then
        echo -e "  ${GREEN}✅ $browser está corriendo${NC}"
        if [ -z "$RUNNING_BROWSER" ]; then
            RUNNING_BROWSER="$browser"
        fi
    else
        echo -e "  ⚪ $browser no está corriendo"
    fi
done

if [ -z "$RUNNING_BROWSER" ]; then
    echo -e "  ${RED}❌ NO hay navegador corriendo${NC}"
    echo
    echo "  Por favor abre un navegador (Safari, Chrome, Arc, Atlas)"
    echo "  y ejecuta este script de nuevo."
    exit 1
fi

echo
echo -e "  ${BLUE}Usando: $RUNNING_BROWSER${NC}"
echo

# Test 3: Activar navegador
echo -e "${YELLOW}Test 3: Activar navegador${NC}"
result=$(osascript -e "tell application \"$RUNNING_BROWSER\" to activate" 2>&1)
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✅ Navegador activado${NC}"
    sleep 1
else
    echo -e "  ${RED}❌ No se pudo activar${NC}"
    echo "  Error: $result"
    exit 1
fi
echo

# Test 4: Enviar tecla simple
echo -e "${YELLOW}Test 4: Enviar tecla 'k' al sistema${NC}"
echo "  (Espera 2 segundos...)"
result=$(osascript -e 'tell application "System Events" to keystroke "k"' 2>&1)
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✅ Tecla enviada correctamente${NC}"
else
    echo -e "  ${RED}❌ Error enviando tecla${NC}"
    echo "  Error: $result"
    exit 1
fi
echo

# Test 5: Verificar YouTube
echo -e "${YELLOW}Test 5: Verificación de YouTube${NC}"
echo -e "  ${YELLOW}¿Tienes YouTube abierto en $RUNNING_BROWSER? (s/n)${NC}"
read has_youtube

if [ "$has_youtube" != "s" ]; then
    echo -e "  ${RED}❌ Abre YouTube primero${NC}"
    echo
    echo "  INSTRUCCIONES:"
    echo "  1. Abre YouTube en $RUNNING_BROWSER"
    echo "  2. Reproduce un video"
    echo "  3. Ejecuta este script de nuevo"
    exit 1
fi

echo -e "  ${YELLOW}¿Hay un video REPRODUCIENDO ahora? (s/n)${NC}"
read is_playing

if [ "$is_playing" != "s" ]; then
    echo -e "  ${RED}❌ Reproduce un video primero${NC}"
    exit 1
fi

echo -e "  ${GREEN}✅ YouTube listo${NC}"
echo

# Test 6: Prueba REAL de control
echo -e "${YELLOW}Test 6: Control REAL de YouTube${NC}"
echo "  Presiona Enter para intentar PAUSAR/REPRODUCIR..."
read

echo "  Ejecutando comando..."
osascript -e "
tell application \"$RUNNING_BROWSER\" to activate
delay 1.0
tell application \"System Events\"
    keystroke \"k\"
end tell
"

echo
echo -e "${YELLOW}¿El video se pausó o reprodujo? (s/n)${NC}"
read worked

if [ "$worked" = "s" ]; then
    echo -e "  ${GREEN}✅ ¡FUNCIONA!${NC}"
    echo
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✅ TODO ESTÁ BIEN${NC}"
    echo -e "${GREEN}═══════════════════════════════════════${NC}"
    echo
    echo "Ahora ejecuta el sistema completo:"
    echo -e "${YELLOW}  ./run_test.sh${NC}"
    echo
    echo "Y prueba: ${YELLOW}para la música${NC}"
else
    echo -e "  ${RED}❌ No funcionó${NC}"
    echo
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo -e "${RED}  DIAGNÓSTICO DEL PROBLEMA${NC}"
    echo -e "${RED}═══════════════════════════════════════${NC}"
    echo

    # Test 7: Probar con diferentes teclas
    echo -e "${YELLOW}Test 7: Probando teclas alternativas${NC}"
    echo

    echo "  Probando con ESPACIO..."
    echo "  Presiona Enter..."
    read
    osascript -e "
    tell application \"$RUNNING_BROWSER\" to activate
    delay 1.0
    tell application \"System Events\"
        keystroke \" \"
    end tell
    "

    echo -e "${YELLOW}¿Funcionó con ESPACIO? (s/n)${NC}"
    read space_worked

    if [ "$space_worked" = "s" ]; then
        echo -e "  ${GREEN}✅ ESPACIO funciona${NC}"
        echo
        echo "  SOLUCIÓN: Cambiar a usar ESPACIO en lugar de K"
        echo "  Edita utils/media_detector.py y cambia:"
        echo "    keystroke \"k\" → keystroke \" \""
    else
        echo -e "  ${RED}❌ ESPACIO tampoco funciona${NC}"
        echo

        # Test con key code
        echo "  Probando con key code 49 (espacio)..."
        echo "  Presiona Enter..."
        read
        osascript -e "
        tell application \"$RUNNING_BROWSER\" to activate
        delay 1.0
        tell application \"System Events\"
            key code 49
        end tell
        "

        echo -e "${YELLOW}¿Funcionó con key code 49? (s/n)${NC}"
        read keycode_worked

        if [ "$keycode_worked" = "s" ]; then
            echo -e "  ${GREEN}✅ Key code 49 funciona${NC}"
            echo
            echo "  SOLUCIÓN: Cambiar a usar key code 49"
            echo "  Edita utils/media_detector.py y cambia:"
            echo "    keystroke \"k\" → key code 49"
        else
            echo -e "  ${RED}❌ Nada funciona${NC}"
            echo
            echo "  PROBLEMA POSIBLE:"
            echo "  1. El navegador no recibe las teclas"
            echo "  2. YouTube está en modo especial (pantalla completa?)"
            echo "  3. Hay algún bloqueador o extensión"
            echo
            echo "  PRUEBA MANUAL:"
            echo "  1. Con YouTube abierto, presiona 'K' en tu teclado"
            echo "  2. ¿Se pausa/reproduce?"
            echo
            echo "  Si NO funciona manualmente:"
            echo "    → El problema es YouTube o el navegador"
            echo "  Si SÍ funciona manualmente:"
            echo "    → El problema es cómo enviamos las teclas"
        fi
    fi
fi
