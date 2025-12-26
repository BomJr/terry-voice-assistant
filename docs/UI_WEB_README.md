# Terry Web UI - Interfaz Profesional v6.1

## 🎨 Diseño Moderno y Profesional

Una interfaz web elegante con diseño **glassmorphism**, gradientes animados y actualizaciones en tiempo real vía WebSocket.

---

## ✨ Características

### 🎯 Dashboard Principal
- **Estadísticas en tiempo real**: Notas, interacciones, macros, comandos
- **Cards con glassmorphism**: Efecto de vidrio esmerilado con blur
- **Gradientes animados**: Fondos sutiles que cambian suavemente
- **Iconos profesionales**: Font Awesome 6.4.0

### 🎙️ Input de Voz Interactivo
- **Botón de voz central**: Con animaciones de pulso
- **Visualizador de ondas**: Anillos que pulsan al grabar
- **Input de texto alternativo**: Para comandos escritos
- **Estados visuales**: Idle → Recording → Processing

### 📊 Tabs Organizados
1. **Historial**: Comandos y respuestas recientes
2. **Notas**: Grid de notas con categorías y prioridades
3. **Macros**: Lista de macros guardados
4. **Configuración**: Ajustes del sistema

### 🌓 Tema Dark/Light
- **Toggle instantáneo**: Cambio suave entre temas
- **Persistencia**: Se guarda en localStorage
- **Colores optimizados**: Paleta profesional para cada tema
- **Glassmorphism adaptativo**: Ajustado para cada tema

### 📡 WebSocket Real-time
- **Conexión persistente**: Updates automáticos
- **Reconexión automática**: Si se pierde la conexión
- **Broadcast de eventos**: Todos los clientes sincronizados
- **Ping/pong keep-alive**: Mantiene conexión activa

### 🔔 Notificaciones Toast
- **Feedback visual**: Para cada acción
- **Auto-dismiss**: Desaparecen después de 3s
- **Tipos**: Success, Error, Info
- **Animaciones suaves**: Slide in/out

---

## 🚀 Cómo Usar

### 1. Iniciar la UI Web

```bash
./run_ui.sh
```

Esto:
- ✅ Verifica/instala dependencias
- ✅ Inicia el servidor FastAPI
- ✅ Abre en: http://localhost:8080

### 2. Acceder desde el Navegador

Abre tu navegador favorito:
```
http://localhost:8080
```

### 3. Explorar las Funcionalidades

#### 📝 Crear Notas
1. Click en tab "Notas"
2. Click en "Nueva Nota"
3. Escribe contenido, elige categoría y prioridad
4. Guardar

#### 🎙️ Enviar Comandos
- **Opción 1**: Click en botón de micrófono (en desarrollo)
- **Opción 2**: Escribe comando en input y presiona Enter

#### ⚙️ Configurar
1. Tab "Configuración"
2. Toggle tema dark/light
3. Activar/desactivar modo silencioso
4. Ver información del sistema

---

## 🛠️ Arquitectura Técnica

### Backend (FastAPI)
```
ui_web/
├── app.py                    # FastAPI server
├── templates/
│   └── index.html           # Main page
└── static/
    ├── css/
    │   └── style.css        # Professional styles
    └── js/
        └── app.js           # Interactive logic
```

### Endpoints API

#### GET /
- **Descripción**: Página principal
- **Retorna**: HTML

#### GET /api/status
- **Descripción**: Estado del sistema
- **Retorna**: JSON con status, version, features

#### GET /api/stats
- **Descripción**: Estadísticas detalladas
- **Retorna**: JSON con notas, macros, memoria, comandos

#### POST /api/command
- **Descripción**: Ejecutar comando
- **Body**: `{"command": "texto", "language": "es"}`
- **Retorna**: JSON con resultado

#### POST /api/silent-mode
- **Descripción**: Toggle modo silencioso
- **Retorna**: JSON con nuevo estado

#### GET /api/notes
- **Descripción**: Obtener notas
- **Query**: `?limit=10&category=work`
- **Retorna**: JSON con array de notas

#### POST /api/notes
- **Descripción**: Crear nota
- **Body**: `{"content": "...", "category": "...", "priority": 0}`
- **Retorna**: JSON con ID de nota

#### GET /api/macros
- **Descripción**: Obtener macros
- **Retorna**: JSON con array de macros

#### WebSocket /ws
- **Descripción**: Conexión en tiempo real
- **Eventos**:
  - `command_executed`
  - `silent_mode_changed`
  - `note_created`
  - `ping/pong`

---

## 🎨 Diseño Visual

### Paleta de Colores

**Light Theme**:
```css
Primary:    #6366f1 (Índigo)
Secondary:  #8b5cf6 (Púrpura)
Accent:     #ec4899 (Rosa)
Success:    #10b981 (Verde)
Warning:    #f59e0b (Amarillo)
Error:      #ef4444 (Rojo)
```

**Dark Theme**:
```css
Background: #0f172a (Azul oscuro profundo)
Cards:      rgba(30, 41, 59, 0.7) (Con blur)
Text:       #f1f5f9 (Blanco humo)
```

### Efectos Glassmorphism

```css
background: rgba(255, 255, 255, 0.25);
backdrop-filter: blur(20px);
border: 1px solid rgba(255, 255, 255, 0.3);
box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
```

### Animaciones

- **Pulse rings**: Anillos que pulsan desde el botón de voz
- **Gradient shift**: Fondo con gradiente animado
- **Fade in**: Transiciones suaves entre tabs
- **Slide in**: Modales y toasts con animación
- **Hover effects**: Scale y shadow en cards

---

## 📱 Responsive Design

La UI es completamente responsive:

- **Desktop** (>768px): Grid completo, 4 columnas
- **Tablet** (768px): Grid 2 columnas
- **Mobile** (<768px): Stack vertical, 1 columna

```css
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: 1fr;
    }
    .tabs {
        flex-direction: column;
    }
}
```

---

## 🔌 Integración con Terry

### Conexión Automática

La UI se conecta automáticamente con los sistemas de Terry:

```javascript
// En app.py
from notes.voice_notes import get_notes_manager
from memory.memory_manager import MemoryManager
from macros.macro_recorder import get_macro_recorder
```

### Updates en Tiempo Real

Cuando ejecutas comandos vía voz en Terry normal, la UI se actualiza automáticamente si está conectada al mismo backend.

---

## 🚧 Estado de Desarrollo

### ✅ Completado

- [x] Diseño UI profesional con glassmorphism
- [x] Sistema de temas dark/light
- [x] Dashboard con estadísticas
- [x] Gestión de notas (crear, ver)
- [x] Historial de comandos
- [x] Visualización de macros
- [x] Panel de configuración
- [x] WebSocket para updates en tiempo real
- [x] Notificaciones toast
- [x] Modal para nueva nota
- [x] Responsive design

### 🚧 En Desarrollo

- [ ] Integración real con micrófono (Web Speech API)
- [ ] Visualizador de ondas de audio en tiempo real
- [ ] Editar/eliminar notas
- [ ] Ejecutar macros desde UI
- [ ] Crear/editar macros desde UI
- [ ] Gráficos de estadísticas (Chart.js)
- [ ] Búsqueda de notas en tiempo real
- [ ] Filtros por categoría

### 💡 Mejoras Futuras

- [ ] PWA (Progressive Web App)
- [ ] Notificaciones push del navegador
- [ ] Modo offline con Service Workers
- [ ] Exportar datos (JSON, CSV)
- [ ] Importar notas desde archivo
- [ ] Temas personalizables
- [ ] Atajos de teclado
- [ ] Drag & drop para notas

---

## 🎯 Ejemplo de Uso

```bash
# Terminal 1: Inicia la UI web
./run_ui.sh

# Terminal 2: (Opcional) Inicia Terry voz
./run_voice.sh

# Navegador: Abre http://localhost:8080
# - Click en "Nueva Nota"
# - Escribe: "Llamar a mamá mañana"
# - Categoría: Personal
# - Prioridad: Alta
# - Guardar

# Resultado:
# ✅ Nota guardada en ~/.terry/notes/notes.db
# ✅ Aparece en grid de notas
# ✅ Contador actualizado en dashboard
# ✅ Toast de confirmación
```

---

## 🔧 Personalización

### Cambiar Puerto

En `ui_web/app.py`:
```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=8080  # Cambiar aquí
)
```

### Cambiar Colores

En `ui_web/static/css/style.css`:
```css
:root {
    --primary: #tu-color;
    --secondary: #tu-color;
    /* ... */
}
```

### Agregar Nuevo Tab

1. Añade botón en HTML:
```html
<button class="tab" data-tab="nuevo">
    <i class="fas fa-icon"></i> Nuevo
</button>
```

2. Añade panel:
```html
<div class="tab-panel" id="nuevoPanel">
    <!-- Contenido -->
</div>
```

3. El JavaScript ya maneja el switch automáticamente

---

## 🐛 Troubleshooting

### Puerto ya en uso
```bash
# Ver qué proceso usa el puerto 8080
lsof -i :8080

# Matar proceso
kill -9 <PID>

# O cambiar puerto en app.py
```

### WebSocket no conecta
- Verifica que el servidor esté corriendo
- Revisa la consola del navegador (F12)
- Comprueba firewall/antivirus

### Estilos no cargan
- Verifica ruta en HTML: `/static/css/style.css`
- Comprueba que la carpeta `static` esté en `ui_web/`
- Fuerza refresh: Ctrl+Shift+R

---

## 📚 Tecnologías Usadas

- **Backend**: FastAPI 0.109+
- **Frontend**: Vanilla JavaScript (ES6+)
- **WebSocket**: FastAPI WebSockets
- **CSS**: Modern CSS3 con variables CSS
- **Iconos**: Font Awesome 6.4.0
- **Fuentes**: System fonts (San Francisco en macOS)

---

## 🎉 Resultado Final

Una interfaz web moderna, profesional y funcional para Terry que:

- ✅ Se ve **increíble** con glassmorphism
- ✅ Funciona en **tiempo real** con WebSocket
- ✅ Es **responsive** para desktop y mobile
- ✅ Tiene tema **dark/light** con toggle
- ✅ Muestra **estadísticas** en vivo
- ✅ Permite **crear y ver notas**
- ✅ Visualiza **historial de comandos**
- ✅ Se **conecta a Terry** automáticamente

**¡Pruébalo ahora con `./run_ui.sh`! 🚀**
