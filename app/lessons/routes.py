"""
Lesson routes
"""

from flask import jsonify, request, render_template
from . import lessons_bp
from app.scripts.routes import get_script_manager

@lessons_bp.route('/', methods=['GET'])
def list_lessons():
    """List available lessons from script engine."""
    manager = get_script_manager()
    scripts = manager.get_script_list()
    lessons = [
        {
            'id': script['id'],
            'title': script['name'],
            'description': script['description'],
            'difficulty': script.get('difficulty', 'beginner'),
            'script': script['id']
        }
        for script in scripts
    ]
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify({'lessons': lessons})
    return render_template('lessons.html', lessons=lessons)

@lessons_bp.route('/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get lesson details from script engine."""
    manager = get_script_manager()
    scripts = {script['id']: script for script in manager.get_script_list()}
    script = scripts.get(lesson_id)
    if not script:
        return (jsonify({'error': 'Lesson not found'}), 404) if 'application/json' in request.headers.get('Accept', '') else ("Lesson not found", 404)
    lesson = {
        'id': script['id'],
        'title': script['name'],
        'description': script['description'],
        'difficulty': script.get('difficulty', 'beginner'),
        'script': script['id']
    }
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify(lesson)
    return render_template('lesson_detail.html', lesson=lesson)

@lessons_bp.route('/<lesson_id>/start', methods=['POST'])
def start_lesson(lesson_id):
    """Start a lesson session and script."""
    manager = get_script_manager()
    # Try to start the script for this lesson
    success = manager.start_script(lesson_id)
    if not success:
        # Try to reload the script and start again
        reloaded = manager.load_script_from_file(lesson_id)
        if reloaded:
            success = manager.start_script(lesson_id)
    if success:
        return jsonify({
            'session_id': f'session_{lesson_id}_{hash(lesson_id) % 1000}',
            'status': 'started',
            'message': 'Lesson session started'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start script {lesson_id}'
        }), 400 