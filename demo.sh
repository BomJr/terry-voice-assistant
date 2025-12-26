#!/bin/bash
# Demo Completo de Home-Alexa

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${GREEN}╔═══════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   HOME-ALEXA - DEMOSTRACIÓN COMPLETA  ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════╝${NC}"
echo

echo -e "${BLUE}🔍 VERIFICANDO SISTEMA...${NC}"
echo

# Verificar Ollama
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama no está corriendo${NC}"
    echo "Inicia Ollama: ollama serve"
    exit 1
fi
echo "✅ Ollama: Corriendo"

# Verificar venv
if [ ! -d ".venv" ]; then
    echo "❌ Entorno virtual no encontrado"
    echo "Ejecuta: ./install.sh"
    exit 1
fi
echo "✅ Python venv: OK"

echo
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo -e "${GREEN}  TODAS LAS ACCIONES DISPONIBLES${NC}"
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo
echo "🖥️  SISTEMA"
echo "   • abre Safari / Chrome / Calculator / Music"
echo "   • sube el volumen / baja el volumen"
echo "   • silencia"
echo
echo "🌐 NAVEGADOR"
echo "   • busca Python en Google"
echo "   • abre youtube.com"
echo "   • abre una nueva pestaña"
echo
echo "🎵 MULTIMEDIA (~200 variaciones de comandos)"
echo "   REPRODUCIR: pon/reproduce/continúa/reanuda/sigue/dale/despausa música/video"
echo "   PAUSAR: para/pausa/detén/frena/apaga/corta/stop música/video"
echo "   SIGUIENTE: siguiente/next/skip/salta canción/video"
echo "   ANTERIOR: anterior/atrás/vuelve/retrocede canción/video"
echo "   Ejemplos: 'para el video', 'despausa', 'skip', 'apaga la música'"
echo
echo "⏰ UTILIDADES"
echo "   • pon un temporizador de 5 minutos"
echo "   • crea una alarma a las 7"
echo
echo "💬 CONVERSACIÓN"
echo "   • hola"
echo "   • ¿qué puedes hacer?"
echo
echo -e "${GREEN}═══════════════════════════════════════${NC}"
echo
echo -e "${YELLOW}OPCIONES:${NC}"
echo "  [1] Probar TODAS las acciones (test automático)"
echo "  [2] Modo interactivo (tú escribes comandos)"
echo "  [3] Ver documentación completa"
echo "  [4] Salir"
echo
read -p "Selecciona opción [1-4]: " option

case $option in
    1)
        echo
        echo -e "${GREEN}Ejecutando tests automáticos...${NC}"
        echo
        source .venv/bin/activate
        python3 test_actions.py
        ;;
    2)
        echo
        echo -e "${GREEN}Modo interactivo iniciado...${NC}"
        echo
        ./run_test.sh
        ;;
    3)
        echo
        cat CAPACIDADES.md | less
        ;;
    4)
        echo "¡Hasta luego!"
        exit 0
        ;;
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac
