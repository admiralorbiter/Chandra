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

## 2 · Lesson Engine v2 (Refactored)
- [x] **Robust Python Environment**
  - [x] Replace restricted sandbox with flexible Python execution
  - [x] Support for numpy, pandas, matplotlib, scipy, sklearn
  - [x] Safe module import system with allowlist
  - [x] Better error handling and debugging capabilities
- [x] **Enhanced Lesson API**
  - [x] Clean state management with `state.update()` and `state.get()`
  - [x] Improved event system with `emit()` and `log()`
  - [x] Decorator-based hooks: `@on_start`, `@on_gesture`, `@on_tick`, `@on_complete`
  - [x] Better lesson lifecycle management
- [x] **Python Tool Integration**
  - [x] Data science lessons with numpy/pandas/matplotlib
  - [x] Statistical analysis capabilities
  - [x] Real-time data processing and visualization
  - [x] Machine learning integration ready
- [x] **Improved Lesson Manager**
  - [x] Hot reload for `lessons/` directory
  - [x] Enhanced metadata with tags, difficulty, duration
  - [x] Better lesson discovery and validation
  - [x] Template system for quick lesson creation
- [x] **Enhanced CLI Tool (`eductl_v2.py`)**
  - [x] `eductl new-lesson <name>` - Create new lessons
  - [x] `eductl run <lesson>` - Run lessons with progress tracking
  - [x] `eductl validate <lesson>` - Validate lesson syntax and hooks
  - [x] `eductl analyze <lesson>` - Analyze Python tool usage and complexity
  - [x] `eductl install-deps` - Install lesson dependencies
  - [x] `eductl info <lesson>` - Show detailed lesson information
- [x] **Sample Lessons**
  - [x] Counting Fingers (`lessons/counting_fingers.py`) - Enhanced with statistics
  - [x] Data Analysis (`lessons/data_analysis.py`) - Demonstrates Python tools
  - [x] Basic template for new lessons
- [x] **API Endpoints v2**
  - [x] RESTful API for lesson management
  - [x] WebSocket integration for real-time communication
  - [x] Lesson validation and state monitoring
  - [x] Analysis and complexity assessment

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

## Cross‑Cutting Concerns

### Security
- [x] Sandbox import allow‑list

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

### 📖 Documentation & Community Readiness
- [x] **User & Developer Guides**
  - [x] Installation & deployment instructions
  - [x] Script-authoring examples/cookbook
  - [x] Comprehensive script engine documentation

## 6 · Stretch & Future‑Proofing
- [ ] **GraphQL Facade (Graphene)**
- [ ] **Admin Dashboard (HTMX)**
- [ ] **Plugin Loader Refactor**
  - [ ] Dynamic discovery via entry‑points
- [ ] **AI Tutor Module (Listens on internal bus)**
- [ ] **Swagger / OpenAPI Spec**
  - [ ] Autogenerate with `flask-smorest`
- [ ] **Automated Testing**
  - [ ] Pytest (backend endpoints)
  - [ ] Jest or similar (client-side JS/gesture logic)
- [ ] **Community Contribution Guidelines**
  - [ ] Proposing new gestures/scripts
  - [ ] GitHub Issue templates (bugs, features)
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

### 📁 Backup & Data Integrity
- [ ] **Database Backup Strategy**
  - [ ] Automated DB backups (SQLite/Postgres)
- [ ] **Export/Import Utility**
  - [ ] CLI/web admin tool for JSON export/import