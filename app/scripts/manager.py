"""
Chandra Script Manager
Handles script file operations, hot reloading, and script discovery
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .engine import ScriptMetadata, ScriptOrchestrator

class ScriptFileHandler(FileSystemEventHandler):
    """File system event handler for script hot reloading"""
    
    def __init__(self, script_manager):
        self.script_manager = script_manager
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            script_path = Path(event.src_path)
            script_id = script_path.stem
            logging.info(f"Script file modified: {script_id}")
            self.script_manager.reload_script(script_id)
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            script_path = Path(event.src_path)
            script_id = script_path.stem
            logging.info(f"New script file created: {script_id}")
            self.script_manager.load_script_from_file(script_id)
    
    def on_deleted(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            script_path = Path(event.src_path)
            script_id = script_path.stem
            logging.info(f"Script file deleted: {script_id}")
            self.script_manager.unload_script(script_id)

class ScriptManager:
    """Manages script files, metadata, and hot reloading"""
    
    def __init__(self, scripts_dir: str = "scripts"):
        self.scripts_dir = Path(scripts_dir)
        self.orchestrator = ScriptOrchestrator()
        self.script_files: Dict[str, Path] = {}
        self.script_metadata: Dict[str, ScriptMetadata] = {}
        self.file_observer = None
        self.last_reload = {}
        
        # Ensure scripts directory exists
        self.scripts_dir.mkdir(exist_ok=True)
        
        # Initialize file watcher
        self._setup_file_watcher()
        
        # Load existing scripts
        self._discover_scripts()
    
    def _setup_file_watcher(self):
        """Set up file system watcher for hot reloading"""
        try:
            self.file_observer = Observer()
            event_handler = ScriptFileHandler(self)
            self.file_observer.schedule(event_handler, str(self.scripts_dir), recursive=False)
            self.file_observer.start()
            logging.info("File watcher started for hot reloading")
        except Exception as e:
            logging.error(f"Failed to start file watcher: {e}")
    
    def _discover_scripts(self):
        """Discover and load all scripts in the scripts directory"""
        for script_file in self.scripts_dir.glob("*.py"):
            if script_file.name.startswith('_'):
                continue  # Skip private files
            
            script_id = script_file.stem
            self.load_script_from_file(script_id)
    
    def load_script_from_file(self, script_id: str) -> bool:
        """Load a script from file"""
        script_file = self.scripts_dir / f"{script_id}.py"
        metadata_file = self.scripts_dir / f"{script_id}.json"
        
        if not script_file.exists():
            logging.error(f"Script file not found: {script_file}")
            return False
        
        try:
            # Read script code
            with open(script_file, 'r', encoding='utf-8') as f:
                script_code = f.read()
            
            # Read or create metadata
            metadata = self._load_or_create_metadata(script_id, metadata_file)
            
            # Store file reference
            self.script_files[script_id] = script_file
            self.script_metadata[script_id] = metadata
            
            # Load into orchestrator
            success = self.orchestrator.load_script(script_id, script_code, metadata)
            
            if success:
                logging.info(f"Loaded script: {script_id}")
            else:
                logging.error(f"Failed to load script: {script_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error loading script {script_id}: {e}")
            return False
    
    def _load_or_create_metadata(self, script_id: str, metadata_file: Path) -> ScriptMetadata:
        """Load existing metadata or create new metadata"""
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return ScriptMetadata(**data)
            except Exception as e:
                logging.warning(f"Failed to load metadata for {script_id}: {e}")
        
        # Create new metadata
        metadata = ScriptMetadata(
            id=script_id,
            name=script_id.replace('_', ' ').title(),
            description=f"Script {script_id}",
            author="system",
            version="1.0.0",
            created=time.strftime("%Y-%m-%d"),
            hooks={
                'on_start': False,
                'on_gesture': False,
                'on_tick': False
            },
            requirements=[]
        )
        
        # Save metadata
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata.__dict__, f, indent=2)
        except Exception as e:
            logging.warning(f"Failed to save metadata for {script_id}: {e}")
        
        return metadata
    
    def reload_script(self, script_id: str) -> bool:
        """Reload a script from file"""
        # Prevent rapid reloading
        current_time = time.time()
        if script_id in self.last_reload:
            if current_time - self.last_reload[script_id] < 1.0:  # 1 second cooldown
                return True
        
        self.last_reload[script_id] = current_time
        
        # Stop the script if it's running
        self.orchestrator.stop_script(script_id)
        
        # Reload from file
        success = self.load_script_from_file(script_id)
        
        if success:
            logging.info(f"Reloaded script: {script_id}")
        else:
            logging.error(f"Failed to reload script: {script_id}")
        
        return success
    
    def unload_script(self, script_id: str):
        """Unload a script"""
        # Stop the script if it's running
        self.orchestrator.stop_script(script_id)
        
        # Remove from tracking
        self.script_files.pop(script_id, None)
        self.script_metadata.pop(script_id, None)
        
        logging.info(f"Unloaded script: {script_id}")
    
    def create_script(self, script_id: str, template: str = "basic") -> bool:
        """Create a new script with a template"""
        script_file = self.scripts_dir / f"{script_id}.py"
        
        if script_file.exists():
            logging.error(f"Script {script_id} already exists")
            return False
        
        try:
            # Create script content based on template
            script_content = self._get_script_template(template, script_id)
            
            # Write script file
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Load the new script
            success = self.load_script_from_file(script_id)
            
            if success:
                logging.info(f"Created new script: {script_id}")
            else:
                # Clean up if loading failed
                script_file.unlink(missing_ok=True)
                logging.error(f"Failed to create script: {script_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Error creating script {script_id}: {e}")
            return False
    
    def _get_script_template(self, template: str, script_id: str) -> str:
        """Get script template content"""
        if template == "counting_fingers":
            return f'''"""
{script_id} - Finger Counting Lesson
A simple lesson that counts fingers and tracks progress
"""

# Lesson configuration
LESSON_NAME = "{script_id.replace('_', ' ').title()}"
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
    set_state("lesson_name", LESSON_NAME)
    set_state("target_gestures", TARGET_GESTURES)
    set_state("total_fingers", total_fingers)
    set_state("gestures_seen", list(gestures_seen))
    set_state("lesson_progress", lesson_progress)
    
    emit_event("lesson_started", {{
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
            emit_event("lesson_completed", {{
                "total_fingers": total_fingers,
                "gestures_seen": list(gestures_seen),
                "final_progress": lesson_progress
            }})
    
    # Update state
    set_state("total_fingers", total_fingers)
    set_state("gestures_seen", list(gestures_seen))
    set_state("lesson_progress", lesson_progress)
    set_state("current_gesture", gesture)
    set_state("current_finger_count", finger_count)
    
    # Emit gesture event
    emit_event("gesture_processed", {{
        "gesture": gesture,
        "finger_count": finger_count,
        "total_fingers": total_fingers,
        "progress": lesson_progress
    }})

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = get_state("start_time")
    if start_time:
        duration = time.time() - start_time
        set_state("lesson_duration", duration)
    
    # Emit periodic update
    emit_event("lesson_tick", {{
        "total_fingers": get_state("total_fingers"),
        "progress": get_state("lesson_progress"),
        "gestures_seen": get_state("gestures_seen")
    }})
'''
        elif template == "letter_tracing":
            return f'''"""
{script_id} - Letter Tracing Lesson
A lesson for practicing letter writing with hand gestures
"""

# Lesson configuration
LESSON_NAME = "{script_id.replace('_', ' ').title()}"
LETTERS = ["A", "B", "C", "D", "E"]
CURRENT_LETTER_INDEX = 0

@on_start
def lesson_start():
    """Called when the lesson starts"""
    global CURRENT_LETTER_INDEX
    
    log("INFO", f"Starting letter tracing lesson")
    log("INFO", f"Letters to trace: {{LETTERS}}")
    
    CURRENT_LETTER_INDEX = 0
    
    set_state("lesson_name", LESSON_NAME)
    set_state("letters", LETTERS)
    set_state("current_letter_index", CURRENT_LETTER_INDEX)
    set_state("current_letter", LETTERS[CURRENT_LETTER_INDEX])
    set_state("lesson_progress", 0.0)
    
    emit_event("lesson_started", {{
        "lesson_name": LESSON_NAME,
        "letters": LETTERS,
        "current_letter": LETTERS[CURRENT_LETTER_INDEX]
    }})

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
        
        log("INFO", f"Completed letter {{current_letter}}! Progress: {{progress:.1f}}%")
        
        if CURRENT_LETTER_INDEX >= len(LETTERS):
            log("INFO", "All letters completed!")
            emit_event("lesson_completed", {{
                "letters_completed": len(LETTERS),
                "final_progress": 100.0
            }})
        else:
            next_letter = LETTERS[CURRENT_LETTER_INDEX]
            set_state("current_letter", next_letter)
            set_state("current_letter_index", CURRENT_LETTER_INDEX)
            set_state("lesson_progress", progress)
            
            emit_event("letter_completed", {{
                "completed_letter": current_letter,
                "next_letter": next_letter,
                "progress": progress
            }})
    
    # Update state
    set_state("current_gesture", gesture)
    set_state("lesson_progress", (CURRENT_LETTER_INDEX / len(LETTERS)) * 100.0)
    
    emit_event("gesture_processed", {{
        "gesture": gesture,
        "current_letter": current_letter,
        "progress": (CURRENT_LETTER_INDEX / len(LETTERS)) * 100.0
    }})

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = get_state("start_time")
    if start_time:
        duration = time.time() - start_time
        set_state("lesson_duration", duration)
'''
        else:  # basic template
            return f'''"""
{script_id} - Basic Lesson Template
A basic template for creating interactive lessons
"""

# Lesson configuration
LESSON_NAME = "{script_id.replace('_', ' ').title()}"
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
    set_state("lesson_name", LESSON_NAME)
    set_state("gesture_count", gesture_count)
    set_state("lesson_progress", lesson_progress)
    
    emit_event("lesson_started", {{
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
    set_state("gesture_count", gesture_count)
    set_state("lesson_progress", lesson_progress)
    set_state("current_gesture", gesture)
    set_state("current_finger_count", finger_count)
    
    # Emit gesture event
    emit_event("gesture_processed", {{
        "gesture": gesture,
        "finger_count": finger_count,
        "gesture_count": gesture_count,
        "progress": lesson_progress
    }})
    
    # Check if lesson is complete
    if lesson_progress >= 100.0:
        log("INFO", "Lesson completed!")
        emit_event("lesson_completed", {{
            "final_gesture_count": gesture_count,
            "final_progress": lesson_progress
        }})

@on_tick
def lesson_tick():
    """Called periodically during the lesson"""
    # Update lesson duration
    start_time = get_state("start_time")
    if start_time:
        duration = time.time() - start_time
        set_state("lesson_duration", duration)
    
    # Emit periodic update
    emit_event("lesson_tick", {{
        "gesture_count": get_state("gesture_count"),
        "progress": get_state("lesson_progress")
    }})
'''
    
    def get_script_list(self) -> List[Dict[str, any]]:
        """Get list of all available scripts"""
        scripts = []
        
        for script_id, metadata in self.script_metadata.items():
            script_info = {
                'id': script_id,
                'name': metadata.name,
                'description': metadata.description,
                'author': metadata.author,
                'version': metadata.version,
                'created': metadata.created,
                'hooks': metadata.hooks,
                'file_exists': script_id in self.script_files
            }
            scripts.append(script_info)
        
        return scripts
    
    def get_script_content(self, script_id: str) -> Optional[str]:
        """Get the content of a script"""
        if script_id not in self.script_files:
            return None
        
        try:
            with open(self.script_files[script_id], 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading script {script_id}: {e}")
            return None
    
    def update_script_content(self, script_id: str, content: str) -> bool:
        """Update the content of a script"""
        if script_id not in self.script_files:
            return False
        
        try:
            with open(self.script_files[script_id], 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Reload the script
            return self.reload_script(script_id)
            
        except Exception as e:
            logging.error(f"Error updating script {script_id}: {e}")
            return False
    
    def get_script_state(self, script_id: str) -> Optional[Dict[str, any]]:
        """Get the current state of a script"""
        return self.orchestrator.get_script_state(script_id)
    
    def start_script(self, script_id: str) -> bool:
        """Start a script"""
        return self.orchestrator.start_script(script_id)
    
    def stop_script(self, script_id: str) -> bool:
        """Stop a script"""
        return self.orchestrator.stop_script(script_id)
    
    def handle_gesture(self, script_id: str, gesture_data: Dict[str, any]):
        """Handle gesture for a script"""
        self.orchestrator.handle_gesture(script_id, gesture_data)
    
    def tick(self):
        """Handle periodic tick for all scripts"""
        self.orchestrator.tick()
    
    def shutdown(self):
        """Shutdown the script manager"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        # Stop all scripts
        for script_id in list(self.script_metadata.keys()):
            self.stop_script(script_id)
        
        logging.info("Script manager shutdown complete") 