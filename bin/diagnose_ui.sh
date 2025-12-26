#!/bin/bash
# Diagnóstico completo de Web UI

echo "🔍 Diagnóstico de Terry Web UI"
echo ""

# 1. Verificar servidor
echo "1️⃣ Verificando servidor..."
if lsof -ti:8080 >/dev/null 2>&1; then
    echo "   ✅ Servidor corriendo en puerto 8080"
    PID=$(lsof -ti:8080)
    echo "   PID: $PID"
else
    echo "   ❌ Servidor NO está corriendo"
    echo "   Iniciando servidor..."
    cd "$(dirname "$0")/.."
    source .venv/bin/activate
    python3 -m uvicorn terry.core.ui.web.app:app --host 0.0.0.0 --port 8080 > /tmp/terry_ui.log 2>&1 &
    sleep 3
fi

echo ""

# 2. Test API
echo "2️⃣ Probando API endpoints..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/status)
if [ "$STATUS" = "200" ]; then
    echo "   ✅ GET /api/status: OK (200)"
else
    echo "   ❌ GET /api/status: Error ($STATUS)"
fi

# 3. Test página principal
echo ""
echo "3️⃣ Probando página principal..."
MAIN=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/)
if [ "$MAIN" = "200" ]; then
    echo "   ✅ GET /: OK (200)"
else
    echo "   ❌ GET /: Error ($MAIN)"
fi

# 4. Test archivos estáticos
echo ""
echo "4️⃣ Probando archivos estáticos..."
JS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/static/js/app.js)
if [ "$JS" = "200" ]; then
    echo "   ✅ JavaScript: OK (200)"
else
    echo "   ❌ JavaScript: Error ($JS)"
fi

CSS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/static/css/style.css)
if [ "$CSS" = "200" ]; then
    echo "   ✅ CSS: OK (200)"
else
    echo "   ❌ CSS: Error ($CSS)"
fi

# 5. Ver últimos logs
echo ""
echo "5️⃣ Últimos logs del servidor:"
echo "   (últimas 10 líneas de /tmp/terry_ui.log)"
echo ""
tail -10 /tmp/terry_ui.log 2>/dev/null || echo "   No hay logs disponibles"

echo ""
echo "6️⃣ Instrucciones para diagnosticar en navegador:"
echo ""
echo "   1. Abre: http://localhost:8080"
echo "   2. Presiona F12 (o Cmd+Option+I en Mac)"
echo "   3. Ve a la tab 'Console'"
echo "   4. Busca mensajes de error (rojos)"
echo "   5. Copia y pega cualquier error aquí"
echo ""
echo "7️⃣ Si la página se ve pero no responde:"
echo ""
echo "   Posibles causas:"
echo "   • JavaScript bloqueado por navegador"
echo "   • Modal/overlay invisible bloqueando clicks"
echo "   • Error de inicialización de TerryUI"
echo ""
echo "   Prueba:"
echo "   • Abrir en modo incógnito"
echo "   • Probar en otro navegador (Chrome, Firefox, Safari)"
echo "   • Limpiar caché: Cmd+Shift+R (Mac) o Ctrl+Shift+R (Linux/Win)"
echo ""
