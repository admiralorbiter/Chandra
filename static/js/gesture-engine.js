/**
 * Chandra Gesture Recognition Engine
 * Integrates TensorFlow.js with Handpose and Fingerpose for real-time hand gesture detection
 */

class GestureEngine {
    constructor() {
        this.detector = null;
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isRunning = false;
        this.lastGesture = null;
        this.gestureHistory = [];
        this.maxHistoryLength = 10;
        this.confidenceThreshold = 0.7;
        this.fps = 10; // Throttle to 10 Hz as per requirements
        this.lastFrameTime = 0;
        this.frameInterval = 1000 / this.fps;
        this.debugMode = false;
        
        // Gesture definitions
        this.gestures = {
            'fist': { name: 'Fist', confidence: 0 },
            'open_hand': { name: 'Open Hand', confidence: 0 },
            'thumbs_up': { name: 'Thumbs Up', confidence: 0 },
            'thumbs_down': { name: 'Thumbs Down', confidence: 0 },
            'point': { name: 'Point', confidence: 0 },
            'victory': { name: 'Victory', confidence: 0 },
            'ok': { name: 'OK', confidence: 0 },
            'rock': { name: 'Rock', confidence: 0 },
            'paper': { name: 'Paper', confidence: 0 },
            'scissors': { name: 'Scissors', confidence: 0 }
        };
        
        this.onGestureDetected = null;
        this.onError = null;
    }

    /**
     * Initialize the gesture engine
     */
    async initialize(videoElement, canvasElement) {
        try {
            this.video = videoElement;
            this.canvas = canvasElement;
            this.ctx = this.canvas.getContext('2d');

            // Load TensorFlow.js and Handpose
            await this.loadTensorFlow();
            await this.loadHandpose();
            
            console.log('Gesture engine initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize gesture engine:', error);
            if (this.onError) this.onError(error);
            return false;
        }
    }

    /**
     * Load TensorFlow.js and required dependencies
     */
    async loadTensorFlow() {
        // Check if TensorFlow.js is already loaded
        if (typeof tf === 'undefined') {
            await this.loadScript('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.11.0/dist/tf.min.js');
        }
        
        // Load Handpose
        if (typeof handpose === 'undefined') {
            await this.loadScript('https://cdn.jsdelivr.net/npm/@tensorflow-models/handpose@0.0.7/dist/handpose.js');
        }
        
        // Load Fingerpose
        if (typeof fingerpose === 'undefined') {
            await this.loadScript('https://cdn.jsdelivr.net/npm/fingerpose@0.1.0/dist/fingerpose.js');
        }
    }

    /**
     * Load external script
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * Load Handpose model
     */
    async loadHandpose() {
        try {
            this.detector = await handpose.load();
            console.log('Handpose model loaded');
        } catch (error) {
            throw new Error(`Failed to load Handpose model: ${error.message}`);
        }
    }

    /**
     * Start gesture detection
     */
    start() {
        if (!this.detector) {
            console.error('Gesture detector not initialized');
            return false;
        }

        this.isRunning = true;
        this.detectGestures();
        console.log('Gesture detection started');
        return true;
    }

    /**
     * Stop gesture detection
     */
    stop() {
        this.isRunning = false;
        console.log('Gesture detection stopped');
    }

    /**
     * Main gesture detection loop
     */
    async detectGestures() {
        if (!this.isRunning) return;

        const currentTime = Date.now();
        if (currentTime - this.lastFrameTime < this.frameInterval) {
            requestAnimationFrame(() => this.detectGestures());
            return;
        }

        this.lastFrameTime = currentTime;

        try {
            // Detect hands
            const predictions = await this.detector.estimateHands(this.video);
            
            if (predictions.length > 0) {
                const hand = predictions[0];
                if (this.debugMode) {
                    this.drawLandmarks(hand.landmarks);
                } else if (this.ctx) {
                    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                }
                const gesture = this.analyzeGesture(hand);
                
                if (gesture && gesture.confidence > this.confidenceThreshold) {
                    this.handleGestureDetected(gesture);
                }
            } else if (this.ctx) {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            }

            // Continue detection loop
            requestAnimationFrame(() => this.detectGestures());
        } catch (error) {
            console.error('Error in gesture detection:', error);
            requestAnimationFrame(() => this.detectGestures());
        }
    }

    /**
     * Analyze hand landmarks to determine gesture
     */
    analyzeGesture(hand) {
        const landmarks = hand.landmarks;
        const gesture = this.classifyGesture(landmarks);
        
        // Add to history for smoothing
        this.gestureHistory.push(gesture);
        if (this.gestureHistory.length > this.maxHistoryLength) {
            this.gestureHistory.shift();
        }
        
        // Return most common gesture in recent history
        return this.getMostCommonGesture();
    }

    /**
     * Classify gesture based on hand landmarks
     */
    classifyGesture(landmarks) {
        // Simple gesture classification based on finger positions
        const fingers = this.getFingerStates(landmarks);
        
        // Define gesture patterns
        if (fingers.thumb && fingers.index && fingers.middle && fingers.ring && fingers.pinky) {
            return { name: 'open_hand', confidence: 0.9 };
        } else if (!fingers.thumb && !fingers.index && !fingers.middle && !fingers.ring && !fingers.pinky) {
            return { name: 'fist', confidence: 0.9 };
        } else if (fingers.thumb && !fingers.index && !fingers.middle && !fingers.ring && !fingers.pinky) {
            return { name: 'thumbs_up', confidence: 0.8 };
        } else if (fingers.index && !fingers.thumb && !fingers.middle && !fingers.ring && !fingers.pinky) {
            return { name: 'point', confidence: 0.8 };
        } else if (fingers.index && fingers.middle && !fingers.thumb && !fingers.ring && !fingers.pinky) {
            return { name: 'victory', confidence: 0.8 };
        }
        
        return { name: 'unknown', confidence: 0.5 };
    }

    /**
     * Determine which fingers are extended
     */
    getFingerStates(landmarks) {
        // Simplified finger detection based on landmark positions
        const thumb = this.isFingerExtended(landmarks, [0, 1, 2, 3, 4]);
        const index = this.isFingerExtended(landmarks, [5, 6, 7, 8]);
        const middle = this.isFingerExtended(landmarks, [9, 10, 11, 12]);
        const ring = this.isFingerExtended(landmarks, [13, 14, 15, 16]);
        const pinky = this.isFingerExtended(landmarks, [17, 18, 19, 20]);
        
        return { thumb, index, middle, ring, pinky };
    }

    /**
     * Check if a finger is extended
     */
    isFingerExtended(landmarks, fingerIndices) {
        if (fingerIndices.length < 3) return false;
        
        // Simple heuristic: check if the tip is further from the base than the middle joint
        const base = landmarks[fingerIndices[0]];
        const middle = landmarks[fingerIndices[Math.floor(fingerIndices.length / 2)]];
        const tip = landmarks[fingerIndices[fingerIndices.length - 1]];
        
        const baseToTip = this.distance(base, tip);
        const baseToMiddle = this.distance(base, middle);
        
        return baseToTip > baseToMiddle * 1.2;
    }

    /**
     * Calculate distance between two points
     */
    distance(point1, point2) {
        return Math.sqrt(
            Math.pow(point1[0] - point2[0], 2) + 
            Math.pow(point1[1] - point2[1], 2)
        );
    }

    /**
     * Get most common gesture from recent history
     */
    getMostCommonGesture() {
        const gestureCounts = {};
        this.gestureHistory.forEach(gesture => {
            gestureCounts[gesture.name] = (gestureCounts[gesture.name] || 0) + 1;
        });
        
        let mostCommon = null;
        let maxCount = 0;
        
        for (const [name, count] of Object.entries(gestureCounts)) {
            if (count > maxCount) {
                maxCount = count;
                mostCommon = name;
            }
        }
        
        return mostCommon ? { name: mostCommon, confidence: maxCount / this.gestureHistory.length } : null;
    }

    /**
     * Handle detected gesture
     */
    handleGestureDetected(gesture) {
        if (gesture.name !== this.lastGesture) {
            this.lastGesture = gesture.name;
            
            const gestureEvent = {
                type: 'gesture',
                name: gesture.name,
                confidence: gesture.confidence,
                timestamp: Date.now()
            };
            
            console.log('Gesture detected:', gestureEvent);
            
            if (this.onGestureDetected) {
                this.onGestureDetected(gestureEvent);
            }
        }
    }

    /**
     * Set gesture detection callback
     */
    onGesture(callback) {
        this.onGestureDetected = callback;
    }

    /**
     * Set error callback
     */
    setOnError(callback) {
        this.onError = callback;
    }

    /**
     * Draw hand landmarks on canvas for debugging
     */
    drawLandmarks(landmarks) {
        if (!this.ctx) return;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.strokeStyle = '#00FF00';
        this.ctx.lineWidth = 2;
        
        // Draw connections between landmarks
        const connections = [
            [0, 1], [1, 2], [2, 3], [3, 4], // thumb
            [5, 6], [6, 7], [7, 8], // index
            [9, 10], [10, 11], [11, 12], // middle
            [13, 14], [14, 15], [15, 16], // ring
            [17, 18], [18, 19], [19, 20], // pinky
            [0, 5], [5, 9], [9, 13], [13, 17], // palm connections
            [0, 17] // palm base
        ];
        
        connections.forEach(([start, end]) => {
            const startPoint = landmarks[start];
            const endPoint = landmarks[end];
            
            this.ctx.beginPath();
            this.ctx.moveTo(startPoint[0], startPoint[1]);
            this.ctx.lineTo(endPoint[0], endPoint[1]);
            this.ctx.stroke();
        });
        
        // Draw landmark points
        landmarks.forEach(landmark => {
            this.ctx.fillStyle = '#FF0000';
            this.ctx.beginPath();
            this.ctx.arc(landmark[0], landmark[1], 3, 0, 2 * Math.PI);
            this.ctx.fill();
        });
    }
}

// Export for use in other modules
window.GestureEngine = GestureEngine; 