# Chandra Robustness & Error Handling

This document describes the robustness and error handling features implemented in Chandra to ensure a reliable user experience even under adverse conditions.

## Overview

Chandra includes comprehensive error handling and connectivity management to provide a smooth user experience even when:
- Network connectivity is intermittent
- JavaScript errors occur in the browser
- WebSocket connections are lost
- Camera permissions are denied
- Server-side errors occur

## Features

### 1. Connection Manager

The `ConnectionManager` class provides robust WebSocket connectivity with automatic reconnection and offline mode support.

#### Key Features:
- **Auto-reconnect**: Automatically attempts to reconnect when connection is lost
- **Exponential backoff**: Increases delay between reconnection attempts
- **Message queuing**: Queues messages when offline and sends them when reconnected
- **Heartbeat monitoring**: Detects connection health and triggers reconnection if needed
- **Offline mode**: Allows limited functionality when completely disconnected
- **User notifications**: Shows connection status changes to users

#### Usage:
```javascript
// Initialize connection manager
const connectionManager = new ConnectionManager({
    maxReconnectAttempts: 10,
    reconnectDelay: 1000,
    maxReconnectDelay: 30000,
    connectionTimeout: 5000,
    heartbeatTimeout: 30000
});

// Connect to server
await connectionManager.connect();

// Send messages (will be queued if offline)
connectionManager.emit('gesture', gestureData);

// Listen for connection changes
connectionManager.onConnectionChange((status) => {
    console.log('Connection status:', status);
});
```

### 2. Error Boundary

The `ErrorBoundary` class provides comprehensive JavaScript error handling and reporting.

#### Key Features:
- **Global error catching**: Catches unhandled JavaScript errors and promise rejections
- **Error throttling**: Prevents spam by limiting error reports
- **User-friendly messages**: Shows appropriate error messages to users
- **Backend reporting**: Automatically reports errors to the server for monitoring
- **Critical error detection**: Identifies errors that affect core functionality
- **Console interception**: Captures console errors for additional context

#### Usage:
```javascript
// Error boundary is automatically initialized globally
window.errorBoundary.onError((error, context) => {
    console.log('Error caught:', error, context);
});

// Wrap functions with error boundary
const safeFunction = window.errorBoundary.wrapFunction(myFunction, {
    context: 'my_function'
});

// Wrap async functions
const safeAsyncFunction = window.errorBoundary.wrapAsyncFunction(myAsyncFunction, {
    context: 'my_async_function'
});
```

### 3. Backend Error Reporting

The backend includes an API endpoint for receiving and logging frontend errors.

#### Endpoint: `POST /api/errors`

Accepts error reports from the frontend and logs them for monitoring and debugging.

**Request Body:**
```json
{
    "message": "Error message",
    "stack": "Error stack trace",
    "name": "Error name",
    "timestamp": "2024-01-01T12:00:00Z",
    "userAgent": "Browser user agent",
    "url": "Page URL",
    "context": {
        "type": "error_type",
        "functionName": "function_name"
    },
    "sessionId": "session_id",
    "userId": "user_id"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Error reported successfully"
}
```

## Implementation Details

### Connection Manager Architecture

1. **Connection State Management**
   - Tracks connection status (connected, disconnected, connecting, reconnecting)
   - Manages reconnection attempts with exponential backoff
   - Monitors connection health with heartbeat

2. **Message Queuing**
   - Queues messages when offline
   - Flushes queue when reconnected
   - Limits queue size to prevent memory issues

3. **User Notifications**
   - Shows connection status changes
   - Provides feedback during reconnection attempts
   - Indicates offline mode when appropriate

### Error Boundary Architecture

1. **Error Detection**
   - Global error event listeners
   - Promise rejection handlers
   - Resource loading error handlers
   - Console error interception

2. **Error Classification**
   - Critical errors (affect core functionality)
   - Non-critical errors (cosmetic or minor issues)
   - Resource errors (failed to load assets)

3. **Error Reporting**
   - Throttled reporting to prevent spam
   - Structured error data with context
   - Automatic backend reporting

## Configuration

### Connection Manager Options

```javascript
const connectionManager = new ConnectionManager({
    maxReconnectAttempts: 10,        // Maximum reconnection attempts
    reconnectDelay: 1000,            // Initial delay between attempts (ms)
    maxReconnectDelay: 30000,        // Maximum delay between attempts (ms)
    connectionTimeout: 5000,          // Connection timeout (ms)
    heartbeatTimeout: 30000,          // Heartbeat interval (ms)
    maxQueueSize: 100,               // Maximum queued messages
    notificationTimeout: 5000         // Notification display time (ms)
});
```

### Error Boundary Options

```javascript
const errorBoundary = new ErrorBoundary({
    maxErrorReports: 10,             // Maximum error reports to queue
    errorThrottle: 5000,             // Minimum time between reports (ms)
    reportEndpoint: '/api/errors'    // Backend endpoint for reporting
});
```

## Testing

Run the robustness test suite:

```bash
python test_robustness.py
```

This will test:
- Error reporting endpoint
- Connection status monitoring
- Script endpoint functionality

## Monitoring

### Frontend Monitoring

The error boundary provides statistics for monitoring:

```javascript
const stats = window.errorBoundary.getErrorStats();
console.log('Error count:', stats.errorCount);
console.log('Queued reports:', stats.queuedReports);
console.log('Last error time:', stats.lastErrorTime);
```

### Backend Monitoring

Errors are logged to the application log with structured data:

```python
# Errors are logged with context
logging.error(f"Frontend error: {error_report['message']}", extra={
    'error_report': error_report,
    'session_id': error_report['session_id'],
    'user_id': error_report['user_id']
})
```

## Best Practices

1. **Always wrap critical functions** with the error boundary
2. **Handle connection state** in your UI components
3. **Provide user feedback** for connection issues
4. **Monitor error patterns** in production
5. **Test offline scenarios** during development

## Troubleshooting

### Common Issues

1. **Connection not reconnecting**
   - Check network connectivity
   - Verify server is running
   - Check browser console for errors

2. **Errors not being reported**
   - Verify error boundary is initialized
   - Check network connectivity
   - Verify backend endpoint is accessible

3. **Too many error reports**
   - Adjust error throttling settings
   - Check for error loops in code
   - Review error classification logic

### Debug Mode

Enable debug logging for connection manager:

```javascript
connectionManager.debugMode = true;
```

This will provide detailed logging of connection events and message queuing. 