#!/bin/bash

# Repository Cleanup and Organization Script
# Ensures clean and organized repository structure

echo "🧹 FFXI Server Repository Cleanup and Organization"
echo "================================================"

# Function to display status
show_status() {
    echo "✅ $1"
}

show_cleaning() {
    echo "🔧 $1"
}

# Remove temporary and backup files
show_cleaning "Removing temporary and backup files..."
find . -name "*.tmp" -type f -delete 2>/dev/null || true
find . -name "*.bak" -type f -delete 2>/dev/null || true
find . -name "*~" -type f -delete 2>/dev/null || true
find . -name ".DS_Store" -type f -delete 2>/dev/null || true
find . -name "*.swp" -type f -delete 2>/dev/null || true
find . -name "*.swo" -type f -delete 2>/dev/null || true

# Clean up log files in documentation
show_cleaning "Removing stale log files from documentation..."
rm -f ./documentation/MessageSystemIDs.log 2>/dev/null || true
rm -f ./documentation/message.log 2>/dev/null || true

# Remove empty directories (but preserve important ones)
show_cleaning "Removing empty directories..."
find . -type d -empty ! -path "./.git/*" ! -path "./build*" ! -path "./logs" ! -path "./log" -delete 2>/dev/null || true

# Organize file permissions
show_cleaning "Setting appropriate file permissions..."
find . -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
find . -type f -name "*.py" -exec chmod +x {} \; 2>/dev/null || true

# Ensure critical directories exist
show_cleaning "Ensuring critical directories exist..."
mkdir -p logs log
mkdir -p build
mkdir -p docs/reports
mkdir -p docs/systems
mkdir -p docs/operations
mkdir -p docs/development

# Validate and fix UTF-8 BOM issues in configuration files
show_cleaning "Fixing UTF-8 BOM issues in configuration files..."
for config_file in .clang-format .clang-tidy .github/codeql/codeql-config.yml; do
    if [ -f "$config_file" ]; then
        # Remove UTF-8 BOM if present
        sed -i '1s/^\xEF\xBB\xBF//' "$config_file" 2>/dev/null || true
    fi
done

# Organize development tools symlinks
show_cleaning "Ensuring development tool symlinks are correct..."
if [ ! -L "tools/generate_ipc_stubs.py" ] && [ -f "tools/development/generate_ipc_stubs.py" ]; then
    ln -sf development/generate_ipc_stubs.py tools/generate_ipc_stubs.py
fi

# Update .gitignore to prevent future clutter
show_cleaning "Updating .gitignore for better organization..."
cat >> .gitignore << 'EOF'

# Temporary files
*.tmp
*.bak
*~
*.swp
*.swo

# Build artifacts
build/
cmake-build-*/

# Logs
*.log
logs/*.log

# IDE files
.vscode/settings.json
.idea/

# OS specific
.DS_Store
Thumbs.db

# Cache directories
__pycache__/
*.pyc
*.pyo

EOF

# Sort and deduplicate .gitignore
if [ -f .gitignore ]; then
    sort .gitignore | uniq > .gitignore.tmp && mv .gitignore.tmp .gitignore
fi

# Validation checks
show_status "Repository cleanup completed!"
echo ""
echo "📊 Cleanup Summary:"
echo "==================="

# Count files by type
total_files=$(find . -type f ! -path "./.git/*" | wc -l)
cpp_files=$(find . -name "*.cpp" -o -name "*.hpp" -o -name "*.h" | wc -l)
lua_files=$(find . -name "*.lua" | wc -l)
sql_files=$(find . -name "*.sql" | wc -l)
py_files=$(find . -name "*.py" | wc -l)
md_files=$(find . -name "*.md" | wc -l)

echo "📁 Total files: $total_files"
echo "🔧 C++ files: $cpp_files"
echo "🌙 Lua files: $lua_files"
echo "🗃️  SQL files: $sql_files"
echo "🐍 Python files: $py_files"
echo "📖 Markdown files: $md_files"

echo ""
echo "🎯 Repository Organization Status:"
echo "================================="

# Check critical directories
check_dir() {
    if [ -d "$1" ]; then
        file_count=$(find "$1" -type f | wc -l)
        echo "✅ $1/ ($file_count files)"
    else
        echo "❌ $1/ (missing)"
    fi
}

check_dir "src"
check_dir "scripts"
check_dir "sql"
check_dir "tools"
check_dir "docs"
check_dir "documentation"
check_dir ".github/workflows"

echo ""
echo "🔍 Configuration File Status:"
echo "============================="

# Check configuration files
check_config() {
    if [ -f "$1" ]; then
        echo "✅ $1 (exists)"
    else
        echo "❌ $1 (missing)"
    fi
}

check_config ".clang-format"
check_config ".clang-tidy"
check_config "CMakeLists.txt"
check_config "docker-compose.yml"

echo ""
echo "🎉 Repository is now clean and organized!"
echo "All temporary files removed, permissions set, and structure validated."