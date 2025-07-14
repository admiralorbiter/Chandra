"""
Lesson routes
"""

from flask import jsonify, request, render_template
from . import lessons_bp
from app.scripts.routes import get_lesson_manager
import logging
import os
import json
from pathlib import Path

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

@lessons_bp.route('/', methods=['GET'])
def list_lessons():
    """List available lessons from lesson engine."""
    try:
        # Get lesson manager
        manager = get_lesson_manager()
        
        # Ensure lessons directory is correct
        cwd = os.getcwd()
        lessons_dir = os.path.join(cwd, "lessons")
        
        if str(manager.lessons_dir) != lessons_dir:
            manager.lessons_dir = Path(lessons_dir)
            manager._discover_lessons()
        
        # Get lessons from manager
        lessons = manager.get_lesson_list()
        
        # Transform lessons for output
        lessons_out = []
        for lesson in lessons:
            lesson_out = {
                'id': lesson.get('id', 'unknown'),
                'title': lesson.get('name', 'Unknown Lesson'),
                'description': lesson.get('description', 'No description available'),
                'difficulty': lesson.get('difficulty', 'beginner'),
            }
            lessons_out.append(lesson_out)
        
        # Import recent_errors from main.routes
        try:
            from app.main.routes import recent_errors
        except Exception:
            recent_errors = []
        
        if 'application/json' in request.headers.get('Accept', ''):
            return jsonify({'lessons': lessons_out, 'errors': recent_errors})
        return render_template('lessons.html', lessons=lessons_out, errors=recent_errors)
        
    except Exception as e:
        logging.error(f"CRITICAL ERROR in list_lessons: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        
        # Return error page
        return render_template('lessons.html', lessons=[], errors=[{
            'type': 'error',
            'message': f"Critical error: {str(e)}",
            'timestamp': 'now',
            'time_ago': 'just now'
        }])

@lessons_bp.route('/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get lesson details from lesson engine."""
    manager = get_lesson_manager()
    lessons = {lesson['id']: lesson for lesson in manager.get_lesson_list()}
    lesson = lessons.get(lesson_id)
    if not lesson:
        return (jsonify({'error': 'Lesson not found'}), 404) if 'application/json' in request.headers.get('Accept', '') else ("Lesson not found", 404)
    lesson_out = {
        'id': lesson['id'],
        'title': lesson['name'],
        'description': lesson['description'],
        'difficulty': lesson.get('difficulty', 'beginner'),
    }
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify(lesson_out)
    return render_template('lesson_detail.html', lesson=lesson_out)

@lessons_bp.route('/<lesson_id>/start', methods=['POST'])
def start_lesson(lesson_id):
    """Start a lesson session."""
    manager = get_lesson_manager()
    success = manager.start_lesson(lesson_id)
    if not success:
        reloaded = manager.load_lesson_from_file(lesson_id)
        if reloaded:
            success = manager.start_lesson(lesson_id)
    if success:
        return jsonify({
            'session_id': f'session_{lesson_id}_{hash(lesson_id) % 1000}',
            'status': 'started',
            'message': 'Lesson session started'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start lesson {lesson_id}'
        }), 400 