"""
Authentication routes
"""

from datetime import datetime
from flask import jsonify, request, render_template, redirect, url_for, flash, session
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity,
    get_jwt
)
from app import db
from app.models import User
from app.models import RevokedToken
from . import auth_bp
from .decorators import admin_required, author_required, login_required

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login endpoint."""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle POST request for login
    email = request.form.get('email')
    password = request.form.get('password')
    
    if not email or not password:
        return render_template('login.html', error='Please provide both email and password')
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if user is None or not user.check_password(password):
        return render_template('login.html', error='Invalid email or password')
    
    if not user.is_active:
        return render_template('login.html', error='Account is deactivated')
    
    # Update last login time
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # Create JWT tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Store user info in session for web interface
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_role'] = user.role
    
    flash(f'Welcome back, {user.name}!', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration endpoint."""
    if request.method == 'GET':
        return render_template('register.html')
    
    # Handle POST request for registration
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not name or not email or not password or not confirm_password:
        return render_template('register.html', error='Please fill in all fields')
    
    if password != confirm_password:
        return render_template('register.html', error='Passwords do not match')
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return render_template('register.html', error='Email already registered')
    
    # Validate password strength (basic)
    if len(password) < 6:
        return render_template('register.html', error='Password must be at least 6 characters long')
    
    try:
        # Create new user
        user = User(name=name, email=email, password=password, role='student')
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        return render_template('register.html', error='Registration failed. Please try again.')

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh JWT token endpoint."""
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify({
        'access_token': new_token
    })

@auth_bp.route('/logout')
def logout():
    """User logout endpoint."""
    # Revoke JWT tokens if they exist
    try:
        jwt_data = get_jwt()
        jti = jwt_data.get("jti")
        if jti:
            revoked = RevokedToken(jti=jti)
            db.session.add(revoked)
            db.session.commit()
    except Exception:
        pass  # No JWT token to revoke
    # Clear session data
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/revoke', methods=['POST'])
@jwt_required()
def revoke_token_endpoint():
    """Revoke JWT token endpoint."""
    jti = get_jwt()["jti"]
    revoked = RevokedToken(jti=jti)
    db.session.add(revoked)
    db.session.commit()
    return jsonify({"message": "Token revoked"}), 200

@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Get user profile page."""
    if 'user_id' in session:
        user_id = session['user_id']
    else:
        user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('main.index'))
    
    return render_template('profile.html', user=user)

@auth_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """List all users (admin only)."""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user role or status (admin only)."""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'role' in data:
        if data['role'] not in ['admin', 'author', 'student']:
            return jsonify({'error': 'Invalid role'}), 400
        user.role = data['role']
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    
    db.session.commit()
    return jsonify(user.to_dict())

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'}), 200

@auth_bp.route('/users', methods=['GET'])
@admin_required
def user_management_page():
    """User management page (admin only)."""
    return render_template('user_management.html')

@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get specific user details (admin only)."""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()) 