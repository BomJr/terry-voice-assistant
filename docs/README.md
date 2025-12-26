# Home-Alexa

Asistente de voz personal offline para Mac Mini M4, optimizado para Apple Silicon.

## Características

- **Wake Word**: Activa con "hey mac"
- **100% Offline**: Funciona completamente sin internet
- **Speech-to-Text**: MLX Whisper optimizado para Apple Silicon
- **Text-to-Speech**: Piper TTS para voz natural
- **LLM Local**: Ollama con LLaMA 3.1
- **Memoria Persistente**: Contexto entre conversaciones
- **Sistema de Acciones**: Control completo del sistema
- **Confirmación de Voz**: Para acciones críticas

## Requisitos

- **Hardware**: Mac Mini M4 (o cualquier Mac con Apple Silicon)
- **Sistema**: macOS 12.0 o superior
- **Python**: 3.10 o superior
- **Micrófono**: Razer BlackShark V2 X o cualquier otro
- **Ollama**: Instalado y corriendo

## Instalación

### 1. Clonar/Descargar el proyecto

```bash
cd ~/Home-Alexa
```

### 2. Instalar Ollama

```bash
# Descargar desde https://ollama.ai
# O con Homebrew:
brew install ollama

# Iniciar Ollama
ollama serve &

# Descargar modelo
ollama pull llama3.1
```

### 3. Ejecutar instalación

```bash
./install.sh
```

Esto instalará todas las dependencias Python y configurará el entorno.

### 4. (Opcional) Descargar voces Piper

Las voces de alta calidad para Piper deben descargarse por separado:

```bash
# Español
cd config/voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/davefx/medium/es_ES-davefx-medium.onnx.json

# Inglés
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
```

## Uso

### Ejecución Manual

```bash
./run.sh
```

### Instalación como Servicio (Inicio Automático)

```bash
./install_service.sh
```

El asistente se iniciará automáticamente al encender el Mac.

### Comandos de Ejemplo

- **"Hey mac, abre Safari"** - Abre navegador
- **"Hey mac, sube el volumen"** - Control de audio
- **"Hey mac, busca el clima en Google"** - Búsqueda web
- **"Hey mac, pon música"** - Control multimedia
- **"Hey mac, crea una alarma a las 7"** - Alarmas y recordatorios

## Configuración

Edita `config/settings.yaml` para personalizar:

- Wake word phrase
- Volumen y velocidad de voz
- Idioma por defecto
- Nivel de confirmación para acciones
- Modelos de LLM
- Y más...

## Acciones Disponibles

### Sistema
- Abrir/cerrar aplicaciones
- Control de volumen
- Búsqueda de archivos

### Navegador
- Abrir URLs
- Búsquedas web
- Gestión de pestañas

### Multimedia
- Play/Pause
- Siguiente/Anterior
- Saltar anuncios de YouTube

### Terminal
- Ejecutar comandos (con confirmación)

### Utilidades
- Alarmas y temporizadores
- Recordatorios

## Estructura del Proyecto

```
Home-Alexa/
├── main.py                 # Punto de entrada principal
├── config.py              # Gestión de configuración
├── requirements.txt       # Dependencias Python
│
├── config/               # Archivos de configuración
│   ├── settings.yaml
│   ├── voices/          # Modelos de voz Piper
│   └── wakewords/       # Modelos wake word
│
├── core/                # Componentes core
│   ├── audio_manager.py
│   ├── state_machine.py
│   └── event_bus.py
│
├── wakeword/           # Detección wake word
├── stt/                # Speech-to-Text
├── tts/                # Text-to-Speech
├── llm/                # LLM y procesamiento
├── memory/             # Memoria persistente
├── actions/            # Sistema de acciones
├── utils/              # Utilidades
│
├── logs/              # Logs del sistema
└── data/              # Base de datos
```

## Logs y Debugging

Ver logs en tiempo real:

```bash
tail -f logs/home_alexa.log
```

Para servicios del sistema:

```bash
tail -f logs/service.log
tail -f logs/service_error.log
```

## Gestión del Servicio

```bash
# Ver estado
launchctl list | grep homealexa

# Detener
launchctl unload ~/Library/LaunchAgents/com.homealexa.assistant.plist

# Iniciar
launchctl load ~/Library/LaunchAgents/com.homealexa.assistant.plist

# Desinstalar
./uninstall_service.sh
```

## Solución de Problemas

### Ollama no conecta

```bash
# Verificar que esté corriendo
curl http://localhost:11434/api/tags

# Si no responde, iniciar:
ollama serve
```

### No detecta el micrófono

Verificar permisos en:
`Preferencias del Sistema > Seguridad y Privacidad > Privacidad > Micrófono`

### Error al cargar MLX Whisper

Asegúrate de tener instaladas las herramientas de línea de comandos de Xcode:

```bash
xcode-select --install
```

### Voces de TTS no funcionan

Si Piper falla, el sistema usa automáticamente el comando `say` de macOS como fallback.

## Extensión

### Agregar Nueva Acción

1. Crear archivo en `actions/{categoria}/nueva_accion.py`
2. Heredar de `ActionBase`
3. Implementar `execute()`
4. Registrar en `actions/__init__.py`

### Cambiar Modelo LLM

Edita `config/settings.yaml`:

```yaml
llm:
  ollama:
    model: "llama3.2:latest"  # O cualquier otro modelo
```

## Licencia

Proyecto personal. Uso libre.

## Créditos

- MLX Whisper (Apple)
- Piper TTS
- Ollama
- OpenWakeWord
