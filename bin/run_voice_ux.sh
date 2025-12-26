#!/bin/bash
# Terry v6.0.1 UX - Launcher Mejorado con Todas las Opciones

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                ║${NC}"
echo -e "${BLUE}║         TERRY - VOICE AI v6.0.1 UX            ║${NC}"
echo -e "${BLUE}║       Experiencia de Usuario Mejorada         ║${NC}"
echo -e "${BLUE}║                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo

# Verificar sistema
source .venv/bin/activate
python3 check_system.py
if [ $? -ne 0 ]; then
    echo
    echo -e "${YELLOW}⚠️  Corrige los requisitos faltantes${NC}"
    exit 1
fi

echo
echo -e "${CYAN}✨ MEJORAS UX v6.0.1:${NC}"
echo "  ✅ Beeps diferenciados por contexto (wake/processing/error)"
echo "  ✅ Confirmación audible opcional de comandos"
echo "  ✅ Retry automático si no te escucha"
echo "  ✅ Mensajes visuales más claros y útiles"
echo "  ✅ Timeout ajustable según tu ritmo"
echo

# ===== MODO =====
echo -e "${YELLOW}1. ¿Qué modo de escucha quieres?${NC}"
echo "  1) Continuo (escucha siempre) - ⚡ MÁS RÁPIDO"
echo "  2) Wake word (di 'terry' o 'hey mac') - 🔒 MÁS PRIVADO"
echo
read -p "Selecciona (1/2) [1]: " mode
mode=${mode:-1}

# ===== RESPUESTAS =====
echo
echo -e "${YELLOW}2. ¿Estilo de respuestas de voz?${NC}"
echo "  1) Alexa - Rápido ('Reproduciendo') - ⚡ RECOMENDADO"
echo "  2) Completo - Informativo ('Reproduciendo música')"
echo
read -p "Selecciona (1/2) [1]: " response_style
response_style=${response_style:-1}

# ===== CONFIRMACIÓN AUDIBLE =====
echo
echo -e "${YELLOW}3. ¿Confirmar comandos antes de ejecutar?${NC}"
echo "  1) No - Ejecutar directamente - ⚡ RÁPIDO"
echo "  2) Sí - Decir comando antes de ejecutar (ej: 'pon música')"
echo
read -p "Selecciona (1/2) [1]: " confirm
confirm=${confirm:-1}

# ===== TIMEOUT =====
if [ "$mode" = "2" ]; then
    echo
    echo -e "${YELLOW}4. ¿Cuánto tiempo esperar para wake word?${NC}"
    echo "  1) Normal (10s) - ⚡ RECOMENDADO"
    echo "  2) Más tiempo (15s) - Si hablas despacio"
    echo "  3) Rápido (5s) - Si estás cerca del micrófono"
    echo
    read -p "Selecciona (1/2/3) [1]: " timeout_choice
    timeout_choice=${timeout_choice:-1}
fi

# ===== CONSTRUIR ARGUMENTOS =====
ARGS=""

# Modo wake word
if [ "$mode" = "2" ]; then
    ARGS="$ARGS --wake-word"
fi

# Respuestas completas
if [ "$response_style" = "2" ]; then
    ARGS="$ARGS --full-responses"
fi

# Confirmación audible
if [ "$confirm" = "2" ]; then
    ARGS="$ARGS --confirm-commands"
fi

# Timeout
if [ "$mode" = "2" ]; then
    case $timeout_choice in
        2) ARGS="$ARGS --timeout 15" ;;
        3) ARGS="$ARGS --timeout 5" ;;
        *) ARGS="$ARGS --timeout 10" ;;
    esac
fi

# ===== MOSTRAR CONFIGURACIÓN =====
echo
echo -e "${CYAN}📋 CONFIGURACIÓN SELECCIONADA:${NC}"
echo "=" * 50

if [ "$mode" = "2" ]; then
    echo "  🔒 Modo: Wake Word"
    echo "     Di: 'terry pon música' (todo de una vez)"
    echo "     O: 'terry' → beep → 'pon música'"
else
    echo "  ⚡ Modo: Continuo (siempre escuchando)"
fi

if [ "$response_style" = "1" ]; then
    echo "  ⚡ Respuestas: Alexa-style (rápidas)"
else
    echo "  🗣️  Respuestas: Completas (informativas)"
fi

if [ "$confirm" = "2" ]; then
    echo "  👂 Confirmación: Activa (repite comando)"
else
    echo "  ⚡ Confirmación: Desactivada (directa)"
fi

if [ "$mode" = "2" ]; then
    case $timeout_choice in
        2) echo "  ⏱️  Timeout: 15s (más tiempo)" ;;
        3) echo "  ⏱️  Timeout: 5s (rápido)" ;;
        *) echo "  ⏱️  Timeout: 10s (normal)" ;;
    esac
fi

echo
echo -e "${CYAN}🎯 INSTRUCCIONES:${NC}"
if [ "$mode" = "2" ]; then
    echo "  1. Espera 'Esperando wake word...'"
    echo "  2. Di 'terry pon música' (todo de una vez) o en dos pasos"
    echo "  3. Escucha el beep de confirmación"
    echo "  4. Terry ejecuta tu comando"
    echo "  5. Presiona Ctrl+C para salir"
else
    echo "  1. Espera '🎤 Habla ahora'"
    echo "  2. Di tu comando directamente"
    echo "  3. Terry responde inmediatamente"
    echo "  4. Presiona Ctrl+C para salir"
fi

echo
echo -e "${GREEN}✨ Mejoras UX activas:${NC}"
echo "  🔔 Beeps diferentes para wake/processing/error"
echo "  🔁 Retry automático si no se escucha"
echo "  💡 Mensajes de ayuda en pantalla"

echo
read -p "Presiona ENTER para comenzar..."

# EJECUTAR
python3 -m voice.voice_pipeline $ARGS
