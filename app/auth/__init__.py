"""
Authentication blueprint for user management and JWT authentication
"""

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from . import routes 