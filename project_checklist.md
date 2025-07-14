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
- [x] **JWT Auth (Flask‑JWT‑Extended)**
  - [x] Login, refresh, revoke
- [x] **Role Seed**
  - [x] `admin`, `author`, `student`
  - [x] Decorator for role‑protected routes
- [x] **Bootstrap UI**
  - [x] Login & Register pages
  - [x] Alert banners & nav bar state

---

## 5 · Packaging & CLI
- [x] **`eductl` Command‑Line Tool**
  - [x] `eductl new-script <name>`
  - [x] `eductl run <lesson>`
  - [x] `eductl export --zip`
  - [x] `eductl validate <script>` - Validate script syntax
  - [x] `eductl info <script>` - Show script information
- [ ] **Swagger / OpenAPI Spec**
  - [ ] Autogenerate with `flask-smorest`

---

## 6 · Stretch & Future‑Proofing
- [ ] **GraphQL Facade (Graphene)**
- [ ] **Admin Dashboard (HTMX)**
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
- [x] **Local Dev Dashboard**
  - [x] Server status, recent errors, connected WebSocket clients

### 🎥 Gesture Engine Enhancements
- [x] **Gesture Debugging Overlay**
  - [x] Visualize landmarks on webcam feed
  - [x] Display recognized gestures/confidence scores
- [x] **Gesture Recorder**
  - [x] Capture videos/frames of gestures for debugging/training

### 📡 Robustness & Error Handling
- [x] **Offline & Connectivity Handling**
  - [x] WebSocket auto-reconnect
  - [x] User notifications (disconnect/reconnect)
- [x] **Error Boundary (Frontend)**
  - [x] Handle JS runtime errors gracefully
  - [x] Auto-report frontend errors to Flask backend

### 📁 Backup & Data Integrity
- [ ] **Database Backup Strategy**
  - [ ] Automated DB backups (SQLite/Postgres)
- [ ] **Export/Import Utility**
  - [ ] CLI/web admin tool for JSON export/import

### ⚙️ Testing & CI/CD
- [ ] **Automated Testing**
  - [ ] Pytest (backend endpoints)
  - [ ] Jest or similar (client-side JS/gesture logic)

### 📖 Documentation & Community Readiness
- [x] **User & Developer Guides**
  - [x] Installation & deployment instructions
  - [x] Script-authoring examples/cookbook
  - [x] Comprehensive script engine documentation
- [ ] **Community Contribution Guidelines**
  - [ ] Proposing new gestures/scripts
  - [ ] GitHub Issue templates (bugs, features)

