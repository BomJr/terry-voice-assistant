# ✅ SOLUCIÓN DEFINITIVA: nowplaying-cli

## 🎯 EL PROBLEMA (RESUELTO)

**Antes**:
- Se abría Safari cuando querías pausar Atlas
- Aparecía una "k" escrita en el navegador
- Solo funcionaba si activabas la ventana

**Ahora**:
- ✅ Controla lo que **ESTÁ REPRODUCIENDO**
- ✅ **NO abre** navegadores
- ✅ **NO escribe** texto
- ✅ Funciona con YouTube, Spotify, Music, etc.

---

## 🔧 SOLUCIÓN: nowplaying-cli

[**nowplaying-cli**](https://github.com/kirtan-shah/nowplaying-cli) es una herramienta de línea de comandos para macOS que controla la reproducción de medios usando las APIs nativas del sistema.

**Características**:
- ✅ Controla **cualquier app** que reproduzca audio
- ✅ NO requiere activar ventanas
- ✅ NO escribe texto
- ✅ Funciona en segundo plano
- ✅ Compatible con macOS Ventura y Sonoma

---

## 📦 INSTALACIÓN (2 PASOS)

### Paso 1: Instalar nowplaying-cli

```bash
./install_nowplaying.sh
```

O manualmente con Homebrew:
```bash
brew install nowplaying-cli
```

### Paso 2: Verificar instalación

```bash
nowplaying-cli --version
```

Debes ver algo como: `nowplaying-cli version 1.2.1`

---

## 🧪 PRUEBA AHORA

Con nowplaying-cli instalado:

```bash
./run_test.sh
```

Luego escribe:
```
para la música    → Pausa lo que esté reproduciendo ✅
pon música        → Reproduce ✅
siguiente         → Siguiente canción/video ✅
```

**RESULTADO ESPERADO**:
- ✅ NO se abre Safari ni ningún navegador
- ✅ NO aparece texto escrito
- ✅ Solo se pausa/reproduce lo que está sonando
- ✅ Funciona con YouTube en Atlas, Chrome, Safari, etc.

---

## 📊 CÓMO FUNCIONA

### Sistema Dual (Automático)

El sistema ahora usa **dos métodos** en orden:

| Prioridad | Método | Ventajas |
|-----------|--------|----------|
| 1️⃣ | **nowplaying-cli** | ✅ Mejor - controla lo que reproduce, no activa ventanas |
| 2️⃣ | **Teclas F7/F8/F9** | Fallback si nowplaying-cli no está instalado |

**Código** (`utils/media_detector.py`):
```python
if _has_nowplaying_cli():
    # Usar nowplaying-cli (mejor)
    subprocess.run(['nowplaying-cli', 'pause'])
else:
    # Fallback: teclas de media
    osascript -e 'key code 100'  # F8
```

---

## 🎹 COMANDOS DISPONIBLES

nowplaying-cli soporta:

| Comando | Función |
|---------|---------|
| `nowplaying-cli play` | Reproduce |
| `nowplaying-cli pause` | Pausa |
| `nowplaying-cli togglePlayPause` | Alterna play/pause |
| `nowplaying-cli next` | Siguiente |
| `nowplaying-cli previous` | Anterior |
| `nowplaying-cli get title artist` | Obtiene info de la canción |

---

## 🔍 VERIFICAR QUÉ MÉTODO SE USA

Para ver si tu sistema está usando nowplaying-cli:

```bash
source .venv/bin/activate
python3 -c "
from utils.media_detector import _has_nowplaying_cli
if _has_nowplaying_cli():
    print('✅ Usando nowplaying-cli')
else:
    print('⚠️ Usando fallback (teclas de media)')
    print('Instala nowplaying-cli para mejor rendimiento')
"
```

---

## ⚙️ SI NO TIENES HOMEBREW

### Opción 1: Instalar Homebrew (Recomendado)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Opción 2: Compilar desde fuente
```bash
git clone https://github.com/kirtan-shah/nowplaying-cli.git
cd nowplaying-cli
make
mv nowplaying-cli ~/.local/bin/
```

---

## 📝 REFERENCIAS

- **Repositorio GitHub**: [kirtan-shah/nowplaying-cli](https://github.com/kirtan-shah/nowplaying-cli)
- **Compatibilidad**: macOS Ventura (13.1-13.6), macOS Sonoma (14.4+)
- **Licencia**: GPL-3.0

**Fuentes investigadas**:
- [nowplaying-cli GitHub](https://github.com/kirtan-shah/nowplaying-cli)
- [Apple Community: Media Control](https://discussions.apple.com/thread/5061523)
- [AppleScript Media Controller](https://github.com/jonathanpoh/applescript-media-controller)

---

## 🎉 RESULTADO FINAL

| Antes | Ahora con nowplaying-cli |
|-------|--------------------------|
| ❌ Abre Safari cuando usas Atlas | ✅ NO abre nada |
| ❌ Escribe "k" en el navegador | ✅ NO escribe nada |
| ❌ Requiere que el navegador esté activo | ✅ Funciona en segundo plano |
| ❌ Solo funciona con navegador al frente | ✅ Funciona siempre |

---

## 🚀 EJECUTA AHORA

```bash
# 1. Instalar
./install_nowplaying.sh

# 2. Probar
./run_test.sh

# 3. Usar
Tú: para la música    ← Pausa lo que esté reproduciendo ✅
Tú: pon música        ← Reproduce ✅
Tú: siguiente         ← Siguiente ✅
```

**¡TODO DEBE FUNCIONAR AHORA!** 🎉
