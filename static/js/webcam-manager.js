/**
 * Chandra Webcam Manager
 * Handles camera permissions, HTTPS requirements, and fallback messages
 */

class WebcamManager {
    constructor() {
        this.video = null;
        this.stream = null;
        this.isInitialized = false;
        this.onReady = null;
        this.onError = null;
        this.onPermissionDenied = null;
    }

    /**
     * Initialize webcam with proper error handling
     */
    async initialize(videoElement) {
        this.video = videoElement;
        
        try {
            // Check if we're on HTTPS (required for camera access)
            if (!this.isSecureContext()) {
                throw new Error('Camera access requires HTTPS. Please use ngrok or deploy to HTTPS.');
            }

            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('Camera access is not supported in this browser.');
            }

            // Request camera permissions
            await this.requestCameraAccess();
            
            this.isInitialized = true;
            console.log('Webcam initialized successfully');
            
            if (this.onReady) {
                this.onReady();
            }
            
            return true;
        } catch (error) {
            console.error('Failed to initialize webcam:', error);
            this.handleError(error);
            return false;
        }
    }

    /**
     * Check if we're in a secure context (HTTPS or localhost)
     */
    isSecureContext() {
        return window.isSecureContext || 
               window.location.protocol === 'https:' || 
               window.location.hostname === 'localhost' ||
               window.location.hostname === '127.0.0.1';
    }

    /**
     * Request camera access with proper constraints
     */
    async requestCameraAccess() {
        const constraints = {
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user' // Use front camera
            },
            audio: false
        };

        try {
            this.stream = await navigator.mediaDevices.getUserMedia(constraints);
            this.video.srcObject = this.stream;
            
            // Wait for video to be ready
            return new Promise((resolve, reject) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    resolve();
                };
                this.video.onerror = reject;
            });
        } catch (error) {
            if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
                throw new Error('Camera access was denied. Please allow camera permissions and refresh the page.');
            } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
                throw new Error('No camera found. Please connect a camera and try again.');
            } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
                throw new Error('Camera is already in use by another application.');
            } else {
                throw new Error(`Camera error: ${error.message}`);
            }
        }
    }

    /**
     * Stop camera stream
     */
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        
        if (this.video) {
            this.video.srcObject = null;
        }
        
        this.isInitialized = false;
        console.log('Webcam stopped');
    }

    /**
     * Get video element
     */
    getVideo() {
        return this.video;
    }

    /**
     * Check if webcam is ready
     */
    isReady() {
        return this.isInitialized && this.video && this.video.readyState >= 2;
    }

    /**
     * Handle errors with appropriate user messages
     */
    handleError(error) {
        let userMessage = 'An unexpected error occurred with the camera.';
        
        if (error.message.includes('HTTPS')) {
            userMessage = `
                <div class="alert alert-warning">
                    <h5>HTTPS Required</h5>
                    <p>Camera access requires a secure connection (HTTPS).</p>
                    <p><strong>For development:</strong></p>
                    <ul>
                        <li>Install ngrok: <code>npm install -g ngrok</code></li>
                        <li>Run: <code>ngrok http 5000</code></li>
                        <li>Use the HTTPS URL provided by ngrok</li>
                    </ul>
                </div>
            `;
        } else if (error.message.includes('denied')) {
            userMessage = `
                <div class="alert alert-danger">
                    <h5>Camera Access Denied</h5>
                    <p>Please allow camera permissions in your browser and refresh the page.</p>
                    <p><strong>How to enable:</strong></p>
                    <ul>
                        <li>Click the camera icon in your browser's address bar</li>
                        <li>Select "Allow" for camera access</li>
                        <li>Refresh the page</li>
                    </ul>
                </div>
            `;
        } else if (error.message.includes('not supported')) {
            userMessage = `
                <div class="alert alert-danger">
                    <h5>Browser Not Supported</h5>
                    <p>Your browser doesn't support camera access. Please use a modern browser like Chrome, Firefox, or Safari.</p>
                </div>
            `;
        } else if (error.message.includes('not found')) {
            userMessage = `
                <div class="alert alert-warning">
                    <h5>No Camera Found</h5>
                    <p>No camera was detected. Please connect a camera and try again.</p>
                </div>
            `;
        } else if (error.message.includes('in use')) {
            userMessage = `
                <div class="alert alert-warning">
                    <h5>Camera in Use</h5>
                    <p>Your camera is being used by another application. Please close other camera applications and try again.</p>
                </div>
            `;
        }

        if (this.onError) {
            this.onError(error, userMessage);
        }
    }

    /**
     * Set ready callback
     */
    onReady(callback) {
        this.onReady = callback;
    }

    /**
     * Set error callback
     */
    setOnError(callback) {
        this.onError = callback;
    }

    /**
     * Set permission denied callback
     */
    onPermissionDenied(callback) {
        this.onPermissionDenied = callback;
    }

    /**
     * Get camera capabilities
     */
    async getCameraCapabilities() {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getSupportedConstraints) {
            return null;
        }

        const constraints = navigator.mediaDevices.getSupportedConstraints();
        return {
            width: constraints.width,
            height: constraints.height,
            aspectRatio: constraints.aspectRatio,
            frameRate: constraints.frameRate,
            facingMode: constraints.facingMode
        };
    }

    /**
     * Get current video dimensions
     */
    getVideoDimensions() {
        if (!this.video) return null;
        
        return {
            width: this.video.videoWidth,
            height: this.video.videoHeight
        };
    }
}

// Export for use in other modules
window.WebcamManager = WebcamManager; 