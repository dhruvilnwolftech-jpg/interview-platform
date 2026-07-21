# Quick Reference Card

## 🚀 Start the System (5 Steps, 5 Minutes)

### Step 1: Install Dependencies
```bash
cd C:\Users\dell\Desktop\my_project
pip install -r requirements.txt
```
⏱️ **2 minutes**

---

### Step 2: Start Backend (Terminal 1 - KEEP RUNNING)
```bash
cd backend
python server.py
```

**Expected:**
```
Starting Interview Platform Backend Server...
Server running on http://localhost:5000
```

⏱️ **30 seconds**

---

### Step 3: Test APIs (Terminal 2)
```bash
cd tests
python test_api.py
```

**Expected:**
```
RESULTS: 8 passed, 0 failed
```

⏱️ **2 minutes**

---

### Step 4: Run Apps (Terminals 3, 4, 5)

**Terminal 3:**
```bash
cd support_person_app
python main.py
```

**Terminal 4:**
```bash
cd user_app
python main.py
```

**Terminal 5:**
```bash
cd admin_app
python main.py
```

⏱️ **1 minute**

---

### Step 5: Test Workflow
1. **Support**: Click "Create New Session" → Copy code
2. **User**: Paste code → Click "Join"
3. **Both**: Type text → See real-time sync
4. **Admin**: Click "Refresh" → See dashboard

⏱️ **2 minutes**

---

## 📋 Full Testing Checklist

### Backend
- [ ] Dependencies installed
- [ ] Database created
- [ ] Backend server running
- [ ] 8/8 API tests pass
- [ ] 12/12 Integration tests pass

### Applications
- [ ] Support Person APK running
- [ ] User APK running
- [ ] Admin APK running

### Functionality
- [ ] User can join with code
- [ ] Real-time sync works (both directions)
- [ ] Document customization works
- [ ] Admin dashboard shows users
- [ ] Change history tracks updates
- [ ] User can disconnect

---

## 🔥 Common Commands

### Check Python
```bash
python --version
```

### Check Dependencies
```bash
pip list | findstr flask
```

### Kill Process on Port 5000
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Reset Database
```bash
cd backend
del interview_platform.db
python -c "from server import app, db; app.app_context().push(); db.create_all()"
```

### View Database
```bash
cd backend
sqlite3 interview_platform.db
.tables
SELECT COUNT(*) FROM interview_sessions;
.quit
```

---

## 🎯 What Each App Does

### Support Person APK
- **Create** interview sessions
- **Get** 6-digit codes
- **Edit** documents
- **View** user connections
- **See** change history

### User APK
- **Join** with 6-digit code
- **Edit** transparent document
- **See** live updates
- **Customize** appearance
- **Disconnect** from session

### Admin APK
- **Monitor** all sessions
- **Track** users in real-time
- **View** document changes
- **See** connection history
- **Dashboard** with statistics

### Backend Server
- **Verify** session codes
- **Manage** documents
- **Sync** changes (ms-level)
- **Track** connections
- **Persist** data

---

## 📊 Terminal Layout

```
┌─────────────────────┬─────────────────────┬─────────────────────┐
│   Terminal 1        │   Terminal 2        │   Terminal 3        │
│   Backend Server    │   API Tests         │   Support Person    │
│                     │   + Integration     │   APK              │
│   python server.py  │   Tests             │                     │
│                     │                     │   python main.py    │
│   KEEP RUNNING!     │   Run then close    │   Interactive       │
└─────────────────────┴─────────────────────┴─────────────────────┘

┌─────────────────────┬─────────────────────┬─────────────────────┐
│   Terminal 4        │   Terminal 5        │   Terminal 6        │
│   User APK          │   Admin APK         │   Optional          │
│                     │                     │                     │
│   python main.py    │   python main.py    │   For notes/debug   │
│                     │                     │                     │
│   Interactive       │   Interactive       │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
```

---

## ⚡ Testing Workflow

### Minute 0-2: Setup
```
pip install -r requirements.txt
```

### Minute 2-2.5: Database
```
cd backend
python server.py
```

### Minute 2.5-4.5: Tests
```
cd tests
python test_api.py
python integration_test.py
```

### Minute 4.5-5: Apps Running
```
Terminal 3: python support_person_app/main.py
Terminal 4: python user_app/main.py
Terminal 5: python admin_app/main.py
```

### Minute 5+: Manual Testing
- Support creates session
- User joins
- Both edit
- Admin monitors

---

## ✅ Success Indicators

| Check | Status | What It Means |
|-------|--------|--------------|
| Backend logs | ✓ Running | Server is ready |
| API tests | ✓ 8/8 pass | Backend working |
| Integration tests | ✓ 12/12 pass | Full system working |
| Support app | ✓ Opens | UI framework OK |
| User app | ✓ Opens | UI framework OK |
| Admin app | ✓ Opens | UI framework OK |
| Code join | ✓ Works | WebSocket working |
| Real-time sync | ✓ <50ms | Communication OK |
| Admin dashboard | ✓ Updates | Monitoring working |

---

## 🔴 Quick Fixes

| Problem | Solution |
|---------|----------|
| Port 5000 in use | `taskkill /PID <PID> /F` |
| Modules not found | `pip install -r requirements.txt` |
| Database error | `del backend/interview_platform.db` then restart |
| No connection | Check firewall, restart backend |
| Slow sync | Normal for first test, should be <50ms |

---

## 📈 Performance Checklist

- [ ] Document sync: <50ms
- [ ] Connection: <1 second
- [ ] Database: ~10MB
- [ ] Memory per app: ~50MB
- [ ] Total system: ~300MB
- [ ] CPU: Minimal (unless typing fast)
- [ ] Network: localhost only during testing

---

## 🎓 Understanding the Flow

```
1. User enters code ABC123
   ↓
2. Backend verifies: SELECT * FROM interview_sessions WHERE code='ABC123'
   ↓
3. Backend returns session_id and document_id
   ↓
4. User connects via WebSocket
   ↓
5. Backend sends current document state (sync_response)
   ↓
6. User sees document and can edit
   ↓
7. User types text → WebSocket event → Backend records → Broadcasts to all users
   ↓
8. All users see update instantly (<50ms)
   ↓
9. Admin sees real-time dashboard updates
   ↓
10. All changes saved to database permanently
```

---

## 🗂️ File Organization

```
my_project/
├── backend/server.py          ← Backend engine
├── user_app/main.py           ← User interface
├── support_person_app/main.py ← Support interface
├── admin_app/main.py          ← Admin interface
├── tests/                      ← Automated tests
└── requirements.txt           ← Dependencies
```

---

## 📱 What You'll See

### Support Person App
```
┌─────────────────────────────────┐
│  Interview Support              │
├─────────────────────────────────┤
│                                 │
│  [Create New Session]           │
│  [View Active Sessions]         │
│                                 │
│  Code: ABC123                   │
│  Users: 1                       │
│  [Document editing area]        │
│                                 │
│  [Settings] [Exit]              │
└─────────────────────────────────┘
```

### User App
```
┌─────────────────────────────────┐
│  Interview Session              │
├─────────────────────────────────┤
│                                 │
│  Enter the 6-digit code         │
│  [ABC123        ]               │
│  [Join Session]                 │
│                                 │
│  Status: Connected              │
│  [Transparent document]         │
│                                 │
│  [Settings] [Exit]              │
└─────────────────────────────────┘
```

### Admin App
```
┌─────────────────────────────────┐
│  Admin Dashboard                │
├─────────────────────────────────┤
│  [Refresh Sessions]             │
│                                 │
│  Session: ABC123                │
│  Status: Active                 │
│  Users: 2                       │
│  [View Documents]               │
│                                 │
│  [View more sessions...]        │
└─────────────────────────────────┘
```

---

## 🎯 Test Outcomes

### All Tests Pass ✓
→ System is working perfectly
→ Ready for production deployment
→ Follow DEPLOYMENT.md

### Some Tests Fail ✗
→ Check error messages
→ Review TESTING_GUIDE.md troubleshooting
→ Try resetting database
→ Restart backend

### Apps Don't Open ✗
→ Check if dependencies installed
→ Check Python version (3.10+)
→ Try running from command line to see errors
→ Check for Kivy/graphics issues

---

## ⏰ Time Breakdown

| Task | Time |
|------|------|
| Install deps | 2 min |
| Start backend | 30 sec |
| Run API tests | 2 min |
| Run integration tests | 3 min |
| Start 3 apps | 1 min |
| Manual workflow test | 5 min |
| **TOTAL** | **~15 min** |

---

## 💡 Pro Tips

✨ **Tip 1:** Keep Terminal 1 (backend) running the whole time
✨ **Tip 2:** Changes sync instantly - watch the real-time updates
✨ **Tip 3:** Admin dashboard refreshes automatically
✨ **Tip 4:** Database persists - even after closing apps
✨ **Tip 5:** 6-digit code changes each session - use the new one

---

## 📞 If Something Goes Wrong

1. **Read errors carefully** - They tell you exactly what's wrong
2. **Check TESTING_GUIDE.md** - Troubleshooting section
3. **Reset database** - `del backend/interview_platform.db`
4. **Restart backend** - Sometimes just works
5. **Check dependencies** - `pip install -r requirements.txt` again
6. **Check port 5000** - Not blocked by firewall

---

## 🚀 You're Ready!

**Go to Terminal 1 and run:**
```bash
cd C:\Users\dell\Desktop\my_project\backend
python server.py
```

**Then follow the steps above!**

---

*For detailed information, see TESTING_GUIDE.md*
