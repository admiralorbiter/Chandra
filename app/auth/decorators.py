"""
Role-based access control decorators for authentication
"""

from functools import wraps
from flask import jsonify, session, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models import User

def role_required(allowed_roles):
    """
    Decorator to check if user has required role(s).
    
    Args:
        allowed_roles: String or list of strings representing allowed roles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated via session (web interface)
            if 'user_id' in session:
                user_id = session['user_id']
                user = User.query.get(user_id)
                if not user or not user.is_active:
                    session.clear()
                    flash('Please log in to access this page.', 'warning')
                    return redirect(url_for('auth.login'))
                
                user_role = user.role
            else:
                # Check JWT token (API access)
                try:
                    verify_jwt_in_request()
                    user_id = get_jwt_identity()
                    user = User.query.get(user_id)
                    if not user or not user.is_active:
                        return jsonify({'error': 'Invalid or expired token'}), 401
                    user_role = user.role
                except Exception:
                    return jsonify({'error': 'Authentication required'}), 401
            
            # Check if user has required role
            if isinstance(allowed_roles, str):
                allowed_roles_list = [allowed_roles]
            else:
                allowed_roles_list = allowed_roles
            
            if user_role not in allowed_roles_list:
                if 'user_id' in session:
                    flash('You do not have permission to access this page.', 'error')
                    return redirect(url_for('main.index'))
                else:
                    return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to require admin role."""
    return role_required('admin')(f)

def author_required(f):
    """Decorator to require author role."""
    return role_required(['admin', 'author'])(f)

def student_required(f):
    """Decorator to require student role."""
    return role_required(['admin', 'author', 'student'])(f)

def login_required(f):
    """Decorator to require any authenticated user."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session first (web interface)
        if 'user_id' not in session:
            # Check JWT token (API access)
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = User.query.get(user_id)
                if not user or not user.is_active:
                    return jsonify({'error': 'Invalid or expired token'}), 401
            except Exception:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
        
        return f(*args, **kwargs)
    return decorated_function 