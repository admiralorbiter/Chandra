/**
 * Connection Manager for Chandra Education Engine
 * Handles WebSocket connections with auto-reconnect and user notifications
 */

class ConnectionManager {
    constructor(options = {}) {
        this.socket = null;
        this.isConnected = false;
        this.isReconnecting = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        this.reconnectDelay = options.reconnectDelay || 1000;
        this.maxReconnectDelay = options.maxReconnectDelay || 30000;
        this.currentReconnectDelay = this.reconnectDelay;
        this.reconnectTimer = null;
        this.connectionListeners = [];
        this.errorListeners = [];
        this.messageQueue = [];
        this.maxQueueSize = options.maxQueueSize || 100;
        this.offlineMode = false;
        this.lastConnectionTime = null;
        this.connectionTimeout = options.connectionTimeout || 5000;
        this.heartbeatInterval = null;
        this.heartbeatTimeout = options.heartbeatTimeout || 30000;
        
        // Notification system
        this.notificationContainer = null;
        this.notificationTimeout = options.notificationTimeout || 5000;
        
        this.initializeNotificationSystem();
    }

    /**
     * Initialize the notification system
     */
    initializeNotificationSystem() {
        // Create notification container if it doesn't exist
        if (!document.getElementById('connection-notifications')) {
            this.notificationContainer = document.createElement('div');
            this.notificationContainer.id = 'connection-notifications';
            this.notificationContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 300px;
            `;
            document.body.appendChild(this.notificationContainer);
        } else {
            this.notificationContainer = document.getElementById('connection-notifications');
        }
    }

    /**
     * Connect to WebSocket server
     */
    async connect() {
        if (this.isConnected || this.isReconnecting) {
            return;
        }

        try {
            this.isReconnecting = true;
            this.updateConnectionStatus('connecting');
            this.showNotification('Connecting to server...', 'info');

            this.socket = io({
                timeout: this.connectionTimeout,
                reconnection: false, // We handle reconnection manually
                forceNew: true
            });

            this.setupSocketEventHandlers();
            
            // Wait for connection with timeout
            await this.waitForConnection();
            
        } catch (error) {
            console.error('Connection failed:', error);
            this.handleConnectionError(error);
        }
    }

    /**
     * Wait for connection with timeout
     */
    waitForConnection() {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Connection timeout'));
            }, this.connectionTimeout);

            const onConnect = () => {
                clearTimeout(timeout);
                this.socket.off('connect', onConnect);
                this.socket.off('connect_error', onError);
                resolve();
            };

            const onError = (error) => {
                clearTimeout(timeout);
                this.socket.off('connect', onConnect);
                this.socket.off('connect_error', onError);
                reject(error);
            };

            this.socket.on('connect', onConnect);
            this.socket.on('connect_error', onError);
        });
    }

    /**
     * Setup WebSocket event handlers
     */
    setupSocketEventHandlers() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.isConnected = true;
            this.isReconnecting = false;
            this.reconnectAttempts = 0;
            this.currentReconnectDelay = this.reconnectDelay;
            this.lastConnectionTime = Date.now();
            this.updateConnectionStatus('connected');
            this.showNotification('Connected to server', 'success');
            this.startHeartbeat();
            this.flushMessageQueue();
            this.notifyConnectionListeners('connected');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('Disconnected from server:', reason);
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
            this.stopHeartbeat();
            this.notifyConnectionListeners('disconnected');
            
            if (reason === 'io server disconnect') {
                // Server initiated disconnect
                this.showNotification('Disconnected by server', 'warning');
            } else {
                // Client initiated disconnect or network issue
                this.showNotification('Connection lost', 'warning');
                this.scheduleReconnect();
            }
        });

        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.handleConnectionError(error);
        });

        this.socket.on('error', (error) => {
            console.error('Socket error:', error);
            this.handleConnectionError(error);
        });
    }

    /**
     * Handle connection errors
     */
    handleConnectionError(error) {
        this.isConnected = false;
        this.isReconnecting = false;
        this.updateConnectionStatus('disconnected');
        this.stopHeartbeat();
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.scheduleReconnect();
        } else {
            this.showNotification('Connection failed. Please refresh the page.', 'error');
            this.enableOfflineMode();
        }
        
        this.notifyErrorListeners(error);
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }

        this.reconnectAttempts++;
        this.currentReconnectDelay = Math.min(
            this.currentReconnectDelay * 1.5,
            this.maxReconnectDelay
        );

        console.log(`Scheduling reconnect attempt ${this.reconnectAttempts} in ${this.currentReconnectDelay}ms`);
        
        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, this.currentReconnectDelay);
    }

    /**
     * Start heartbeat to detect connection issues
     */
    startHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }

        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected && this.socket) {
                this.socket.emit('ping');
            }
        }, this.heartbeatTimeout);
    }

    /**
     * Stop heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    /**
     * Enable offline mode
     */
    enableOfflineMode() {
        this.offlineMode = true;
        this.showNotification('Working in offline mode', 'info');
        console.log('Offline mode enabled');
    }

    /**
     * Disable offline mode
     */
    disableOfflineMode() {
        this.offlineMode = false;
        console.log('Offline mode disabled');
    }

    /**
     * Send message to server
     */
    emit(event, data) {
        if (this.isConnected && this.socket) {
            this.socket.emit(event, data);
            return true;
        } else {
            // Queue message for later
            this.queueMessage(event, data);
            return false;
        }
    }

    /**
     * Queue message for later transmission
     */
    queueMessage(event, data) {
        if (this.messageQueue.length >= this.maxQueueSize) {
            this.messageQueue.shift(); // Remove oldest message
        }
        
        this.messageQueue.push({
            event,
            data,
            timestamp: Date.now()
        });
        
        console.log(`Message queued: ${event} (${this.messageQueue.length} in queue)`);
    }

    /**
     * Flush queued messages
     */
    flushMessageQueue() {
        if (!this.isConnected || !this.socket) {
            return;
        }

        const messages = [...this.messageQueue];
        this.messageQueue = [];

        messages.forEach(({ event, data }) => {
            try {
                this.socket.emit(event, data);
                console.log(`Queued message sent: ${event}`);
            } catch (error) {
                console.error(`Failed to send queued message ${event}:`, error);
            }
        });
    }

    /**
     * Disconnect from server
     */
    disconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        this.stopHeartbeat();
        
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        
        this.isConnected = false;
        this.isReconnecting = false;
        this.updateConnectionStatus('disconnected');
        console.log('Disconnected from server');
    }

    /**
     * Update connection status UI
     */
    updateConnectionStatus(status) {
        const statusElements = document.querySelectorAll('.connection-status, .status-indicator');
        
        statusElements.forEach(element => {
            if (element.classList.contains('status-indicator')) {
                element.className = `status-indicator status-${status}`;
            } else if (element.querySelector('.status-indicator')) {
                const indicator = element.querySelector('.status-indicator');
                indicator.className = `status-indicator status-${status}`;
            }
        });

        // Update status text
        const statusTexts = {
            'connected': 'Connected',
            'disconnected': 'Disconnected',
            'connecting': 'Connecting...',
            'reconnecting': 'Reconnecting...'
        };

        const statusTextElements = document.querySelectorAll('.connection-text, .status-text');
        statusTextElements.forEach(element => {
            element.textContent = statusTexts[status] || 'Unknown';
        });
    }

    /**
     * Show notification to user
     */
    showNotification(message, type = 'info', duration = this.notificationTimeout) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${this.getBootstrapAlertType(type)} alert-dismissible fade show`;
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        this.notificationContainer.appendChild(notification);

        // Auto-remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, duration);
        }

        return notification;
    }

    /**
     * Get Bootstrap alert type
     */
    getBootstrapAlertType(type) {
        const typeMap = {
            'success': 'success',
            'error': 'danger',
            'warning': 'warning',
            'info': 'info'
        };
        return typeMap[type] || 'info';
    }

    /**
     * Add connection status listener
     */
    onConnectionChange(callback) {
        this.connectionListeners.push(callback);
    }

    /**
     * Add error listener
     */
    onError(callback) {
        this.errorListeners.push(callback);
    }

    /**
     * Notify connection listeners
     */
    notifyConnectionListeners(status) {
        this.connectionListeners.forEach(callback => {
            try {
                callback(status);
            } catch (error) {
                console.error('Connection listener error:', error);
            }
        });
    }

    /**
     * Notify error listeners
     */
    notifyErrorListeners(error) {
        this.errorListeners.forEach(callback => {
            try {
                callback(error);
            } catch (error) {
                console.error('Error listener error:', error);
            }
        });
    }

    /**
     * Get connection status
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            isReconnecting: this.isReconnecting,
            reconnectAttempts: this.reconnectAttempts,
            offlineMode: this.offlineMode,
            queuedMessages: this.messageQueue.length,
            lastConnectionTime: this.lastConnectionTime
        };
    }

    /**
     * Check if connection is healthy
     */
    isConnectionHealthy() {
        if (!this.isConnected) {
            return false;
        }
        
        if (this.lastConnectionTime) {
            const timeSinceLastConnection = Date.now() - this.lastConnectionTime;
            return timeSinceLastConnection < this.heartbeatTimeout * 2;
        }
        
        return true;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConnectionManager;
} 