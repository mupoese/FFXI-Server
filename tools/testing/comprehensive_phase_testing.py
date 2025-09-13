#!/usr/bin/env python3
"""
Comprehensive Phase Testing for FFXI Server
Tests all development phases including AI systems, build validation, and integration testing
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class ComprehensivePhaseTest:
    def __init__(self):
        self.repo_root = Path('/home/runner/work/FFXI-Server/FFXI-Server')
        self.results = {
            'start_time': datetime.now().isoformat(),
            'phases': {},
            'overall_status': 'UNKNOWN',
            'issues_found': [],
            'fixes_applied': []
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, cmd: List[str], cwd: Path = None, timeout: int = 600) -> Dict[str, Any]:
        """Run command and return results"""
        if cwd is None:
            cwd = self.repo_root
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(cwd)
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Command timed out after {timeout} seconds',
                'command': ' '.join(cmd)
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'command': ' '.join(cmd)
            }

    def test_phase_1_ai_systems(self) -> Dict[str, Any]:
        """Test all AI systems from Iteration 13"""
        self.log("=" * 60)
        self.log("PHASE 1: AI SYSTEMS VALIDATION")
        self.log("=" * 60)
        
        phase_results = {
            'status': 'PASSED',
            'systems_tested': {},
            'issues': []
        }
        
        ai_systems = [
            'tools/admin/autonomous_system_manager.py',
            'tools/admin/ai_gamemaster.py', 
            'tools/admin/predictive_analytics.py',
            'tools/admin/intelligent_content_generator.py'
        ]
        
        for system_path in ai_systems:
            system_name = Path(system_path).stem
            self.log(f"Testing {system_name}...")
            
            full_path = self.repo_root / system_path
            if not full_path.exists():
                phase_results['issues'].append(f"AI system not found: {system_path}")
                phase_results['status'] = 'FAILED'
                continue
                
            # Test import and basic functionality
            test_cmd = ['python3', '-c', f'''
import sys
sys.path.append("/home/runner/work/FFXI-Server/FFXI-Server")
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("{system_name}", "{full_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(f"✅ {system_name}: Import successful")
    
    # Try to instantiate main class if available
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and attr_name.replace("_", "").lower() in "{system_name}".replace("_", "").lower():
            try:
                instance = attr()
                print(f"✅ {system_name}: Class instantiation successful")
                break
            except Exception as e:
                print(f"⚠️ {system_name}: Class instantiation failed: {{e}}")
                break
    else:
        print(f"ℹ️ {system_name}: No matching class found for instantiation")
        
except Exception as e:
    print(f"❌ {system_name}: Import failed: {{e}}")
    sys.exit(1)
''']
            
            result = self.run_command(test_cmd)
            phase_results['systems_tested'][system_name] = {
                'status': 'PASSED' if result['success'] else 'FAILED',
                'output': result['stdout'],
                'error': result['stderr']
            }
            
            if not result['success']:
                phase_results['issues'].append(f"{system_name}: {result['stderr']}")
                phase_results['status'] = 'FAILED'
                
        return phase_results

    def test_phase_2_system_validation(self) -> Dict[str, Any]:
        """Run comprehensive system validation"""
        self.log("=" * 60)
        self.log("PHASE 2: COMPREHENSIVE SYSTEM VALIDATION")
        self.log("=" * 60)
        
        validation_script = self.repo_root / 'tools' / 'comprehensive_system_validation.py'
        
        if not validation_script.exists():
            return {
                'status': 'FAILED',
                'error': 'Comprehensive system validation script not found'
            }
            
        result = self.run_command(['python3', str(validation_script)], timeout=900)
        
        return {
            'status': 'PASSED' if result['success'] else 'FAILED',
            'output': result['stdout'],
            'error': result['stderr'],
            'returncode': result['returncode']
        }

    def test_phase_3_build_validation(self) -> Dict[str, Any]:
        """Run build validation for all components"""
        self.log("=" * 60)
        self.log("PHASE 3: BUILD VALIDATION")
        self.log("=" * 60)
        
        phase_results = {
            'status': 'PASSED',
            'components': {},
            'issues': []
        }
        
        # Test each component
        components = [
            ('Python', 'tools/ci/python.sh', ['tools']),
            ('C++', 'tools/ci/cpp.sh', ['src']),
            ('Lua', 'tools/ci/lua.sh', []),
            ('SQL', 'tools/ci/sql.sh', []),
            ('General', 'tools/ci/general.sh', [])
        ]
        
        for component_name, script_path, args in components:
            self.log(f"Testing {component_name} build...")
            
            full_script_path = self.repo_root / script_path
            if not full_script_path.exists():
                phase_results['issues'].append(f"{component_name} CI script not found: {script_path}")
                phase_results['status'] = 'FAILED'
                continue
                
            cmd = ['bash', str(full_script_path)] + args
            result = self.run_command(cmd, timeout=1200)  # 20 minutes for builds
            
            phase_results['components'][component_name] = {
                'status': 'PASSED' if result['success'] else 'FAILED',
                'output': result['stdout'][-2000:] if result['stdout'] else '',  # Last 2000 chars
                'error': result['stderr'][-1000:] if result['stderr'] else '',   # Last 1000 chars
                'returncode': result['returncode']
            }
            
            if not result['success']:
                phase_results['issues'].append(f"{component_name} build failed with code {result['returncode']}")
                phase_results['status'] = 'FAILED'
                
        return phase_results

    def test_phase_4_integration(self) -> Dict[str, Any]:
        """Run integration tests"""
        self.log("=" * 60)
        self.log("PHASE 4: INTEGRATION TESTING")
        self.log("=" * 60)
        
        phase_results = {
            'status': 'PASSED',
            'tests': {},
            'issues': []
        }
        
        # Run master test coordinator
        master_test_script = self.repo_root / 'tools' / 'testing' / 'master_test_coordinator.py'
        if master_test_script.exists():
            self.log("Running master test coordinator...")
            result = self.run_command(['python3', str(master_test_script), '--verbose'], timeout=1800)
            
            phase_results['tests']['master_coordinator'] = {
                'status': 'PASSED' if result['success'] else 'FAILED',
                'output': result['stdout'][-2000:] if result['stdout'] else '',
                'error': result['stderr'][-1000:] if result['stderr'] else ''
            }
            
            if not result['success']:
                phase_results['issues'].append(f"Master test coordinator failed: {result['stderr']}")
                phase_results['status'] = 'FAILED'
        
        # Run integration testing report
        integration_script = self.repo_root / 'tools' / 'integration_testing_report.py'
        if integration_script.exists():
            self.log("Running integration testing report...")
            result = self.run_command(['python3', str(integration_script)], timeout=600)
            
            phase_results['tests']['integration_report'] = {
                'status': 'PASSED' if result['success'] else 'FAILED',
                'output': result['stdout'][-2000:] if result['stdout'] else '',
                'error': result['stderr'][-1000:] if result['stderr'] else ''
            }
            
            if not result['success']:
                phase_results['issues'].append(f"Integration testing report failed: {result['stderr']}")
                phase_results['status'] = 'FAILED'
                
        return phase_results

    def fix_identified_issues(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix identified issues"""
        self.log("=" * 60)
        self.log("PHASE 5: ISSUE RESOLUTION")
        self.log("=" * 60)
        
        fixes_applied = []
        
        # Check for common issues and apply fixes
        for phase_name, phase_result in all_results.items():
            if phase_name == 'overall_status':
                continue
                
            if isinstance(phase_result, dict) and phase_result.get('status') == 'FAILED':
                self.log(f"Analyzing issues in {phase_name}...")
                
                # Check for missing dependencies
                if 'issues' in phase_result:
                    for issue in phase_result['issues']:
                        if 'not found' in issue.lower() or 'missing' in issue.lower():
                            # Try to install missing dependencies
                            if 'python' in issue.lower():
                                self.log("Attempting to install Python dependencies...")
                                result = self.run_command(['pip3', 'install', '-r', 'tools/requirements.txt'])
                                if result['success']:
                                    fixes_applied.append("Installed Python dependencies")
                                    
                            elif 'clang-format' in issue.lower():
                                self.log("Attempting to install clang-format...")
                                result = self.run_command(['sudo', 'apt-get', 'update'])
                                if result['success']:
                                    result = self.run_command(['sudo', 'apt-get', 'install', '-y', 'clang-format'])
                                    if result['success']:
                                        fixes_applied.append("Installed clang-format")
                
                # Check build components for UTF-8 BOM issues
                if 'components' in phase_result:
                    for comp_name, comp_result in phase_result['components'].items():
                        if comp_result.get('status') == 'FAILED' and 'BOM' in comp_result.get('error', ''):
                            self.log(f"Fixing UTF-8 BOM issues for {comp_name}...")
                            # Remove BOM from .clang-format
                            bom_fix_cmd = ['sed', '-i', '1s/^\\xEF\\xBB\\xBF//', '.clang-format']
                            result = self.run_command(bom_fix_cmd)
                            if result['success']:
                                fixes_applied.append(f"Removed UTF-8 BOM from .clang-format")
        
        return {
            'fixes_applied': fixes_applied,
            'fix_count': len(fixes_applied)
        }

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all testing phases"""
        self.log("🚀 Starting Comprehensive Phase Testing for FFXI Server")
        self.log(f"Repository: {self.repo_root}")
        self.log(f"Start time: {self.results['start_time']}")
        
        # Phase 1: AI Systems
        self.results['phases']['phase_1_ai_systems'] = self.test_phase_1_ai_systems()
        
        # Phase 2: System Validation  
        self.results['phases']['phase_2_system_validation'] = self.test_phase_2_system_validation()
        
        # Phase 3: Build Validation
        self.results['phases']['phase_3_build_validation'] = self.test_phase_3_build_validation()
        
        # Phase 4: Integration Testing
        self.results['phases']['phase_4_integration'] = self.test_phase_4_integration()
        
        # Phase 5: Fix Issues
        fix_results = self.fix_identified_issues(self.results['phases'])
        self.results['fixes_applied'] = fix_results['fixes_applied']
        
        # Determine overall status
        failed_phases = []
        for phase_name, phase_result in self.results['phases'].items():
            if isinstance(phase_result, dict) and phase_result.get('status') == 'FAILED':
                failed_phases.append(phase_name)
                
        self.results['overall_status'] = 'FAILED' if failed_phases else 'PASSED'
        self.results['failed_phases'] = failed_phases
        self.results['end_time'] = datetime.now().isoformat()
        
        # Generate summary
        self.generate_summary()
        
        return self.results

    def generate_summary(self):
        """Generate test summary"""
        self.log("=" * 60)
        self.log("COMPREHENSIVE TESTING SUMMARY")
        self.log("=" * 60)
        
        self.log(f"Overall Status: {self.results['overall_status']}")
        self.log(f"Start Time: {self.results['start_time']}")
        self.log(f"End Time: {self.results['end_time']}")
        
        self.log("\nPhase Results:")
        for phase_name, phase_result in self.results['phases'].items():
            if isinstance(phase_result, dict):
                status = phase_result.get('status', 'UNKNOWN')
                self.log(f"  {phase_name}: {status}")
                
        if self.results['fixes_applied']:
            self.log(f"\nFixes Applied ({len(self.results['fixes_applied'])}):")
            for fix in self.results['fixes_applied']:
                self.log(f"  ✅ {fix}")
                
        if self.results.get('failed_phases'):
            self.log(f"\nFailed Phases ({len(self.results['failed_phases'])}):")
            for phase in self.results['failed_phases']:
                self.log(f"  ❌ {phase}")

def main():
    """Main function"""
    tester = ComprehensivePhaseTest()
    results = tester.run_comprehensive_test()
    
    # Save results to file
    results_file = Path('/home/runner/work/FFXI-Server/FFXI-Server/comprehensive_test_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📊 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_status'] == 'PASSED' else 1)

if __name__ == '__main__':
    main()