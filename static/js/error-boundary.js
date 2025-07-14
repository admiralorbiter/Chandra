/**
 * Error Boundary System for Chandra Education Engine
 * Handles JavaScript runtime errors gracefully and reports them to the backend
 */

class ErrorBoundary {
    constructor(options = {}) {
        this.errorListeners = [];
        this.maxErrorReports = options.maxErrorReports || 10;
        this.errorReportQueue = [];
        this.reportEndpoint = options.reportEndpoint || '/api/errors';
        this.isEnabled = true;
        this.errorCount = 0;
        this.lastErrorTime = 0;
        this.errorThrottle = options.errorThrottle || 5000; // 5 seconds between reports
        
        this.initialize();
    }

    /**
     * Initialize error boundary
     */
    initialize() {
        // Global error handlers
        window.addEventListener('error', (event) => {
            this.handleError(event.error || new Error(event.message), {
                type: 'runtime',
                filename: event.filename,
                lineno: event.lineno,
                colno: event.colno,
                url: window.location.href
            });
        });

        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(new Error(event.reason), {
                type: 'promise',
                url: window.location.href
            });
        });

        // Resource loading errors
        window.addEventListener('error', (event) => {
            if (event.target && event.target !== window) {
                this.handleError(new Error(`Failed to load resource: ${event.target.src || event.target.href}`), {
                    type: 'resource',
                    element: event.target.tagName,
                    src: event.target.src || event.target.href,
                    url: window.location.href
                });
            }
        }, true);

        // Console error interception
        this.interceptConsoleErrors();

        console.log('Error boundary initialized');
    }

    /**
     * Intercept console errors for additional context
     */
    interceptConsoleErrors() {
        const originalError = console.error;
        const originalWarn = console.warn;
        
        console.error = (...args) => {
            this.handleError(new Error(args.join(' ')), {
                type: 'console',
                level: 'error',
                url: window.location.href
            });
            originalError.apply(console, args);
        };

        console.warn = (...args) => {
            this.handleError(new Error(args.join(' ')), {
                type: 'console',
                level: 'warning',
                url: window.location.href
            });
            originalWarn.apply(console, args);
        };
    }

    /**
     * Handle errors
     */
    handleError(error, context = {}) {
        if (!this.isEnabled) {
            return;
        }

        // Throttle error reporting
        const now = Date.now();
        if (now - this.lastErrorTime < this.errorThrottle) {
            return;
        }

        this.errorCount++;
        this.lastErrorTime = now;

        const errorReport = {
            message: error.message,
            stack: error.stack,
            name: error.name,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
            url: window.location.href,
            context: context,
            sessionId: this.getSessionId(),
            userId: this.getUserId()
        };

        // Add to queue
        this.errorReportQueue.push(errorReport);

        // Limit queue size
        if (this.errorReportQueue.length > this.maxErrorReports) {
            this.errorReportQueue.shift();
        }

        // Report to backend
        this.reportError(errorReport);

        // Notify listeners
        this.notifyErrorListeners(error, context);

        // Show user-friendly error message if critical
        if (this.isCriticalError(error, context)) {
            this.showUserError(error, context);
        }

        console.error('Error boundary caught:', error, context);
    }

    /**
     * Determine if error is critical
     */
    isCriticalError(error, context) {
        const criticalPatterns = [
            /gesture/i,
            /webcam/i,
            /camera/i,
            /tensorflow/i,
            /socket/i,
            /connection/i
        ];

        const message = error.message.toLowerCase();
        return criticalPatterns.some(pattern => pattern.test(message));
    }

    /**
     * Show user-friendly error message
     */
    showUserError(error, context) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'alert alert-warning alert-dismissible fade show';
        notification.innerHTML = `
            <strong>Something went wrong</strong><br>
            ${this.getUserFriendlyMessage(error, context)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Add to page
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(notification, container.firstChild);

        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 10000);
    }

    /**
     * Get user-friendly error message
     */
    getUserFriendlyMessage(error, context) {
        const message = error.message.toLowerCase();
        
        if (message.includes('camera') || message.includes('webcam')) {
            return 'Camera access is required for this lesson. Please allow camera permissions and refresh the page.';
        }
        
        if (message.includes('gesture') || message.includes('tensorflow')) {
            return 'Gesture recognition is having issues. Please refresh the page to try again.';
        }
        
        if (message.includes('socket') || message.includes('connection')) {
            return 'Connection issues detected. The app will try to reconnect automatically.';
        }
        
        return 'An unexpected error occurred. Please refresh the page to continue.';
    }

    /**
     * Report error to backend
     */
    async reportError(errorReport) {
        try {
            const response = await fetch(this.reportEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(errorReport)
            });

            if (!response.ok) {
                console.warn('Failed to report error to backend:', response.status);
            }
        } catch (error) {
            console.warn('Failed to report error to backend:', error);
        }
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
     * Get user ID
     */
    getUserId() {
        // In a real implementation, this would come from user authentication
        return null;
    }

    /**
     * Add error listener
     */
    onError(callback) {
        this.errorListeners.push(callback);
    }

    /**
     * Notify error listeners
     */
    notifyErrorListeners(error, context) {
        this.errorListeners.forEach(callback => {
            try {
                callback(error, context);
            } catch (listenerError) {
                console.error('Error in error listener:', listenerError);
            }
        });
    }

    /**
     * Enable error boundary
     */
    enable() {
        this.isEnabled = true;
        console.log('Error boundary enabled');
    }

    /**
     * Disable error boundary
     */
    disable() {
        this.isEnabled = false;
        console.log('Error boundary disabled');
    }

    /**
     * Get error statistics
     */
    getErrorStats() {
        return {
            errorCount: this.errorCount,
            queuedReports: this.errorReportQueue.length,
            lastErrorTime: this.lastErrorTime,
            isEnabled: this.isEnabled
        };
    }

    /**
     * Clear error queue
     */
    clearErrorQueue() {
        this.errorReportQueue = [];
        console.log('Error queue cleared');
    }

    /**
     * Wrap function with error boundary
     */
    wrapFunction(fn, context = {}) {
        return (...args) => {
            try {
                return fn.apply(this, args);
            } catch (error) {
                this.handleError(error, {
                    type: 'function',
                    functionName: fn.name || 'anonymous',
                    ...context
                });
                throw error; // Re-throw to maintain original behavior
            }
        };
    }

    /**
     * Wrap async function with error boundary
     */
    wrapAsyncFunction(fn, context = {}) {
        return async (...args) => {
            try {
                return await fn.apply(this, args);
            } catch (error) {
                this.handleError(error, {
                    type: 'async_function',
                    functionName: fn.name || 'anonymous',
                    ...context
                });
                throw error; // Re-throw to maintain original behavior
            }
        };
    }
}

// Global error boundary instance
window.errorBoundary = new ErrorBoundary();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorBoundary;
} 