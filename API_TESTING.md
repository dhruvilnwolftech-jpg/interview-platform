# Live API Testing Guide

Your backend is now live at: **https://interview-platform-bdot.onrender.com/**

## Test It Now

### 1. Health Check (Test Connection)
```bash
curl https://interview-platform-bdot.onrender.com/api/health
```

Expected response:
```json
{"status":"ok","timestamp":"2026-07-22T..."}
```

---

## 2. Create an Interview Session

This is what a **support person** does to start an interview.

```bash
curl -X POST https://interview-platform-bdot.onrender.com/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"support_person_id":"sp-001"}'
```

Response:
```json
{
  "session_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "code": "ABC123",
  "document_id": "d7e8f9g0-h1i2-j3k4-l5m6-n7o8p9q0r1s2",
  "created_at": "2026-07-22T09:45:00.123456"
}
```

**Save the `code` (e.g., "ABC123") - this is what the user enters**

---

## 3. Verify Session Code

This is what a **user/candidate** does when they enter the code.

```bash
curl https://interview-platform-bdot.onrender.com/api/sessions/ABC123
```

Replace `ABC123` with the code from step 2.

Response:
```json
{
  "session_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "document_id": "d7e8f9g0-h1i2-j3k4-l5m6-n7o8p9q0r1s2",
  "support_person_id": "sp-001",
  "created_at": "2026-07-22T09:45:00.123456"
}
```

---

## 4. Get All Sessions (Admin)

```bash
curl https://interview-platform-bdot.onrender.com/api/admin/sessions
```

Response:
```json
{
  "sessions": [
    {
      "id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
      "code": "ABC123",
      "support_person_id": "sp-001",
      "created_at": "2026-07-22T09:45:00.123456",
      "is_active": true,
      "document_count": 1,
      "connection_count": 0
    }
  ]
}
```

---

## 5. Get Document Details (Admin)

```bash
curl https://interview-platform-bdot.onrender.com/api/admin/documents/d7e8f9g0-h1i2-j3k4-l5m6-n7o8p9q0r1s2
```

Replace the ID with the `document_id` from step 2.

Response:
```json
{
  "id": "d7e8f9g0-h1i2-j3k4-l5m6-n7o8p9q0r1s2",
  "session_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "content": "",
  "bg_color": "#FFFFFF",
  "font_color": "#000000",
  "font_size": 14,
  "opacity": 1.0,
  "created_at": "2026-07-22T09:45:00.123456",
  "updated_at": "2026-07-22T09:45:00.123456",
  "change_history": []
}
```

---

## 6. Get Document History

```bash
curl https://interview-platform-bdot.onrender.com/api/documents/d7e8f9g0-h1i2-j3k4-l5m6-n7o8p9q0r1s2/history
```

Response:
```json
{
  "document_id": "d7e8f9g0-h1i2-j3k4-l5m6-n7o8p9q0r1s2",
  "changes": []
}
```

---

## 🎯 Next: Build a Web UI

Your APIs are ready! Now you can build:

- **Support Person App** - Create sessions, monitor candidates
- **Candidate App** - Enter code, view shared documents
- **Admin Dashboard** - View all sessions and history

Example web UI features:
- Login page
- Session creation form
- Real-time document editor
- Session history viewer
- Analytics dashboard

---

## Database

Your data is stored in SQLite on Render (free tier).

Each session has:
- ✅ Interview Session (code, support person ID, created date)
- ✅ Document (content, styling, timestamps)
- ✅ Document Changes (edit history)
- ✅ User Connections (who joined and when)

---

## Deployment Status

| Component | Status | URL |
|-----------|--------|-----|
| Backend API | ✅ Live | https://interview-platform-bdot.onrender.com |
| Database | ✅ Running | SQLite on Render |
| Health Check | ✅ Working | /api/health |
| Session APIs | ✅ Working | /api/sessions |
| Admin APIs | ✅ Working | /api/admin/* |

---

**Ready to build the UI? Let me know!**
