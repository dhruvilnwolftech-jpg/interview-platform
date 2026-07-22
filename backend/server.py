"""
Interview Document Sharing Platform - Backend Server
Real-time synchronization using WebSocket (Socket.IO)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///interview_platform.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)

# Placeholder for socketio (disabled for deployment)
socketio = None

# ==================== DATABASE MODELS ====================

class InterviewSession(db.Model):
    """Stores interview session information"""
    __tablename__ = 'interview_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    support_person_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    documents = db.relationship('Document', backref='session', lazy=True, cascade='all, delete-orphan')
    connections = db.relationship('UserConnection', backref='session', lazy=True, cascade='all, delete-orphan')


class Document(db.Model):
    """Stores document content and metadata"""
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('interview_sessions.id'), nullable=False)
    content = db.Column(db.Text, default='')
    bg_color = db.Column(db.String(7), default='#FFFFFF')
    font_color = db.Column(db.String(7), default='#000000')
    font_size = db.Column(db.Integer, default=14)
    opacity = db.Column(db.Float, default=1.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    changes = db.relationship('DocumentChange', backref='document', lazy=True, cascade='all, delete-orphan')


class DocumentChange(db.Model):
    """Tracks all changes to documents for history"""
    __tablename__ = 'document_changes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = db.Column(db.String(36), db.ForeignKey('documents.id'), nullable=False)
    change_type = db.Column(db.String(50), nullable=False)  # 'text_edit', 'style_change', 'image_insert'
    old_value = db.Column(db.Text)
    new_value = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.String(36), nullable=False)


class UserConnection(db.Model):
    """Tracks user connections to documents"""
    __tablename__ = 'user_connections'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('interview_sessions.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    disconnected_at = db.Column(db.DateTime)
    user_type = db.Column(db.String(20), nullable=False)  # 'user', 'support_person', 'admin'


# ==================== SOCKET.IO EVENTS ====================

# Store active connections for real-time updates
active_connections = {}


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    client_id = request.sid
    active_connections[client_id] = {
        'user_id': None,
        'user_type': None,
        'session_id': None
    }
    print(f"Client connected: {client_id}")
    emit('connection_response', {'data': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    client_id = request.sid
    if client_id in active_connections:
        conn = active_connections[client_id]
        if conn['session_id']:
            # Record disconnection
            user_conn = UserConnection.query.filter_by(
                user_id=conn['user_id'],
                session_id=conn['session_id']
            ).first()
            if user_conn:
                user_conn.disconnected_at = datetime.utcnow()
                db.session.commit()
            
            # Notify others about disconnection
            socketio.emit('user_disconnected', {
                'user_id': conn['user_id'],
                'session_id': conn['session_id']
            }, room=conn['session_id'])
        
        del active_connections[client_id]
    print(f"Client disconnected: {client_id}")


@socketio.on('register')
def handle_register(data):
    """Register user and join session room"""
    user_id = data.get('user_id', str(uuid.uuid4()))
    user_type = data.get('user_type')  # 'user', 'support_person', 'admin'
    session_id = data.get('session_id')
    
    client_id = request.sid
    active_connections[client_id]['user_id'] = user_id
    active_connections[client_id]['user_type'] = user_type
    active_connections[client_id]['session_id'] = session_id
    
    join_room(session_id)
    
    # Record connection
    connection = UserConnection(
        user_id=user_id,
        session_id=session_id,
        user_type=user_type
    )
    db.session.add(connection)
    db.session.commit()
    
    # Get current active user count
    active_count = UserConnection.query.filter_by(
        session_id=session_id,
        disconnected_at=None
    ).count()
    
    emit('register_response', {'status': 'success', 'user_id': user_id})
    socketio.emit('user_connected', {
        'user_id': user_id,
        'user_type': user_type,
        'active_users': active_count
    }, room=session_id)


@socketio.on('document_change')
def handle_document_change(data):
    """Handle real-time document changes"""
    session_id = data.get('session_id')
    document_id = data.get('document_id')
    change_type = data.get('change_type')  # 'text_edit', 'style_change', 'image_insert'
    new_value = data.get('new_value')
    old_value = data.get('old_value')
    user_id = data.get('user_id')
    
    # Record change in database
    doc_change = DocumentChange(
        document_id=document_id,
        change_type=change_type,
        new_value=new_value,
        old_value=old_value,
        user_id=user_id
    )
    db.session.add(doc_change)
    db.session.commit()
    
    # Update document
    document = Document.query.get(document_id)
    if change_type == 'text_edit':
        document.content = new_value
    elif change_type == 'style_change':
        for key, value in new_value.items():
            if hasattr(document, key):
                setattr(document, key, value)
    
    document.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Broadcast to all users in session
    socketio.emit('document_updated', {
        'document_id': document_id,
        'change_type': change_type,
        'new_value': new_value,
        'updated_at': document.updated_at.isoformat(),
        'user_id': user_id
    }, room=session_id)


@socketio.on('request_sync')
def handle_sync_request(data):
    """Send current document state to newly connected user"""
    session_id = data.get('session_id')
    document_id = data.get('document_id')
    
    document = Document.query.get(document_id)
    if document:
        emit('sync_response', {
            'document_id': document_id,
            'content': document.content,
            'bg_color': document.bg_color,
            'font_color': document.font_color,
            'font_size': document.font_size,
            'opacity': document.opacity,
            'updated_at': document.updated_at.isoformat()
        })


# ==================== ROOT ENDPOINT ====================

@app.route('/', methods=['GET'])
def welcome():
    """Welcome endpoint"""
    return jsonify({
        'status': 'Welcome to Interview Platform Backend',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'create_session': 'POST /api/sessions',
            'verify_code': 'GET /api/sessions/<code>',
            'get_connections': 'GET /api/sessions/<id>/connections',
            'get_history': 'GET /api/documents/<id>/history',
            'admin_sessions': 'GET /api/admin/sessions',
            'admin_documents': 'GET /api/admin/documents/<id>'
        }
    })

# ==================== REST API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create new interview session (Support Person)"""
    data = request.json
    
    # Generate 6-digit code
    code = str(uuid.uuid4())[:6].upper()
    support_person_id = data.get('support_person_id')
    
    session = InterviewSession(
        code=code,
        support_person_id=support_person_id
    )
    db.session.add(session)
    db.session.commit()
    
    # Create initial document
    document = Document(session_id=session.id)
    db.session.add(document)
    db.session.commit()
    
    return jsonify({
        'session_id': session.id,
        'code': code,
        'document_id': document.id,
        'created_at': session.created_at.isoformat()
    }), 201


@app.route('/api/sessions/<code>', methods=['GET'])
def verify_session(code):
    """Verify session code and get document details (User)"""
    session = InterviewSession.query.filter_by(code=code).first()
    
    if not session:
        return jsonify({'error': 'Invalid code'}), 404
    
    if not session.is_active:
        return jsonify({'error': 'Session inactive'}), 400
    
    document = session.documents[0] if session.documents else None
    
    if not document:
        return jsonify({'error': 'No document found'}), 404
    
    return jsonify({
        'session_id': session.id,
        'document_id': document.id,
        'support_person_id': session.support_person_id,
        'created_at': session.created_at.isoformat()
    }), 200


@app.route('/api/documents/<document_id>/history', methods=['GET'])
def get_document_history(document_id):
    """Get document change history"""
    changes = DocumentChange.query.filter_by(document_id=document_id).all()
    
    return jsonify({
        'document_id': document_id,
        'changes': [
            {
                'id': change.id,
                'change_type': change.change_type,
                'old_value': change.old_value,
                'new_value': change.new_value,
                'timestamp': change.timestamp.isoformat(),
                'user_id': change.user_id
            }
            for change in changes
        ]
    }), 200


@app.route('/api/sessions/<session_id>/connections', methods=['GET'])
def get_session_connections(session_id):
    """Get active connections count for a session"""
    active_count = UserConnection.query.filter_by(
        session_id=session_id,
        disconnected_at=None
    ).count()
    
    connections = UserConnection.query.filter_by(session_id=session_id).all()
    
    return jsonify({
        'session_id': session_id,
        'active_count': active_count,
        'all_connections': [
            {
                'user_id': conn.user_id,
                'user_type': conn.user_type,
                'connected_at': conn.connected_at.isoformat(),
                'disconnected_at': conn.disconnected_at.isoformat() if conn.disconnected_at else None
            }
            for conn in connections
        ]
    }), 200


@app.route('/api/admin/sessions', methods=['GET'])
def get_all_sessions():
    """Get all sessions with documents (Admin)"""
    sessions = InterviewSession.query.all()
    
    return jsonify({
        'sessions': [
            {
                'id': session.id,
                'code': session.code,
                'support_person_id': session.support_person_id,
                'created_at': session.created_at.isoformat(),
                'is_active': session.is_active,
                'document_count': len(session.documents),
                'connection_count': len([c for c in session.connections if not c.disconnected_at])
            }
            for session in sessions
        ]
    }), 200


@app.route('/api/admin/documents/<document_id>', methods=['GET'])
def get_admin_document(document_id):
    """Get full document details for admin"""
    document = Document.query.get(document_id)
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    changes = DocumentChange.query.filter_by(document_id=document_id).all()
    
    return jsonify({
        'id': document.id,
        'session_id': document.session_id,
        'content': document.content,
        'bg_color': document.bg_color,
        'font_color': document.font_color,
        'font_size': document.font_size,
        'opacity': document.opacity,
        'created_at': document.created_at.isoformat(),
        'updated_at': document.updated_at.isoformat(),
        'change_history': [
            {
                'id': change.id,
                'change_type': change.change_type,
                'timestamp': change.timestamp.isoformat(),
                'user_id': change.user_id
            }
            for change in changes
        ]
    }), 200


# ==================== DATABASE INITIALIZATION ====================

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'InterviewSession': InterviewSession, 'Document': Document}


# ==================== APP STARTUP ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    print("Starting Interview Platform Backend Server...")
    print("Server running on http://localhost:5000")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
