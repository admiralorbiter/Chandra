"""
letter_tracing - Letter Tracing Lesson
A lesson for practicing letter writing with hand gestures
"""

# Lesson configuration
LESSON_NAME = "Letter Tracing"
LETTERS = ["A", "B", "C", "D", "E"]
CURRENT_LETTER_INDEX = 0

# Letter tracing patterns - simplified movement patterns
LETTER_PATTERNS = {
    "A": {
        "description": "Draw a triangle shape",
        "gestures": ["point", "open_hand"],
        "min_gestures": 2,
        "timeout": 30  # seconds
    },
    "B": {
        "description": "Draw a vertical line with two curves",
        "gestures": ["point", "open_hand", "victory"],
        "min_gestures": 3,
        "timeout": 30
    },
    "C": {
        "description": "Draw a curved line",
        "gestures": ["point", "open_hand"],
        "min_gestures": 2,
        "timeout": 25
    },
    "D": {
        "description": "Draw a vertical line with a curve",
        "gestures": ["point", "open_hand", "thumbs_up"],
        "min_gestures": 3,
        "timeout": 30
    },
    "E": {
        "description": "Draw three horizontal lines connected by a vertical line",
        "gestures": ["point", "open_hand", "victory", "thumbs_up"],
        "min_gestures": 4,
        "timeout": 35
    }
}

# Lesson state
current_letter = None
current_pattern = None
gestures_for_current_letter = []
letter_start_time = None
lesson_progress = 0.0

def get_time():
    # Use the sandbox-provided time module
    return time.time()

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global CURRENT_LETTER_INDEX, current_letter, current_pattern, gestures_for_current_letter
    global letter_start_time, lesson_progress
    
    log("INFO", f"Starting letter tracing lesson")
    log("INFO", f"Letters to trace: {LETTERS}")
    
    # Reset state
    CURRENT_LETTER_INDEX = 0
    current_letter = LETTERS[CURRENT_LETTER_INDEX]
    current_pattern = LETTER_PATTERNS[current_letter]
    gestures_for_current_letter = []
    letter_start_time = get_time()
    lesson_progress = 0.0
    
    # Set initial state
    set_state("lesson_name", LESSON_NAME)
    set_state("letters", LETTERS)
    set_state("current_letter_index", CURRENT_LETTER_INDEX)
    set_state("current_letter", current_letter)
    set_state("current_pattern", current_pattern)
    set_state("gestures_for_current_letter", gestures_for_current_letter)
    set_state("letter_start_time", letter_start_time)
    set_state("lesson_progress", lesson_progress)
    
    emit_event("lesson_started", {
        "lesson_name": LESSON_NAME,
        "letters": LETTERS,
        "current_letter": current_letter,
        "pattern_description": current_pattern["description"]
    })

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global CURRENT_LETTER_INDEX, current_letter, current_pattern, gestures_for_current_letter
    global letter_start_time, lesson_progress
    
    gesture = gesture_data.get("gesture")
    finger_count = gesture_data.get("fingerCount", 0)
    
    if not gesture:
        return
    
    log("INFO", f"Detected gesture: {gesture} ({finger_count} fingers) for letter {current_letter}")
    
    # Add gesture to current letter's gesture list
    gestures_for_current_letter.append(gesture)
    
    # Check if we have enough gestures for the current letter
    required_gestures = current_pattern["gestures"]
    min_gestures = current_pattern["min_gestures"]
    
    # Count how many required gestures we've seen
    seen_required_gestures = set()
    for g in gestures_for_current_letter:
        if g in required_gestures:
            seen_required_gestures.add(g)
    
    log("INFO", f"Seen gestures: {list(seen_required_gestures)} / {required_gestures}")
    
    # Check if letter is completed
    if len(seen_required_gestures) >= min_gestures:
        # Letter completed!
        CURRENT_LETTER_INDEX += 1
        progress = (CURRENT_LETTER_INDEX / len(LETTERS)) * 100.0
        
        log("INFO", f"Completed letter {current_letter}! Progress: {progress:.1f}%")
        
        if CURRENT_LETTER_INDEX >= len(LETTERS):
            # All letters completed!
            log("INFO", "All letters completed!")
            emit_event("lesson_completed", {
                "letters_completed": len(LETTERS),
                "final_progress": 100.0,
                "total_gestures": sum(len(get_state("gestures_for_current_letter")) for _ in range(len(LETTERS)))
            })
        else:
            # Move to next letter
            current_letter = LETTERS[CURRENT_LETTER_INDEX]
            current_pattern = LETTER_PATTERNS[current_letter]
            gestures_for_current_letter = []
            letter_start_time = get_time()
            lesson_progress = progress
            
            set_state("current_letter", current_letter)
            set_state("current_letter_index", CURRENT_LETTER_INDEX)
            set_state("current_pattern", current_pattern)
            set_state("gestures_for_current_letter", gestures_for_current_letter)
            set_state("letter_start_time", letter_start_time)
            set_state("lesson_progress", lesson_progress)
            
            emit_event("letter_completed", {
                "completed_letter": LETTERS[CURRENT_LETTER_INDEX - 1],
                "next_letter": current_letter,
                "progress": lesson_progress,
                "pattern_description": current_pattern["description"]
            })
    
    # Update state
    set_state("current_gesture", gesture)
    set_state("current_finger_count", finger_count)
    set_state("gestures_for_current_letter", gestures_for_current_letter)
    set_state("lesson_progress", lesson_progress)
    
    emit_event("gesture_processed", {
        "gesture": gesture,
        "finger_count": finger_count,
        "current_letter": current_letter,
        "progress": lesson_progress,
        "gestures_for_letter": gestures_for_current_letter
    })

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    global letter_start_time, current_pattern
    
    # Update lesson duration
    start_time = get_state("start_time")
    if start_time:
        duration = get_time() - start_time
        set_state("lesson_duration", duration)
    
    # Check for letter timeout
    if letter_start_time and current_pattern:
        time_elapsed = get_time() - letter_start_time
        timeout = current_pattern["timeout"]
        
        if time_elapsed > timeout:
            log("WARNING", f"Letter {current_letter} timed out after {timeout} seconds")
            emit_event("letter_timeout", {
                "letter": current_letter,
                "time_elapsed": time_elapsed,
                "timeout": timeout
            })
    
    # Emit periodic update
    emit_event("lesson_tick", {
        "current_letter": get_state("current_letter"),
        "progress": get_state("lesson_progress"),
        "gestures_for_letter": get_state("gestures_for_current_letter"),
        "time_elapsed": get_time() - letter_start_time if letter_start_time else 0
    }) 