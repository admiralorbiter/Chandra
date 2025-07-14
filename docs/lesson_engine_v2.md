# Chandra Lesson Engine v2

The Chandra Lesson Engine v2 provides a robust, Python-native environment for creating interactive educational lessons that leverage the full power of Python's data science and machine learning ecosystem.

## Overview

The new lesson engine replaces the restrictive sandbox approach with a flexible Python execution environment that allows you to use popular Python libraries like numpy, pandas, matplotlib, scipy, and sklearn. This enables the creation of sophisticated data analysis, machine learning, and scientific computing lessons.

## Key Features

### 🔧 Robust Python Environment
- **Flexible Execution**: No more restricted sandbox limitations
- **Python Tool Integration**: Full access to numpy, pandas, matplotlib, scipy, sklearn
- **Safe Module System**: Controlled import system with allowlist
- **Better Error Handling**: Comprehensive debugging and error reporting

### 📊 Enhanced Lesson API
- **Clean State Management**: `state.update()` and `state.get()` for easy state handling
- **Improved Events**: `emit()` and `log()` for better event system
- **Decorator Hooks**: `@on_start`, `@on_gesture`, `@on_tick`, `@on_complete`
- **Lifecycle Management**: Better lesson start, stop, and cleanup

### 🎯 Python Tool Integration
- **Data Science**: numpy, pandas, matplotlib for data analysis
- **Machine Learning**: scipy, sklearn for ML lessons
- **Real-time Processing**: Live data analysis and visualization
- **Statistical Analysis**: Built-in statistical functions and tools

## Lesson Structure

### Basic Lesson Template

```python
"""
my_lesson - My Interactive Lesson
A lesson that demonstrates Python tool usage
"""

# Import Python libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

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
    state.update({
        "lesson_name": LESSON_NAME,
        "gesture_count": gesture_count,
        "lesson_progress": lesson_progress
    })
    
    emit("lesson_started", {
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
    
    # Your lesson logic here
    gesture_count += 1
    lesson_progress = min(100.0, gesture_count * 10.0)
    
    # Update state
    state.update({
        "gesture_count": gesture_count,
        "lesson_progress": lesson_progress,
        "current_gesture": gesture,
        "current_finger_count": finger_count
    })
    
    # Emit events
    emit("gesture_processed", {
        "gesture": gesture,
        "finger_count": finger_count,
        "gesture_count": gesture_count,
        "progress": lesson_progress
    })
    
    # Check completion
    if lesson_progress >= 100.0:
        log("INFO", "Lesson completed!")
        emit("lesson_completed", {
            "final_progress": lesson_progress,
            "total_gestures": gesture_count
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
        "gesture_count": state.get("gesture_count"),
        "progress": state.get("lesson_progress")
    })

@on_complete
def lesson_complete():
    """Called when the lesson is completed"""
    log("INFO", "Lesson cleanup and final statistics")
    
    # Calculate final statistics
    gesture_count = state.get("gesture_count", 0)
    duration = state.get("lesson_duration", 0)
    
    stats = {
        "total_gestures": gesture_count,
        "duration": duration,
        "gestures_per_minute": (gesture_count / duration * 60) if duration > 0 else 0
    }
    
    log("INFO", f"Final statistics: {stats}")
    emit("lesson_statistics", stats)
```

## Available Python Libraries

### Core Libraries
- **numpy**: Numerical computing and array operations
- **pandas**: Data manipulation and analysis
- **matplotlib**: Data visualization and plotting
- **scipy**: Scientific computing and optimization
- **sklearn**: Machine learning algorithms
- **seaborn**: Statistical data visualization

### Standard Libraries
- **math**: Mathematical functions
- **random**: Random number generation
- **collections**: Data structures (Counter, defaultdict, etc.)
- **itertools**: Iteration tools
- **functools**: Function tools
- **json**: JSON handling
- **time**: Time utilities
- **datetime**: Date/time handling

## State Management

### Using the State API

```python
# Update multiple state values
state.update({
    "gesture_count": 5,
    "lesson_progress": 50.0,
    "current_gesture": "fist"
})

# Get a single state value
gesture_count = state.get("gesture_count", 0)

# Set a single state value
state.set("new_value", 42)

# Get all state
all_state = state.to_dict()
```

## Event System

### Emitting Events

```python
# Emit a simple event
emit("gesture_detected", {
    "gesture": "fist",
    "timestamp": time.time()
})

# Emit complex data
emit("analysis_complete", {
    "type": "correlation",
    "results": {
        "correlation": 0.85,
        "p_value": 0.001
    }
})
```

### Logging

```python
# Different log levels
log("INFO", "Lesson started successfully")
log("WARNING", "Gesture not recognized")
log("ERROR", "Failed to process data")
log("DEBUG", "Processing gesture data...")
```

## Data Science Examples

### Statistical Analysis Lesson

```python
import numpy as np
import pandas as pd
from scipy import stats

# Generate sample data
data = np.random.normal(0, 1, 100)
df = pd.DataFrame({'values': data})

@on_gesture
def handle_gesture(gesture_data):
    gesture = gesture_data.get("gesture")
    
    if gesture == "fist":
        # Calculate descriptive statistics
        stats_result = {
            "mean": float(df['values'].mean()),
            "std": float(df['values'].std()),
            "median": float(df['values'].median()),
            "skewness": float(df['values'].skew()),
            "kurtosis": float(df['values'].kurtosis())
        }
        
        emit("statistics_complete", stats_result)
    
    elif gesture == "open_hand":
        # Perform hypothesis test
        t_stat, p_value = stats.ttest_1samp(df['values'], 0)
        
        emit("hypothesis_test_complete", {
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "significant": p_value < 0.05
        })
```

### Machine Learning Lesson

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# Generate sample data
X = np.random.rand(100, 2)
y = X[:, 0] * 2 + X[:, 1] * 3 + np.random.normal(0, 0.1, 100)

@on_gesture
def handle_gesture(gesture_data):
    gesture = gesture_data.get("gesture")
    
    if gesture == "point":
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # Train model
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        score = model.score(X_test, y_test)
        
        emit("model_trained", {
            "coefficients": model.coef_.tolist(),
            "intercept": float(model.intercept_),
            "r2_score": float(score)
        })
```

## CLI Usage

### Creating Lessons

```bash
# Create a basic lesson
eductl new-lesson my_lesson

# Create a lesson with specific template
eductl new-lesson data_analysis --template data_analysis

# Create a counting fingers lesson
eductl new-lesson finger_counting --template counting_fingers
```

### Managing Lessons

```bash
# List all lessons
eductl list-lessons

# Run a lesson
eductl run my_lesson

# Validate a lesson
eductl validate my_lesson

# Analyze lesson complexity
eductl analyze my_lesson

# Show lesson information
eductl info my_lesson
```

### Installing Dependencies

```bash
# Install lesson dependencies
eductl install-deps

# Export lessons
eductl export --zip
```

## API Endpoints

### REST API

```bash
# List all lessons
GET /scripts/lessons

# Get lesson information
GET /scripts/lessons/{lesson_id}

# Create a new lesson
POST /scripts/lessons
{
    "lesson_id": "my_lesson",
    "template": "basic"
}

# Update lesson content
PUT /scripts/lessons/{lesson_id}
{
    "content": "# Lesson code here..."
}

# Start a lesson
POST /scripts/lessons/{lesson_id}/start

# Stop a lesson
POST /scripts/lessons/{lesson_id}/stop

# Get lesson state
GET /scripts/lessons/{lesson_id}/state

# Validate a lesson
POST /scripts/lessons/{lesson_id}/validate

# Analyze a lesson
GET /scripts/lessons/{lesson_id}/analyze
```

### WebSocket Events

```javascript
// Start a lesson
socket.emit('lesson_start', {
    lesson_id: 'my_lesson',
    session_id: 'session_123',
    user_id: 'user_456'
});

// Handle gesture
socket.emit('lesson_gesture', {
    lesson_id: 'my_lesson',
    gesture_data: {
        gesture: 'fist',
        fingerCount: 0
    }
});

// Get lesson state
socket.emit('get_lesson_state', {
    lesson_id: 'my_lesson'
});

// Listen for events
socket.on('lesson_started', (data) => {
    console.log('Lesson started:', data);
});

socket.on('gesture_processed', (data) => {
    console.log('Gesture processed:', data);
});

socket.on('lesson_state', (data) => {
    console.log('Lesson state:', data);
});
```

## Best Practices

### 1. State Management
- Use `state.update()` for multiple values
- Use `state.get()` with defaults for safety
- Keep state updates atomic

### 2. Event Handling
- Use descriptive event names
- Include relevant data in events
- Handle errors gracefully

### 3. Python Tool Usage
- Import libraries at the top
- Use try/except for library operations
- Provide fallbacks for missing libraries

### 4. Performance
- Avoid heavy computations in gesture handlers
- Use periodic ticks for background processing
- Cache expensive calculations

### 5. Error Handling
- Log errors with context
- Provide user-friendly error messages
- Gracefully handle missing data

## Migration from v1

### Key Changes
1. **Directory**: `scripts/` → `lessons/`
2. **API**: `set_state()` → `state.update()`
3. **Events**: `emit_event()` → `emit()`
4. **Logging**: `log()` function instead of print
5. **CLI**: `eductl.py` → `eductl_v2.py`

### Migration Steps
1. Move lesson files from `scripts/` to `lessons/`
2. Update API calls in lesson code
3. Update CLI commands
4. Test lessons with new engine

## Troubleshooting

### Common Issues

1. **Import Errors**: Check if library is in SAFE_MODULES
2. **State Issues**: Use `state.get()` with defaults
3. **Event Problems**: Check event names and data structure
4. **Performance**: Move heavy work to tick handlers

### Debug Tips

1. Use `log("DEBUG", "message")` for debugging
2. Check lesson state with `eductl info <lesson>`
3. Validate lessons with `eductl validate <lesson>`
4. Analyze complexity with `eductl analyze <lesson>`

## Future Enhancements

- **More Libraries**: Additional scientific computing libraries
- **Visualization**: Real-time plotting and charts
- **Machine Learning**: Pre-trained models and datasets
- **Collaboration**: Multi-user lesson sessions
- **Analytics**: Advanced lesson analytics and insights 