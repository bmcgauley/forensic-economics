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
 * Start polling for job status (every 3 seconds)
 */
function startStatusPolling(statusUrl) {
    // Update session info (with null checks)
    const sessionIdEl = document.getElementById('session-id');
    const personNameEl = document.getElementById('person-name');
    const fullNameInput = document.getElementById('full_name');

    if (sessionIdEl) sessionIdEl.textContent = currentJobId ? currentJobId.substring(0, 8) : 'N/A';
    if (personNameEl && fullNameInput) personNameEl.textContent = fullNameInput.value || 'N/A';

    statusPollInterval = setInterval(async () => {
        try {
            const response = await fetch(statusUrl);

            if (!response.ok) {
                throw new Error('Failed to check status');
            }

            const status = await response.json();
            console.log('[Dashboard] Status update:', status);

            // Update current step (with null check)
            const currentStepEl = document.getElementById('current-step');
            if (status.current_step && currentStepEl) {
                currentStepEl.textContent = status.current_step;
            }

            // Update progress percentage (with null checks)
            if (status.progress_pct !== undefined) {
                updateProgress(status.progress_pct);
                const progressTextEl = document.getElementById('progress-text');
                if (progressTextEl) {
                    progressTextEl.textContent = status.progress_pct + '%';
                }
            }

            // Update agent progress table
            if (status.agent_progress && Array.isArray(status.agent_progress)) {
                console.log('[Dashboard] Updating agent table with', status.agent_progress.length, 'agents');
                updateAgentTable(status.agent_progress);

                // Update agent count (with null check)
                const agentCountEl = document.getElementById('agent-count');
                if (agentCountEl) {
                    const completed = status.agent_progress.filter(a => a.status === 'COMPLETED').length;
                    const total = status.agent_progress.length;
                    agentCountEl.textContent = `${completed}/${total} agents`;
                }
            }

            switch (status.status) {
                case 'queued':
                    if (currentStepEl) currentStepEl.textContent = 'Job queued, waiting to start...';
                    break;
                case 'running':
                    // Status is updated via current_step and agent_progress above
                    break;
                case 'completed':
                    updateProgress(100);
                    const progressTextEl = document.getElementById('progress-text');
                    if (progressTextEl) progressTextEl.textContent = '100%';
                    if (currentStepEl) currentStepEl.textContent = 'Analysis completed successfully';

                    const downloadSectionEl = document.getElementById('download-section');
                    if (downloadSectionEl) downloadSectionEl.classList.remove('hidden');

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
            console.error('[Dashboard] Polling error:', error);
            stopStatusPolling();
            showError('Failed to check job status');
            resetButton();
        }
    }, 3000); // Poll every 3 seconds
}

/**
 * Update agent table with real-time progress
 */
function updateAgentTable(agents) {
    const tbody = document.getElementById('agent-table-body');

    if (!tbody) {
        console.error('[Dashboard] agent-table-body element not found');
        return;
    }

    // Clear existing rows
    tbody.innerHTML = '';

    // Add row for each agent
    agents.forEach(agent => {
        const row = document.createElement('tr');
        row.className = `agent-row agent-${agent.status.toLowerCase()}`;

        // Agent name
        const nameCell = document.createElement('td');
        nameCell.className = 'agent-name';
        nameCell.textContent = agent.name;
        row.appendChild(nameCell);

        // Status badge
        const statusCell = document.createElement('td');
        statusCell.className = 'agent-status';
        const statusBadge = document.createElement('span');
        statusBadge.className = `status-badge status-${agent.status.toLowerCase()}`;
        statusBadge.textContent = agent.status;
        statusCell.appendChild(statusBadge);
        row.appendChild(statusCell);

        // Message
        const messageCell = document.createElement('td');
        messageCell.className = 'agent-message';
        messageCell.textContent = agent.message || '-';
        row.appendChild(messageCell);

        // Output (condensed)
        const outputCell = document.createElement('td');
        outputCell.className = 'agent-output';
        if (agent.output && Object.keys(agent.output).length > 0) {
            const outputText = JSON.stringify(agent.output, null, 2);
            if (outputText.length > 100) {
                outputCell.textContent = outputText.substring(0, 100) + '...';
                outputCell.title = outputText; // Full output on hover
            } else {
                outputCell.textContent = outputText;
            }
        } else {
            outputCell.textContent = '-';
        }
        row.appendChild(outputCell);

        tbody.appendChild(row);
    });
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
