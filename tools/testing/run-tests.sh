#!/bin/bash

# Simple Test Runner
set -euo pipefail

echo "🧪 Running Tests"
echo "================"

if [[ -d "build" ]]; then
    cd build
    echo "Running C++ tests..."
    ctest --output-on-failure --parallel 4
    cd ..
    echo "✅ Tests completed"
else
    echo "❌ Build directory not found. Run build script first."
    exit 1
fi
