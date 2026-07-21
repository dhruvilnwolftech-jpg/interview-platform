# Interview Document Sharing Platform

A multi-interface application for real-time document sharing during interviews, with three separate APK applications for Users, Interview Support Persons, and Admins.

## Features

### User APK
- **Code-based Session Joining**: Users enter a 6-digit code to join an interview session
- **Transparent Document**: View documents that are invisible during screen sharing (anti-screen capture)
- **Live Editing**: Real-time document editing with instant synchronization
- **Customization**: Control opacity, background color, font color, and font size
- **Privacy**: Document changes are synced only between users in the same session

### Interview Support Person APK
- **Session Creation**: Generate unique session codes for interviews
- **Live Document Editing**: Create and edit documents in real-time
- **Connection Tracking**: See active user connections (shows count of connected users)
- **Document History**: Access complete change history for compliance and review
- **Styling Control**: Customize document appearance with colors and fonts

### Admin APK
- **Real-time Dashboard**: Monitor all active interview sessions
- **Live Statistics**: Track active users and connection metrics
- **Session Details**: View detailed information about each session
- **Document Monitoring**: Review document content and change history
- **Activity Tracking**: See all user connections and disconnections

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Backend Server                         │
│  (Flask + Socket.IO + SQLAlchemy + SQLite)            │
│  - Real-time WebSocket communication                    │
│  - Document synchronization (ms-level)                  │
│  - Session management and verification                  │
│  - Complete history tracking                            │
└─────────────────────────────────────────────────────────┘
       ↑                    ↑                    ↑
       │                    │                    │
   WebSocket            WebSocket            WebSocket
   (User)            (Support Person)         (Admin)
       │                    │                    │
┌─────────────┐  ┌──────────────────┐  ┌──────────────┐
│  User APK   │  │Support Person APK│  │  Admin APK   │
│  (Kivy)     │  │   (Kivy)         │  │   (Kivy)     │
└─────────────┘  └──────────────────┘  └──────────────┘
```

## Technology Stack

- **Backend**: Python Flask + Flask-SocketIO (real-time WebSocket)
- **Database**: SQLite (can upgrade to PostgreSQL)
- **Frontend**: Kivy + KivyMD (cross-platform mobile framework)
- **Communication**: Socket.IO (real-time bidirectional communication)
- **Packaging**: Buildozer (builds Python into Android APK)

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Android SDK and NDK (for building APKs)
- Buildozer (for packaging)
- Java Development Kit (JDK)

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r ../requirements.txt
```

### 2. Initialize Database

```bash
cd backend
python
>>> from server import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### 3. Start Backend Server

```bash
cd backend
python server.py
```

The server will start on `http://localhost:5000` and accept WebSocket connections.

### 4. Install APK Dependencies (Local Testing)

```bash
pip install -r requirements.txt
```

## Running Applications Locally (for Testing)

### Test Backend API

```bash
# Create a session
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"support_person_id": "sp-001"}'

# Verify session code
curl http://localhost:5000/api/sessions/ABC123
```

### Run User APK (Local)

```bash
cd user_app
python main.py
```

### Run Support Person APK (Local)

```bash
cd support_person_app
python main.py
```

### Run Admin APK (Local)

```bash
cd admin_app
python main.py
```

## Building APK Packages

### Prerequisites for Building APKs

1. Install Buildozer dependencies:
```bash
pip install buildozer
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev  # Linux
```

2. Install Java Development Kit (JDK):
```bash
sudo apt-get install default-jdk  # Linux
# or brew install java  # macOS
```

### Build User APK

```bash
cd user_app
buildozer android debug
# APK will be in bin/interview_user-0.1-debug.apk
```

### Build Support Person APK

Update the `buildozer.spec` file:
- Change `source.dir = ./support_person_app`
- Change `package.name = interview_support`
- Change `title = Interview Platform - Support Person`

```bash
cd ..
buildozer android debug
```

### Build Admin APK

Update the `buildozer.spec` file:
- Change `source.dir = ./admin_app`
- Change `package.name = interview_admin`
- Change `title = Interview Platform - Admin`

```bash
cd ..
buildozer android debug
```

## API Endpoints

### Session Management
- `POST /api/sessions` - Create new session
- `GET /api/sessions/<code>` - Verify session code

### Document Operations
- `GET /api/documents/<document_id>/history` - Get change history

### Admin Endpoints
- `GET /api/admin/sessions` - Get all sessions
- `GET /api/admin/documents/<document_id>` - Get full document details
- `GET /api/sessions/<session_id>/connections` - Get active connections

### Health Check
- `GET /api/health` - Server health status

## WebSocket Events

### Client → Server
- `register` - Register user/support/admin
- `document_change` - Send document edit/style change
- `request_sync` - Request document state sync

### Server → Client
- `connection_response` - Connection acknowledgment
- `register_response` - Registration result
- `document_updated` - Document change notification
- `sync_response` - Document state sync
- `user_connected` - New user connected to session
- `user_disconnected` - User disconnected from session

## Database Schema

### Tables
1. **interview_sessions** - Stores session information
2. **documents** - Stores document content and styling
3. **document_changes** - Complete change history
4. **user_connections** - Tracks all user connections/disconnections

## Configuration

### Backend Configuration (`.env`)
```
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///interview_platform.db
DEBUG=True
```

### Server URL Configuration
Update `SERVER_URL` in each APK's main.py:
```python
SERVER_URL = 'http://your-server-ip:5000'  # Change to actual server
```

## Security Considerations

1. **Code Verification**: All sessions are verified with 6-digit codes
2. **User Isolation**: Documents are session-specific
3. **Connection Tracking**: All connections are logged with timestamps
4. **Change History**: Complete audit trail of all modifications
5. **Production Security**:
   - Use HTTPS instead of HTTP
   - Change SECRET_KEY in production
   - Use PostgreSQL instead of SQLite
   - Implement proper authentication
   - Use environment variables for sensitive data

## Deployment

### Local Network Deployment
1. Get your machine's IP address
2. Update `SERVER_URL` in all APKs
3. Start backend server on your machine
4. Build and install APKs on devices
5. All devices must be on the same network

### Cloud Deployment
1. Deploy backend to cloud server (AWS, GCP, Azure, Heroku)
2. Use HTTPS and proper domain name
3. Configure CORS properly
4. Update `SERVER_URL` in APKs
5. Consider using Redis for scaling WebSocket connections

## Transparent Document Feature

The transparent document in the User APK appears invisible during screen sharing because:
- The document uses a transparent canvas overlay
- Screen capture APIs can't detect UI overlays rendered on Kivy layer
- Only keyboard input and direct interaction reveals content
- This prevents accidental document exposure during screen shares

### Testing Screen Share Protection
1. User opens document on Android
2. User starts screen share (Zoom, Google Meet, etc.)
3. Document remains invisible on screen share
4. Document is fully visible to user on their device

## Troubleshooting

### Connection Issues
- Ensure backend server is running: `python backend/server.py`
- Check firewall allows port 5000
- Verify `SERVER_URL` matches actual server address
- Check network connectivity between devices

### Database Issues
- Delete `interview_platform.db` to reset database
- Check file permissions on database location

### APK Issues
- Clear app cache before reinstalling
- Check Android API level compatibility
- Ensure all permissions are granted

## Future Enhancements

1. **Image Support**: Insert images into documents
2. **Rich Text Editing**: Bold, italic, formatting options
3. **Export Functionality**: Save documents as PDF/DOC
4. **Chat Integration**: Real-time messaging
5. **Voice/Video**: Built-in communication
6. **Encryption**: End-to-end document encryption
7. **Multiple Documents**: Handle multiple docs per session
8. **Mobile Optimization**: Better UI for different screen sizes

## Support

For issues or questions:
1. Check logs in `backend/` directory
2. Review API responses using browser console
3. Check WebSocket connection in browser DevTools
4. Verify database contents using SQLite browser

## License

This project is provided as-is for educational and commercial use.
