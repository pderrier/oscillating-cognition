/**
 * Oscillating Cognition - Memory Explorer
 */

const API = {
    status: '/api/status',
    insights: '/api/insights',
    knots: '/api/knots',
    raw: '/api/memory/raw',
    clear: '/api/memory',
    oscillate: '/api/oscillate',
    oscillationStatus: '/api/oscillation/status'
};

// State
let state = {
    insights: [],
    knots: [],
    status: null
};

// DOM elements
const elements = {
    crystallizedCount: document.getElementById('crystallized-count'),
    knotsCount: document.getElementById('knots-count'),
    lastModified: document.getElementById('last-modified'),
    insightsList: document.getElementById('insights-list'),
    knotsList: document.getElementById('knots-list'),
    insightsBadge: document.getElementById('insights-badge'),
    knotsBadge: document.getElementById('knots-badge'),
    rawJson: document.getElementById('raw-json'),
    refreshBtn: document.getElementById('refresh-btn')
};

// Fetch helpers
async function fetchJson(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Fetch error for ${url}:`, error);
        throw error;
    }
}

// Format relative time
function formatRelativeTime(isoString) {
    if (!isoString) return 'Never';

    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
}

// Render functions
function renderItem(item, type) {
    const div = document.createElement('div');
    div.className = 'item';
    div.innerHTML = `
        <div class="item-content">${escapeHtml(item.content)}</div>
        <div class="item-meta">Cycle ${item.cycle_added} · #${item.index}</div>
    `;
    return div;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderList(container, items, type) {
    container.innerHTML = '';

    if (items.length === 0) {
        container.innerHTML = `<p class="empty-state">No ${type} yet. Run an oscillation cycle to generate some.</p>`;
        return;
    }

    // Render in reverse order (newest first)
    const reversed = [...items].reverse();
    reversed.forEach(item => {
        container.appendChild(renderItem(item, type));
    });
}

// Load data
async function loadStatus() {
    try {
        state.status = await fetchJson(API.status);

        elements.crystallizedCount.textContent = state.status.crystallized_count;
        elements.knotsCount.textContent = state.status.open_knots_count;
        elements.lastModified.textContent = formatRelativeTime(state.status.last_modified);

        elements.insightsBadge.textContent = state.status.crystallized_count;
        elements.knotsBadge.textContent = state.status.open_knots_count;
    } catch (error) {
        elements.crystallizedCount.textContent = '?';
        elements.knotsCount.textContent = '?';
        elements.lastModified.textContent = 'Error';
    }
}

async function loadInsights() {
    try {
        state.insights = await fetchJson(API.insights);
        renderList(elements.insightsList, state.insights, 'insights');
    } catch (error) {
        elements.insightsList.innerHTML = '<p class="empty-state">Error loading insights</p>';
    }
}

async function loadKnots() {
    try {
        state.knots = await fetchJson(API.knots);
        renderList(elements.knotsList, state.knots, 'knots');
    } catch (error) {
        elements.knotsList.innerHTML = '<p class="empty-state">Error loading knots</p>';
    }
}

async function loadRaw() {
    try {
        const raw = await fetchJson(API.raw);
        elements.rawJson.textContent = JSON.stringify(raw, null, 2);
    } catch (error) {
        elements.rawJson.textContent = 'Error loading raw data';
    }
}

async function loadAll() {
    elements.refreshBtn.textContent = '⟳';
    elements.refreshBtn.disabled = true;

    await Promise.all([
        loadStatus(),
        loadInsights(),
        loadKnots(),
        loadRaw()
    ]);

    elements.refreshBtn.textContent = '↻';
    elements.refreshBtn.disabled = false;
}

// Toggle raw panel
function toggleRaw() {
    const panel = document.getElementById('raw-panel');
    panel.classList.toggle('collapsed');
    panel.classList.toggle('expanded');
}

// Clear memory
async function confirmClear() {
    const confirmed = confirm(
        'Are you sure you want to clear all memory?\n\n' +
        'This will delete:\n' +
        `- ${state.status?.crystallized_count || 0} crystallized insights\n` +
        `- ${state.status?.open_knots_count || 0} open knots\n\n` +
        'This cannot be undone.'
    );

    if (!confirmed) return;

    try {
        const response = await fetch(API.clear, { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to clear');

        await loadAll();
        alert('Memory cleared.');
    } catch (error) {
        alert('Error clearing memory: ' + error.message);
    }
}

// Oscillation form handling
const oscillateForm = document.getElementById('oscillate-form');
const oscillateBtn = document.getElementById('oscillate-btn');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultContainer = document.getElementById('result-container');
const resultSummary = document.getElementById('result-summary');

let pollInterval = null;

async function runOscillation(seed, cycles, ground) {
    // Reset UI
    resultContainer.style.display = 'none';
    resultContainer.classList.remove('error');
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Starting oscillation...';

    oscillateBtn.disabled = true;
    oscillateBtn.querySelector('.btn-text').textContent = 'Running...';
    oscillateBtn.querySelector('.btn-spinner').style.display = 'inline';

    // Start polling for progress
    pollInterval = setInterval(async () => {
        try {
            const status = await fetchJson(API.oscillationStatus);
            if (status.running) {
                const progress = (status.current_cycle / status.total_cycles) * 100;
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `Cycle ${status.current_cycle} of ${status.total_cycles}: Exploring "${status.seed}"`;
            }
        } catch (e) {
            // Ignore polling errors
        }
    }, 500);

    try {
        const response = await fetch(API.oscillate, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ seed, cycles, ground })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        const result = await response.json();

        // Update progress to complete
        progressFill.style.width = '100%';
        progressText.textContent = 'Complete!';

        // Show result
        setTimeout(() => {
            progressContainer.style.display = 'none';
            resultContainer.style.display = 'block';

            let summary = `${result.cycles_completed} cycles completed. `;
            summary += `${result.insights.length} new insights, `;
            summary += `${result.open_questions.length} new open questions.`;

            if (result.grounding) {
                if (result.grounding.error) {
                    summary += ` Grounding failed: ${result.grounding.error}`;
                } else {
                    summary += ' Grounding complete.';
                }
            }

            resultSummary.textContent = summary;
        }, 500);

        // Refresh the data displays
        await loadAll();

    } catch (error) {
        progressContainer.style.display = 'none';
        resultContainer.style.display = 'block';
        resultContainer.classList.add('error');
        resultSummary.textContent = `Error: ${error.message}`;
    } finally {
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
        oscillateBtn.disabled = false;
        oscillateBtn.querySelector('.btn-text').textContent = 'Oscillate';
        oscillateBtn.querySelector('.btn-spinner').style.display = 'none';
    }
}

oscillateForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const seed = document.getElementById('seed-input').value.trim();
    const cycles = parseInt(document.getElementById('cycles-input').value, 10) || 3;
    const ground = document.getElementById('ground-checkbox').checked;

    if (!seed) {
        alert('Please enter a seed topic');
        return;
    }

    await runOscillation(seed, cycles, ground);
});

// Event listeners
elements.refreshBtn.addEventListener('click', loadAll);

// Auto-refresh every 30 seconds
setInterval(loadAll, 30000);

// Initial load
loadAll();

// Make functions available globally for onclick handlers
window.toggleRaw = toggleRaw;
window.confirmClear = confirmClear;
