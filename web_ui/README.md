# Interview Platform Web UI

A modern, responsive web interface for the Interview Platform backend.

## Features

### 👨‍💼 Candidate Interface
- Join sessions with a 6-character code
- View session details
- Access shared documents
- Simple, intuitive UI

### 👥 Support Person Dashboard
- Create new interview sessions
- Generate unique session codes
- Monitor session details
- Quick session management

### 👨‍💻 Admin Dashboard
- View all active sessions
- Monitor connection counts
- Track document changes
- Real-time statistics

## Quick Start

### Option 1: Open Locally
1. Open `index.html` directly in your browser
2. No server required - it's a static web app
3. All data syncs with your live backend

### Option 2: Deploy to GitHub Pages
```bash
# Push to your GitHub repo
git add web_ui/
git commit -m "Add web UI"
git push origin main

# Go to GitHub → Settings → Pages → Deploy from main branch
# Your UI will be live at: https://yourusername.github.io/interview-platform/
```

### Option 3: Deploy to Render (with backend)
Create a static web server on Render:
1. Create new Web Service
2. Select your repository
3. Build: `echo "No build needed"`
4. Start: `python3 -m http.server 8000 --directory web_ui`
5. Your UI will be live

## Architecture

```
┌─────────────────────────────────────────┐
│      Web UI (HTML/CSS/JavaScript)       │
│  - Candidate Join                       │
│  - Support Create Session               │
│  - Admin Dashboard                      │
└─────────────────────────────────────────┘
                    ↕
          (REST API via fetch)
                    ↕
┌─────────────────────────────────────────┐
│      Backend (Flask + SQLAlchemy)       │
│  - Session Management                   │
│  - Document Storage                     │
│  - Change History                       │
│  - Connection Tracking                  │
└─────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────┐
│    Database (SQLite on Render)          │
│  - Sessions                             │
│  - Documents                            │
│  - Changes                              │
│  - Connections                          │
└─────────────────────────────────────────┘
```

## API Integration

The UI connects to your live backend at:
```
https://interview-platform-bdot.onrender.com/
```

### Endpoints Used

| Feature | Endpoint | Method |
|---------|----------|--------|
| Health Check | `/api/health` | GET |
| Create Session | `/api/sessions` | POST |
| Join Session | `/api/sessions/<code>` | GET |
| Get Document | `/api/admin/documents/<id>` | GET |
| List Sessions | `/api/admin/sessions` | GET |
| Get History | `/api/documents/<id>/history` | GET |

## Usage

### For Candidates
1. Click "Candidate" tab
2. Enter the 6-character session code
3. Click "Join Session"
4. View session details and documents

### For Support Staff
1. Click "Support Person" tab
2. Enter your ID (e.g., "sp-001")
3. Click "Create Session"
4. Share the generated code with the candidate
5. Code is automatically copied to clipboard

### For Admins
1. Click "Admin" tab
2. Click "Load Sessions"
3. View all active sessions and statistics
4. Click any session to view details

## Customization

### Change API URL
Edit `app.js` line 2:
```javascript
const API_BASE = 'https://your-new-url.onrender.com';
```

### Change Colors
Edit `styles.css` CSS variables (lines 5-13):
```css
:root {
    --primary: #0066cc;      /* Main color */
    --success: #28a745;      /* Success color */
    --danger: #dc3545;       /* Error color */
    /* ... etc */
}
```

### Add Custom Branding
Edit `index.html` line 7 (title) and line 42 (logo text):
```html
<title>Your Company - Interview Platform</title>
```

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Performance

- **No dependencies** - Pure JavaScript
- **Small bundle** - ~15KB combined
- **Fast loading** - Loads in <1 second
- **Responsive** - Works on all devices

## Security Notes

⚠️ This is a demo/development interface. For production:

1. **Add Authentication**
   - Implement JWT tokens
   - Add login page
   - Protect admin endpoints

2. **Add CORS Headers**
   - Configure on backend
   - Whitelist your domain

3. **Rate Limiting**
   - Prevent brute force session code guessing
   - Implement API rate limiting

4. **Input Validation**
   - Sanitize all inputs
   - Validate on both client and server

5. **HTTPS Only**
   - Already enabled on Render
   - Force HTTPS in production

## Troubleshooting

### "Connected to backend" message doesn't appear
- Check internet connection
- Verify backend URL in `app.js`
- Check Render service status
- Check browser console for CORS errors

### Can't join session
- Verify session code is correct (case-insensitive)
- Check if session is still active
- Confirm backend is running

### Modal not closing
- Try pressing Escape key
- Click outside the modal
- Check browser console for JavaScript errors

## Development

### File Structure
```
web_ui/
├── index.html       # Main UI structure
├── styles.css       # Styling and responsive design
├── app.js          # JavaScript logic and API calls
└── README.md       # This file
```

### Adding Features

1. Add UI element in `index.html`
2. Add styling in `styles.css`
3. Add JavaScript handler in `app.js`
4. Test with backend APIs

### Example: Add a feature
```html
<!-- In index.html -->
<button onclick="newFeature()">Click Me</button>

<!-- In app.js -->
async function newFeature() {
    const result = await makeRequest('/api/endpoint');
    if (result) {
        showToast('Success!', 'success');
    }
}
```

## Support

For issues or questions:
1. Check the API_TESTING.md for endpoint examples
2. Review backend server.py for available endpoints
3. Check browser console (F12) for errors
4. Verify backend is running and accessible

## License

Same as main project
