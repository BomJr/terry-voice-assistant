#!/bin/bash

# ============================================
# Terry - Sanitization Verification Script
# ============================================
# Checks for remaining personal information
# before GitHub publication
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║     Terry - Sanitization Verification Tool        ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

cd "$(dirname "$0")/.." || exit 1

issues_found=0

# Check 1: Personal name
echo -e "${BLUE}[1/7]${NC} Checking for personal name 'Bruno'..."
bruno_count=$(grep -r "bruno\|Bruno" --include="*.py" --include="*.md" --include="*.yaml" --exclude-dir=".venv" --exclude-dir="docs/archive" . 2>/dev/null | wc -l | tr -d ' ')
if [ "$bruno_count" -gt 0 ]; then
    echo -e "      ${RED}❌ Found $bruno_count instances${NC}"
    echo "      Run: grep -r 'bruno\|Bruno' --include='*.py' --include='*.md' --include='*.yaml' --exclude-dir='.venv' ."
    issues_found=$((issues_found + 1))
else
    echo -e "      ${GREEN}✅ No instances found${NC}"
fi

# Check 2: Absolute paths
echo -e "${BLUE}[2/7]${NC} Checking for absolute paths (/Users/bruno/)..."
paths_count=$(grep -r "/Users/bruno" --include="*.py" --include="*.md" --exclude-dir=".venv" . 2>/dev/null | wc -l | tr -d ' ')
if [ "$paths_count" -gt 0 ]; then
    echo -e "      ${RED}❌ Found $paths_count instances${NC}"
    echo "      Run: grep -r '/Users/bruno' --include='*.py' --include='*.md' --exclude-dir='.venv' ."
    issues_found=$((issues_found + 1))
else
    echo -e "      ${GREEN}✅ No instances found${NC}"
fi

# Check 3: IP addresses
echo -e "${BLUE}[3/7]${NC} Checking for local IP addresses (192.168.x.x)..."
ip_count=$(grep -r "192\.168\.[0-9]\+\.[0-9]\+" --include="*.py" --include="*.md" --include="*.yaml" --exclude-dir=".venv" --exclude="GITHUB_PUBLICATION_AUDIT.md" . 2>/dev/null | wc -l | tr -d ' ')
if [ "$ip_count" -gt 5 ]; then  # Allow a few example placeholders
    echo -e "      ${YELLOW}⚠️  Found $ip_count instances (review if they're examples)${NC}"
    issues_found=$((issues_found + 1))
else
    echo -e "      ${GREEN}✅ Acceptable level ($ip_count instances - likely examples)${NC}"
fi

# Check 4: Database files
echo -e "${BLUE}[4/7]${NC} Checking for database files..."
if find . -name "*.db" -o -name "*.sqlite" 2>/dev/null | grep -v ".venv" | grep -q .; then
    echo -e "      ${RED}❌ Database files found${NC}"
    find . -name "*.db" -o -name "*.sqlite" 2>/dev/null | grep -v ".venv"
    issues_found=$((issues_found + 1))
else
    echo -e "      ${GREEN}✅ No database files${NC}"
fi

# Check 5: Log files
echo -e "${BLUE}[5/7]${NC} Checking for log files..."
if [ -d "logs" ] && find logs -name "*.log" 2>/dev/null | grep -q .; then
    echo -e "      ${RED}❌ Log files found${NC}"
    ls -la logs/
    issues_found=$((issues_found + 1))
else
    echo -e "      ${GREEN}✅ No log files${NC}"
fi

# Check 6: Cache files
echo -e "${BLUE}[6/7]${NC} Checking for cache files..."
cache_files=0
for cache_dir in "cache" "ui_web/cache" "terry/core/ui/web/cache"; do
    if [ -d "$cache_dir" ] && find "$cache_dir" -type f ! -name ".gitkeep" 2>/dev/null | grep -q .; then
        echo -e "      ${RED}❌ Cache files found in $cache_dir${NC}"
        cache_files=$((cache_files + 1))
    fi
done

if [ "$cache_files" -gt 0 ]; then
    issues_found=$((issues_found + 1))
else
    echo -e "      ${GREEN}✅ No cache files${NC}"
fi

# Check 7: Python artifacts
echo -e "${BLUE}[7/7]${NC} Checking for Python artifacts..."
if find . -name "__pycache__" -o -name "*.pyc" 2>/dev/null | grep -v ".venv" | grep -q .; then
    echo -e "      ${YELLOW}⚠️  Python cache found (minor issue)${NC}"
else
    echo -e "      ${GREEN}✅ No Python artifacts${NC}"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════"
if [ "$issues_found" -eq 0 ]; then
    echo -e "${GREEN}✅ PASSED: No critical issues found!${NC}"
    echo ""
    echo "Repository appears ready for GitHub publication."
    echo ""
    echo "Final steps:"
    echo "  1. Review README.md"
    echo "  2. Add LICENSE file"
    echo "  3. Create example configs"
    echo "  4. Double-check documentation"
    echo "  5. Run: git status"
    exit 0
else
    echo -e "${RED}❌ FAILED: $issues_found issue(s) found${NC}"
    echo ""
    echo "Please address the issues above before publication."
    echo "See GITHUB_PUBLICATION_AUDIT.md for details."
    exit 1
fi
