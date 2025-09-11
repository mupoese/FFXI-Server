#!/bin/bash

# Repository Cleanup Script
# Removes redundant files and organizes repository structure

set -euo pipefail

echo "🧹 Starting Repository Cleanup"

# Remove duplicate or obsolete files
echo "🗑️  Removing obsolete files..."

# Remove backup files if they exist
find . -name "*.bak" -type f -delete 2>/dev/null || true
find . -name "*.orig" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true

# Clean up temporary files
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "Thumbs.db" -type f -delete 2>/dev/null || true

echo "✅ Obsolete files removed"

# Organize remaining files
echo "📁 Organizing remaining files..."

# Move any remaining documentation to docs/
for doc in *.md; do
    if [[ -f "$doc" && "$doc" != "README.md" && "$doc" != "README_ENHANCED.md" ]]; then
        mkdir -p docs/misc/
        mv "$doc" docs/misc/ 2>/dev/null || true
        echo "  📄 Moved $doc to docs/misc/"
    fi
done

# Create .gitignore additions for organized structure
cat >> .gitignore << 'GITIGNORE'

# Repository organization
/docs/generated/
/.github/workflows-backup/
/.github/workflows-optimized/

# Development artifacts
/tools/logs/
/tools/temp/
*.log.old

# Enhanced build artifacts
/build-*
/cmake-build-*
GITIGNORE

echo "✅ Repository structure organized"

echo ""
echo "🎉 Repository Cleanup Complete!"
echo "================================"
echo "✅ Obsolete files removed"
echo "✅ Documentation organized"
echo "✅ .gitignore updated"
echo ""
echo "📊 Repository is now clean and organized!"
