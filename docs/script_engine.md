# Chandra Script Engine Documentation

The Chandra Script Engine provides a sandboxed Python execution environment for creating interactive educational lessons. Scripts can respond to gestures, manage lesson state, and provide real-time feedback to users.

## Overview

The script engine consists of several key components:

- **ScriptSandbox**: Secure Python execution environment
- **ScriptOrchestrator**: Manages script lifecycle and events
- **ScriptManager**: Handles file operations and hot reloading
- **WebSocket Integration**: Real-time communication with frontend

## Script Structure

Scripts are Python files that use decorators to define hooks for different events:

```python
"""
my_lesson - My Custom Lesson
A description of what this lesson does
"""

# Lesson configuration
LESSON_NAME = "My Lesson"
TARGET_GESTURES = ["fist", "open_hand", "point"]

# Lesson state
gesture_count = 0
lesson_progress = 0.0

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global gesture_count, lesson_progress
    
    log("INFO", f"Starting lesson: {LESSON_NAME}")
    
    # Reset state
    gesture_count = 0
    lesson_progress = 0.0
    
    # Update lesson state
    set_state("lesson_name", LESSON_NAME)
    set_state("gesture_count", gesture_count)
    set_state("lesson_progress", lesson_progress)
    
    emit_event("lesson_started", {
        "lesson_name": LESSON_NAME
    })

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global gesture_count, lesson_progress
    
    gesture = gesture_data.get("gesture")
    finger_count = gesture_data.get("fingerCount", 0)
    
    if not gesture:
        return
    
    log("INFO", f"Detected gesture: {gesture} ({finger_count} fingers)")
    
    # Increment gesture count
    gesture_count += 1
    
    # Update progress
    lesson_progress = min(100.0, gesture_count * 10.0)
    
    # Update state
    set_state("gesture_count", gesture_count)
    set_state("lesson_progress", lesson_progress)
    set_state("current_gesture", gesture)
    set_state("current_finger_count", finger_count)
    
    # Emit gesture event
    emit_event("gesture_processed", {
        "gesture": gesture,
        "finger_count": finger_count,
        "gesture_count": gesture_count,
        "progress": lesson_progress
    })
    
    # Check if lesson is complete
    if lesson_progress >= 100.0:
        log("INFO", "Lesson completed!")
        emit_event("lesson_completed", {
            "final_gesture_count": gesture_count,
            "final_progress": lesson_progress
        })

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = get_state("start_time")
    if start_time:
        duration = time.time() - start_time
        set_state("lesson_duration", duration)
    
    # Emit periodic update
    emit_event("lesson_tick", {
        "gesture_count": get_state("gesture_count"),
        "progress": get_state("lesson_progress")
    })
```

## Available Hooks

### @on_start
Called when the script starts. Use this to initialize lesson state and configuration.

```python
@on_start
def lesson_start():
    # Initialize lesson
    set_state("lesson_name", "My Lesson")
    set_state("progress", 0.0)
    emit_event("lesson_started", {"name": "My Lesson"})
```

### @on_gesture
Called when a gesture is detected. Receives gesture data including:
- `gesture`: The detected gesture name (e.g., "fist", "open_hand", "point")
- `fingerCount`: Number of fingers detected
- `confidence`: Confidence score of the detection

```python
@on_gesture
def handle_gesture(gesture_data):
    gesture = gesture_data.get("gesture")
    finger_count = gesture_data.get("fingerCount", 0)
    
    # Process the gesture
    if gesture == "open_hand":
        # Handle open hand gesture
        pass
```

### @on_tick
Called periodically (every second by default). Use for time-based updates.

```python
@on_tick
def lesson_tick():
    # Update timers, progress, etc.
    duration = time.time() - get_state("start_time", 0)
    set_state("duration", duration)
```

## Available API Functions

### State Management

#### `set_state(key, value)`
Set a value in the script's state.

```python
set_state("progress", 50.0)
set_state("current_gesture", "fist")
```

#### `get_state(key=None)`
Get a value from the script's state. If no key is provided, returns the entire state.

```python
progress = get_state("progress")
entire_state = get_state()  # Returns all state
```

### Logging

#### `log(level, message)`
Log a message with the specified level (DEBUG, INFO, WARNING, ERROR).

```python
log("INFO", "Lesson started successfully")
log("WARNING", "Low confidence gesture detected")
log("ERROR", "Failed to process gesture")
```

### Event Emission

#### `emit_event(event_type, data=None)`
Emit a custom event with optional data.

```python
emit_event("gesture_processed", {
    "gesture": "fist",
    "confidence": 0.95
})

emit_event("lesson_completed", {
    "final_score": 100,
    "duration": 120.5
})
```

### Safe Functions

The script sandbox provides access to safe Python functions:

- **Built-in functions**: `len()`, `str()`, `int()`, `float()`, `bool()`, `list()`, `dict()`, `tuple()`, `set()`, `range()`, `enumerate()`, `zip()`, `min()`, `max()`, `sum()`, `abs()`, `round()`, `chr()`, `ord()`, `hex()`, `oct()`, `bin()`, `format()`, `repr()`, `ascii()`
- **Math functions**: All functions from the `math` module (sin, cos, sqrt, etc.)
- **String operations**: All standard string methods
- **List/Dict operations**: All standard list and dict methods

## Security

The script engine uses RestrictedPython to provide a secure execution environment:

- **No file system access**: Scripts cannot read or write files
- **No network access**: Scripts cannot make network requests
- **No dangerous imports**: Restricted imports like `os`, `sys`, `subprocess` are blocked
- **No eval/exec**: Dynamic code execution is prevented
- **Memory limits**: Scripts have memory and execution time limits

## Creating Scripts

### Using the Web Interface

1. Navigate to `/scripts` in your browser
2. Click "Create New Script"
3. Enter a script ID and select a template
4. Edit the script in the code editor
5. Click "Save Script" to save your changes
6. Use "Validate" to check for errors
7. Use "Start" to run the script

### Using the CLI Tool

```bash
# Create a new script
python eductl.py new-script my_lesson --template counting_fingers

# List all scripts
python eductl.py list-scripts

# Run a script
python eductl.py run my_lesson

# Validate a script
python eductl.py validate my_lesson

# Show script information
python eductl.py info my_lesson

# Export scripts
python eductl.py export --zip
```

### Using the API

```bash
# List scripts
curl http://localhost:5000/scripts/

# Get script content
curl http://localhost:5000/scripts/my_lesson

# Create script
curl -X POST http://localhost:5000/scripts/ \
  -H "Content-Type: application/json" \
  -d '{"script_id": "my_lesson", "template": "basic"}'

# Update script
curl -X PUT http://localhost:5000/scripts/my_lesson \
  -H "Content-Type: application/json" \
  -d '{"content": "# My script content"}'

# Start script
curl -X POST http://localhost:5000/scripts/my_lesson/start

# Stop script
curl -X POST http://localhost:5000/scripts/my_lesson/stop

# Get script state
curl http://localhost:5000/scripts/my_lesson/state

# Get script events
curl http://localhost:5000/scripts/my_lesson/events
```

## WebSocket Events

The script engine supports real-time communication via WebSocket:

### Client to Server

```javascript
// Start a script
socket.emit('script_start', { script_id: 'my_lesson' });

// Stop a script
socket.emit('script_stop', { script_id: 'my_lesson' });

// Send gesture data
socket.emit('script_gesture', {
    script_id: 'my_lesson',
    gesture_data: {
        gesture: 'fist',
        fingerCount: 0,
        confidence: 0.95
    }
});

// Get script state
socket.emit('get_script_state', { script_id: 'my_lesson' });
```

### Server to Client

```javascript
// Script started
socket.on('script_started', (data) => {
    console.log('Script started:', data);
});

// Script stopped
socket.on('script_stopped', (data) => {
    console.log('Script stopped:', data);
});

// Gesture processed
socket.on('script_gesture_processed', (data) => {
    console.log('Gesture processed:', data);
});

// Script state update
socket.on('script_state', (data) => {
    console.log('Script state:', data);
});
```

## Templates

The script engine provides several templates to get you started:

### Basic Template
A simple template with basic hooks for gesture detection and progress tracking.

### Counting Fingers Template
A lesson that counts fingers and tracks progress through different gestures.

### Letter Tracing Template
A lesson for practicing letter writing with gesture recognition.

## Best Practices

1. **Use descriptive names**: Choose clear, descriptive names for your scripts and variables
2. **Handle errors gracefully**: Always check for None values and handle edge cases
3. **Log important events**: Use the `log()` function to track important events
4. **Update state consistently**: Always update state when processing gestures
5. **Emit meaningful events**: Emit events with relevant data for the frontend
6. **Keep scripts focused**: Each script should have a single, clear purpose
7. **Test thoroughly**: Use the validation feature and test with different gestures
8. **Document your scripts**: Include clear docstrings and comments

## Troubleshooting

### Common Issues

1. **Script not loading**: Check that the script file exists and has valid Python syntax
2. **Gestures not detected**: Ensure the gesture engine is running and the camera is working
3. **State not updating**: Make sure you're calling `set_state()` with the correct parameters
4. **Events not firing**: Check that your event handlers are properly decorated
5. **Validation errors**: Review the validation output for syntax or security issues

### Debugging Tips

1. **Use logging**: Add `log()` statements to track script execution
2. **Check state**: Use the web interface to inspect script state
3. **Monitor events**: Watch the events panel for real-time updates
4. **Validate frequently**: Use the validation feature to catch issues early
5. **Test incrementally**: Build and test your script in small pieces

## Examples

See the `scripts/` directory for example scripts:
- `counting_fingers.py`: Finger counting lesson
- `letter_tracing.py`: Letter writing practice

These examples demonstrate various techniques and patterns you can use in your own scripts. 