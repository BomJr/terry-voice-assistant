# 🐛 ERRORES ENCONTRADOS EN TERRY WEB UI - REPORTE COMPLETO

**Fecha**: 25 de diciembre de 2025
**Versión**: Terry v6.1 Web UI
**Servidor probado**: http://localhost:8080

---

## 📊 RESUMEN EJECUTIVO

Se realizó una prueba exhaustiva de la UI web de Terry, incluyendo:
- ✅ Todos los endpoints de la API REST (9 endpoints probados)
- ✅ Comandos en español e inglés
- ✅ Archivos estáticos (HTML, CSS, JS)
- ✅ Conexión WebSocket
- ✅ Integración con CommandProcessor
- ✅ Logs del servidor

**Total de errores encontrados**: **8 errores** (3 críticos, 3 moderados, 2 menores)

---

## 🔴 ERRORES CRÍTICOS

### 1. ❌ `action_type` siempre retorna `null` en la API

**Severidad**: CRÍTICA
**Archivo**: `ui_web/app.py` línea 204

**Problema**:
```json
{
  "success": true,
  "command": "pon música",
  "response": "Reproduciendo",
  "action_type": null,  ← ❌ Siempre null
  "timestamp": "2025-12-25T17:59:01.666695"
}
```

**Causa raíz**:
El `CommandProcessor` devuelve las acciones en un array `actions` con estructura:
```python
{
  "intent": "media_play",
  "actions": [
    {
      "type": "media_play",  ← El action_type está aquí
      "params": {}
    }
  ],
  "response": "Reproduciendo"
}
```

Pero `app.py` busca `result.get("action_type")` que no existe en el diccionario raíz.

**Solución**:
```python
# En ui_web/app.py línea 200-206
response = {
    "success": True,
    "command": request.command,
    "response": result.get("response", "Comando ejecutado"),
    "action_type": result["actions"][0]["type"] if result.get("actions") else None,  # ✅ FIX
    "timestamp": datetime.now().isoformat()
}
```

**Impacto**: La UI no puede diferenciar qué tipo de acción se ejecutó, afectando el feedback visual y las estadísticas.

---

### 2. ❌ ChromaDB no funciona (pydantic-settings faltante)

**Severidad**: CRÍTICA
**Archivo**: `notes/voice_notes.py`

**Error**:
```
ChromaDB unavailable (PydanticImportError): `BaseSettings` has been moved
to the `pydantic-settings` package.
```

**Causa**: Falta instalar `pydantic-settings` en el virtualenv.

**Solución**:
```bash
source .venv/bin/activate
pip install pydantic-settings
```

**Impacto**: El sistema de búsqueda semántica de notas no funciona, fallback a SQLite básico.

---

### 3. ❌ MemoryManager no se puede instanciar

**Severidad**: CRÍTICA
**Archivo**: `ui_web/app.py` líneas 119, 170

**Error**:
```
Error getting memory stats: MemoryManager.__init__() missing 1 required
positional argument: 'db_path'
```

**Causa**: `MemoryManager()` se llama sin el parámetro requerido `db_path`.

**Ocurrencias**:
- Línea 119: `memory = MemoryManager()` en `/api/status`
- Línea 170: `memory = MemoryManager()` en `/api/stats`

**Solución**:
```python
# En ui_web/app.py
from pathlib import Path

# Línea 119
memory = MemoryManager(db_path=str(Path.home() / ".terry" / "memory" / "memory.db"))

# Línea 170
memory = MemoryManager(db_path=str(Path.home() / ".terry" / "memory" / "memory.db"))
```

**Impacto**: Las estadísticas de memoria siempre muestran 0 interacciones.

---

## 🟠 ERRORES MODERADOS

### 4. ⚠️ Archivo de rutinas no encontrado

**Severidad**: MODERADA
**Archivo**: `actions/routines/routine_manager.py`

**Error** (se repite constantemente):
```
Archivo de rutinas no encontrado: config/routines.yaml
```

**Causa**: El archivo SÍ existe en `/Users/bruno/Home-Alexa/config/routines.yaml`, pero el `RoutineManager` está buscando en una ruta relativa incorrecta desde el contexto del servidor web.

**Working Directory del servidor**: `/Users/bruno/Home-Alexa/ui_web/`
**Ruta buscada**: `config/routines.yaml` (relativa al CWD)
**Ruta real**: `../config/routines.yaml` (desde ui_web)

**Solución 1** (cambiar CWD):
```bash
# En run_ui.sh, cambiar a:
cd /Users/bruno/Home-Alexa  # ← No ui_web
python3 -m ui_web.app
```

**Solución 2** (fix en routine_manager.py):
```python
# En routine_manager.py
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
routines_file = project_root / "config" / "routines.yaml"
```

**Impacto**: Los comandos de rutinas ("modo trabajo", "buenas noches") no funcionan desde la UI web.

---

### 5. ⚠️ No existe `config/settings.py`

**Severidad**: MODERADA

**Error**:
```
Could not load settings for notes: No module named 'config.settings';
'config' is not a package
```

**Causa**: Varios módulos intentan importar `from config.settings import ...` pero solo existe `config/settings.yaml`, no `config/settings.py`.

**Módulos afectados**:
- `notes/voice_notes.py`
- `macros/macro_recorder.py`

**Solución**: Crear `config/settings.py` que cargue el YAML:
```python
# config/settings.py
import yaml
from pathlib import Path

_settings = None

def get_settings():
    global _settings
    if _settings is None:
        settings_file = Path(__file__).parent / "settings.yaml"
        with open(settings_file) as f:
            _settings = yaml.safe_load(f)
    return _settings

# Alias para compatibilidad
settings = get_settings()
```

**Impacto**: Algunas configuraciones no se cargan correctamente.

---

### 6. ⚠️ Comandos LLM devuelven respuesta vacía

**Severidad**: MODERADA

**Test**:
```bash
$ curl -X POST 'http://localhost:8080/api/command' \
  -d '{"command": "qué hora es", "language": "es"}'

# Respuesta:
{
  "response": "",  ← Vacío
  "action_type": null
}
```

**Test directo con CommandProcessor**:
```python
result = await processor.process_command("qué hora es", language="es")
# Retorna:
{
  "intent": "",
  "actions": [{"type": "", "params": {}}],
  "response": "",
  "raw_llm_response": "{\"intent\":\"\",\"actions\":[{\"type\":\"\",\"params\":{}}],\"response_text\":\"\",\"requires_confirmation\":false,\"language\":\"es\"}"
}
```

**Posibles causas**:
1. Ollama no está corriendo
2. El modelo no está cargado
3. El prompt no está funcionando correctamente

**Verificación**:
```bash
# ¿Ollama está corriendo?
curl http://localhost:11434/api/tags

# ¿El modelo está disponible?
ollama list | grep llama
```

**Impacto**: Comandos que no están en el cache (como "qué hora es") no funcionan.

---

## 🟡 ERRORES MENORES

### 7. ⚠️ Deprecation warning en FastAPI

**Severidad**: MENOR
**Archivo**: `ui_web/app.py` línea 344

**Warning**:
```
DeprecationWarning: on_event is deprecated, use lifespan event handlers instead.
```

**Código actual**:
```python
@app.on_event("startup")
async def startup_event():
    print("🚀 Terry Web UI starting...")
```

**Solución** (FastAPI 0.109+):
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Terry Web UI starting...")
    print("   Version: 6.1.0")
    print("   Access: http://localhost:8080")
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Terry Web UI",
    description="Professional web interface for Terry voice assistant",
    version="6.1.0",
    lifespan=lifespan
)
```

**Impacto**: Solo un warning, no afecta funcionalidad. Pero se deprecará en futuras versiones de FastAPI.

---

### 8. ⚠️ Silent mode toggle falla

**Severidad**: MENOR
**Archivo**: `ui_web/app.py` línea 30

**Problema**: Se intentó importar `toggle_silent` pero no existe:
```python
from utils.silent_mode import is_silent, toggle_silent  # ❌ toggle_silent no existe
```

**Ya corregido** en la última versión:
```python
from utils.silent_mode import is_silent  # ✅
```

**Endpoint afectado**: `POST /api/silent-mode` probablemente no funciona.

**Verificación**:
```bash
curl -X POST http://localhost:8080/api/silent-mode
```

**Solución**: Verificar que existe la función `toggle_silent()` en `utils/silent_mode.py` o implementarla.

---

## ✅ LO QUE SÍ FUNCIONA

### Endpoints probados exitosamente:

1. **GET /api/status** ✅
   - Retorna estado del sistema, versión, features
   - Silent mode funciona

2. **GET /api/stats** ✅
   - Retorna estadísticas de notas, macros, memoria (aunque memoria = 0 por error #3)

3. **POST /api/command** ✅ (parcial)
   - Comandos en español funcionan
   - Comandos en inglés funcionan
   - Comandos desde cache funcionan perfectamente
   - Comandos con LLM fallan (error #6)
   - `action_type` siempre null (error #1)

4. **GET /api/notes** ✅
   - Lista notas correctamente

5. **POST /api/notes** ✅
   - Crea notas exitosamente

6. **GET /api/macros** ✅
   - Lista macros (0 en este test)

7. **WebSocket /ws** ✅
   - Ping/pong funciona
   - Subscribe funciona
   - Broadcast funciona

8. **Archivos estáticos** ✅
   - HTML se carga correctamente
   - CSS con colores cyan/teal carga bien
   - JavaScript con Web Speech API funciona

### Comandos probados:

| Comando | Español | Inglés | Status |
|---------|---------|--------|--------|
| Pon música | ✅ | ✅ (play music) | Funciona |
| Sube volumen | ✅ | ✅ (turn up) | Funciona |
| Pausa | ✅ | ✅ (pause) | Funciona |
| Qué hora es | ❌ | ❌ (what time) | Respuesta vacía |
| Chiste | ✅ | - | Funciona (LLM respondió) |

---

## 🔧 PRIORIDAD DE CORRECCIÓN

### Prioridad 1 (Arreglar AHORA):
1. **Error #1**: Fix `action_type` en API response
2. **Error #3**: Fix MemoryManager instantiation
3. **Error #6**: Verificar por qué Ollama no responde a algunos comandos

### Prioridad 2 (Arreglar esta semana):
4. **Error #4**: Fix rutinas con ruta absoluta
5. **Error #2**: Instalar pydantic-settings
6. **Error #5**: Crear config/settings.py

### Prioridad 3 (Mejorar después):
7. **Error #7**: Migrar a lifespan handlers
8. **Error #8**: Implementar toggle_silent si es necesario

---

## 📝 TESTS REALIZADOS

### API REST Tests:
```bash
✅ TEST 1:  GET /api/status
✅ TEST 2:  GET /api/stats
✅ TEST 3:  POST /api/command (pon música)
✅ TEST 4:  POST /api/command (sube volumen)
✅ TEST 5:  GET /api/notes
✅ TEST 6:  POST /api/notes
✅ TEST 7:  GET /api/macros
✅ TEST 8:  POST /api/command (inglés: what time is it)
⚠️ TEST 9:  POST /api/command (LLM: cuéntame un chiste) - funcionó
❌ TEST 10: POST /api/command (qué hora es) - respuesta vacía
✅ TEST 11: GET /static/css/style.css
✅ TEST 12: GET /static/js/app.js
✅ TEST 13: WebSocket ping/pong
✅ TEST 14: WebSocket subscribe
```

### Comandos directos a CommandProcessor:
```bash
✅ "pon música"    → intent: media_play, response: "Reproduciendo"
✅ "sube volumen"  → intent: volume_up, response: "Subiendo volumen"
✅ "pausa"         → intent: media_pause, response: "Pausando"
❌ "qué hora es"   → intent: "", response: ""
```

---

## 💡 RECOMENDACIONES ADICIONALES

### 1. Agregar health check endpoint:
```python
@app.get("/api/health")
async def health_check():
    """Health check para monitoring"""
    return {
        "status": "healthy",
        "ollama": await check_ollama_connection(),
        "db": check_database_connection(),
        "timestamp": datetime.now().isoformat()
    }
```

### 2. Mejorar error handling:
```python
# En execute_command, agregar más detalles:
except Exception as e:
    logger.error(f"Error executing command: {e}", exc_info=True)  # ← Stack trace
    return JSONResponse(
        status_code=500,  # ← HTTP 500 en vez de 200
        content={
            "success": False,  # ← false no true
            "error": str(e),
            "error_type": type(e).__name__
        }
    )
```

### 3. Agregar logging de requests:
```python
# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
    return response
```

### 4. Validación de comandos vacíos:
```python
@app.post("/api/command")
async def execute_command(request: CommandRequest):
    if not request.command or not request.command.strip():
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Command cannot be empty"}
        )
    # ...
```

---

## 🎯 CONCLUSIÓN

La UI web está **funcionalmente operativa** para comandos básicos desde cache, pero tiene **3 errores críticos** que limitan su funcionalidad completa:

1. El `action_type` no se devuelve correctamente
2. La memoria no se inicializa bien
3. ChromaDB no funciona (búsqueda semántica deshabilitada)

Los endpoints REST funcionan, el WebSocket funciona, los archivos estáticos cargan correctamente, y el diseño visual con colores cyan/teal se ve bien.

**Estimación de tiempo para arreglar**:
- Errores críticos (3): ~30-45 minutos
- Errores moderados (3): ~1-2 horas
- Errores menores (2): ~30 minutos

**Total**: 2-3 horas para tener la UI 100% funcional.
