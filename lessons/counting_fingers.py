"""
counting_fingers - Finger Counting Lesson
A simple lesson that counts fingers and tracks progress using Python tools
"""

# Import useful Python libraries
import math
import random
from collections import Counter

# Lesson configuration
LESSON_NAME = "Counting Fingers"
TARGET_GESTURES = ["fist", "open_hand", "point", "victory", "thumbs_up"]
PROGRESS_PER_GESTURE = 20.0  # 20% per gesture

# Lesson state
total_fingers = 0
gestures_seen = set()
lesson_progress = 0.0
gesture_history = []

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global total_fingers, gestures_seen, lesson_progress, gesture_history
    
    log("INFO", f"Starting lesson: {LESSON_NAME}")
    log("INFO", f"Target gestures: {TARGET_GESTURES}")
    
    # Reset state
    total_fingers = 0
    gestures_seen = set()
    lesson_progress = 0.0
    gesture_history = []
    
    # Update lesson state
    state.update({
        "lesson_name": LESSON_NAME,
        "target_gestures": TARGET_GESTURES,
        "total_fingers": total_fingers,
        "gestures_seen": list(gestures_seen),
        "lesson_progress": lesson_progress,
        "gesture_history": gesture_history,
        "start_time": time.time()
    })
    
    emit("lesson_started", {
        "lesson_name": LESSON_NAME,
        "target_gestures": TARGET_GESTURES,
        "total_gestures": len(TARGET_GESTURES)
    })

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global total_fingers, gestures_seen, lesson_progress, gesture_history
    
    gesture = gesture_data.get("gesture")
    finger_count = gesture_data.get("fingerCount", 0)
    
    if not gesture:
        return
    
    log("INFO", f"Detected gesture: {gesture} ({finger_count} fingers)")
    
    # Add to total fingers
    total_fingers += finger_count
    
    # Track gesture history
    gesture_history.append({
        "gesture": gesture,
        "finger_count": finger_count,
        "timestamp": time.time()
    })
    
    # Track unique gestures
    if gesture in TARGET_GESTURES and gesture not in gestures_seen:
        gestures_seen.add(gesture)
        lesson_progress = min(100.0, len(gestures_seen) * PROGRESS_PER_GESTURE)
        
        log("INFO", f"New gesture! Progress: {lesson_progress:.1f}%")
        
        # Calculate statistics
        if len(gesture_history) > 1:
            finger_counts = [g["finger_count"] for g in gesture_history]
            avg_fingers = sum(finger_counts) / len(finger_counts)
            max_fingers = max(finger_counts)
            min_fingers = min(finger_counts)
            
            log("INFO", f"Statistics - Avg: {avg_fingers:.1f}, Max: {max_fingers}, Min: {min_fingers}")
        
        # Check if lesson is complete
        if lesson_progress >= 100.0:
            log("INFO", "Lesson completed!")
            
            # Calculate final statistics
            gesture_counter = Counter([g["gesture"] for g in gesture_history])
            most_common_gesture = gesture_counter.most_common(1)[0] if gesture_counter else ("none", 0)
            
            emit("lesson_completed", {
                "total_fingers": total_fingers,
                "gestures_seen": list(gestures_seen),
                "final_progress": lesson_progress,
                "total_gestures": len(gesture_history),
                "most_common_gesture": most_common_gesture[0],
                "gesture_frequency": dict(gesture_counter)
            })
    
    # Update state
    state.update({
        "total_fingers": total_fingers,
        "gestures_seen": list(gestures_seen),
        "lesson_progress": lesson_progress,
        "current_gesture": gesture,
        "current_finger_count": finger_count,
        "gesture_history": gesture_history
    })
    
    # Emit gesture event
    emit("gesture_processed", {
        "gesture": gesture,
        "finger_count": finger_count,
        "total_fingers": total_fingers,
        "progress": lesson_progress,
        "gestures_remaining": len(TARGET_GESTURES) - len(gestures_seen)
    })

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = state.get("start_time")
    if start_time:
        duration = time.time() - start_time
        state.set("lesson_duration", duration)
    
    # Calculate real-time statistics
    gesture_history = state.get("gesture_history", [])
    if gesture_history:
        recent_gestures = gesture_history[-10:]  # Last 10 gestures
        avg_fingers = sum(g["finger_count"] for g in recent_gestures) / len(recent_gestures)
        gesture_rate = len(recent_gestures) / 10.0  # gestures per second (assuming 10 second window)
        
        state.update({
            "recent_avg_fingers": avg_fingers,
            "gesture_rate": gesture_rate
        })
    
    # Emit periodic update
    emit("lesson_tick", {
        "total_fingers": state.get("total_fingers"),
        "progress": state.get("lesson_progress"),
        "gestures_seen": state.get("gestures_seen"),
        "gestures_remaining": len(TARGET_GESTURES) - len(state.get("gestures_seen", [])),
        "lesson_duration": state.get("lesson_duration", 0)
    })

@on_complete
def lesson_complete():
    """Called when the lesson is completed"""
    log("INFO", "Lesson cleanup and final statistics")
    
    # Calculate comprehensive statistics
    gesture_history = state.get("gesture_history", [])
    if gesture_history:
        finger_counts = [g["finger_count"] for g in gesture_history]
        gesture_types = [g["gesture"] for g in gesture_history]
        
        stats = {
            "total_gestures": len(gesture_history),
            "total_fingers": sum(finger_counts),
            "average_fingers": sum(finger_counts) / len(finger_counts),
            "max_fingers": max(finger_counts),
            "min_fingers": min(finger_counts),
            "gesture_variety": len(set(gesture_types)),
            "most_common_gesture": Counter(gesture_types).most_common(1)[0] if gesture_types else ("none", 0)
        }
        
        log("INFO", f"Final statistics: {stats}")
        emit("lesson_statistics", stats) 