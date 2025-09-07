#!/usr/bin/env python3
"""
Developer Productivity Suite for FFXI-Server
Enhanced debugging and development tools with comprehensive automation.

This tool provides advanced debugging capabilities, code analysis, development
workflow automation, and productivity enhancements specifically designed for
FFXI server development following modern C++20 practices.
"""

import os
import sys
import json
import subprocess
import re
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import argparse
import shutil

@dataclass
class CodeIssue:
    """Code issue data structure"""
    file_path: str
    line_number: int
    issue_type: str
    severity: str  # info, warning, error, critical
    message: str
    suggestion: str = ""
    auto_fixable: bool = False
    tool: str = ""

@dataclass
class BuildResult:
    """Build result information"""
    success: bool
    duration_seconds: float
    warnings: List[str]
    errors: List[str]
    output: str
    build_type: str

class DeveloperProductivitySuite:
    """Advanced developer productivity and debugging tools"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).absolute()
        self.config = self.load_config()
        self.issues = []
        self.build_cache = {}
        
        # Tool availability
        self.available_tools = self.check_tool_availability()
        
        # File patterns
        self.cpp_extensions = {'.cpp', '.hpp', '.h', '.cc', '.cxx', '.hxx'}
        self.lua_extensions = {'.lua'}
        self.python_extensions = {'.py'}
        
        # Modern C++20 patterns to check for
        self.cpp20_features = {
            'concepts': r'\b(?:concept|requires)\b',
            'coroutines': r'\b(?:co_await|co_yield|co_return)\b',
            'modules': r'\b(?:module|import)\b',
            'ranges': r'std::ranges::|std::views::|ranges::|views::',
            'format': r'std::format\(',
            'span': r'std::span<',
            'string_view': r'std::string_view',
            'optional': r'std::optional<',
            'variant': r'std::variant<',
            'any': r'std::any',
            'constexpr_if': r'if\s+constexpr',
            'structured_bindings': r'auto\s*\[[^]]+\]\s*=',
            'init_if': r'if\s*\([^;]+;[^)]+\)',
            'init_switch': r'switch\s*\([^;]+;[^)]+\)'
        }

    def load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        config_path = self.root_dir / "dev_productivity_config.json"
        default_config = {
            "auto_fix_enabled": True,
            "parallel_builds": True,
            "max_parallel_jobs": 4,
            "enable_all_warnings": True,
            "treat_warnings_as_errors": False,
            "enable_static_analysis": True,
            "enable_format_check": True,
            "enable_modern_cpp_suggestions": True,
            "build_types": ["Debug", "Release"],
            "skip_directories": ["build", "ext", ".git", "node_modules"],
            "notification_level": "warning"
        }
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config

    def check_tool_availability(self) -> Dict[str, bool]:
        """Check availability of development tools"""
        tools = {}
        
        # Build tools
        tools['cmake'] = shutil.which('cmake') is not None
        tools['make'] = shutil.which('make') is not None
        tools['ninja'] = shutil.which('ninja') is not None
        
        # Compilers
        tools['gcc'] = shutil.which('gcc') is not None
        tools['clang'] = shutil.which('clang') is not None
        tools['clang++'] = shutil.which('clang++') is not None
        
        # Static analysis
        tools['clang-tidy'] = shutil.which('clang-tidy') is not None
        tools['cppcheck'] = shutil.which('cppcheck') is not None
        tools['clang-format'] = shutil.which('clang-format') is not None
        
        # Debug tools
        tools['gdb'] = shutil.which('gdb') is not None
        tools['lldb'] = shutil.which('lldb') is not None
        tools['valgrind'] = shutil.which('valgrind') is not None
        
        # Other tools
        tools['git'] = shutil.which('git') is not None
        tools['ccache'] = shutil.which('ccache') is not None
        
        return tools

    def run_enhanced_build(self, build_type: str = "Debug", clean: bool = False) -> BuildResult:
        """Run enhanced build with comprehensive error checking"""
        print(f"🔧 Running enhanced {build_type} build...")
        
        build_dir = self.root_dir / "build" / build_type.lower()
        build_dir.mkdir(parents=True, exist_ok=True)
        
        start_time = time.time()
        warnings = []
        errors = []
        all_output = []
        
        try:
            # Clean if requested
            if clean and build_dir.exists():
                shutil.rmtree(build_dir)
                build_dir.mkdir(parents=True, exist_ok=True)
            
            # Configure CMake
            cmake_args = [
                "cmake",
                "-S", str(self.root_dir),
                "-B", str(build_dir),
                f"-DCMAKE_BUILD_TYPE={build_type}",
                "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"
            ]
            
            # Enable additional warnings
            if self.config.get("enable_all_warnings", True):
                cmake_args.extend([
                    "-DCMAKE_CXX_FLAGS=-Wall -Wextra -Wpedantic"
                ])
            
            # Treat warnings as errors if configured
            if self.config.get("treat_warnings_as_errors", False):
                cmake_args.append("-DCMAKE_CXX_FLAGS_INIT=-Werror")
            
            # Use ccache if available
            if self.available_tools.get('ccache', False):
                cmake_args.extend([
                    "-DCMAKE_CXX_COMPILER_LAUNCHER=ccache"
                ])
            
            print(f"Configuring: {' '.join(cmake_args)}")
            result = subprocess.run(cmake_args, capture_output=True, text=True, cwd=build_dir)
            all_output.append(f"=== CMAKE CONFIGURE ===\n{result.stdout}\n{result.stderr}")
            
            if result.returncode != 0:
                errors.append(f"CMake configuration failed: {result.stderr}")
                return BuildResult(False, time.time() - start_time, warnings, errors, 
                                 '\n'.join(all_output), build_type)
            
            # Build
            build_args = ["cmake", "--build", str(build_dir)]
            
            if self.config.get("parallel_builds", True):
                jobs = self.config.get("max_parallel_jobs", 4)
                build_args.extend(["--parallel", str(jobs)])
            
            print(f"Building: {' '.join(build_args)}")
            result = subprocess.run(build_args, capture_output=True, text=True)
            all_output.append(f"=== BUILD ===\n{result.stdout}\n{result.stderr}")
            
            # Parse output for warnings and errors
            for line in result.stderr.split('\n'):
                if 'warning:' in line.lower():
                    warnings.append(line.strip())
                elif 'error:' in line.lower():
                    errors.append(line.strip())
            
            success = result.returncode == 0 and len(errors) == 0
            duration = time.time() - start_time
            
            build_result = BuildResult(success, duration, warnings, errors, 
                                     '\n'.join(all_output), build_type)
            
            # Cache successful builds
            if success:
                self.build_cache[build_type] = build_result
            
            print(f"✅ Build {'succeeded' if success else 'failed'} in {duration:.2f}s")
            print(f"📊 {len(warnings)} warnings, {len(errors)} errors")
            
            return build_result
            
        except Exception as e:
            errors.append(f"Build exception: {str(e)}")
            return BuildResult(False, time.time() - start_time, warnings, errors, 
                             '\n'.join(all_output), build_type)

    def run_static_analysis(self) -> List[CodeIssue]:
        """Run comprehensive static analysis"""
        print("🔍 Running static analysis...")
        issues = []
        
        # Find C++ files
        cpp_files = []
        for ext in self.cpp_extensions:
            cpp_files.extend(self.root_dir.glob(f"**/*{ext}"))
        
        # Filter out skip directories
        skip_dirs = self.config.get("skip_directories", [])
        cpp_files = [f for f in cpp_files if not any(skip in str(f) for skip in skip_dirs)]
        
        print(f"Analyzing {len(cpp_files)} C++ files...")
        
        # Run clang-tidy
        if self.available_tools.get('clang-tidy', False):
            issues.extend(self.run_clang_tidy(cpp_files))
        
        # Run cppcheck
        if self.available_tools.get('cppcheck', False):
            issues.extend(self.run_cppcheck(cpp_files))
        
        # Check for modern C++20 usage opportunities
        if self.config.get("enable_modern_cpp_suggestions", True):
            issues.extend(self.suggest_modern_cpp_improvements(cpp_files))
        
        # Format checking
        if self.available_tools.get('clang-format', False) and self.config.get("enable_format_check", True):
            issues.extend(self.check_formatting(cpp_files))
        
        print(f"📋 Found {len(issues)} code issues")
        self.issues.extend(issues)
        
        return issues

    def run_clang_tidy(self, files: List[Path]) -> List[CodeIssue]:
        """Run clang-tidy analysis"""
        issues = []
        
        # Check if compile_commands.json exists
        compile_commands = self.root_dir / "build" / "compile_commands.json"
        if not compile_commands.exists():
            # Try to generate it
            build_result = self.run_enhanced_build("Debug")
            if not build_result.success:
                return issues
        
        print("Running clang-tidy...")
        
        # Run clang-tidy on a subset of files to avoid overwhelming output
        sample_files = files[:20] if len(files) > 20 else files
        
        for file_path in sample_files:
            try:
                result = subprocess.run([
                    "clang-tidy",
                    str(file_path),
                    f"-p={self.root_dir / 'build'}",
                    "--quiet"
                ], capture_output=True, text=True, timeout=30)
                
                # Parse clang-tidy output
                for line in result.stdout.split('\n'):
                    if ':' in line and ('warning:' in line or 'error:' in line):
                        parts = line.split(':', 3)
                        if len(parts) >= 4:
                            file_part = parts[0]
                            line_num = parts[1]
                            severity = 'warning' if 'warning:' in line else 'error'
                            message = parts[3].strip()
                            
                            issues.append(CodeIssue(
                                file_path=file_part,
                                line_number=int(line_num) if line_num.isdigit() else 0,
                                issue_type='static_analysis',
                                severity=severity,
                                message=message,
                                tool='clang-tidy'
                            ))
                            
            except (subprocess.TimeoutExpired, Exception) as e:
                print(f"Error running clang-tidy on {file_path}: {e}")
        
        return issues

    def run_cppcheck(self, files: List[Path]) -> List[CodeIssue]:
        """Run cppcheck analysis"""
        issues = []
        
        print("Running cppcheck...")
        
        try:
            # Run cppcheck on source directory
            result = subprocess.run([
                "cppcheck",
                "--enable=all",
                "--inconclusive",
                "--std=c++20",
                "--suppress=missingIncludeSystem",
                "--suppress=unusedFunction",
                "--quiet",
                str(self.root_dir / "src")
            ], capture_output=True, text=True, timeout=60)
            
            # Parse cppcheck output
            for line in result.stderr.split('\n'):
                if ':' in line and ('error' in line or 'warning' in line or 'style' in line):
                    # Parse cppcheck format: [file:line]: (severity) message
                    match = re.match(r'\[([^:]+):(\d+)\]:\s*\(([^)]+)\)\s*(.*)', line)
                    if match:
                        file_path, line_num, severity, message = match.groups()
                        
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=int(line_num),
                            issue_type='static_analysis',
                            severity=severity,
                            message=message,
                            tool='cppcheck'
                        ))
                        
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"Error running cppcheck: {e}")
        
        return issues

    def suggest_modern_cpp_improvements(self, files: List[Path]) -> List[CodeIssue]:
        """Suggest modern C++20 improvements"""
        issues = []
        
        print("Analyzing for modern C++20 opportunities...")
        
        # Patterns to look for and suggest improvements
        improvement_patterns = {
            r'\bstd::make_unique<': {
                'suggestion': 'Consider using std::make_unique for exception safety',
                'modern_feature': 'smart_pointers'
            },
            r'\bstd::shared_ptr<.*>\s*\(new\b': {
                'suggestion': 'Use std::make_shared instead of std::shared_ptr(new ...)',
                'modern_feature': 'smart_pointers'
            },
            r'\bfor\s*\(\s*auto\s+[^:]+:[^)]+\)': {
                'suggestion': 'Good use of range-based for loop',
                'modern_feature': 'range_for'
            },
            r'\bauto\s+[^=]+=.*->': {
                'suggestion': 'Consider using auto with trailing return type',
                'modern_feature': 'auto_deduction'
            }
        }
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Check for C++20 feature usage
                cpp20_usage = {}
                for feature, pattern in self.cpp20_features.items():
                    if re.search(pattern, content):
                        cpp20_usage[feature] = True
                
                # Suggest improvements
                for i, line in enumerate(lines, 1):
                    for pattern, info in improvement_patterns.items():
                        if re.search(pattern, line):
                            issues.append(CodeIssue(
                                file_path=str(file_path.relative_to(self.root_dir)),
                                line_number=i,
                                issue_type='modernization',
                                severity='info',
                                message=info['suggestion'],
                                tool='modernization_analyzer'
                            ))
                
                # Suggest missing C++20 features
                if not cpp20_usage.get('string_view', False):
                    if 'std::string&' in content or 'const std::string&' in content:
                        issues.append(CodeIssue(
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=1,
                            issue_type='modernization',
                            severity='info',
                            message='Consider using std::string_view for read-only string parameters',
                            suggestion='Replace const std::string& with std::string_view where appropriate',
                            tool='modernization_analyzer'
                        ))
                
                if not cpp20_usage.get('optional', False):
                    if 'nullptr' in content or 'NULL' in content:
                        issues.append(CodeIssue(
                            file_path=str(file_path.relative_to(self.root_dir)),
                            line_number=1,
                            issue_type='modernization',
                            severity='info',
                            message='Consider using std::optional for nullable values',
                            suggestion='Use std::optional<T> instead of pointer for optional values',
                            tool='modernization_analyzer'
                        ))
                        
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return issues

    def check_formatting(self, files: List[Path]) -> List[CodeIssue]:
        """Check code formatting"""
        issues = []
        
        print("Checking code formatting...")
        
        for file_path in files[:10]:  # Limit to avoid too many issues
            try:
                # Check if file needs formatting
                result = subprocess.run([
                    "clang-format",
                    "--dry-run",
                    "--Werror",
                    str(file_path)
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    issues.append(CodeIssue(
                        file_path=str(file_path.relative_to(self.root_dir)),
                        line_number=1,
                        issue_type='formatting',
                        severity='warning',
                        message='File formatting does not match project style',
                        suggestion='Run clang-format to fix formatting',
                        auto_fixable=True,
                        tool='clang-format'
                    ))
                    
            except (subprocess.TimeoutExpired, Exception) as e:
                print(f"Error checking formatting for {file_path}: {e}")
        
        return issues

    def run_enhanced_debugging_session(self, executable: str, core_file: str = None) -> Dict[str, Any]:
        """Run enhanced debugging session with automatic analysis"""
        print(f"🐛 Starting enhanced debugging session for {executable}")
        
        debug_info = {
            'executable': executable,
            'debugger': 'gdb' if self.available_tools.get('gdb') else 'lldb',
            'analysis': {},
            'suggestions': []
        }
        
        if not self.available_tools.get('gdb') and not self.available_tools.get('lldb'):
            debug_info['error'] = 'No debugger available (gdb or lldb required)'
            return debug_info
        
        try:
            # Prepare debugging commands
            if core_file:
                debug_commands = [
                    f"file {executable}",
                    f"core {core_file}",
                    "bt",
                    "info registers",
                    "info locals",
                    "quit"
                ]
            else:
                debug_commands = [
                    f"file {executable}",
                    "run",
                    "bt",
                    "info breakpoints",
                    "quit"
                ]
            
            # Run debugger
            if self.available_tools.get('gdb'):
                debug_process = subprocess.Popen([
                    "gdb", "--batch", "--quiet"
                ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                debug_output, debug_error = debug_process.communicate('\n'.join(debug_commands))
                
                debug_info['output'] = debug_output
                debug_info['error_output'] = debug_error
                
                # Analyze crash patterns
                if 'Segmentation fault' in debug_output or 'SIGSEGV' in debug_output:
                    debug_info['analysis']['crash_type'] = 'segmentation_fault'
                    debug_info['suggestions'].append('Check for null pointer dereferences')
                    debug_info['suggestions'].append('Verify array bounds checking')
                
                if 'double free' in debug_output or 'heap corruption' in debug_output:
                    debug_info['analysis']['crash_type'] = 'heap_corruption'
                    debug_info['suggestions'].append('Check for double free() calls')
                    debug_info['suggestions'].append('Verify memory management consistency')
                
                # Extract stack trace
                stack_trace = []
                in_backtrace = False
                for line in debug_output.split('\n'):
                    if line.startswith('#'):
                        in_backtrace = True
                        stack_trace.append(line)
                    elif in_backtrace and not line.startswith('#'):
                        break
                
                debug_info['stack_trace'] = stack_trace
                
        except Exception as e:
            debug_info['error'] = f"Debug session failed: {e}"
        
        return debug_info

    def auto_fix_issues(self, issues: List[CodeIssue]) -> Dict[str, Any]:
        """Automatically fix issues where possible"""
        if not self.config.get("auto_fix_enabled", True):
            return {'fixed': 0, 'skipped': len(issues)}
        
        print("🔧 Auto-fixing issues...")
        
        fixed_count = 0
        skipped_count = 0
        
        for issue in issues:
            if not issue.auto_fixable:
                skipped_count += 1
                continue
            
            try:
                if issue.tool == 'clang-format' and issue.issue_type == 'formatting':
                    # Auto-fix formatting
                    result = subprocess.run([
                        "clang-format", "-i", issue.file_path
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        fixed_count += 1
                        print(f"✅ Fixed formatting in {issue.file_path}")
                    else:
                        skipped_count += 1
                
            except Exception as e:
                print(f"Error auto-fixing issue in {issue.file_path}: {e}")
                skipped_count += 1
        
        return {'fixed': fixed_count, 'skipped': skipped_count}

    def generate_development_report(self) -> Dict[str, Any]:
        """Generate comprehensive development report"""
        print("📊 Generating development report...")
        
        # Collect repository statistics
        cpp_files = list(self.root_dir.glob("**/*.cpp")) + list(self.root_dir.glob("**/*.hpp"))
        lua_files = list(self.root_dir.glob("**/*.lua"))
        python_files = list(self.root_dir.glob("**/*.py"))
        
        # Filter out skip directories
        skip_dirs = self.config.get("skip_directories", [])
        cpp_files = [f for f in cpp_files if not any(skip in str(f) for skip in skip_dirs)]
        lua_files = [f for f in lua_files if not any(skip in str(f) for skip in skip_dirs)]
        python_files = [f for f in python_files if not any(skip in str(f) for skip in skip_dirs)]
        
        # Count lines of code
        total_cpp_lines = sum(self.count_lines(f) for f in cpp_files)
        total_lua_lines = sum(self.count_lines(f) for f in lua_files)
        total_python_lines = sum(self.count_lines(f) for f in python_files)
        
        # Issue summary
        issue_summary = defaultdict(int)
        for issue in self.issues:
            issue_summary[issue.severity] += 1
        
        # Tool availability summary
        available_tools = [name for name, available in self.available_tools.items() if available]
        missing_tools = [name for name, available in self.available_tools.items() if not available]
        
        report = {
            'timestamp': time.time(),
            'repository_stats': {
                'cpp_files': len(cpp_files),
                'lua_files': len(lua_files),
                'python_files': len(python_files),
                'total_cpp_lines': total_cpp_lines,
                'total_lua_lines': total_lua_lines,
                'total_python_lines': total_python_lines,
                'total_lines': total_cpp_lines + total_lua_lines + total_python_lines
            },
            'tool_availability': {
                'available': available_tools,
                'missing': missing_tools,
                'coverage': len(available_tools) / len(self.available_tools) * 100
            },
            'code_quality': {
                'total_issues': len(self.issues),
                'issue_breakdown': dict(issue_summary),
                'auto_fixable_issues': sum(1 for issue in self.issues if issue.auto_fixable)
            },
            'build_cache': {
                'cached_builds': list(self.build_cache.keys()),
                'successful_builds': len(self.build_cache)
            },
            'recommendations': self.generate_recommendations()
        }
        
        return report

    def count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def generate_recommendations(self) -> List[str]:
        """Generate development recommendations"""
        recommendations = []
        
        # Tool recommendations
        if not self.available_tools.get('ccache'):
            recommendations.append("Install ccache to speed up compilation")
        
        if not self.available_tools.get('ninja'):
            recommendations.append("Install ninja for faster builds")
        
        if not self.available_tools.get('clang-tidy'):
            recommendations.append("Install clang-tidy for better static analysis")
        
        # Code quality recommendations
        error_count = sum(1 for issue in self.issues if issue.severity == 'error')
        warning_count = sum(1 for issue in self.issues if issue.severity == 'warning')
        
        if error_count > 0:
            recommendations.append(f"Address {error_count} error(s) in the codebase")
        
        if warning_count > 10:
            recommendations.append(f"Consider addressing {warning_count} warnings")
        
        # Build recommendations
        if not self.build_cache:
            recommendations.append("Run a test build to verify compilation")
        
        # Modern C++ recommendations
        modernization_issues = [i for i in self.issues if i.issue_type == 'modernization']
        if len(modernization_issues) > 5:
            recommendations.append("Consider modernizing code to use more C++20 features")
        
        return recommendations

    def save_report(self, report: Dict[str, Any], filename: str = "dev_productivity_report.json"):
        """Save development report to file"""
        report_path = self.root_dir / filename
        
        try:
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"📋 Development report saved to {report_path}")
            
        except Exception as e:
            print(f"Error saving report: {e}")

    def run_comprehensive_analysis(self):
        """Run comprehensive development analysis"""
        print("🚀 Starting comprehensive development analysis...")
        
        # Run static analysis
        self.run_static_analysis()
        
        # Try to build if not already cached
        if not self.build_cache:
            for build_type in self.config.get("build_types", ["Debug"]):
                build_result = self.run_enhanced_build(build_type)
                if not build_result.success:
                    print(f"❌ {build_type} build failed")
        
        # Auto-fix issues if enabled
        fix_results = self.auto_fix_issues(self.issues)
        print(f"🔧 Auto-fixed {fix_results['fixed']} issues, skipped {fix_results['skipped']}")
        
        # Generate and save report
        report = self.generate_development_report()
        self.save_report(report)
        
        # Print summary
        print("\n=== DEVELOPMENT ANALYSIS SUMMARY ===")
        print(f"📁 Code Files: {report['repository_stats']['cpp_files']} C++, "
              f"{report['repository_stats']['lua_files']} Lua, "
              f"{report['repository_stats']['python_files']} Python")
        print(f"📏 Total Lines: {report['repository_stats']['total_lines']:,}")
        print(f"🔧 Tool Coverage: {report['tool_availability']['coverage']:.1f}%")
        print(f"⚠️  Code Issues: {report['code_quality']['total_issues']} "
              f"({report['code_quality']['auto_fixable_issues']} auto-fixable)")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"   • {rec}")

def main():
    parser = argparse.ArgumentParser(description="Developer Productivity Suite")
    parser.add_argument("--root", default=".", help="Root directory to analyze")
    parser.add_argument("--build", choices=["Debug", "Release"], help="Run build")
    parser.add_argument("--clean", action="store_true", help="Clean build")
    parser.add_argument("--analyze", action="store_true", help="Run static analysis")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    parser.add_argument("--debug", help="Debug executable")
    parser.add_argument("--core", help="Core file for debugging")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive analysis")
    parser.add_argument("--report", help="Generate report to file")
    
    args = parser.parse_args()
    
    suite = DeveloperProductivitySuite(args.root)
    
    if args.comprehensive:
        suite.run_comprehensive_analysis()
    
    elif args.build:
        result = suite.run_enhanced_build(args.build, args.clean)
        print(f"Build {'succeeded' if result.success else 'failed'}")
        
        if result.warnings:
            print(f"\nWarnings ({len(result.warnings)}):")
            for warning in result.warnings[:5]:  # Show first 5
                print(f"  {warning}")
            if len(result.warnings) > 5:
                print(f"  ... and {len(result.warnings) - 5} more")
        
        if result.errors:
            print(f"\nErrors ({len(result.errors)}):")
            for error in result.errors[:5]:  # Show first 5
                print(f"  {error}")
            if len(result.errors) > 5:
                print(f"  ... and {len(result.errors) - 5} more")
    
    elif args.analyze:
        issues = suite.run_static_analysis()
        
        if args.fix:
            fix_results = suite.auto_fix_issues(issues)
            print(f"Auto-fixed {fix_results['fixed']} issues")
    
    elif args.debug:
        debug_info = suite.run_enhanced_debugging_session(args.debug, args.core)
        print(json.dumps(debug_info, indent=2))
    
    elif args.report:
        report = suite.generate_development_report()
        suite.save_report(report, args.report)
    
    else:
        print("No action specified. Use --help for options.")

if __name__ == "__main__":
    main()