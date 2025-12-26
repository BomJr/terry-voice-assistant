#!/bin/bash
# Home-Alexa - Instalación de Componentes de Voz

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   HOME-ALEXA - INSTALACIÓN DE VOZ             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo

# Activar entorno virtual
source .venv/bin/activate

echo -e "${YELLOW}Instalando dependencias de voz...${NC}"
echo

# Instalar PyAudio para captura de audio
echo "📦 Instalando PyAudio (captura de audio)..."
pip install pyaudio

# Instalar SpeechRecognition para STT
echo "📦 Instalando SpeechRecognition..."
pip install SpeechRecognition

# Instalar pyttsx3 para TTS (más simple que Piper)
echo "📦 Instalando pyttsx3 (Text-to-Speech)..."
pip install pyttsx3

# Instalar openwakeword para wake word
echo "📦 Instalando openwakeword..."
pip install openwakeword

# Instalar numpy y scipy (dependencias)
echo "📦 Instalando dependencias adicionales..."
pip install numpy scipy

# Opcional: Whisper de OpenAI (más preciso pero requiere más recursos)
echo
read -p "¿Instalar Whisper de OpenAI? (más preciso pero usa más recursos) [s/N]: " install_whisper
if [[ $install_whisper =~ ^[Ss]$ ]]; then
    echo "📦 Instalando OpenAI Whisper..."
    pip install openai-whisper
fi

echo
echo -e "${GREEN}✅ Instalación completada!${NC}"
echo
echo "Componentes instalados:"
echo "  ✅ PyAudio - Captura de audio del micrófono"
echo "  ✅ SpeechRecognition - Speech-to-Text"
echo "  ✅ pyttsx3 - Text-to-Speech"
echo "  ✅ openwakeword - Wake word detection"

echo
echo "Próximo paso:"
echo "  ./run_voice.sh  - Iniciar Home-Alexa con voz"
echo
