# Usage Examples & Scenarios

## Complete Workflow Example

### Scenario: Interview Session Setup

#### Step 1: Support Person Initiates Session

**Actions**:
1. Launch Support Person APK
2. Click "Create New Session"
3. Wait for session creation (2-3 seconds)
4. Note displayed 6-digit code: `ABC123`
5. Share code with candidate via email/chat

**Backend Activity**:
```
POST /api/sessions → Creates:
  - InterviewSession (id: uuid-123, code: ABC123)
  - Document (id: uuid-456, content: "")
  - Records created_at timestamp
```

**Support Person App**:
```
Code: ABC123
Users: 0
[Connected to session]
[Ready for user to join]
```

---

#### Step 2: User Joins Session

**Actions**:
1. Receive session code: `ABC123`
2. Launch User APK
3. Enter code in input field
4. Click "Join Session"
5. App verifies code with backend

**Backend Activity**:
```
GET /api/sessions/ABC123 → Returns:
  {
    session_id: uuid-123,
    document_id: uuid-456,
    support_person_id: sp-001,
    created_at: 2024-01-01T12:00:00
  }

WebSocket: register event
  - Adds user to session room
  - Creates UserConnection record
  - Broadcasts user_connected event
```

**User App**:
```
→ Connecting...
→ Connected
Code verified: ABC123
[Transparent document displayed]
[Ready to type]
```

**Support Person App**:
```
Users: 1 (updated in real-time)
[Can see document area]
```

---

#### Step 3: Real-Time Collaboration

**Support Person Types**: "Tell me about your experience"

**Backend Activity**:
```
WebSocket: document_change event
  {
    change_type: "text_edit",
    new_value: "Tell me about your experience",
    user_id: sp-001,
    timestamp: 2024-01-01T12:01:00
  }

→ Record in document_changes table
→ Broadcast to session room
```

**User Receives**: Document updates instantly

**User Types**: "I have 5 years of experience"

**Backend Activity**:
```
WebSocket: document_change event
  {
    change_type: "text_edit",
    new_value: "Tell me about your experience\nI have 5 years of experience",
    user_id: user-001,
    timestamp: 2024-01-01T12:01:30
  }

→ Update document content
→ Broadcast to session room
```

**Support Person Receives**: Update appears instantly

---

#### Step 4: Styling Customization

**Support Person**: Clicks Settings

**Changes Made**:
```
Font Size: 14 → 18
Background Color: #FFFFFF → #FFFACD (light yellow)
Font Color: #000000 → #000000 (keep black)
```

**Backend Activity**:
```
WebSocket: document_change event
  {
    change_type: "style_change",
    new_value: {
      font_size: 18,
      bg_color: "#FFFACD",
      font_color: "#000000"
    }
  }

→ Update document record
→ Broadcast style_change event
```

**User App**: Document instantly shows:
- Larger text (18pt)
- Light yellow background
- All text preserved

---

#### Step 5: Admin Monitoring

**Admin**: Launches Admin APK

**Dashboard Shows**:
```
Active Sessions: 1
  ├─ Code: ABC123
  ├─ Support Person: sp-001
  ├─ Status: Active
  ├─ Users: 1
  └─ Documents: 1
```

**Admin**: Clicks "View Documents"

**Detailed View Shows**:
```
Session Code: ABC123
Active Users: 1
Connections:
  ├─ user-001 (user) - Connected: 12:00:30
  ├─ sp-001 (support_person) - Connected: 12:00:00
  └─ admin-001 (admin) - Connected: 12:02:00

Document Changes: 3
  ├─ text_edit - 12:01:00 (sp-001)
  ├─ text_edit - 12:01:30 (user-001)
  └─ style_change - 12:01:45 (sp-001)
```

---

#### Step 6: History Access

**Support Person**: Clicks Settings → View History

**History Shows**:
```
Change 1: [12:01:00] text_edit by sp-001
Change 2: [12:01:30] text_edit by user-001
Change 3: [12:01:45] style_change by sp-001
```

**Each Change Can Show**:
- Timestamp
- Change type
- Old value (if applicable)
- New value
- User who made change

---

#### Step 7: Session Completion

**User**: Clicks "Exit"

**Backend Activity**:
```
WebSocket: disconnect event
  - Remove from session room
  - Set disconnected_at timestamp
  - Broadcast user_disconnected event
```

**Support Person Sees**:
```
Users: 0 (updated in real-time)
[User disconnected]
```

**Admin Sees**:
```
Session ABC123:
  Active Users: 0
  
User Connections:
  ├─ user-001 (user) - Connected: 12:00:30, Disconnected: 12:05:00
  ├─ sp-001 (support_person) - Connected: 12:00:00, Still active
  └─ admin-001 (admin) - Connected: 12:02:00, Still active
```

---

## API Usage Examples

### Create Session (cURL)

```bash
curl -X POST http://localhost:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"support_person_id": "sp-interview-001"}' \
  -w "\n"
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "ABC123",
  "document_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "created_at": "2024-01-01T12:00:00"
}
```

---

### Verify Session Code (cURL)

```bash
curl http://localhost:5000/api/sessions/ABC123 \
  -w "\n"
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "support_person_id": "sp-interview-001",
  "created_at": "2024-01-01T12:00:00"
}
```

---

### Get Document History (cURL)

```bash
curl http://localhost:5000/api/documents/6ba7b810-9dad-11d1-80b4-00c04fd430c8/history \
  -w "\n"
```

**Response**:
```json
{
  "document_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "changes": [
    {
      "id": "change-001",
      "change_type": "text_edit",
      "old_value": "",
      "new_value": "Tell me about your experience",
      "timestamp": "2024-01-01T12:01:00",
      "user_id": "sp-interview-001"
    },
    {
      "id": "change-002",
      "change_type": "text_edit",
      "old_value": "Tell me about your experience",
      "new_value": "Tell me about your experience\nI have 5 years of experience",
      "timestamp": "2024-01-01T12:01:30",
      "user_id": "user-interview-001"
    },
    {
      "id": "change-003",
      "change_type": "style_change",
      "old_value": "{\"font_size\": 14}",
      "new_value": "{\"font_size\": 18, \"bg_color\": \"#FFFACD\"}",
      "timestamp": "2024-01-01T12:01:45",
      "user_id": "sp-interview-001"
    }
  ]
}
```

---

### Get All Sessions (Admin - cURL)

```bash
curl http://localhost:5000/api/admin/sessions \
  -w "\n"
```

**Response**:
```json
{
  "sessions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "code": "ABC123",
      "support_person_id": "sp-interview-001",
      "created_at": "2024-01-01T12:00:00",
      "is_active": true,
      "document_count": 1,
      "connection_count": 2
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "code": "XYZ789",
      "support_person_id": "sp-interview-002",
      "created_at": "2024-01-01T13:00:00",
      "is_active": true,
      "document_count": 1,
      "connection_count": 1
    }
  ]
}
```

---

### Get Connection Info (cURL)

```bash
curl http://localhost:5000/api/sessions/550e8400-e29b-41d4-a716-446655440000/connections \
  -w "\n"
```

**Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "active_count": 2,
  "all_connections": [
    {
      "user_id": "sp-interview-001",
      "user_type": "support_person",
      "connected_at": "2024-01-01T12:00:00",
      "disconnected_at": null
    },
    {
      "user_id": "user-interview-001",
      "user_type": "user",
      "connected_at": "2024-01-01T12:00:30",
      "disconnected_at": null
    },
    {
      "user_id": "admin-001",
      "user_type": "admin",
      "connected_at": "2024-01-01T12:02:00",
      "disconnected_at": null
    }
  ]
}
```

---

## WebSocket Event Examples

### Register Event (Client → Server)

**User Joining**:
```json
{
  "user_id": "user-interview-001",
  "user_type": "user",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response from Server**:
```json
{
  "status": "success",
  "user_id": "user-interview-001"
}
```

---

### Document Change Event (Client → Server)

**Text Edit**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "change_type": "text_edit",
  "new_value": "New text content",
  "old_value": "Old text content",
  "user_id": "user-interview-001"
}
```

**Style Change**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "change_type": "style_change",
  "new_value": {
    "font_size": 18,
    "bg_color": "#FFFACD",
    "font_color": "#000000"
  },
  "user_id": "support-interview-001"
}
```

---

### Broadcast Event (Server → All Clients in Room)

**Document Updated**:
```json
{
  "document_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "change_type": "text_edit",
  "new_value": "New text content",
  "updated_at": "2024-01-01T12:01:00",
  "user_id": "user-interview-001"
}
```

**User Connected**:
```json
{
  "user_id": "user-interview-001",
  "user_type": "user",
  "active_users": 2
}
```

---

## Practical Use Cases

### Case 1: Technical Interview

**Flow**:
1. Support person creates session: `TECH01`
2. Candidate joins with code
3. Interview questions written in document
4. Candidate types answers
5. Real-time evaluation by support person
6. All changes tracked for review
7. Admin monitors progress

### Case 2: Behavioral Interview

**Flow**:
1. Support person creates session: `BEHAV1`
2. Multiple candidates can join (same code)
3. Interview notes taken in document
4. Scoring/feedback added in real-time
5. Documents customized with colors for clarity
6. Admin reviews all evaluations
7. Complete audit trail maintained

### Case 3: Training Session

**Flow**:
1. Trainer creates session: `TRAIN1`
2. Multiple trainees join
3. Training materials displayed
4. Trainees take notes
5. Trainer modifies content in real-time
6. All changes visible to everyone
7. Training records preserved

### Case 4: Feedback Session

**Flow**:
1. Manager creates session: `REVIEW1`
2. Employee joins
3. Feedback written in document
4. Employee can see and respond
5. Both can edit simultaneously
6. Professional appearance maintained
7. HR can audit entire session

---

## Error Scenarios

### Scenario: Invalid Code

**User enters**: `INVALID`

**Backend Response**:
```
HTTP 404: {"error": "Invalid code"}
```

**User App**: Shows "Invalid code or session inactive"

---

### Scenario: Session Inactive

**Code was**: `ABC123` (session already ended)

**Backend Response**:
```
HTTP 400: {"error": "Session inactive"}
```

**User App**: Shows "Session inactive"

---

### Scenario: Connection Lost

**User loses network**:

1. WebSocket connection drops
2. Socket.IO attempts reconnection (3 retries)
3. User App shows "Reconnecting..."
4. If reconnected: Syncs latest state
5. If failed: Shows "Connection lost"

---

### Scenario: Duplicate Edits

**Both users edit simultaneously**:

```
User A: "Hello"
User B: "Hi"

Server receives both events
Last one wins (timestamps compared)
Winner: Depends on which arrives last
All changes recorded with timestamps
```

---

## Monitoring Examples

### Check Active Sessions

```bash
curl http://localhost:5000/api/admin/sessions | python -m json.tool
```

### Count Total Changes

```bash
sqlite3 backend/interview_platform.db \
  "SELECT COUNT(*) as total_changes FROM document_changes;"
```

### Find Longest Session

```bash
sqlite3 backend/interview_platform.db \
  "SELECT 
     s.code, 
     COUNT(uc.id) as connections,
     MAX(uc.disconnected_at) as ended
   FROM interview_sessions s
   JOIN user_connections uc ON s.id = uc.session_id
   GROUP BY s.id
   ORDER BY connections DESC
   LIMIT 5;"
```

### Export Session Data

```bash
# Export all changes for a session
sqlite3 backend/interview_platform.db \
  ".mode csv" \
  ".output session_report.csv" \
  "SELECT * FROM document_changes 
   WHERE document_id = '6ba7b810-9dad-11d1-80b4-00c04fd430c8';"
```

---

This guide covers all major scenarios and use cases. Refer to specific documentation files for more details:
- QUICKSTART.md - Fast setup
- ARCHITECTURE.md - System design
- DEPLOYMENT.md - Production setup
- FEATURES.md - Detailed feature list
