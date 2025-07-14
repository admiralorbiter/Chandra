"""
Chandra Lesson Manager v2
Handles lesson file operations, hot reloading, and lesson discovery
"""

import os
import json
import time
import logging
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .engine import LessonMetadata, LessonOrchestrator

class LessonFileHandler(FileSystemEventHandler):
    """File system event handler for lesson hot reloading"""
    
    def __init__(self, lesson_manager):
        self.lesson_manager = lesson_manager
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            lesson_path = Path(event.src_path)
            lesson_id = lesson_path.stem
            logging.info(f"Lesson file modified: {lesson_id}")
            self.lesson_manager.reload_lesson(lesson_id)
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            lesson_path = Path(event.src_path)
            lesson_id = lesson_path.stem
            logging.info(f"New lesson file created: {lesson_id}")
            self.lesson_manager.load_lesson_from_file(lesson_id)
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            lesson_path = Path(event.src_path)
            lesson_id = lesson_path.stem
            logging.info(f"Lesson file deleted: {lesson_id}")
            self.lesson_manager.unload_lesson(lesson_id)

class LessonManager:
    """Manages lesson files, metadata, and hot reloading"""
    
    def __init__(self, lessons_dir: str = "lessons"):
        self.lessons_dir = Path(lessons_dir)
        self.orchestrator = LessonOrchestrator()
        self.lesson_files: Dict[str, Path] = {}
        self.lesson_metadata: Dict[str, LessonMetadata] = {}
        self.file_observer = None
        self.last_reload = {}
        
        # Ensure lessons directory exists
        self.lessons_dir.mkdir(exist_ok=True)
        
        # Initialize file watcher
        self._setup_file_watcher()
        
        # Load existing lessons
        self._discover_lessons()
    
    def _setup_file_watcher(self):
        """Set up file system watcher for hot reloading"""
        try:
            self.file_observer = Observer()
            event_handler = LessonFileHandler(self)
            self.file_observer.schedule(event_handler, str(self.lessons_dir), recursive=False)
            self.file_observer.start()
            logging.info("File watcher started for hot reloading")
        except Exception as e:
            logging.error(f"Failed to start file watcher: {e}")
    
    def _discover_lessons(self):
        """Discover and load all lessons in the lessons directory"""
        for lesson_file in self.lessons_dir.glob("*.py"):
            if lesson_file.name.startswith('_'):
                continue  # Skip private files
            
            lesson_id = lesson_file.stem
            self.load_lesson_from_file(lesson_id)
    
    def load_lesson_from_file(self, lesson_id: str) -> bool:
        """Load a lesson from file"""
        lesson_file = self.lessons_dir / f"{lesson_id}.py"
        metadata_file = self.lessons_dir / f"{lesson_id}.json"
        
        if not lesson_file.exists():
            logging.error(f"Lesson file not found: {lesson_file}")
            return False
        
        try:
            # Read lesson code
            with open(lesson_file, 'r', encoding='utf-8') as f:
                lesson_code = f.read()
            
            # Read or create metadata
            metadata = self._load_or_create_metadata(lesson_id, metadata_file)
            
            # Store file reference
            self.lesson_files[lesson_id] = lesson_file
            self.lesson_metadata[lesson_id] = metadata
            
            # Load into orchestrator
            success = self.orchestrator.load_lesson(lesson_id, lesson_code, metadata)
            
            if success:
                logging.info(f"Loaded lesson: {lesson_id}")
            else:
                logging.error(f"Failed to load lesson: {lesson_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error loading lesson {lesson_id}: {e}")
            return False
    
    def _load_or_create_metadata(self, lesson_id: str, metadata_file: Path) -> LessonMetadata:
        """Load existing metadata or create new metadata"""
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return LessonMetadata(**data)
            except Exception as e:
                logging.warning(f"Failed to load metadata for {lesson_id}: {e}")
        
        # Create new metadata
        metadata = LessonMetadata(
            id=lesson_id,
            name=lesson_id.replace('_', ' ').title(),
            description=f"Lesson {lesson_id}",
            author="system",
            version="1.0.0",
            created=time.strftime("%Y-%m-%d"),
            tags=["interactive", "education"],
            difficulty="beginner",
            duration=10,
            requirements=[],
            dependencies=[]
        )
        
        # Save metadata
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata.__dict__, f, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save metadata for {lesson_id}: {e}")
        
        return metadata
    
    def reload_lesson(self, lesson_id: str) -> bool:
        """Reload a lesson from file"""
        # Prevent rapid reloading
        current_time = time.time()
        if lesson_id in self.last_reload:
            if current_time - self.last_reload[lesson_id] < 1.0:  # 1 second cooldown
                return True
        
        self.last_reload[lesson_id] = current_time
        
        # Stop the lesson if it's running
        self.orchestrator.stop_lesson(lesson_id)
        
        # Reload from file
        success = self.load_lesson_from_file(lesson_id)
        
        if success:
            logging.info(f"Reloaded lesson: {lesson_id}")
        else:
            logging.error(f"Failed to reload lesson: {lesson_id}")
        
        return success
    
    def unload_lesson(self, lesson_id: str):
        """Unload a lesson"""
        # Stop the lesson if it's running
        self.orchestrator.stop_lesson(lesson_id)
        
        # Remove from tracking
        self.lesson_files.pop(lesson_id, None)
        self.lesson_metadata.pop(lesson_id, None)
        
        logging.info(f"Unloaded lesson: {lesson_id}")
    
    def create_lesson(self, lesson_id: str, template: str = "basic") -> bool:
        """Create a new lesson with a template"""
        lesson_file = self.lessons_dir / f"{lesson_id}.py"
        
        if lesson_file.exists():
            logging.error(f"Lesson {lesson_id} already exists")
            return False
        
        try:
            # Create lesson content based on template
            lesson_content = self._get_lesson_template(template, lesson_id)
            
            # Write lesson file
            with open(lesson_file, 'w', encoding='utf-8') as f:
                f.write(lesson_content)
            
            # Load the new lesson
            success = self.load_lesson_from_file(lesson_id)
            
            if success:
                logging.info(f"Created new lesson: {lesson_id}")
            else:
                # Clean up if loading failed
                lesson_file.unlink(missing_ok=True)
                logging.error(f"Failed to create lesson: {lesson_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error creating lesson {lesson_id}: {e}")
            return False
    
    def _get_lesson_template(self, template: str, lesson_id: str) -> str:
        """Get lesson template content"""
        if template == "counting_fingers":
            return f'''"""
{lesson_id} - Finger Counting Lesson
A simple lesson that counts fingers and tracks progress
"""

# Lesson configuration
LESSON_NAME = "{lesson_id.replace('_', ' ').title()}"
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
    
    log("INFO", f"Starting lesson: {{LESSON_NAME}}")
    log("INFO", f"Target gestures: {{TARGET_GESTURES}}")
    
    # Reset state
    total_fingers = 0
    gestures_seen = set()
    lesson_progress = 0.0
    
    # Update lesson state
    state.update({{
        "lesson_name": LESSON_NAME,
        "target_gestures": TARGET_GESTURES,
        "total_fingers": total_fingers,
        "gestures_seen": list(gestures_seen),
        "lesson_progress": lesson_progress
    }})
    
    emit("lesson_started", {{
        "lesson_name": LESSON_NAME,
        "target_gestures": TARGET_GESTURES
    }})

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global total_fingers, gestures_seen, lesson_progress
    
    gesture = gesture_data.get("gesture")
    finger_count = gesture_data.get("fingerCount", 0)
    
    if not gesture:
        return
    
    log("INFO", f"Detected gesture: {{gesture}} ({{finger_count}} fingers)")
    
    # Add to total fingers
    total_fingers += finger_count
    
    # Track unique gestures
    if gesture in TARGET_GESTURES and gesture not in gestures_seen:
        gestures_seen.add(gesture)
        lesson_progress = min(100.0, len(gestures_seen) * PROGRESS_PER_GESTURE)
        
        log("INFO", f"New gesture! Progress: {{lesson_progress:.1f}}%")
        
        # Check if lesson is complete
        if lesson_progress >= 100.0:
            log("INFO", "Lesson completed!")
            emit("lesson_completed", {{
                "total_fingers": total_fingers,
                "gestures_seen": list(gestures_seen),
                "final_progress": lesson_progress
            }})
    
    # Update state
    state.update({{
        "total_fingers": total_fingers,
        "gestures_seen": list(gestures_seen),
        "lesson_progress": lesson_progress,
        "current_gesture": gesture,
        "current_finger_count": finger_count
    }})
    
    # Emit gesture event
    emit("gesture_processed", {{
        "gesture": gesture,
        "finger_count": finger_count,
        "total_fingers": total_fingers,
        "progress": lesson_progress
    }})

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = state.get("_started")
    if start_time:
        duration = time.time() - start_time
        state.set("lesson_duration", duration)
    
    # Emit periodic update
    emit("lesson_tick", {{
        "total_fingers": state.get("total_fingers"),
        "progress": state.get("lesson_progress"),
        "gestures_seen": state.get("gestures_seen")
    }})
'''
        
        elif template == "data_analysis":
            return f'''"""
{lesson_id} - Data Analysis Lesson
A lesson that uses Python data science tools
"""

# Import data science libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Lesson configuration
LESSON_NAME = "{lesson_id.replace('_', ' ').title()}"
DATA_POINTS = 100

# Generate sample data
data = np.random.normal(0, 1, DATA_POINTS)
df = pd.DataFrame({{
    'values': data,
    'squared': data ** 2,
    'cubed': data ** 3
}})

@on_start
def lesson_start():
    """Called when the lesson starts"""
    log("INFO", f"Starting data analysis lesson: {{LESSON_NAME}}")
    
    # Store data in state
    state.update({{
        "lesson_name": LESSON_NAME,
        "data_points": DATA_POINTS,
        "mean": float(df['values'].mean()),
        "std": float(df['values'].std()),
        "min": float(df['values'].min()),
        "max": float(df['values'].max())
    }})
    
    emit("lesson_started", {{
        "lesson_name": LESSON_NAME,
        "data_points": DATA_POINTS,
        "statistics": {{
            "mean": state.get("mean"),
            "std": state.get("std"),
            "min": state.get("min"),
            "max": state.get("max")
        }}
    }})

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    gesture = gesture_data.get("gesture")
    
    if not gesture:
        return
    
    log("INFO", f"Processing gesture: {{gesture}}")
    
    # Different gestures trigger different analyses
    if gesture == "fist":
        # Calculate percentiles
        percentiles = [25, 50, 75]
        values = [float(df['values'].quantile(p/100)) for p in percentiles]
        state.update({{"percentiles": values}})
        
        emit("analysis_complete", {{
            "type": "percentiles",
            "values": values
        }})
    
    elif gesture == "open_hand":
        # Calculate correlation
        corr = float(df['values'].corr(df['squared']))
        state.set("correlation", corr)
        
        emit("analysis_complete", {{
            "type": "correlation",
            "value": corr
        }})
    
    elif gesture == "point":
        # Generate histogram data
        hist, bins = np.histogram(df['values'], bins=10)
        state.update({{
            "histogram": hist.tolist(),
            "bins": bins.tolist()
        }})
        
        emit("analysis_complete", {{
            "type": "histogram",
            "histogram": hist.tolist(),
            "bins": bins.tolist()
        }})

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update progress based on analyses performed
    analyses = state.get("analyses_performed", 0)
    progress = min(100.0, analyses * 33.33)  # 3 analyses = 100%
    
    state.set("lesson_progress", progress)
    
    emit("lesson_tick", {{
        "progress": progress,
        "analyses_performed": analyses
    }})
'''
        
        else:  # basic template
            return f'''"""
{lesson_id} - Basic Lesson Template
A basic template for creating interactive lessons
"""

# Lesson configuration
LESSON_NAME = "{lesson_id.replace('_', ' ').title()}"
TARGET_GESTURES = ["fist", "open_hand", "point"]

# Lesson state
gesture_count = 0
lesson_progress = 0.0

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global gesture_count, lesson_progress
    
    log("INFO", f"Starting lesson: {{LESSON_NAME}}")
    
    # Reset state
    gesture_count = 0
    lesson_progress = 0.0
    
    # Update lesson state
    state.update({{
        "lesson_name": LESSON_NAME,
        "gesture_count": gesture_count,
        "lesson_progress": lesson_progress
    }})
    
    emit("lesson_started", {{
        "lesson_name": LESSON_NAME
    }})

@on_gesture
def handle_gesture(gesture_data):
    """Called when a gesture is detected"""
    global gesture_count, lesson_progress
    
    gesture = gesture_data.get("gesture")
    finger_count = gesture_data.get("fingerCount", 0)
    
    if not gesture:
        return
    
    log("INFO", f"Detected gesture: {{gesture}} ({{finger_count}} fingers)")
    
    # Increment gesture count
    gesture_count += 1
    
    # Update progress (simple example)
    lesson_progress = min(100.0, gesture_count * 10.0)
    
    # Update state
    state.update({{
        "gesture_count": gesture_count,
        "lesson_progress": lesson_progress,
        "current_gesture": gesture,
        "current_finger_count": finger_count
    }})
    
    # Emit gesture event
    emit("gesture_processed", {{
        "gesture": gesture,
        "finger_count": finger_count,
        "gesture_count": gesture_count,
        "progress": lesson_progress
    }})
    
    # Check if lesson is complete
    if lesson_progress >= 100.0:
        log("INFO", "Lesson completed!")
        emit("lesson_completed", {{
            "final_progress": lesson_progress,
            "total_gestures": gesture_count
        }})

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = state.get("_started")
    if start_time:
        duration = time.time() - start_time
        state.set("lesson_duration", duration)
    
    # Emit periodic update
    emit("lesson_tick", {{
        "gesture_count": state.get("gesture_count"),
        "progress": state.get("lesson_progress")
    }})
'''
    
    def get_lesson_list(self) -> List[Dict[str, Any]]:
        """Get list of all available lessons"""
        lessons = []
        for lesson_id, metadata in self.lesson_metadata.items():
            lesson_info = {
                'id': lesson_id,
                'name': metadata.name,
                'description': metadata.description,
                'author': metadata.author,
                'version': metadata.version,
                'created': metadata.created,
                'tags': metadata.tags,
                'difficulty': metadata.difficulty,
                'duration': metadata.duration,
                'requirements': metadata.requirements,
                'dependencies': metadata.dependencies
            }
            lessons.append(lesson_info)
        return lessons
    
    def get_lesson_content(self, lesson_id: str) -> Optional[str]:
        """Get the content of a lesson"""
        if lesson_id not in self.lesson_files:
            return None
        
        try:
            with open(self.lesson_files[lesson_id], 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading lesson {lesson_id}: {e}")
            return None
    
    def update_lesson_content(self, lesson_id: str, content: str) -> bool:
        """Update the content of a lesson"""
        if lesson_id not in self.lesson_files:
            return False
        
        try:
            with open(self.lesson_files[lesson_id], 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Reload the lesson
            return self.reload_lesson(lesson_id)
            
        except Exception as e:
            logging.error(f"Error updating lesson {lesson_id}: {e}")
            return False
    
    def get_lesson_state(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a lesson"""
        return self.orchestrator.get_lesson_state(lesson_id)
    
    def start_lesson(self, lesson_id: str) -> bool:
        """Start a lesson"""
        return self.orchestrator.start_lesson(lesson_id)
    
    def stop_lesson(self, lesson_id: str) -> bool:
        """Stop a lesson"""
        return self.orchestrator.stop_lesson(lesson_id)
    
    def handle_gesture(self, lesson_id: str, gesture_data: Dict[str, Any]):
        """Handle gesture for a lesson"""
        self.orchestrator.handle_gesture(lesson_id, gesture_data)
    
    def tick(self):
        """Handle periodic tick for all lessons"""
        self.orchestrator.tick()
    
    def shutdown(self):
        """Shutdown the lesson manager"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        # Stop all lessons
        for lesson_id in list(self.lesson_metadata.keys()):
            self.stop_lesson(lesson_id)
        
        logging.info("Lesson manager shutdown complete") 