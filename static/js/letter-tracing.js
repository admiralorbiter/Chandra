// Letter Tracing Plugin for Chandra
// Registers itself as a lesson plugin

function drawLetterOverlay(canvas, letter) {
    if (!canvas || !letter) return;
    const ctx = canvas.getContext('2d');
    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.globalAlpha = 0.15;
    ctx.font = 'bold 320px Arial';
    ctx.fillStyle = '#007bff';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(letter, canvas.width / 2, canvas.height / 2);
    ctx.restore();
}

window.registerLessonPlugin({
    init(player) {
        // Show the letter tracing section
        const section = document.getElementById('letterTracingSection');
        if (section) section.style.display = '';
        // Hide finger count/running total (optional)
        if (player.fingerCount) player.fingerCount.parentElement.style.display = 'none';
        if (player.runningTotalSpan) player.runningTotalSpan.parentElement.style.display = 'none';

        // DOM elements
        const currentLetterDiv = document.getElementById('currentLetter');
        const letterPatternDiv = document.getElementById('letterPattern');
        const overlayCanvas = document.getElementById('overlayCanvas');
        let currentLetter = 'A';
        let currentPattern = '';

        // Listen for backend events via connectionManager
        player.connectionManager.socket.on('lesson_started', (data) => {
            if (data.current_letter) {
                currentLetter = data.current_letter;
                if (currentLetterDiv) currentLetterDiv.textContent = currentLetter;
            }
            if (data.pattern_description) {
                currentPattern = data.pattern_description;
                if (letterPatternDiv) letterPatternDiv.textContent = currentPattern;
            }
            drawLetterOverlay(overlayCanvas, currentLetter);
        });
        player.connectionManager.socket.on('letter_completed', (data) => {
            if (data.next_letter) {
                currentLetter = data.next_letter;
                if (currentLetterDiv) currentLetterDiv.textContent = currentLetter;
            }
            if (data.pattern_description) {
                currentPattern = data.pattern_description;
                if (letterPatternDiv) letterPatternDiv.textContent = currentPattern;
            }
            drawLetterOverlay(overlayCanvas, currentLetter);
        });
        player.connectionManager.socket.on('gesture_processed', (data) => {
            if (data.current_letter) {
                currentLetter = data.current_letter;
                if (currentLetterDiv) currentLetterDiv.textContent = currentLetter;
                drawLetterOverlay(overlayCanvas, currentLetter);
            }
        });
        // Initial overlay
        drawLetterOverlay(overlayCanvas, currentLetter);
    }
}); 