#!/bin/bash

# ============================================
# Terry Voice Assistant - GitHub Sanitization
# ============================================
# This script removes personal data and prepares
# the repository for public GitHub publication.
#
# CAUTION: This script DELETES data. Review before running.
# ============================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════╗"
echo "║   Terry - GitHub Publication Sanitization Tool    ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in the right directory
if [ ! -f "CLAUDE.md" ]; then
    echo -e "${RED}❌ Error: Must be run from Home-Alexa root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  WARNING: This will DELETE personal data${NC}"
echo ""
echo "The following will be removed:"
echo "  - logs/ directory (command history)"
echo "  - data/ directory (databases with personal info)"
echo "  - cache/ directories (personal queries)"
echo "  - Python cache files (__pycache__, *.pyc)"
echo "  - macOS files (.DS_Store)"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}Aborted by user${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}🧹 Starting sanitization...${NC}"
echo ""

# Step 1: Remove personal data directories
echo -e "${GREEN}[1/8]${NC} Removing logs directory..."
if [ -d "logs" ]; then
    rm -rf logs/
    echo "      ✅ Deleted logs/"
else
    echo "      ℹ️  logs/ not found (already clean)"
fi

echo -e "${GREEN}[2/8]${NC} Removing data directory..."
if [ -d "data" ]; then
    rm -rf data/
    echo "      ✅ Deleted data/"
else
    echo "      ℹ️  data/ not found (already clean)"
fi

echo -e "${GREEN}[3/8]${NC} Removing cache directories..."
for cache_dir in "cache" "ui_web/cache" "terry/core/ui/web/cache"; do
    if [ -d "$cache_dir" ]; then
        rm -rf "$cache_dir"
        echo "      ✅ Deleted $cache_dir/"
    fi
done

# Step 2: Create directory structure with .gitkeep
echo -e "${GREEN}[4/8]${NC} Creating directory structure..."
mkdir -p logs
mkdir -p data
mkdir -p cache
mkdir -p terry/core/ui/web/cache

touch logs/.gitkeep
touch data/.gitkeep
touch cache/.gitkeep
touch terry/core/ui/web/cache/.gitkeep

echo "      ✅ Created empty directories with .gitkeep"

# Step 3: Clean Python artifacts
echo -e "${GREEN}[5/8]${NC} Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
echo "      ✅ Removed Python cache"

# Step 4: Clean macOS files
echo -e "${GREEN}[6/8]${NC} Cleaning macOS system files..."
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "._*" -delete 2>/dev/null || true
echo "      ✅ Removed macOS files"

# Step 5: Create example configuration
echo -e "${GREEN}[7/8]${NC} Creating example configuration..."
if [ -f "terry/core/config/settings.yaml" ]; then
    cp terry/core/config/settings.yaml terry/core/config/settings.yaml.example
    echo "      ✅ Created settings.yaml.example"
else
    echo "      ⚠️  settings.yaml not found"
fi

# Step 6: Archive session notes (optional)
echo -e "${GREEN}[8/8]${NC} Archiving session documentation..."
mkdir -p docs/archive
session_files=$(find . -maxdepth 1 -type f \( -name "RESUMEN_*.md" -o -name "SESION_*.md" -o -name "*_COMPLETO.md" \) 2>/dev/null | wc -l)

if [ "$session_files" -gt 0 ]; then
    echo "      Found $session_files session documentation files"
    read -p "      Move to docs/archive/? (yes/no): " archive_confirm

    if [ "$archive_confirm" = "yes" ]; then
        find . -maxdepth 1 -type f \( -name "RESUMEN_*.md" -o -name "SESION_*.md" -o -name "*_COMPLETO.md" \) -exec mv {} docs/archive/ \; 2>/dev/null || true
        echo "      ✅ Moved session docs to archive"
    else
        echo "      ⏭️  Skipped archiving"
    fi
else
    echo "      ℹ️  No session files found"
fi

echo ""
echo -e "${GREEN}✅ Sanitization complete!${NC}"
echo ""
echo -e "${YELLOW}⚠️  Manual review still required:${NC}"
echo ""
echo "CRITICAL:"
echo "  1. CLAUDE.md - Replace /Users/bruno/ with generic paths"
echo "  2. terry/features/vision/camera_vision.py - Use environment variables"
echo "  3. Review files containing 'bruno' or 'Bruno'"
echo "  4. Replace IP addresses (192.168.x.x) with placeholders"
echo ""
echo "RECOMMENDED:"
echo "  5. Create LICENSE file"
echo "  6. Update README.md for public audience"
echo "  7. Review archived session documentation"
echo "  8. Create CONTRIBUTING.md if accepting PRs"
echo ""
echo "Next steps:"
echo "  1. Review GITHUB_PUBLICATION_AUDIT.md"
echo "  2. Complete manual sanitization tasks above"
echo "  3. Run: git status"
echo "  4. Review changes before committing"
echo ""
echo -e "${BLUE}Run './scripts/verify_sanitization.sh' to check for remaining issues${NC}"
