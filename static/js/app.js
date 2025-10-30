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

        // Show temporary success message
        showTemporaryMessage('Form populated from JSON file', 'success');
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

    // Hide previous error messages
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

        // Hide form sections and show dashboard
        document.querySelector('.upload-section')?.classList.add('hidden');
        form.classList.add('hidden');
        hideError();

        // Show status panel and start polling
        statusPanel.classList.remove('hidden');
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
    const sessionIdFullEl = document.getElementById('session-id-full');
    const personNameEl = document.getElementById('person-name');
    const analysisStatusEl = document.getElementById('analysis-status');
    const fullNameInput = document.getElementById('full_name');

    if (sessionIdEl) sessionIdEl.textContent = currentJobId ? currentJobId.substring(0, 15) : 'N/A';
    if (sessionIdFullEl) sessionIdFullEl.textContent = currentJobId || 'N/A';
    if (personNameEl && fullNameInput) personNameEl.textContent = fullNameInput.value || 'N/A';
    if (analysisStatusEl) analysisStatusEl.textContent = 'RUNNING';

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

                    const analysisStatusCompletedEl = document.getElementById('analysis-status');
                    if (analysisStatusCompletedEl) {
                        analysisStatusCompletedEl.textContent = 'COMPLETED';
                        analysisStatusCompletedEl.style.color = 'var(--success-color)';
                    }

                    const downloadSectionEl = document.getElementById('download-section');
                    if (downloadSectionEl) downloadSectionEl.classList.remove('hidden');

                    showDownloadLink(status.download_url, status.filename);
                    stopStatusPolling();
                    resetButton();
                    break;
                case 'failed':
                    stopStatusPolling();
                    const currentStepFailedEl = document.getElementById('current-step');
                    if (currentStepFailedEl) {
                        currentStepFailedEl.textContent = 'Analysis failed';
                        currentStepFailedEl.style.color = '#ef4444';
                    }

                    const analysisStatusFailedEl = document.getElementById('analysis-status');
                    if (analysisStatusFailedEl) {
                        analysisStatusFailedEl.textContent = 'FAILED';
                        analysisStatusFailedEl.style.color = 'var(--error-color)';
                    }

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
 * Format agent output as human-readable text
 */
function formatAgentOutput(output, agentName) {
    if (!output || Object.keys(output).length === 0) {
        return '-';
    }

    // Custom formatting for different agent types
    const formatters = {
        'PersonInvestigation': (data) => {
            if (data.full_name && data.age && data.occupation && data.salary) {
                return `Validated: ${data.full_name}, Age ${data.age}, ${data.occupation}, Salary $${data.salary.toLocaleString()}`;
            }
            if (data.person_name && data.validated_age) {
                return `Validated: ${data.person_name}, Age ${data.validated_age}, ${data.occupation || 'N/A'}, Salary $${(data.annual_salary || 0).toLocaleString()}`;
            }
            return extractKeyInfo(data);
        },
        'Person Investigation': (data) => formatters['PersonInvestigation'](data),
        'FedRateAgent': (data) => {
            if (data.discount_rate !== undefined || data.rate !== undefined) {
                const rate = data.discount_rate || data.rate;
                const vintage = data.data_vintage ? ` (${data.data_vintage})` : '';
                const maturity = data.maturity ? `, ${data.maturity}` : '';
                return `Treasury Rate: ${rate}%${maturity}${vintage}`;
            }
            return extractKeyInfo(data);
        },
        'Federal Reserve': (data) => formatters['FedRateAgent'](data),
        'LifeExpectancyAgent': (data) => {
            if (data.life_expectancy !== undefined) {
                const age = data.age ? ` (${data.age}-year-old` : '';
                const gender = data.gender ? ` ${data.gender.toLowerCase()}` : '';
                const source = data.source ? `, ${data.source}` : '';
                return `Life Expectancy: ${data.life_expectancy} years${age}${gender}${source})`;
            }
            return extractKeyInfo(data);
        },
        'Life Expectancy': (data) => formatters['LifeExpectancyAgent'](data),
        'SkoogTableAgent': (data) => {
            if (data.worklife_expectancy !== undefined || data.median_years !== undefined) {
                const years = data.worklife_expectancy || data.median_years;
                const age = data.age ? ` for age ${data.age}` : '';
                const occupation = data.occupation ? `, ${data.occupation}` : '';
                return `Worklife Expectancy: ${years} years (median${age}${occupation})`;
            }
            return extractKeyInfo(data);
        },
        'Skoog Table': (data) => formatters['SkoogTableAgent'](data),
        'WorklifeExpectancyAgent': (data) => formatters['SkoogTableAgent'](data),
        'WageGrowthAgent': (data) => {
            if (data.growth_rate !== undefined || data.annual_growth_rate !== undefined) {
                const rate = data.growth_rate || data.annual_growth_rate;
                const location = data.location || data.county ? ` in ${data.location || data.county}` : '';
                const occupation = data.occupation ? ` for ${data.occupation}` : '';
                return `Annual Growth Rate: ${rate}% applied${occupation}${location}`;
            }
            return extractKeyInfo(data);
        },
        'Annual Growth': (data) => formatters['WageGrowthAgent'](data),
        'DiscountRateAgent': (data) => {
            if (data.discount_rate !== undefined || data.rate !== undefined) {
                const rate = data.discount_rate || data.rate;
                return `Discount Rate: ${rate}% applied for present value calculations`;
            }
            return extractKeyInfo(data);
        },
        'PresentValueAgent': (data) => {
            if (data.present_value !== undefined) {
                const years = data.years_projected || data.projection_years ? ` for ${data.years_projected || data.projection_years}-year projection` : '';
                const rate = data.discount_rate ? ` with ${data.discount_rate}% discount rate` : '';
                return `Present Value: Calculated${years}${rate}`;
            }
            return extractKeyInfo(data);
        },
        'Present Value': (data) => formatters['PresentValueAgent'](data),
        'ExcelReportAgent': (data) => {
            if (data.filename) {
                return `Excel Report:\n${data.filename}`;
            }
            return 'Excel Report Generated';
        },
        'Excel Report': (data) => formatters['ExcelReportAgent'](data),
        'SummaryReportAgent': (data) => {
            if (data.filename) {
                return `Summary Report:\n${data.filename}`;
            }
            return 'Summary Report Created';
        },
        'Summary Report': (data) => formatters['SummaryReportAgent'](data)
    };

    // Helper to extract key info from any data structure
    function extractKeyInfo(data) {
        // Try to find and display the most important fields
        const importantFields = ['name', 'full_name', 'rate', 'discount_rate', 'life_expectancy',
                                'worklife_expectancy', 'growth_rate', 'present_value', 'filename',
                                'age', 'occupation', 'salary', 'data_vintage'];

        const info = [];
        for (const field of importantFields) {
            if (data[field] !== undefined && data[field] !== null) {
                const value = typeof data[field] === 'number' ?
                    (data[field] % 1 === 0 ? data[field].toLocaleString() : data[field].toFixed(2)) :
                    data[field];
                info.push(`${field.replace(/_/g, ' ')}: ${value}`);
            }
        }

        if (info.length > 0) {
            return info.join(', ');
        }

        // Last resort: show first few keys
        const keys = Object.keys(data).slice(0, 3);
        return keys.map(k => `${k}: ${String(data[k]).substring(0, 20)}`).join(', ');
    }

    // Try to use custom formatter
    const formatter = formatters[agentName];
    if (formatter) {
        try {
            return formatter(output);
        } catch (e) {
            console.warn(`Formatter error for ${agentName}:`, e);
        }
    }

    // Fallback: Use extractKeyInfo
    return extractKeyInfo(output);
}

/**
 * Copy text to clipboard and show notification
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showCopyNotification();
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

/**
 * Show copy notification
 */
function showCopyNotification() {
    const notification = document.createElement('div');
    notification.className = 'copy-notification';
    notification.textContent = 'Copied to clipboard!';
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 2000);
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

    // Clean up old tooltips
    document.querySelectorAll('.agent-output-tooltip').forEach(tooltip => {
        if (!tooltip.matches(':hover')) {
            tooltip.remove();
        }
    });

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

        // Output (human-readable with click-to-copy and tooltip)
        const outputCell = document.createElement('td');
        outputCell.className = 'agent-output';

        if (agent.output && Object.keys(agent.output).length > 0) {
            const rawJSON = JSON.stringify(agent.output, null, 2);
            const humanReadable = formatAgentOutput(agent.output, agent.name);

            // Create text element
            const textSpan = document.createElement('span');
            textSpan.className = 'agent-output-text';
            textSpan.textContent = humanReadable;
            outputCell.appendChild(textSpan);

            // Create tooltip for raw JSON
            const tooltip = document.createElement('div');
            tooltip.className = 'agent-output-tooltip';
            tooltip.textContent = rawJSON;
            document.body.appendChild(tooltip); // Append to body for fixed positioning

            let hideTimeout;

            // Show tooltip on hover
            outputCell.addEventListener('mouseenter', (e) => {
                clearTimeout(hideTimeout);
                const rect = outputCell.getBoundingClientRect();

                // Position tooltip near the cell
                tooltip.style.left = `${rect.left + 10}px`;
                tooltip.style.top = `${rect.bottom + 5}px`;

                // Adjust if tooltip goes off screen
                setTimeout(() => {
                    const tooltipRect = tooltip.getBoundingClientRect();
                    if (tooltipRect.right > window.innerWidth) {
                        tooltip.style.left = `${window.innerWidth - tooltipRect.width - 10}px`;
                    }
                    if (tooltipRect.bottom > window.innerHeight) {
                        tooltip.style.top = `${rect.top - tooltipRect.height - 5}px`;
                    }
                }, 10);

                outputCell.classList.add('show-tooltip');
            });

            // Hide tooltip when mouse leaves both cell and tooltip
            outputCell.addEventListener('mouseleave', (e) => {
                hideTimeout = setTimeout(() => {
                    if (!tooltip.matches(':hover')) {
                        outputCell.classList.remove('show-tooltip');
                    }
                }, 100);
            });

            // Keep tooltip visible when hovering over it
            tooltip.addEventListener('mouseenter', () => {
                clearTimeout(hideTimeout);
                outputCell.classList.add('show-tooltip');
            });

            tooltip.addEventListener('mouseleave', () => {
                outputCell.classList.remove('show-tooltip');
            });

            // Add click-to-copy functionality on cell
            outputCell.classList.add('clickable');
            outputCell.addEventListener('click', (e) => {
                e.stopPropagation();
                copyToClipboard(rawJSON);
            });
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
 * Hide status panel
 */
function hideStatus() {
    statusPanel.classList.add('hidden');
    downloadLink.classList.add('hidden');
}

/**
 * Show temporary message (for JSON upload success, etc.)
 */
function showTemporaryMessage(message, type = 'info') {
    // Create temporary message element
    const msgDiv = document.createElement('div');
    msgDiv.className = `temp-message temp-message-${type}`;
    msgDiv.textContent = message;
    msgDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(msgDiv);

    // Remove after 3 seconds
    setTimeout(() => {
        msgDiv.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => msgDiv.remove(), 300);
    }, 3000);
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
