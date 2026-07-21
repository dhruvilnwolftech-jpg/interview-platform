# Complete Testing & Running Guide

## Prerequisites Check

Before starting, verify you have:

```bash
# Check Python version (should be 3.10+)
python --version

# Check pip
pip --version

# Check if port 5000 is available (Windows)
netstat -ano | findstr :5000
# If port is in use, kill the process:
taskkill /PID <PID> /F
```

---

## Step 1: Install Dependencies (2 minutes)

### Open Command Prompt/PowerShell

```bash
# Navigate to project directory
cd C:\Users\dell\Desktop\my_project

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# On Windows CMD:
.\venv\Scripts\activate.bat

# Install all dependencies
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed flask-2.3.3 flask-socketio-5.3.4 ...
```

---

## Step 2: Verify Database Setup (1 minute)

```bash
# Navigate to backend
cd backend

# Initialize database
python -c "
from server import app, db
with app.app_context():
    db.create_all()
print('✓ Database initialized successfully!')
"
```

**Expected output:**
```
✓ Database initialized successfully!
```

**What was created:**
- `interview_platform.db` - SQLite database with 4 tables

---

## Step 3: Start Backend Server (Keep running)

### Terminal 1: Backend Server

```bash
# Navigate to backend directory
cd C:\Users\dell\Desktop\my_project\backend

# Start the server
python server.py
```

**Expected output:**
```
Starting Interview Platform Backend Server...
Server running on http://localhost:5000
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

✅ **Keep this terminal open while testing!**

---

## Step 4: Test Backend API (New Terminal)

### Terminal 2: API Testing

```bash
# Navigate to tests directory
cd C:\Users\dell\Desktop\my_project\tests

# Run API tests
python test_api.py
```

**Expected output:**
```
=== Testing Health Endpoint ===
✓ Health check passed

=== Testing Session Creation ===
✓ Session created
  Session ID: [uuid]
  Document ID: [uuid]
  Session Code: ABC123

[... more tests ...]

RESULTS: 8 passed, 0 failed
```

✅ **All 8 API tests should pass**

---

## Step 5: Create Test Session (Quick API Call)

### Terminal 2 (same terminal as Step 4)

```bash
# Create a session and note the code
curl -X POST http://localhost:5000/api/sessions ^
  -H "Content-Type: application/json" ^
  -d "{\"support_person_id\": \"sp-001\"}"
```

**Expected output:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "ABC123",
  "document_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
  "created_at": "2024-01-01T12:00:00"
}
```

📝 **Save this code for Step 9!**

---

## Step 6: Run Integration Tests (New Terminal)

### Terminal 3: Integration Testing

```bash
# Navigate to tests directory
cd C:\Users\dell\Desktop\my_project\tests

# Run integration tests
python integration_test.py
```

**Expected output:**
```
============================================================
        INTERVIEW PLATFORM - INTEGRATION TEST SUITE
============================================================

TEST 1: Create Interview Session
✓ Session created successfully

TEST 2: Verify Session Code
✓ Session verified successfully

[... more tests ...]

TEST 12: Cleanup
✓ All clients disconnected

RESULTS: 12 passed, 0 failed
```

✅ **All 12 integration tests should pass**

---

## Step 7: Run Support Person APK (New Terminal)

### Terminal 4: Support Person Interface

```bash
# Navigate to support person app
cd C:\Users\dell\Desktop\my_project\support_person_app

# Run the application
python main.py
```

**Expected:**
- Window opens with "Interview Support" title
- "Create New Session" and "View Sessions" buttons visible
- Click "Create New Session"
- Wait for session to be created
- **Note the 6-digit code displayed** (e.g., ABC123)

---

## Step 8: Run User APK (New Terminal)

### Terminal 5: User Interface

```bash
# Navigate to user app
cd C:\Users\dell\Desktop\my_project\user_app

# Run the application
python main.py
```

**Expected:**
- Window opens with "Interview Session" title
- Code input field visible
- Instructions: "Enter the 6-digit code provided by the interview support person"

---

## Step 9: Test User Joins Session

### In User APK window (from Step 8):

1. **Enter the code** from Step 7 (e.g., ABC123)
2. **Click "Join Session"**
3. **Wait 2-3 seconds** for connection
4. **Status changes to** "Connected as User"
5. **Transparent document appears**

**What's happening:**
- User verifies code with backend
- WebSocket connection established
- Document state synced from server
- Ready for editing

---

## Step 10: Run Admin APK (New Terminal)

### Terminal 6: Admin Interface

```bash
# Navigate to admin app
cd C:\Users\dell\Desktop\my_project\admin_app

# Run the application
python main.py
```

**Expected:**
- Window opens with "Admin Dashboard" title
- "Refresh Sessions" button visible
- Click "Refresh Sessions"
- Your session should appear with details

---

## Step 11: Complete Workflow Test

### Now you have all three interfaces running!

#### Test Real-Time Sync:

**In Support Person APK:**
1. Type: "Hello from Support"
2. **Immediately** in User APK, same text appears
3. ✅ Real-time sync working!

**In User APK:**
1. Type: "Response from User"
2. **Immediately** in Support Person APK, text updates
3. ✅ Bidirectional sync working!

**In Admin APK:**
1. Click "Refresh Sessions"
2. See session with "Users: 2" (updated in real-time)
3. ✅ Admin monitoring working!

#### Test Document Customization:

**In Support Person APK:**
1. Click "Settings"
2. Change Font Size to 18
3. Change Background Color to #FFFF00 (yellow)
4. Change Font Color to #000000 (black)
5. Click "Apply"
6. ✅ **In both apps**, document appearance updates instantly!

#### Test Connection Tracking:

**In User APK:**
1. Click "Exit"
2. **In Support Person APK**, connection count updates
3. **In Admin APK**, user count decreases
4. ✅ Connection tracking working!

---

## Step 12: Advanced Testing

### Test Change History:

**In Support Person APK:**
1. Click "Settings"
2. Click "View History"
3. See all document changes with timestamps
4. ✅ History tracking working!

### Test Admin Monitoring:

**In Admin APK:**
1. Click "Refresh Sessions"
2. Click "View Documents" on your session
3. See all connected users
4. See connection times
5. ✅ Admin features working!

---

## Complete Testing Checklist

### ✅ Phase 1: Setup & Backend
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database created (`interview_platform.db` exists)
- [ ] Backend server running (Terminal 1 showing logs)
- [ ] All API tests passing (8/8)
- [ ] All integration tests passing (12/12)

### ✅ Phase 2: Frontend Applications
- [ ] Support Person APK running (Terminal 4)
- [ ] User APK running (Terminal 5)
- [ ] Admin APK running (Terminal 6)
- [ ] All windows display without errors

### ✅ Phase 3: Functionality
- [ ] Support person creates session
- [ ] User joins with 6-digit code
- [ ] Real-time sync: Support → User
- [ ] Real-time sync: User → Support
- [ ] Document customization works
- [ ] Styles sync to all users
- [ ] Admin dashboard shows session
- [ ] Admin dashboard shows user count

### ✅ Phase 4: Advanced Features
- [ ] User disconnect tracked
- [ ] Admin sees disconnection
- [ ] Change history available
- [ ] Multiple style changes sync
- [ ] Connection count updates real-time

---

## Expected Results Summary

```
BACKEND:
  ✓ Server running on http://localhost:5000
  ✓ Database: interview_platform.db created
  ✓ 8 API tests passing
  ✓ 12 integration tests passing

USER INTERFACE:
  ✓ Support Person APK: Session creation working
  ✓ User APK: Code entry and join working
  ✓ Admin APK: Dashboard and monitoring working

REAL-TIME SYNC:
  ✓ Document changes: <50ms latency
  ✓ Bidirectional editing: Working
  ✓ Style changes: Syncing to all users
  ✓ Connection tracking: Real-time updates

FEATURES:
  ✓ Transparent document: Visible to user
  ✓ Customization: Colors, fonts, opacity working
  ✓ History: All changes tracked
  ✓ Admin monitoring: Live dashboard updating
```

---

## Troubleshooting

### Issue: Port 5000 Already in Use

```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process
taskkill /PID <PID> /F

# Try again
python server.py
```

### Issue: Dependencies Not Installing

```bash
# Update pip
python -m pip install --upgrade pip

# Try again
pip install -r requirements.txt
```

### Issue: Database Errors

```bash
# Delete old database
cd backend
del interview_platform.db

# Reinitialize
python -c "from server import app, db; app.app_context().push(); db.create_all()"
```

### Issue: WebSocket Connection Failed

**Check:**
1. Backend server is running (Terminal 1)
2. Port 5000 is accessible
3. Firewall is not blocking
4. Try connecting again (may take 5 seconds)

### Issue: APK Windows Won't Open

```bash
# Check if dependencies are installed
pip install -r requirements.txt

# Try running again with explicit error output
python -u main.py
```

---

## Testing Duration Guide

| Phase | Task | Time |
|-------|------|------|
| 1 | Install dependencies | 2 min |
| 2 | Setup database | 1 min |
| 3 | Start backend | 30 sec |
| 4 | Run API tests | 2 min |
| 5 | Create test session | 30 sec |
| 6 | Run integration tests | 3 min |
| 7 | Run Support APK | 30 sec |
| 8 | Run User APK | 30 sec |
| 9 | User joins | 2 min |
| 10 | Run Admin APK | 30 sec |
| 11 | Workflow test | 5 min |
| 12 | Advanced features | 5 min |
| **TOTAL** | **Complete test** | **~25 minutes** |

---

## What Each Terminal Does

```
Terminal 1: Backend Server
  → python server.py
  → Keeps running, shows logs
  → LEAVE RUNNING during all tests

Terminal 2: API Testing
  → python test_api.py
  → Runs 8 tests
  → Can close after tests complete

Terminal 3: Integration Testing
  → python integration_test.py
  → Runs 12 tests
  → Can close after tests complete

Terminal 4: Support Person APK
  → python main.py (support_person_app)
  → Interactive window
  → Leave running for workflow test

Terminal 5: User APK
  → python main.py (user_app)
  → Interactive window
  → Leave running for workflow test

Terminal 6: Admin APK
  → python main.py (admin_app)
  → Interactive window
  → Leave running for monitoring
```

---

## Success Criteria

### ✅ Test is SUCCESSFUL if:

1. ✓ All 8 API tests pass
2. ✓ All 12 integration tests pass
3. ✓ All 3 APK windows open without errors
4. ✓ User can join session with code
5. ✓ Real-time sync works (text appears instantly)
6. ✓ Admin dashboard shows active users
7. ✓ Document customization syncs across users
8. ✓ Change history is preserved
9. ✓ No Python errors in console
10. ✓ Database file is created and populated

### ✅ Performance Metrics:

- Document sync latency: <50ms ✓
- Connection setup: <1 second ✓
- API response: <500ms ✓
- All tests complete in: <10 minutes ✓

---

## Quick Start (Copy-Paste Friendly)

### Session 1 - Backend & Tests

```bash
cd C:\Users\dell\Desktop\my_project
pip install -r requirements.txt
cd backend
python -c "from server import app, db; app.app_context().push(); db.create_all(); print('DB OK')"
python server.py
```

### Session 2 - Run Tests (in new terminal)

```bash
cd C:\Users\dell\Desktop\my_project\tests
python test_api.py
```

### Session 3 - Integration Tests (in new terminal)

```bash
cd C:\Users\dell\Desktop\my_project\tests
python integration_test.py
```

### Session 4 - Support Person App (in new terminal)

```bash
cd C:\Users\dell\Desktop\my_project\support_person_app
python main.py
```

### Session 5 - User App (in new terminal)

```bash
cd C:\Users\dell\Desktop\my_project\user_app
python main.py
```

### Session 6 - Admin App (in new terminal)

```bash
cd C:\Users\dell\Desktop\my_project\admin_app
python main.py
```

---

## Next Steps After Testing

### If tests pass ✓
1. Review ARCHITECTURE.md to understand the system
2. Read FEATURES.md to see all capabilities
3. Follow DEPLOYMENT.md to deploy to production

### If tests fail ✗
1. Check error messages in terminal output
2. Review troubleshooting section above
3. Verify all dependencies installed
4. Check if port 5000 is free
5. Try running tests again

---

## Video Walkthrough (What You'll See)

1. **Backend starts** - Terminal shows "Server running on http://localhost:5000"
2. **Tests run** - Green checkmarks appear as each test passes
3. **Support Person app opens** - Window with "Create New Session" button
4. **User app opens** - Window with code input field
5. **User enters code** - Real-time connection established
6. **Both edit document** - Changes appear instantly in both windows
7. **Admin app shows session** - Dashboard displays active users
8. **Changes sync** - All 3 apps update in real-time

---

## Important Notes

⚠️ **Keep Terminal 1 open** - Backend must keep running
⚠️ **Wait 2-3 seconds** - WebSocket connection takes time
⚠️ **Check firewall** - Port 5000 must not be blocked
✅ **Multiple databases** - Each test creates fresh session
✅ **Data persists** - Database remains after tests complete

---

## Still Having Issues?

1. **Read**: `QUICKSTART.md` - Additional setup help
2. **Check**: `README.md` - Troubleshooting section
3. **Review**: `ARCHITECTURE.md` - System understanding
4. **See**: `DEPLOYMENT.md` - Different environment setup

---

**You're now ready to test the entire platform! 🚀**

Start with Terminal 1 (Backend), then follow the steps in order.
