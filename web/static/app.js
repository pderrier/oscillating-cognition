/**
 * Oscillating Cognition - Memory Explorer
 */

const API = {
    status: '/api/status',
    insights: '/api/insights',
    knots: '/api/knots',
    raw: '/api/memory/raw',
    clear: '/api/memory'
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

// Event listeners
elements.refreshBtn.addEventListener('click', loadAll);

// Auto-refresh every 30 seconds
setInterval(loadAll, 30000);

// Initial load
loadAll();

// Make functions available globally for onclick handlers
window.toggleRaw = toggleRaw;
window.confirmClear = confirmClear;
