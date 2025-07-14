"""
Chandra Interactive Education Engine
Flask Application Factory
"""

import os
from flask import Flask
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()

def create_app(config_name=None):
    """Application factory pattern for Flask app creation."""
    
    import os
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, static_folder=static_folder)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_object('app.config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DevelopmentConfig')
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    CORS(app)
    
    # Register blueprints
    from app.auth import auth_bp
    from app.lessons import lessons_bp
    from app.scripts import scripts_bp
    from app.analytics import analytics_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(lessons_bp, url_prefix='/lessons')
    app.register_blueprint(scripts_bp, url_prefix='/scripts')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    # Register main routes
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    # Import models to register them with SQLAlchemy
    from app.models import User, Progress, EventLog
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register WebSocket handlers for scripts
    from app.scripts.routes import register_socketio_handlers
    register_socketio_handlers(socketio)
    
    return app 