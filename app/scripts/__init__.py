"""
Scripts blueprint for script engine management
"""

from flask import Blueprint

scripts_bp = Blueprint('scripts', __name__)

from . import routes 