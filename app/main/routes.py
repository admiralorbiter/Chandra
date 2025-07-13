"""
Main application routes
"""

from flask import render_template, jsonify, current_app, request
from flask_socketio import emit, join_room, leave_room
from . import main_bp
from app import socketio
from datetime import datetime

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@main_bp.route('/lesson-player')
def lesson_player():
    """Lesson player demo page."""
    return render_template('lesson_player.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'app': 'Chandra-edu',
        'version': '1.0.0'
    })

@main_bp.route('/api/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        'database': 'connected' if current_app.config.get('SQLALCHEMY_DATABASE_URI') else 'disconnected',
        'analytics': current_app.config.get('ANALYTICS_ENABLED', False),
        'script_timeout': current_app.config.get('SCRIPT_TIMEOUT', 30)
    })

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f'Client connected: {request.sid}')
    emit('connected', {'data': 'Connected to Chandra gesture server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print(f'Client disconnected: {request.sid}')

@socketio.on('gesture')
def handle_gesture(data):
    """Echo gesture events from browser to server and back."""
    print(f'Gesture received: {data}')
    
    # Echo the gesture back to the client
    emit('gesture_echo', {
        'type': 'gesture_echo',
        'original': data,
        'timestamp': data.get('timestamp'),
        'server_time': datetime.utcnow().isoformat()
    })
    
    # Broadcast to all clients (for demo purposes)
    emit('gesture_broadcast', {
        'type': 'gesture_broadcast',
        'gesture': data.get('name'),
        'confidence': data.get('confidence'),
        'timestamp': data.get('timestamp')
    }, broadcast=True)

@socketio.on('join_lesson')
def handle_join_lesson(data):
    """Join a lesson room for targeted gesture events."""
    lesson_id = data.get('lesson_id')
    if lesson_id:
        join_room(f'lesson_{lesson_id}')
        emit('joined_lesson', {'lesson_id': lesson_id})

@socketio.on('leave_lesson')
def handle_leave_lesson(data):
    """Leave a lesson room."""
    lesson_id = data.get('lesson_id')
    if lesson_id:
        leave_room(f'lesson_{lesson_id}')
        emit('left_lesson', {'lesson_id': lesson_id})

@socketio.on('ping')
def handle_ping():
    """Handle ping for connection testing."""
    emit('pong', {'timestamp': datetime.utcnow().isoformat()}) 