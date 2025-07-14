#!/usr/bin/env python3
"""
Test script for Chandra robustness and error handling features
"""

import requests
import json
import time
from datetime import datetime

def test_error_reporting():
    """Test the error reporting endpoint"""
    print("Testing error reporting endpoint...")
    
    error_data = {
        "message": "Test error from frontend",
        "stack": "Error: Test error\n    at test.js:1:1",
        "name": "TestError",
        "timestamp": datetime.utcnow().isoformat(),
        "userAgent": "Mozilla/5.0 (Test Browser)",
        "url": "http://localhost:5000/test",
        "context": {
            "type": "test",
            "functionName": "testFunction"
        },
        "sessionId": "test_session_123",
        "userId": None
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/errors",
            json=error_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Error reporting endpoint working correctly")
                return True
            else:
                print("❌ Error reporting failed:", result.get("error"))
                return False
        else:
            print(f"❌ Error reporting endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing error reporting: {e}")
        return False

def test_connection_status():
    """Test the connection status endpoint"""
    print("Testing connection status...")
    
    try:
        response = requests.get("http://localhost:5000/api/dev/status")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Connection status endpoint working correctly")
                return True
            else:
                print("❌ Connection status failed:", result.get("error"))
                return False
        else:
            print(f"❌ Connection status endpoint returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing connection status: {e}")
        return False

def test_script_endpoints():
    """Test script-related endpoints"""
    print("Testing script endpoints...")
    
    try:
        # Test getting scripts list
        response = requests.get("http://localhost:5000/scripts/")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Script endpoints working correctly")
                return True
            else:
                print("❌ Script endpoints failed:", result.get("error"))
                return False
        else:
            print(f"❌ Script endpoints returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing script endpoints: {e}")
        return False

def main():
    """Run all robustness tests"""
    print("🧪 Testing Chandra Robustness Features")
    print("=" * 50)
    
    tests = [
        ("Error Reporting", test_error_reporting),
        ("Connection Status", test_connection_status),
        ("Script Endpoints", test_script_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}...")
        if test_func():
            passed += 1
        time.sleep(1)  # Brief pause between tests
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All robustness tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    main() 