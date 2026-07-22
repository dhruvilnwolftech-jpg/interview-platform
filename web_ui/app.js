// API Base URL - use localhost for local testing, production URL for deployed
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : 'https://interview-platform-bdot.onrender.com';

// Global State
let currentRole = 'user';
let currentSession = {
    user: null,
    support: null,
    admin: null
};

// Helper Functions
function showLoading(show = true) {
    const spinner = document.getElementById('loadingSpinner');
    if (show) {
        spinner.classList.add('active');
    } else {
        spinner.classList.remove('active');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} active`;
    setTimeout(() => {
        toast.classList.remove('active');
    }, 3000);
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const text = element.textContent;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    });
}

function switchRole(role) {
    currentRole = role;

    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    document.getElementById(`${role}-view`).classList.add('active');
}

async function makeRequest(endpoint, method = 'GET', data = null) {
    try {
        const url = `${API_BASE}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, 'error');
        return null;
    }
}

// Candidate Functions
async function joinSession() {
    const code = document.getElementById('sessionCode').value.trim().toUpperCase();

    if (!code) {
        showToast('Please enter a session code', 'error');
        return;
    }

    showLoading(true);
    const result = await makeRequest(`/api/sessions/${code}`);
    showLoading(false);

    if (result) {
        currentSession.user = result;

        // Show session info
        document.getElementById('userSessionInfo').classList.remove('hidden');
        document.getElementById('userSessionId').textContent = result.session_id;
        document.getElementById('userDocId').textContent = result.document_id;
        document.getElementById('userSupportId').textContent = result.support_person_id;

        showToast('Successfully joined session!', 'success');
    }
}

async function viewDocument(role) {
    let docId;

    if (role === 'user') {
        docId = currentSession.user?.document_id;
    } else {
        docId = currentSession.support?.document_id;
    }

    if (!docId) {
        showToast('No document to view', 'error');
        return;
    }

    showLoading(true);
    const result = await makeRequest(`/api/admin/documents/${docId}`);
    showLoading(false);

    if (result) {
        // Show modal
        const modal = document.getElementById('documentModal');
        modal.classList.add('active');

        // Populate document info
        document.getElementById('docContent').textContent = result.content || '(Empty document)';
        document.getElementById('docCreated').textContent = new Date(result.created_at).toLocaleString();
        document.getElementById('docUpdated').textContent = new Date(result.updated_at).toLocaleString();
        document.getElementById('docChanges').textContent = result.change_history?.length || 0;
    }
}

// Support Person Functions
async function createSession() {
    const supportId = document.getElementById('supportPersonId').value.trim();

    if (!supportId) {
        showToast('Please enter support person ID', 'error');
        return;
    }

    showLoading(true);
    const result = await makeRequest('/api/sessions', 'POST', {
        support_person_id: supportId
    });
    showLoading(false);

    if (result) {
        currentSession.support = result;

        // Show session info
        document.getElementById('supportSessionInfo').classList.remove('hidden');
        document.getElementById('supportCode').textContent = result.code;
        document.getElementById('supportSessionId').textContent = result.session_id;
        document.getElementById('supportDocId').textContent = result.document_id;

        showToast(`Session created! Code: ${result.code}`, 'success');
    }
}

function resetSupport() {
    document.getElementById('supportSessionInfo').classList.add('hidden');
    document.getElementById('supportPersonId').value = '';
}

// Admin Functions
async function loadAllSessions() {
    showLoading(true);
    const result = await makeRequest('/api/admin/sessions');
    showLoading(false);

    if (result) {
        currentSession.admin = result.sessions;
        renderSessions(result.sessions);
        updateStats(result.sessions);
    }
}

function renderSessions(sessions) {
    const listContainer = document.getElementById('sessionsList');

    if (!sessions || sessions.length === 0) {
        listContainer.innerHTML = '<p class="text-muted">No sessions found</p>';
        return;
    }

    listContainer.innerHTML = sessions.map(session => `
        <div class="session-item" onclick="viewSessionDetails('${session.id}')">
            <h3>Session Code: <strong>${session.code}</strong></h3>
            <div class="row">
                <span class="label">Support Person:</span>
                <span class="value">${session.support_person_id}</span>
            </div>
            <div class="row">
                <span class="label">Created:</span>
                <span class="value">${new Date(session.created_at).toLocaleString()}</span>
            </div>
            <div class="row">
                <span class="label">Status:</span>
                <span class="value">${session.is_active ? '✅ Active' : '⏹️ Inactive'}</span>
            </div>
            <div class="row">
                <span class="label">Documents:</span>
                <span class="value">${session.document_count}</span>
            </div>
            <div class="row">
                <span class="label">Active Connections:</span>
                <span class="value">${session.connection_count}</span>
            </div>
        </div>
    `).join('');
}

function updateStats(sessions) {
    const totalSessions = sessions.length;
    const activeSessions = sessions.filter(s => s.is_active).length;
    const totalDocuments = sessions.reduce((sum, s) => sum + s.document_count, 0);

    const statCards = document.querySelectorAll('.stat-value');
    statCards[0].textContent = totalSessions;
    statCards[1].textContent = activeSessions;
    statCards[2].textContent = totalDocuments;
}

async function viewSessionDetails(sessionId) {
    const session = currentSession.admin.find(s => s.id === sessionId);

    if (!session || session.document_count === 0) {
        showToast('No documents in this session', 'error');
        return;
    }

    // For now, we'll fetch and display the first document
    // In production, you'd want a more sophisticated UI
    showLoading(true);

    // We'd need the document ID which isn't in the sessions list
    // For this demo, we'll just show the session info
    showLoading(false);
    showToast(`Session: ${session.code} - ${session.document_count} document(s)`, 'success');
}

// Modal Functions
function closeModal() {
    const modal = document.getElementById('documentModal');
    modal.classList.remove('active');
}

// Close modal on outside click
window.addEventListener('click', (event) => {
    const modal = document.getElementById('documentModal');
    if (event.target === modal) {
        closeModal();
    }
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Interview Platform Web UI Loaded');
    console.log(`API Base: ${API_BASE}`);

    // Test API connection
    makeRequest('/api/health').then(result => {
        if (result) {
            console.log('✅ Backend connection successful');
            showToast('Connected to backend!', 'success');
        }
    });
});

// Keyboard shortcuts
document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
        closeModal();
    }
});

// Enter key for forms
document.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        if (currentRole === 'user' && event.target.id === 'sessionCode') {
            joinSession();
        } else if (currentRole === 'support' && event.target.id === 'supportPersonId') {
            createSession();
        }
    }
});
