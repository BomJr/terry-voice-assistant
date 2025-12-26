#!/bin/bash
# Home-Alexa - Tutorial Interactivo
# Guía paso a paso para nuevos usuarios

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║     BIENVENIDO A HOME-ALEXA TUTORIAL          ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo
echo -e "${CYAN}Este tutorial te guiará paso a paso para usar Home-Alexa${NC}"
echo
read -p "Presiona ENTER para comenzar..."

# Paso 1: Verificación del Sistema
clear
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PASO 1: VERIFICACIÓN DEL SISTEMA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo
echo "Primero, vamos a verificar que tu sistema está listo."
echo
read -p "Presiona ENTER para verificar..."
echo

source .venv/bin/activate
python3 check_system.py

if [ $? -ne 0 ]; then
    echo
    echo -e "${YELLOW}⚠️  Hay requisitos faltantes. Por favor, corrígelos antes de continuar.${NC}"
    exit 1
fi

echo
read -p "Presiona ENTER para continuar..."

# Paso 2: Comandos Básicos
clear
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PASO 2: COMANDOS BÁSICOS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo
echo "Home-Alexa puede entender LENGUAJE NATURAL en español."
echo
echo "Ejemplos de comandos básicos:"
echo
echo -e "  ${GREEN}1. Saludos:${NC}"
echo "     • hola"
echo "     • buenos días"
echo "     • gracias"
echo
echo -e "  ${GREEN}2. Abrir aplicaciones:${NC}"
echo "     • abre Safari"
echo "     • abre Calculator"
echo
echo -e "  ${GREEN}3. Control de volumen:${NC}"
echo "     • sube el volumen"
echo "     • baja el volumen"
echo "     • silencia"
echo
read -p "Presiona ENTER para continuar..."

# Paso 3: Control de Música
clear
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PASO 3: CONTROL DE MÚSICA/VIDEO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo
echo "¡Home-Alexa tiene ~200 formas de controlar música!"
echo
echo -e "  ${GREEN}Reproducir (70+ formas):${NC}"
echo "     • pon música"
echo "     • reproduce el video"
echo "     • dale"
echo "     • despausa"
echo "     • continúa"
echo
echo -e "  ${GREEN}Pausar (60+ formas):${NC}"
echo "     • para la música"
echo "     • apaga el video"
echo "     • detén"
echo "     • stop"
echo
echo -e "  ${GREEN}Siguiente/Anterior:${NC}"
echo "     • siguiente / skip / salta"
echo "     • anterior / atrás / vuelve"
echo
echo -e "${CYAN}💡 Funciona con YouTube, Spotify, Music, y más!${NC}"
echo
read -p "Presiona ENTER para continuar..."

# Paso 4: Rutinas
clear
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PASO 4: RUTINAS Y MACROS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo
echo "Las rutinas ejecutan múltiples acciones con un comando."
echo
echo "Rutinas disponibles:"
echo
python3 list_routines.py
echo
read -p "Presiona ENTER para continuar..."

# Paso 5: Velocidad
clear
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PASO 5: RENDIMIENTO${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo
echo "Home-Alexa es ULTRA-RÁPIDO:"
echo
echo -e "  ${GREEN}⚡ Caché instantáneo:${NC} 0.00-0.20s"
echo "     Para comandos comunes (música, apps, etc.)"
echo
echo -e "  ${GREEN}🚀 Caché persistente:${NC} 0.01-0.05s"
echo "     Para comandos que ya usaste antes"
echo
echo -e "  ${GREEN}🤖 LLM optimizado:${NC} 1-4s"
echo "     Para comandos nuevos o complejos"
echo
echo -e "${CYAN}Más rápido que Alexa (1-4s típico)${NC}"
echo
read -p "Presiona ENTER para continuar..."

# Paso 6: Prueba Práctica
clear
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${BLUE}  PASO 6: PRUEBA PRÁCTICA${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
echo
echo "¡Ahora vamos a probarlo!"
echo
echo "Comandos sugeridos para probar:"
echo
echo "  1. hola"
echo "  2. abre Safari"
echo "  3. sube el volumen"
echo "  4. para la música (si hay algo reproduciéndose)"
echo "  5. rutina de la mañana"
echo
echo -e "${YELLOW}Consejo:${NC} Abre YouTube en un navegador antes de probar comandos de música"
echo
read -p "Presiona ENTER para iniciar el asistente..."

# Iniciar asistente
clear
python3 test_simple.py

# Final
clear
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║     ¡TUTORIAL COMPLETADO!                     ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo
echo "Has completado el tutorial de Home-Alexa."
echo
echo -e "${CYAN}Próximos pasos:${NC}"
echo
echo "  • Explora más comandos (ver COMANDOS_COMPLETOS.md)"
echo "  • Personaliza rutinas (editar config/routines.yaml)"
echo "  • Ver estadísticas (./show_cache_stats.py)"
echo "  • Ejecutar tests (python3 tests/test_all_features.py)"
echo "  • Benchmark (python3 utils/benchmark.py)"
echo
echo -e "${GREEN}Para usar Home-Alexa:${NC}"
echo "  $ ./run_test.sh"
echo
echo "¡Disfruta de tu asistente local! 🎉"
echo
