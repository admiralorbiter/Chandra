"""
Script routes for Chandra Script Engine
Provides API endpoints for script management and execution
"""

import json
import logging
from flask import jsonify, request, current_app
from flask_socketio import emit
from . import scripts_bp
from .manager import ScriptManager
from app.analytics.collector import log_script_event, update_lesson_progress

# Global script manager instance
script_manager = None

def get_script_manager():
    """Get or create the global script manager instance"""
    global script_manager
    if script_manager is None:
        script_manager = ScriptManager()
    return script_manager

@scripts_bp.route('/', methods=['GET'])
def list_scripts():
    """List all available scripts."""
    try:
        manager = get_script_manager()
        scripts = manager.get_script_list()
        return jsonify({
            'success': True,
            'scripts': scripts,
            'count': len(scripts)
        })
    except Exception as e:
        logging.error(f"Error listing scripts: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>', methods=['GET'])
def get_script(script_id):
    """Get script content and metadata."""
    try:
        manager = get_script_manager()
        
        # Get script content
        content = manager.get_script_content(script_id)
        if content is None:
            return jsonify({
                'success': False,
                'error': f'Script {script_id} not found'
            }), 404
        
        # Get script metadata
        metadata = manager.script_metadata.get(script_id)
        
        # Get current state if script is running
        state = manager.get_script_state(script_id)
        
        return jsonify({
            'success': True,
            'script': {
                'id': script_id,
                'content': content,
                'metadata': metadata.__dict__ if metadata else None,
                'state': state
            }
        })
    except Exception as e:
        logging.error(f"Error getting script {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>', methods=['PUT'])
def update_script(script_id):
    """Update script content."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        manager = get_script_manager()
        success = manager.update_script_content(script_id, data['content'])
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Script {script_id} updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to update script {script_id}'
            }), 500
    except Exception as e:
        logging.error(f"Error updating script {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>/validate', methods=['POST'])
def validate_script(script_id):
    """Validate script syntax and safety."""
    try:
        data = request.get_json()
        content = data.get('content') if data else None
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Script content is required'
            }), 400
        
        # Basic validation
        errors = []
        warnings = []
        
        # Check for restricted imports
        restricted_imports = ['os', 'sys', 'subprocess', 'importlib', 'eval', 'exec']
        for restricted in restricted_imports:
            if f'import {restricted}' in content or f'from {restricted}' in content:
                errors.append(f'Import of {restricted} is not allowed')
        
        # Check for dangerous functions
        dangerous_functions = ['eval', 'exec', 'compile', 'open']
        for func in dangerous_functions:
            if f'{func}(' in content:
                errors.append(f'Use of {func}() is not allowed')
        
        # Check for required hooks
        if '@on_start' not in content:
            warnings.append('No @on_start hook found')
        if '@on_gesture' not in content:
            warnings.append('No @on_gesture hook found')
        
        return jsonify({
            'success': True,
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        })
    except Exception as e:
        logging.error(f"Error validating script {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>/start', methods=['POST'])
def start_script(script_id):
    """Start a script."""
    try:
        manager = get_script_manager()
        success = manager.start_script(script_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Script {script_id} started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to start script {script_id}'
            }), 500
    except Exception as e:
        logging.error(f"Error starting script {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>/stop', methods=['POST'])
def stop_script(script_id):
    """Stop a script."""
    try:
        manager = get_script_manager()
        success = manager.stop_script(script_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Script {script_id} stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to stop script {script_id}'
            }), 500
    except Exception as e:
        logging.error(f"Error stopping script {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>/state', methods=['GET'])
def get_script_state(script_id):
    """Get the current state of a script."""
    try:
        manager = get_script_manager()
        state = manager.get_script_state(script_id)
        
        if state is None:
            return jsonify({
                'success': False,
                'error': f'Script {script_id} not found or not running'
            }), 404
        
        return jsonify({
            'success': True,
            'state': state
        })
    except Exception as e:
        logging.error(f"Error getting script state {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>/events', methods=['GET'])
def get_script_events(script_id):
    """Get recent events for a script."""
    try:
        manager = get_script_manager()
        limit = request.args.get('limit', 100, type=int)
        events = manager.orchestrator.get_recent_events(script_id, limit)
        
        return jsonify({
            'success': True,
            'events': events,
            'count': len(events)
        })
    except Exception as e:
        logging.error(f"Error getting script events {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/', methods=['POST'])
def create_script():
    """Create a new script."""
    try:
        data = request.get_json()
        if not data or 'script_id' not in data:
            return jsonify({
                'success': False,
                'error': 'Script ID is required'
            }), 400
        
        script_id = data['script_id']
        template = data.get('template', 'basic')
        
        manager = get_script_manager()
        success = manager.create_script(script_id, template)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Script {script_id} created successfully',
                'script_id': script_id
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to create script {script_id}'
            }), 500
    except Exception as e:
        logging.error(f"Error creating script: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/<script_id>', methods=['DELETE'])
def delete_script(script_id):
    """Delete a script."""
    try:
        manager = get_script_manager()
        manager.unload_script(script_id)
        
        # Remove the file
        script_file = manager.scripts_dir / f"{script_id}.py"
        metadata_file = manager.scripts_dir / f"{script_id}.json"
        
        if script_file.exists():
            script_file.unlink()
        if metadata_file.exists():
            metadata_file.unlink()
        
        return jsonify({
            'success': True,
            'message': f'Script {script_id} deleted successfully'
        })
    except Exception as e:
        logging.error(f"Error deleting script {script_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@scripts_bp.route('/templates', methods=['GET'])
def get_templates():
    """Get available script templates."""
    templates = [
        {
            'id': 'basic',
            'name': 'Basic Template',
            'description': 'A simple template with basic hooks',
            'hooks': ['on_start', 'on_gesture', 'on_tick']
        },
        {
            'id': 'counting_fingers',
            'name': 'Counting Fingers',
            'description': 'A lesson that counts fingers and tracks progress',
            'hooks': ['on_start', 'on_gesture', 'on_tick']
        },
        {
            'id': 'letter_tracing',
            'name': 'Letter Tracing',
            'description': 'A lesson for practicing letter writing with gestures',
            'hooks': ['on_start', 'on_gesture', 'on_tick']
        }
    ]
    
    return jsonify({
        'success': True,
        'templates': templates
    })

# WebSocket event handlers for real-time script interaction
def handle_gesture_event(script_id, gesture_data, session_id=None, user_id=None):
    """Handle gesture events from WebSocket"""
    try:
        manager = get_script_manager()
        manager.handle_gesture(script_id, gesture_data)
        
        # Log gesture event for analytics
        log_script_event(
            event_type='gesture',
            session_id=session_id or 'unknown',
            script_id=script_id,
            user_id=user_id,
            data={
                'gesture_type': gesture_data.get('gesture'),
                'confidence': gesture_data.get('confidence'),
                'landmarks': gesture_data.get('landmarks')
            }
        )
    except Exception as e:
        logging.error(f"Error handling gesture for script {script_id}: {e}")

def handle_script_tick():
    """Handle periodic tick for all scripts"""
    try:
        manager = get_script_manager()
        manager.tick()
    except Exception as e:
        logging.error(f"Error in script tick: {e}")

def register_socketio_handlers(socketio):
    """Register WebSocket event handlers with the socketio instance"""
    
    @socketio.on('script_gesture')
    def on_script_gesture(data):
        """Handle gesture events for scripts via WebSocket"""
        script_id = data.get('script_id')
        gesture_data = data.get('gesture_data', {})
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if script_id:
            handle_gesture_event(script_id, gesture_data, session_id, user_id)
            emit('script_gesture_processed', {
                'script_id': script_id,
                'success': True
            })
        else:
            emit('script_gesture_processed', {
                'success': False,
                'error': 'Script ID is required'
            })

    @socketio.on('script_start')
    def on_script_start(data):
        """Handle script start events via WebSocket"""
        script_id = data.get('script_id')
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        
        if script_id:
            try:
                manager = get_script_manager()
                success = manager.start_script(script_id)
                
                # Log script start event
                if success:
                    log_script_event(
                        event_type='lesson_start',
                        session_id=session_id or 'unknown',
                        script_id=script_id,
                        user_id=user_id,
                        data={'status': 'started'}
                    )
                
                emit('script_started', {
                    'script_id': script_id,
                    'success': success
                })
            except Exception as e:
                emit('script_started', {
                    'script_id': script_id,
                    'success': False,
                    'error': str(e)
                })
        else:
            emit('script_started', {
                'success': False,
                'error': 'Script ID is required'
            })

    @socketio.on('script_stop')
    def on_script_stop(data):
        """Handle script stop events via WebSocket"""
        script_id = data.get('script_id')
        session_id = data.get('session_id')
        user_id = data.get('user_id')
        completion_data = data.get('completion_data', {})
        
        if script_id:
            try:
                manager = get_script_manager()
                success = manager.stop_script(script_id)
                
                # Log script stop event
                if success:
                    log_script_event(
                        event_type='lesson_complete',
                        session_id=session_id or 'unknown',
                        script_id=script_id,
                        user_id=user_id,
                        data=completion_data
                    )
                    
                    # Update progress if user_id is provided
                    if user_id and completion_data:
                        update_lesson_progress(
                            user_id=user_id,
                            lesson_id=script_id,
                            completed=completion_data.get('completed', False),
                            score=completion_data.get('score', 0),
                            attempts=completion_data.get('attempts', 1),
                            time_spent=completion_data.get('time_spent', 0)
                        )
                
                emit('script_stopped', {
                    'script_id': script_id,
                    'success': success
                })
            except Exception as e:
                emit('script_stopped', {
                    'script_id': script_id,
                    'success': False,
                    'error': str(e)
                })
        else:
            emit('script_stopped', {
                'success': False,
                'error': 'Script ID is required'
            })

    @socketio.on('get_script_state')
    def on_get_script_state(data):
        """Get script state via WebSocket"""
        script_id = data.get('script_id')
        
        if script_id:
            try:
                manager = get_script_manager()
                state = manager.get_script_state(script_id)
                
                emit('script_state', {
                    'script_id': script_id,
                    'state': state
                })
            except Exception as e:
                emit('script_state', {
                    'script_id': script_id,
                    'error': str(e)
                })
        else:
            emit('script_state', {
                'error': 'Script ID is required'
            }) 