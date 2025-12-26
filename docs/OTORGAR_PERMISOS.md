# 🔐 GUÍA: Otorgar Permisos de Accesibilidad

## ❌ Problema

Terminal **NO tiene permisos** para controlar otras aplicaciones (Safari, Atlas, etc.). Por eso los comandos de música no funcionan.

---

## ✅ SOLUCIÓN PASO A PASO

### 1. Abre Preferencias del Sistema
```
Click en el ícono  en la barra superior
→ Preferencias del Sistema (o Ajustes del Sistema en macOS Ventura+)
```

### 2. Ve a Privacidad y Seguridad
```
En el panel izquierdo, busca:
"Privacidad y Seguridad"
(o "Seguridad y Privacidad" en versiones anteriores)
```

### 3. Click en "Accesibilidad"
```
En el menú izquierdo dentro de Privacidad:
→ Accesibilidad
```

### 4. Desbloquea (si está bloqueado)
```
Abajo a la izquierda verás un candado 🔒
→ Click en el candado
→ Ingresa tu contraseña de administrador
```

### 5. Busca "Terminal" en la lista
```
En la lista de apps, busca "Terminal"

Si NO está en la lista:
→ Click en el botón "+" (abajo)
→ Navega a: /System/Applications/Utilities/
→ Selecciona "Terminal.app"
→ Click "Abrir"
```

### 6. Activa el checkbox ✅
```
Marca el checkbox junto a "Terminal"

Debe quedar así:
☑ Terminal
```

### 7. Cierra Preferencias
```
Cierra la ventana de Preferencias
(Los cambios se guardan automáticamente)
```

---

## 🧪 VERIFICAR QUE FUNCIONA

Ejecuta este comando:
```bash
./check_permissions.sh
```

**Debes ver**:
```
✅ Terminal puede leer procesos
✅ Terminal puede enviar teclas
✅ Terminal puede activar Safari

✅ PERMISOS CORRECTOS
```

Si ves esto, **FUNCIONA**. Prueba el control de música:
```bash
./test_youtube_manual.sh
```

---

## ⚠️ SI SIGUE SIN FUNCIONAR

### Opción A: Reinicia Terminal
```bash
# Cierra Terminal completamente (Cmd+Q)
# Abre Terminal de nuevo
./check_permissions.sh
```

### Opción B: Usa la app en lugar de Terminal
```bash
# Si estás usando iTerm2 u otra terminal:
# Otorga permisos a ESA app también
# (Repite los pasos 1-7 pero para iTerm2)
```

### Opción C: Verifica la ubicación correcta
```
Terminal debe estar en:
/System/Applications/Utilities/Terminal.app

NO en:
/Applications/Terminal.app  ← INCORRECTO
```

---

## 📱 CAPTURAS DE PANTALLA (Referencia)

En macOS Ventura / Sonoma, verás:
```
Preferencias del Sistema
└── Privacidad y Seguridad
    └── Accesibilidad
        ├── 🔒 (Desbloquear primero)
        ├── [ ] App1
        ├── [✅] Terminal  ← Esto debe estar marcado
        └── [ ] App3
```

---

## 🎯 DESPUÉS DE OTORGAR PERMISOS

1. **Ejecuta**:
   ```bash
   ./check_permissions.sh
   ```

2. **Si ve ✅✅✅**, entonces ejecuta:
   ```bash
   ./test_youtube_manual.sh
   ```

3. **Debe funcionar** ahora:
   - ✅ Pausar video
   - ✅ Reproducir video
   - ✅ Siguiente video

---

## 💡 POR QUÉ ES NECESARIO

macOS **bloquea** que apps controlen otras apps por seguridad.

Terminal necesita permiso para:
- Activar Safari/Atlas/Chrome
- Enviar teclas (ESPACIO, Shift+N, etc.)
- Controlar reproducción de YouTube

Sin estos permisos = ❌ **NADA FUNCIONA**

Con estos permisos = ✅ **TODO FUNCIONA**

---

## 🚀 EJECUTA AHORA

```bash
./check_permissions.sh
```

Y comparte el resultado aquí.
