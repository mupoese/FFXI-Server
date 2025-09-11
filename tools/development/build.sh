#!/bin/bash

# Enhanced Build Script with Options
# Provides comprehensive build management for FFXI-Server

set -euo pipefail

# Default options
BUILD_TYPE="Debug"
PARALLEL_JOBS=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
CLEAN_BUILD=false
VERBOSE=false
ENABLE_TESTS=true
ENABLE_DOCS=false

show_help() {
    cat << 'HELP'
Enhanced Build Script for FFXI-Server

USAGE:
    $0 [OPTIONS]

OPTIONS:
    -t, --type TYPE        Build type: Debug, Release, RelWithDebInfo (default: Debug)
    -j, --jobs JOBS        Number of parallel jobs (default: auto-detected)
    -c, --clean            Clean build directory before building
    -v, --verbose          Enable verbose build output
    --no-tests             Disable test building
    --enable-docs          Enable documentation generation
    -h, --help             Show this help message

EXAMPLES:
    $0                     # Build with defaults
    $0 -t Release -j 8     # Release build with 8 parallel jobs
    $0 -c -v               # Clean verbose debug build
    $0 --type Release --enable-docs  # Release build with documentation
HELP
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            BUILD_TYPE="$2"
            shift 2
            ;;
        -j|--jobs)
            PARALLEL_JOBS="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN_BUILD=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-tests)
            ENABLE_TESTS=false
            shift
            ;;
        --enable-docs)
            ENABLE_DOCS=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo "🏗️ Enhanced Build Configuration"
echo "==============================="
echo "Build Type: $BUILD_TYPE"
echo "Parallel Jobs: $PARALLEL_JOBS"
echo "Clean Build: $CLEAN_BUILD"
echo "Verbose: $VERBOSE"
echo "Enable Tests: $ENABLE_TESTS"
echo "Enable Docs: $ENABLE_DOCS"
echo ""

# Clean build directory if requested
if [[ "$CLEAN_BUILD" == "true" ]]; then
    echo "🧹 Cleaning build directory..."
    rm -rf build/
fi

# Create build directory
mkdir -p build
cd build

# Configure CMake options
CMAKE_ARGS=(
    "-DCMAKE_BUILD_TYPE=$BUILD_TYPE"
    "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
)

if [[ "$ENABLE_TESTS" == "false" ]]; then
    CMAKE_ARGS+=("-DBUILD_TESTING=OFF")
fi

if [[ "$ENABLE_DOCS" == "true" ]]; then
    CMAKE_ARGS+=("-DBUILD_DOCUMENTATION=ON")
fi

# Set verbose flag for make
MAKE_ARGS=("--parallel" "$PARALLEL_JOBS")
if [[ "$VERBOSE" == "true" ]]; then
    MAKE_ARGS+=("VERBOSE=1")
fi

echo "⚙️ Configuring with CMake..."
cmake .. "${CMAKE_ARGS[@]}"

echo "🔨 Building project..."
cmake --build . "${MAKE_ARGS[@]}"

if [[ "$ENABLE_TESTS" == "true" ]]; then
    echo "🧪 Running tests..."
    ctest --output-on-failure --parallel "$PARALLEL_JOBS"
fi

echo ""
echo "✅ Build completed successfully!"
echo "Build artifacts are in: $(pwd)"
