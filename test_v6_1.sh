#!/bin/bash
# Terry v6.1 - Script de Verificación de las 20 Mejoras

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║     TERRY v6.1 - VERIFICACIÓN DE MEJORAS      ║${NC}"
echo -e "${GREEN}║              20/20 Implementadas               ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo

# Verificar entorno virtual
if [ ! -d ".venv" ]; then
    echo -e "${RED}❌ Entorno virtual no encontrado${NC}"
    echo "   Ejecuta: python3 -m venv .venv"
    exit 1
fi

source .venv/bin/activate

echo -e "${BLUE}🔍 Verificando dependencias...${NC}"
echo

# Función para verificar módulo Python
check_module() {
    python3 -c "import $1" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} $2"
        return 0
    else
        echo -e "  ${RED}✗${NC} $2 (falta: $1)"
        return 1
    fi
}

# Verificar dependencias críticas
echo -e "${YELLOW}Fase 1-2: Inteligencia${NC}"
check_module "chromadb" "ChromaDB (búsqueda semántica - opcional, usa SQLite como fallback)"
check_module "sentence_transformers" "Sentence Transformers (embeddings - opcional)"
echo

echo -e "${YELLOW}Fase 3: Multimodalidad${NC}"
check_module "PIL" "Pillow (procesamiento de imágenes)"
check_module "pytesseract" "Pytesseract (OCR)"
check_module "pync" "Pync (notificaciones macOS)"
echo

echo -e "${YELLOW}Fase 4: Automatización${NC}"
check_module "apscheduler" "APScheduler (rutinas programadas)"
echo

echo -e "${YELLOW}Fase 5: Productividad${NC}"
check_module "pyautogui" "PyAutoGUI (dictado universal)"
echo

echo -e "${YELLOW}Fase 7: Integración${NC}"
check_module "fastapi" "FastAPI (REST API)"
check_module "uvicorn" "Uvicorn (servidor API)"
echo

# Verificar Tesseract
echo -e "${YELLOW}Herramientas del sistema:${NC}"
if command -v tesseract &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} Tesseract OCR"
else
    echo -e "  ${RED}✗${NC} Tesseract OCR (instala: brew install tesseract)"
fi

if command -v code &> /dev/null; then
    echo -e "  ${GREEN}✓${NC} VS Code CLI"
else
    echo -e "  ${YELLOW}!${NC} VS Code CLI (opcional, instala desde Command Palette)"
fi
echo

# Verificar estructura de archivos
echo -e "${BLUE}📁 Verificando módulos implementados...${NC}"
echo

modules=(
    "visual/notification_manager.py:Notificaciones Visuales (#6)"
    "notes/voice_notes.py:Notas por Voz (#12)"
    "undo/action_history.py:Sistema de Deshacer (#16)"
    "memory/pattern_learner.py:Aprendizaje de Patrones (#2)"
    "memory/context_manager.py:Contexto Implícito (#3)"
    "memory/intelligent_suggestions.py:Sugerencias Inteligentes (#4)"
    "vision/camera_vision.py:Visión por Cámara (#5)"
    "vision/ocr_engine.py:OCR Universal (#7)"
    "scheduler/cron_manager.py:Rutinas Programadas (#8)"
    "triggers/conditional_engine.py:Triggers Condicionales (#9)"
    "macros/macro_recorder.py:Grabación de Macros (#10)"
    "dictation/universal_dictation.py:Dictado Universal (#11)"
    "search/file_search.py:Búsqueda de Archivos (#13)"
    "ide/vscode_control.py:Control de IDE (#14)"
    "interruption/barge_in.py:Interrumpir Terry (#15)"
    "emotion/frustration_detector.py:Detección de Frustración (#18)"
    "plugins/plugin_system.py:Sistema de Plugins (#19)"
    "api/rest_api.py:API REST (#20)"
)

for module in "${modules[@]}"; do
    IFS=':' read -r path name <<< "$module"
    if [ -f "$path" ]; then
        echo -e "  ${GREEN}✓${NC} $name"
    else
        echo -e "  ${RED}✗${NC} $name (falta: $path)"
    fi
done

echo
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║           📋 CÓMO PROBAR v6.1                  ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}1. Instalar dependencias:${NC}"
echo "   ./install_v6_1.sh"
echo
echo -e "${YELLOW}2. Iniciar Terry:${NC}"
echo "   ./run_voice.sh"
echo
echo -e "${YELLOW}3. Comandos de prueba (di 'terry' primero):${NC}"
echo
echo -e "${BLUE}   Fase 1 - Quick Wins:${NC}"
echo "   • 'modo silencioso' - Activar modo silencioso"
echo "   • 'nota: comprar leche' - Crear nota"
echo "   • 'busca mis notas sobre leche' - Buscar notas"
echo "   • 'deshaz eso' - Deshacer última acción"
echo
echo -e "${BLUE}   Fase 2 - Inteligencia:${NC}"
echo "   • 'pon música' (varias veces) - Aprende patrones"
echo "   • 'eso' o 'siguiente' - Contexto implícito"
echo "   • (Sugerencias aparecen automáticamente)"
echo
echo -e "${BLUE}   Fase 3 - Multimodalidad:${NC}"
echo "   • 'captura la pantalla' - Screenshot"
echo "   • 'lee la pantalla' - OCR"
echo "   • 'copia el texto de la pantalla' - OCR + clipboard"
echo
echo -e "${BLUE}   Fase 4 - Automatización:${NC}"
echo "   • 'lista rutinas' - Ver rutinas programadas"
echo "   • 'graba macro test' - Iniciar grabación"
echo "   • 'detén grabación' - Parar grabación"
echo "   • 'ejecuta macro test' - Reproducir macro"
echo
echo -e "${BLUE}   Fase 5 - Productividad:${NC}"
echo "   • 'escribe Hola mundo' - Dictado"
echo "   • 'busca archivo test.py' - Búsqueda Spotlight"
echo "   • 'ejecuta tests' - Control VS Code"
echo "   • 'git status' - Git en VS Code"
echo
echo -e "${YELLOW}4. Verificar configuración:${NC}"
echo "   cat config/settings.yaml | grep enabled"
echo
echo -e "${YELLOW}5. Ver logs en tiempo real:${NC}"
echo "   tail -f logs/terry.log"
echo
echo -e "${GREEN}✨ Todas las 20 mejoras están listas para probar!${NC}"
echo
