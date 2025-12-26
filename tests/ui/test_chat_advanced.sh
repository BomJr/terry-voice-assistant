#!/bin/bash

echo "╔══════════════════════════════════════════════════════════╗"
echo "║    TESTS AVANZADOS DE MEMORIA CONVERSACIONAL             ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo

# Test 1: Conversación de 3 turnos
echo "📝 TEST 1: Conversación de 3 turnos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "👤 Usuario: Mi color favorito es el azul"
R1=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "Mi color favorito es el azul", "language": "es", "context": null}')
echo "🤖 Terry: $(echo $R1 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "👤 Usuario: También me gusta el verde"
R2=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "También me gusta el verde", "language": "es", "context": "Usuario: Mi color favorito es el azul\nAsistente: Entendido, el azul es un color muy bonito"}')
echo "🤖 Terry: $(echo $R2 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "👤 Usuario: ¿Qué colores me gustan?"
R3=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "¿Qué colores me gustan?", "language": "es", "context": "Usuario: Mi color favorito es el azul\nAsistente: Entendido, el azul es un color muy bonito\nUsuario: También me gusta el verde\nAsistente: ¡Genial! El verde también es hermoso"}')
echo "🤖 Terry: $(echo $R3 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

# Test 2: Referencias pronominales
echo "📝 TEST 2: Referencias pronominales (él, eso, lo)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "👤 Usuario: Tengo un perro llamado Max"
R4=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "Tengo un perro llamado Max", "language": "es", "context": null}')
echo "🤖 Terry: $(echo $R4 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "👤 Usuario: ¿Cómo se llama?"
R5=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "¿Cómo se llama?", "language": "es", "context": "Usuario: Tengo un perro llamado Max\nAsistente: ¡Qué bien! Max debe ser un gran compañero"}')
echo "🤖 Terry: $(echo $R5 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

# Test 3: Cambio de tema
echo "📝 TEST 3: Cambio de tema (debería olvidar sin contexto)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "👤 Usuario: ¿De qué hablábamos? (sin contexto)"
R6=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "¿De qué hablábamos?", "language": "es", "context": null}')
echo "🤖 Terry: $(echo $R6 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

# Test 4: Números y datos
echo "📝 TEST 4: Recordar números y datos específicos"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "👤 Usuario: Mi número de teléfono es 555-1234"
R7=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "Mi número de teléfono es 555-1234", "language": "es", "context": null}')
echo "🤖 Terry: $(echo $R7 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "👤 Usuario: ¿Cuál es mi número?"
R8=$(curl -s -X POST http://localhost:8080/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "¿Cuál es mi número?", "language": "es", "context": "Usuario: Mi número de teléfono es 555-1234\nAsistente: He anotado tu número 555-1234"}')
echo "🤖 Terry: $(echo $R8 | python3 -c 'import json,sys; print(json.load(sys.stdin)["response"])')"
echo

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                    TESTS COMPLETADOS                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
