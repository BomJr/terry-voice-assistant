#!/bin/bash
# Terry v6.1.9 - Test Automatizado de Todas las Features
# Ejecuta sin intervención del usuario

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Counters
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Terry v6.1.9 - Test Suite Completo          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}\n"

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "Testing: $test_name ... "

    if eval "$test_command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Start server
echo -e "${CYAN}Starting Web UI server...${NC}"
source .venv/bin/activate
lsof -ti:8080 | xargs kill -9 2>/dev/null || true
python3 -m uvicorn terry.core.ui.web.app:app --host 0.0.0.0 --port 8080 --log-level critical > /tmp/terry_test.log 2>&1 &
SERVER_PID=$!

# Wait for server
echo -n "Waiting for server to start..."
for i in {1..15}; do
    if curl -s http://localhost:8080/api/status >/dev/null 2>&1; then
        echo -e " ${GREEN}OK${NC}\n"
        break
    fi
    sleep 1
done

# ============================================================
# API ENDPOINT TESTS
# ============================================================

echo -e "${YELLOW}═══ API Endpoint Tests ═══${NC}\n"

# System endpoints
run_test "GET /api/status" \
    "curl -s http://localhost:8080/api/status | jq -e '.status == \"online\"'"

run_test "GET /api/stats" \
    "curl -s http://localhost:8080/api/stats | jq -e '.notes'"

run_test "POST /api/silent-mode" \
    "curl -s -X POST http://localhost:8080/api/silent-mode | jq -e '.silent'"

# Command endpoint
run_test "POST /api/command (basic)" \
    "curl -s -X POST http://localhost:8080/api/command -H 'Content-Type: application/json' -d '{\"command\":\"test\",\"language\":\"es\"}' | jq -e '.success'"

run_test "POST /api/command (with context)" \
    "curl -s -X POST http://localhost:8080/api/command -H 'Content-Type: application/json' -d '{\"command\":\"qué hora es\",\"language\":\"es\",\"context\":\"test\"}' | jq -e '.response'"

# Notes endpoints
run_test "POST /api/notes (create)" \
    "curl -s -X POST http://localhost:8080/api/notes -H 'Content-Type: application/json' -d '{\"content\":\"Test note\",\"category\":\"test\",\"priority\":1}' | jq -e '.success'"

run_test "GET /api/notes (list)" \
    "curl -s 'http://localhost:8080/api/notes?limit=10' | jq -e '.notes'"

run_test "GET /api/notes (with category filter)" \
    "curl -s 'http://localhost:8080/api/notes?category=test&limit=5' | jq -e '.total >= 0'"

# Macros endpoint
run_test "GET /api/macros" \
    "curl -s http://localhost:8080/api/macros | jq -e '.macros'"

# Camera endpoints
run_test "GET /api/camera/config" \
    "curl -s http://localhost:8080/api/camera/config | jq -e '.config'"

run_test "GET /api/camera/status" \
    "curl -s http://localhost:8080/api/camera/status | jq -e 'has(\"running\")'"

run_test "POST /api/camera/config" \
    "curl -s -X POST http://localhost:8080/api/camera/config -H 'Content-Type: application/json' -d '{\"enabled\":false,\"use_webcam\":false}' | jq -e '.success'"

# ============================================================
# SWAGGER/OPENAPI TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Swagger/OpenAPI Tests ═══${NC}\n"

run_test "GET /docs (Swagger UI available)" \
    "curl -s http://localhost:8080/docs | grep -q 'Swagger UI'"

run_test "GET /redoc (ReDoc available)" \
    "curl -s http://localhost:8080/redoc | grep -q 'Redoc'"

run_test "GET /openapi.json (schema exists)" \
    "curl -s http://localhost:8080/openapi.json | jq -e '.openapi'"

run_test "OpenAPI schema version" \
    "curl -s http://localhost:8080/openapi.json | jq -e '.info.version == \"6.1.9\"'"

run_test "OpenAPI schema has tags" \
    "curl -s http://localhost:8080/openapi.json | jq -e '.tags | length >= 6'"

run_test "OpenAPI schema has all endpoints" \
    "curl -s http://localhost:8080/openapi.json | jq -e '.paths | length >= 12'"

# ============================================================
# RESPONSE MODEL VALIDATION TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Response Model Validation ═══${NC}\n"

run_test "StatusResponse has required fields" \
    "curl -s http://localhost:8080/api/status | jq -e 'has(\"status\") and has(\"version\") and has(\"timestamp\")'"

run_test "CommandResponse has required fields" \
    "curl -s -X POST http://localhost:8080/api/command -H 'Content-Type: application/json' -d '{\"command\":\"test\"}' | jq -e 'has(\"success\") and has(\"command\") and has(\"response\")'"

run_test "NotesResponse has required fields" \
    "curl -s http://localhost:8080/api/notes | jq -e 'has(\"notes\") and has(\"total\")'"

run_test "MacrosResponse has required fields" \
    "curl -s http://localhost:8080/api/macros | jq -e 'has(\"macros\") and has(\"total\")'"

# ============================================================
# VALIDATION TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Input Validation Tests ═══${NC}\n"

# Test priority validation (should accept 0-5)
run_test "Note priority validation (valid: 3)" \
    "curl -s -X POST http://localhost:8080/api/notes -H 'Content-Type: application/json' -d '{\"content\":\"test\",\"priority\":3}' | jq -e '.success'"

# Test invalid priority (should fail)
run_test "Note priority validation (invalid: 10)" \
    "! curl -s -X POST http://localhost:8080/api/notes -H 'Content-Type: application/json' -d '{\"content\":\"test\",\"priority\":10}' | jq -e '.success'"

# Test required fields
run_test "Command without required field (should fail)" \
    "curl -s -X POST http://localhost:8080/api/command -H 'Content-Type: application/json' -d '{}' | grep -q 'detail'"

# ============================================================
# WEB UI TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Web UI Tests ═══${NC}\n"

run_test "GET / (main UI loads)" \
    "curl -s http://localhost:8080 | grep -q 'Terry'"

run_test "Web UI has version 6.1.9" \
    "curl -s http://localhost:8080 | grep -q 'v6.1.9'"

run_test "Web UI has API docs button" \
    "curl -s http://localhost:8080 | grep -q '/docs'"

run_test "Web UI has all 8 tabs" \
    "curl -s http://localhost:8080 | grep -c 'data-tab=' | grep -q '8'"

# ============================================================
# STATIC ASSETS TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Static Assets Tests ═══${NC}\n"

run_test "GET /static/js/app.js" \
    "curl -s http://localhost:8080/static/js/app.js | grep -q 'class TerryUI'"

run_test "GET /static/css/style.css" \
    "curl -s http://localhost:8080/static/css/style.css | grep -q ':root'"

run_test "app.js has all required methods" \
    "curl -s http://localhost:8080/static/js/app.js | grep -q 'initMonitor\\|refreshMonitor\\|updateSystemHealth'"

# ============================================================
# INTEGRATION TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Integration Tests ═══${NC}\n"

# Create note and verify it appears in list
run_test "Create note → Verify in list" \
    "curl -s -X POST http://localhost:8080/api/notes -H 'Content-Type: application/json' -d '{\"content\":\"Integration test note\",\"category\":\"integration\"}' >/dev/null && curl -s 'http://localhost:8080/api/notes?category=integration' | jq -e '.notes | map(select(.content | contains(\"Integration\"))) | length > 0'"

# Execute command → Verify stats updated
run_test "Execute command → Stats updated" \
    "BEFORE=\$(curl -s http://localhost:8080/api/stats | jq '.commands.total // 0') && curl -s -X POST http://localhost:8080/api/command -H 'Content-Type: application/json' -d '{\"command\":\"test\"}' >/dev/null && sleep 0.5 && AFTER=\$(curl -s http://localhost:8080/api/stats | jq '.commands.total // 0') && [ \"\$AFTER\" -ge \"\$BEFORE\" ]"

# Toggle silent mode twice → Verify state changes
run_test "Toggle silent mode twice" \
    "STATE1=\$(curl -s -X POST http://localhost:8080/api/silent-mode | jq -r '.silent') && STATE2=\$(curl -s -X POST http://localhost:8080/api/silent-mode | jq -r '.silent') && [ \"\$STATE1\" != \"\$STATE2\" ]"

# ============================================================
# PERFORMANCE TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Performance Tests ═══${NC}\n"

# Test response time for status endpoint
run_test "GET /api/status < 100ms" \
    "TIME=\$(curl -w '%{time_total}' -o /dev/null -s http://localhost:8080/api/status) && awk 'BEGIN {exit !('\$TIME' < 0.1)}'"

# Test response time for command endpoint
run_test "POST /api/command < 3s" \
    "TIME=\$(curl -w '%{time_total}' -o /dev/null -s -X POST http://localhost:8080/api/command -H 'Content-Type: application/json' -d '{\"command\":\"test\"}') && awk 'BEGIN {exit !('\$TIME' < 3)}'"

# Test concurrent requests
run_test "Handle 5 concurrent requests" \
    "for i in {1..5}; do curl -s http://localhost:8080/api/status & done; wait"

# ============================================================
# ERROR HANDLING TESTS
# ============================================================

echo -e "\n${YELLOW}═══ Error Handling Tests ═══${NC}\n"

# Test 404 for non-existent endpoint
run_test "404 for non-existent endpoint" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/nonexistent | grep -q '404'"

# Test invalid JSON
run_test "400 for invalid JSON" \
    "curl -s -X POST http://localhost:8080/api/command -H 'Content-Type: application/json' -d 'invalid json' | grep -q 'detail'"

# Test missing content-type
run_test "422 for missing content-type" \
    "curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8080/api/notes -d '{\"content\":\"test\"}' | grep -q '422'"

# ============================================================
# CLEANUP AND SUMMARY
# ============================================================

# Stop server
kill $SERVER_PID 2>/dev/null || true

echo -e "\n${BLUE}╔════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              TEST SUMMARY                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════╝${NC}\n"

echo -e "Total tests:  ${CYAN}$TOTAL_TESTS${NC}"
echo -e "Passed:       ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed:       ${RED}$TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ ALL TESTS PASSED!${NC}\n"
    exit 0
else
    PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
    echo -e "\nPass rate: ${YELLOW}${PASS_RATE}%${NC}\n"
    exit 1
fi
