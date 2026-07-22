"""
Interview Platform Backend - Flask API
Simple, robust REST API for interview management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'interview-platform-secret-key')
# Use backend directory for database
db_path = os.path.join(os.path.dirname(__file__), 'interview_platform.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Enable CORS - BEFORE anything else
CORS(app, 
     resources={r"/api/*": {"origins": "*"}},
     methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
     allow_headers=["Content-Type"],
     supports_credentials=False)

# Initialize database
db = SQLAlchemy(app)

# ==================== DATABASE MODELS ====================

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    support_person_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    documents = db.relationship('Document', backref='session', lazy=True, cascade='all, delete-orphan')
    connections = db.relationship('UserConnection', backref='session', lazy=True, cascade='all, delete-orphan')


class Document(db.Model):
    __tablename__ = 'documents'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('interview_sessions.id'), nullable=False)
    content = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserConnection(db.Model):
    __tablename__ = 'user_connections'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('interview_sessions.id'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    connected_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_type = db.Column(db.String(20), nullable=False, default='user')


# ==================== ERROR HANDLERS ====================

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error', 'details': str(error)}), 500


# ==================== API ENDPOINTS ====================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'status': 'Interview Platform API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'sessions_create': 'POST /api/sessions',
            'sessions_verify': 'GET /api/sessions/<code>',
            'admin_sessions': 'GET /api/admin/sessions',
            'admin_documents': 'GET /api/admin/documents/<id>'
        }
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


@app.route('/api/sessions', methods=['POST'])
def create_session():
    """Create new interview session"""
    try:
        data = request.get_json() or {}
        support_person_id = data.get('support_person_id', 'unknown')
        
        # Generate 6-digit code
        code = str(uuid.uuid4())[:6].upper()
        
        # Create session
        session = InterviewSession(
            code=code,
            support_person_id=support_person_id
        )
        db.session.add(session)
        db.session.flush()
        
        # Create document
        document = Document(session_id=session.id)
        db.session.add(document)
        db.session.commit()
        
        return jsonify({
            'session_id': session.id,
            'code': code,
            'document_id': document.id,
            'created_at': session.created_at.isoformat()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/sessions/<code>', methods=['GET'])
def verify_session(code):
    """Verify session code"""
    try:
        session = InterviewSession.query.filter_by(code=code.upper()).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if not session.is_active:
            return jsonify({'error': 'Session inactive'}), 400
        
        document = session.documents[0] if session.documents else None
        
        if not document:
            return jsonify({'error': 'No document'}), 404
        
        return jsonify({
            'session_id': session.id,
            'code': session.code,
            'document_id': document.id,
            'support_person_id': session.support_person_id,
            'created_at': session.created_at.isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/sessions', methods=['GET'])
def get_all_sessions():
    """Get all sessions"""
    try:
        sessions = InterviewSession.query.all()
        return jsonify({
            'sessions': [
                {
                    'id': s.id,
                    'code': s.code,
                    'support_person_id': s.support_person_id,
                    'created_at': s.created_at.isoformat(),
                    'is_active': s.is_active,
                    'document_count': len(s.documents),
                    'connection_count': len([c for c in s.connections if c.user_type != 'disconnected'])
                }
                for s in sessions
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/documents/<doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get document details"""
    try:
        document = Document.query.get(doc_id)
        
        if not document:
            return jsonify({'error': 'Document not found'}), 404
        
        return jsonify({
            'id': document.id,
            'session_id': document.session_id,
            'content': document.content,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== INITIALIZATION ====================

def init_db():
    """Initialize database"""
    try:
        with app.app_context():
            db.create_all()
            print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database error: {e}")


if __name__ == '__main__':
    init_db()
    print("Starting Interview Platform Backend...")
    print("Server: http://0.0.0.0:5000")
    print("API: http://localhost:5000/api/health")
    app.run(host='0.0.0.0', port=5000, debug=True)
