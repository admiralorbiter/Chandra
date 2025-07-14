"""
Chandra Script Engine v2 - Robust Python-based Lesson Engine
Provides a more flexible and powerful execution environment for interactive lessons
"""

import os
import sys
import time
import json
import logging
import importlib
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, asdict
from pathlib import Path
from contextlib import contextmanager
import threading
import queue

# Safe imports for lesson scripts
SAFE_MODULES = {
    'math': 'math',
    'random': 'random',
    'time': 'time',
    'datetime': 'datetime',
    'collections': 'collections',
    'itertools': 'itertools',
    'functools': 'functools',
    'operator': 'operator',
    're': 're',
    'json': 'json',
    '_io': '_io',
    'numpy': 'numpy',
    'pandas': 'pandas',
    'matplotlib': 'matplotlib',
    'seaborn': 'seaborn',
    'scipy': 'scipy',
    'sklearn': 'sklearn',
}

@dataclass
class LessonEvent:
    """Represents an event in the lesson execution timeline"""
    timestamp: float
    event_type: str  # 'start', 'gesture', 'tick', 'error', 'complete', 'custom'
    data: Dict[str, Any]
    lesson_id: str
    session_id: str
    severity: str = 'info'  # 'debug', 'info', 'warning', 'error'

@dataclass
class LessonMetadata:
    """Metadata for a lesson script"""
    id: str
    name: str
    description: str
    author: str
    version: str
    created: str
    tags: List[str]
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    duration: int  # estimated minutes
    requirements: List[str]
    dependencies: List[str]

class LessonState:
    """Manages lesson state and provides a clean API"""
    
    def __init__(self, lesson_id: str, session_id: str):
        self.lesson_id = lesson_id
        self.session_id = session_id
        self._state = {}
        self._history = []
        self._start_time = None
        self._event_callbacks = []
    
    def set(self, key: str, value: Any):
        """Set a state value"""
        self._state[key] = value
        self._history.append({
            'timestamp': time.time(),
            'key': key,
            'value': value
        })
    
    def get(self, key: str, default=None):
        """Get a state value"""
        return self._state.get(key, default)
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple state values"""
        for key, value in updates.items():
            self.set(key, value)
    
    def clear(self):
        """Clear all state"""
        self._state.clear()
        self._history.clear()
    
    def to_dict(self):
        """Convert state to dictionary"""
        return {
            'state': self._state.copy(),
            'history': self._history[-100:],  # Keep last 100 changes
            'start_time': self._start_time,
            'duration': time.time() - self._start_time if self._start_time else 0
        }
    
    def start(self):
        """Mark lesson as started"""
        self._start_time = time.time()
        self.set('_started', True)
    
    def add_event_callback(self, callback: Callable[[LessonEvent], None]):
        """Add an event callback"""
        self._event_callbacks.append(callback)

class LessonAPI:
    """Provides a clean API for lesson scripts"""
    
    def __init__(self, lesson_id: str, session_id: str):
        self.lesson_id = lesson_id
        self.session_id = session_id
        self.state = LessonState(lesson_id, session_id)
        self._events = queue.Queue()
        self._running = False
        self._hooks = {}
    
    def log(self, level: str, message: str, **kwargs):
        """Log a message with optional data"""
        event = LessonEvent(
            timestamp=time.time(),
            event_type='log',
            data={'message': message, 'level': level, **kwargs},
            lesson_id=self.lesson_id,
            session_id=self.session_id,
            severity=level
        )
        self._events.put(event)
        logging.log(getattr(logging, level.upper(), logging.INFO), 
                   f"[{self.lesson_id}] {message}")
    
    def emit(self, event_type: str, data: Dict[str, Any] = None):
        """Emit a custom event"""
        if data is None:
            data = {}
        
        event = LessonEvent(
            timestamp=time.time(),
            event_type=event_type,
            data=data,
            lesson_id=self.lesson_id,
            session_id=self.session_id
        )
        self._events.put(event)
    
    def on_start(self, func):
        """Decorator for start hook"""
        self._hooks['start'] = func
        return func
    
    def on_gesture(self, func):
        """Decorator for gesture hook"""
        self._hooks['gesture'] = func
        return func
    
    def on_tick(self, func):
        """Decorator for tick hook"""
        self._hooks['tick'] = func
        return func
    
    def on_complete(self, func):
        """Decorator for completion hook"""
        self._hooks['complete'] = func
        return func
    
    def get_events(self):
        """Get all pending events"""
        events = []
        while not self._events.empty():
            events.append(self._events.get_nowait())
        return events

class LessonEnvironment:
    """Provides a safe execution environment for lessons"""
    
    def __init__(self, lesson_id: str, session_id: str):
        self.lesson_id = lesson_id
        self.session_id = session_id
        self.api = LessonAPI(lesson_id, session_id)
        self.globals = self._create_globals()
        self.locals = {}
        self.module = None
        self._error_count = 0
        self._max_errors = 10
    
    def _create_globals(self) -> Dict[str, Any]:
        """Create a safe globals dictionary"""
        globals_dict = {
            # Core API
            'api': self.api,
            'state': self.api.state,
            'log': self.api.log,
            'emit': self.api.emit,
            
            # Decorators
            'on_start': self.api.on_start,
            'on_gesture': self.api.on_gesture,
            'on_tick': self.api.on_tick,
            'on_complete': self.api.on_complete,
            
            # Safe built-ins
            'print': self.api.log,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'range': range,
            'enumerate': enumerate,
            'zip': zip,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'chr': chr,
            'ord': ord,
            'hex': hex,
            'oct': oct,
            'bin': bin,
            'format': format,
            'repr': repr,
            'ascii': ascii,
            'sorted': sorted,
            'reversed': reversed,
            'filter': filter,
            'map': map,
            'any': any,
            'all': all,
            
            # Time utilities
            'time': time,
            'datetime': datetime,
            
            # Safe modules (lazy loaded)
            '_safe_modules': SAFE_MODULES,
        }
        
        return globals_dict
    
    def _safe_import(self, module_name: str):
        """Safely import a module"""
        if module_name not in SAFE_MODULES:
            raise ImportError(f"Module '{module_name}' is not allowed")
        
        try:
            return importlib.import_module(module_name)
        except ImportError as e:
            self.api.log('warning', f"Could not import {module_name}: {e}")
            return None
        except Exception as e:
            # For data science libraries, be more permissive
            if module_name in ['numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn', 'seaborn']:
                try:
                    # Try importing with a different approach
                    if module_name == 'matplotlib':
                        import matplotlib
                        matplotlib.use('Agg')  # Use non-interactive backend
                        return importlib.import_module(module_name)
                    else:
                        return importlib.import_module(module_name)
                except Exception as e2:
                    self.api.log('warning', f"Could not import {module_name}: {e2}")
                    return None
            else:
                self.api.log('warning', f"Could not import {module_name}: {e}")
                return None
    
    def _handle_import(self, name, globals_dict, locals_dict, fromlist, level):
        """Custom import handler for safe modules"""
        if name in SAFE_MODULES:
            return self._safe_import(name)
        else:
            # Allow standard library imports that are commonly needed
            if name in ['_io', 'os', 'sys', 'time', 'datetime', 'json', 'math', 'random', 'collections', 'itertools', 'functools', 're']:
                return self._safe_import(name)
            else:
                raise ImportError(f"Import of '{name}' is not allowed")
    
    def load_lesson(self, lesson_code: str) -> bool:
        """Load and compile a lesson"""
        try:
            # Create a custom module
            self.module = type(sys.modules[__name__])(f"lesson_{self.lesson_id}")
            self.module.__file__ = f"<lesson_{self.lesson_id}>"
            
            # Set up the module's globals
            self.module.__dict__.update(self.globals)
            
            # Add custom import handler
            original_import = __builtins__['__import__']
            __builtins__['__import__'] = self._handle_import
            
            try:
                # Execute the lesson code
                exec(lesson_code, self.module.__dict__)
                
                # Restore original import
                __builtins__['__import__'] = original_import
                
                return True
                
            except Exception as e:
                # Restore original import
                __builtins__['__import__'] = original_import
                raise e
                
        except Exception as e:
            self.api.log('error', f"Failed to load lesson: {e}")
            self.api.log('debug', traceback.format_exc())
            return False
    
    def start_lesson(self) -> bool:
        """Start the lesson"""
        try:
            self.api.state.start()
            self.api.emit('lesson_started', {
                'lesson_id': self.lesson_id,
                'session_id': self.session_id,
                'timestamp': time.time()
            })
            
            # Call start hook if it exists
            if 'start' in self.api._hooks:
                try:
                    self.api._hooks['start']()
                except Exception as e:
                    self.api.log('error', f"Error in start hook: {e}")
                    self._error_count += 1
            
            return True
            
        except Exception as e:
            self.api.log('error', f"Failed to start lesson: {e}")
            return False
    
    def handle_gesture(self, gesture_data: Dict[str, Any]):
        """Handle a gesture event"""
        try:
            # Call gesture hook if it exists
            if 'gesture' in self.api._hooks:
                try:
                    self.api._hooks['gesture'](gesture_data)
                except Exception as e:
                    self.api.log('error', f"Error in gesture hook: {e}")
                    self._error_count += 1
            
            self.api.emit('gesture_received', gesture_data)
            
        except Exception as e:
            self.api.log('error', f"Error handling gesture: {e}")
            self._error_count += 1
    
    def tick(self):
        """Handle periodic tick"""
        try:
            # Call tick hook if it exists
            if 'tick' in self.api._hooks:
                try:
                    self.api._hooks['tick']()
                except Exception as e:
                    self.api.log('error', f"Error in tick hook: {e}")
                    self._error_count += 1
            
            self.api.emit('tick', {'timestamp': time.time()})
            
        except Exception as e:
            self.api.log('error', f"Error in tick: {e}")
            self._error_count += 1
    
    def complete_lesson(self):
        """Mark lesson as complete"""
        try:
            # Call complete hook if it exists
            if 'complete' in self.api._hooks:
                try:
                    self.api._hooks['complete']()
                except Exception as e:
                    self.api.log('error', f"Error in complete hook: {e}")
            
            self.api.emit('lesson_completed', {
                'lesson_id': self.lesson_id,
                'session_id': self.session_id,
                'duration': time.time() - self.api.state._start_time if self.api.state._start_time else 0
            })
            
        except Exception as e:
            self.api.log('error', f"Error completing lesson: {e}")
    
    def should_stop(self) -> bool:
        """Check if lesson should be stopped due to errors"""
        return self._error_count >= self._max_errors

class LessonOrchestrator:
    """Manages lesson execution and orchestration"""
    
    def __init__(self):
        self.active_lessons: Dict[str, LessonEnvironment] = {}
        self.lesson_metadata: Dict[str, LessonMetadata] = {}
        self.event_log: List[LessonEvent] = []
        self.tick_interval = 1.0  # seconds
        self.last_tick = 0
        
    def load_lesson(self, lesson_id: str, lesson_code: str, metadata: LessonMetadata) -> bool:
        """Load a lesson into the orchestrator"""
        try:
            # Create lesson environment
            session_id = f"{lesson_id}_{int(time.time())}"
            environment = LessonEnvironment(lesson_id, session_id)
            
            # Load the lesson
            if not environment.load_lesson(lesson_code):
                return False
            
            # Store lesson
            self.active_lessons[session_id] = environment
            self.lesson_metadata[lesson_id] = metadata
            
            logging.info(f"Loaded lesson {lesson_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load lesson {lesson_id}: {e}")
            return False
    
    def start_lesson(self, lesson_id: str) -> bool:
        """Start a loaded lesson"""
        session_id = self._find_session_id(lesson_id)
        if not session_id:
            logging.error(f"Lesson {lesson_id} not found")
            return False
        
        try:
            environment = self.active_lessons[session_id]
            success = environment.start_lesson()
            
            if success:
                logging.info(f"Started lesson {lesson_id}")
            
            return success
            
        except Exception as e:
            logging.error(f"Failed to start lesson {lesson_id}: {e}")
            return False
    
    def stop_lesson(self, lesson_id: str) -> bool:
        """Stop a running lesson"""
        session_id = self._find_session_id(lesson_id)
        if not session_id:
            return False
        
        try:
            environment = self.active_lessons[session_id]
            environment.complete_lesson()
            
            logging.info(f"Stopped lesson {lesson_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to stop lesson {lesson_id}: {e}")
            return False
    
    def handle_gesture(self, lesson_id: str, gesture_data: Dict[str, Any]):
        """Handle gesture for a specific lesson"""
        session_id = self._find_session_id(lesson_id)
        if not session_id:
            return
        
        try:
            environment = self.active_lessons[session_id]
            environment.handle_gesture(gesture_data)
            
            # Collect events
            events = environment.api.get_events()
            for event in events:
                self.event_log.append(event)
                
                # Keep only last 1000 events
                if len(self.event_log) > 1000:
                    self.event_log = self.event_log[-1000:]
            
        except Exception as e:
            logging.error(f"Failed to handle gesture for lesson {lesson_id}: {e}")
    
    def tick(self):
        """Handle periodic tick for all active lessons"""
        current_time = time.time()
        if current_time - self.last_tick < self.tick_interval:
            return
        
        self.last_tick = current_time
        
        for session_id, environment in list(self.active_lessons.items()):
            try:
                environment.tick()
                
                # Collect events
                events = environment.api.get_events()
                for event in events:
                    self.event_log.append(event)
                
                # Check if lesson should be stopped
                if environment.should_stop():
                    logging.warning(f"Stopping lesson {environment.lesson_id} due to errors")
                    self.stop_lesson(environment.lesson_id)
                
            except Exception as e:
                logging.error(f"Error in lesson tick for {environment.lesson_id}: {e}")
    
    def _find_session_id(self, lesson_id: str) -> Optional[str]:
        """Find session ID for a lesson ID"""
        for session_id, environment in self.active_lessons.items():
            if environment.lesson_id == lesson_id:
                return session_id
        return None
    
    def get_lesson_state(self, lesson_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a lesson"""
        session_id = self._find_session_id(lesson_id)
        if not session_id:
            return None
        
        environment = self.active_lessons[session_id]
        return environment.api.state.to_dict()
    
    def get_recent_events(self, lesson_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events for a lesson or all lessons"""
        if lesson_id:
            events = [asdict(e) for e in self.event_log if e.lesson_id == lesson_id]
        else:
            events = [asdict(e) for e in self.event_log]
        
        return events[-limit:] if limit else events 