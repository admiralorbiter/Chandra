"""
Lessons blueprint for lesson management and playback
"""

from flask import Blueprint

lessons_bp = Blueprint('lessons', __name__)

from . import routes 