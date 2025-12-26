#!/bin/bash

echo "=== TEST: Conversación con memoria ==="
echo

echo "Mensaje 1: Hola, soy Bruno"
RESPONSE1=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "Hola, soy Bruno", "language": "es", "context": null}')
echo "Terry: $(echo $RESPONSE1 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "Mensaje 2: ¿Cómo me llamo? (CON contexto)"
RESPONSE2=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "¿Cómo me llamo?", "language": "es", "context": "Usuario: Hola, soy Bruno\nAsistente: ¡Hola Bruno! ¿En qué puedo ayudarte?"}')
echo "Terry: $(echo $RESPONSE2 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "Mensaje 3: ¿Cuál es mi color favorito? (Sin contexto - NO debería saber)"
RESPONSE3=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "¿Cuál es mi color favorito?", "language": "es", "context": null}')
echo "Terry: $(echo $RESPONSE3 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "✅ Test completado"
