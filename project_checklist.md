# Chandra Interactive Education Engine — Development Checklist

> **How to use:** Check each item as you implement it.  
> Nested boxes are subtasks—finish all before checking the parent item.

## 0 · Project Scaffold
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

## 1 · Gesture MVP
- [ ] **Client‑side Models**
  - [ ] Integrate TensorFlow.js
  - [ ] Load Handpose/Fingerpose templates
  - [ ] Lazy‑cache models in IndexedDB
- [ ] **Webcam & Permission Flow**
  - [ ] HTTPS dev via `ngrok`
  - [ ] Fallback message if camera denied
- [ ] **WebSocket Echo Server**
  - [ ] Add `flask_socketio` config (eventlet)
  - [ ] Echo gesture events browser ↔ server
- [ ] **Lesson Player Demo**
  - [ ] Build Bootstrap “Counting Fingers” proof‑of‑concept
  - [ ] Throttle event frequency to 10 Hz

---

## 2 · Script Engine
- [ ] **Python Sandbox**
  - [ ] Implement restricted namespace (`restrictedpython`)
  - [ ] Expose hooks: `on_start`, `on_gesture`, `on_tick`
- [ ] **Lesson Orchestrator**
  - [ ] Load metadata & enforce sequence
  - [ ] Timestamp & persist events
- [ ] **Hot Reload**
  - [ ] File‑watcher to reload `scripts/` modules without restart
- [ ] **SDK Docs**
  - [ ] Docstring examples & README section
  - [ ] Provide sample Python + JS stubs
- [ ] **Port Sample Lessons**
  - [ ] Counting Fingers
  - [ ] Letter Tracing Wizard
  - [ ] Molecule Builder

---

## 3 · Analytics & Progress Tracking
- [ ] **Database Tables**
  - [ ] `progress` (user × lesson)
  - [ ] `event_logs` (JSON, ts index)
- [ ] **Collector Service**
  - [ ] Emit logs from orchestrator
  - [ ] Batch inserts / async queue
- [ ] **Simple Charts**
  - [ ] Matplotlib PNG endpoint for lesson completion timeline
  - [ ] Embed chart on admin dashboard

---

## 4 · User Accounts & Auth
- [ ] **JWT Auth (Flask‑JWT‑Extended)**
  - [ ] Login, refresh, revoke
- [ ] **Role Seed**
  - [ ] `admin`, `author`, `student`
  - [ ] Decorator for role‑protected routes
- [ ] **Bootstrap UI**
  - [ ] Login & Register pages
  - [ ] Alert banners & nav bar state

---

## 5 · Packaging & CLI
- [ ] **`eductl` Command‑Line Tool**
  - [ ] `eductl new-script <name>`
  - [ ] `eductl run <lesson>`
  - [ ] `eductl export --zip`
- [ ] **Dockerization**
  - [ ] `Dockerfile` (python:3.12‑slim, gunicorn + eventlet)
  - [ ] `docker-compose.yml` with Postgres option
- [ ] **Swagger / OpenAPI Spec**
  - [ ] Autogenerate with `flask-smorest`

---

## 6 · Stretch & Future‑Proofing
- [ ] **GraphQL Facade (Graphene)**
- [ ] **Postgres Migration Script**
- [ ] **Admin Dashboard (React or HTMX)**
- [ ] **Plugin Loader Refactor**
  - [ ] Dynamic discovery via entry‑points
- [ ] **AI Tutor Module (Listens on internal bus)**

---

## Cross‑Cutting Concerns

### Security
- [ ] Enable CORS whitelist
- [ ] Sandbox import allow‑list
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
- [ ] **Enhanced Logging & Debugging**
  - [ ] Centralized logging (`loguru` or built-in logging)
  - [ ] Real-time Flask logging UI
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
- [ ] **User & Developer Guides**
  - [ ] Installation & deployment instructions
  - [ ] Script-authoring examples/cookbook
- [ ] **Community Contribution Guidelines**
  - [ ] Proposing new gestures/scripts
  - [ ] GitHub Issue templates (bugs, features)

