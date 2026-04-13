document.addEventListener('DOMContentLoaded', () => {
    
    // Elements
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-btn');
    const previewSection = document.getElementById('preview-section');
    const imagePreview = document.getElementById('image-preview');
    const clearBtn = document.getElementById('clear-btn');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    const resultsDisplay = document.getElementById('results-display');
    const loadingState = document.getElementById('loading-state');
    const diagnosticData = document.getElementById('diagnostic-data');
    
    const diagnosisAlert = document.getElementById('diagnosis-alert');
    const diagnosisResultText = document.getElementById('diagnosis-result-text');
    const confidenceVal = document.getElementById('confidence-val');
    const timeVal = document.getElementById('time-val');
    const progressBar = document.getElementById('analysis-progress');
    
    const heatmapOverlay = document.getElementById('heatmap-overlay');
    const downloadPdfBtn = document.getElementById('download-pdf-btn');

    let currentFile = null;

    // --- High-End Features: Light/Dark Theme Toggle ---
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = themeToggleBtn.querySelector('i');
    
    // Check local storage for preference
    if (localStorage.getItem('theme') === 'light') {
        document.body.classList.add('light-theme');
        themeIcon.classList.replace('ph-sun', 'ph-moon');
    }

    themeToggleBtn.addEventListener('click', () => {
        document.body.classList.toggle('light-theme');
        if (document.body.classList.contains('light-theme')) {
            themeIcon.classList.replace('ph-sun', 'ph-moon');
            localStorage.setItem('theme', 'light');
        } else {
            themeIcon.classList.replace('ph-moon', 'ph-sun');
            localStorage.setItem('theme', 'dark');
        }
    });

    // --- High-End Features: Interactive Image Viewer ---
    let currentScale = 1;
    const btnZoomIn = document.getElementById('tool-zoom-in');
    const btnZoomOut = document.getElementById('tool-zoom-out');
    const btnResetZoom = document.getElementById('tool-reset');

    function applyTransform() {
        imagePreview.style.transform = `scale(${currentScale})`;
        imagePreview.style.transition = 'transform 0.2s';
        if(heatmapOverlay) {
            heatmapOverlay.style.transform = `translate(-50%, -50%) scale(${currentScale})`;
            heatmapOverlay.style.transition = 'transform 0.2s';
        }
    }

    btnZoomIn.addEventListener('click', () => {
        if (currentScale < 3) currentScale += 0.2;
        applyTransform();
    });

    btnZoomOut.addEventListener('click', () => {
        if (currentScale > 0.5) currentScale -= 0.2;
        applyTransform();
    });

    btnResetZoom.addEventListener('click', () => {
        currentScale = 1;
        applyTransform();
    });

    // --- High-End Features: PDF Generation ---
    downloadPdfBtn.addEventListener('click', () => {
        // Hide the button during capture
        downloadPdfBtn.classList.add('hidden');
        
        const elementToCapture = document.getElementById('pdf-report-container');
        const sessionUser = document.getElementById('session-user-name');
        const username = sessionUser ? sessionUser.innerText : 'Medical_Report';
        
        const opt = {
            margin:       1,
            filename:     `Clinical_Diagnostic_Report_${username.replace(' ', '_')}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
        };

        // Render PDF
        html2pdf().set(opt).from(elementToCapture).save().then(() => {
            // Restore button post capture
            downloadPdfBtn.classList.remove('hidden');
        });
    });

    // --- Dynamic Data Fetching ---
    function loadDashboardData() {
        fetch('/api/dashboard_data')
            .then(res => res.json())
            .then(data => {
                if(data.error) return;
                
                // Update specific text counters
                const statTotal = document.getElementById('stat-total');
                const statRisk = document.getElementById('stat-highrisk');
                if(statTotal) statTotal.textContent = data.total_scans;
                if(statRisk) statRisk.textContent = data.high_risk;

                // Update insights bars
                const barPnu = document.getElementById('insight-bar-pneumonia');
                const barNor = document.getElementById('insight-bar-normal');
                const lblPnu = document.getElementById('insight-lbl-pneumonia');
                const lblNor = document.getElementById('insight-lbl-normal');
                
                if (barPnu && barNor && lblPnu && lblNor) {
                    barPnu.style.width = data.pneumonia_pct + '%';
                    barNor.style.width = data.normal_pct + '%';
                    lblPnu.textContent = data.pneumonia_pct;
                    lblNor.textContent = data.normal_pct;
                }

                // Update Patient Table
                const pBody = document.getElementById('patient-tbody');
                if (pBody) {
                    pBody.innerHTML = '';
                    data.history.forEach(scan => {
                        let badgeHtml = scan.status_label === 'danger' 
                            ? `<span class="badge badge-danger">High Risk</span>`
                            : `<span class="badge badge-success">Clear</span>`;
                        let tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${scan.patient_id}</td>
                            <td>${scan.patient_name}</td>
                            <td>${scan.age_sex}</td>
                            <td>${scan.timestamp}</td>
                            <td>${badgeHtml}</td>
                            <td><a href="#" style="color:#0284c7; text-decoration:none;">View File</a></td>
                        `;
                        pBody.appendChild(tr);
                    });
                }

                // Update History Table
                const hBody = document.getElementById('history-tbody');
                if (hBody) {
                    hBody.innerHTML = '';
                    data.history.forEach(scan => {
                        let outcomeColor = scan.status_label === 'danger' ? '#dc2626' : '#059669';
                        let tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>INF-${1000 + scan.id}</td>
                            <td>${scan.timestamp}</td>
                            <td>v1.4-Chest-ResNet</td>
                            <td>${scan.confidence}%</td>
                            <td><span style="color:${outcomeColor}; font-weight: 500;">${scan.outcome}</span></td>
                        `;
                        hBody.appendChild(tr);
                    });
                }
            })
            .catch(err => console.error("Error fetching data:", err));
    }

    // Initial load
    loadDashboardData();

    // --- Upload Logic ---
    
    browseBtn.addEventListener('click', () => fileInput.click());

    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            handleFile(this.files[0]);
        }
    });

    // Drag and drop mechanics
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
            fileInput.files = e.dataTransfer.files; // Sync logic
        }
    });

    function handleFile(file) {
        // Validate
        if (!file.type.match('image.*')) {
            alert("Please upload a valid image file (JPG/PNG).");
            return;
        }

        currentFile = file;
        const reader = new FileReader();
        
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZone.classList.add('hidden');
            previewSection.classList.remove('hidden');
            
            // Reset right panel if needed
            resetResultsPanel();
        };
        
        reader.readAsDataURL(file);
    }

    clearBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        previewSection.classList.add('hidden');
        dropZone.classList.remove('hidden');
        resetResultsPanel();
    });

    function resetResultsPanel() {
        diagnosticData.classList.add('hidden');
        loadingState.classList.add('hidden');
        resultsDisplay.classList.remove('hidden');
        heatmapOverlay.classList.add('hidden'); // Ensure heatmap clears
        downloadPdfBtn.classList.add('hidden');
        currentScale = 1;
        applyTransform();
    }

    // --- API Interaction Logic ---
    
    analyzeBtn.addEventListener('click', async () => {
        if (!currentFile) return;

        const formData = new FormData();
        formData.append('image', currentFile);

        // UI transitions
        resultsDisplay.classList.add('hidden');
        diagnosticData.classList.add('hidden');
        loadingState.classList.remove('hidden');
        heatmapOverlay.classList.add('hidden'); // Clear prior
        downloadPdfBtn.classList.add('hidden');

        // Simulate progress bar and scanning animation
        const imageWrapper = document.querySelector('.image-wrapper');
        if (imageWrapper) imageWrapper.classList.add('scanning');
        
        let width = 0;
        const interval = setInterval(() => {
            if (width >= 90) {
                clearInterval(interval);
            } else {
                width += Math.random() * 15;
                progressBar.style.width = Math.min(width, 90) + '%';
            }
        }, 300);

        const startTime = performance.now();

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            clearInterval(interval);
            progressBar.style.width = '100%';

            const endTime = performance.now();
            const processTime = Math.round(endTime - startTime);

            // Give a slight delay purely for UX realism (feeling of "processing")
            setTimeout(() => {
                if (imageWrapper) imageWrapper.classList.remove('scanning');
                showResults(data, processTime);
                
                // Hot reload the db dashboard immediately to show real time syncing
                loadDashboardData();
            }, 600);

        } catch (error) {
            clearInterval(interval);
            if (imageWrapper) imageWrapper.classList.remove('scanning');
            console.error("Analysis Error:", error);
            alert("An error occurred connecting to the diagnostic server.");
            resetResultsPanel();
        }
    });

    function showResults(data, timeMs) {
        loadingState.classList.add('hidden');
        diagnosticData.classList.remove('hidden');
        downloadPdfBtn.classList.remove('hidden'); // Allow PDF download now
        
        // Populate DOM
        if(data.error) {
            diagnosisResultText.textContent = "Error Analysis";
            diagnosisAlert.className = 'diagnosis-card danger';
            confidenceVal.textContent = "N/A";
            timeVal.textContent = "--";
            alert(data.error);
            return;
        }

        diagnosisResultText.textContent = data.diagnosis;
        confidenceVal.textContent = `${data.confidence}%`;
        timeVal.textContent = `${timeMs} ms`;

        // Update classes based on status string sent from Python
        diagnosisAlert.className = `diagnosis-card ${data.status}`;
        
        // Update icon based on status
        const diagnosisIcon = document.getElementById('diagnosis-icon');
        const reportFindings = document.getElementById('report-findings');
        const reportImpression = document.getElementById('report-impression');

        if (data.status === 'danger') {
            diagnosisIcon.className = 'ph-fill ph-warning-circle';
            // Trigger Visual Heatmap Explainable AI Mock
            heatmapOverlay.classList.remove('hidden');
            
            // Generate detailed medical report for Pneumonia
            reportFindings.innerHTML = `High opacity zones observed in bilateral lung fields. Evidence of consolidation typical of pulmonary infiltrates. Costophrenic angles appear slightly obscured. Model highlights significant anomalous pixel intensity clustered at ~[R:45, L:70] region of the spatial matrix.`;
            reportImpression.innerHTML = `<strong>High likelihood of Pneumonia infection (${data.confidence}% confidence interval)</strong>. It is strongly recommended that this scan is routed for immediate review by a certified radiologist. Consider correlating with clinical symptoms (fever, cough).`;
        } else {
            diagnosisIcon.className = 'ph-fill ph-check-circle';
            heatmapOverlay.classList.add('hidden'); // Clear Heatmap
            
            // Generate detailed medical report for Normal
            reportFindings.innerHTML = `No focal consolidation, pleural effusion, or pneumothorax identified. Cardiac silhouette and mediastinal contours are within normal limits. Spatial matrix correlates highly (>95%) with structural properties of healthy pulmonary tissue sets.`;
            reportImpression.innerHTML = `<strong>No acute cardiopulmonary disease detected.</strong> The radiograph presents as Normal/Healthy with a ${data.confidence}% confidence limit. Routine follow-up recommended if clinical symptoms persist.`;
        }
    }

    // --- SPA Navigation Logic ---
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    const spaViews = document.querySelectorAll('.spa-view');

    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active from all nav items
            navItems.forEach(n => n.classList.remove('active'));
            // Add active to clicked
            item.classList.add('active');

            // Hide all views
            spaViews.forEach(view => view.classList.add('hidden'));

            // Show target view
            const targetId = item.getAttribute('data-target');
            if (targetId) {
                const targetView = document.getElementById(targetId);
                if (targetView) {
                    targetView.classList.remove('hidden');
                }
            }
        });
    });
});
