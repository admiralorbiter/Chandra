/**
 * Chandra Data Analysis Lesson Player
 * Handles interactive data analysis with Chart.js visualizations
 */

import { attachGestureDevTools } from './gesture-dev-tools.js';

class DataAnalysisPlayer {
    constructor() {
        this.lessonData = null;
        this.webcamManager = null;
        this.gestureEngine = null;
        this.connectionManager = null;
        this.charts = {};
        this.analysisResults = {};
        this.completedAnalyses = new Set();
        this.isRunning = false;
        
        // UI elements
        this.elements = {
            video: null,
            canvas: null,
            startBtn: null,
            stopBtn: null,
            debugBtn: null,
            gestureName: null,
            gestureConfidence: null,
            lessonProgress: null,
            progressText: null,
            datasetInfo: null,
            gestureMapping: null,
            analysisResults: null
        };
        
        // Chart colors
        this.colors = {
            primary: '#007bff',
            secondary: '#6c757d',
            success: '#28a745',
            warning: '#ffc107',
            danger: '#dc3545',
            info: '#17a2b8'
        };
        
        // Analysis type configurations
        this.analysisConfigs = {
            descriptive: {
                title: 'Descriptive Statistics',
                icon: '📊',
                color: this.colors.primary
            },
            correlation: {
                title: 'Correlation Analysis',
                icon: '🔗',
                color: this.colors.info
            },
            distribution: {
                title: 'Distribution Analysis',
                icon: '📈',
                color: this.colors.success
            },
            regression: {
                title: 'Regression Modeling',
                icon: '📉',
                color: this.colors.warning
            },
            clustering: {
                title: 'Clustering Analysis',
                icon: '🎯',
                color: this.colors.danger
            },
            pca: {
                title: 'Principal Component Analysis',
                icon: '🔍',
                color: this.colors.secondary
            }
        };
    }
    
    init(lessonData) {
        this.lessonData = lessonData;
        this.initializeElements();
        this.initializeManagers();
        this.setupEventListeners();
        this.setupSocketListeners();
        this.renderInitialUI();
        
        console.log('Data Analysis Player initialized', lessonData);
    }
    
    initializeElements() {
        this.elements.video = document.getElementById('video');
        this.elements.canvas = document.getElementById('canvas');
        this.elements.startBtn = document.getElementById('startBtn');
        this.elements.stopBtn = document.getElementById('stopBtn');
        this.elements.debugBtn = document.getElementById('debugBtn');
        this.elements.gestureName = document.getElementById('gestureName');
        this.elements.gestureConfidence = document.getElementById('gestureConfidence');
        this.elements.lessonProgress = document.getElementById('lessonProgress');
        this.elements.progressText = document.getElementById('progressText');
        this.elements.datasetInfo = document.getElementById('datasetInfo');
        this.elements.gestureMapping = document.getElementById('gestureMapping');
        this.elements.analysisResults = document.getElementById('analysisResults');
    }
    
    initializeManagers() {
        // Initialize webcam manager
        this.webcamManager = new WebcamManager();
        this.webcamManager.setOnReady(() => {
            console.log('Webcam ready');
        });
        
        // Initialize gesture engine
        this.gestureEngine = new GestureEngine();
        this.gestureEngine.onGesture((gestureData) => {
            this.handleGesture(gestureData);
        });
        
        // Initialize connection manager
        this.connectionManager = new ConnectionManager();
        
        // Attach dev tools
        attachGestureDevTools(this.gestureEngine, this.elements.video, this.elements.canvas);
    }
    
    setupEventListeners() {
        this.elements.startBtn.addEventListener('click', () => this.startDetection());
        this.elements.stopBtn.addEventListener('click', () => this.stopDetection());
        this.elements.debugBtn.addEventListener('click', () => this.toggleDebug());
    }
    
    setupSocketListeners() {
        const socket = io();
        
        socket.on('lesson_started', (data) => {
            console.log('Lesson started:', data);
            this.handleLessonStarted(data);
        });
        
        socket.on('analysis_complete', (data) => {
            console.log('Analysis complete:', data);
            this.handleAnalysisComplete(data);
        });
        
        socket.on('gesture_processed', (data) => {
            console.log('Gesture processed:', data);
            this.handleGestureProcessed(data);
        });
        
        socket.on('lesson_completed', (data) => {
            console.log('Lesson completed:', data);
            this.handleLessonCompleted(data);
        });
        
        socket.on('lesson_tick', (data) => {
            this.handleLessonTick(data);
        });
    }
    
    renderInitialUI() {
        this.renderDatasetInfo();
        this.renderGestureMapping();
        this.renderAnalysisPanels();
    }
    
    renderDatasetInfo() {
        const datasetInfo = this.lessonData.dataset_info;
        if (!datasetInfo) return;
        
        const html = `
            <div class="row">
                <div class="col-md-6">
                    <h6>${datasetInfo.name || 'Dataset'}</h6>
                    <p class="text-muted">${datasetInfo.description || 'Interactive dataset for analysis'}</p>
                </div>
                <div class="col-md-6">
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">${datasetInfo.size || 0}</div>
                            <div class="stat-label">Records</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${datasetInfo.features?.length || 0}</div>
                            <div class="stat-label">Features</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        this.elements.datasetInfo.innerHTML = html;
    }
    
    renderGestureMapping() {
        const mappings = this.lessonData.gesture_mappings;
        if (!mappings) return;
        
        const gestureIcons = {
            fist: '✊',
            open_hand: '✋',
            point: '👆',
            victory: '✌️',
            thumbs_up: '👍',
            ok: '👌'
        };
        
        const html = Object.entries(mappings).map(([gesture, info]) => {
            const isCompleted = this.completedAnalyses.has(info.analysis_type);
            return `
                <div class="gesture-card ${isCompleted ? 'completed' : ''}" data-gesture="${gesture}">
                    <div class="gesture-icon">${gestureIcons[gesture] || '👋'}</div>
                    <div class="fw-bold">${info.name}</div>
                    <div class="text-muted small">${info.description}</div>
                    ${isCompleted ? '<div class="text-success small">✓ Completed</div>' : ''}
                </div>
            `;
        }).join('');
        
        this.elements.gestureMapping.innerHTML = html;
    }
    
    renderAnalysisPanels() {
        const analysisTypes = ['descriptive', 'correlation', 'distribution', 'regression', 'clustering', 'pca'];
        
        const html = analysisTypes.map(type => {
            const config = this.analysisConfigs[type];
            const isCompleted = this.completedAnalyses.has(type);
            const result = this.analysisResults[type];
            
            return `
                <div class="analysis-panel" id="analysis-${type}">
                    <div class="analysis-header">
                        <div class="analysis-type">${config.icon} ${config.title}</div>
                        <div class="analysis-status ${isCompleted ? 'completed' : ''}">
                            ${isCompleted ? 'Completed' : 'Waiting...'}
                        </div>
                    </div>
                    <div class="analysis-content" id="content-${type}">
                        ${isCompleted ? this.renderAnalysisContent(type, result) : '<p class="text-muted">Perform the gesture to trigger this analysis.</p>'}
                    </div>
                </div>
            `;
        }).join('');
        
        this.elements.analysisResults.innerHTML = html;
    }
    
    renderAnalysisContent(type, result) {
        if (!result) return '<p class="text-muted">No results available.</p>';
        
        switch (type) {
            case 'descriptive':
                return this.renderDescriptiveStats(result);
            case 'correlation':
                return this.renderCorrelationResults(result);
            case 'distribution':
                return this.renderDistributionResults(result);
            case 'regression':
                return this.renderRegressionResults(result);
            case 'clustering':
                return this.renderClusteringResults(result);
            case 'pca':
                return this.renderPCAResults(result);
            default:
                return '<p class="text-muted">Analysis results not available.</p>';
        }
    }
    
    renderDescriptiveStats(result) {
        const columns = Object.keys(result);
        const html = columns.map(col => {
            const stats = result[col];
            return `
                <div class="mb-3">
                    <h6>${col}</h6>
                    <div class="stats-grid">
                        <div class="stat-item">
                            <div class="stat-value">${stats.mean?.toFixed(2) || 'N/A'}</div>
                            <div class="stat-label">Mean</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${stats.std?.toFixed(2) || 'N/A'}</div>
                            <div class="stat-label">Std Dev</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${stats.outliers || 0}</div>
                            <div class="stat-label">Outliers</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value">${stats.skewness?.toFixed(2) || 'N/A'}</div>
                            <div class="stat-label">Skewness</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        return html;
    }
    
    renderCorrelationResults(result) {
        const strongest = result.strongest;
        if (!strongest) return '<p class="text-muted">No correlation data available.</p>';
        
        const html = `
            <div class="mb-3">
                <h6>Strongest Correlation</h6>
                <div class="alert alert-info">
                    <strong>${strongest.variables.join(' ↔ ')}</strong><br>
                    Correlation: ${strongest.correlation.toFixed(3)}<br>
                    Strength: ${strongest.strength}
                </div>
            </div>
            <div class="chart-container">
                <canvas id="correlationChart"></canvas>
            </div>
        `;
        
        setTimeout(() => this.createCorrelationChart(result), 100);
        return html;
    }
    
    renderDistributionResults(result) {
        const columns = Object.keys(result);
        const normalColumns = columns.filter(col => result[col].normality_test?.is_normal);
        
        const html = `
            <div class="mb-3">
                <h6>Distribution Summary</h6>
                <div class="alert alert-success">
                    ${normalColumns.length} out of ${columns.length} variables are normally distributed
                </div>
            </div>
            <div class="chart-container">
                <canvas id="distributionChart"></canvas>
            </div>
        `;
        
        setTimeout(() => this.createDistributionChart(result), 100);
        return html;
    }
    
    renderRegressionResults(result) {
        const html = `
            <div class="mb-3">
                <h6>Regression Model: ${result.target}</h6>
                <div class="stats-grid">
                    <div class="stat-item">
                        <div class="stat-value">${result.r2_score?.toFixed(3) || 'N/A'}</div>
                        <div class="stat-label">R² Score</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${result.rmse?.toFixed(0) || 'N/A'}</div>
                        <div class="stat-label">RMSE</div>
                    </div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="regressionChart"></canvas>
            </div>
        `;
        
        setTimeout(() => this.createRegressionChart(result), 100);
        return html;
    }
    
    renderClusteringResults(result) {
        const html = `
            <div class="mb-3">
                <h6>K-Means Clustering (k=${result.n_clusters})</h6>
                <div class="row">
                    ${Object.entries(result.cluster_analysis).map(([cluster, info]) => `
                        <div class="col-md-4">
                            <div class="stat-item">
                                <div class="stat-value">${info.size}</div>
                                <div class="stat-label">${cluster.replace('_', ' ')}</div>
                                <div class="text-muted small">${info.percentage.toFixed(1)}%</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
            <div class="chart-container">
                <canvas id="clusteringChart"></canvas>
            </div>
        `;
        
        setTimeout(() => this.createClusteringChart(result), 100);
        return html;
    }
    
    renderPCAResults(result) {
        const html = `
            <div class="mb-3">
                <h6>Principal Component Analysis</h6>
                <div class="alert alert-info">
                    ${result.components_95_percent} components explain 95% of variance
                </div>
            </div>
            <div class="chart-container">
                <canvas id="pcaChart"></canvas>
            </div>
        `;
        
        setTimeout(() => this.createPCAChart(result), 100);
        return html;
    }
    
    createCorrelationChart(result) {
        const ctx = document.getElementById('correlationChart');
        if (!ctx) return;
        
        const pairs = result.pairs.slice(0, 10); // Top 10 correlations
        
        this.charts.correlation = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: pairs.map(p => p.variables.join(' vs ')),
                datasets: [{
                    label: 'Correlation',
                    data: pairs.map(p => p.correlation),
                    backgroundColor: pairs.map(p => p.correlation > 0 ? this.colors.success : this.colors.danger),
                    borderColor: this.colors.primary,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        min: -1,
                        max: 1
                    }
                }
            }
        });
    }
    
    createDistributionChart(result) {
        const ctx = document.getElementById('distributionChart');
        if (!ctx) return;
        
        const columns = Object.keys(result);
        const firstColumn = columns[0];
        const histData = result[firstColumn].histogram;
        
        this.charts.distribution = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: histData.bin_centers.map(c => c.toFixed(1)),
                datasets: [{
                    label: `${firstColumn} Distribution`,
                    data: histData.counts,
                    backgroundColor: this.colors.primary,
                    borderColor: this.colors.primary,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    createRegressionChart(result) {
        const ctx = document.getElementById('regressionChart');
        if (!ctx) return;
        
        const data = result.predictions_sample.map((pred, i) => ({
            x: result.actual_sample[i],
            y: pred
        }));
        
        this.charts.regression = new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [{
                    label: 'Predictions vs Actual',
                    data: data,
                    backgroundColor: this.colors.primary,
                    borderColor: this.colors.primary
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Actual Values'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Predicted Values'
                        }
                    }
                }
            }
        });
    }
    
    createClusteringChart(result) {
        const ctx = document.getElementById('clusteringChart');
        if (!ctx) return;
        
        const clusterData = Object.entries(result.cluster_analysis).map(([cluster, info]) => ({
            label: cluster.replace('_', ' '),
            data: info.size,
            backgroundColor: [this.colors.primary, this.colors.success, this.colors.warning][parseInt(cluster.split('_')[1])]
        }));
        
        this.charts.clustering = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: clusterData.map(d => d.label),
                datasets: [{
                    data: clusterData.map(d => d.data),
                    backgroundColor: clusterData.map(d => d.backgroundColor),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    createPCAChart(result) {
        const ctx = document.getElementById('pcaChart');
        if (!ctx) return;
        
        this.charts.pca = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: result.explained_variance_ratio.map((_, i) => `PC${i + 1}`),
                datasets: [{
                    label: 'Explained Variance',
                    data: result.explained_variance_ratio,
                    backgroundColor: this.colors.info,
                    borderColor: this.colors.info,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }
    
    async startDetection() {
        try {
            await this.webcamManager.initialize(this.elements.video);
            await this.gestureEngine.initialize(this.elements.video, this.elements.canvas);
            
            this.gestureEngine.start();
            this.isRunning = true;
            
            this.elements.startBtn.disabled = true;
            this.elements.stopBtn.disabled = false;
            
            // Start the lesson
            const socket = io();
            socket.emit('lesson_start', {
                lesson_id: this.lessonData.id,
                script_id: this.lessonData.script_id
            });
            
        } catch (error) {
            console.error('Failed to start detection:', error);
            alert('Failed to start camera detection. Please check camera permissions.');
        }
    }
    
    stopDetection() {
        this.gestureEngine.stop();
        this.webcamManager.stop();
        this.isRunning = false;
        
        this.elements.startBtn.disabled = false;
        this.elements.stopBtn.disabled = true;
        
        this.elements.gestureName.textContent = 'Detection stopped';
        this.elements.gestureConfidence.textContent = 'Click "Start Detection" to resume';
    }
    
    toggleDebug() {
        this.gestureEngine.debugMode = !this.gestureEngine.debugMode;
        this.elements.debugBtn.textContent = this.gestureEngine.debugMode ? 'Hide Debug' : 'Show Debug';
    }
    
    handleGesture(gestureData) {
        // Update UI
        this.elements.gestureName.textContent = gestureData.gesture || 'Unknown';
        this.elements.gestureConfidence.textContent = `Confidence: ${Math.round(gestureData.confidence * 100)}%`;
        
        // Send to server
        const socket = io();
        socket.emit('lesson_gesture', {
            lesson_id: this.lessonData.id,
            script_id: this.lessonData.script_id,
            gesture_data: gestureData
        });
    }
    
    handleLessonStarted(data) {
        this.renderDatasetInfo();
        this.renderGestureMapping();
        this.renderAnalysisPanels();
    }
    
    handleAnalysisComplete(data) {
        const { type, results } = data;
        
        this.analysisResults[type] = results;
        this.completedAnalyses.add(type);
        
        // Update the specific analysis panel
        const contentElement = document.getElementById(`content-${type}`);
        if (contentElement) {
            contentElement.innerHTML = this.renderAnalysisContent(type, results);
        }
        
        // Update gesture mapping
        this.renderGestureMapping();
        
        // Show success message
        this.showMessage(`${this.analysisConfigs[type].title} completed!`, 'success');
    }
    
    handleGestureProcessed(data) {
        const { progress } = data;
        
        this.elements.lessonProgress.style.width = `${progress}%`;
        this.elements.progressText.textContent = `${Math.round(progress)}% Complete`;
    }
    
    handleLessonCompleted(data) {
        this.showMessage('Congratulations! You have completed all data analysis tasks!', 'success');
        this.elements.lessonProgress.style.width = '100%';
        this.elements.progressText.textContent = '100% Complete';
    }
    
    handleLessonTick(data) {
        // Update any time-based UI elements
        if (data.lesson_duration) {
            const minutes = Math.floor(data.lesson_duration / 60);
            const seconds = Math.floor(data.lesson_duration % 60);
            // Could add duration display if needed
        }
    }
    
    showMessage(message, type = 'info') {
        const alertClass = type === 'success' ? 'success-message' : 'error-message';
        const messageElement = document.createElement('div');
        messageElement.className = alertClass;
        messageElement.textContent = message;
        
        this.elements.analysisResults.insertBefore(messageElement, this.elements.analysisResults.firstChild);
        
        setTimeout(() => {
            messageElement.remove();
        }, 5000);
    }
    
    destroy() {
        // Clean up charts
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        
        // Stop detection
        if (this.isRunning) {
            this.stopDetection();
        }
    }
}

// Create global instance
window.DataAnalysisPlayer = new DataAnalysisPlayer();

export default DataAnalysisPlayer; 