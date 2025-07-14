"""
Chandra Script Engine
Provides a sandboxed Python execution environment for interactive lessons
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

# Import restricted execution libraries
try:
    from RestrictedPython import compile_restricted, safe_globals
    from RestrictedPython.Eval import default_guarded_getiter
    from RestrictedPython.Guards import guarded_unpack_sequence
    RESTRICTED_AVAILABLE = True
except ImportError:
    RESTRICTED_AVAILABLE = False
    logging.warning("RestrictedPython not available. Script execution will be disabled.")

@dataclass
class ScriptEvent:
    """Represents an event in the script execution timeline"""
    timestamp: float
    event_type: str  # 'start', 'gesture', 'tick', 'error', 'complete'
    data: Dict[str, Any]
    script_id: str
    session_id: str

@dataclass
class ScriptMetadata:
    """Metadata for a script"""
    id: str
    name: str
    description: str
    author: str
    version: str
    created: str
    hooks: Dict[str, bool]  # on_start, on_gesture, on_tick
    requirements: list

class ScriptSandbox:
    """Sandboxed Python execution environment for scripts"""
    
    def __init__(self, script_id: str, session_id: str):
        self.script_id = script_id
        self.session_id = session_id
        self.globals = self._create_safe_globals()
        self.locals = {}
        self.script_code = None
        self.compiled_code = None
        self.is_running = False
        self.start_time = None
        self.event_callback: Optional[Callable[[ScriptEvent], None]] = None
        
        # Script state
        self.state = {
            'total_fingers': 0,
            'gesture_count': 0,
            'current_gesture': None,
            'lesson_progress': 0.0,
            'start_time': None,
            'last_gesture_time': None
        }
    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a safe globals dictionary for restricted execution"""
        if not RESTRICTED_AVAILABLE:
            logging.error("RestrictedPython not available. Cannot create safe globals.")
            return {}
        
        from RestrictedPython import safe_globals as restricted_safe_globals
        # Copy the imported safe_globals to avoid shadowing
        safe_globals_copy = restricted_safe_globals.copy()
        
        # Add Chandra-specific safe functions
        safe_globals_copy.update({
            'print': self._safe_print,
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
            # Chandra API functions
            'on_start': self._hook_on_start,
            'on_gesture': self._hook_on_gesture,
            'on_tick': self._hook_on_tick,
            'log': self._safe_log,
            'get_state': self._get_state,
            'set_state': self._set_state,
            'emit_event': self._emit_event,
            # Safe math functions
            'math': self._safe_math_module(),
        })
        
        return safe_globals_copy
    
    def _safe_math_module(self):
        """Create a safe math module with only safe functions"""
        import math
        safe_math = type('SafeMath', (), {})
        
        safe_functions = [
            'ceil', 'floor', 'trunc', 'copysign', 'fabs', 'fmod',
            'frexp', 'ldexp', 'modf', 'fsum', 'gcd', 'isclose',
            'isfinite', 'isinf', 'isnan', 'pow', 'sqrt', 'exp',
            'expm1', 'log', 'log1p', 'log2', 'log10', 'cos', 'sin',
            'tan', 'acos', 'asin', 'atan', 'atan2', 'cosh', 'sinh',
            'tanh', 'acosh', 'asinh', 'atanh', 'erf', 'erfc',
            'gamma', 'lgamma', 'pi', 'e', 'tau', 'inf', 'nan'
        ]
        
        for func_name in safe_functions:
            if hasattr(math, func_name):
                setattr(safe_math, func_name, getattr(math, func_name))
        
        return safe_math
    
    def _safe_print(self, *args, **kwargs):
        """Safe print function that logs instead of printing"""
        message = ' '.join(str(arg) for arg in args)
        logging.info(f"[Script {self.script_id}] {message}")
    
    def _safe_log(self, level: str, message: str):
        """Safe logging function"""
        level = level.upper()
        if level == 'DEBUG':
            logging.debug(f"[Script {self.script_id}] {message}")
        elif level == 'INFO':
            logging.info(f"[Script {self.script_id}] {message}")
        elif level == 'WARNING':
            logging.warning(f"[Script {self.script_id}] {message}")
        elif level == 'ERROR':
            logging.error(f"[Script {self.script_id}] {message}")
    
    def _get_state(self, key: str = None):
        """Get script state"""
        if key is None:
            return self.state.copy()
        return self.state.get(key)
    
    def _set_state(self, key: str, value: Any):
        """Set script state"""
        self.state[key] = value
    
    def _emit_event(self, event_type: str, data: Dict[str, Any] = None):
        """Emit a custom event"""
        if data is None:
            data = {}
        
        event = ScriptEvent(
            timestamp=time.time(),
            event_type=event_type,
            data=data,
            script_id=self.script_id,
            session_id=self.session_id
        )
        
        if self.event_callback:
            self.event_callback(event)
    
    def _hook_on_start(self, func):
        """Register on_start hook"""
        self.state['_on_start_hook'] = func
        return func
    
    def _hook_on_gesture(self, func):
        """Register on_gesture hook"""
        self.state['_on_gesture_hook'] = func
        return func
    
    def _hook_on_tick(self, func):
        """Register on_tick hook"""
        self.state['_on_tick_hook'] = func
        return func
    
    def load_script(self, script_code: str) -> bool:
        """Load and compile a script"""
        try:
            self.script_code = script_code
            
            if not RESTRICTED_AVAILABLE:
                logging.error("RestrictedPython not available")
                return False
            
            # Compile the script
            self.compiled_code = compile_restricted(script_code, '<script>', 'exec')
            return True
            
        except Exception as e:
            logging.error(f"Failed to compile script {self.script_id}: {e}")
            return False
    
    def execute_script(self) -> bool:
        """Execute the loaded script"""
        if not self.compiled_code:
            logging.error("No script loaded")
            return False
        
        try:
            # Execute the script in the sandbox
            exec(self.compiled_code, self.globals, self.locals)
            
            # Call on_start hook if it exists
            if '_on_start_hook' in self.state and callable(self.state['_on_start_hook']):
                try:
                    self.state['_on_start_hook']()
                except Exception as e:
                    logging.error(f"Error in on_start hook: {e}")
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to execute script {self.script_id}: {e}")
            return False
    
    def handle_gesture(self, gesture_data: Dict[str, Any]):
        """Handle a gesture event"""
        if not self.is_running:
            return
        
        try:
            # Update state
            self.state['current_gesture'] = gesture_data.get('gesture')
            self.state['last_gesture_time'] = time.time()
            
            # Call on_gesture hook if it exists
            if '_on_gesture_hook' in self.state and callable(self.state['_on_gesture_hook']):
                try:
                    self.state['_on_gesture_hook'](gesture_data)
                except Exception as e:
                    logging.error(f"Error in on_gesture hook: {e}")
            
            # Emit gesture event
            self._emit_event('gesture', gesture_data)
            
        except Exception as e:
            logging.error(f"Error handling gesture: {e}")
    
    def tick(self):
        """Handle tick event (called periodically)"""
        if not self.is_running:
            return
        
        try:
            # Call on_tick hook if it exists
            if '_on_tick_hook' in self.state and callable(self.state['_on_tick_hook']):
                try:
                    self.state['_on_tick_hook']()
                except Exception as e:
                    logging.error(f"Error in on_tick hook: {e}")
            
            # Emit tick event
            self._emit_event('tick', {'timestamp': time.time()})
            
        except Exception as e:
            logging.error(f"Error in tick: {e}")
    
    def start(self):
        """Start the script"""
        self.is_running = True
        self.start_time = time.time()
        self.state['start_time'] = self.start_time
        
        # Emit start event
        self._emit_event('start', {'timestamp': self.start_time})
        
        logging.info(f"Started script {self.script_id}")
    
    def stop(self):
        """Stop the script"""
        self.is_running = False
        
        # Emit complete event
        self._emit_event('complete', {
            'duration': time.time() - self.start_time if self.start_time else 0
        })
        
        logging.info(f"Stopped script {self.script_id}")
    
    def set_event_callback(self, callback: Callable[[ScriptEvent], None]):
        """Set the event callback function"""
        self.event_callback = callback

class ScriptOrchestrator:
    """Manages script execution and lesson orchestration"""
    
    def __init__(self):
        self.active_scripts: Dict[str, ScriptSandbox] = {}
        self.script_metadata: Dict[str, ScriptMetadata] = {}
        self.event_log: list = []
        self.tick_interval = 1.0  # seconds
        self.last_tick = 0
        
    def load_script(self, script_id: str, script_code: str, metadata: ScriptMetadata) -> bool:
        """Load a script into the orchestrator"""
        try:
            # Create sandbox
            session_id = f"{script_id}_{int(time.time())}"
            sandbox = ScriptSandbox(script_id, session_id)
            
            # Set event callback
            sandbox.set_event_callback(self._handle_script_event)
            
            # Load and execute script
            if not sandbox.load_script(script_code):
                return False
            
            if not sandbox.execute_script():
                return False
            
            # Store script
            self.active_scripts[session_id] = sandbox
            self.script_metadata[script_id] = metadata
            
            logging.info(f"Loaded script {script_id}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to load script {script_id}: {e}")
            return False
    
    def start_script(self, script_id: str) -> bool:
        """Start a loaded script"""
        session_id = self._find_session_id(script_id)
        if not session_id:
            logging.error(f"Script {script_id} not found")
            return False
        
        try:
            sandbox = self.active_scripts[session_id]
            sandbox.start()
            return True
        except Exception as e:
            logging.error(f"Failed to start script {script_id}: {e}")
            return False
    
    def stop_script(self, script_id: str) -> bool:
        """Stop a running script"""
        session_id = self._find_session_id(script_id)
        if not session_id:
            return False
        
        try:
            sandbox = self.active_scripts[session_id]
            sandbox.stop()
            return True
        except Exception as e:
            logging.error(f"Failed to stop script {script_id}: {e}")
            return False
    
    def handle_gesture(self, script_id: str, gesture_data: Dict[str, Any]):
        """Handle gesture for a specific script"""
        session_id = self._find_session_id(script_id)
        if not session_id:
            return
        
        try:
            sandbox = self.active_scripts[session_id]
            sandbox.handle_gesture(gesture_data)
        except Exception as e:
            logging.error(f"Failed to handle gesture for script {script_id}: {e}")
    
    def tick(self):
        """Handle periodic tick for all active scripts"""
        current_time = time.time()
        if current_time - self.last_tick < self.tick_interval:
            return
        
        self.last_tick = current_time
        
        for session_id, sandbox in self.active_scripts.items():
            if sandbox.is_running:
                sandbox.tick()
    
    def _find_session_id(self, script_id: str) -> Optional[str]:
        """Find session ID for a script ID"""
        for session_id, sandbox in self.active_scripts.items():
            if sandbox.script_id == script_id:
                return session_id
        return None
    
    def _handle_script_event(self, event: ScriptEvent):
        """Handle events from script sandboxes"""
        # Log the event
        self.event_log.append(asdict(event))
        
        # Keep only last 1000 events
        if len(self.event_log) > 1000:
            self.event_log = self.event_log[-1000:]
        
        logging.debug(f"Script event: {event.event_type} from {event.script_id}")
    
    def get_script_state(self, script_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a script"""
        session_id = self._find_session_id(script_id)
        if not session_id:
            return None
        
        sandbox = self.active_scripts[session_id]
        return sandbox.state.copy()
    
    def get_recent_events(self, script_id: str = None, limit: int = 100) -> list:
        """Get recent events for a script or all scripts"""
        if script_id:
            events = [e for e in self.event_log if e['script_id'] == script_id]
        else:
            events = self.event_log
        
        return events[-limit:] if limit else events 