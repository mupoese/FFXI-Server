#!/usr/bin/env python3
"""
Test script for item enum validator.
Creates test files with valid and invalid item references to ensure validation works.
"""

import os
import tempfile
import subprocess
import sys

def create_test_files():
    """Create temporary test files for validation."""
    
    # Create temporary directory
    test_dir = tempfile.mkdtemp()
    
    # Valid test file
    valid_file = os.path.join(test_dir, "valid_test.lua")
    with open(valid_file, 'w') as f:
        f.write("""
-- Valid item references
local items = {
    xi.item.USUKANE_SOMEN,
    xi.item.ARES_MASK,
    xi.item.SKADIS_VISOR,
}

-- Commented out invalid reference should be ignored
-- xi.item.INVALID_ITEM_NAME
""")
    
    # Invalid test file
    invalid_file = os.path.join(test_dir, "invalid_test.lua")
    with open(invalid_file, 'w') as f:
        f.write("""
-- Valid and invalid item references
local items = {
    xi.item.USUKANE_SOMEN,
    xi.item.INVALID_ITEM_NOT_IN_ENUM,
    xi.item.ANOTHER_MISSING_ITEM,
}
""")
    
    return test_dir, valid_file, invalid_file


def run_validator(check_files):
    """Run the validator on specified files."""
    cmd = [
        'python3', 
        'tools/ci/item_enum_validator.py',
        '--check-files'
    ] + check_files
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def main():
    """Run tests for the item enum validator."""
    print("Testing item enum validator...")
    
    # Create test files
    test_dir, valid_file, invalid_file = create_test_files()
    
    try:
        # Test 1: Valid file should pass
        print("\nTest 1: Valid file should pass")
        returncode, stdout, stderr = run_validator([valid_file])
        if returncode == 0 and "PASSED" in stdout:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            print(f"Return code: {returncode}")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            sys.exit(1)
        
        # Test 2: Invalid file should fail
        print("\nTest 2: Invalid file should fail")
        returncode, stdout, stderr = run_validator([invalid_file])
        if returncode == 1 and "FAILED" in stdout and "INVALID_ITEM_NOT_IN_ENUM" in stdout:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            print(f"Return code: {returncode}")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            sys.exit(1)
        
        # Test 3: Mixed files should fail
        print("\nTest 3: Mixed valid and invalid files should fail")
        returncode, stdout, stderr = run_validator([valid_file, invalid_file])
        if returncode == 1 and "FAILED" in stdout:
            print("✅ PASS")
        else:
            print("❌ FAIL")
            print(f"Return code: {returncode}")
            print(f"Stdout: {stdout}")
            print(f"Stderr: {stderr}")
            sys.exit(1)
        
        print("\n✅ All tests passed!")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)


if __name__ == '__main__':
    main()