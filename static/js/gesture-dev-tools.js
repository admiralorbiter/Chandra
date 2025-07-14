// Gesture Dev Tools Module
// Usage: attachGestureDevTools(engine, { container: HTMLElement })

console.log('[Gesture Dev Tools] Module loaded');

export function attachGestureDevTools(engine, options = {}) {
    console.log('[Gesture Dev Tools] Initializing for engine:', engine);
    const container = options.container || document.body;
    let recording = false;
    let recordedGestures = [];

    // Create controls
    const controls = document.createElement('div');
    controls.style.margin = '16px 0';
    controls.innerHTML = `
        <div class="btn-group" role="group">
            <button id="gdt-debugBtn" class="btn btn-outline-info">🛠️ Debug Overlay</button>
            <button id="gdt-startRecBtn" class="btn btn-outline-success">⏺️ Start Rec</button>
            <button id="gdt-stopRecBtn" class="btn btn-outline-danger" disabled>⏹️ Stop Rec</button>
            <button id="gdt-downloadJsonBtn" class="btn btn-outline-primary" disabled>⬇️ JSON</button>
            <button id="gdt-downloadCsvBtn" class="btn btn-outline-secondary" disabled>⬇️ CSV</button>
        </div>
    `;
    container.appendChild(controls);
    console.log('[Gesture Dev Tools] Controls created:', controls);

    // Add a recording badge and counter
    const badge = document.createElement('span');
    badge.style.display = 'none';
    badge.style.marginLeft = '12px';
    badge.style.fontWeight = 'bold';
    badge.style.color = '#d9534f';
    badge.textContent = '● Recording...';
    controls.appendChild(badge);

    const counter = document.createElement('span');
    counter.style.display = 'none';
    counter.style.marginLeft = '12px';
    counter.style.fontWeight = 'bold';
    counter.style.color = '#007bff';
    counter.textContent = '(0 frames)';
    controls.appendChild(counter);

    function updateCounter() {
        if (recording) {
            counter.textContent = `(${recordedGestures.length} frames)`;
        } else {
            counter.textContent = '';
        }
    }

    // Get buttons
    const debugBtn = controls.querySelector('#gdt-debugBtn');
    const startRecBtn = controls.querySelector('#gdt-startRecBtn');
    const stopRecBtn = controls.querySelector('#gdt-stopRecBtn');
    const downloadJsonBtn = controls.querySelector('#gdt-downloadJsonBtn');
    const downloadCsvBtn = controls.querySelector('#gdt-downloadCsvBtn');

    // Overlay toggle
    debugBtn.addEventListener('click', () => {
        engine.debugMode = !engine.debugMode;
        debugBtn.classList.toggle('btn-info', engine.debugMode);
        debugBtn.classList.toggle('btn-outline-info', !engine.debugMode);
        debugBtn.textContent = engine.debugMode ? '🛠️ Debug ON' : '🛠️ Debug Overlay';
    });

    // Recorder logic
    startRecBtn.addEventListener('click', () => {
        console.log('[Gesture Dev Tools] Start Recording clicked');
        recording = true;
        recordedGestures = [];
        startRecBtn.disabled = true;
        stopRecBtn.disabled = false;
        downloadJsonBtn.disabled = true;
        downloadCsvBtn.disabled = true;
        badge.style.display = '';
        counter.style.display = '';
        updateCounter();
    });
    stopRecBtn.addEventListener('click', () => {
        recording = false;
        startRecBtn.disabled = false;
        stopRecBtn.disabled = true;
        badge.style.display = 'none';
        counter.style.display = 'none';
        if (recordedGestures.length === 0) {
            alert('No gestures were recorded. Try again with your hand visible and detection running.');
        } else {
            // Show summary
            const uniqueGestures = new Set(recordedGestures.map(g => g.gesture));
            alert(`Recording complete!\nFrames: ${recordedGestures.length}\nUnique gestures: ${Array.from(uniqueGestures).join(', ')}`);
        }
        downloadJsonBtn.disabled = recordedGestures.length === 0;
        downloadCsvBtn.disabled = recordedGestures.length === 0;
    });
    downloadJsonBtn.addEventListener('click', () => {
        if (recordedGestures.length === 0) {
            alert('No gestures to download.');
            return;
        }
        const blob = new Blob([JSON.stringify(recordedGestures, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gesture_recording_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
    downloadCsvBtn.addEventListener('click', () => {
        if (recordedGestures.length === 0) {
            alert('No gestures to download.');
            return;
        }
        const header = ['timestamp', 'gesture', 'confidence', 'fingerCount', 'landmarks'];
        const rows = recordedGestures.map(g => [
            g.timestamp,
            g.gesture,
            g.confidence,
            g.fingerCount,
            JSON.stringify(g.landmarks)
        ]);
        const csvContent = [header, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `gesture_recording_${new Date().toISOString().replace(/[:.]/g, '-')}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    // Patch GestureEngine to support multiple listeners
    const proto = engine.constructor.prototype;
    if (!proto._gestureListeners) {
        proto._gestureListeners = [];
        proto.addGestureListener = function(fn) {
            this._gestureListeners.push(fn);
        };
        const origOnGesture = proto.onGesture;
        proto.onGesture = function(fn) {
            this.addGestureListener(fn);
            if (origOnGesture) origOnGesture.call(this, fn);
        };
        // Patch handleGestureDetected to call all listeners
        const origHandle = proto.handleGestureDetected;
        proto.handleGestureDetected = function(gesture) {
            console.log('[Gesture Dev Tools] Patched handleGestureDetected called', gesture);
            if (origHandle) origHandle.call(this, gesture);
            if (this._gestureListeners) {
                this._gestureListeners.forEach(fn => {
                    try { fn(gesture); } catch (e) { console.error('Gesture listener error:', e); }
                });
            }
        };
    }

    // Hook into gesture events using addGestureListener
    engine.addGestureListener((gestureEvent) => {
        if (recording) {
            let landmarks = null;
            if (engine.lastLandmarks) landmarks = engine.lastLandmarks;
            const record = {
                timestamp: Date.now(),
                gesture: gestureEvent.name,
                confidence: gestureEvent.confidence,
                fingerCount: gestureEvent.fingerCount,
                landmarks: landmarks
            };
            recordedGestures.push(record);
            updateCounter();
            console.log('[Gesture Recorder] Recorded:', record);
        }
    });
} 