#!/bin/bash
# LandSandBoat Development Workflow Integration Script
# Integrates the Dutch SWE agent logic with existing development tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

print_header() {
    echo -e "${BLUE}🚀 LandSandBoat Development Workflow${NC}"
    echo -e "${BLUE}Enhanced with Dutch SWE Agent Logic${NC}"
    echo "=================================================="
}

print_phase() {
    echo -e "${YELLOW}📍 Phase: $1${NC}"
    echo "--------------------------------------------------"
}

log_prompt_phase() {
    local phase="$1"
    local description="$2"
    local improvements="$3"
    
    if [[ -f "$PROJECT_ROOT/tools/log_manager.py" ]]; then
        python3 "$PROJECT_ROOT/tools/log_manager.py" --log-prompt "$phase" "$description" "$improvements" 2>/dev/null || true
    fi
}

run_quality_checks() {
    print_phase "8. VALIDATIE (Validation)"
    echo "Running quality assurance checks..."
    
    # Run vulnerability scanner
    if [[ -f "$PROJECT_ROOT/tools/vulnerability_scanner.py" ]]; then
        echo -e "${BLUE}🔍 Security Vulnerability Scan${NC}"
        python3 "$PROJECT_ROOT/tools/vulnerability_scanner.py" || echo -e "${YELLOW}⚠ Vulnerabilities detected - review required${NC}"
    fi
    
    # Run existing CI checks if available
    echo -e "${BLUE}🔧 Code Quality Checks${NC}"
    
    # C++ checks
    if [[ -f "$PROJECT_ROOT/tools/ci/cpp.sh" ]]; then
        echo "Running C++ static analysis..."
        bash "$PROJECT_ROOT/tools/ci/cpp.sh" src || echo -e "${YELLOW}⚠ C++ issues detected${NC}"
    fi
    
    # Lua checks
    if [[ -f "$PROJECT_ROOT/tools/ci/lua.sh" ]]; then
        echo "Running Lua checks..."
        bash "$PROJECT_ROOT/tools/ci/lua.sh" scripts || echo -e "${YELLOW}⚠ Lua issues detected${NC}"
    fi
    
    # Shell script checks are included in vulnerability scanner
    
    # License header checks
    if [[ -f "$PROJECT_ROOT/tools/ci/detect_license_headers.py" ]]; then
        echo "Checking license headers..."
        python3 "$PROJECT_ROOT/tools/ci/detect_license_headers.py" || echo -e "${YELLOW}⚠ License header issues detected${NC}"
    fi
}

run_build_test() {
    print_phase "5. TEST"
    echo "Building and testing the project..."
    
    # Check if build directory exists
    if [[ -d "$PROJECT_ROOT/build" ]]; then
        echo "Build directory exists, running build..."
        cd "$PROJECT_ROOT/build"
        if command -v ninja >/dev/null 2>&1; then
            ninja || echo -e "${YELLOW}⚠ Build failed${NC}"
        elif command -v make >/dev/null 2>&1; then
            make -j$(nproc) || echo -e "${YELLOW}⚠ Build failed${NC}"
        else
            echo -e "${YELLOW}⚠ No build system found${NC}"
        fi
        cd "$PROJECT_ROOT"
    else
        echo -e "${YELLOW}⚠ No build directory found. Run cmake to configure build.${NC}"
    fi
}

update_logs() {
    print_phase "9. LEREN (Learning)"
    echo "Updating development logs..."
    
    if [[ -f "$PROJECT_ROOT/tools/log_manager.py" ]]; then
        python3 "$PROJECT_ROOT/tools/log_manager.py" --validate
    fi
}

show_swe_logic() {
    echo -e "${BLUE}📋 Dutch SWE Agent Logic (11 Steps)${NC}"
    echo "=================================================="
    echo "1. 🎯 INTENTIE = DOEL (Intent = Goal)"
    echo "   Define what you want to achieve"
    echo ""
    echo "2. 📝 ACTIE = PLAN (Action = Plan)" 
    echo "   Create a concrete plan to reach the goal"
    echo ""
    echo "3. ⚡ REACTIE = UITVOERING (Reaction = Execution)"
    echo "   Execute the plan systematically"
    echo ""
    echo "4. 🔀 MULTIPLE OUTCOMES"
    echo "   Evaluate different possible outcomes"
    echo ""
    echo "5. 🧪 TEST"
    echo "   Test different approaches and choose the best"
    echo ""
    echo "6. 💭 FEEDBACK"
    echo "   Gather information on why the chosen approach works"
    echo ""
    echo "7. 🔧 CORRECTIE (Correction)"
    echo "   Improve the plan to the most optimal version"
    echo ""
    echo "8. ✅ VALIDATIE (Validation)"
    echo "   Verify and confirm the improved plan works"
    echo ""
    echo "9. 📚 LEREN (Learning)"
    echo "   Document what was learned and how code improved"
    echo ""
    echo "10. 🔄 HERHALEN (Repeat)"
    echo "    If insufficient, repeat from INTENTIE"
    echo ""
    echo "11. 🎉 UITKOMST (Outcome)"
    echo "    Deliver improved, validated solution"
    echo ""
}

check_dependencies() {
    echo -e "${BLUE}🔍 Checking Development Dependencies${NC}"
    
    local missing_deps=()
    
    # Check Python tools
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi
    
    # Check build tools
    if ! command -v cmake >/dev/null 2>&1; then
        missing_deps+=("cmake")
    fi
    
    # Check optional tools
    if ! command -v shellcheck >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠ shellcheck not found - install for better script validation${NC}"
    fi
    
    if ! python3 -c "import pip_audit" 2>/dev/null; then
        echo -e "${YELLOW}⚠ pip-audit not found - install for vulnerability scanning: pip install pip-audit${NC}"
    fi
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo -e "${RED}❌ Missing required dependencies: ${missing_deps[*]}${NC}"
        return 1
    else
        echo -e "${GREEN}✅ All required dependencies found${NC}"
        return 0
    fi
}

show_help() {
    echo "LandSandBoat Development Workflow Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  logic        Show the 11-step Dutch SWE agent logic"
    echo "  deps         Check development dependencies"
    echo "  quality      Run quality assurance checks"
    echo "  build        Build and test the project"
    echo "  logs         Update and validate development logs"
    echo "  full         Run complete workflow (quality + build + logs)"
    echo "  help         Show this help message"
    echo ""
    echo "Integration with existing tools:"
    echo "  - Vulnerability scanning with custom scanner"
    echo "  - Code quality checks using existing CI tools"
    echo "  - Development logging and tracking"
    echo "  - License compliance verification"
    echo ""
}

main() {
    local command="${1:-help}"
    
    case "$command" in
        "logic")
            show_swe_logic
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
            run_build_test
            ;;
        "logs")
            print_header
            update_logs
            ;;
        "full")
            print_header
            if check_dependencies; then
                run_quality_checks
                echo ""
                run_build_test
                echo ""
                update_logs
                echo ""
                echo -e "${GREEN}✅ Complete workflow finished${NC}"
            else
                echo -e "${RED}❌ Cannot continue - missing dependencies${NC}"
                exit 1
            fi
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Only run main if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi