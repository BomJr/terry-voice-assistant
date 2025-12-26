#!/bin/bash
# Terry v6.1 - Instalación de todas las 20 mejoras
# Instala dependencias necesarias para las nuevas funcionalidades

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║        TERRY v6.1 - INSTALACIÓN COMPLETA      ║${NC}"
echo -e "${GREEN}║          20 Mejoras Sustanciales               ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo

# Activar entorno virtual
source .venv/bin/activate

echo -e "${YELLOW}📦 Instalando dependencias v6.1...${NC}"
echo

# FASE 1-2: Inteligencia y Quick Wins
echo "  🧠 Memoria y Aprendizaje..."
pip install -q chromadb sentence-transformers 2>/dev/null

# FASE 3: Multimodalidad
echo "  👁️  Visión y OCR..."
pip install -q pillow pytesseract opencv-python 2>/dev/null
pip install -q pync 2>/dev/null  # Notificaciones macOS

# FASE 4: Automatización
echo "  ⚙️  Automatización..."
pip install -q apscheduler watchdog 2>/dev/null

# FASE 5: Productividad
echo "  💼 Productividad..."
pip install -q pyautogui pynput 2>/dev/null

# FASE 7: Integración
echo "  🔌 API y Plugins..."
pip install -q fastapi uvicorn[standard] pydantic 2>/dev/null
pip install -q importlib-metadata 2>/dev/null

echo
echo -e "${GREEN}✅ Dependencias instaladas${NC}"
echo
echo -e "${YELLOW}🍺 Dependencias de sistema (Homebrew)...${NC}"

# OCR
if ! command -v tesseract &> /dev/null; then
    echo "  📝 Instalando Tesseract OCR..."
    brew install tesseract 2>/dev/null
fi

echo
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}║           ✅ INSTALACIÓN COMPLETADA            ║${NC}"
echo -e "${GREEN}║                                                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo
echo -e "${YELLOW}📋 Próximos pasos:${NC}"
echo "  1. Ejecuta: ./run_voice_ux.sh"
echo "  2. Prueba: 'terry modo silencioso'"
echo "  3. Lee: TERRY_V6.1_ROADMAP.md para ver todas las mejoras"
echo
echo -e "${GREEN}🚀 Terry v6.1 está listo!${NC}"
echo
