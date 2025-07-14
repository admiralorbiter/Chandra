# Chandra Interactive Education Engine — Development Checklist

> **How to use:** Check each item as you implement it.  
> Nested boxes are subtasks—finish all before checking the parent item.

## 0 · Project Scaffold
- [x] **Initialize Repository**
  - [x] Create Git repo & `.gitignore`
  - [x] Add `README.md` with project vision
- [x] **Flask Skeleton**
  - [x] Create Flask app factory (`create_app`)
  - [x] Register blueprints: `auth`, `lessons`, `scripts`, `analytics`
  - [x] Add `.env` and config classes (Dev, Prod)
- [x] **Environment Setup**
  - [x] Basic `requirements.txt` (`flask`, `flask-socketio`, `sqlalchemy`, etc.)
  - [x] Pre‑commit hooks (black, flake8)

## 1 · Gesture MVP
- [x] **Client‑side Models**
  - [x] Integrate TensorFlow.js
  - [x] Load Handpose/Fingerpose templates
  - [x] Lazy‑cache models in IndexedDB
- [x] **Webcam & Permission Flow**
  - [x] HTTPS dev via `ngrok`
  - [x] Fallback message if camera denied
- [x] **WebSocket Echo Server**
  - [x] Add `flask_socketio` config (eventlet)
  - [x] Echo gesture events browser ↔ server
- [x] **Lesson Player Demo**
  - [x] Build Bootstrap "Counting Fingers" proof‑of‑concept
  - [x] Throttle event frequency to 10 Hz

## 2 · Script Engine
- [x] **Python Sandbox**
  - [x] Implement restricted namespace (`restrictedpython`)
  - [x] Expose hooks: `on_start`, `on_gesture`, `on_tick`
  - [x] Safe execution environment with limited Python functions
  - [x] Security measures to prevent dangerous operations
- [x] **Lesson Orchestrator**
  - [x] Load metadata & enforce sequence
  - [x] Timestamp & persist events
  - [x] Script lifecycle management (load, start, stop, tick)
  - [x] Event logging and state management
- [x] **Hot Reload**
  - [x] File‑watcher to reload `scripts/` modules without restart
  - [x] Automatic script discovery and loading
  - [x] Real-time script updates during development
- [x] **SDK Docs**
  - [x] Docstring examples & README section
  - [x] Provide sample Python + JS stubs
  - [x] Comprehensive documentation in `docs/script_engine.md`
  - [x] API reference and usage examples
- [x] **Port Sample Lessons**
  - [x] Counting Fingers (`scripts/counting_fingers.py`)
  - [x] Letter Tracing Wizard (`scripts/letter_tracing.py`)
  - [x] Basic template for new lessons
- [x] **Script Management Interface**
  - [x] Web-based script editor with syntax highlighting
  - [x] Real-time validation and error checking
  - [x] Script creation with templates
  - [x] Script state monitoring and event logging
- [x] **CLI Tool (`eductl.py`)**
  - [x] `eductl new-script <name>` - Create new scripts
  - [x] `eductl run <lesson>` - Run scripts
  - [x] `eductl export --zip` - Export scripts
  - [x] `eductl validate <script>` - Validate script syntax
  - [x] `eductl info <script>` - Show script information
- [x] **API Endpoints**
  - [x] RESTful API for script management
  - [x] WebSocket integration for real-time communication
  - [x] Script validation and state monitoring
  - [x] Event streaming and logging

---

## 3 · Analytics & Progress Tracking
- [x] **Database Tables**
  - [x] `progress` (user × lesson)
  - [x] `event_logs` (JSON, ts index)
- [x] **Collector Service**
  - [x] Emit logs from orchestrator
  - [x] Batch inserts / async queue
- [x] **Simple Charts**
  - [x] Matplotlib PNG endpoint for lesson completion timeline
  - [x] Embed chart on admin dashboard

---

## 4 · User Accounts & Auth
- [ ] **JWT Auth (Flask‑JWT‑Extended)**
  - [ ] Login, refresh, revoke
- [ ] **Role Seed**
  - [ ] `admin`, `author`, `student`
  - [ ] Decorator for role‑protected routes
- [ ] **Bootstrap UI**
  - [ ] Login & Register pages
  - [ ] Alert banners & nav bar state

---

## 5 · Packaging & CLI
- [x] **`eductl` Command‑Line Tool**
  - [x] `eductl new-script <name>`
  - [x] `eductl run <lesson>`
  - [x] `eductl export --zip`
  - [x] `eductl validate <script>` - Validate script syntax
  - [x] `eductl info <script>` - Show script information
- [ ] **Dockerization**
  - [ ] `Dockerfile` (python:3.12‑slim, gunicorn + eventlet)
  - [ ] `docker-compose.yml` with Postgres option
- [ ] **Swagger / OpenAPI Spec**
  - [ ] Autogenerate with `flask-smorest`

---

## 6 · Stretch & Future‑Proofing
- [ ] **GraphQL Facade (Graphene)**
- [ ] **Postgres Migration Script**
- [ ] **Admin Dashboard (React or HTMX)**
- [ ] **Plugin Loader Refactor**
  - [ ] Dynamic discovery via entry‑points
- [ ] **AI Tutor Module (Listens on internal bus)**

---

## Cross‑Cutting Concerns

### Security
- [x] Sandbox import allow‑list
- [ ] Enable CORS whitelist
- [ ] HTTPS enforcement tips for prod

### Performance
- [ ] GZIP static JS (`Flask‑Compress`)
- [ ] Object pooling for script sandboxes
- [ ] Client FPS monitor & auto‑downgrade

### Extensibility Hooks
- [ ] Gesture Template Registry (JSON + images)
- [ ] Message Bus (Pub/Sub) abstraction
- [ ] DB URI config toggle (SQLite ↔ Postgres)

## ✅ Additional Chandra-Edu Checklist Features

### 🔧 Developer Experience & Debugging
- [x] **Enhanced Logging & Debugging**
  - [x] Centralized logging (`loguru` or built-in logging)
  - [x] Real-time Flask logging UI
- [ ] **Local Dev Dashboard**
  - [ ] Server status, recent errors, connected WebSocket clients

### 🎥 Gesture Engine Enhancements
- [ ] **Gesture Debugging Overlay**
  - [ ] Visualize landmarks on webcam feed
  - [ ] Display recognized gestures/confidence scores
- [ ] **Gesture Recorder**
  - [ ] Capture videos/frames of gestures for debugging/training

### 📡 Robustness & Error Handling
- [ ] **Offline & Connectivity Handling**
  - [ ] WebSocket auto-reconnect
  - [ ] User notifications (disconnect/reconnect)
- [ ] **Error Boundary (Frontend)**
  - [ ] Handle JS runtime errors gracefully
  - [ ] Auto-report frontend errors to Flask backend


### 🚩 Accessibility & User Experience
- [ ] **Accessibility Audit**
  - [ ] Basic WCAG guidelines (contrast, ARIA)
  - [ ] Keyboard navigation support
- [ ] **Feedback & Gamification**
  - [ ] Sound effects/visual feedback on gesture success
  - [ ] Achievement/badge system (optional)

---

### 📊 Advanced Analytics & Metrics
- [ ] **User Engagement Metrics**
  - [ ] Track attention span, interaction frequency, drop-off points
- [ ] **Real-time Analytics Dashboard (future)**
  - [ ] Interactive visualizations for deeper insights

---

### 📁 Backup & Data Integrity
- [ ] **Database Backup Strategy**
  - [ ] Automated DB backups (SQLite/Postgres)
- [ ] **Export/Import Utility**
  - [ ] CLI/web admin tool for JSON export/import

---

### ⚙️ Testing & CI/CD
- [ ] **Automated Testing**
  - [ ] Pytest (backend endpoints)
  - [ ] Jest or similar (client-side JS/gesture logic)
- [ ] **Continuous Integration**
  - [ ] GitHub Actions (lint, tests, Docker builds)

---

### 📖 Documentation & Community Readiness
- [x] **User & Developer Guides**
  - [x] Installation & deployment instructions
  - [x] Script-authoring examples/cookbook
  - [x] Comprehensive script engine documentation
- [ ] **Community Contribution Guidelines**
  - [ ] Proposing new gestures/scripts
  - [ ] GitHub Issue templates (bugs, features)

