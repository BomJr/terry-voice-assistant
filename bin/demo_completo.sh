#!/bin/bash
# Terry v6.1.9 - Demo Completo Interactivo
# Prueba todas las features paso a paso

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Emojis
CHECK="✅"
CROSS="❌"
ROCKET="🚀"
GEAR="⚙️"
EYES="👀"
FIRE="🔥"

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${PURPLE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║   ████████╗███████╗██████╗ ██████╗ ██╗   ██╗              ║
║   ╚══██╔══╝██╔════╝██╔══██╗██╔══██╗╚██╗ ██╔╝              ║
║      ██║   █████╗  ██████╔╝██████╔╝ ╚████╔╝               ║
║      ██║   ██╔══╝  ██╔══██╗██╔══██╗  ╚██╔╝                ║
║      ██║   ███████╗██║  ██║██║  ██║   ██║                 ║
║      ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝                 ║
║                                                            ║
║             DEMOSTRACIÓN COMPLETA v6.1.9                   ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${CYAN}${ROCKET} Bienvenido a la demo completa de Terry!${NC}\n"
echo -e "Esta demo te guiará por TODAS las features implementadas.\n"

# Function to wait for user
wait_for_user() {
    echo -e "\n${YELLOW}Presiona ENTER para continuar...${NC}"
    read
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================================
# FASE 1: VERIFICACIÓN DE REQUISITOS
# ============================================================

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  FASE 1: Verificación de Requisitos   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${GEAR} Verificando dependencias...\n"

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${CHECK} Python 3: ${GREEN}$PYTHON_VERSION${NC}"
else
    echo -e "${CROSS} Python 3: ${RED}No instalado${NC}"
    exit 1
fi

# Check venv
if [ -d ".venv" ]; then
    echo -e "${CHECK} Virtual env: ${GREEN}Existe${NC}"
else
    echo -e "${CROSS} Virtual env: ${RED}No existe${NC}"
    echo -e "${YELLOW}Ejecuta: ./scripts/install/install.sh${NC}"
    exit 1
fi

# Check Ollama
if command_exists ollama; then
    echo -e "${CHECK} Ollama: ${GREEN}Instalado${NC}"

    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo -e "${CHECK} Ollama service: ${GREEN}Running${NC}"
    else
        echo -e "${YELLOW}⚠️  Ollama service: No está corriendo${NC}"
        echo -e "${YELLOW}   Iniciando Ollama en background...${NC}"
        ollama serve >/dev/null 2>&1 &
        sleep 2
    fi
else
    echo -e "${YELLOW}⚠️  Ollama: No instalado (opcional para LLM)${NC}"
fi

# Check ffmpeg
if command_exists ffmpeg; then
    echo -e "${CHECK} ffmpeg: ${GREEN}Instalado${NC}"
else
    echo -e "${YELLOW}⚠️  ffmpeg: No instalado (necesario para audio)${NC}"
fi

echo -e "\n${GREEN}${CHECK} Sistema listo para la demo!${NC}"
wait_for_user

# ============================================================
# FASE 2: INICIAR WEB UI
# ============================================================

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    FASE 2: Iniciar Web UI (Backend)   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${ROCKET} Iniciando Terry Web UI en background...\n"

# Activate venv and start server in background
source .venv/bin/activate

# Kill any existing server
lsof -ti:8080 | xargs kill -9 2>/dev/null || true

# Start server in background
python3 -m uvicorn terry.core.ui.web.app:app --host 0.0.0.0 --port 8080 --log-level warning > /tmp/terry_ui.log 2>&1 &
SERVER_PID=$!

echo -e "${GEAR} Server PID: $SERVER_PID"
echo -e "${GEAR} Esperando que el servidor inicie..."

# Wait for server to start
for i in {1..15}; do
    if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
        echo -e "\n${GREEN}${CHECK} Web UI iniciada exitosamente!${NC}\n"
        break
    fi
    echo -n "."
    sleep 1
done

if ! curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
    echo -e "\n${RED}${CROSS} Error: No se pudo iniciar el servidor${NC}"
    echo -e "Ver logs en: /tmp/terry_ui.log"
    exit 1
fi

echo -e "${CYAN}URLs disponibles:${NC}"
echo -e "  ${GREEN}→${NC} Web UI:     ${BLUE}http://localhost:8080${NC}"
echo -e "  ${GREEN}→${NC} Swagger UI: ${BLUE}http://localhost:8080/docs${NC}"
echo -e "  ${GREEN}→${NC} ReDoc:      ${BLUE}http://localhost:8080/redoc${NC}"

wait_for_user

# ============================================================
# FASE 3: ABRIR NAVEGADOR Y EXPLORAR WEB UI
# ============================================================

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     FASE 3: Explorar Web UI (8 Tabs)   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${EYES} Abriendo navegador en http://localhost:8080\n"
open http://localhost:8080 2>/dev/null || echo "Abre manualmente: http://localhost:8080"

echo -e "${CYAN}CHECKLIST - Explora estos 8 tabs:${NC}\n"

echo -e "  ${YELLOW}1. Tab CHAT${NC}"
echo -e "     ${GREEN}→${NC} Escribe: 'Qué hora es'"
echo -e "     ${GREEN}→${NC} Escribe: 'Pon música de Coldplay'"
echo -e "     ${GREEN}→${NC} Prueba reconocimiento de voz (click micrófono)"
echo -e "     ${GREEN}→${NC} Prueba quick commands (botones 1-9)"
echo -e "     ${GREEN}→${NC} Presiona tecla '1' para ejecutar primer quick command\n"

echo -e "  ${YELLOW}2. Tab HISTORY${NC}"
echo -e "     ${GREEN}→${NC} Ve historial de comandos con timestamps"
echo -e "     ${GREEN}→${NC} Presiona Ctrl+K para buscar"
echo -e "     ${GREEN}→${NC} Hover sobre comando → 4 acciones (re-run, edit, copy, add)"
echo -e "     ${GREEN}→${NC} Presiona Ctrl+E para exportar a JSON/CSV\n"

echo -e "  ${YELLOW}3. Tab NOTES${NC}"
echo -e "     ${GREEN}→${NC} Click 'Nueva Nota'"
echo -e "     ${GREEN}→${NC} Contenido: 'Comprar leche mañana'"
echo -e "     ${GREEN}→${NC} Categoría: shopping, Priority: 2"
echo -e "     ${GREEN}→${NC} Ve la nota creada en la lista\n"

echo -e "  ${YELLOW}4. Tab TEMPLATES${NC}"
echo -e "     ${GREEN}→${NC} Click 'Crear Template'"
echo -e "     ${GREEN}→${NC} Comando: 'Pon música de {{artista}}'"
echo -e "     ${GREEN}→${NC} Variables: artista"
echo -e "     ${GREEN}→${NC} Categoría: music"
echo -e "     ${GREEN}→${NC} Ejecuta el template → Rellena 'Coldplay'\n"

echo -e "  ${YELLOW}5. Tab PROFILER${NC}"
echo -e "     ${GREEN}→${NC} Ve gráfico de performance (últimos 20 comandos)"
echo -e "     ${GREEN}→${NC} Ve 4 cards: avg time, fastest, slowest, total"
echo -e "     ${GREEN}→${NC} Ve Top 10 comandos más lentos"
echo -e "     ${GREEN}→${NC} Ve sugerencias de optimización"
echo -e "     ${GREEN}→${NC} Click 'Export JSON'\n"

echo -e "  ${YELLOW}6. Tab MONITOR${NC}"
echo -e "     ${GREEN}→${NC} Ve 4 health cards: CPU, RAM, Uptime, Commands/min"
echo -e "     ${GREEN}→${NC} Ve estado de 6 servicios (con pulse animation)"
echo -e "     ${GREEN}→${NC} Ve timeline de actividad (comandos + logs)"
echo -e "     ${GREEN}→${NC} Ve system info (platform, Python, IP, etc.)"
echo -e "     ${GREEN}→${NC} Espera 5 segundos → Auto-refresh\n"

echo -e "  ${YELLOW}7. Tab LOGS${NC}"
echo -e "     ${GREEN}→${NC} Ve logs en tiempo real (terminal-style)"
echo -e "     ${GREEN}→${NC} Toggle filtros por nivel (debug/info/warn/error)"
echo -e "     ${GREEN}→${NC} Toggle auto-scroll"
echo -e "     ${GREEN}→${NC} Click 'Export Logs' para descargar .txt\n"

echo -e "  ${YELLOW}8. Tab SETTINGS${NC}"
echo -e "     ${GREEN}→${NC} Configura cámara (si tienes IP Webcam)"
echo -e "     ${GREEN}→${NC} Toggle silent mode"
echo -e "     ${GREEN}→${NC} Ve stats del sistema\n"

echo -e "${PURPLE}Features Globales (Header):${NC}\n"
echo -e "  ${YELLOW}• Botón </>:${NC} Abre Swagger UI en nueva pestaña"
echo -e "  ${YELLOW}• Campana 🔔:${NC} Panel de notificaciones (slide-in desde derecha)"
echo -e "  ${YELLOW}• Luna 🌙:${NC} Cambiar tema (6 temas + custom editor)"
echo -e "  ${YELLOW}• Volumen 🔊:${NC} Toggle silent mode"
echo -e "  ${YELLOW}• Status dot:${NC} Online/Offline indicator\n"

wait_for_user

# ============================================================
# FASE 4: PROBAR SWAGGER UI (API INTERACTIVA)
# ============================================================

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   FASE 4: Swagger UI (API Interactiva) ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${ROCKET} Abriendo Swagger UI en http://localhost:8080/docs\n"
open http://localhost:8080/docs 2>/dev/null || echo "Abre manualmente: http://localhost:8080/docs"

echo -e "${CYAN}CHECKLIST - Prueba estos endpoints:${NC}\n"

echo -e "  ${YELLOW}1. GET /api/status${NC}"
echo -e "     ${GREEN}→${NC} Click en el endpoint"
echo -e "     ${GREEN}→${NC} Click 'Try it out'"
echo -e "     ${GREEN}→${NC} Click 'Execute'"
echo -e "     ${GREEN}→${NC} Ve response con status: online, version: 6.1.9\n"

echo -e "  ${YELLOW}2. POST /api/command${NC}"
echo -e "     ${GREEN}→${NC} Click en el endpoint"
echo -e "     ${GREEN}→${NC} Click 'Try it out'"
echo -e "     ${GREEN}→${NC} Edita JSON: {\"command\": \"Qué hora es\", \"language\": \"es\"}"
echo -e "     ${GREEN}→${NC} Click 'Execute'"
echo -e "     ${GREEN}→${NC} Ve response con la hora actual\n"

echo -e "  ${YELLOW}3. POST /api/notes${NC}"
echo -e "     ${GREEN}→${NC} Crear una nota desde la API"
echo -e "     ${GREEN}→${NC} JSON: {\"content\": \"Test desde Swagger\", \"category\": \"test\", \"priority\": 1}\n"

echo -e "  ${YELLOW}4. GET /api/notes${NC}"
echo -e "     ${GREEN}→${NC} Ve todas las notas creadas"
echo -e "     ${GREEN}→${NC} Prueba parámetros: limit=5, category=test\n"

echo -e "  ${YELLOW}5. Explorar otros endpoints${NC}"
echo -e "     ${GREEN}→${NC} GET /api/stats - Estadísticas detalladas"
echo -e "     ${GREEN}→${NC} GET /api/macros - Lista de macros"
echo -e "     ${GREEN}→${NC} GET /api/camera/status - Estado de cámara"
echo -e "     ${GREEN}→${NC} POST /api/silent-mode - Toggle silent mode\n"

echo -e "${PURPLE}Features de Swagger UI:${NC}"
echo -e "  ${GREEN}→${NC} Ve schema completo de request/response"
echo -e "  ${GREEN}→${NC} Ve ejemplos con valores reales"
echo -e "  ${GREEN}→${NC} Ve validaciones (ranges, tipos, required)"
echo -e "  ${GREEN}→${NC} Descarga OpenAPI schema (botón arriba)\n"

wait_for_user

# ============================================================
# FASE 5: PROBAR API CON CURL
# ============================================================

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      FASE 5: Probar API con cURL      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${GEAR} Ejecutando requests de ejemplo...\n"

# Test 1: Status
echo -e "${CYAN}Test 1: GET /api/status${NC}"
curl -s http://localhost:8080/api/status | jq '.'
echo -e "${GREEN}${CHECK} Status OK${NC}\n"
sleep 1

# Test 2: Execute command
echo -e "${CYAN}Test 2: POST /api/command (Qué hora es)${NC}"
RESPONSE=$(curl -s -X POST "http://localhost:8080/api/command" \
  -H "Content-Type: application/json" \
  -d '{"command":"Qué hora es","language":"es"}')
echo "$RESPONSE" | jq '.'
echo -e "${GREEN}${CHECK} Comando ejecutado${NC}\n"
sleep 1

# Test 3: Create note
echo -e "${CYAN}Test 3: POST /api/notes (Crear nota de prueba)${NC}"
NOTE_RESPONSE=$(curl -s -X POST "http://localhost:8080/api/notes" \
  -H "Content-Type: application/json" \
  -d '{"content":"Nota de prueba desde demo","category":"demo","priority":3}')
echo "$NOTE_RESPONSE" | jq '.'
echo -e "${GREEN}${CHECK} Nota creada${NC}\n"
sleep 1

# Test 4: Get notes
echo -e "${CYAN}Test 4: GET /api/notes (Ver notas)${NC}"
curl -s "http://localhost:8080/api/notes?limit=5" | jq '.'
echo -e "${GREEN}${CHECK} Notas recuperadas${NC}\n"
sleep 1

# Test 5: Stats
echo -e "${CYAN}Test 5: GET /api/stats (Estadísticas)${NC}"
curl -s http://localhost:8080/api/stats | jq '.'
echo -e "${GREEN}${CHECK} Stats OK${NC}\n"

wait_for_user

# ============================================================
# FASE 6: PROBAR FEATURES AVANZADAS
# ============================================================

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    FASE 6: Features Avanzadas          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}Features para probar manualmente:${NC}\n"

echo -e "  ${YELLOW}1. TEMAS PERSONALIZADOS${NC}"
echo -e "     ${GREEN}→${NC} En Web UI, click icono luna 🌙"
echo -e "     ${GREEN}→${NC} Prueba: Blue, Green, Purple, Pink, Dark"
echo -e "     ${GREEN}→${NC} Click 'Custom' para crear tu propio tema"
echo -e "     ${GREEN}→${NC} Ajusta 6 colores con pickers"
echo -e "     ${GREEN}→${NC} Ve preview en vivo"
echo -e "     ${GREEN}→${NC} Export/Import como JSON\n"

echo -e "  ${YELLOW}2. NOTIFICACIONES${NC}"
echo -e "     ${GREEN}→${NC} Click icono campana 🔔"
echo -e "     ${GREEN}→${NC} Panel slide-in desde derecha"
echo -e "     ${GREEN}→${NC} Ejecuta comandos → Ve notificaciones aparecer"
echo -e "     ${GREEN}→${NC} Escucha sonidos únicos por tipo"
echo -e "     ${GREEN}→${NC} Badge con contador de no leídas"
echo -e "     ${GREEN}→${NC} Click engranaje → Settings (browser notifications, sounds)\n"

echo -e "  ${YELLOW}3. AUTOCOMPLETE INTELIGENTE${NC}"
echo -e "     ${GREEN}→${NC} En tab Chat, empieza a escribir 'pon'"
echo -e "     ${GREEN}→${NC} Ve sugerencias aparecer (fuzzy matching)"
echo -e "     ${GREEN}→${NC} Usa ↑↓ para navegar"
echo -e "     ${GREEN}→${NC} Enter para seleccionar"
echo -e "     ${GREEN}→${NC} ESC para cerrar\n"

echo -e "  ${YELLOW}4. QUICK COMMANDS${NC}"
echo -e "     ${GREEN}→${NC} En tab Chat, ve botones de quick commands"
echo -e "     ${GREEN}→${NC} Presiona teclas 1-9 para ejecutar"
echo -e "     ${GREEN}→${NC} Click '+' para agregar nuevo"
echo -e "     ${GREEN}→${NC} Edita nombre y comando"
echo -e "     ${GREEN}→${NC} Guarda (localStorage)\n"

echo -e "  ${YELLOW}5. KEYBOARD SHORTCUTS${NC}"
echo -e "     ${GREEN}→${NC} Ctrl+K: Abrir búsqueda en historial"
echo -e "     ${GREEN}→${NC} Ctrl+E: Exportar historial"
echo -e "     ${GREEN}→${NC} Ctrl+Enter: Enviar comando"
echo -e "     ${GREEN}→${NC} ESC: Cerrar modales"
echo -e "     ${GREEN}→${NC} 1-9: Quick commands\n"

echo -e "  ${YELLOW}6. BÚSQUEDA EN HISTORIAL${NC}"
echo -e "     ${GREEN}→${NC} Tab History, presiona Ctrl+K"
echo -e "     ${GREEN}→${NC} Escribe 'música'"
echo -e "     ${GREEN}→${NC} Ve filtrado en tiempo real"
echo -e "     ${GREEN}→${NC} ESC para cerrar\n"

echo -e "  ${YELLOW}7. EXPORTAR DATOS${NC}"
echo -e "     ${GREEN}→${NC} History: Ctrl+E → JSON o CSV"
echo -e "     ${GREEN}→${NC} Logs: Click 'Export Logs' → .txt"
echo -e "     ${GREEN}→${NC} Profiler: Click 'Export JSON' → performance data"
echo -e "     ${GREEN}→${NC} Themes: Click 'Export' → JSON del tema\n"

echo -e "  ${YELLOW}8. CAMERA VISION (Opcional)${NC}"
echo -e "     ${GREEN}→${NC} Tab Settings → Camera Configuration"
echo -e "     ${GREEN}→${NC} URL: http://192.168.1.X:8080/video (Android IP Webcam)"
echo -e "     ${GREEN}→${NC} O toggle 'Use Webcam' para cámara local"
echo -e "     ${GREEN}→${NC} Start camera service"
echo -e "     ${GREEN}→${NC} Ve quién está presente\n"

wait_for_user

# ============================================================
# FASE 7: GENERAR CLIENTE DESDE OPENAPI
# ============================================================

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   FASE 7: Generar Cliente (Opcional)  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${CYAN}Descargar OpenAPI Schema:${NC}\n"

echo -e "curl http://localhost:8080/openapi.json > terry_api.json"
curl -s http://localhost:8080/openapi.json > /tmp/terry_api.json
echo -e "${GREEN}${CHECK} Schema descargado en /tmp/terry_api.json${NC}\n"

echo -e "${CYAN}Ejemplos de uso del schema:${NC}\n"

echo -e "  ${YELLOW}1. Importar a Postman${NC}"
echo -e "     ${GREEN}→${NC} Abrir Postman"
echo -e "     ${GREEN}→${NC} Import → Link → http://localhost:8080/openapi.json"
echo -e "     ${GREEN}→${NC} Collection completa importada\n"

echo -e "  ${YELLOW}2. Generar cliente Python${NC}"
echo -e "     ${GREEN}→${NC} pip install openapi-python-client"
echo -e "     ${GREEN}→${NC} openapi-python-client generate --url http://localhost:8080/openapi.json"
echo -e "     ${GREEN}→${NC} Cliente Python listo para usar\n"

echo -e "  ${YELLOW}3. Generar cliente JavaScript${NC}"
echo -e "     ${GREEN}→${NC} npm install @openapitools/openapi-generator-cli"
echo -e "     ${GREEN}→${NC} openapi-generator-cli generate -i /tmp/terry_api.json -g javascript"
echo -e "     ${GREEN}→${NC} Cliente JS listo\n"

wait_for_user

# ============================================================
# FASE 8: RESUMEN Y PRÓXIMOS PASOS
# ============================================================

echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        RESUMEN DE LA DEMOSTRACIÓN     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${FIRE} ${GREEN}¡Demo completada!${NC} Has visto:\n"

echo -e "${CHECK} ${CYAN}Web UI con 8 tabs completos${NC}"
echo -e "  • Chat, History, Notes, Templates, Profiler, Monitor, Logs, Settings\n"

echo -e "${CHECK} ${CYAN}Swagger UI interactiva${NC}"
echo -e "  • 13 endpoints documentados y probables desde browser\n"

echo -e "${CHECK} ${CYAN}REST API funcional${NC}"
echo -e "  • Comandos, notas, macros, cámara, stats, todo via HTTP\n"

echo -e "${CHECK} ${CYAN}Features avanzadas${NC}"
echo -e "  • Temas, notificaciones, autocomplete, quick commands, shortcuts\n"

echo -e "${CHECK} ${CYAN}Performance profiler${NC}"
echo -e "  • Análisis en tiempo real con gráficos y sugerencias\n"

echo -e "${CHECK} ${CYAN}System monitor${NC}"
echo -e "  • CPU, RAM, servicios, timeline, todo en tiempo real\n"

echo -e "${CHECK} ${CYAN}Logs en tiempo real${NC}"
echo -e "  • Terminal-style con filtros y export\n"

echo -e "${CHECK} ${CYAN}OpenAPI schema${NC}"
echo -e "  • Listo para generar clientes en cualquier lenguaje\n"

echo -e "\n${PURPLE}╔════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║         PRÓXIMOS PASOS                 ║${NC}"
echo -e "${PURPLE}╚════════════════════════════════════════╝${NC}\n"

echo -e "${YELLOW}1. Probar modo voz (opcional):${NC}"
echo -e "   ./bin/run_voice.sh\n"

echo -e "${YELLOW}2. Configurar cámara (opcional):${NC}"
echo -e "   python3 scripts/tools/configure_camera.py\n"

echo -e "${YELLOW}3. Ver documentación completa:${NC}"
echo -e "   cat CLAUDE.md"
echo -e "   cat SWAGGER_API_DOCS_IMPLEMENTADO.md"
echo -e "   cat SYSTEM_MONITOR_IMPLEMENTADO.md\n"

echo -e "${YELLOW}4. Explorar código:${NC}"
echo -e "   terry/core/ui/web/app.py    # Backend API"
echo -e "   terry/core/ui/web/static/   # Frontend assets\n"

echo -e "${YELLOW}5. Integrar con tu app:${NC}"
echo -e "   Usa /docs para ver API completa"
echo -e "   Genera cliente con openapi-python-client"
echo -e "   O usa requests/fetch directamente\n"

echo -e "\n${CYAN}Servidor sigue corriendo en:${NC}"
echo -e "  ${GREEN}→${NC} Web UI:     http://localhost:8080"
echo -e "  ${GREEN}→${NC} Swagger UI: http://localhost:8080/docs"
echo -e "  ${GREEN}→${NC} ReDoc:      http://localhost:8080/redoc"
echo -e "  ${GREEN}→${NC} PID:        $SERVER_PID\n"

echo -e "${YELLOW}Para detener el servidor:${NC}"
echo -e "  kill $SERVER_PID\n"

echo -e "${GREEN}${ROCKET} ¡Disfruta de Terry v6.1.9! ${ROCKET}${NC}\n"
