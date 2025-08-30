#!/usr/bin/env python3
"""
Test script for enhanced web admin panel
"""

import sys
import os

# Add the tools directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_web_admin_import():
    """Test that the web admin module can be imported"""
    try:
        # Mock the missing dependencies for testing
        import unittest.mock
        
        with unittest.mock.patch.dict('sys.modules', {
            'flask': unittest.mock.MagicMock(),
            'mysql.connector': unittest.mock.MagicMock(),
            'psutil': unittest.mock.MagicMock()
        }):
            import web_admin
            print("✅ Enhanced web admin module imports successfully")
            
            # Test class instantiation
            admin = web_admin.WebAdminPanel("web_admin_config.json")
            print("✅ WebAdminPanel class instantiates successfully")
            
            # Test configuration loading
            if 'user_management' in admin.config:
                print("✅ Configuration includes user management settings")
            
            print("✅ All basic tests passed!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_web_admin_import()
    sys.exit(0 if success else 1)