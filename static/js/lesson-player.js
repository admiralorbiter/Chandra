/**
 * Chandra Lesson Player
 * Integrates webcam, gesture recognition, and WebSocket communication
 *
 * === USAGE INSTRUCTIONS ===
 *
 * - Click "Start Detection" and allow camera access if prompted.
 * - Hold your hand up to the camera, palm facing forward.
 * - The "Current Gesture" box shows the detected gesture (e.g., Open Hand, Fist, Point, etc.).
 * - The large number below shows how many fingers are detected as extended (0 = fist, 5 = open hand, etc.).
 * - Try different gestures (fist, open hand, point, victory, thumbs up) to complete the lesson.
 * - The "Lesson Progress" bar increases as you show new gestures.
 * - Click "Toggle Debug" to show/hide hand landmark overlays (green lines and red dots) for troubleshooting detection.
 *
 * === DEVELOPER NOTES ===
 *
 * - Finger counting is based on the detected gesture:
 *   - Fist = 0, Point = 1, Victory = 2, Open Hand = 5, Thumbs Up = 1 (thumb only)
 *   - If the gesture is not recognized, it will show as "Unknown" and 0 fingers.
 * - Debug mode overlays hand landmarks and connections on the video feed (if implemented in GestureEngine.drawLandmarks).
 * - Good lighting and a clear background improve detection accuracy.
 */

// Import the reusable dev tools module
import { attachGestureDevTools } from './gesture-dev-tools.js';

// Plugin registry for per-lesson plugins
window._lessonPlugin = null;
window.registerLessonPlugin = function(plugin) {
    window._lessonPlugin = plugin;
};

class LessonPlayer {
    constructor() {
        this.webcamManager = new WebcamManager();
        this.gestureEngine = new GestureEngine();
        
        // Use connection manager instead of direct socket
        this.connectionManager = new ConnectionManager({
            maxReconnectAttempts: 10,
            reconnectDelay: 1000,
            maxReconnectDelay: 30000,
            connectionTimeout: 5000,
            heartbeatTimeout: 30000
        });
        
        this.isDetectionActive = false;
        this.debugMode = false;
        this.gestureHistory = [];
        this.maxHistoryLength = 10;
        this.runningTotal = 0;
        this.lastFingerCount = null;
        this.runningTotalSpan = document.getElementById('runningTotal');
        this.lessonStartTime = Date.now();
        
        // DOM elements
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.startBtn = document.getElementById('startBtn');
        this.stopBtn = document.getElementById('stopBtn');
        this.debugBtn = document.getElementById('debugBtn');
        this.gestureName = document.getElementById('gestureName');
        this.confidenceFill = document.getElementById('confidenceFill');
        this.confidenceText = document.getElementById('confidenceText');
        this.fingerCount = document.getElementById('fingerCount');
        this.lessonProgress = document.getElementById('lessonProgress');
        this.lessonStatus = document.getElementById('lessonStatus');
        this.gestureHistoryDiv = document.getElementById('gestureHistory');
        this.connectionIndicator = document.getElementById('connectionIndicator');
        this.connectionText = document.getElementById('connectionText');
        this.errorContainer = document.getElementById('errorContainer');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.mainContent = document.getElementById('mainContent');
        
        // Dev tools container
        this.devToolsContainer = document.createElement('div');
        this.devToolsContainer.className = 'text-center mt-3';
        
        // Setup connection manager listeners
        this.setupConnectionListeners();
        
        // Setup error boundary
        this.setupErrorBoundary();
        // Move controls outside of .video-container for visibility
        this.video.parentNode.parentNode.appendChild(this.devToolsContainer);
        this.initialize();
    }

    /**
     * Setup connection manager listeners
     */
    setupConnectionListeners() {
        this.connectionManager.onConnectionChange((status) => {
            console.log('Connection status changed:', status);
            this.updateConnectionStatus(status);
            
            if (status === 'connected') {
                // Re-enable detection if it was active
                if (this.isDetectionActive) {
                    this.lessonStatus.textContent = 'Detection active - show your hand!';
                }
            } else if (status === 'disconnected') {
                // Pause detection if connection lost
                if (this.isDetectionActive) {
                    this.lessonStatus.textContent = 'Connection lost - detection paused';
                }
            }
        });

        this.connectionManager.onError((error) => {
            console.error('Connection error:', error);
            this.showError('Connection error: ' + error.message);
        });
    }

    /**
     * Setup error boundary
     */
    setupErrorBoundary() {
        // Wrap critical methods with error boundary
        this.initialize = window.errorBoundary.wrapAsyncFunction(this.initialize.bind(this), {
            context: 'lesson_player_initialize'
        });
        
        this.handleGestureDetected = window.errorBoundary.wrapFunction(this.handleGestureDetected.bind(this), {
            context: 'lesson_player_gesture'
        });
        
        this.startDetection = window.errorBoundary.wrapFunction(this.startDetection.bind(this), {
            context: 'lesson_player_start'
        });
        
        this.stopDetection = window.errorBoundary.wrapFunction(this.stopDetection.bind(this), {
            context: 'lesson_player_stop'
        });
    }

    /**
     * Initialize the lesson player
     */
    async initialize() {
        try {
            // Show loading spinner
            this.showLoading();

            // Auto-start the script for this lesson if SCRIPT_ID is set
            if (typeof SCRIPT_ID !== 'undefined' && SCRIPT_ID) {
                const startRes = await fetch(`/scripts/lessons/${SCRIPT_ID}/start`, { method: 'POST' });
                const startData = await startRes.json();
                if (!startData.success) {
                    this.showError('Failed to start lesson script: ' + (startData.error || 'Unknown error'));
                    this.hideLoading();
                    return;
                }
            }
            
            // Initialize connection manager
            await this.connectionManager.connect();
            
            // Initialize webcam
            await this.initializeWebcam();
            
            // Initialize gesture engine
            await this.initializeGestureEngine();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Attach dev tools after gesture engine is ready
            attachGestureDevTools(this.gestureEngine, { container: this.devToolsContainer });
            
            // Hide loading and show main content
            this.hideLoading();
            this.showMainContent();
            console.log('Lesson player initialized successfully');
        } catch (error) {
            console.error('Failed to initialize lesson player:', error);
            this.showError('Failed to initialize lesson player: ' + error.message);
        }
    }

    /**
     * Initialize WebSocket connection (legacy method - now handled by connection manager)
     */
    async initializeWebSocket() {
        // This method is now deprecated - connection is handled by ConnectionManager
        console.warn('initializeWebSocket is deprecated - use connectionManager.connect() instead');
        return this.connectionManager.connect();
    }

    /**
     * Initialize webcam
     */
    async initializeWebcam() {
        this.webcamManager.setOnError((error, userMessage) => {
            this.showError(userMessage);
        });
        
        const success = await this.webcamManager.initialize(this.video);
        if (!success) {
            throw new Error('Failed to initialize webcam');
        }
    }

    /**
     * Initialize gesture engine
     */
    async initializeGestureEngine() {
        this.gestureEngine.onGesture((gestureEvent) => {
            this.handleGestureDetected(gestureEvent);
        });
        
        this.gestureEngine.setOnError((error) => {
            this.showError('Gesture engine error: ' + error.message);
        });
        
        const success = await this.gestureEngine.initialize(this.video, this.canvas);
        if (!success) {
            throw new Error('Failed to initialize gesture engine');
        }
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Start/Stop buttons
        this.startBtn.addEventListener('click', () => {
            this.startDetection();
        });
        
        this.stopBtn.addEventListener('click', () => {
            this.stopDetection();
        });
        
        this.debugBtn.addEventListener('click', () => {
            this.toggleDebugMode();
        });
    }

    /**
     * Start gesture detection
     */
    startDetection() {
        if (!this.connectionManager.isConnected && !this.connectionManager.offlineMode) {
            this.showError('Not connected to server');
            return;
        }
        
        if (this.gestureEngine.start()) {
            this.isDetectionActive = true;
            this.startBtn.disabled = true;
            this.stopBtn.disabled = false;
            this.lessonStatus.textContent = 'Detection active - show your hand!';
            
            // Send lesson start analytics
            this.sendAnalyticsEvent('lesson_start', {
                timestamp: new Date().toISOString(),
                lesson_id: typeof LESSON_ID !== 'undefined' ? LESSON_ID : 'unknown'
            });
            
            console.log('Gesture detection started');
        } else {
            this.showError('Failed to start gesture detection');
        }
    }

    /**
     * Stop gesture detection
     */
    stopDetection() {
        this.gestureEngine.stop();
        this.isDetectionActive = false;
        this.startBtn.disabled = false;
        this.stopBtn.disabled = true;
        this.lessonStatus.textContent = 'Detection stopped';
        console.log('Gesture detection stopped');
    }

    /**
     * Toggle debug mode
     */
    toggleDebugMode() {
        this.debugMode = !this.debugMode;
        this.gestureEngine.debugMode = this.debugMode;
        this.debugBtn.classList.toggle('btn-outline-info', !this.debugMode);
        this.debugBtn.classList.toggle('btn-info', this.debugMode);
        console.log('Debug mode:', this.debugMode ? 'enabled' : 'disabled');
    }

    /**
     * Handle detected gesture
     */
    handleGestureDetected(gestureEvent) {
        console.log('Gesture detected:', gestureEvent);
        
        // Update UI
        this.updateGestureDisplay(gestureEvent);
        
        // Update finger count using gestureEvent.fingerCount
        this.updateFingerCount(gestureEvent.name, gestureEvent.fingerCount);
        
        // Add to history
        this.addToHistory(gestureEvent);
        
        // Send to server via connection manager
        if (this.connectionManager.isConnected || this.connectionManager.offlineMode) {
            this.connectionManager.emit('gesture', gestureEvent);
            
            // Send analytics event
            this.sendAnalyticsEvent('gesture', gestureEvent);
        }
        
        // Update lesson progress
        this.updateLessonProgress(gestureEvent);
    }

    /**
     * Update gesture display
     */
    updateGestureDisplay(gestureEvent) {
        const gestureName = this.getGestureDisplayName(gestureEvent.name);
        const confidence = Math.round(gestureEvent.confidence * 100);
        
        this.gestureName.textContent = gestureName;
        this.confidenceFill.style.width = confidence + '%';
        this.confidenceText.textContent = `Confidence: ${confidence}%`;
    }

    /**
     * Get display name for gesture
     */
    getGestureDisplayName(gestureName) {
        const displayNames = {
            'open_hand': 'Open Hand',
            'fist': 'Fist',
            'thumbs_up': 'Thumbs Up',
            'point': 'Point',
            'victory': 'Victory',
            'unknown': 'Unknown'
        };
        
        return displayNames[gestureName] || gestureName;
    }

    /**
     * Update finger count based on gesture
     */
    updateFingerCount(gestureName, fingerCount) {
        // Use the provided fingerCount directly
        this.fingerCount.textContent = fingerCount;
        
        // Add to running total only if the count changes from the previous detection
        if (this.lastFingerCount !== null && fingerCount !== this.lastFingerCount) {
            this.runningTotal += fingerCount;
            this.runningTotalSpan.textContent = this.runningTotal;
        }
        this.lastFingerCount = fingerCount;
        
        // Add visual feedback
        this.fingerCount.style.transform = 'scale(1.2)';
        setTimeout(() => {
            this.fingerCount.style.transform = 'scale(1)';
        }, 200);
    }

    /**
     * Add gesture to history
     */
    addToHistory(gestureEvent) {
        this.gestureHistory.unshift({
            name: this.getGestureDisplayName(gestureEvent.name),
            confidence: Math.round(gestureEvent.confidence * 100),
            timestamp: new Date().toLocaleTimeString()
        });
        
        if (this.gestureHistory.length > this.maxHistoryLength) {
            this.gestureHistory.pop();
        }
        
        this.updateHistoryDisplay();
    }

    /**
     * Update history display
     */
    updateHistoryDisplay() {
        if (this.gestureHistory.length === 0) {
            this.gestureHistoryDiv.innerHTML = '<small class="text-muted">No gestures detected yet</small>';
            return;
        }
        
        const historyHtml = this.gestureHistory.map(gesture => 
            `<div class="d-flex justify-content-between align-items-center mb-1">
                <span>${gesture.name}</span>
                <span class="badge bg-secondary">${gesture.confidence}%</span>
                <small class="text-muted">${gesture.timestamp}</small>
            </div>`
        ).join('');
        
        this.gestureHistoryDiv.innerHTML = historyHtml;
    }

    /**
     * Update lesson progress
     */
    updateLessonProgress(gestureEvent) {
        // Simple progress based on gesture variety
        const uniqueGestures = new Set(this.gestureHistory.map(g => g.name));
        const progress = Math.min((uniqueGestures.size / 5) * 100, 100);
        
        this.lessonProgress.style.width = progress + '%';
        
        if (progress >= 100) {
            this.lessonStatus.textContent = 'Lesson completed! Great job!';
            this.lessonStatus.style.color = '#28a745';
            
            // Send lesson completion analytics
            this.sendLessonCompletion({
                completed: true,
                score: progress,
                attempts: 1,
                timeSpent: Math.floor((Date.now() - this.lessonStartTime) / 1000)
            });
        } else {
            this.lessonStatus.textContent = `Progress: ${Math.round(progress)}% - Keep trying different gestures!`;
        }
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(status) {
        this.connectionIndicator.className = `status-indicator status-${status}`;
        
        const statusTexts = {
            'connected': 'Connected',
            'disconnected': 'Disconnected',
            'connecting': 'Connecting...',
            'reconnecting': 'Reconnecting...'
        };
        
        this.connectionText.textContent = statusTexts[status] || 'Unknown';
        
        // Update lesson status based on connection
        if (status === 'disconnected' && this.isDetectionActive) {
            this.lessonStatus.textContent = 'Connection lost - detection paused';
        } else if (status === 'connected' && this.isDetectionActive) {
            this.lessonStatus.textContent = 'Detection active - show your hand!';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        this.errorContainer.style.display = 'block';
        this.errorContainer.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        this.hideLoading();
        if (this.mainContent) this.mainContent.style.display = 'none';
    }

    /**
     * Show loading spinner
     */
    showLoading() {
        this.loadingSpinner.style.display = 'block';
        this.mainContent.style.display = 'none';
    }

    /**
     * Hide loading spinner
     */
    hideLoading() {
        this.loadingSpinner.style.display = 'none';
    }

    /**
     * Show main content
     */
    showMainContent() {
        this.mainContent.style.display = 'block';
    }

    /**
     * Send analytics event
     */
    sendAnalyticsEvent(eventType, data) {
        const analyticsData = {
            event_type: eventType,
            session_id: this.getSessionId(),
            user_id: this.getUserId(),
            lesson_id: typeof LESSON_ID !== 'undefined' ? LESSON_ID : 'unknown',
            data: data
        };

        fetch('/analytics/events', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(analyticsData)
        }).catch(error => {
            console.error('Failed to send analytics event:', error);
        });
    }

    /**
     * Get session ID
     */
    getSessionId() {
        if (!this._sessionId) {
            this._sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        return this._sessionId;
    }

    /**
     * Get user ID (placeholder - would be set from authentication)
     */
    getUserId() {
        // In a real implementation, this would come from user authentication
        return null; // or session.user_id if available
    }

    /**
     * Send lesson completion data
     */
    sendLessonCompletion(completionData) {
        const progressData = {
            user_id: this.getUserId(),
            lesson_id: typeof LESSON_ID !== 'undefined' ? LESSON_ID : 'unknown',
            completed: completionData.completed || false,
            score: completionData.score || 0,
            attempts: completionData.attempts || 1,
            time_spent: completionData.timeSpent || 0
        };

        fetch('/analytics/progress', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(progressData)
        }).catch(error => {
            console.error('Failed to send progress data:', error);
        });
    }
}

// Initialize lesson player when DOM is loaded
// After creating LessonPlayer, call plugin.init if present

document.addEventListener('DOMContentLoaded', () => {
    const player = new LessonPlayer();
    if (window._lessonPlugin && typeof window._lessonPlugin.init === 'function') {
        window._lessonPlugin.init(player);
    }
}); 