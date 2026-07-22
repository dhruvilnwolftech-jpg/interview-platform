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

// ============ DOCUMENT EDITOR FUNCTIONS ============

let currentDocumentId = null;
let currentDocumentRole = null;
let autoSaveInterval = null;
let syncInterval = null;
let isAutoSaving = false;
let isSyncing = false;
let lastSaveTime = null;
let lastSyncedContent = '';
let lastContentFromServer = '';
let lastSaveAttemptTime = 0;

function viewDocumentEditor(role) {
    if (role === 'support') {
        currentDocumentId = document.getElementById('doc-id').textContent;
    } else {
        currentDocumentId = document.getElementById('joined-doc-id').textContent;
    }
    currentDocumentRole = role;

    document.getElementById('document-modal').classList.remove('hidden');

    // Load document from backend
    loadDocument();

    // Start auto-save and real-time sync
    startAutoSave();
    startRealtimeSync();
}

function loadDocument() {
    if (!currentDocumentId) return;

    console.log('[LOAD] Document ID:', currentDocumentId);

    const url = `${API_BASE}/api/documents/${currentDocumentId}`;

    fetch(url)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            console.log('[LOAD] Received content length:', (data.content || '').length);
            const textarea = document.getElementById('document-text');
            textarea.value = data.content || '';
            lastSyncedContent = data.content || '';
            lastContentFromServer = data.content || '';
            textarea.focus();
            updateCharCount();
            showSaveStatus('✓ Loaded', '#28a745');
        })
        .catch(err => {
            console.error('[LOAD] Error:', err);
            showSaveStatus('✗ Failed', '#dc3545');
        });
}

function closeDocumentEditor() {
    document.getElementById('document-modal').classList.add('hidden');
    currentDocumentId = null;
    currentDocumentRole = null;

    // Stop intervals
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
        autoSaveInterval = null;
    }
    if (syncInterval) {
        clearInterval(syncInterval);
        syncInterval = null;
    }

    // Final save
    saveDocument();
}

function startAutoSave() {
    // Clear existing interval
    if (autoSaveInterval) {
        clearInterval(autoSaveInterval);
    }
    if (syncInterval) {
        clearInterval(syncInterval);
    }

    const textarea = document.getElementById('document-text');

    // Auto-save every 500ms (reduced frequency to prevent blinking)
    autoSaveInterval = setInterval(() => {
        autoSaveDocument();
    }, 500);

    // Sync every 800ms but ONLY if user is not typing (more conservative)
    let lastTypedTime = Date.now();
    textarea.addEventListener('input', () => {
        lastTypedTime = Date.now();
        updateCharCount();
    });

    syncInterval = setInterval(() => {
        // Only sync if user hasn't typed in last 300ms
        if (Date.now() - lastTypedTime > 300) {
            syncDocumentContent();
        }
    }, 800);

    // Save immediately on paste AND force sync after pause
    textarea.addEventListener('paste', () => {
        setTimeout(() => {
            console.log('[PASTE] Detected - saving immediately');
            autoSaveDocument();
            // Force sync after 150ms (after paste settles)
            setTimeout(() => {
                syncDocumentContent();
            }, 150);
        }, 20);
    });
}

function startRealtimeSync() {
    // Sync is now handled in startAutoSave() with smart typing detection
    // This function is kept for compatibility but syncing is more intelligent now
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
    const now = Date.now();

    // Only save if content actually changed
    if (content === lastSyncedContent) {
        return;
    }

    // Debounce: don't save too frequently
    if ((now - lastSaveAttemptTime) < 200) {
        return;
    }

    isAutoSaving = true;
    lastSyncedContent = content; // Update BEFORE sending to prevent overwrite
    lastSaveAttemptTime = now;

    const url = `${API_BASE}/api/documents/${currentDocumentId}/save`;
    const options = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: content })
    };

    console.log('[AUTO-SAVE] Saving', content.length, 'chars');

    fetch(url, options)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            console.log('[AUTO-SAVE] Success');
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

            // CRITICAL FIX: Only sync if no changes on this device
            // If server content is new AND local content is exactly what we last saved
            if (serverContent !== lastContentFromServer && localContent === lastSyncedContent) {
                console.log('[SYNC] Updating from server: ', lastContentFromServer.length, '→', serverContent.length);
                lastContentFromServer = serverContent;

                // Save cursor position
                const cursorPos = textarea.selectionStart;

                // Update content
                textarea.value = serverContent;

                // Restore cursor (but limit to new content length)
                const newCursorPos = Math.min(cursorPos, serverContent.length);
                textarea.selectionStart = newCursorPos;
                textarea.selectionEnd = newCursorPos;

                updateCharCount();
                showSaveStatus('✓ Synced', '#10b981');
            } else if (serverContent !== lastContentFromServer) {
                // Server changed but we're editing - just update our knowledge
                console.log('[SYNC] Server changed but user editing - NOT updating');
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
    console.log('[SAVE] Final save');

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
            console.log('[SAVE] Final save successful');
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
    const diff = now - lastSaveTime; // milliseconds

    let timeStr;
    if (diff < 1000) {
        timeStr = `${diff}ms ago`;
    } else if (diff < 60000) {
        timeStr = `${Math.floor(diff / 1000)}s ago`;
    } else if (diff < 3600000) {
        timeStr = `${Math.floor(diff / 60000)}m ago`;
    } else {
        timeStr = `${Math.floor(diff / 3600000)}h ago`;
    }

    const timeEl = document.getElementById('auto-save-time');
    if (timeEl) {
        timeEl.textContent = `Last saved: ${timeStr}`;
    }
}

// Refresh save time display every 100ms for millisecond precision
setInterval(updateSaveTime, 100);

// Close modal when clicking outside
document.addEventListener('click', (e) => {
    const modal = document.getElementById('document-modal');
    if (e.target === modal) {
        closeDocumentEditor();
    }
});
