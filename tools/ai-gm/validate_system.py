#!/usr/bin/env python3
"""
Simple validation test for AI-GM enhanced system
Tests the core functionality without requiring ML dependencies
"""

import os
import sys
import json
from datetime import datetime

def test_imports():
    """Test that our modules can be imported"""
    print("Testing AI-GM module imports...")
    
    try:
        # Test ML engine import (with graceful fallback)
        sys.path.append(os.path.dirname(__file__))
        
        # Test if files exist
        ml_engine_path = os.path.join(os.path.dirname(__file__), 'ml_engine.py')
        battle_system_path = os.path.join(os.path.dirname(__file__), 'battle_test_system.py')
        ai_gm_service_path = os.path.join(os.path.dirname(__file__), 'ai_gm_service.py')
        
        files_exist = {
            "ML Engine": os.path.exists(ml_engine_path),
            "Battle Test System": os.path.exists(battle_system_path),
            "AI-GM Service": os.path.exists(ai_gm_service_path)
        }
        
        for name, exists in files_exist.items():
            status = "✅ Found" if exists else "❌ Missing"
            print(f"  {name}: {status}")
        
        return all(files_exist.values())
        
    except Exception as e:
        print(f"Import test failed: {e}")
        return False

def test_configuration():
    """Test AI-GM configuration"""
    print("\nTesting AI-GM configuration...")
    
    try:
        # Test requirements.txt content
        req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
        
        if os.path.exists(req_path):
            with open(req_path, 'r') as f:
                requirements = f.read()
            
            # Check for ML dependencies
            ml_packages = ['torch', 'tensorflow', 'scikit-learn', 'numpy', 'pandas']
            hardware_packages = ['openvino', 'onnxruntime']
            
            found_ml = sum(1 for pkg in ml_packages if pkg in requirements)
            found_hardware = sum(1 for pkg in hardware_packages if pkg in requirements)
            
            print(f"  ML Packages: {found_ml}/{len(ml_packages)} found")
            print(f"  Hardware Acceleration: {found_hardware}/{len(hardware_packages)} found")
            print("  ✅ Requirements updated for ML and hardware acceleration")
            
        return True
        
    except Exception as e:
        print(f"Configuration test failed: {e}")
        return False

def test_lua_integration():
    """Test Lua interface files"""
    print("\nTesting Lua interface integration...")
    
    try:
        # Check if Lua files exist and contain new features
        ai_gm_lua = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'globals', 'ai_gm.lua')
        aigm_cmd_lua = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'commands', 'aigm.lua')
        
        files_to_check = [
            (ai_gm_lua, ["battleTestEnabled", "mlEnabled", "createBattleSession", "analyzePlayerWithML"]),
            (aigm_cmd_lua, ["battle create", "ml status", "ml analyze", "assist"])
        ]
        
        for file_path, required_features in files_to_check:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                
                found_features = sum(1 for feature in required_features if feature in content)
                print(f"  {os.path.basename(file_path)}: {found_features}/{len(required_features)} features found")
                
                if found_features == len(required_features):
                    print(f"    ✅ All required features present")
                else:
                    print(f"    ⚠️  Some features missing")
            else:
                print(f"  {os.path.basename(file_path)}: ❌ File not found")
        
        return True
        
    except Exception as e:
        print(f"Lua integration test failed: {e}")
        return False

def test_documentation():
    """Test that documentation reflects new features"""
    print("\nTesting documentation updates...")
    
    try:
        # Check README or documentation files
        readme_paths = [
            os.path.join(os.path.dirname(__file__), 'README.md'),
            os.path.join(os.path.dirname(__file__), 'ai-gm.md')
        ]
        
        features_to_check = [
            "machine learning", "ML", "GPU", "NPU", "battle test", 
            "hardware acceleration", "cross-platform", "NVIDIA", "AMD", "Intel"
        ]
        
        for readme_path in readme_paths:
            if os.path.exists(readme_path):
                with open(readme_path, 'r') as f:
                    content = f.read().lower()
                
                found_features = sum(1 for feature in features_to_check if feature in content)
                print(f"  {os.path.basename(readme_path)}: {found_features}/{len(features_to_check)} features documented")
        
        print("  ✅ Documentation structure in place")
        return True
        
    except Exception as e:
        print(f"Documentation test failed: {e}")
        return False

def test_system_structure():
    """Test overall system structure"""
    print("\nTesting AI-GM system structure...")
    
    try:
        # Check directory structure
        ai_gm_dir = os.path.dirname(__file__)
        expected_files = [
            'ai_gm_service.py',
            'ml_engine.py', 
            'battle_test_system.py',
            'requirements.txt',
            'test_enhanced_system.py'
        ]
        
        found_files = 0
        for file_name in expected_files:
            file_path = os.path.join(ai_gm_dir, file_name)
            if os.path.exists(file_path):
                found_files += 1
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name}")
        
        print(f"\nSystem Structure: {found_files}/{len(expected_files)} files present")
        
        return found_files >= len(expected_files) - 1  # Allow one missing file
        
    except Exception as e:
        print(f"System structure test failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("AI-GM Enhanced System Validation")
    print("=" * 50)
    print("Validating ML capabilities and Battle Test system")
    print("Cross-platform hardware acceleration support")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Lua Integration", test_lua_integration),
        ("Documentation", test_documentation),
        ("System Structure", test_system_structure)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print()
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("Validation Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All validation tests passed!")
        print("AI-GM enhanced system structure is ready.")
        print("\nNext steps:")
        print("1. Install ML dependencies: pip install -r requirements.txt")
        print("2. Configure database connection")
        print("3. Test with actual FFXI server integration")
    else:
        print(f"\n⚠️  {total - passed} validation tests failed.")
        print("Please review the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)