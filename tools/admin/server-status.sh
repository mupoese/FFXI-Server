#!/bin/bash

# Simple Server Status Tool
set -euo pipefail

echo "📊 FFXI-Server Status"
echo "===================="
echo "  Build Status: $([ -d build ] && echo "✅ Built" || echo "❌ Not built")"
echo "  Configuration: $([ -f settings/main.conf ] && echo "✅ Configured" || echo "❌ Not configured")"
echo "  Database: $([ -f sql/char_stats.sql ] && echo "✅ Schema available" || echo "❌ Schema missing")"
echo ""
echo "Use ./tools/development/build.sh to build the project"
