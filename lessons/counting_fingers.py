"""
counting_fingers - Finger Counting Lesson
A simple lesson that counts fingers and tracks progress
"""

import time

# Lesson configuration
LESSON_NAME = "Counting Fingers"
TARGET_GESTURES = ["fist", "open_hand", "point", "victory", "thumbs_up"]
PROGRESS_PER_GESTURE = 20.0  # 20% per gesture

# Lesson state
total_fingers = 0
gestures_seen = set()
lesson_progress = 0.0

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global total_fingers, gestures_seen, lesson_progress
    
    log("INFO", f"Starting lesson: {LESSON_NAME}")
    log("INFO", f"Target gestures: {TARGET_GESTURES}")
    
    # Reset state
    total_fingers = 0
    gestures_seen = set()
    lesson_progress = 0.0
    
    # Update lesson state
    state.set("lesson_name", LESSON_NAME)
    state.set("target_gestures", TARGET_GESTURES)
    state.set("total_fingers", total_fingers)
    state.set("gestures_seen", list(gestures_seen))
    state.set("lesson_progress", lesson_progress)
    
    emit("lesson_started", {
        "lesson_name": LESSON_NAME,
        "target_gestures": TARGET_GESTURES
    })

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global total_fingers, gestures_seen, lesson_progress
    
    gesture = gesture_data.get("gesture")
    finger_count = gesture_data.get("fingerCount", 0)
    
    if not gesture:
        return
    
    log("INFO", f"Detected gesture: {gesture} ({finger_count} fingers)")
    
    # Add to total fingers
    total_fingers += finger_count
    
    # Track unique gestures
    if gesture in TARGET_GESTURES and gesture not in gestures_seen:
        gestures_seen.add(gesture)
        lesson_progress = min(100.0, len(gestures_seen) * PROGRESS_PER_GESTURE)
        
        log("INFO", f"New gesture! Progress: {lesson_progress:.1f}%")
        
        # Check if lesson is complete
        if lesson_progress >= 100.0:
            log("INFO", "Lesson completed!")
            emit("lesson_completed", {
                "total_fingers": total_fingers,
                "gestures_seen": list(gestures_seen),
                "final_progress": lesson_progress
            })
    
    # Update state
    state.set("total_fingers", total_fingers)
    state.set("gestures_seen", list(gestures_seen))
    state.set("lesson_progress", lesson_progress)
    state.set("current_gesture", gesture)
    state.set("current_finger_count", finger_count)
    
    # Emit gesture event
    emit("gesture_processed", {
        "gesture": gesture,
        "finger_count": finger_count,
        "total_fingers": total_fingers,
        "progress": lesson_progress
    })

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = state.get("start_time")
    if start_time:
        duration = time.time() - start_time
        state.set("lesson_duration", duration)
    
    # Emit periodic update
    emit("lesson_tick", {
        "total_fingers": state.get("total_fingers"),
        "progress": state.get("lesson_progress"),
        "gestures_seen": state.get("gestures_seen")
    }) 