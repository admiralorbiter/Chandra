# Chandra Interactive Education Engine

> **Seeing beyond visible** - Inspired by the Chandra X-ray Observatory, this AI-powered gesture recognition platform brings interactive educational experiences to a new spectrum.

## 🎯 Vision

Chandra transforms learning through computer vision and gesture recognition, inspired by the precision and reach of the Chandra X-ray Observatory. Students interact with educational content using hand gestures, making learning more engaging and accessible.

## 🚀 Features

- **Real-time Gesture Recognition**: TensorFlow.js-powered hand pose detection
- **Interactive Lessons**: Python script engine for dynamic educational content
- **Progress Analytics**: Track student engagement and learning outcomes
- **Multi-role Support**: Admin, Author, and Student roles with appropriate permissions
- **WebSocket Communication**: Real-time bidirectional communication
- **Offline Capability**: Works with intermittent connectivity

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   Script Engine │
│   (TensorFlow.js)│◄──►│   (WebSocket)   │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Analytics     │    │   Auth System   │    │   Lesson Store  │
│   (Progress)    │    │   (JWT)         │    │   (Scripts)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Flask, Flask-SocketIO, SQLAlchemy
- **Frontend**: TensorFlow.js, Bootstrap, WebSocket
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Auth**: JWT with role-based access
- **Scripting**: Restricted Python sandbox

## 📋 Development Status

See [project_checklist.md](./project_checklist.md) for detailed development progress.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/admiralorbiter/Chandra.git
cd Chandra

# Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
flask run
```

## 📚 Documentation

- [Script Authoring Guide](./docs/script-authoring.md)
- [API Documentation](./docs/api.md)
- [Deployment Guide](./docs/deployment.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
