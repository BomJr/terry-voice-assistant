#!/bin/bash
# Terry - Asistente de Voz Ultra-Rápido v6.0

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                                                ║${NC}"
echo -e "${BLUE}║              TERRY - VOICE AI                 ║${NC}"
echo -e "${BLUE}║        Asistente Ultra-Rápido v6.0            ║${NC}"
echo -e "${BLUE}║                                                ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}"
echo

# Verificar sistema primero
source .venv/bin/activate
python3 scripts/diagnostics/check_system.py
if [ $? -ne 0 ]; then
    echo
    echo -e "${YELLOW}⚠️  Corrige los requisitos faltantes${NC}"
    exit 1
fi

echo
echo -e "${CYAN}⚡ NUEVAS FUNCIONES v6.0:${NC}"
echo "  ✅ LED visual de estado (escuchando/procesando/respondiendo)"
echo "  ✅ Conversación continua (8s sin wake word después de respuesta)"
echo "  ✅ Gestos de voz rápidos (ok, mmm, siguiente, cancela)"
echo "  ✅ Rutinas por voz (modo trabajo, buenas noches, etc.)"
echo "  ✅ Detección automática español/inglés"
echo "  ✅ Feedback inmediato mientras procesa"
echo

echo -e "${YELLOW}¿Qué modo quieres usar?${NC}"
echo "  1) Modo continuo (escucha siempre) - ⚡ ULTRA-RÁPIDO"
echo "  2) Modo wake word (di 'terry' o 'hey mac')"
echo
read -p "Selecciona (1/2) [1]: " mode
mode=${mode:-1}

echo
echo -e "${YELLOW}¿Estilo de respuestas de voz?${NC}"
echo "  1) Estilo Alexa - Rápido ('Reproduciendo') - ⚡ RECOMENDADO"
echo "  2) Completo - Informativo ('Reproduciendo música')"
echo
read -p "Selecciona (1/2) [1]: " response_style
response_style=${response_style:-1}

# Determinar argumentos
WAKE_WORD_ARG=""
RESPONSE_ARG=""

if [ "$mode" = "2" ]; then
    WAKE_WORD_ARG="--wake-word"
fi

if [ "$response_style" = "2" ]; then
    RESPONSE_ARG="--full-responses"
fi

echo
if [ "$mode" = "2" ]; then
    echo -e "${CYAN}🔒 Modo Wake Word activado${NC}"
    echo "Instrucciones:"
    echo "  1. Opción A - Todo de una vez (recomendado):"
    echo "     'terry pon música' o 'hey mac qué hora es'"
    echo "  2. Opción B - En dos pasos:"
    echo "     Paso 1: 'terry' → Espera beep"
    echo "     Paso 2: 'pon música'"
    echo "  3. Presiona Ctrl+C para salir"
else
    echo -e "${CYAN}⚡ Modo Continuo ULTRA-RÁPIDO activado${NC}"
    echo "Instrucciones:"
    echo "  1. Espera '🎤 Habla ahora'"
    echo "  2. Di tu comando"
    echo "  3. Respuesta instantánea (tipo Alexa)"
    echo "  4. Presiona Ctrl+C para salir"
fi

if [ "$response_style" = "1" ]; then
    echo "  ⚡ Respuestas rápidas estilo Alexa"
else
    echo "  🗣️  Respuestas completas"
fi

echo
read -p "Presiona ENTER para comenzar..."
python3 -m terry.core.voice.pipeline $WAKE_WORD_ARG $RESPONSE_ARG
