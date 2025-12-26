# 📸 CONFIGURACIÓN DE CÁMARA - GUÍA COMPLETA

**Terry v6.1 - Sistema de Reconocimiento Facial**

---

## 🎯 PROBLEMA RESUELTO

Tu cámara IP no tiene una dirección IP fija, por lo que necesitas poder **cambiar la configuración fácilmente** cuando la IP cambia.

## ✅ SOLUCIONES IMPLEMENTADAS

Ahora tienes **4 formas diferentes** de configurar la cámara, desde la más fácil hasta la más técnica:

---

## 📋 MÉTODO 1: INTERFAZ WEB (MÁS FÁCIL)

### Ventajas
- ✅ Interfaz gráfica visual
- ✅ Sin necesidad de editar archivos
- ✅ Prueba de cámara en tiempo real
- ✅ Ver quién está presente

### Cómo Usar

1. **Inicia la Web UI**:
```bash
./bin/run_ui.sh
```

2. **Abre tu navegador**:
```
http://localhost:8080
```

3. **Ve a la pestaña "Configuración"** (icono de engranaje)

4. **Desplázate hasta "Configuración de Cámara"**

5. **Configura tu cámara**:
   - **Tipo de Cámara**: Selecciona "Cámara IP (RTSP)" o "Webcam Local"

   **Para Cámara IP**:
   - URL: `rtsp://192.168.1.100:554/stream` (cambia la IP)
   - Usuario: `admin` (si tu cámara requiere autenticación)
   - Contraseña: tu contraseña

   **Para Webcam**:
   - Índice: `0` (primera webcam), `1` (segunda), etc.

6. **Opciones adicionales**:
   - ☑️ **Habilitar Cámara**: Activar el sistema de cámara
   - ☑️ **Auto-inicio**: Iniciar cámara automáticamente con Terry

7. **Haz clic en "Guardar Configuración"**

8. **Prueba la cámara**: Haz clic en "Probar Cámara"
   - Verás el estado de la cámara
   - Quién está presente
   - Estadísticas de detección

---

## 🔧 MÉTODO 2: SCRIPT INTERACTIVO (FÁCIL)

### Ventajas
- ✅ Guiado paso a paso
- ✅ Desde la terminal
- ✅ Construye la URL automáticamente
- ✅ Valida la configuración

### Cómo Usar

```bash
python3 scripts/tools/configure_camera.py
```

**El script te preguntará**:
1. ¿Cámara IP o webcam?
2. IP de la cámara (ej: `192.168.1.100`)
3. Puerto (por defecto: `554`)
4. Path del stream (por defecto: `/stream`)
5. Protocolo (por defecto: `rtsp`)
6. Usuario y contraseña (si son necesarios)
7. ¿Auto-iniciar con Terry?

**Ejemplo de sesión**:
```
╔════════════════════════════════════════════════════════╗
║     CONFIGURACIÓN DE CÁMARA - TERRY v6.1              ║
╚════════════════════════════════════════════════════════╝

Configuración actual:
  URL: rtsp://192.168.1.50:554/stream
  Usuario: admin

¿Qué tipo de cámara quieres usar?
  1) Cámara IP (RTSP)
  2) Webcam local (USB o integrada)

Selecciona (1/2): 1

Configuración de cámara IP:

IP de la cámara (ej: 192.168.1.100):
IP: 192.168.1.200

Puerto (ej: 554) [554]:

Path del stream (/stream):

Protocolo (rtsp/http) [rtsp]:

Credenciales (déjalas vacías si no se requieren):
Usuario: admin
Contraseña: ••••••••

✅ Cámara IP configurada:
   URL: rtsp://admin:****@192.168.1.200:554/stream

¿Iniciar cámara automáticamente con Terry? (s/n) [n]: s

╔════════════════════════════════════════════════════════╗
║           ✅ CONFIGURACIÓN GUARDADA                    ║
╚════════════════════════════════════════════════════════╝
```

---

## 🔍 MÉTODO 3: AUTO-DETECCIÓN DE CÁMARAS (INTELIGENTE)

### Ventajas
- ✅ Encuentra cámaras automáticamente
- ✅ Escanea la red local
- ✅ Prueba múltiples puertos y rutas
- ✅ Identifica cámaras funcionales

### Cómo Usar

```bash
python3 scripts/tools/detect_cameras.py
```

**Opciones de escaneo**:

1. **Escaneo rápido** (recomendado):
   - Busca solo en dispositivos activos (tabla ARP)
   - Más rápido (~1-2 minutos)

2. **Escaneo completo**:
   - Escanea toda la red (192.168.1.1-254)
   - Más lento (~5-10 minutos)
   - Encuentra todas las cámaras

3. **IP específica**:
   - Prueba solo una IP conocida
   - Muy rápido (~10 segundos)
   - Útil si conoces la IP aproximada

**Ejemplo de salida**:
```
╔════════════════════════════════════════════════════════╗
║     DETECCIÓN DE CÁMARAS IP - TERRY v6.1              ║
╚════════════════════════════════════════════════════════╝

📡 Tu IP local: 192.168.1.50
📡 Red local: 192.168.1.0/24

¿Cómo quieres buscar cámaras?
  1) Escaneo rápido (solo dispositivos activos en ARP)
  2) Escaneo completo (toda la red, más lento)
  3) Escanear IP específica

Selecciona (1/2/3): 1

🔍 Escaneo rápido de dispositivos activos...
   Encontrados 15 dispositivos en tabla ARP

🔍 Probando 15 dispositivos...

  🔍 Puerto 554 abierto en 192.168.1.100
    Probando: rtsp://192.168.1.100:554/stream
    ✅ Funciona!

  🔍 Puerto 554 abierto en 192.168.1.101
    Probando: rtsp://192.168.1.101:554/live
    ✅ Funciona!

════════════════════════════════════════════════════════
✅ Se encontraron 2 cámara(s):

1. rtsp://192.168.1.100:554/stream
   IP: 192.168.1.100, Puerto: 554, Path: /stream

2. rtsp://192.168.1.101:554/live
   IP: 192.168.1.101, Puerto: 554, Path: /live

¿Configurar Terry con alguna cámara? (1-2/n): 1

✅ Configuración guardada

Para probar la cámara:
  1. Inicia Terry: ./bin/run_voice.sh
  2. Di: 'Terry, activa la cámara'
  3. Di: 'Terry, quién está aquí'
════════════════════════════════════════════════════════
```

---

## 📝 MÉTODO 4: EDITAR settings.yaml (DIRECTO)

### Ventajas
- ✅ Control total
- ✅ Configuración avanzada
- ✅ Cambios rápidos si conoces la IP
- ✅ Todas las opciones disponibles

### Cómo Usar

**Archivo**: `terry/core/config/settings.yaml`

**Busca la sección** `camera_vision:` (línea ~228):

```yaml
# ============================================
# Camera Vision System - Terry v6.1
# ============================================

camera_vision:
  enabled: false                    # ← Cambia a true para habilitar
  auto_start: false                 # ← true para iniciar con Terry

  # Camera Connection (EASY TO CHANGE!)
  camera_url: "rtsp://192.168.1.100:554/stream"  # ← CAMBIA AQUÍ LA IP
  camera_username: "admin"          # ← Usuario de la cámara
  camera_password: ""               # ← Contraseña

  # Alternative: Use webcam instead of IP camera
  use_webcam: false                 # ← true para usar webcam
  webcam_index: 0                   # ← 0 = primera, 1 = segunda, etc.

  # Detection Settings
  detection_interval: 1.0           # Segundos entre detecciones
  presence_timeout: 10.0            # Segundos para considerar "ausente"
  confidence_threshold: 0.6         # 0-1, confianza mínima

  # Performance
  max_faces_per_frame: 5
  skip_frames: 0                    # 0 = procesar todos los frames

  # Notifications
  notify_on_detection: true
  notify_on_unknown: true
```

**Ejemplo de cambio de IP**:
```yaml
# ANTES
camera_url: "rtsp://192.168.1.100:554/stream"

# DESPUÉS (nueva IP)
camera_url: "rtsp://192.168.1.200:554/stream"
```

**Con credenciales**:
```yaml
camera_url: "rtsp://admin:mipassword@192.168.1.100:554/stream"
camera_username: "admin"
camera_password: "mipassword"
```

**Para webcam**:
```yaml
use_webcam: true
webcam_index: 0  # 0 = primera webcam
```

---

## 🧪 PROBAR LA CONFIGURACIÓN

### Método 1: Script de Test

```bash
python3 scripts/tools/test_camera.py
```

**Qué hace**:
- ✅ Verifica la configuración
- ✅ Intenta conectar a la cámara
- ✅ Captura frames durante 5 segundos
- ✅ Detecta personas presentes
- ✅ Muestra estadísticas

**Ejemplo de salida**:
```
╔════════════════════════════════════════════════════════╗
║     TEST DE CÁMARA - TERRY v6.1                       ║
╚════════════════════════════════════════════════════════╝

📋 Configuración actual:
   Habilitada: True
   Auto-inicio: False
   Tipo: Cámara IP
   URL: rtsp://192.168.1.100:554/stream

🔧 Inicializando servicio de cámara...
✅ Servicio inicializado

🎥 Iniciando cámara...
✅ Cámara iniciada correctamente

⏳ Capturando frames (5 segundos)...

👤 Verificando presencia...
✅ Detectadas 1 persona(s):
   - Bruno

📊 Estadísticas:
   Total detecciones: 12
   Personas únicas: 1
   Desconocidos: 0

🛑 Deteniendo cámara...
✅ Cámara detenida
```

### Método 2: Web UI

1. Ve a http://localhost:8080
2. Pestaña "Configuración"
3. Sección "Configuración de Cámara"
4. Haz clic en "Probar Cámara"

### Método 3: Comandos de Voz

```bash
./bin/run_voice.sh

# Di:
"Terry, activa la cámara"
"Terry, quién está aquí"
"Terry, estado de la cámara"
"Terry, estadísticas de la cámara"
```

---

## 📊 COMPARACIÓN DE MÉTODOS

| Método | Facilidad | Velocidad | Características |
|--------|-----------|-----------|-----------------|
| **Web UI** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Visual, prueba en vivo, estado en tiempo real |
| **Script Interactivo** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Guiado, valida entrada, terminal |
| **Auto-Detección** | ⭐⭐⭐ | ⭐⭐⭐ | Encuentra cámaras, escanea red |
| **Editar YAML** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Control total, más técnico |

---

## 🚀 FLUJO RECOMENDADO

### Primera Vez
1. **Detecta tu cámara**: `python3 scripts/tools/detect_cameras.py`
2. **Configura automáticamente** cuando el script te pregunte
3. **Prueba**: `python3 scripts/tools/test_camera.py`

### Cuando la IP Cambia
**Opción A - Más Fácil**: Web UI
1. Abre http://localhost:8080
2. Ve a Configuración > Cámara
3. Cambia la URL
4. Guarda y prueba

**Opción B - Más Rápido**: Script Interactivo
```bash
python3 scripts/tools/configure_camera.py
```

**Opción C - Si No Conoces la Nueva IP**: Auto-Detección
```bash
python3 scripts/tools/detect_cameras.py
```

---

## 🔧 CONFIGURACIONES COMUNES

### Cámara IP con Autenticación
```yaml
camera_url: "rtsp://admin:password123@192.168.1.100:554/stream"
camera_username: "admin"
camera_password: "password123"
```

### Cámara IP sin Autenticación
```yaml
camera_url: "rtsp://192.168.1.100:554/stream"
camera_username: ""
camera_password: ""
```

### Webcam Integrada (Mac)
```yaml
use_webcam: true
webcam_index: 0
```

### Webcam USB Externa
```yaml
use_webcam: true
webcam_index: 1  # o 2, 3, etc.
```

### Diferentes Puertos
```yaml
# Puerto 8554
camera_url: "rtsp://192.168.1.100:8554/stream"

# Puerto 88 (algunas cámaras chinas)
camera_url: "rtsp://192.168.1.100:88/stream"
```

### Diferentes Paths de Stream
```yaml
# Reolink
camera_url: "rtsp://192.168.1.100:554/live"

# Hikvision
camera_url: "rtsp://192.168.1.100:554/Streaming/Channels/101"

# Dahua
camera_url: "rtsp://192.168.1.100:554/cam/realmonitor?channel=1&subtype=0"

# Generic
camera_url: "rtsp://192.168.1.100:554/video"
camera_url: "rtsp://192.168.1.100:554/h264"
```

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### "No se pudo iniciar la cámara"

**Causa**: URL incorrecta o cámara no accesible

**Solución**:
1. Verifica que la cámara esté encendida
2. Verifica la IP con: `python3 scripts/tools/detect_cameras.py`
3. Prueba hacer ping: `ping 192.168.1.100`
4. Verifica el puerto: `nc -zv 192.168.1.100 554`

### "Error de autenticación"

**Causa**: Usuario o contraseña incorrectos

**Solución**:
1. Verifica las credenciales de la cámara
2. Prueba sin credenciales primero
3. Asegúrate de que la URL incluye las credenciales correctamente

### "No detecta a nadie"

**Causa**: Sistema de reconocimiento facial no configurado

**Solución**:
1. Verifica que face-recognition esté instalado:
```bash
cd /Users/bruno/face-recognition
pip install -r requirements.txt
```

2. Agrega personas conocidas:
```bash
cd /Users/bruno/face-recognition
python3 -m tools.add_person --name "Bruno" --images path/to/images/
```

3. Verifica el threshold de confianza en settings.yaml:
```yaml
confidence_threshold: 0.6  # Baja a 0.4 si no detecta
```

### "Cámara muy lenta"

**Solución**: Ajusta estos parámetros en settings.yaml:
```yaml
detection_interval: 2.0      # Aumenta a 2-3 segundos
skip_frames: 2               # Procesa solo cada 3 frames
max_faces_per_frame: 3       # Reduce a 3
```

---

## 📚 COMANDOS DE VOZ DISPONIBLES

Una vez configurada la cámara:

```bash
# Iniciar/Detener
"Terry, activa la cámara"
"Terry, inicia la cámara"
"Terry, desactiva la cámara"
"Terry, apaga la cámara"

# Consultar Presencia
"Terry, quién está aquí"
"Terry, hay alguien aquí"
"Terry, está Bruno aquí"
"Terry, está María presente"

# Estado
"Terry, estado de la cámara"
"Terry, estadísticas de la cámara"
```

---

## 🎯 RESUMEN

**Tienes 4 formas de configurar la cámara cuando la IP cambia:**

1. **🌐 Web UI** - Visual y fácil (RECOMENDADO)
2. **💻 Script Interactivo** - Guiado paso a paso
3. **🔍 Auto-Detección** - Encuentra cámaras automáticamente
4. **📝 Editar YAML** - Control total

**Todas guardan en el mismo archivo** (`settings.yaml`), así que puedes usar cualquiera.

**¡La configuración es ahora súper fácil de cambiar!** 🎉
