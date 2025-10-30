/**
 * Forensic Economics - Dashboard JavaScript
 * Handles form submission, job status polling, and download
 */

const API_BASE = '/api';

// DOM elements
const form = document.getElementById('intake-form');
const generateBtn = document.getElementById('generate-btn');
const statusPanel = document.getElementById('status-panel');
const errorPanel = document.getElementById('error-panel');
const statusMessage = document.getElementById('status-message');
const errorMessage = document.getElementById('error-message');
const progressFill = document.getElementById('progress-fill');
const downloadLink = document.getElementById('download-link');

// State
let currentJobId = null;
let statusPollInterval = null;

/**
 * Handle form submission
 */
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Hide previous status/error messages
    hideStatus();
    hideError();

    // Disable submit button
    generateBtn.disabled = true;
    generateBtn.textContent = 'Generating...';

    try {
        // Collect form data
        const formData = new FormData(form);
        const intake = {
            id: crypto.randomUUID(),
            victim_age: parseInt(formData.get('victim_age')),
            victim_sex: formData.get('victim_sex'),
            occupation: formData.get('occupation'),
            education: formData.get('education'),
            salary: parseFloat(formData.get('salary')),
            salary_type: formData.get('salary_type'),
            location: formData.get('location'),
            dependents: parseInt(formData.get('dependents')) || 0,
            benefits: {
                retirement_contribution: parseFloat(formData.get('retirement_contribution')) || 0,
                health_benefits: parseFloat(formData.get('health_benefits')) || 0
            },
            metadata: {
                submission_timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent
            }
        };

        // Submit to API
        const response = await fetch(`${API_BASE}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(intake)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to generate report');
        }

        const result = await response.json();
        currentJobId = result.job_id;

        // Show status and start polling
        showStatus('Report generation started...');
        updateProgress(10);
        startStatusPolling(result.status_url);

    } catch (error) {
        showError(error.message);
        resetButton();
    }
});

/**
 * Start polling for job status
 */
function startStatusPolling(statusUrl) {
    statusPollInterval = setInterval(async () => {
        try {
            const response = await fetch(statusUrl);

            if (!response.ok) {
                throw new Error('Failed to check status');
            }

            const status = await response.json();

            switch (status.status) {
                case 'queued':
                    updateProgress(20);
                    statusMessage.textContent = 'Job queued, waiting to start...';
                    break;
                case 'running':
                    updateProgress(50);
                    statusMessage.textContent = status.message || 'Running calculations...';
                    break;
                case 'completed':
                    updateProgress(100);
                    statusMessage.textContent = 'Report generated successfully!';
                    showDownloadLink(status.download_url, status.filename);
                    stopStatusPolling();
                    resetButton();
                    break;
                case 'failed':
                    stopStatusPolling();
                    hideStatus();
                    showError(status.error || 'Report generation failed');
                    resetButton();
                    break;
            }
        } catch (error) {
            stopStatusPolling();
            showError('Failed to check job status');
            resetButton();
        }
    }, 2000); // Poll every 2 seconds
}

/**
 * Stop status polling
 */
function stopStatusPolling() {
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
}

/**
 * Show status panel
 */
function showStatus(message) {
    statusMessage.textContent = message;
    statusPanel.classList.remove('hidden');
}

/**
 * Hide status panel
 */
function hideStatus() {
    statusPanel.classList.add('hidden');
    downloadLink.classList.add('hidden');
}

/**
 * Show error panel
 */
function showError(message) {
    errorMessage.textContent = message;
    errorPanel.classList.remove('hidden');
}

/**
 * Hide error panel
 */
function hideError() {
    errorPanel.classList.add('hidden');
}

/**
 * Update progress bar
 */
function updateProgress(percent) {
    progressFill.style.width = `${percent}%`;
}

/**
 * Show download link
 */
function showDownloadLink(url, filename) {
    downloadLink.innerHTML = `
        <a href="${url}" download="${filename}">
            Download Report (${filename})
        </a>
    `;
    downloadLink.classList.remove('hidden');
}

/**
 * Reset submit button
 */
function resetButton() {
    generateBtn.disabled = false;
    generateBtn.textContent = 'Generate Report';
}

/**
 * Clean up on page unload
 */
window.addEventListener('beforeunload', () => {
    stopStatusPolling();
});
