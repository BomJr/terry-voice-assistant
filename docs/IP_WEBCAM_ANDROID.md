# 📱 USAR TU ANDROID COMO CÁMARA CON IP WEBCAM

**Terry v6.1 - Guía para IP Webcam (Android)**

---

## 🎯 QUÉ ES IP WEBCAM

**IP Webcam** es una app de Android que convierte tu móvil en una cámara IP accesible por WiFi.

- ✅ Gratis (con versión Pro opcional)
- ✅ Streaming en tiempo real
- ✅ Funciona por WiFi
- ✅ Múltiples formatos de video

---

## 📲 CONFIGURACIÓN EN ANDROID

### 1. Instalar IP Webcam

1. Abre **Google Play Store**
2. Busca: **"IP Webcam"** (por Pavel Khlebovich)
3. Instala la app

### 2. Configurar la App

1. **Abre IP Webcam**

2. **Configuración básica** (opcional pero recomendado):
   - Menú ≡ → **Configuración de vídeo**
     - Resolución: `640x480` o `800x600` (mejor rendimiento)
     - Calidad: `50-70%` (balance calidad/velocidad)
     - FPS: `15-20` (suficiente para reconocimiento facial)

   - Menú ≡ → **Configuración de conexión**
     - Puerto: `8080` (por defecto, está bien)
     - Autenticación: Configura usuario/contraseña si quieres (opcional)

   - Menú ≡ → **Configuración de alimentación**
     - ☑️ **Mantener pantalla encendida** (IMPORTANTE)
     - ☑️ **Wake Lock** (evita que se duerma)

3. **Iniciar el servidor**:
   - Botón grande **"Iniciar servidor"** en la pantalla principal
   - Verás una URL como: `http://192.168.1.42:8080`
   - **Anota esta IP y puerto**

4. **Posicionar el móvil**:
   - Colócalo donde pueda ver tu cara
   - Usa un soporte o apóyalo contra algo
   - Asegúrate de que la cámara trasera (o delantera) apunte hacia ti

---

## 💻 CONFIGURACIÓN EN TERRY

### Método 1: Script Automático (RECOMENDADO)

```bash
cd /Users/bruno/Home-Alexa

python3 scripts/tools/configure_ip_webcam.py
```

**El script va a**:
1. Pedirte la IP del móvil (ej: `192.168.1.42`)
2. Pedirte el puerto (ej: `8080`)
3. **Probar automáticamente** las URLs de IP Webcam
4. Guardar la configuración en Terry
5. ¡Listo!

**Ejemplo de sesión**:
```
╔════════════════════════════════════════════════════════╗
║        CONFIGURACIÓN IP WEBCAM - TERRY v6.1           ║
╚════════════════════════════════════════════════════════╝

📱 IP Webcam es una app de Android que convierte tu móvil en cámara IP

IP del móvil [192.168.1.42]: 192.168.1.42
Puerto [8080]: 8080

Usuario (Enter para omitir):

════════════════════════════════════════════════════════
🧪 PROBANDO CONEXIONES...
════════════════════════════════════════════════════════

📹 Video feed principal
🔍 Probando: http://192.168.1.42:8080/video
✅ Conexión exitosa!
   Content-Type: multipart/x-mixed-replace

📹 Video feed alternativo
🔍 Probando: http://192.168.1.42:8080/videofeed
✅ Conexión exitosa!
   Content-Type: text/html

════════════════════════════════════════════════════════
✅ CONEXIÓN EXITOSA
════════════════════════════════════════════════════════

URL que funciona: http://192.168.1.42:8080/video

¿Guardar esta configuración en Terry? (s/n): s

✅ Configuración guardada en settings.yaml
```

### Método 2: Manual (Editar settings.yaml)

Abre: `terry/core/config/settings.yaml`

Busca la sección `camera_vision:` y configura:

```yaml
camera_vision:
  enabled: true
  auto_start: false

  # URL de IP Webcam
  camera_url: "http://192.168.1.42:8080/video"  # ← Cambia la IP
  camera_username: ""  # Déjalo vacío si no configuraste autenticación
  camera_password: ""

  use_webcam: false  # IP Webcam usa URL, no índice de webcam

  detection_interval: 1.0
  presence_timeout: 10.0
  confidence_threshold: 0.6
```

**Guarda el archivo.**

---

## 🧪 PROBAR QUE FUNCIONA

### 1. Probar desde Navegador (Verificación Rápida)

Abre en Chrome/Safari: `http://192.168.1.42:8080`

Deberías ver:
- Interfaz de IP Webcam
- Video en vivo
- Controles

Si no se ve, hay un problema de red (revisa la sección de problemas abajo).

### 2. Probar con Terry

```bash
cd /Users/bruno/Home-Alexa

python3 scripts/tools/test_camera.py
```

Verás:
```
✅ Cámara iniciada correctamente
⏳ Capturando frames (5 segundos)...
✅ Detectadas 1 persona(s):
   - Bruno
```

---

## 🎤 USAR CON COMANDOS DE VOZ

```bash
./bin/run_voice.sh
```

Di:
```
"Terry, activa la cámara"
"Terry, quién está aquí"
"Terry, está Bruno aquí"
"Terry, estado de la cámara"
```

---

## 🔧 URLS DE IP WEBCAM

IP Webcam expone varios endpoints:

```bash
# Video stream (MJPEG) - Para reconocimiento facial
http://192.168.1.42:8080/video

# Video feed alternativo
http://192.168.1.42:8080/videofeed

# Captura de imagen estática
http://192.168.1.42:8080/shot.jpg

# Página principal (interfaz web)
http://192.168.1.42:8080

# Con autenticación
http://usuario:password@192.168.1.42:8080/video
```

**Terry usa**: `/video` (el stream MJPEG principal)

---

## ⚙️ CONFIGURACIÓN RECOMENDADA EN LA APP

Para mejor rendimiento:

### Video
- **Resolución**: 640x480 o 800x600
- **Calidad**: 50-70%
- **FPS**: 15-20
- **Orientación**: Landscape o Portrait (según cómo lo coloques)

### Conexión
- **Puerto**: 8080 (o el que prefieras)
- **Autenticación**: Opcional (usuario/contraseña)

### Alimentación
- ☑️ **Mantener pantalla encendida** ← IMPORTANTE
- ☑️ **Wake Lock** ← IMPORTANTE
- ☑️ **Prevenir suspensión** ← IMPORTANTE

### Rendimiento
- **Usar cámara trasera** (mejor calidad) o delantera (selfie)
- **Modo nocturno**: ON si vas a usarla de noche

---

## ❌ SOLUCIÓN DE PROBLEMAS

### "No se puede conectar"

**Causa**: No están en la misma red WiFi

**Solución**:
1. Verifica que tu Mac y Android estén en la **misma WiFi**
2. Verifica la IP en la app (puede haber cambiado)
3. Prueba hacer ping:
   ```bash
   ping 192.168.1.42
   ```

### "Timeout al conectar"

**Causa**: Firewall o puerto bloqueado

**Solución**:
1. Desactiva temporalmente el firewall del móvil
2. Verifica que IP Webcam esté ejecutándose
3. Reinicia la app

### "Se ve pero no detecta personas"

**Causa**: Face recognition no configurado

**Solución**:
1. Verifica que face-recognition esté instalado:
   ```bash
   cd /Users/bruno/face-recognition
   pip install -r requirements.txt
   ```

2. Agrega tu cara al sistema:
   ```bash
   cd /Users/bruno/face-recognition
   # Sigue las instrucciones para agregar personas
   ```

### "La conexión se cae"

**Causa**: El móvil se duerme o cambia de IP

**Solución**:
1. En la app: **Configuración de alimentación**
   - ☑️ Mantener pantalla encendida
   - ☑️ Wake Lock
   - ☑️ Prevenir suspensión

2. Conecta el móvil al cargador

3. Configura IP estática en tu router para el móvil

### "Video muy lento"

**Causa**: Resolución o FPS muy altos

**Solución**:
1. Reduce resolución a 640x480
2. Reduce FPS a 15
3. Reduce calidad a 50%

---

## 💡 CONSEJOS

### Rendimiento
- **Resolución baja** (640x480) es suficiente para reconocimiento facial
- **FPS bajo** (15-20) ahorra batería y ancho de banda
- **Conecta el móvil al cargador** para uso prolongado

### Posicionamiento
- Coloca el móvil a **altura de los ojos** o un poco más alto
- Apunta la cámara hacia donde sueles estar
- Asegúrate de tener **buena iluminación**

### Red
- Usa **WiFi de 5GHz** si está disponible (menos latencia)
- Si la IP cambia mucho, configura **IP estática** en el router
- Mantén el móvil cerca del router para mejor señal

### Batería
- Conecta el móvil a un **cargador** para uso 24/7
- Reduce el **brillo de pantalla** al mínimo
- Cierra otras apps en segundo plano

---

## 🔄 CAMBIAR LA IP

Si la IP del móvil cambia:

### Opción A: Script de configuración
```bash
python3 scripts/tools/configure_ip_webcam.py
```

### Opción B: Web UI
1. `./bin/run_ui.sh`
2. http://localhost:8080
3. Configuración > Cámara
4. Cambia la URL
5. Guarda y prueba

### Opción C: Editar settings.yaml
```yaml
camera_url: "http://NUEVA_IP:8080/video"
```

---

## 📊 COMPARACIÓN: IP WEBCAM vs WEBCAM USB vs CÁMARA IP

| Característica | IP Webcam (Android) | Webcam USB | Cámara IP |
|----------------|---------------------|------------|-----------|
| **Costo** | Gratis (móvil que ya tienes) | $20-100 | $50-300 |
| **Instalación** | App + WiFi | USB directo | Red WiFi |
| **Portabilidad** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ |
| **Calidad** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Facilidad** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**IP Webcam es perfecto para**: Pruebas, desarrollo, uso temporal, portabilidad

---

## 🎯 RESUMEN RÁPIDO

1. **Instala IP Webcam** en Android (Google Play)
2. **Inicia el servidor** en la app
3. **Ejecuta**: `python3 scripts/tools/configure_ip_webcam.py`
4. **Prueba**: `python3 scripts/tools/test_camera.py`
5. **Usa**: `./bin/run_voice.sh` → "Terry, activa la cámara"

¡Y listo! Tu Android ahora es la cámara de Terry 📱✨

---

## 📚 MÁS INFORMACIÓN

- App oficial: https://play.google.com/store/apps/details?id=com.pas.webcam
- Documentación Terry: `docs/CONFIGURACION_CAMARA_FACIL.md`
- Guía técnica: `docs/CONFIGURACION_CAMARA_COMPLETADA.md`
