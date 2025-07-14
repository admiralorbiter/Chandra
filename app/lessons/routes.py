"""
Lesson routes
"""

from flask import jsonify, request, render_template
from . import lessons_bp
from app.scripts.routes import get_lesson_manager

@lessons_bp.route('/', methods=['GET'])
def list_lessons():
    """List available lessons from lesson engine."""
    manager = get_lesson_manager()
    lessons = manager.get_lesson_list()
    lessons_out = [
        {
            'id': lesson['id'],
            'title': lesson['name'],
            'description': lesson['description'],
            'difficulty': lesson.get('difficulty', 'beginner'),
        }
        for lesson in lessons
    ]
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify({'lessons': lessons_out})
    return render_template('lessons.html', lessons=lessons_out)

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