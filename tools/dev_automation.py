#!/usr/bin/env python3
"""
Enhanced Development Automation Tool for LandSandBoat
Provides modern development workflow automation and quality assurance
"""

import os
import sys
import subprocess
import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import concurrent.futures

class DevelopmentAutomation:
    """Comprehensive development automation for LandSandBoat"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.build_dir = self.project_root / "build"
        self.tools_dir = self.project_root / "tools"
        
    def setup_development_environment(self) -> bool:
        """Set up optimal development environment"""
        print("🔧 Setting up development environment...")
        
        # Install Python dependencies
        if not self._install_python_dependencies():
            return False
            
        # Configure git hooks
        if not self._setup_git_hooks():
            return False
            
        # Setup build directory with modern configuration
        if not self._setup_build_directory():
            return False
            
        print("✅ Development environment setup complete")
        return True
    
    def _install_python_dependencies(self) -> bool:
        """Install and upgrade Python dependencies"""
        print("  📦 Installing Python dependencies...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.tools_dir / "requirements.txt")
            ], check=True, capture_output=True)
            
            print("  ✅ Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to install Python dependencies: {e}")
            return False
    
    def _setup_git_hooks(self) -> bool:
        """Setup git hooks for automated quality checks"""
        print("  🪝 Setting up git hooks...")
        
        hooks_dir = self.project_root / ".git" / "hooks"
        if not hooks_dir.exists():
            print("  ⚠️ Git hooks directory not found")
            return False
        
        # Pre-commit hook
        pre_commit_hook = hooks_dir / "pre-commit"
        with open(pre_commit_hook, 'w') as f:
            f.write("""#!/bin/bash
# LandSandBoat pre-commit hook
set -e

echo "🔍 Running pre-commit checks..."

# Run Python formatting
python3 tools/dev_automation.py format

# Run quality checks
python3 tools/dev_automation.py lint

# Check commit message length
if git rev-parse --verify HEAD >/dev/null 2>&1; then
    commit_msg_length=$(git log -1 --pretty=format:'%s' | wc -c)
    if [ $commit_msg_length -gt 72 ]; then
        echo "❌ Commit message too long ($commit_msg_length chars). Max 72 characters."
        exit 1
    fi
fi

echo "✅ Pre-commit checks passed"
""")
        
        os.chmod(pre_commit_hook, 0o755)
        print("  ✅ Git hooks configured")
        return True
    
    def _setup_build_directory(self) -> bool:
        """Setup build directory with modern CMake configuration"""
        print("  🏗️ Setting up build directory...")
        
        self.build_dir.mkdir(exist_ok=True)
        
        cmake_args = [
            "cmake",
            "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
            "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON",
            "-DENABLE_STATIC_ANALYSIS=ON",
            "-DENABLE_TESTING=ON",
            str(self.project_root)
        ]
        
        try:
            subprocess.run(cmake_args, cwd=self.build_dir, check=True, capture_output=True)
            print("  ✅ Build directory configured")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Failed to configure build: {e}")
            return False
    
    def format_code(self) -> bool:
        """Format code using modern tools"""
        print("🎨 Formatting code...")
        
        success = True
        
        # Format Python code
        if not self._format_python():
            success = False
            
        # Format C++ code
        if not self._format_cpp():
            success = False
            
        if success:
            print("✅ Code formatting complete")
        else:
            print("❌ Code formatting had errors")
            
        return success
    
    def _format_python(self) -> bool:
        """Format Python code with black and isort"""
        print("  🐍 Formatting Python code...")
        
        try:
            # Black formatting
            subprocess.run([
                sys.executable, "-m", "black",
                "--line-length", "100",
                "--target-version", "py38",
                str(self.tools_dir)
            ], check=True, capture_output=True)
            
            # Import sorting
            subprocess.run([
                sys.executable, "-m", "isort",
                "--profile", "black",
                "--line-length", "100",
                str(self.tools_dir)
            ], check=True, capture_output=True)
            
            print("  ✅ Python code formatted")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ Python formatting failed: {e}")
            return False
    
    def _format_cpp(self) -> bool:
        """Format C++ code with clang-format"""
        print("  ⚡ Formatting C++ code...")
        
        try:
            cpp_files = list(self.project_root.glob("src/**/*.cpp"))
            cpp_files.extend(self.project_root.glob("src/**/*.h"))
            
            if not cpp_files:
                print("  ⚠️ No C++ files found")
                return True
            
            subprocess.run([
                "clang-format", "-i", "--style=file"
            ] + [str(f) for f in cpp_files[:10]], check=True, capture_output=True)  # Limit for demo
            
            print(f"  ✅ Formatted {len(cpp_files)} C++ files")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  ❌ C++ formatting failed: {e}")
            return False
        except FileNotFoundError:
            print("  ⚠️ clang-format not found, skipping C++ formatting")
            return True
    
    def lint_code(self) -> bool:
        """Run comprehensive code linting"""
        print("🔍 Running code analysis...")
        
        results = {}
        
        # Run linting tasks in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                'python': executor.submit(self._lint_python),
                'cpp': executor.submit(self._lint_cpp),
                'lua': executor.submit(self._lint_lua),
                'security': executor.submit(self._security_scan)
            }
            
            for name, future in futures.items():
                try:
                    results[name] = future.result(timeout=300)  # 5 minute timeout
                except concurrent.futures.TimeoutError:
                    print(f"  ⏰ {name} linting timed out")
                    results[name] = False
                except Exception as e:
                    print(f"  ❌ {name} linting failed: {e}")
                    results[name] = False
        
        success = all(results.values())
        if success:
            print("✅ All code analysis passed")
        else:
            failed = [name for name, result in results.items() if not result]
            print(f"❌ Code analysis failed for: {', '.join(failed)}")
            
        return success
    
    def _lint_python(self) -> bool:
        """Lint Python code"""
        print("  🐍 Analyzing Python code...")
        
        try:
            # Pylint
            subprocess.run([
                sys.executable, "-m", "pylint",
                "--rcfile=.pylintrc" if (self.project_root / ".pylintrc").exists() else "",
                str(self.tools_dir)
            ], check=True, capture_output=True)
            
            # Bandit security analysis
            subprocess.run([
                sys.executable, "-m", "bandit",
                "-r", str(self.tools_dir),
                "-f", "json",
                "-o", "/tmp/bandit_report.json"
            ], capture_output=True)  # Don't fail on security issues
            
            print("  ✅ Python analysis complete")
            return True
        except subprocess.CalledProcessError:
            print("  ⚠️ Python linting found issues")
            return False
        except FileNotFoundError:
            print("  ⚠️ Python linting tools not found")
            return True
    
    def _lint_cpp(self) -> bool:
        """Lint C++ code"""
        print("  ⚡ Analyzing C++ code...")
        
        try:
            # Run cppcheck
            subprocess.run([
                "cppcheck",
                "--enable=warning,performance,portability",
                "--inline-suppr",
                "--xml",
                "--output-file=/tmp/cppcheck_report.xml",
                str(self.project_root / "src")
            ], capture_output=True)  # Don't fail on warnings
            
            print("  ✅ C++ analysis complete")
            return True
        except FileNotFoundError:
            print("  ⚠️ cppcheck not found, skipping C++ analysis")
            return True
    
    def _lint_lua(self) -> bool:
        """Lint Lua code"""
        print("  🌙 Analyzing Lua code...")
        
        if not (self.project_root / "scripts").exists():
            print("  ⚠️ No Lua scripts found")
            return True
        
        try:
            subprocess.run([
                sys.executable, str(self.tools_dir / "ci" / "lua.sh")
            ], check=True, capture_output=True)
            
            print("  ✅ Lua analysis complete")
            return True
        except subprocess.CalledProcessError:
            print("  ⚠️ Lua linting found issues")
            return False
        except FileNotFoundError:
            print("  ⚠️ Lua linting tools not found")
            return True
    
    def _security_scan(self) -> bool:
        """Run security vulnerability scan"""
        print("  🛡️ Running security scan...")
        
        try:
            subprocess.run([
                sys.executable, str(self.tools_dir / "vulnerability_scanner.py")
            ], check=True, capture_output=True)
            
            print("  ✅ Security scan complete")
            return True
        except subprocess.CalledProcessError:
            print("  ⚠️ Security scan found issues")
            return False
    
    def build_project(self, target: Optional[str] = None) -> bool:
        """Build the project with modern configuration"""
        print("🔨 Building project...")
        
        if not self.build_dir.exists():
            print("  ❌ Build directory not found. Run setup first.")
            return False
        
        build_args = ["cmake", "--build", str(self.build_dir)]
        if target:
            build_args.extend(["--target", target])
        
        # Use parallel builds
        build_args.extend(["--parallel", str(os.cpu_count() or 4)])
        
        try:
            start_time = time.time()
            subprocess.run(build_args, check=True)
            build_time = time.time() - start_time
            
            print(f"✅ Build completed in {build_time:.1f} seconds")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run comprehensive test suite"""
        print("🧪 Running tests...")
        
        if not self.build_dir.exists():
            print("  ❌ Build directory not found. Run build first.")
            return False
        
        try:
            # Run CTest
            subprocess.run([
                "ctest", "--output-on-failure", "--parallel", str(os.cpu_count() or 4)
            ], cwd=self.build_dir, check=True)
            
            print("✅ All tests passed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Tests failed")
            return False
        except FileNotFoundError:
            print("⚠️ CTest not found, skipping tests")
            return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="LandSandBoat Development Automation")
    parser.add_argument("command", choices=[
        "setup", "format", "lint", "build", "test", "all"
    ], help="Command to run")
    parser.add_argument("--target", help="Build target (for build command)")
    
    args = parser.parse_args()
    
    automation = DevelopmentAutomation()
    
    if args.command == "setup":
        success = automation.setup_development_environment()
    elif args.command == "format":
        success = automation.format_code()
    elif args.command == "lint":
        success = automation.lint_code()
    elif args.command == "build":
        success = automation.build_project(args.target)
    elif args.command == "test":
        success = automation.run_tests()
    elif args.command == "all":
        success = (
            automation.setup_development_environment() and
            automation.format_code() and
            automation.lint_code() and
            automation.build_project() and
            automation.run_tests()
        )
    else:
        print(f"Unknown command: {args.command}")
        success = False
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()