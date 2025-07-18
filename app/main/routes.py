"""
Main routes for Chandra Interactive Education Engine
"""

from flask import render_template, jsonify, request, current_app
from . import main_bp
from app.scripts.manager import LessonManager
from app.lessons.routes import get_lesson
from app.auth.decorators import login_required, author_required
import psutil
import time
from datetime import datetime, timedelta
import logging

# Global variables for tracking
connected_clients = set()
recent_errors = []
server_start_time = time.time()

@main_bp.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@main_bp.route('/lesson/<lesson_id>')
def lesson_detail(lesson_id):
    """Lesson detail page"""
    return render_template('lesson_detail.html', lesson_id=lesson_id)

@main_bp.route('/lesson/<lesson_id>/play')
def lesson_player(lesson_id):
    """Lesson player page"""
    # Get lesson info from lesson engine
    manager = LessonManager()
    lessons = {lesson['id']: lesson for lesson in manager.get_lesson_list()}
    lesson = lessons.get(lesson_id)
    if not lesson:
        return render_template('lesson_player.html', error='Lesson not found', lesson_id=lesson_id)
    
    # Create lesson output object
    lesson_out = {
        'id': lesson['id'],
        'name': lesson['name'],
        'title': lesson['name'],
        'description': lesson['description'],
        'difficulty': lesson.get('difficulty', 'beginner'),
    }
    
    # Add additional metadata for data analysis lesson
    if lesson_id == 'data_analysis':
        lesson_out.update({
            'gesture_mappings': lesson.get('gesture_mappings', {}),
            'dataset_info': lesson.get('dataset_info', {}),
            'learning_objectives': lesson.get('learning_objectives', []),
            'analysis_types': lesson.get('analysis_types', [])
        })
        # Use specialized template for data analysis
        return render_template('data_analysis_player.html', lesson=lesson_out, script_id=lesson['id'])
    
    # Use default template for other lessons
    return render_template('lesson_player.html', lesson=lesson_out, script_id=lesson['id'])

@main_bp.route('/dev-dashboard')
def dev_dashboard():
    """Local development dashboard - shows server status, errors, and connected clients"""
    return render_template('dev_dashboard.html')

@main_bp.route('/api/dev/status')
def api_dev_status():
    """API endpoint for dev dashboard data"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get server uptime
        uptime_seconds = time.time() - server_start_time
        uptime = str(timedelta(seconds=int(uptime_seconds)))
        
        # Get Flask app info
        app_info = {
            'debug': current_app.debug,
            'testing': current_app.testing,
            'config_name': current_app.config.get('ENV', 'development'),
            'static_folder': current_app.static_folder
        }
        
        # Get lesson manager status
        manager = LessonManager()
        running_lessons = []
        # FIX: Use active_lessons and check is_running
        for environment in getattr(manager.orchestrator, 'active_lessons', {}).values():
            if getattr(environment, 'api', None) and getattr(environment.api, '_running', False):
                running_lessons.append({
                    'id': getattr(environment, 'lesson_id', 'unknown'),
                    'state': getattr(environment.api.state, '_state', {}),
                    'uptime': getattr(environment.api.state, '_start_time', 0)
                })
        
        return jsonify({
            'success': True,
            'data': {
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_used': memory.used,
                    'memory_total': memory.total,
                    'disk_percent': disk.percent,
                    'disk_used': disk.used,
                    'disk_total': disk.total
                },
                'server': {
                    'uptime': uptime,
                    'start_time': server_start_time,
                    'connected_clients': len(connected_clients),
                    'app_info': app_info
                },
                'lessons': {
                    'running_count': len(running_lessons),
                    'running_lessons': running_lessons,
                    'total_lessons': len(manager.get_lesson_list())
                },
                'errors': {
                    'recent_count': len(recent_errors),
                    'recent_errors': recent_errors[-10:]  # Last 10 errors
                }
            }
        })
    except Exception as e:
        # Log the error for the dashboard
        log_error(f"Dev dashboard API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main_bp.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'name': 'Chandra Interactive Education Engine'
    })

@main_bp.route('/api/errors', methods=['POST'])
def report_error():
    """Report frontend errors for monitoring and debugging"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Extract error information
        error_report = {
            'message': data.get('message', 'Unknown error'),
            'stack': data.get('stack', ''),
            'name': data.get('name', 'Error'),
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'user_agent': data.get('userAgent', ''),
            'url': data.get('url', ''),
            'context': data.get('context', {}),
            'session_id': data.get('sessionId', ''),
            'user_id': data.get('userId')
        }
        
        # Log the error
        logging.error(f"Frontend error: {error_report['message']}", extra={
            'error_report': error_report,
            'session_id': error_report['session_id'],
            'user_id': error_report['user_id']
        })
        
        # Store in database if needed (optional)
        # You could create an ErrorLog model and store errors for analysis
        
        return jsonify({'success': True, 'message': 'Error reported successfully'})
        
    except Exception as e:
        logging.error(f"Error reporting frontend error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Utility functions for tracking
def add_connected_client(client_id):
    """Add a connected WebSocket client"""
    connected_clients.add(client_id)

def remove_connected_client(client_id):
    """Remove a disconnected WebSocket client"""
    connected_clients.discard(client_id)

def log_error(error_message, error_type='error', timestamp=None):
    """Log an error for the dev dashboard"""
    if timestamp is None:
        timestamp = datetime.now()
    
    error_entry = {
        'message': error_message,
        'type': error_type,
        'timestamp': timestamp.isoformat(),
        'time_ago': get_time_ago(timestamp)
    }
    
    recent_errors.append(error_entry)
    
    # Keep only last 100 errors
    if len(recent_errors) > 100:
        recent_errors.pop(0)

def get_time_ago(timestamp):
    """Get human readable time ago"""
    now = datetime.now()
    diff = now - timestamp
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}h ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}m ago"
    else:
        return f"{diff.seconds}s ago" 