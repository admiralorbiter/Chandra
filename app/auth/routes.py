"""
Authentication routes
"""

from datetime import datetime
from flask import jsonify, request, render_template, redirect, url_for, flash, session
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
from . import auth_bp

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
    # Clear session data
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get user profile endpoint."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()) 