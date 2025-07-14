"""
letter_tracing - Letter Tracing Lesson
A lesson for practicing letter writing with hand gestures
"""

# Lesson configuration
LESSON_NAME = "Letter Tracing"
LETTERS = ["A", "B", "C", "D", "E"]
CURRENT_LETTER_INDEX = 0

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global CURRENT_LETTER_INDEX
    
    log("INFO", f"Starting letter tracing lesson")
    log("INFO", f"Letters to trace: {LETTERS}")
    
    CURRENT_LETTER_INDEX = 0
    
    set_state("lesson_name", LESSON_NAME)
    set_state("letters", LETTERS)
    set_state("current_letter_index", CURRENT_LETTER_INDEX)
    set_state("current_letter", LETTERS[CURRENT_LETTER_INDEX])
    set_state("lesson_progress", 0.0)
    
    emit_event("lesson_started", {
        "lesson_name": LESSON_NAME,
        "letters": LETTERS,
        "current_letter": LETTERS[CURRENT_LETTER_INDEX]
    })

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global CURRENT_LETTER_INDEX
    
    gesture = gesture_data.get("gesture")
    
    if not gesture:
        return
    
    current_letter = LETTERS[CURRENT_LETTER_INDEX]
    
    # Check if gesture matches letter tracing pattern
    if gesture == "point" and current_letter in ["A", "I", "L"]:
        # Letter completed
        CURRENT_LETTER_INDEX += 1
        progress = (CURRENT_LETTER_INDEX / len(LETTERS)) * 100.0
        
        log("INFO", f"Completed letter {current_letter}! Progress: {progress:.1f}%")
        
        if CURRENT_LETTER_INDEX >= len(LETTERS):
            log("INFO", "All letters completed!")
            emit_event("lesson_completed", {
                "letters_completed": len(LETTERS),
                "final_progress": 100.0
            })
        else:
            next_letter = LETTERS[CURRENT_LETTER_INDEX]
            set_state("current_letter", next_letter)
            set_state("current_letter_index", CURRENT_LETTER_INDEX)
            set_state("lesson_progress", progress)
            
            emit_event("letter_completed", {
                "completed_letter": current_letter,
                "next_letter": next_letter,
                "progress": progress
            })
    
    # Update state
    set_state("current_gesture", gesture)
    set_state("lesson_progress", (CURRENT_LETTER_INDEX / len(LETTERS)) * 100.0)
    
    emit_event("gesture_processed", {
        "gesture": gesture,
        "current_letter": current_letter,
        "progress": (CURRENT_LETTER_INDEX / len(LETTERS)) * 100.0
    })

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = get_state("start_time")
    if start_time:
        duration = time.time() - start_time
        set_state("lesson_duration", duration) 