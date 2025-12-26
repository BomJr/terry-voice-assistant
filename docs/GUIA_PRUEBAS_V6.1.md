# Guía de Pruebas - Terry v6.1
## 20 Mejoras Sustanciales Implementadas ✅

---

## 🚀 Inicio Rápido

### 1. Instalar Dependencias
```bash
# Instalar todas las dependencias v6.1
./install_v6_1.sh

# Verificar instalación
./test_v6_1.sh
```

### 2. Iniciar Terry
```bash
# Modo wake word (recomendado)
./run_voice.sh

# O modo continuo
python3 -m voice.voice_pipeline
```

---

## 📋 Pruebas por Fase

### ✅ FASE 1: QUICK WINS

#### #17 Modo Silencioso
```
terry modo silencioso          # Activar (solo notificaciones)
terry modo normal              # Desactivar
```
**Resultado esperado**: Notificaciones macOS sin voz

#### #6 Notificaciones Visuales
```
terry qué hora es              # Cualquier comando
```
**Resultado esperado**: Notificación macOS aparece + voz

#### #12 Notas por Voz
```
terry nota: comprar leche
terry nota: reunión mañana a las 10
terry busca mis notas sobre leche
terry mis pendientes
terry lista mis notas
```
**Resultado esperado**: Notas guardadas en `~/.terry/notes/notes.db`

#### #16 Sistema de Deshacer
```
terry sube volumen
terry deshaz eso               # Restaura volumen anterior
terry pon música
terry vuelve atrás             # Pausa música
```
**Resultado esperado**: Última acción revertida

---

### ✅ FASE 2: INTELIGENCIA

#### #1 Memoria Persistente
```
terry pon música
terry (5 minutos después) qué canción puse hace rato?
```
**Resultado esperado**: Todas las interacciones en `data/memory.db`

#### #2 Aprendizaje de Patrones
```
# Ejecutar el mismo comando varias veces a la misma hora
terry pon música               # Lunes 9 AM
terry pon música               # Martes 9 AM
terry pon música               # Miércoles 9 AM
# El patrón se guarda en ~/.terry/memory/patterns.json
```
**Resultado esperado**: Patrones detectados por hora/día

#### #3 Contexto Implícito
```
terry abre VS Code
terry cierra eso               # "eso" = VS Code
terry pon música de trabajo
terry siguiente                # Siguiente canción (contexto)
```
**Resultado esperado**: Pronombres resueltos correctamente

#### #4 Sugerencias Inteligentes
```
# Sugerencias aparecen automáticamente basadas en:
# - Hora del día (9 AM = "modo trabajo")
# - Patrones aprendidos
# - Contexto actual
```
**Resultado esperado**: Log muestra sugerencias generadas

---

### ✅ FASE 3: MULTIMODALIDAD

#### #5 Visión por Cámara
```
terry captura la pantalla
```
**Resultado esperado**: Screenshot en `/tmp/terry_screenshot_*.png`

**Nota**: Reconocimiento facial requiere proyecto face-recognition
```yaml
# En config/settings.yaml
camera_vision:
  enabled: true  # Cambiar a true si tienes face-recognition
```

#### #7 OCR Universal
```
terry lee la pantalla          # Lee texto visible
terry copia el texto           # Lee + copia al portapapeles
```
**Resultado esperado**: Texto extraído de pantalla

**Requisito**: Tesseract instalado
```bash
brew install tesseract
```

---

### ✅ FASE 4: AUTOMATIZACIÓN

#### #8 Rutinas Programadas
```
terry lista rutinas
```
**Crear rutina manualmente** en `~/.terry/scheduler/routines.json`:
```json
{
  "routine_20231225_090000": {
    "name": "Buenos días",
    "command": "pon música de trabajo",
    "schedule": "09:00",
    "enabled": true
  }
}
```

#### #9 Triggers Condicionales
```
terry lista triggers
```
**Crear trigger** vía API o manualmente en `~/.terry/triggers/triggers.json`

**Ejemplo programático**:
```python
from triggers.conditional_engine import get_conditional_engine
engine = get_conditional_engine()
await engine.add_trigger(
    name="Música al abrir VS Code",
    condition_type="app_open",
    condition_params={"app_name": "Code"},
    action_command="pon música de trabajo"
)
```

#### #10 Grabación de Macros
```
terry graba macro setup trabajo
terry abre VS Code
terry pon música
terry sube volumen
terry detén grabación

# Luego ejecutar:
terry ejecuta macro setup trabajo
terry lista macros
```
**Resultado esperado**: Macro guardado en `~/.terry/macros/`

---

### ✅ FASE 5: PRODUCTIVIDAD

#### #11 Dictado Universal
```
# Abre cualquier editor de texto primero (TextEdit, Notes, etc.)
terry escribe Hola mundo
terry nueva línea
terry escribe Segunda línea
terry nuevo párrafo
```
**Resultado esperado**: Texto escrito en app activa

#### #13 Búsqueda de Archivos
```
terry busca archivo test.py
terry busca archivos que contengan TODO
```
**Resultado esperado**: Archivos encontrados vía Spotlight

#### #14 Control de IDE
```
# Requiere VS Code abierto
terry ejecuta tests
terry git status
terry git commit trabajo completado
terry git push
```
**Resultado esperado**: Comandos ejecutados en VS Code

**Requisito**: VS Code CLI instalado
```bash
# En VS Code: Cmd+Shift+P > "Shell Command: Install 'code' command in PATH"
```

---

### ✅ FASE 6: EXPERIENCIA

#### #15 Interrumpir Terry (Barge-in)
```
terry (empieza a hablar algo largo)
para                           # Interrumpe mientras habla
```
**Resultado esperado**: Terry se detiene inmediatamente

**Configuración**:
```yaml
barge_in:
  enabled: true
  interrupt_keywords: ["cancela", "para", "stop", "cancel"]
```

#### #18 Detección de Frustración
```yaml
# En config/settings.yaml
frustration_detection:
  enabled: true  # Cambiar a true para habilitar
```

```
# Comandos repetidos o fallidos activan detección
terry abre archivo inexistente
terry abre archivo inexistente
terry abre archivo inexistente
# Log mostrará: "Frustration detected: ..."
```

---

### ✅ FASE 7: INTEGRACIÓN

#### #19 Sistema de Plugins
**Crear plugin** en `~/.terry/plugins/ejemplo.py`:
```python
class Plugin:
    def __init__(self):
        self.name = "ejemplo"
        self.version = "1.0.0"

    def initialize(self):
        print("Plugin ejemplo cargado")

    def execute(self, command, params):
        return f"Ejecutando: {command}"

    def cleanup(self):
        pass
```

**Resultado esperado**: Plugin cargado al iniciar Terry

#### #20 API REST
```yaml
# En config/settings.yaml
rest_api:
  enabled: true  # Cambiar a true para habilitar
  host: "127.0.0.1"
  port: 8765
```

**Probar API**:
```bash
# Desde otra terminal
curl http://localhost:8765/

# Ejecutar comando
curl -X POST http://localhost:8765/command \
  -H "Content-Type: application/json" \
  -d '{"command": "qué hora es"}'

# Health check
curl http://localhost:8765/health

# Toggle silent mode
curl -X POST http://localhost:8765/silent-mode
```

---

## 🔧 Configuración Recomendada

### Para Desarrollo/Testing
```yaml
# En config/settings.yaml
visual_notifications:
  enabled: true

voice_notes:
  enabled: true

undo_system:
  enabled: true

persistent_memory:
  enabled: true

pattern_learning:
  enabled: true

context_tracking:
  enabled: true

intelligent_suggestions:
  enabled: true

camera_vision:
  enabled: false  # Solo si tienes face-recognition

ocr:
  enabled: true

scheduler:
  enabled: true

triggers:
  enabled: true

macros:
  enabled: true

dictation:
  enabled: true

file_search:
  enabled: true

ide_control:
  enabled: true

barge_in:
  enabled: true

frustration_detection:
  enabled: false  # Opt-in

plugins:
  enabled: true

rest_api:
  enabled: false  # Opt-in por seguridad
```

---

## 📊 Verificar Estado

### Ver Logs en Tiempo Real
```bash
tail -f logs/terry.log
```

### Verificar Base de Datos de Memoria
```bash
sqlite3 data/memory.db "SELECT COUNT(*) FROM interactions;"
```

### Verificar Notas
```bash
sqlite3 ~/.terry/notes/notes.db "SELECT * FROM notes;"
```

### Verificar Patrones Aprendidos
```bash
cat ~/.terry/memory/patterns.json | jq
```

### Verificar Macros
```bash
ls -la ~/.terry/macros/
```

---

## 🐛 Troubleshooting

### Problema: Notificaciones no aparecen
```bash
# Verificar pync instalado
pip install pync

# Verificar permisos en macOS
# System Preferences > Notifications > Terminal
```

### Problema: OCR no funciona
```bash
# Instalar Tesseract
brew install tesseract

# Verificar instalación
tesseract --version
```

### Problema: VS Code CLI no encontrado
```bash
# En VS Code: Cmd+Shift+P
# Buscar: "Shell Command: Install 'code' command in PATH"
```

### Problema: ChromaDB error
**Nota**: ChromaDB es opcional. Si no está disponible, Terry usa SQLite para búsqueda de texto.

```bash
# Ver logs - debería mostrar "Falling back to SQLite full-text search"
tail -f logs/terry.log | grep ChromaDB

# ChromaDB funciona pero es opcional:
# - Con ChromaDB: búsqueda semántica inteligente
# - Sin ChromaDB: búsqueda de texto simple (LIKE)
# Ambos métodos funcionan correctamente

# Si quieres intentar arreglar ChromaDB (opcional):
pip install pydantic-settings
pip install --upgrade chromadb sentence-transformers
```

### Problema: API no inicia
```bash
# Verificar puerto no está en uso
lsof -i :8765

# Cambiar puerto en settings.yaml si está ocupado
```

---

## 📈 Métricas de Éxito

Después de probar, deberías ver:

- ✅ **Archivos creados**:
  - `data/memory.db` - Interacciones
  - `~/.terry/notes/notes.db` - Notas
  - `~/.terry/memory/patterns.json` - Patrones
  - `~/.terry/action_history.json` - Historial de deshacer
  - `~/.terry/macros/*.json` - Macros

- ✅ **Logs muestran**:
  - "✅ Persistent Memory initialized"
  - "✅ Pattern Learning initialized"
  - "✅ Context Tracking initialized"
  - "✅ Intelligent Suggestions initialized"
  - "✅ Macro Recorder initialized"
  - etc.

- ✅ **Comandos funcionan**:
  - Respuestas rápidas (<1s)
  - Notificaciones aparecen
  - Notas se guardan y buscan
  - Macros se graban y ejecutan

---

## 🎯 Comandos Completos de Prueba

### Script de Prueba Completo
```bash
#!/bin/bash
# Prueba sistemática de las 20 mejoras

echo "=== FASE 1: QUICK WINS ==="
# (Decir con wake word "terry" antes de cada comando)

# #17 Silent Mode
echo "terry modo silencioso"
sleep 2
echo "terry qué hora es"  # Debe mostrar notificación sin voz
sleep 2
echo "terry modo normal"

# #6 Visual Notifications
echo "terry pon música"  # Debe mostrar notificación

# #12 Voice Notes
echo "terry nota: test de notas"
sleep 1
echo "terry busca mis notas sobre test"

# #16 Undo
echo "terry sube volumen"
sleep 1
echo "terry deshaz eso"

echo "=== FASE 2: INTELIGENCIA ==="

# Los patrones y sugerencias se prueban con uso continuado

echo "=== FASE 3: MULTIMODALIDAD ==="

echo "terry captura la pantalla"
echo "terry lee la pantalla"

echo "=== FASE 4: AUTOMATIZACIÓN ==="

echo "terry graba macro test"
sleep 1
echo "terry abre calculadora"
sleep 1
echo "terry detén grabación"
sleep 1
echo "terry ejecuta macro test"

echo "=== FASE 5: PRODUCTIVIDAD ==="

echo "terry busca archivo .py"
echo "terry ejecuta tests"

echo "=== Todas las pruebas completadas ==="
```

---

## 🚀 Próximos Pasos

1. **Prueba básica**: Ejecuta `./test_v6_1.sh` para verificar instalación
2. **Inicia Terry**: `./run_voice.sh`
3. **Prueba cada fase**: Sigue los comandos de esta guía
4. **Revisa logs**: `tail -f logs/terry.log` para debugging
5. **Personaliza**: Ajusta `config/settings.yaml` según necesites

---

**¡Terry v6.1 con 20 mejoras está listo para usar! 🎉**
