"""
Chandra-Edu Interactive Education Engine
Application Entry Point
"""

import os
from app import create_app, socketio

app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Run the application
    socketio.run(
        app,
        host='127.0.0.1',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False)
    ) 