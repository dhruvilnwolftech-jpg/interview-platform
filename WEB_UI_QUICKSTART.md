# Web UI Quick Start

Your complete web interface is ready! Here's how to use it:

---

## 🚀 Open Now

### Option A: From Your Computer
```bash
# Navigate to the folder
cd C:\Users\dell\Desktop\my_project\web_ui

# Open in browser (Windows)
start index.html

# Or macOS
open index.html

# Or Linux
xdg-open index.html
```

### Option B: Deploy Online
See `DEPLOY_WEB_UI.md` for deployment options

---

## 📱 What You Can Do

### 1️⃣ Join an Interview (Candidate)
**Tab: Candidate**

1. Get a session code from support person
2. Enter the code in "Session Code" field
3. Click "Join Session"
4. View session details
5. Click "View Document" to see shared content

**Example:**
- Code: `ABC123`
- You see: Session ID, Document ID, Support Person contact

---

### 2️⃣ Create Interview Session (Support Person)
**Tab: Support Person**

1. Enter your ID (e.g., `sp-001`, `support-jane`)
2. Click "Create Session"
3. System generates a unique 6-character code
4. Code is auto-copied to clipboard
5. Share code with candidate
6. Click "Create Another Session" to continue

**Example:**
- You enter: `sp-john`
- System creates: Code `XYZ789`
- You share: `XYZ789` with candidate
- System shows: Session ID, Document ID

---

### 3️⃣ Monitor Everything (Admin)
**Tab: Admin**

1. Click "Load Sessions"
2. See all active sessions with:
   - Session codes
   - Support person name
   - When created
   - Number of documents
   - Active connections
3. Click any session to view details
4. Monitor statistics in real-time

**What you see:**
- Total sessions created
- Active right now
- Total documents
- List of all sessions

---

## 🎯 Real-World Workflow

### Scenario: Conduct an Interview

**Step 1: Support Person Creates Session**
1. Support person logs into web UI
2. Switches to "Support Person" tab
3. Enters their ID: `sp-support-team`
4. Clicks "Create Session"
5. Gets code: `ABC123`
6. Sends code to candidate via email/SMS

**Step 2: Candidate Joins**
1. Candidate receives code: `ABC123`
2. Opens web UI
3. Switches to "Candidate" tab
4. Enters code: `ABC123`
5. Clicks "Join Session"
6. Confirms they're connected
7. Can now see shared documents

**Step 3: Admin Monitors**
1. Admin opens web UI
2. Switches to "Admin" tab
3. Clicks "Load Sessions"
4. Sees active session with code `ABC123`
5. Sees 1 active connection (candidate)
6. Can track all activity

---

## 🎨 Interface Features

### Navigation
- Top bar with 3 tabs: Candidate | Support | Admin
- Click to switch between views
- Current tab is highlighted

### Session Code Display
- Large, bold display
- Easy to read and copy
- One-click copy button

### Session Details
- Session ID (unique identifier)
- Document ID (for tracking)
- Support Person ID (who created it)
- Creation timestamp
- Active connection count

### Document Viewer
- View content shared during interview
- See when document was created
- Check when it was last updated
- View change count/history
- Clean, readable formatting

### Admin Statistics
- Real-time dashboard
- Total sessions count
- Active sessions right now
- Total documents managed
- Session list with filtering

---

## 💡 Tips & Tricks

### Copy Session Code Easily
```
Support Person view
↓
Click "Copy" button next to code
↓
Paste anywhere (email, chat, etc.)
```

### Find Old Sessions
```
Admin view
↓
Click "Load Sessions"
↓
Scroll through list
↓
Look for date/time created
```

### Troubleshoot Connection
```
Any view
↓
Look for green "Connected to backend!" toast
↓
If not showing: Check internet connection
↓
If still failing: Wait 30 seconds and refresh
```

### Share Code Formats
```
Text message:
"Your interview code: ABC123"

Email:
"Please enter code ABC123 at https://your-platform.com"

Chat:
Code: ABC123
Link: https://your-platform.com
```

---

## 🔒 Security Notes

This is a demo interface. Before using in production:

1. **Add Login** - Require password/authentication
2. **Protect Admin** - Only admins can see all sessions
3. **Verify Codes** - Codes should expire after use
4. **SSL/HTTPS** - Already enabled (✅ on Render)
5. **Input Validation** - Check all user inputs
6. **Rate Limiting** - Prevent abuse

---

## 🆘 Troubleshooting

### "Connected to backend!" doesn't appear
**Problem:** Can't reach your backend
**Solutions:**
1. Check internet connection
2. Refresh page (Ctrl+R or Cmd+R)
3. Check if backend is running
4. Wait 30 seconds and try again

### Can't join session
**Problem:** Session code not working
**Solutions:**
1. Check code is correct (case doesn't matter)
2. Make sure support person created session
3. Confirm session is still active
4. Try creating a new session

### Buttons don't respond
**Problem:** UI not responding to clicks
**Solutions:**
1. Refresh page
2. Try different browser
3. Clear browser cache
4. Check browser console (F12) for errors

### No error messages showing
**Problem:** Something failed silently
**Solutions:**
1. Open browser console (F12)
2. Look for red error messages
3. Check network tab (are API calls working?)
4. Try in Incognito mode

---

## 📊 What Happens Behind the Scenes

```
Web UI (your browser)
        ↓
  Makes API calls
        ↓
Backend (https://interview-platform-bdot.onrender.com)
        ↓
Database (SQLite)
        ↓
Stores: Sessions, Documents, History, Connections
```

**When you create a session:**
1. Web UI sends: `POST /api/sessions` with support person ID
2. Backend creates: New session record with unique code
3. Backend returns: Session ID, Document ID, Code
4. Web UI displays: Code and session info
5. Database stores: Everything for later access

**When you join:**
1. Web UI sends: `GET /api/sessions/ABC123`
2. Backend finds: Session with that code
3. Backend returns: Session details and document ID
4. Web UI displays: All details
5. Database tracks: You joined (connection record)

---

## 🚀 Next Steps

1. **Test it now:**
   ```
   Open index.html in browser
   ↓
   Switch to Support Person tab
   ↓
   Create a session
   ↓
   Copy the code
   ↓
   Switch to Candidate tab
   ↓
   Paste and join
   ↓
   Switch to Admin and see it live!
   ```

2. **Deploy online:** See `DEPLOY_WEB_UI.md`

3. **Customize:** Edit `styles.css` to change colors/fonts

4. **Add features:** Edit `app.js` to add new functionality

---

## 📞 Support

**Need help?**

1. Check browser console (F12) for errors
2. Verify backend is running
3. Try the troubleshooting section above
4. Check `API_TESTING.md` for manual API tests
5. Review `web_ui/README.md` for developer docs

**Common Issues:**

| Problem | Solution |
|---------|----------|
| Can't see "Connected!" | Refresh page, check internet |
| Session code not working | Check code is exact, session active |
| Buttons don't respond | Refresh, clear cache, try Chrome |
| Page looks broken | Hard refresh: Ctrl+Shift+R |
| No data showing | Wait for API response, check network tab |

---

**You're ready to go! 🎉**

Open the web UI now and try all three roles:
1. ✅ Create session (Support)
2. ✅ Join session (Candidate)
3. ✅ Monitor session (Admin)
