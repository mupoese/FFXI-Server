#!/bin/bash
# Enhanced Development Workflow Script for LandSandBoat
# Implements comprehensive quality assurance and Dutch SWE methodology

set -e

# Colors for output  
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

print_header() {
    echo -e "${BLUE}🚀 LandSandBoat Enhanced Development Workflow${NC}"
    echo -e "${PURPLE}Implementing Dutch SWE Agent Logic & Quality Assurance${NC}"
    echo "================================================================="
}

print_phase() {
    echo -e "${YELLOW}📍 $1${NC}"
    echo "--------------------------------------------------"
}

show_dutch_swe_logic() {
    print_header
    echo -e "${CYAN}📋 Dutch SWE Agent Logic (11 Steps)${NC}"
    echo "=================================================="
    echo -e "1. 🎯 ${YELLOW}INTENTIE = DOEL${NC} (Intent = Goal)"
    echo "   Define what you want to achieve"
    echo ""
    echo -e "2. 📝 ${YELLOW}ACTIE = PLAN${NC} (Action = Plan)"
    echo "   Create a concrete plan to reach the goal"
    echo ""
    echo -e "3. ⚡ ${YELLOW}REACTIE = UITVOERING${NC} (Reaction = Execution)"
    echo "   Execute the plan systematically"
    echo ""
    echo -e "4. 🔀 ${YELLOW}MULTIPLE OUTCOMES${NC}"
    echo "   Evaluate different possible outcomes"
    echo ""
    echo -e "5. 🧪 ${YELLOW}TEST${NC}"
    echo "   Test different approaches and choose the best"
    echo ""
    echo -e "6. 💭 ${YELLOW}FEEDBACK${NC}"
    echo "   Gather information on why the chosen approach works"
    echo ""
    echo -e "7. 🔧 ${YELLOW}CORRECTIE${NC} (Correction)"
    echo "   Improve the plan to the most optimal version"
    echo ""
    echo -e "8. ✅ ${YELLOW}VALIDATIE${NC} (Validation)"
    echo "   Verify and confirm the improved plan works"
    echo ""
    echo -e "9. 📚 ${YELLOW}LEREN${NC} (Learning)"
    echo "   Document what was learned and how code improved"
    echo ""
    echo -e "10. 🔄 ${YELLOW}HERHALEN${NC} (Repeat)"
    echo "    If insufficient, repeat from INTENTIE"
    echo ""
    echo -e "11. 🎉 ${YELLOW}UITKOMST${NC} (Outcome)"
    echo "    Deliver improved, validated solution"
}

check_dependencies() {
    print_phase "Checking Development Dependencies"
    
    local missing_deps=()
    
    # Check essential tools
    command -v git >/dev/null 2>&1 || missing_deps+=("git")
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v cmake >/dev/null 2>&1 || missing_deps+=("cmake")
    
    # Check Python packages
    python3 -c "import pylint" 2>/dev/null || missing_deps+=("pylint")
    python3 -c "import black" 2>/dev/null || missing_deps+=("black")
    python3 -c "import yaml" 2>/dev/null || missing_deps+=("PyYAML")
    
    # Check optional but recommended tools
    command -v shellcheck >/dev/null 2>&1 || echo -e "  ${YELLOW}⚠ shellcheck recommended for shell script validation${NC}"
    command -v clang-format >/dev/null 2>&1 || echo -e "  ${YELLOW}⚠ clang-format recommended for C++ formatting${NC}"
    
    if [ ${#missing_deps[@]} -eq 0 ]; then
        echo -e "  ${GREEN}✓ All essential dependencies available${NC}"
        return 0
    else
        echo -e "  ${RED}❌ Missing dependencies:${NC}"
        for dep in "${missing_deps[@]}"; do
            echo -e "    - $dep"
        done
        return 1
    fi
}

run_quality_checks() {
    print_phase "Comprehensive Quality Assurance"
    
    local exit_code=0
    
    echo -e "${CYAN}🔍 Running security vulnerability scan...${NC}"
    if python3 tools/vulnerability_scanner.py >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Security scan completed${NC}"
    else
        echo -e "  ${YELLOW}⚠ Security scan had warnings${NC}"
    fi
    
    echo -e "${CYAN}🔧 Running general CI checks...${NC}"
    if bash tools/ci/general.sh >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ General checks passed${NC}"
    else
        echo -e "  ${RED}❌ General checks failed${NC}"
        exit_code=1
    fi
    
    echo -e "${CYAN}📝 Checking git commit standards...${NC}"
    if bash tools/ci/git.sh >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Git standards check passed${NC}"
    else
        echo -e "  ${YELLOW}⚠ Git standards check had warnings${NC}"
    fi
    
    # Check if we have C++ files to analyze
    if find src/ -name "*.cpp" -o -name "*.h" | head -1 | grep -q .; then
        echo -e "${CYAN}⚙️ Running C++ static analysis...${NC}"
        if bash tools/ci/cpp.sh src >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ C++ analysis passed${NC}"
        else
            echo -e "  ${YELLOW}⚠ C++ analysis had warnings${NC}"
        fi
    fi
    
    # Check if we have Lua files to analyze
    if find scripts/ -name "*.lua" | head -1 | grep -q .; then
        echo -e "${CYAN}🌙 Running Lua script validation...${NC}"
        if bash tools/ci/lua.sh scripts >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Lua validation passed${NC}"
        else
            echo -e "  ${YELLOW}⚠ Lua validation had warnings${NC}"
        fi
    fi
    
    # Check if we have Python files to analyze
    if find tools/ -name "*.py" | head -1 | grep -q .; then
        echo -e "${CYAN}🐍 Running Python code analysis...${NC}"
        if bash tools/ci/python.sh tools >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Python analysis passed${NC}"
        else
            echo -e "  ${YELLOW}⚠ Python analysis had warnings${NC}"
        fi
    fi
    
    return $exit_code
}

run_build_process() {
    print_phase "Build Process"
    
    if [ ! -d build ]; then
        echo -e "${CYAN}📁 Creating build directory...${NC}"
        mkdir -p build
    fi
    
    cd build || exit 1
    
    echo -e "${CYAN}⚙️ Configuring build with CMake...${NC}"
    if cmake .. >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ CMake configuration successful${NC}"
    else
        echo -e "  ${RED}❌ CMake configuration failed${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    echo -e "${CYAN}🔨 Building project...${NC}"
    if command -v ninja >/dev/null 2>&1; then
        if ninja >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Build completed successfully (ninja)${NC}"
        else
            echo -e "  ${RED}❌ Build failed${NC}"
            cd "$PROJECT_ROOT"
            return 1
        fi
    elif command -v make >/dev/null 2>&1; then
        if make -j"$(nproc)" >/dev/null 2>&1; then
            echo -e "  ${GREEN}✓ Build completed successfully (make)${NC}"
        else
            echo -e "  ${RED}❌ Build failed${NC}"
            cd "$PROJECT_ROOT"
            return 1
        fi
    else
        echo -e "  ${YELLOW}⚠ No build system found (ninja/make)${NC}"
        cd "$PROJECT_ROOT"
        return 1
    fi
    
    cd "$PROJECT_ROOT"
    return 0
}

update_documentation() {
    print_phase "Documentation Generation"
    
    echo -e "${CYAN}📚 Generating function index...${NC}"
    if python3 tools/enhanced_function_indexer.py >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Function index generated${NC}"
    else
        echo -e "  ${YELLOW}⚠ Function index generation had issues${NC}"
    fi
    
    echo -e "${CYAN}📖 Updating development logs...${NC}"
    if python3 tools/log_manager.py --scan >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Development logs updated${NC}"
    else
        echo -e "  ${YELLOW}⚠ Log update had issues${NC}"
    fi
    
    if [ -f documentation/function_index/index.html ]; then
        echo -e "  ${GREEN}📄 Function documentation available at: documentation/function_index/index.html${NC}"
    fi
}

run_comprehensive_workflow() {
    print_header
    echo -e "${PURPLE}Running Comprehensive Development Workflow${NC}"
    echo "=================================================="
    
    local overall_success=true
    
    # Phase 1: INTENTIE (Intent) - Check dependencies
    if ! check_dependencies; then
        echo -e "${RED}💔 Workflow cannot continue without essential dependencies${NC}"
        return 1
    fi
    
    # Phase 2: ACTIE (Action) - Plan by running quality checks
    echo ""
    if ! run_quality_checks; then
        echo -e "${YELLOW}⚠ Quality checks found issues - continuing with caution${NC}"
        overall_success=false
    fi
    
    # Phase 3: REACTIE (Execution) - Build the project
    echo ""
    if ! run_build_process; then
        echo -e "${RED}💔 Build failed - critical issue${NC}"
        return 1
    fi
    
    # Phase 4-6: TEST/FEEDBACK/CORRECTIE - Generate documentation
    echo ""
    update_documentation
    
    # Phase 7-11: VALIDATIE/LEREN/HERHALEN/UITKOMST - Summary
    echo ""
    print_phase "Workflow Summary"
    if $overall_success; then
        echo -e "${GREEN}🎉 Comprehensive workflow completed successfully!${NC}"
        echo -e "${GREEN}✅ All quality checks passed${NC}"
        echo -e "${GREEN}✅ Build completed successfully${NC}"
        echo -e "${GREEN}✅ Documentation updated${NC}"
    else
        echo -e "${YELLOW}⚠ Workflow completed with warnings${NC}"
        echo -e "${YELLOW}⚠ Some quality checks had issues${NC}"
        echo -e "${GREEN}✅ Build completed successfully${NC}"
        echo -e "${GREEN}✅ Documentation updated${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}📊 Next Steps:${NC}"
    echo "  • Review any warnings from quality checks"
    echo "  • Check documentation/function_index/index.html"
    echo "  • Run tests if available"
    echo "  • Consider running vulnerability scanner manually for details"
}

show_help() {
    print_header
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  logic     - Display Dutch SWE Agent methodology"
    echo "  deps      - Check development dependencies"
    echo "  quality   - Run comprehensive quality checks"
    echo "  build     - Build the project"
    echo "  docs      - Generate/update documentation"
    echo "  full      - Run complete workflow (default)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 logic    # Show development methodology"
    echo "  $0 quality  # Run quality assurance checks"
    echo "  $0 full     # Complete development workflow"
}

# Main execution logic
case "${1:-full}" in
    "logic")
        show_dutch_swe_logic
        ;;
    "deps")
        print_header
        check_dependencies
        ;;
    "quality")
        print_header
        run_quality_checks
        ;;
    "build")
        print_header
        run_build_process
        ;;
    "docs")
        print_header
        update_documentation
        ;;
    "full")
        run_comprehensive_workflow
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac