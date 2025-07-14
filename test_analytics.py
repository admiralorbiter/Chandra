#!/usr/bin/env python3
"""
Test script for Chandra Analytics & Progress Tracking
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
USER_ID = 1
LESSON_ID = "counting_fingers"
SESSION_ID = f"test_session_{int(time.time())}"

def test_analytics_endpoints():
    """Test the analytics endpoints."""
    print("🧪 Testing Chandra Analytics & Progress Tracking")
    print("=" * 50)
    
    # Test 1: Log an event
    print("\n1. Testing event logging...")
    event_data = {
        "event_type": "gesture",
        "session_id": SESSION_ID,
        "user_id": USER_ID,
        "lesson_id": LESSON_ID,
        "data": {
            "gesture_type": "open_hand",
            "confidence": 0.95,
            "finger_count": 5
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analytics/events", json=event_data)
        if response.status_code == 200:
            print("✅ Event logged successfully")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to log event: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error logging event: {e}")
    
    # Test 2: Update progress
    print("\n2. Testing progress update...")
    progress_data = {
        "user_id": USER_ID,
        "lesson_id": LESSON_ID,
        "completed": True,
        "score": 85.5,
        "attempts": 1,
        "time_spent": 120
    }
    
    try:
        response = requests.post(f"{BASE_URL}/analytics/progress", json=progress_data)
        if response.status_code == 200:
            print("✅ Progress updated successfully")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to update progress: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error updating progress: {e}")
    
    # Test 3: Get user progress
    print("\n3. Testing user progress retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/progress/{USER_ID}")
        if response.status_code == 200:
            print("✅ User progress retrieved successfully")
            data = response.json()
            if data.get('success'):
                progress = data.get('data', {})
                print(f"   Total lessons: {progress.get('total_lessons', 0)}")
                print(f"   Completed lessons: {progress.get('completed_lessons', 0)}")
                print(f"   Progress percentage: {progress.get('progress_percentage', 0)}%")
            else:
                print(f"   Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed to get user progress: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting user progress: {e}")
    
    # Test 4: Get dashboard data
    print("\n4. Testing dashboard data...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/dashboard/data")
        if response.status_code == 200:
            print("✅ Dashboard data retrieved successfully")
            data = response.json()
            if data.get('success'):
                dashboard = data.get('data', {})
                print(f"   Total users: {dashboard.get('total_users', 0)}")
                print(f"   Total lessons: {dashboard.get('total_lessons', 0)}")
                print(f"   Recent activity: {dashboard.get('recent_activity', 0)}")
            else:
                print(f"   Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed to get dashboard data: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting dashboard data: {e}")
    
    # Test 5: Get lesson analytics
    print("\n5. Testing lesson analytics...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/lessons/{LESSON_ID}/analytics")
        if response.status_code == 200:
            print("✅ Lesson analytics retrieved successfully")
            data = response.json()
            if data.get('success'):
                analytics = data.get('data', {})
                print(f"   Total plays: {analytics.get('total_plays', 0)}")
                print(f"   Completed plays: {analytics.get('completed_plays', 0)}")
                print(f"   Completion rate: {analytics.get('completion_rate', 0)}%")
            else:
                print(f"   Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ Failed to get lesson analytics: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error getting lesson analytics: {e}")
    
    # Test 6: Test chart generation (optional - requires matplotlib)
    print("\n6. Testing chart generation...")
    try:
        response = requests.get(f"{BASE_URL}/analytics/charts/dashboard/overview")
        if response.status_code == 200:
            print("✅ Dashboard chart generated successfully")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
        else:
            print(f"❌ Failed to generate dashboard chart: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error generating chart: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Analytics testing completed!")

def test_script_integration():
    """Test script integration with analytics."""
    print("\n🧪 Testing Script Integration with Analytics")
    print("=" * 50)
    
    # Test script start with analytics
    print("\n1. Testing script start with analytics...")
    script_start_data = {
        "script_id": LESSON_ID,
        "session_id": SESSION_ID,
        "user_id": USER_ID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scripts/{LESSON_ID}/start", json=script_start_data)
        if response.status_code == 200:
            print("✅ Script started successfully")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to start script: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error starting script: {e}")
    
    # Test gesture event with analytics
    print("\n2. Testing gesture event with analytics...")
    gesture_data = {
        "script_id": LESSON_ID,
        "gesture_data": {
            "gesture": "open_hand",
            "confidence": 0.92,
            "landmarks": []
        },
        "session_id": SESSION_ID,
        "user_id": USER_ID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/scripts/{LESSON_ID}/gesture", json=gesture_data)
        if response.status_code == 200:
            print("✅ Gesture event processed successfully")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to process gesture event: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error processing gesture event: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Script integration testing completed!")

if __name__ == "__main__":
    print("🚀 Starting Chandra Analytics Tests")
    print(f"📅 Test started at: {datetime.now()}")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"👤 User ID: {USER_ID}")
    print(f"📚 Lesson ID: {LESSON_ID}")
    print(f"🆔 Session ID: {SESSION_ID}")
    
    try:
        test_analytics_endpoints()
        test_script_integration()
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
    
    print(f"\n📅 Test completed at: {datetime.now()}") 