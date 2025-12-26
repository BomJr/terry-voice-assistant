#!/bin/bash
# Prueba completa del sistema de cámara de Terry v6.1

cd "$(dirname "$0")/.."

echo "🎬 INICIANDO PRUEBA COMPLETA DEL SISTEMA DE CÁMARA..."
echo ""

python3 scripts/tools/test_camera_complete.py
