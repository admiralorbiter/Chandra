"""
Chandra-Edu Interactive Education Engine
Application Entry Point
"""

import os
from app import create_app, socketio

print("Starting application...")
app = create_app(os.environ.get('FLASK_ENV', 'development'))
print("App created successfully")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print("=" * 50)
    print(f"🚀 Server starting on: http://127.0.0.1:{port}")
    print("=" * 50)
    print("Starting server...")
    # Run the application
    socketio.run(
        app,
        host='127.0.0.1',
        port=port,
        debug=False  # Temporarily disabled for Python 3.13 compatibility
    ) 