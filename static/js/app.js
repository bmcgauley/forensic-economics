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
const jsonUploadZone = document.getElementById('json-upload-zone');
const jsonFileInput = document.getElementById('json-file-input');

// State
let currentJobId = null;
let statusPollInterval = null;

/**
 * Initialize the application
 */
document.addEventListener('DOMContentLoaded', async () => {
    // Set default present_date to 10/20/2025
    const presentDateInput = document.getElementById('present_date');
    if (presentDateInput) {
        presentDateInput.value = '2025-10-20';
    }

    // Load dropdown data
    await loadCaliforniaCounties();
    await loadSOCOccupations();

    // Setup JSON upload handlers
    setupJSONUpload();
});

/**
 * Load California counties from JSON
 */
async function loadCaliforniaCounties() {
    try {
        const response = await fetch('/data/california_counties.json');
        const data = await response.json();
        const select = document.getElementById('california_county');

        data.counties.forEach(county => {
            const option = document.createElement('option');
            option.value = county;
            option.textContent = county;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load California counties:', error);
    }
}

/**
 * Load SOC occupations from JSON
 */
async function loadSOCOccupations() {
    try {
        const response = await fetch('/data/soc_occupations.json');
        const data = await response.json();
        const select = document.getElementById('occupation');

        data.occupations.forEach(occ => {
            const option = document.createElement('option');
            option.value = occ.code;
            option.textContent = `${occ.code} - ${occ.title}`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Failed to load SOC occupations:', error);
    }
}

/**
 * Setup JSON file upload handlers
 */
function setupJSONUpload() {
    // Click to browse
    jsonUploadZone.addEventListener('click', () => {
        jsonFileInput.click();
    });

    // File input change
    jsonFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleJSONFile(e.target.files[0]);
        }
    });

    // Drag and drop
    jsonUploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        jsonUploadZone.classList.add('drag-over');
    });

    jsonUploadZone.addEventListener('dragleave', () => {
        jsonUploadZone.classList.remove('drag-over');
    });

    jsonUploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        jsonUploadZone.classList.remove('drag-over');

        if (e.dataTransfer.files.length > 0) {
            handleJSONFile(e.dataTransfer.files[0]);
        }
    });
}

/**
 * Handle JSON file upload
 */
async function handleJSONFile(file) {
    if (!file.name.endsWith('.json')) {
        showError('Please upload a JSON file');
        return;
    }

    try {
        const text = await file.text();
        const data = JSON.parse(text);
        populateFormFromJSON(data);
        showStatus('Form populated from JSON file');
        setTimeout(hideStatus, 3000);
    } catch (error) {
        showError('Invalid JSON file: ' + error.message);
    }
}

/**
 * Populate form from JSON data
 */
function populateFormFromJSON(data) {
    // Populate all fields that exist in the JSON
    if (data.full_name) document.getElementById('full_name').value = data.full_name;
    if (data.date_of_birth) document.getElementById('date_of_birth').value = data.date_of_birth;
    if (data.date_of_death) document.getElementById('date_of_death').value = data.date_of_death;
    if (data.present_date) document.getElementById('present_date').value = data.present_date;
    if (data.gender) document.getElementById('gender').value = data.gender;
    if (data.level_of_schooling) document.getElementById('level_of_schooling').value = data.level_of_schooling;
    if (data.occupation) document.getElementById('occupation').value = data.occupation;
    if (data.employment_status) document.getElementById('employment_status').value = data.employment_status;
    if (data.annual_salary) document.getElementById('annual_salary').value = data.annual_salary;
    if (data.california_county) document.getElementById('california_county').value = data.california_county;
}

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
            full_name: formData.get('full_name'),
            date_of_birth: formData.get('date_of_birth'),
            date_of_death: formData.get('date_of_death') || null,
            present_date: formData.get('present_date'),
            gender: formData.get('gender'),
            level_of_schooling: formData.get('level_of_schooling'),
            occupation: formData.get('occupation'),
            employment_status: formData.get('employment_status'),
            annual_salary: parseFloat(formData.get('annual_salary')),
            california_county: formData.get('california_county'),
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
