"""
Configuration classes for Chandra Interactive Education Engine
"""

import os
from datetime import timedelta

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chandra_edu.db'
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # SocketIO settings
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # Script engine settings
    SCRIPT_TIMEOUT = 30  # seconds
    MAX_SCRIPT_SIZE = 1024 * 1024  # 1MB max script size
    
    # Analytics settings
    ANALYTICS_ENABLED = True
    EVENT_BATCH_SIZE = 100
    
    # Security settings
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
    
    @staticmethod
    def init_app(app):
        """Initialize app with configuration."""
        pass

class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Development database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///chandra_edu_dev.db'
    
    # Development settings
    SCRIPT_TIMEOUT = 60  # Longer timeout for debugging
    ANALYTICS_ENABLED = True
    
    # CORS for development
    CORS_ORIGINS = [
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'http://localhost:3000',  # For React dev server
        'http://127.0.0.1:3000'
    ]

class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = False
    
    # Test database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable analytics for tests
    ANALYTICS_ENABLED = False
    
    # Faster timeouts for tests
    SCRIPT_TIMEOUT = 5
    
    # Test secret key
    SECRET_KEY = 'test-secret-key'
    JWT_SECRET_KEY = 'test-jwt-secret-key'

class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production database (PostgreSQL recommended)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Production security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Production CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')
    
    # Production settings
    SCRIPT_TIMEOUT = 30
    ANALYTICS_ENABLED = True
    
    @classmethod
    def init_app(cls, app):
        """Initialize production app."""
        Config.init_app(app)
        
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 