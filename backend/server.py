#!/usr/bin/env python3
"""
Interview Platform Backend - Minimal Version
Handles authentication and session management
"""

from flask import Flask, request, jsonify
import uuid
import json
import os
import sys

# Create Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Enable CORS with @after_request
@app.after_request
def add_cors(response):
    """Add CORS headers to all responses"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Accept,Authorization'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response

# In-memory database
DB = {
    'users': {},
    'sessions': {},
    'documents': {}
}

# ============ AUTH ENDPOINTS ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    print(f"[REGISTER] Received POST request")
    try:
        payload = request.get_json()
        print(f"[REGISTER] Payload: {payload}")
        
        if not payload:
            return jsonify({'error': 'No data'}), 400
        
        email = payload.get('email', '').strip()
        password = payload.get('password', '')
        full_name = payload.get('full_name', '').strip()
        user_type = payload.get('user_type', 'candidate')
        
        if not email or not password or not full_name:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if email in DB['users']:
            return jsonify({'error': 'Email already registered'}), 409
        
        user_id = str(uuid.uuid4())
        DB['users'][email] = {
            'id': user_id,
            'email': email,
            'password': password,
            'full_name': full_name,
            'user_type': user_type
        }
        
        print(f"[REGISTER] User registered: {email}")
        return jsonify({
            'success': True,
            'user_id': user_id,
            'message': 'Registration successful'
        }), 201
        
    except Exception as e:
        print(f"[REGISTER] ERROR: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    print(f"[LOGIN] Received POST request")
    try:
        payload = request.get_json()
        print(f"[LOGIN] Payload: {payload}")
        
        if not payload:
            return jsonify({'error': 'No data'}), 400
        
        email = payload.get('email', '').strip()
        password = payload.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Missing credentials'}), 400
        
        if email not in DB['users']:
            return jsonify({'error': 'User not found'}), 401
        
        user = DB['users'][email]
        if user['password'] != password:
            return jsonify({'error': 'Invalid password'}), 401
        
        print(f"[LOGIN] User logged in: {email}")
        return jsonify({
            'success': True,
            'user_id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'user_type': user['user_type'],
            'message': 'Login successful'
        }), 200
        
    except Exception as e:
        print(f"[LOGIN] ERROR: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ============ SESSION ENDPOINTS ============

@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create interview session"""
    print(f"[SESSION] Received POST request")
    try:
        payload = request.get_json() or {}
        print(f"[SESSION] Payload: {payload}")
        
        support_person_id = payload.get('support_person_id')
        
        if not support_person_id:
            return jsonify({'error': 'support_person_id required'}), 400
        
        code = str(uuid.uuid4())[:6].upper()
        session_id = str(uuid.uuid4())
        doc_id = str(uuid.uuid4())
        
        DB['sessions'][code] = {
            'id': session_id,
            'code': code,
            'support_person_id': support_person_id,
            'document_id': doc_id,
            'created_at': '2026-07-22T00:00:00',
            'is_active': True
        }
        
        print(f"[SESSION] Session created: {code}")
        return jsonify({
            'session_id': session_id,
            'code': code,
            'document_id': doc_id,
            'created_at': '2026-07-22T00:00:00'
        }), 201
        
    except Exception as e:
        print(f"[SESSION] ERROR: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/sessions/<code>', methods=['GET'])
def get_session(code):
    """Get session by code"""
    print(f"[GET_SESSION] Code: {code}")
    try:
        code_upper = code.upper()
        
        if code_upper not in DB['sessions']:
            return jsonify({'error': 'Session not found'}), 404
        
        session = DB['sessions'][code_upper]
        print(f"[GET_SESSION] Found session")
        return jsonify({
            'session_id': session['id'],
            'code': session['code'],
            'document_id': session['document_id'],
            'support_person_id': session['support_person_id'],
            'created_at': session['created_at']
        }), 200
        
    except Exception as e:
        print(f"[GET_SESSION] ERROR: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/admin/sessions', methods=['GET'])
def get_all_sessions():
    """Get all sessions"""
    print(f"[ADMIN_SESSIONS] Request")
    try:
        sessions_list = list(DB['sessions'].values())
        print(f"[ADMIN_SESSIONS] Found {len(sessions_list)} sessions")
        return jsonify({'sessions': sessions_list}), 200
        
    except Exception as e:
        print(f"[ADMIN_SESSIONS] ERROR: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ============ DOCUMENT ENDPOINTS ============

@app.route('/api/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get document content"""
    print(f"[GET_DOC] ID: {doc_id}")
    try:
        if doc_id not in DB['documents']:
            # Return empty document if not exists
            DB['documents'][doc_id] = {'content': '', 'created_at': '2026-07-22T00:00:00'}
        
        doc = DB['documents'][doc_id]
        print(f"[GET_DOC] Found document, content length: {len(doc['content'])}")
        return jsonify({
            'document_id': doc_id,
            'content': doc['content'],
            'created_at': doc['created_at']
        }), 200
        
    except Exception as e:
        print(f"[GET_DOC] ERROR: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/documents/<doc_id>/save', methods=['POST'])
def save_document(doc_id):
    """Save document content"""
    print(f"[SAVE_DOC] ID: {doc_id}")
    try:
        payload = request.get_json() or {}
        print(f"[SAVE_DOC] Payload keys: {payload.keys()}")
        
        content = payload.get('content', '')
        print(f"[SAVE_DOC] Content length: {len(content)}")
        
        DB['documents'][doc_id] = {
            'content': content,
            'created_at': '2026-07-22T00:00:00',
            'updated_at': '2026-07-22T00:00:00'
        }
        
        print(f"[SAVE_DOC] Document saved successfully")
        return jsonify({
            'success': True,
            'document_id': doc_id,
            'message': 'Document saved'
        }), 200
        
    except Exception as e:
        print(f"[SAVE_DOC] ERROR: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500


# ============ HEALTH ENDPOINTS ============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok'})


@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({'status': 'Interview Platform API', 'version': '1.0.0'})


# ============ ERROR HANDLERS ============

@app.errorhandler(404)
def not_found(e):
    """Handle 404"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405"""
    print(f"[ERROR 405] {request.method} {request.path}")
    return jsonify({'error': 'Method not allowed'}), 405


@app.errorhandler(500)
def server_error(e):
    """Handle 500"""
    print(f"[ERROR 500] {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


# ============ RUN ============

if __name__ == '__main__':
    print("=" * 60)
    print("Interview Platform Backend")
    print("=" * 60)
    print("Starting server on http://0.0.0.0:5000")
    print("=" * 60)
    
    # Run with proper settings
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )
