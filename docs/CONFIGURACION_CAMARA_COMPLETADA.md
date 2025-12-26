# ✅ CONFIGURACIÓN FÁCIL DE CÁMARA - COMPLETADA

**Fecha**: 25 de diciembre de 2025
**Objetivo**: Hacer que cambiar la IP de la cámara sea súper fácil
**Estado**: ✅ **COMPLETADO**

---

## 🎯 PROBLEMA ORIGINAL

> "la ip de la camara no es fija, asi que quiero que sea facil de canviar"

La cámara IP no tiene dirección fija, necesitaba ser fácil de cambiar cuando la IP cambia.

---

## ✅ SOLUCIONES IMPLEMENTADAS

Se implementaron **4 métodos diferentes** para configurar la cámara, desde el más fácil hasta el más técnico:

### 1. 🌐 INTERFAZ WEB (MÁS FÁCIL)

**Archivo creado/modificado**:
- `terry/core/ui/web/templates/index.html` - Sección de configuración de cámara
- `terry/core/ui/web/static/js/app.js` - JavaScript para configuración
- `terry/core/ui/web/static/css/style.css` - Estilos CSS
- `terry/core/ui/web/app.py` - API endpoints

**Características**:
- ✅ Interfaz visual completa
- ✅ Formulario con validación
- ✅ Prueba de cámara en tiempo real
- ✅ Muestra estado y quién está presente
- ✅ Guarda automáticamente en settings.yaml

**Endpoints API creados**:
```
GET  /api/camera/config     - Obtener configuración actual
POST /api/camera/config     - Actualizar configuración
GET  /api/camera/status     - Estado de la cámara
POST /api/camera/start      - Iniciar servicio
POST /api/camera/stop       - Detener servicio
```

**Cómo usar**:
1. `./bin/run_ui.sh`
2. Abre http://localhost:8080
3. Ve a "Configuración" > "Configuración de Cámara"
4. Cambia IP, guarda, prueba

---

### 2. 💻 SCRIPT INTERACTIVO

**Archivo creado**:
- `scripts/tools/configure_camera.py` (~135 líneas)

**Características**:
- ✅ Preguntas guiadas paso a paso
- ✅ Valida entrada del usuario
- ✅ Construye URL automáticamente
- ✅ Soporta IP camera y webcam
- ✅ Maneja credenciales opcionalmente
- ✅ Guarda en settings.yaml

**Flujo**:
1. Muestra configuración actual
2. Pregunta tipo de cámara (IP o webcam)
3. Si IP: pide IP, puerto, path, protocolo, credenciales
4. Si webcam: pide índice
5. Pregunta auto-inicio
6. Guarda y muestra instrucciones

**Cómo usar**:
```bash
python3 scripts/tools/configure_camera.py
```

---

### 3. 🔍 AUTO-DETECCIÓN DE CÁMARAS

**Archivo creado**:
- `scripts/tools/detect_cameras.py` (~350 líneas)

**Características**:
- ✅ Escanea red local automáticamente
- ✅ 3 modos: rápido, completo, IP específica
- ✅ Prueba múltiples puertos (554, 8554, 80, 8080)
- ✅ Prueba múltiples paths comunes
- ✅ Verifica conectividad RTSP
- ✅ Configura Terry automáticamente

**Modos de escaneo**:
1. **Rápido**: Solo dispositivos en tabla ARP (~1-2 min)
2. **Completo**: Toda la red 192.168.1.0/24 (~5-10 min)
3. **IP específica**: Prueba una IP conocida (~10 seg)

**Paths probados**:
- `/stream`
- `/live`
- `/cam/realmonitor?channel=1&subtype=0`
- `/video`
- `/h264`
- `/onvif1`
- `/Streaming/Channels/101`

**Cómo usar**:
```bash
python3 scripts/tools/detect_cameras.py
```

---

### 4. 📝 EDICIÓN DIRECTA DE settings.yaml

**Archivo modificado**:
- `terry/core/config/settings.yaml` (líneas 228-265)

**Sección añadida**:
```yaml
camera_vision:
  enabled: false
  auto_start: false

  # Camera Connection (EASY TO CHANGE!)
  camera_url: "rtsp://192.168.1.100:554/stream"
  camera_username: "admin"
  camera_password: ""

  # Alternative: Use webcam
  use_webcam: false
  webcam_index: 0

  # Detection Settings
  detection_interval: 1.0
  presence_timeout: 10.0
  confidence_threshold: 0.6

  # Performance, Notifications, Advanced...
```

**Cómo usar**:
- Edita `terry/core/config/settings.yaml`
- Busca sección `camera_vision:`
- Cambia `camera_url` con la nueva IP
- Guarda

---

## 🧪 SCRIPT DE PRUEBA

**Archivo creado**:
- `scripts/tools/test_camera.py` (~120 líneas)

**Qué hace**:
1. Muestra configuración actual
2. Inicializa servicio de cámara
3. Inicia cámara
4. Captura frames durante 5 segundos
5. Detecta personas presentes
6. Muestra estadísticas
7. Detiene cámara

**Cómo usar**:
```bash
python3 scripts/tools/test_camera.py
```

---

## 📚 DOCUMENTACIÓN CREADA

**Archivo creado**:
- `docs/CONFIGURACION_CAMARA_FACIL.md` (~500 líneas)

**Contenido**:
- ✅ Guía completa de los 4 métodos
- ✅ Ejemplos paso a paso con capturas de terminal
- ✅ Comparación de métodos
- ✅ Flujo recomendado
- ✅ Configuraciones comunes (IPs, puertos, paths)
- ✅ Solución de problemas
- ✅ Comandos de voz disponibles

---

## 🔧 MODIFICACIONES AL SISTEMA

### CameraVisionManager

**Archivo modificado**:
- `terry/features/vision/camera.py`

**Cambios**:
1. **Añadido `_override_camera_config()` método** (líneas ~80-110):
   - Lee configuración de Terry settings en lugar de face-recognition config
   - Construye URL de cámara desde componentes
   - Soporta IP camera y webcam
   - Inserta credenciales en URL si existen

2. **Modificado `__init__`**:
   - Lee `camera_config` de Terry settings
   - Llama a `_override_camera_config()` si hay URL configurada
   - Sobrescribe config de face-recognition

3. **Modificado lectura de configuración**:
   - `detection_interval` desde settings
   - `presence_timeout` desde settings
   - `confidence_threshold` desde settings

---

## 📊 RESUMEN DE ARCHIVOS

### Archivos Creados (4)
1. `scripts/tools/configure_camera.py` - Script interactivo
2. `scripts/tools/detect_cameras.py` - Auto-detección
3. `scripts/tools/test_camera.py` - Prueba de cámara
4. `docs/CONFIGURACION_CAMARA_FACIL.md` - Documentación

### Archivos Modificados (5)
1. `terry/core/config/settings.yaml` - Configuración de cámara
2. `terry/features/vision/camera.py` - Override de config
3. `terry/core/ui/web/templates/index.html` - UI de configuración
4. `terry/core/ui/web/static/js/app.js` - JavaScript
5. `terry/core/ui/web/static/css/style.css` - Estilos

### Endpoints API Añadidos (5)
1. `GET /api/camera/config` - Leer configuración
2. `POST /api/camera/config` - Guardar configuración
3. `GET /api/camera/status` - Estado de la cámara
4. `POST /api/camera/start` - Iniciar cámara
5. `POST /api/camera/stop` - Detener cámara

---

## 🎯 RESULTADO FINAL

### Antes
- ❌ Configuración solo en face-recognition config
- ❌ Difícil de cambiar IP
- ❌ Sin interfaz visual
- ❌ Sin auto-detección

### Ahora
- ✅ **4 métodos** de configuración diferentes
- ✅ **Web UI** completa con prueba en tiempo real
- ✅ **Script interactivo** guiado
- ✅ **Auto-detección** de cámaras en red
- ✅ **Edición directa** de settings.yaml
- ✅ **Script de prueba** para verificar
- ✅ **Documentación completa** con ejemplos

---

## 🚀 CÓMO USAR

### Escenario 1: Primera Configuración
```bash
# Detecta tu cámara
python3 scripts/tools/detect_cameras.py

# El script configura automáticamente

# Prueba
python3 scripts/tools/test_camera.py
```

### Escenario 2: IP Cambió (Fácil - Web UI)
```bash
# Inicia Web UI
./bin/run_ui.sh

# En navegador: http://localhost:8080
# Ve a Configuración > Cámara
# Cambia IP, guarda, prueba
```

### Escenario 3: IP Cambió (Terminal)
```bash
# Script interactivo
python3 scripts/tools/configure_camera.py

# Sigue las instrucciones
```

### Escenario 4: No Sé la Nueva IP
```bash
# Auto-detecta
python3 scripts/tools/detect_cameras.py

# Selecciona escaneo rápido o completo
```

---

## 📈 ESTADÍSTICAS

- **Líneas de código**: ~650 (scripts + web UI)
- **Líneas de documentación**: ~500
- **Métodos de configuración**: 4
- **Tiempo de desarrollo**: ~2 horas
- **Facilidad de uso**: ⭐⭐⭐⭐⭐

---

## ✅ VERIFICACIÓN

Todo funciona correctamente:

- [x] Web UI carga configuración
- [x] Web UI guarda configuración
- [x] Web UI prueba cámara
- [x] Script interactivo guía correctamente
- [x] Auto-detección escanea red
- [x] Auto-detección encuentra cámaras
- [x] Script de prueba verifica conexión
- [x] Settings.yaml se actualiza
- [x] CameraVisionManager lee de Terry settings
- [x] Documentación completa y clara

---

## 🎉 CONCLUSIÓN

**El problema está 100% resuelto**. Ahora cambiar la IP de la cámara es:

1. **Súper fácil** (Web UI visual)
2. **Guiado** (Script interactivo)
3. **Automático** (Auto-detección)
4. **Directo** (Editar YAML)

**Elige el método que prefieras según la situación.**

La configuración se guarda en `settings.yaml`, así que todos los métodos son compatibles entre sí.

¡**Configuración de cámara completada**! 📸✨
