# System Architecture

## Overview

The Interview Document Sharing Platform is a real-time collaborative document system with three distinct user interfaces. The architecture uses WebSocket technology for instant synchronization across all connected clients.

```
┌──────────────────────────────────────────────────────────────┐
│                       INTERNET / LAN                         │
└──────────────────────────────────────────────────────────────┘
              ↑                    ↑                    ↑
         HTTPS/WSS           HTTPS/WSS            HTTPS/WSS
              │                    │                    │
    ┌─────────────────┐  ┌────────────────┐  ┌──────────────┐
    │  User APK       │  │Support Person  │  │  Admin APK   │
    │  (Kivy)         │  │  APK (Kivy)    │  │  (Kivy)      │
    │                 │  │                │  │              │
    ├─────────────────┤  ├────────────────┤  ├──────────────┤
    │- Code Entry     │  │- Session Mgmt  │  │- Dashboard   │
    │- Transparent    │  │- Doc Editing   │  │- Session     │
    │  Document       │  │- Live Sync     │  │  Monitoring  │
    │- Customization  │  │- User Tracking │  │- History     │
    └─────────────────┘  └────────────────┘  └──────────────┘
              │                    │                    │
              └────────┬───────────┴────────┬───────────┘
                       │                    │
                   WebSocket           WebSocket
                   Manager             Manager
                       │                    │
                       └────────┬───────────┘
                                │
                ┌───────────────────────────────────┐
                │  WebSocket Handler (Socket.IO)    │
                │  Real-time Event Broadcasting     │
                └───────────────────────────────────┘
                                │
                ┌───────────────────────────────────────────┐
                │      Flask Application Server             │
                │  http://0.0.0.0:5000                      │
                ├───────────────────────────────────────────┤
                │  Routes:                                  │
                │  - POST   /api/sessions                   │
                │  - GET    /api/sessions/<code>            │
                │  - GET    /api/documents/<id>/history     │
                │  - GET    /api/sessions/<id>/connections  │
                │  - GET    /api/admin/sessions             │
                │  - GET    /api/admin/documents/<id>       │
                └───────────────────────────────────────────┘
                                │
                ┌───────────────────────────────────────────┐
                │      SQLAlchemy ORM Layer                 │
                ├───────────────────────────────────────────┤
                │  - Session Management                     │
                │  - Document Versioning                    │
                │  - Connection Tracking                    │
                │  - Change History Logging                 │
                └───────────────────────────────────────────┘
                                │
                ┌───────────────────────────────────────────┐
                │      SQLite Database                      │
                │  interview_platform.db                    │
                ├───────────────────────────────────────────┤
                │  Tables:                                  │
                │  - interview_sessions                     │
                │  - documents                              │
                │  - document_changes                       │
                │  - user_connections                       │
                └───────────────────────────────────────────┘
```

## Component Details

### Frontend Applications (Kivy APKs)

#### User APK
**Purpose**: Join and participate in interview sessions

**Key Features**:
- Code verification for session access
- Transparent document rendering (invisible to screen capture)
- Real-time text editing with local changes
- Customizable document styling (opacity, colors, fonts)
- Live synchronization with other session participants

**Communication Flow**:
1. User enters 6-digit session code
2. APK sends code to backend for verification
3. Backend returns session_id and document_id
4. APK establishes WebSocket connection
5. APK joins session room and requests document sync
6. APK displays document with current state
7. User edits trigger WebSocket events
8. Changes broadcast to all session participants

**Transparent Document Implementation**:
- Uses Kivy Canvas with transparent color
- Overlay not captured by Android screen recording
- Visible on device screen but invisible to screen share
- User can control opacity for local visibility

#### Support Person APK
**Purpose**: Create sessions, manage documents, track connections

**Key Features**:
- Create new session (generates unique code)
- Live document editing with full UI
- Real-time connection tracking
- Document change history access
- Document styling customization
- Session management

**Communication Flow**:
1. Support person creates new session
2. Backend generates unique code
3. Backend creates initial document
4. Support person joins session as "support_person"
5. Support person sees connection count in real-time
6. Document changes sync instantly
7. Support person can view change history

#### Admin APK
**Purpose**: Monitor all sessions and activity

**Key Features**:
- Real-time dashboard of all sessions
- Live connection monitoring
- Session details and user tracking
- Document content preview
- Change history access
- Activity analytics

**Communication Flow**:
1. Admin launches app and connects to server
2. Admin registers as "admin" user type
3. Dashboard fetches all active sessions
4. WebSocket subscriptions for real-time updates
5. Admin can drill down to session details
6. Admin can view document history
7. All data updates in real-time

### Backend Server (Flask)

#### Architecture Layers

```
┌─────────────────────────────────────────┐
│         HTTP Request Handler             │
│  (Handles REST API and WebSocket)       │
├─────────────────────────────────────────┤
│         Business Logic Layer              │
│  - Session management                    │
│  - Document operations                   │
│  - User tracking                         │
│  - Change recording                      │
├─────────────────────────────────────────┤
│         Data Access Layer (SQLAlchemy)   │
│  - ORM mapping                           │
│  - Query building                        │
│  - Transaction management                │
├─────────────────────────────────────────┤
│         Database Layer (SQLite)          │
│  - Persistent storage                    │
│  - Transaction support                   │
│  - Indexing                              │
└─────────────────────────────────────────┘
```

#### REST API Endpoints

**Session Management**
```
POST   /api/sessions
├─ Input:  {support_person_id}
├─ Output: {session_id, code, document_id, created_at}
└─ Purpose: Create new interview session

GET    /api/sessions/<code>
├─ Input:  6-digit session code
├─ Output: {session_id, document_id, support_person_id, created_at}
└─ Purpose: Verify session code and get document info
```

**Document Operations**
```
GET    /api/documents/<document_id>/history
├─ Output: {document_id, changes: [{id, change_type, timestamp, user_id}]}
└─ Purpose: Get complete change history

GET    /api/sessions/<session_id>/connections
├─ Output: {session_id, active_count, all_connections: [...]}
└─ Purpose: Get active user connections
```

**Admin Operations**
```
GET    /api/admin/sessions
├─ Output: {sessions: [{id, code, support_person_id, is_active, document_count, connection_count}]}
└─ Purpose: Get all sessions dashboard data

GET    /api/admin/documents/<document_id>
├─ Output: {id, session_id, content, styling, created_at, change_history}
└─ Purpose: Get full document with history for admin review
```

#### WebSocket Events

**Client → Server Events**
```
register
├─ Payload: {user_id, user_type, session_id}
└─ Purpose: Register user in session

document_change
├─ Payload: {session_id, document_id, change_type, new_value, old_value, user_id}
├─ change_type: 'text_edit' | 'style_change' | 'image_insert'
└─ Purpose: Broadcast document change

request_sync
├─ Payload: {session_id, document_id}
└─ Purpose: Request current document state
```

**Server → Client Events**
```
connection_response
├─ Payload: {data: "Connected to server"}
└─ To: Connecting client

register_response
├─ Payload: {status, user_id}
└─ To: Registering client

document_updated
├─ Payload: {document_id, change_type, new_value, updated_at, user_id}
└─ To: All clients in session

sync_response
├─ Payload: {document_id, content, bg_color, font_color, font_size, opacity}
└─ To: Requesting client

user_connected
├─ Payload: {user_id, user_type, active_users}
└─ To: All clients in session

user_disconnected
├─ Payload: {user_id, session_id}
└─ To: All clients in session
```

### Database Schema

#### interview_sessions Table
```sql
CREATE TABLE interview_sessions (
    id VARCHAR(36) PRIMARY KEY,           -- UUID
    code VARCHAR(10) UNIQUE NOT NULL,     -- 6-digit code
    support_person_id VARCHAR(36),        -- Support person UUID
    created_at DATETIME DEFAULT NOW(),    -- Creation timestamp
    is_active BOOLEAN DEFAULT TRUE,       -- Session status
    
    FOREIGN KEY relationships:
    - ONE to MANY with documents
    - ONE to MANY with user_connections
);
```

#### documents Table
```sql
CREATE TABLE documents (
    id VARCHAR(36) PRIMARY KEY,           -- UUID
    session_id VARCHAR(36) NOT NULL,      -- Session reference
    content TEXT DEFAULT '',              -- Document content
    bg_color VARCHAR(7) DEFAULT '#FFFFFF',-- Background color
    font_color VARCHAR(7) DEFAULT '#000000', -- Font color
    font_size INTEGER DEFAULT 14,         -- Font size
    opacity FLOAT DEFAULT 1.0,            -- Document opacity
    created_at DATETIME DEFAULT NOW(),    -- Creation time
    updated_at DATETIME DEFAULT NOW(),    -- Last update time
    
    FOREIGN KEY (session_id) REFERENCES interview_sessions(id)
);
```

#### document_changes Table
```sql
CREATE TABLE document_changes (
    id VARCHAR(36) PRIMARY KEY,           -- UUID
    document_id VARCHAR(36) NOT NULL,     -- Document reference
    change_type VARCHAR(50),              -- text_edit, style_change, etc
    old_value TEXT,                       -- Previous value
    new_value TEXT,                       -- New value
    timestamp DATETIME DEFAULT NOW(),     -- Change timestamp
    user_id VARCHAR(36),                  -- User who made change
    
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
```

#### user_connections Table
```sql
CREATE TABLE user_connections (
    id VARCHAR(36) PRIMARY KEY,           -- UUID
    session_id VARCHAR(36) NOT NULL,      -- Session reference
    user_id VARCHAR(36),                  -- User UUID
    connected_at DATETIME DEFAULT NOW(),  -- Connection time
    disconnected_at DATETIME NULL,        -- Disconnection time
    user_type VARCHAR(20),                -- 'user', 'support_person', 'admin'
    
    FOREIGN KEY (session_id) REFERENCES interview_sessions(id)
);
```

## Data Flow Diagrams

### Session Creation Flow
```
Support Person
      │
      └──> Create New Session (UI Button)
             │
             └──> POST /api/sessions
                  │
                  ├─> Generate UUID for session
                  ├─> Generate 6-digit code
                  ├─> Create document
                  ├─> Save to DB
                  │
                  └──> Response: {session_id, code, document_id}
                       │
                       └──> Display code to support person
                            Connect to WebSocket
```

### User Join Flow
```
User
  │
  └──> Enter 6-digit code
       │
       └──> GET /api/sessions/<code>
            │
            ├─> Verify code exists
            ├─> Verify session is active
            ├─> Return session_id, document_id
            │
            └──> Response received
                 │
                 ├─> Store session_id, document_id
                 ├─> Connect to WebSocket
                 │
                 └──> emit 'register' event
                      │
                      ├─> Create UserConnection record
                      ├─> Add to session room
                      │
                      └──> emit 'register_response'
                           │
                           └──> emit 'request_sync'
                                │
                                └──> emit 'sync_response'
                                     │
                                     └──> Display document
```

### Document Edit Flow
```
User/Support Person
      │
      └──> Edit document text
           │
           └──> TextInput.bind(on_text_change)
                │
                └──> emit 'document_change'
                     │
                     ├─> Store change in document_changes
                     ├─> Update document content
                     ├─> Update document.updated_at
                     │
                     └──> broadcast 'document_updated' to session room
                          │
                          ├─> Other users receive update
                          ├─> Update their local document
                          └─> Refresh display
```

### Admin Monitoring Flow
```
Admin
  │
  └──> Open Dashboard
       │
       └──> Connect to WebSocket
            │
            ├─> Register as admin
            │
            └──> GET /api/admin/sessions
                 │
                 ├─> Fetch all sessions
                 ├─> Display in dashboard
                 │
                 └──> Subscribe to WebSocket events
                      │
                      ├─> 'user_connected'
                      ├─> 'document_updated'
                      │
                      └──> Real-time dashboard updates
```

## Real-Time Synchronization

### Synchronization Strategy

1. **Event-Driven Updates**
   - Changes broadcast immediately
   - All clients in session receive updates
   - ms-level synchronization

2. **Optimistic Updates**
   - Client applies change locally immediately
   - Change sent to server
   - Server broadcasts to other clients
   - Conflict resolution: Last-write-wins

3. **State Consistency**
   - New clients request sync on join
   - Server sends current state
   - Subsequent updates applied incrementally

### Conflict Resolution

For concurrent edits at same position:
- Last change received by server wins
- Timestamp is used as tiebreaker
- Change history preserves all versions

## Performance Considerations

### Optimization Techniques

1. **Database Indexing**
   ```sql
   CREATE INDEX idx_session_code ON interview_sessions(code);
   CREATE INDEX idx_document_session ON documents(session_id);
   CREATE INDEX idx_change_document ON document_changes(document_id);
   CREATE INDEX idx_connection_session ON user_connections(session_id);
   ```

2. **WebSocket Efficiency**
   - Room-based broadcasting (not all clients)
   - Minimal payload sizes
   - Compression enabled

3. **Caching Strategy**
   - Cache session codes temporarily
   - Cache active session list for admin
   - Invalidate on updates

### Scalability

**Current Architecture Limits**:
- Single SQLite database: ~10,000 documents
- Single WebSocket connection: ~1,000 concurrent users
- Single server: ~5,000 active sessions

**Scaling Solutions**:
- PostgreSQL for database
- Redis for WebSocket message queue
- Load balancer for multiple server instances
- CDN for static assets

## Security Architecture

### Authentication & Authorization

1. **Session Verification**
   - 6-digit codes for user access
   - Code verification on join
   - Code expiration (optional)

2. **User Type Authorization**
   - Users: View/edit document only
   - Support Persons: Full document management
   - Admins: Read-only monitoring

3. **Data Isolation**
   - Documents scoped to sessions
   - Users only see their session
   - Admins see all sessions

### Data Protection

1. **Transport Security**
   - HTTPS/WSS for production
   - TLS 1.2+ encryption
   - Certificate validation

2. **Storage Security**
   - Passwords hashed (if added)
   - Sensitive data encrypted at rest
   - Regular backups

3. **Audit Trail**
   - All changes logged
   - User tracking per change
   - Timestamps on all records

## Deployment Architecture

### Development
- Local Flask server on localhost:5000
- SQLite database in project directory
- WebSocket over HTTP (localhost only)

### Production
```
┌──────────────────────────────────────────────┐
│         CloudFlare / AWS Route 53             │
│         (DNS + DDoS Protection)              │
├──────────────────────────────────────────────┤
│         AWS ELB / Nginx Load Balancer        │
│         (SSL/TLS Termination)                │
├──────────────────────────────────────────────┤
│    Application Server Cluster (3+ nodes)    │
│    - Flask + Gunicorn + Socket.IO           │
│    - Horizontal scaling                      │
├──────────────────────────────────────────────┤
│    Redis Cache & Message Queue              │
│    - Session storage                         │
│    - Message broadcasting                    │
├──────────────────────────────────────────────┤
│    PostgreSQL Database with Replication     │
│    - Master-Slave or Multi-Master           │
│    - Regular backups to S3                   │
├──────────────────────────────────────────────┤
│    Monitoring & Logging                     │
│    - CloudWatch / ELK Stack                 │
│    - Alerting and dashboards               │
└──────────────────────────────────────────────┘
```

## Technology Rationale

| Component | Choice | Reason |
|-----------|--------|--------|
| Backend | Flask | Lightweight, WebSocket support, easy deployment |
| WebSocket | Socket.IO | Cross-browser, fallback support, room broadcasting |
| Database | SQLite/PostgreSQL | ACID compliance, change tracking support |
| Frontend | Kivy | Cross-platform mobile, Python native, APK support |
| Communication | JSON | Lightweight, human-readable, standard |
| Session Management | UUID + Code | Security + usability balance |
| Change Tracking | Event Sourcing | Complete audit trail, replay capability |
