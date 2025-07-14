#!/usr/bin/env python3
"""
Test script for the Local Dev Dashboard feature
"""

import requests
import json
import time

def test_dev_dashboard():
    """Test the dev dashboard API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Chandra Dev Dashboard...")
    print("=" * 50)
    
    # Test 1: Check if dev dashboard page loads
    print("\n1. Testing dev dashboard page...")
    try:
        response = requests.get(f"{base_url}/dev-dashboard")
        if response.status_code == 200:
            print("✅ Dev dashboard page loads successfully")
        else:
            print(f"❌ Dev dashboard page failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing dev dashboard: {e}")
    
    # Test 2: Check dev status API
    print("\n2. Testing dev status API...")
    try:
        response = requests.get(f"{base_url}/api/dev/status")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Dev status API working")
                print(f"   - CPU: {data['data']['system']['cpu_percent']:.1f}%")
                print(f"   - Memory: {data['data']['system']['memory_percent']:.1f}%")
                print(f"   - Connected clients: {data['data']['server']['connected_clients']}")
                print(f"   - Recent errors: {data['data']['errors']['recent_count']}")
            else:
                print(f"❌ Dev status API error: {data.get('error')}")
        else:
            print(f"❌ Dev status API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing dev status API: {e}")
    
    # Test 3: Check main status API
    print("\n3. Testing main status API...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Main status API working: {data['name']}")
        else:
            print(f"❌ Main status API failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error accessing main status API: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Dev Dashboard test completed!")
    print("\nTo view the dashboard:")
    print(f"   Open: {base_url}/dev-dashboard")
    print("\nTo test WebSocket connections:")
    print("   1. Open a lesson player page")
    print("   2. Check the 'Connected Clients' count in the dashboard")

if __name__ == "__main__":
    test_dev_dashboard() 