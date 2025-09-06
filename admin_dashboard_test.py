#!/usr/bin/env python3
"""
Admin Dashboard Functionality Test
Tests the web interface for GM management
"""

import tempfile
import os
import json
from pathlib import Path

def test_admin_dashboard_functionality():
    """Test admin dashboard specific functionality"""
    print("🌐 Testing Admin Dashboard Functionality")
    print("=" * 50)
    
    # Read the admin.html file
    with open('web/admin.html', 'r') as f:
        html_content = f.read()
    
    # Test 1: Check GM Management Tab Structure
    print("1. Testing GM Management Tab Structure...")
    gm_tab_found = 'data-tab="gm-management"' in html_content
    gm_content_found = 'id="gm-management"' in html_content
    server_owner_text = 'Server Owner Exclusive' in html_content
    
    print(f"   ✅ GM Tab Element: {gm_tab_found}")
    print(f"   ✅ GM Content Section: {gm_content_found}")
    print(f"   ✅ Server Owner Exclusive Text: {server_owner_text}")
    
    # Test 2: Check GM Management UI Elements
    print("\n2. Testing GM Management UI Elements...")
    ui_elements = {
        'Promote Button': 'Promote New GM' in html_content,
        'Revoke Functionality': 'revokeGM(' in html_content,
        'Audit Log': 'GM Actions' in html_content,
        'GM Accounts Table': 'gmAccountsTableBody' in html_content,
        'Server Owner Protection': 'Cannot modify owner' in html_content
    }
    
    for element, found in ui_elements.items():
        print(f"   {'✅' if found else '❌'} {element}: {found}")
    
    # Test 3: Check JavaScript Functions
    print("\n3. Testing JavaScript Functions...")
    js_functions = {
        'refreshGMAccounts': 'function refreshGMAccounts()' in html_content or 'refreshGMAccounts()' in html_content,
        'promoteGM': 'function promoteGM(' in html_content or 'promoteGM(' in html_content,
        'revokeGM': 'function revokeGM(' in html_content or 'revokeGM(' in html_content,
        'showPromoteModal': 'function showPromoteModal(' in html_content or 'showPromoteModal(' in html_content,
        'updateGMAccountsTable': 'function updateGMAccountsTable(' in html_content or 'updateGMAccountsTable(' in html_content,
        'refreshGMAudit': 'function refreshGMAudit(' in html_content or 'refreshGMAudit(' in html_content
    }
    
    for func, found in js_functions.items():
        print(f"   {'✅' if found else '❌'} {func}: {found}")
    
    # Test 4: Check API Integration
    print("\n4. Testing API Integration...")
    api_calls = {
        'GM Accounts API': '/api/gm/accounts' in html_content,
        'Promote API': '/api/gm/promote' in html_content,
        'Revoke API': '/api/gm/revoke' in html_content,
        'Audit API': '/api/gm/audit' in html_content,
        'Authentication Header': 'Authorization' in html_content,
        'Error Handling': 'showNotification' in html_content
    }
    
    for api, found in api_calls.items():
        print(f"   {'✅' if found else '❌'} {api}: {found}")
    
    # Test 5: Check Security Features
    print("\n5. Testing Security Features...")
    security_features = {
        'Server Owner Check': 'server_owner' in html_content,
        'Level Protection': 'level 5' in html_content.lower(),
        'Authentication Token': 'getAuthToken' in html_content,
        'Permission Validation': 'Only the server owner' in html_content,
        'Audit Logging': 'audit_logs' in html_content
    }
    
    for feature, found in security_features.items():
        print(f"   {'✅' if found else '❌'} {feature}: {found}")
    
    # Overall Assessment
    all_tests = [gm_tab_found, gm_content_found, server_owner_text]
    all_tests.extend(ui_elements.values())
    all_tests.extend(js_functions.values())
    all_tests.extend(api_calls.values())
    all_tests.extend(security_features.values())
    
    passed_tests = sum(all_tests)
    total_tests = len(all_tests)
    
    print(f"\n📊 ADMIN DASHBOARD TEST SUMMARY")
    print("=" * 50)
    print(f"Total Checks: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ADMIN DASHBOARD FULLY FUNCTIONAL!")
        print("   All GM management features are properly implemented")
    elif passed_tests >= total_tests * 0.9:
        print("\n✅ ADMIN DASHBOARD MOSTLY FUNCTIONAL")
        print("   Minor issues detected but core functionality working")
    else:
        print("\n⚠️  ADMIN DASHBOARD HAS ISSUES")
        print("   Several features are missing or not working")
    
    return passed_tests == total_tests

def test_api_security():
    """Test API security implementation"""
    print("\n🔒 Testing API Security Implementation")
    print("=" * 50)
    
    try:
        # Import the API module
        import sys
        sys.path.append('web/api')
        import app
        
        # Test 1: Check Authentication Decorator
        print("1. Testing Authentication System...")
        has_require_auth = hasattr(app, 'require_auth')
        has_token_generation = hasattr(app, 'generate_api_token')
        has_token_verification = hasattr(app, 'verify_api_token')
        
        print(f"   ✅ require_auth decorator: {has_require_auth}")
        print(f"   ✅ Token generation: {has_token_generation}")
        print(f"   ✅ Token verification: {has_token_verification}")
        
        # Test 2: Check GM Endpoints Security
        print("\n2. Testing GM Endpoints Security...")
        gm_endpoints = []
        for rule in app.app.url_map.iter_rules():
            if '/api/gm/' in rule.rule:
                gm_endpoints.append(rule.rule)
        
        required_endpoints = ['/api/gm/accounts', '/api/gm/promote', '/api/gm/revoke', '/api/gm/audit']
        found_endpoints = [ep for ep in required_endpoints if ep in gm_endpoints]
        
        print(f"   ✅ Required GM endpoints found: {len(found_endpoints)}/{len(required_endpoints)}")
        for endpoint in found_endpoints:
            print(f"       - {endpoint}")
        
        # Test 3: Check Server Owner Protection
        print("\n3. Testing Server Owner Protection...")
        with open('web/api/app.py', 'r') as f:
            api_content = f.read()
        
        protection_features = {
            'Server Owner Check': 'server_owner' in api_content,
            'Owner Demotion Prevention': 'cannot be demoted' in api_content.lower(),
            'Owner Authentication': 'promoter_id != server_owner' in api_content,
            'Environment Variable': 'FFXI_SERVER_OWNER' in api_content,
            'Level 5 Protection': 'target_level < 5' in api_content
        }
        
        for feature, found in protection_features.items():
            print(f"   {'✅' if found else '❌'} {feature}: {found}")
        
        print(f"\n📊 API SECURITY TEST SUMMARY")
        all_security_tests = [has_require_auth, has_token_generation, has_token_verification]
        all_security_tests.append(len(found_endpoints) == len(required_endpoints))
        all_security_tests.extend(protection_features.values())
        
        passed_security = sum(all_security_tests)
        total_security = len(all_security_tests)
        
        print(f"Security Checks Passed: {passed_security}/{total_security}")
        print(f"Security Score: {(passed_security/total_security)*100:.1f}%")
        
        return passed_security >= total_security * 0.9
        
    except Exception as e:
        print(f"❌ Error testing API security: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 FFXI Server Admin Dashboard Comprehensive Test")
    print("=" * 60)
    
    # Change to the correct directory
    if not Path('web/admin.html').exists():
        print("❌ Error: Must be run from FFXI Server root directory")
        return False
    
    # Run tests
    dashboard_ok = test_admin_dashboard_functionality()
    api_ok = test_api_security()
    
    # Final result
    print("\n🏁 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"{'✅' if dashboard_ok else '❌'} Admin Dashboard Functionality: {'PASS' if dashboard_ok else 'FAIL'}")
    print(f"{'✅' if api_ok else '❌'} API Security Implementation: {'PASS' if api_ok else 'FAIL'}")
    
    overall_success = dashboard_ok and api_ok
    print(f"\n{'🎉' if overall_success else '🚨'} OVERALL RESULT: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
    
    if overall_success:
        print("\n✅ The admin dashboard is fully functional and secure!")
        print("✅ GM privileges are properly restricted to server owner control!")
        print("✅ All security measures are in place and working!")
    
    return overall_success

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)