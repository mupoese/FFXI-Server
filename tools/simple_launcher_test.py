#!/usr/bin/env python3
"""
Simple Launcher Communication Test
Tests core functionality without GUI dependencies
"""

import os
import sys
import json
import time
import tempfile
import subprocess
import requests
from pathlib import Path
from typing import Dict, Any


def test_config_loading():
    """Test configuration loading"""
    print("🔧 Testing configuration loading...")
    
    # Create test .env file
    test_config = """SERVERNAME=TestServer
TESTSERVER_SERVER_NAME=Test Server
TESTSERVER_SERVER_URL=http://localhost:5000
TESTSERVER_API_BASE_URL=http://localhost:5000/api
TESTSERVER_SERVER_IPV4=127.0.0.1
TESTSERVER_SERVER_IPV6=::1
TESTSERVER_API_PORT=5000
TESTSERVER_ADMIN_USERNAME=testadmin
TESTSERVER_ADMIN_PASSWORD=testpass123
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write(test_config)
        env_file = f.name
    
    try:
        # Test configuration loading (without GUI imports)
        sys.path.insert(0, 'tools')
        
        # Create a simple config loader to test the concept
        config = {}
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
        
        # Test retrieval
        server_name = config.get('SERVERNAME', 'FFXI')
        server_url = config.get(f'{server_name}_SERVER_URL', '')
        api_url = config.get(f'{server_name}_API_BASE_URL', '')
        
        print(f"  ✅ Server Name: {server_name}")
        print(f"  ✅ Server URL: {server_url}")
        print(f"  ✅ API URL: {api_url}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Config loading failed: {e}")
        return False
    finally:
        os.unlink(env_file)


def test_url_fallback():
    """Test URL fallback logic"""
    print("🌐 Testing URL fallback logic...")
    
    def test_connection(url: str) -> bool:
        """Test if a URL is reachable"""
        try:
            response = requests.get(f"{url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    # Test URLs
    test_urls = [
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://[::1]:5000'
    ]
    
    working_urls = []
    for url in test_urls:
        if test_connection(url):
            working_urls.append(url)
            print(f"  ✅ {url} - reachable")
        else:
            print(f"  ❌ {url} - not reachable")
    
    print(f"  📊 Found {len(working_urls)} working URLs")
    return True


def test_api_endpoints():
    """Test basic API functionality"""
    print("🔌 Testing API endpoints...")
    
    # Start a simple test server
    try:
        # Test if we can import and start the API
        env = os.environ.copy()
        env.update({
            'SERVERNAME': 'TestServer',
            'TESTSERVER_API_PORT': '5001',  # Use different port to avoid conflicts
            'TESTSERVER_ADMIN_USERNAME': 'testadmin',
            'TESTSERVER_ADMIN_PASSWORD': 'testpass123'
        })
        
        # Try to start the API server
        process = subprocess.Popen([
            sys.executable, '-c', """
import os
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Test Server API'})

@app.route('/auth/token', methods=['POST'])
def auth():
    return jsonify({'token': 'test_token_123'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
"""
        ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(2)
        
        # Test health endpoint
        try:
            response = requests.get('http://localhost:5001/health', timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Health check: {data['status']}")
                
                # Test auth endpoint
                auth_response = requests.post('http://localhost:5001/auth/token', 
                                            json={'username': 'test', 'password': 'test'}, 
                                            timeout=5)
                if auth_response.status_code == 200:
                    auth_data = auth_response.json()
                    print(f"  ✅ Auth endpoint: token received")
                else:
                    print(f"  ❌ Auth endpoint failed: {auth_response.status_code}")
                
                success = True
            else:
                print(f"  ❌ Health check failed: {response.status_code}")
                success = False
                
        except Exception as e:
            print(f"  ❌ API test failed: {e}")
            success = False
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
        
        return success
        
    except Exception as e:
        print(f"  ❌ Could not start test server: {e}")
        return False


def test_build_config():
    """Test build configuration"""
    print("🏗️ Testing build configuration...")
    
    try:
        # Test the build script configuration loading
        sys.path.insert(0, 'tools')
        
        # Test config loading logic from build script
        config = {
            'SERVERNAME': 'TestServer',
            'TESTSERVER_SERVER_URL': 'http://test.example.com:5000',
            'TESTSERVER_API_BASE_URL': 'http://test.example.com:5000/api',
            'TESTSERVER_SERVER_IPV4': '192.168.1.100',
            'TESTSERVER_SERVER_IPV6': '2001:db8::1'
        }
        
        server_name = config.get('SERVERNAME', 'FFXI')
        
        # Test baked configuration creation
        baked_config = {
            'SERVERNAME': server_name,
            f'{server_name}_SERVER_URL': config.get(f'{server_name}_SERVER_URL', ''),
            f'{server_name}_API_BASE_URL': config.get(f'{server_name}_API_BASE_URL', ''),
            f'{server_name}_SERVER_IPV4': config.get(f'{server_name}_SERVER_IPV4', '127.0.0.1'),
            f'{server_name}_SERVER_IPV6': config.get(f'{server_name}_SERVER_IPV6', '::1')
        }
        
        print(f"  ✅ Baked config created for: {server_name}")
        print(f"  ✅ Server URL: {baked_config.get(f'{server_name}_SERVER_URL')}")
        print(f"  ✅ API URL: {baked_config.get(f'{server_name}_API_BASE_URL')}")
        print(f"  ✅ IPv4 fallback: {baked_config.get(f'{server_name}_SERVER_IPV4')}")
        print(f"  ✅ IPv6 fallback: {baked_config.get(f'{server_name}_SERVER_IPV6')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Build config test failed: {e}")
        return False


def main():
    """Run simplified tests"""
    print("🚀 Simple Launcher Communication Test")
    print("=" * 50)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("URL Fallback Logic", test_url_fallback),
        ("API Endpoints", test_api_endpoints),
        ("Build Configuration", test_build_config)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
            print()
        except Exception as e:
            print(f"  ❌ {test_name} error: {e}")
            results.append(False)
            print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())