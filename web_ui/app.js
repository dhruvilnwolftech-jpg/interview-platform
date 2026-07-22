// API Base URL
const API_BASE = (window.location.protocol === 'file:' ||
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1')
    ? 'http://localhost:5000'
    : 'https://interview-platform-bdot.onrender.com';

// Global State
let currentUser = null;

// Helper Functions
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} active`;
    setTimeout(() => toast.classList.remove('active'), 3000);
}

function switchAuthForm() {
    document.getElementById('login-form').classList.toggle('active');
    document.getElementById('register-form').classList.toggle('active');
    return false;
}

async function makeRequest(endpoint, method = 'GET', data = null) {
    try {
        const url = `${API_BASE}${endpoint}`;
        console.log(`[API] ${method} ${url}`);

        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (data) options.body = JSON.stringify(data);

        const response = await fetch(url, options);
        const result = await response.json();
        return { success: response.ok, status: response.status, data: result };
    } catch (error) {
        console.error('[API Error]', error);
        return { success: false, error: error.message };
    }
}

// Auth Functions
async function handleLogin() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    if (!email || !password) {
        showToast('Please fill all fields', 'error');
        return;
    }

    const result = await makeRequest('/api/auth/login', 'POST', { email, password });

    if (result.success) {
        currentUser = result.data;
        showToast(`Welcome, ${currentUser.full_name}!`, 'success');
        showApp();
    } else {
        showToast(result.data.error || 'Login failed', 'error');
    }
}

async function handleRegister() {
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const type = document.getElementById('register-type').value;

    if (!name || !email || !password) {
        showToast('Please fill all fields', 'error');
        return;
    }

    const result = await makeRequest('/api/auth/register', 'POST', {
        full_name: name,
        email,
        password,
        user_type: type
    });

    if (result.success) {
        showToast('Registration successful! Please login.', 'success');
        switchAuthForm();
        document.getElementById('register-name').value = '';
        document.getElementById('register-email').value = '';
        document.getElementById('register-password').value = '';
    } else {
        showToast(result.data.error || 'Registration failed', 'error');
    }
}

function logout() {
    currentUser = null;
    document.getElementById('auth-container').classList.add('active');
    document.getElementById('app-container').classList.add('hidden');
    document.getElementById('login-email').value = '';
    document.getElementById('login-password').value = '';
    showToast('Logged out', 'success');
}

function showApp() {
    document.getElementById('auth-container').classList.remove('active');
    document.getElementById('app-container').classList.remove('hidden');
    document.getElementById('user-info').textContent = `${currentUser.full_name} (${currentUser.user_type})`;

    if (currentUser.user_type === 'support') {
        document.getElementById('support-view').classList.add('active');
        document.getElementById('candidate-view').classList.remove('active');
    } else {
        document.getElementById('support-view').classList.remove('active');
        document.getElementById('candidate-view').classList.add('active');
    }
}

// Session Functions
async function createSession() {
    if (!currentUser || currentUser.user_type !== 'support') {
        showToast('Only support staff can create sessions', 'error');
        return;
    }

    const result = await makeRequest('/api/sessions', 'POST', {
        support_person_id: currentUser.user_id
    });

    if (result.success) {
        document.getElementById('session-code').textContent = result.data.code;
        document.getElementById('session-id').textContent = result.data.session_id;
        document.getElementById('doc-id').textContent = result.data.document_id;
        document.getElementById('session-created').classList.remove('hidden');
        showToast(`Session created! Code: ${result.data.code}`, 'success');
    } else {
        showToast(result.data.error || 'Failed to create session', 'error');
    }
}

function copyCode() {
    const code = document.getElementById('session-code').textContent;
    navigator.clipboard.writeText(code);
    showToast('Code copied!', 'success');
}

function resetSession() {
    document.getElementById('session-created').classList.add('hidden');
}

async function joinSession() {
    const code = document.getElementById('session-code-input').value.trim().toUpperCase();

    if (!code) {
        showToast('Please enter a code', 'error');
        return;
    }

    const result = await makeRequest(`/api/sessions/${code}`, 'GET');

    if (result.success) {
        document.getElementById('joined-code').textContent = result.data.code;
        document.getElementById('joined-doc-id').textContent = result.data.document_id;
        document.getElementById('support-id').textContent = result.data.support_person_id;
        document.getElementById('joined-session').classList.remove('hidden');
        showToast('Session joined!', 'success');
    } else {
        showToast(result.data.error || 'Failed to join session', 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Interview Platform Loaded');
    console.log('API Base:', API_BASE);
});

// ============ DOCUMENT EDITOR - ZERO BLINKING VERSION ============

let currentDocumentId = null;
let currentDocumentRole = null;
let autoSaveInterval = null;
let syncInterval = null;
let isAutoSaving = false;
let isSyncing = false;
let lastSaveTime = null;
let lastSyncedContent = '';
let lastContentFromServer = '';
let lastUserInteractionTime = 0;

function viewDocumentEditor(role) {
    if (role === 'support') {
        currentDocumentId = document.getElementById('doc-id').textContent;
    } else {
        currentDocumentId = document.getElementById('joined-doc-id').textContent;
    }
    currentDocumentRole = role;

    document.getElementById('document-modal').classList.remove('hidden');
    loadDocument();
    startSmartAutoSave();
}

function loadDocument() {
    if (!currentDocumentId) return;

    const url = `${API_BASE}/api/documents/${currentDocumentId}`;

    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            const textarea = document.getElementById('document-text');
            textarea.value = data.content || '';
            lastSyncedContent = data.content || '';
            lastContentFromServer = data.content || '';
            textarea.focus();
            updateCharCount();
            showSaveStatus('✓ Loaded', '#10b981');
        })
        .catch(err => {
            console.error('[LOAD] Error:', err);
            showSaveStatus('✗ Error', '#ef4444');
        });
}

function closeDocumentEditor() {
    document.getElementById('document-modal').classList.add('hidden');
    currentDocumentId = null;
    currentDocumentRole = null;

    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
        autoSaveInterval = null;
    }
    if (syncInterval) {
        clearInterval(syncInterval);
        syncInterval = null;
    }

    saveDocument();
}

function startSmartAutoSave() {
    if (autoSaveInterval) clearInterval(autoSaveInterval);
    if (syncInterval) clearInterval(syncInterval);

    const textarea = document.getElementById('document-text');
    lastUserInteractionTime = Date.now();

    // Track user interaction (typing, pasting, etc.)
    textarea.addEventListener('input', () => {
        lastUserInteractionTime = Date.now();
        updateCharCount();
    });

    textarea.addEventListener('keydown', () => {
        lastUserInteractionTime = Date.now();
    });

    textarea.addEventListener('paste', () => {
        lastUserInteractionTime = Date.now();
    });

    // Save every 800ms but ONLY if user hasn't interacted in 400ms
    autoSaveInterval = setInterval(() => {
        const idleTime = Date.now() - lastUserInteractionTime;
        if (idleTime > 400) {
            autoSaveDocument();
        }
    }, 800);

    // Sync every 1200ms but ONLY if user hasn't interacted in 600ms
    syncInterval = setInterval(() => {
        const idleTime = Date.now() - lastUserInteractionTime;
        if (idleTime > 600) {
            syncDocumentContent();
        }
    }, 1200);
}

function updateCharCount() {
    const textarea = document.getElementById('document-text');
    const charCount = textarea.value.length;
    document.getElementById('char-count').textContent = `${charCount} character${charCount !== 1 ? 's' : ''}`;
}

function showSaveStatus(message, color = '#6c757d') {
    const statusEl = document.getElementById('save-status');
    const indicator = document.querySelector('.status-indicator');
    if (statusEl && indicator) {
        statusEl.textContent = message;
        statusEl.style.color = color;
        indicator.style.background = color;
    }
}

function autoSaveDocument() {
    if (!currentDocumentId || isAutoSaving) return;

    const textarea = document.getElementById('document-text');
    const content = textarea.value;

    if (content === lastSyncedContent) {
        return;
    }

    isAutoSaving = true;
    lastSyncedContent = content;

    const url = `${API_BASE}/api/documents/${currentDocumentId}/save`;
    const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    };

    fetch(url, options)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            lastSaveTime = new Date();
            showSaveStatus('✓ Saved', '#10b981');
            updateSaveTime();
        })
        .catch(err => {
            console.error('[AUTO-SAVE] Error:', err);
            showSaveStatus('⚠ Error', '#ef4444');
        })
        .finally(() => {
            isAutoSaving = false;
        });
}

function syncDocumentContent() {
    if (!currentDocumentId || isSyncing) return;

    // NEVER sync while user is typing - this prevents all blinking
    const idleTime = Date.now() - lastUserInteractionTime;
    if (idleTime < 600) {
        return;
    }

    isSyncing = true;
    const url = `${API_BASE}/api/documents/${currentDocumentId}`;

    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            const serverContent = data.content || '';
            const textarea = document.getElementById('document-text');
            const localContent = textarea.value;

            // CRITICAL: Only update if BOTH are true:
            // 1. Server has new content
            // 2. Local content matches what we last saved (user is idle)
            if (serverContent !== lastContentFromServer && localContent === lastSyncedContent) {
                lastContentFromServer = serverContent;

                const cursorPos = textarea.selectionStart;
                textarea.value = serverContent;

                const newCursorPos = Math.min(cursorPos, serverContent.length);
                textarea.selectionStart = newCursorPos;
                textarea.selectionEnd = newCursorPos;

                updateCharCount();
                showSaveStatus('✓ Synced', '#10b981');
            } else if (serverContent !== lastContentFromServer) {
                lastContentFromServer = serverContent;
            }
        })
        .catch(err => {
            console.error('[SYNC] Error:', err);
        })
        .finally(() => {
            isSyncing = false;
        });
}

function saveDocument() {
    if (!currentDocumentId) return;

    const content = document.getElementById('document-text').value;
    const url = `${API_BASE}/api/documents/${currentDocumentId}/save`;
    const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    };

    fetch(url, options)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            lastSaveTime = new Date();
            updateSaveTime();
        })
        .catch(err => {
            console.error('[SAVE] Error:', err);
        });
}

function updateSaveTime() {
    if (!lastSaveTime) return;

    const now = new Date();
    const diff = now - lastSaveTime;

    let timeStr;
    if (diff < 1000) {
        timeStr = `${diff}ms ago`;
    } else if (diff < 60000) {
        timeStr = `${Math.floor(diff / 1000)}s ago`;
    } else {
        timeStr = `${Math.floor(diff / 60000)}m ago`;
    }

    const timeEl = document.getElementById('auto-save-time');
    if (timeEl) {
        timeEl.textContent = `Last saved: ${timeStr}`;
    }
}

setInterval(updateSaveTime, 100);

document.addEventListener('click', (e) => {
    const modal = document.getElementById('document-modal');
    if (e.target === modal) {
        closeDocumentEditor();
    }
});
