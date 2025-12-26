#!/bin/bash
# Home-Alexa - Script de Ejecución

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar entorno virtual
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Entorno virtual no encontrado${NC}"
    echo "Ejecuta primero: ./install.sh"
    exit 1
fi

# Activar entorno virtual
source .venv/bin/activate

# Verificar que Ollama esté corriendo
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}Error: Ollama no está corriendo${NC}"
    echo "Inicia Ollama en otra terminal con: ollama serve"
    exit 1
fi

# Ejecutar
echo -e "${GREEN}Iniciando Home-Alexa...${NC}"
python3 main.py

# Guardar código de salida
EXIT_CODE=$?

# Desactivar entorno virtual
deactivate

exit $EXIT_CODE
