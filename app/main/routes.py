"""
Main application routes
"""

from flask import render_template, jsonify, current_app
from . import main_bp

@main_bp.route('/')
def index():
    """Home page route."""
    return render_template('index.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'app': 'Chandra-edu',
        'version': '1.0.0'
    })

@main_bp.route('/api/status')
def api_status():
    """API status endpoint."""
    return jsonify({
        'database': 'connected' if current_app.config.get('SQLALCHEMY_DATABASE_URI') else 'disconnected',
        'analytics': current_app.config.get('ANALYTICS_ENABLED', False),
        'script_timeout': current_app.config.get('SCRIPT_TIMEOUT', 30)
    }) 