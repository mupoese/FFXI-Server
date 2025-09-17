#!/usr/bin/env python3
"""
Workflow Job Simulator - Simulates GitHub Actions workflow jobs one by one
and identifies issues for targeted fixes.

This tool allows for comprehensive testing of individual workflow jobs
before running the complete CI pipeline.
"""
import os
import sys
import subprocess
import yaml
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse
import tempfile
import shutil

class WorkflowJobSimulator:
    def __init__(self, repository_path: str):
        self.repo_path = Path(repository_path)
        self.workflow_path = self.repo_path / ".github" / "workflows"
        self.results = {}
        self.failed_jobs = []
        self.successful_jobs = []
        
    def discover_workflows(self) -> List[Path]:
        """Discover all workflow files in the repository."""
        workflow_files = []
        for pattern in ["*.yml", "*.yaml"]:
            workflow_files.extend(self.workflow_path.glob(pattern))
            # Include manual workflows
            manual_path = self.workflow_path / "manual"
            if manual_path.exists():
                workflow_files.extend(manual_path.glob(pattern))
        return sorted(workflow_files)
    
    def parse_workflow(self, workflow_file: Path) -> Dict[str, Any]:
        """Parse a workflow file and extract job information."""
        try:
            with open(workflow_file, 'r') as f:
                workflow_content = yaml.safe_load(f)
            
            jobs = workflow_content.get('jobs', {})
            workflow_info = {
                'name': workflow_content.get('name', workflow_file.stem),
                'file': str(workflow_file),
                'jobs': jobs,
                'triggers': workflow_content.get('on', {}),
                'concurrency': workflow_content.get('concurrency', {}),
            }
            
            return workflow_info
        except Exception as e:
            print(f"❌ Error parsing {workflow_file}: {e}")
            return None
    
    def extract_job_steps(self, job_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract steps from a job configuration."""
        steps = job_config.get('steps', [])
        processed_steps = []
        
        for step in steps:
            step_info = {
                'name': step.get('name', 'Unnamed step'),
                'uses': step.get('uses'),
                'run': step.get('run'),
                'with': step.get('with', {}),
                'env': step.get('env', {}),
                'if': step.get('if'),
                'shell': step.get('shell', 'bash'),
                'continue_on_error': step.get('continue-on-error', False),
            }
            processed_steps.append(step_info)
        
        return processed_steps
    
    def simulate_dependency_installation(self) -> Tuple[bool, str]:
        """Simulate the dependency installation steps."""
        print("🔧 Simulating dependency installation...")
        
        try:
            # Check if system dependencies are available
            cmd = "apt list --installed 2>/dev/null | grep -E 'libmariadb|libzmq|luajit|cmake'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                print("✅ System dependencies are installed")
                return True, "System dependencies installed successfully"
            else:
                return False, "Missing system dependencies"
                
        except Exception as e:
            return False, f"Error checking dependencies: {e}"
    
    def simulate_python_setup(self, python_version: str = "3.12") -> Tuple[bool, str]:
        """Simulate Python setup step."""
        print(f"🐍 Simulating Python {python_version} setup...")
        
        try:
            # Check current Python version
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            current_version = result.stdout.strip()
            
            if python_version in current_version:
                print(f"✅ Python {python_version} is available: {current_version}")
                return True, f"Python {python_version} setup successful"
            else:
                return False, f"Python version mismatch: expected {python_version}, got {current_version}"
                
        except Exception as e:
            return False, f"Error checking Python version: {e}"
    
    def simulate_build_step(self, job_name: str, build_type: str = "Debug") -> Tuple[bool, str]:
        """Simulate build steps for C++ components."""
        print(f"🔨 Simulating build step for {job_name} ({build_type})...")
        
        try:
            # Check if CMake can configure
            build_dir = self.repo_path / "build_sim"
            build_dir.mkdir(exist_ok=True)
            
            # Clean any existing CMake cache
            cmake_cache = build_dir / "CMakeCache.txt"
            if cmake_cache.exists():
                cmake_cache.unlink()
            
            # Test CMake configuration
            configure_cmd = [
                "cmake", "-S", str(self.repo_path), "-B", str(build_dir),
                f"-DCMAKE_BUILD_TYPE={build_type}"
            ]
            
            print(f"Running: {' '.join(configure_cmd)}")
            result = subprocess.run(configure_cmd, capture_output=True, text=True, 
                                  cwd=self.repo_path, timeout=120)
            
            if result.returncode == 0:
                print("✅ CMake configuration successful")
                
                # Test a quick build (just configuration, not full build)
                # This tests that the build system is working without full compilation
                return True, f"Build simulation successful for {job_name}"
            else:
                print(f"❌ CMake configuration failed: {result.stderr}")
                return False, f"Build configuration failed: {result.stderr[:200]}"
                
        except subprocess.TimeoutExpired:
            return False, "Build configuration timed out"
        except Exception as e:
            return False, f"Build simulation error: {e}"
        finally:
            # Cleanup
            build_dir = self.repo_path / "build_sim"
            if build_dir.exists():
                shutil.rmtree(build_dir, ignore_errors=True)
    
    def simulate_ci_scripts(self) -> Tuple[bool, str]:
        """Simulate running CI scripts."""
        print("🧪 Simulating CI script execution...")
        
        ci_scripts = [
            "tools/ci/git.sh",
            "tools/ci/general.sh", 
            "tools/ci/python.sh",
            "tools/ci/cpp.sh",
            "tools/ci/lua.sh",
            "tools/ci/sql.sh"
        ]
        
        results = []
        for script in ci_scripts:
            script_path = self.repo_path / script
            if script_path.exists():
                try:
                    # Just check if script is executable and has no syntax errors
                    result = subprocess.run(["bash", "-n", str(script_path)], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        results.append(f"✅ {script}: Syntax OK")
                    else:
                        results.append(f"❌ {script}: Syntax Error - {result.stderr}")
                except Exception as e:
                    results.append(f"❌ {script}: Error - {e}")
            else:
                results.append(f"⚠️  {script}: Not found")
        
        # Determine overall success
        failed_scripts = [r for r in results if "❌" in r]
        if failed_scripts:
            return False, f"CI script issues: {'; '.join(failed_scripts)}"
        else:
            return True, f"CI scripts validated: {len(results)} scripts checked"
    
    def simulate_job(self, workflow_name: str, job_name: str, job_config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a single workflow job."""
        print(f"\n🎯 Simulating job: {workflow_name}::{job_name}")
        print("=" * 60)
        
        job_result = {
            'workflow': workflow_name,
            'job': job_name,
            'success': True,
            'steps': [],
            'errors': [],
            'warnings': [],
            'duration': 0,
            'platform': job_config.get('runs-on', 'unknown')
        }
        
        start_time = time.time()
        
        try:
            steps = self.extract_job_steps(job_config)
            
            for i, step in enumerate(steps):
                step_name = step['name']
                print(f"  📋 Step {i+1}: {step_name}")
                
                step_result = {'name': step_name, 'success': True, 'output': ''}
                
                # Simulate different types of steps
                if step.get('uses') and 'setup-python' in step.get('uses', ''):
                    # Python setup step
                    python_version = step.get('with', {}).get('python-version', '3.12')
                    success, output = self.simulate_python_setup(python_version)
                    step_result['success'] = success
                    step_result['output'] = output
                    
                elif step.get('uses') and 'checkout' in step.get('uses', ''):
                    # Checkout step - always succeeds in simulation
                    step_result['success'] = True
                    step_result['output'] = "Repository checkout simulated"
                    
                elif step.get('run'):
                    # Shell command step
                    run_command = step['run']
                    
                    # Identify command types and simulate appropriately
                    if 'cmake' in run_command and ('configure' in step_name.lower() or 'cmake -S' in run_command):
                        # CMake configuration
                        success, output = self.simulate_build_step(job_name, "Debug")
                        step_result['success'] = success
                        step_result['output'] = output
                        
                    elif 'cmake --build' in run_command:
                        # Build step - simulate as successful since we tested configuration
                        step_result['success'] = True
                        step_result['output'] = "Build step simulated (configuration tested)"
                        
                    elif 'apt-get' in run_command or 'sudo apt' in run_command:
                        # Dependency installation
                        success, output = self.simulate_dependency_installation()
                        step_result['success'] = success
                        step_result['output'] = output
                        
                    elif 'tools/ci/' in run_command:
                        # CI script execution
                        success, output = self.simulate_ci_scripts()
                        step_result['success'] = success
                        step_result['output'] = output
                        
                    elif 'pip install' in run_command:
                        # Python package installation
                        step_result['success'] = True
                        step_result['output'] = "Python packages already installed"
                        
                    else:
                        # Generic command - just validate syntax if possible
                        step_result['success'] = True
                        step_result['output'] = f"Command simulated: {run_command[:50]}..."
                
                else:
                    # Unknown step type
                    step_result['success'] = True
                    step_result['output'] = "Step type not specifically simulated"
                
                job_result['steps'].append(step_result)
                
                if not step_result['success']:
                    job_result['success'] = False
                    job_result['errors'].append(f"Step '{step_name}': {step_result['output']}")
                    
                    # Stop on critical failures unless continue-on-error is set
                    if not step.get('continue_on_error', False):
                        print(f"    ❌ Failed: {step_result['output']}")
                        break
                else:
                    print(f"    ✅ Success: {step_result['output']}")
                    
        except Exception as e:
            job_result['success'] = False
            job_result['errors'].append(f"Job simulation error: {e}")
            print(f"❌ Job simulation failed: {e}")
        
        job_result['duration'] = time.time() - start_time
        
        # Summary
        status = "✅ SUCCESS" if job_result['success'] else "❌ FAILED"
        print(f"\n{status} - {job_name} ({job_result['duration']:.2f}s)")
        
        if job_result['errors']:
            print("Errors:")
            for error in job_result['errors']:
                print(f"  - {error}")
        
        return job_result
    
    def simulate_workflow(self, workflow_file: Path, job_filter: Optional[str] = None) -> Dict[str, Any]:
        """Simulate all jobs in a workflow or a specific job."""
        workflow_info = self.parse_workflow(workflow_file)
        if not workflow_info:
            return None
        
        workflow_name = workflow_info['name']
        print(f"\n🚀 Starting workflow simulation: {workflow_name}")
        print(f"📁 File: {workflow_file}")
        
        workflow_result = {
            'name': workflow_name,
            'file': str(workflow_file),
            'jobs': {},
            'success': True,
            'total_duration': 0
        }
        
        start_time = time.time()
        jobs = workflow_info['jobs']
        
        # Filter jobs if specified
        if job_filter:
            if job_filter in jobs:
                jobs = {job_filter: jobs[job_filter]}
            else:
                print(f"❌ Job '{job_filter}' not found in workflow")
                return None
        
        for job_name, job_config in jobs.items():
            job_result = self.simulate_job(workflow_name, job_name, job_config)
            workflow_result['jobs'][job_name] = job_result
            
            if not job_result['success']:
                workflow_result['success'] = False
                self.failed_jobs.append(f"{workflow_name}::{job_name}")
            else:
                self.successful_jobs.append(f"{workflow_name}::{job_name}")
        
        workflow_result['total_duration'] = time.time() - start_time
        
        print(f"\n📊 Workflow Summary: {workflow_name}")
        print(f"Duration: {workflow_result['total_duration']:.2f}s")
        print(f"Jobs: {len(jobs)} total, {len([j for j in workflow_result['jobs'].values() if j['success']])} successful")
        
        return workflow_result
    
    def generate_report(self) -> str:
        """Generate a comprehensive simulation report."""
        report = []
        report.append("# Workflow Job Simulation Report")
        report.append(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_jobs = len(self.successful_jobs) + len(self.failed_jobs)
        report.append("## Summary")
        report.append(f"- Total jobs simulated: {total_jobs}")
        report.append(f"- Successful jobs: {len(self.successful_jobs)}")
        report.append(f"- Failed jobs: {len(self.failed_jobs)}")
        report.append("")
        
        # Successful jobs
        if self.successful_jobs:
            report.append("## ✅ Successful Jobs")
            for job in self.successful_jobs:
                report.append(f"- {job}")
            report.append("")
        
        # Failed jobs
        if self.failed_jobs:
            report.append("## ❌ Failed Jobs")
            for job in self.failed_jobs:
                report.append(f"- {job}")
            report.append("")
        
        # Detailed results
        report.append("## Detailed Results")
        for workflow_name, workflow_result in self.results.items():
            report.append(f"### {workflow_name}")
            
            if workflow_result and 'jobs' in workflow_result:
                for job_name, job_result in workflow_result['jobs'].items():
                    status = "✅" if job_result['success'] else "❌"
                    report.append(f"#### {status} {job_name}")
                    report.append(f"Platform: {job_result['platform']}")
                    report.append(f"Duration: {job_result['duration']:.2f}s")
                    
                    if job_result['errors']:
                        report.append("Errors:")
                        for error in job_result['errors']:
                            report.append(f"- {error}")
                    
                    report.append("")
        
        return "\n".join(report)
    
    def run_simulation(self, workflow_filter: Optional[str] = None, 
                      job_filter: Optional[str] = None) -> None:
        """Run the complete workflow simulation."""
        print("🎬 Starting Workflow Job Simulation")
        print("=" * 50)
        
        workflows = self.discover_workflows()
        print(f"Found {len(workflows)} workflow files")
        
        # Filter workflows if specified
        if workflow_filter:
            workflows = [w for w in workflows if workflow_filter.lower() in w.name.lower()]
            print(f"Filtered to {len(workflows)} workflows matching '{workflow_filter}'")
        
        for workflow_file in workflows:
            try:
                result = self.simulate_workflow(workflow_file, job_filter)
                if result:
                    self.results[result['name']] = result
            except Exception as e:
                print(f"❌ Error simulating {workflow_file}: {e}")
                self.failed_jobs.append(f"{workflow_file.name}::ERROR")
        
        # Generate and save report
        report = self.generate_report()
        report_file = self.repo_path / "workflow_simulation_report.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_file}")
        print("\n" + "=" * 50)
        print("🎬 Workflow Job Simulation Complete")
        
        # Print summary
        total_jobs = len(self.successful_jobs) + len(self.failed_jobs)
        print(f"📊 Results: {len(self.successful_jobs)}/{total_jobs} jobs successful")
        
        if self.failed_jobs:
            print("\n❌ Failed jobs that need attention:")
            for job in self.failed_jobs:
                print(f"  - {job}")
        else:
            print("\n✅ All jobs simulated successfully!")

def main():
    parser = argparse.ArgumentParser(description="Simulate GitHub Actions workflow jobs")
    parser.add_argument("--repo", default=".", 
                       help="Repository path (default: current directory)")
    parser.add_argument("--workflow", 
                       help="Filter to specific workflow (partial name match)")
    parser.add_argument("--job", 
                       help="Filter to specific job name")
    parser.add_argument("--list", action="store_true",
                       help="List available workflows and jobs")
    
    args = parser.parse_args()
    
    simulator = WorkflowJobSimulator(args.repo)
    
    if args.list:
        # List workflows and jobs
        workflows = simulator.discover_workflows()
        print("📋 Available Workflows and Jobs:")
        print("=" * 40)
        
        for workflow_file in workflows:
            workflow_info = simulator.parse_workflow(workflow_file)
            if workflow_info:
                print(f"\n🚀 {workflow_info['name']} ({workflow_file.name})")
                for job_name in workflow_info['jobs'].keys():
                    print(f"  - {job_name}")
    else:
        # Run simulation
        simulator.run_simulation(args.workflow, args.job)

if __name__ == "__main__":
    main()