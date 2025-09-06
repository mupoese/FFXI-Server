#!/usr/bin/env python3
"""
Comprehensive Security and Build Test for FFXI Server GM System
Tests all security implementations and admin dashboard functionality
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

class SecurityTestSuite:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0
            }
        }
        
    def add_test_result(self, name, passed, details, warnings=None):
        """Add a test result to the suite"""
        result = {
            'name': name,
            'passed': passed,
            'details': details,
            'warnings': warnings or []
        }
        self.results['tests'].append(result)
        self.results['summary']['total'] += 1
        if passed:
            self.results['summary']['passed'] += 1
        else:
            self.results['summary']['failed'] += 1
        if warnings:
            self.results['summary']['warnings'] += len(warnings)
    
    def test_promote_command_disabled(self):
        """Test that promote command is properly disabled"""
        try:
            with open('scripts/commands/promote.lua', 'r') as f:
                content = f.read()
            
            required_elements = [
                'GM promotion is now restricted to the web admin dashboard',
                'Contact the server owner to request GM privileges',
                '[SECURITY]',
                'attempted to use disabled promote command'
            ]
            
            found = [elem for elem in required_elements if elem in content]
            
            # Check for dangerous patterns
            dangerous_patterns = ['SetGMLevel', 'player:setGMLevel', 'PromotePlayer']
            found_dangerous = [pattern for pattern in dangerous_patterns if pattern in content]
            
            passed = len(found) == len(required_elements) and not found_dangerous
            details = {
                'security_messages': found,
                'dangerous_patterns_found': found_dangerous,
                'file_size': len(content),
                'disabled_properly': passed
            }
            
            self.add_test_result('Promote Command Security', passed, details)
            
        except Exception as e:
            self.add_test_result('Promote Command Security', False, {'error': str(e)})
    
    def test_database_triggers(self):
        """Test that database security triggers are implemented"""
        try:
            with open('sql/gm_security_triggers.sql', 'r') as f:
                content = f.read()
            
            required_triggers = [
                'prevent_unauthorized_account_priv_update',
                'prevent_unauthorized_gmlevel_update',
                'prevent_unauthorized_account_priv_insert',
                'prevent_unauthorized_gmlevel_insert'
            ]
            
            found_triggers = [trigger for trigger in required_triggers if trigger in content]
            
            security_features = {
                'server_owner_protection': 'server_owner' in content and 'cannot be demoted' in content,
                'audit_logging': 'audit_gm' in content and 'INSERT INTO audit_gm' in content,
                'privilege_validation': 'NEW.priv' in content and 'NEW.gmlevel' in content,
                'trigger_creation': 'CREATE TRIGGER' in content,
                'sqlstate_errors': 'SIGNAL SQLSTATE' in content
            }
            
            passed = len(found_triggers) == len(required_triggers) and all(security_features.values())
            details = {
                'triggers_found': found_triggers,
                'security_features': security_features,
                'file_size': len(content)
            }
            
            self.add_test_result('Database Security Triggers', passed, details)
            
        except Exception as e:
            self.add_test_result('Database Security Triggers', False, {'error': str(e)})
    
    def test_admin_dashboard(self):
        """Test admin dashboard GM management functionality"""
        try:
            with open('web/admin.html', 'r') as f:
                content = f.read()
            
            # Check for GM management elements
            gm_elements = {
                'gm_tab': 'data-tab="gm-management"' in content,
                'gm_section': 'id="gm-management"' in content,
                'gm_title': 'GM Management' in content,
                'server_owner_exclusive': 'Server Owner Exclusive' in content,
                'promote_button': 'Promote New GM' in content,
                'revoke_functionality': 'Revoke' in content
            }
            
            # Check for JavaScript functions
            js_functions = [
                'refreshGMAccounts', 'promoteGM', 'revokeGM', 'refreshGMAudit',
                'updateGMAccountsTable', 'showPromoteModal'
            ]
            found_functions = [func for func in js_functions if func in content]
            
            # Check for API endpoint references
            api_endpoints = ['/api/gm/accounts', '/api/gm/promote', '/api/gm/revoke', '/api/gm/audit']
            found_endpoints = [endpoint for endpoint in api_endpoints if endpoint in content]
            
            passed = (all(gm_elements.values()) and 
                     len(found_functions) == len(js_functions) and 
                     len(found_endpoints) == len(api_endpoints))
            
            details = {
                'gm_elements': gm_elements,
                'js_functions_found': found_functions,
                'api_endpoints_found': found_endpoints,
                'file_size': len(content)
            }
            
            self.add_test_result('Admin Dashboard GM Management', passed, details)
            
        except Exception as e:
            self.add_test_result('Admin Dashboard GM Management', False, {'error': str(e)})
    
    def test_api_endpoints(self):
        """Test that API endpoints are properly defined"""
        try:
            # Test that the API file can be imported (syntax check)
            sys.path.append('web/api')
            import app
            
            # Check for GM endpoints
            gm_routes = []
            for rule in app.app.url_map.iter_rules():
                if 'gm' in rule.rule:
                    gm_routes.append({
                        'endpoint': rule.rule,
                        'methods': list(rule.methods)
                    })
            
            # Check for security functions
            security_functions = {
                'generate_api_token': hasattr(app, 'generate_api_token'),
                'verify_api_token': hasattr(app, 'verify_api_token'),
                'require_auth': hasattr(app, 'require_auth'),
                'get_gm_accounts': '/api/gm/accounts' in [route['endpoint'] for route in gm_routes],
                'promote_gm': '/api/gm/promote' in [route['endpoint'] for route in gm_routes],
                'revoke_gm': '/api/gm/revoke' in [route['endpoint'] for route in gm_routes],
                'gm_audit': '/api/gm/audit' in [route['endpoint'] for route in gm_routes]
            }
            
            passed = len(gm_routes) >= 4 and all(security_functions.values())
            details = {
                'gm_routes': gm_routes,
                'security_functions': security_functions,
                'total_routes': len(list(app.app.url_map.iter_rules()))
            }
            
            self.add_test_result('API Endpoints Implementation', passed, details)
            
        except Exception as e:
            self.add_test_result('API Endpoints Implementation', False, {'error': str(e)})
    
    def test_documentation(self):
        """Test that GM documentation is comprehensive"""
        try:
            with open('docs/GM_ACCOUNT_SYSTEM.md', 'r') as f:
                content = f.read()
            
            required_sections = [
                'Admin Dashboard Exclusive',
                'Server Owner Authority',
                'GM Level System',
                'Database Structure',
                'Security Model',
                'Promotion Security'
            ]
            
            found_sections = [section for section in required_sections if section in content]
            
            security_keywords = [
                'server owner',
                'admin dashboard',
                'audit',
                'trigger',
                'exclusive control',
                'unauthorized'
            ]
            
            found_keywords = [keyword for keyword in security_keywords if keyword.lower() in content.lower()]
            
            passed = (len(found_sections) >= len(required_sections) * 0.8 and 
                     len(found_keywords) >= len(security_keywords) * 0.8)
            
            details = {
                'sections_found': found_sections,
                'security_keywords': found_keywords,
                'word_count': len(content.split()),
                'file_size': len(content)
            }
            
            self.add_test_result('GM Documentation Completeness', passed, details)
            
        except Exception as e:
            self.add_test_result('GM Documentation Completeness', False, {'error': str(e)})
    
    def test_build_configuration(self):
        """Test build system configuration"""
        try:
            # Check if CMake configuration exists and works
            build_dir = Path('build')
            if not build_dir.exists():
                os.makedirs(build_dir)
            
            # Run CMake configuration test
            result = subprocess.run(
                ['cmake', '..', '-DCMAKE_BUILD_TYPE=Debug'],
                cwd='build',
                capture_output=True,
                text=True,
                timeout=120
            )
            
            cmake_success = result.returncode == 0
            
            # Check for required files
            required_files = [
                'CMakeLists.txt',
                'web/admin.html',
                'web/api/app.py',
                'sql/gm_security_triggers.sql',
                'scripts/commands/promote.lua',
                'docs/GM_ACCOUNT_SYSTEM.md'
            ]
            
            existing_files = [f for f in required_files if Path(f).exists()]
            
            passed = cmake_success and len(existing_files) == len(required_files)
            details = {
                'cmake_success': cmake_success,
                'cmake_output': result.stdout[-500:] if result.stdout else '',
                'cmake_errors': result.stderr[-500:] if result.stderr else '',
                'existing_files': existing_files,
                'missing_files': [f for f in required_files if f not in existing_files]
            }
            
            warnings = []
            if not cmake_success:
                warnings.append(f"CMake configuration failed: {result.stderr[:200]}")
            
            self.add_test_result('Build Configuration', passed, details, warnings)
            
        except Exception as e:
            self.add_test_result('Build Configuration', False, {'error': str(e)})
    
    def run_all_tests(self):
        """Run all security and build tests"""
        print("🔒 Starting Comprehensive Security and Build Test Suite")
        print("=" * 60)
        
        # Run all tests
        self.test_promote_command_disabled()
        self.test_database_triggers()
        self.test_admin_dashboard()
        self.test_api_endpoints()
        self.test_documentation()
        self.test_build_configuration()
        
        # Print results
        self.print_results()
        
        # Save results to file
        with open('comprehensive_security_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)
        
        return self.results['summary']['failed'] == 0
    
    def print_results(self):
        """Print test results in a formatted way"""
        print("\n📋 TEST RESULTS")
        print("=" * 60)
        
        for test in self.results['tests']:
            status = "✅ PASS" if test['passed'] else "❌ FAIL"
            print(f"{status} {test['name']}")
            
            # Print key details
            if isinstance(test['details'], dict):
                for key, value in test['details'].items():
                    if key == 'error':
                        print(f"    ❌ Error: {value}")
                    elif isinstance(value, bool):
                        print(f"    {'✅' if value else '❌'} {key}")
                    elif isinstance(value, list) and value:
                        print(f"    📝 {key}: {len(value)} items")
                    elif isinstance(value, (int, str)) and str(value):
                        print(f"    📝 {key}: {value}")
            
            # Print warnings
            if test['warnings']:
                for warning in test['warnings']:
                    print(f"    ⚠️  {warning}")
            
            print()
        
        # Print summary
        summary = self.results['summary']
        print("📊 SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {summary['total']}")
        print(f"✅ Passed: {summary['passed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⚠️  Warnings: {summary['warnings']}")
        
        if summary['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED - GM Security System is properly implemented!")
        else:
            print(f"\n🚨 {summary['failed']} TESTS FAILED - Review and fix issues above")
        
        print(f"\nDetailed results saved to: comprehensive_security_test_results.json")

def main():
    """Main function to run the test suite"""
    if not Path('scripts/commands/promote.lua').exists():
        print("❌ Error: Must be run from FFXI Server root directory")
        sys.exit(1)
    
    test_suite = SecurityTestSuite()
    success = test_suite.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()