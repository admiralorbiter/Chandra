"""
Main routes for Chandra Interactive Education Engine
"""

from flask import render_template, jsonify, request
from . import main_bp
from app.scripts.manager import ScriptManager
from app.lessons.routes import get_lesson
from app.auth.decorators import login_required, author_required

@main_bp.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@main_bp.route('/lessons')
def lessons():
    """Lessons page"""
    return render_template('lessons.html')

@main_bp.route('/lesson/<lesson_id>')
def lesson_detail(lesson_id):
    """Lesson detail page"""
    return render_template('lesson_detail.html', lesson_id=lesson_id)

@main_bp.route('/lesson/<lesson_id>/play')
def lesson_player(lesson_id):
    """Lesson player page"""
    # Get lesson info from script engine
    manager = ScriptManager()
    scripts = {script['id']: script for script in manager.get_script_list()}
    script = scripts.get(lesson_id)
    if not script:
        return render_template('lesson_player.html', error='Lesson not found', lesson_id=lesson_id)
    lesson = {
        'id': script['id'],
        'title': script['name'],
        'description': script['description'],
        'difficulty': script.get('difficulty', 'beginner'),
        'script': script['id']
    }
    return render_template('lesson_player.html', lesson=lesson, script_id=script['id'])

@main_bp.route('/scripts')
@author_required
def script_editor():
    """Script editor page (authors and admins only)"""
    return render_template('script_editor.html')

@main_bp.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'name': 'Chandra Interactive Education Engine'
    }) 