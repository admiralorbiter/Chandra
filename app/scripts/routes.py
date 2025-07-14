"""
Lesson routes for Chandra Lesson Engine v2
Provides API endpoints for lesson management and execution
"""

import json
import logging
from flask import jsonify, request, current_app
from flask_socketio import emit
from . import scripts_bp
from .manager import LessonManager
from app.analytics.collector import log_script_event, update_lesson_progress
from app.auth.decorators import author_required

# Global lesson manager instance
lesson_manager = None

def get_lesson_manager():
    """Get or create the global lesson manager instance"""
    global lesson_manager
    if lesson_manager is None:
        lesson_manager = LessonManager()
    return lesson_manager

def log_error(message):
    """Log an error message"""
    logging.error(f"[Lesson API] {message}")

# REST API Routes

@scripts_bp.route('/lessons', methods=['GET'])
def list_lessons():
    """List all available lessons."""
    try:
        manager = get_lesson_manager()
        lessons = manager.get_lesson_list()
        
        return jsonify({
            'success': True,
            'lessons': lessons,
            'count': len(lessons)
        })
    except Exception as e:
        log_error(f"Error listing lessons: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get lesson information."""
    try:
        manager = get_lesson_manager()
        
        # Get lesson metadata
        metadata = manager.lesson_metadata.get(lesson_id)
        if not metadata:
            return jsonify({
                'success': False,
                'error': f'Lesson {lesson_id} not found'
            }), 404
        
        # Get lesson content
        content = manager.get_lesson_content(lesson_id)
        
        # Get lesson state
        state = manager.get_lesson_state(lesson_id)
        
        return jsonify({
            'success': True,
            'lesson': {
                'id': lesson_id,
                'metadata': metadata.__dict__,
                'content': content,
                'state': state
            }
        })
    except Exception as e:
        log_error(f"Error getting lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons', methods=['POST'])
@author_required
def create_lesson():
    """Create a new lesson."""
    try:
        data = request.get_json()
        lesson_id = data.get('lesson_id')
        template = data.get('template', 'basic')
        
        if not lesson_id:
            return jsonify({
                'success': False,
                'error': 'lesson_id is required'
            }), 400
        
        manager = get_lesson_manager()
        success = manager.create_lesson(lesson_id, template)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Lesson {lesson_id} created successfully',
                'lesson_id': lesson_id
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to create lesson {lesson_id}'
            }), 500
    except Exception as e:
        log_error(f"Error creating lesson: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>', methods=['PUT'])
@author_required
def update_lesson(lesson_id):
    """Update lesson content."""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'content is required'
            }), 400
        
        manager = get_lesson_manager()
        success = manager.update_lesson_content(lesson_id, content)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Lesson {lesson_id} updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to update lesson {lesson_id}'
            }), 500
    except Exception as e:
        log_error(f"Error updating lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>', methods=['DELETE'])
@author_required
def delete_lesson(lesson_id):
    """Delete a lesson."""
    try:
        manager = get_lesson_manager()
        
        # Stop the lesson if it's running
        manager.stop_lesson(lesson_id)
        
        # Remove lesson files
        lesson_file = manager.lessons_dir / f"{lesson_id}.py"
        metadata_file = manager.lessons_dir / f"{lesson_id}.json"
        
        if lesson_file.exists():
            lesson_file.unlink()
        
        if metadata_file.exists():
            metadata_file.unlink()
        
        # Unload from manager
        manager.unload_lesson(lesson_id)
        
        return jsonify({
            'success': True,
            'message': f'Lesson {lesson_id} deleted successfully'
        })
    except Exception as e:
        log_error(f"Error deleting lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>/start', methods=['POST'])
def start_lesson(lesson_id):
    """Start a lesson."""
    try:
        manager = get_lesson_manager()
        success = manager.start_lesson(lesson_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Lesson {lesson_id} started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to start lesson {lesson_id}'
            }), 500
    except Exception as e:
        log_error(f"Error starting lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>/stop', methods=['POST'])
def stop_lesson(lesson_id):
    """Stop a lesson."""
    try:
        manager = get_lesson_manager()
        success = manager.stop_lesson(lesson_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Lesson {lesson_id} stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to stop lesson {lesson_id}'
            }), 500
    except Exception as e:
        log_error(f"Error stopping lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>/state', methods=['GET'])
def get_lesson_state(lesson_id):
    """Get lesson state."""
    try:
        manager = get_lesson_manager()
        state = manager.get_lesson_state(lesson_id)
        
        if state is None:
            return jsonify({
                'success': False,
                'error': f'Lesson {lesson_id} not found or not running'
            }), 404
        
        return jsonify({
            'success': True,
            'state': state
        })
    except Exception as e:
        log_error(f"Error getting lesson state for {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>/validate', methods=['POST'])
def validate_lesson(lesson_id):
    """Validate a lesson."""
    try:
        manager = get_lesson_manager()
        
        # Get lesson content
        content = manager.get_lesson_content(lesson_id)
        if not content:
            return jsonify({
                'success': False,
                'error': f'Lesson {lesson_id} not found'
            }), 404
        
        # Basic syntax validation
        try:
            compile(content, f'<lesson_{lesson_id}>', 'exec')
            syntax_valid = True
            syntax_errors = []
        except SyntaxError as e:
            syntax_valid = False
            syntax_errors = [str(e)]
        except Exception as e:
            syntax_valid = False
            syntax_errors = [str(e)]
        
        # Check for required hooks
        required_hooks = ['@on_start', '@on_gesture']
        missing_hooks = []
        
        for hook in required_hooks:
            if hook not in content:
                missing_hooks.append(hook)
        
        # Check for Python tool usage
        python_tools = ['import numpy', 'import pandas', 'import matplotlib', 
                       'import scipy', 'import sklearn', 'import seaborn']
        used_tools = []
        
        for tool in python_tools:
            if tool in content:
                used_tools.append(tool.split()[1])
        
        # Validation result
        is_valid = syntax_valid and len(missing_hooks) == 0
        
        return jsonify({
            'success': True,
            'valid': is_valid,
            'syntax_valid': syntax_valid,
            'syntax_errors': syntax_errors,
            'missing_hooks': missing_hooks,
            'used_tools': used_tools,
            'recommendations': []
        })
    except Exception as e:
        log_error(f"Error validating lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/lessons/<lesson_id>/analyze', methods=['GET'])
def analyze_lesson(lesson_id):
    """Analyze a lesson for complexity and tool usage."""
    try:
        manager = get_lesson_manager()
        
        # Get lesson content
        content = manager.get_lesson_content(lesson_id)
        if not content:
            return jsonify({
                'success': False,
                'error': f'Lesson {lesson_id} not found'
            }), 404
        
        # Analyze imports
        imports = []
        for line in content.split('\n'):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                imports.append(line.strip())
        
        # Analyze hooks
        hooks = []
        hook_patterns = ['@on_start', '@on_gesture', '@on_tick', '@on_complete']
        for pattern in hook_patterns:
            if pattern in content:
                hooks.append(pattern)
        
        # Analyze Python tools usage
        tools = {
            'numpy': 'Numerical computing',
            'pandas': 'Data manipulation',
            'matplotlib': 'Data visualization',
            'scipy': 'Scientific computing',
            'sklearn': 'Machine learning',
            'seaborn': 'Statistical visualization',
            'requests': 'HTTP requests',
            'json': 'JSON handling',
            'time': 'Time utilities',
            'datetime': 'Date/time handling',
            'math': 'Mathematical functions',
            'random': 'Random number generation',
            'collections': 'Data structures',
            'itertools': 'Iteration tools',
            'functools': 'Function tools'
        }
        
        used_tools = []
        for tool, description in tools.items():
            if f'import {tool}' in content or f'from {tool}' in content:
                used_tools.append((tool, description))
        
        # Complexity analysis
        lines = len(content.split('\n'))
        functions = content.count('def ')
        variables = content.count(' = ')
        
        if lines < 50:
            complexity = "Simple"
        elif lines < 100:
            complexity = "Moderate"
        else:
            complexity = "Complex"
        
        return jsonify({
            'success': True,
            'analysis': {
                'imports': imports,
                'hooks': hooks,
                'used_tools': used_tools,
                'complexity': {
                    'lines': lines,
                    'functions': functions,
                    'variables': variables,
                    'level': complexity
                }
            }
        })
    except Exception as e:
        log_error(f"Error analyzing lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# WebSocket event handlers

def handle_lesson_gesture(data):
    """Handle gesture events for lessons"""
    lesson_id = data.get('lesson_id')
    gesture_data = data.get('gesture_data', {})
    session_id = data.get('session_id')
    user_id = data.get('user_id')
    
    if lesson_id and gesture_data:
        try:
            manager = get_lesson_manager()
            manager.handle_gesture(lesson_id, gesture_data)
            
            # Log gesture event
            log_script_event(
                event_type='gesture',
                session_id=session_id or 'unknown',
                script_id=lesson_id,
                user_id=user_id,
                data=gesture_data
            )
            
            # Get updated state
            state = manager.get_lesson_state(lesson_id)
            if state:
                emit('lesson_state_updated', {
                    'lesson_id': lesson_id,
                    'state': state
                })
                
        except Exception as e:
            log_error(f"Gesture handling error for {lesson_id}: {str(e)}")
            emit('lesson_error', {
                'lesson_id': lesson_id,
                'error': str(e)
            })

def handle_lesson_tick():
    """Handle periodic tick for all lessons"""
    try:
        manager = get_lesson_manager()
        manager.tick()
    except Exception as e:
        log_error(f"Error in lesson tick: {str(e)}")

def register_socketio_handlers(socketio):
    """Register WebSocket event handlers"""
    
    @socketio.on('lesson_gesture')
    def on_lesson_gesture(data):
        """Handle lesson gesture events via WebSocket"""
        handle_lesson_gesture(data)
    
    @socketio.on('lesson_start')
    def on_lesson_start(data):
        """Handle lesson start events via WebSocket"""
        lesson_id = data.get('lesson_id')
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if lesson_id:
            try:
                manager = get_lesson_manager()
                success = manager.start_lesson(lesson_id)
                
                # Log lesson start event
                if success:
                    log_script_event(
                        event_type='lesson_start',
                        session_id=session_id or 'unknown',
                        script_id=lesson_id,
                        user_id=user_id,
                        data={'status': 'started'}
                    )
                
                emit('lesson_started', {
                    'lesson_id': lesson_id,
                    'success': success
                })
            except Exception as e:
                log_error(f"Lesson start error for {lesson_id}: {str(e)}")
                emit('lesson_started', {
                    'lesson_id': lesson_id,
                    'success': False,
                    'error': str(e)
                })
        else:
            emit('lesson_started', {
                'success': False,
                'error': 'Lesson ID is required'
            })
    
    @socketio.on('lesson_stop')
    def on_lesson_stop(data):
        """Handle lesson stop events via WebSocket"""
        lesson_id = data.get('lesson_id')
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if lesson_id:
            try:
                manager = get_lesson_manager()
                success = manager.stop_lesson(lesson_id)
                
                # Log lesson stop event
                if success:
                    log_script_event(
                        event_type='lesson_stop',
                        session_id=session_id or 'unknown',
                        script_id=lesson_id,
                        user_id=user_id,
                        data={'status': 'stopped'}
                    )
                
                emit('lesson_stopped', {
                    'lesson_id': lesson_id,
                    'success': success
                })
            except Exception as e:
                log_error(f"Lesson stop error for {lesson_id}: {str(e)}")
                emit('lesson_stopped', {
                    'lesson_id': lesson_id,
                    'success': False,
                    'error': str(e)
                })
        else:
            emit('lesson_stopped', {
                'success': False,
                'error': 'Lesson ID is required'
            })
    
    @socketio.on('get_lesson_state')
    def on_get_lesson_state(data):
        """Get lesson state via WebSocket"""
        lesson_id = data.get('lesson_id')
        
        if lesson_id:
            try:
                manager = get_lesson_manager()
                state = manager.get_lesson_state(lesson_id)
                
                emit('lesson_state', {
                    'lesson_id': lesson_id,
                    'state': state
                })
            except Exception as e:
                log_error(f"Error getting lesson state for {lesson_id}: {str(e)}")
                emit('lesson_state', {
                    'lesson_id': lesson_id,
                    'error': str(e)
                })
        else:
            emit('lesson_state', {
                'error': 'Lesson ID is required'
            })

# All compatibility routes and WebSocket handlers for old script endpoints/events have been removed. 