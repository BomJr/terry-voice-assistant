#!/bin/bash
# Terry v6.0 - Test de Micrófono (wrapper con virtualenv)

echo "🎤 Activando entorno virtual..."
source .venv/bin/activate

echo ""
python3 test_mic_levels.py
