#!/usr/bin/env python3
"""
Test script for letter tracing functionality
"""

import sys
import os
import time
import json

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.scripts.engine import ScriptSandbox

def test_letter_tracing():
    """Test the letter tracing script"""
    
    # Load the script
    with open('scripts/letter_tracing.py', 'r') as f:
        script_code = f.read()
    
    # Create sandbox
    sandbox = ScriptSandbox('letter_tracing', 'test_session')
    
    # Load the script
    if not sandbox.load_script(script_code):
        print("❌ Failed to load script")
        return False
    
    print("✅ Script loaded successfully")
    
    # Execute the script
    if not sandbox.execute_script():
        print("❌ Failed to execute script")
        return False
    
    print("✅ Script executed successfully")
    
    # Start the script
    if not sandbox.start():
        print("❌ Failed to start script")
        return False
    
    print("✅ Script started successfully")
    
    # Test gesture handling
    test_gestures = [
        {"gesture": "point", "fingerCount": 1},
        {"gesture": "open_hand", "fingerCount": 5},
        {"gesture": "victory", "fingerCount": 2},
        {"gesture": "thumbs_up", "fingerCount": 1},
        {"gesture": "point", "fingerCount": 1},
        {"gesture": "open_hand", "fingerCount": 5},
        {"gesture": "victory", "fingerCount": 2},
        {"gesture": "thumbs_up", "fingerCount": 1},
        {"gesture": "point", "fingerCount": 1},
        {"gesture": "open_hand", "fingerCount": 5},
        {"gesture": "victory", "fingerCount": 2},
        {"gesture": "thumbs_up", "fingerCount": 1},
        {"gesture": "point", "fingerCount": 1},
        {"gesture": "open_hand", "fingerCount": 5},
        {"gesture": "victory", "fingerCount": 2},
        {"gesture": "thumbs_up", "fingerCount": 1},
        {"gesture": "point", "fingerCount": 1},
        {"gesture": "open_hand", "fingerCount": 5},
        {"gesture": "victory", "fingerCount": 2},
        {"gesture": "thumbs_up", "fingerCount": 1},
        {"gesture": "point", "fingerCount": 1},
        {"gesture": "open_hand", "fingerCount": 5},
        {"gesture": "victory", "fingerCount": 2},
        {"gesture": "thumbs_up", "fingerCount": 1},
        {"gesture": "point", "fingerCount": 1},
        {"gesture": "open_hand", "fingerCount": 5},
        {"gesture": "victory", "fingerCount": 2},
        {"gesture": "thumbs_up", "fingerCount": 1},
    ]
    
    print("\n🧪 Testing gesture processing...")
    
    for i, gesture in enumerate(test_gestures):
        print(f"  Gesture {i+1}: {gesture['gesture']} ({gesture['fingerCount']} fingers)")
        sandbox.handle_gesture(gesture)
        
        # Get current state
        state = sandbox.get_state()
        current_letter = state.get('current_letter', 'Unknown')
        progress = state.get('lesson_progress', 0.0)
        
        print(f"    Current letter: {current_letter}")
        print(f"    Progress: {progress:.1f}%")
        
        # Check if lesson is complete
        if progress >= 100.0:
            print("🎉 Lesson completed!")
            break
        
        time.sleep(0.1)  # Small delay for readability
    
    # Test tick functionality
    print("\n⏰ Testing tick functionality...")
    for i in range(5):
        sandbox.tick()
        time.sleep(0.1)
    
    # Get final state
    final_state = sandbox.get_state()
    print(f"\n📊 Final state:")
    print(f"  Lesson name: {final_state.get('lesson_name', 'Unknown')}")
    print(f"  Current letter: {final_state.get('current_letter', 'Unknown')}")
    print(f"  Progress: {final_state.get('lesson_progress', 0.0):.1f}%")
    print(f"  Gestures for current letter: {final_state.get('gestures_for_current_letter', [])}")
    
    # Stop the script
    sandbox.stop()
    print("✅ Script stopped successfully")
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Letter Tracing Script")
    print("=" * 40)
    
    success = test_letter_tracing()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1) 