"""
Lesson routes
"""

from flask import jsonify, request, render_template
from . import lessons_bp

@lessons_bp.route('/', methods=['GET'])
def list_lessons():
    """List available lessons."""
    lessons = [
        {
            'id': 'counting-fingers',
            'title': 'Counting Fingers',
            'description': 'Learn to count using hand gestures',
            'difficulty': 'beginner'
        },
        {
            'id': 'letter-tracing',
            'title': 'Letter Tracing Wizard',
            'description': 'Practice writing letters with gestures',
            'difficulty': 'intermediate'
        }
    ]
    # If the request is from a browser (not API), render the template
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify({'lessons': lessons})
    return render_template('lessons.html', lessons=lessons)

@lessons_bp.route('/<lesson_id>', methods=['GET'])
def get_lesson(lesson_id):
    """Get lesson details."""
    # For now, use the same hardcoded lessons as in list_lessons
    lessons = {
        'counting-fingers': {
            'id': 'counting-fingers',
            'title': 'Counting Fingers',
            'description': 'Learn to count using hand gestures',
            'difficulty': 'beginner',
            'script': 'counting_fingers.py'
        },
        'letter-tracing': {
            'id': 'letter-tracing',
            'title': 'Letter Tracing Wizard',
            'description': 'Practice writing letters with gestures',
            'difficulty': 'intermediate',
            'script': 'letter_tracing.py'
        }
    }
    lesson = lessons.get(lesson_id)
    if not lesson:
        return (jsonify({'error': 'Lesson not found'}), 404) if 'application/json' in request.headers.get('Accept', '') else ("Lesson not found", 404)
    if 'application/json' in request.headers.get('Accept', ''):
        return jsonify(lesson)
    return render_template('lesson_detail.html', lesson=lesson)

@lessons_bp.route('/<lesson_id>/start', methods=['POST'])
def start_lesson(lesson_id):
    """Start a lesson session."""
    # TODO: Implement lesson start logic
    return jsonify({
        'session_id': f'session_{lesson_id}_{hash(lesson_id) % 1000}',
        'status': 'started',
        'message': 'Lesson session started'
    }) 