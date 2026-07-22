# Deploy Web UI - 3 Options

Your web UI is ready! Here are three ways to deploy it:

---

## Option 1: GitHub Pages (EASIEST - 5 minutes) ⭐

Your web UI is already in GitHub. Publish it as a static site:

### Steps:
1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Build and deployment":
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/ (root)`
4. Click **Save**
5. Wait 2-3 minutes for GitHub to build
6. Your UI will be live at:
   ```
   https://yourusername.github.io/interview-platform/
   ```

✅ **Pros:**
- Free
- Automatic updates when you push
- Fast CDN worldwide
- No server management

❌ **Cons:**
- Can only serve static files
- URL is GitHub subdomain (unless you add custom domain)

---

## Option 2: Render Static Site (5 minutes)

Deploy alongside your backend on Render:

### Steps:
1. In your existing Render Web Service (backend):
   - Settings → Redirects
   - Add: `/* -> /index.html` (for SPA routing)

2. Update your Render build command:
   ```
   pip install -r requirements_deploy.txt
   ```

3. Update your start command:
   ```
   gunicorn -w 1 --bind 0.0.0.0:$PORT backend.server:app
   ```

4. Create a new Static Site:
   - Go to Render Dashboard
   - Click "New +" → "Static Site"
   - Connect your GitHub repo
   - Root directory: `web_ui`
   - Click Deploy

5. Your UI will be live at:
   ```
   https://your-app.onrender.com
   ```

✅ **Pros:**
- Same server as backend (simpler)
- All-in-one solution
- Custom domain easy
- Professional URL

❌ **Cons:**
- Need to manage both UI and backend on same service
- Slightly more complex setup

---

## Option 3: Netlify (RECOMMENDED for Static Sites)

Fast, simple deployment for frontend:

### Steps:
1. Go to [Netlify.com](https://netlify.com)
2. Click "Sign up with GitHub"
3. Select your `interview-platform` repository
4. Configure:
   - Base directory: `web_ui`
   - Build command: (leave empty - it's just static files)
   - Publish directory: `web_ui`
5. Click "Deploy"
6. Your UI will be live at:
   ```
   https://your-site-name.netlify.app
   ```

✅ **Pros:**
- Incredibly fast
- Easy custom domain
- Free SSL
- Built-in analytics
- Preview deployments
- One-click rollbacks

❌ **Cons:**
- Another service to manage
- Needs separate account

---

## Recommended Setup

**Best Overall:**
```
Web UI → Netlify (fast, optimized for static sites)
Backend → Render (powerful, handles all APIs)
Database → SQLite on Render (included)
```

**All-in-One:**
```
Web UI + Backend → Render on same service
Database → SQLite on Render (included)
```

**Most Professional:**
```
Web UI → GitHub Pages (free, integrated)
Backend → Render (scalable)
Database → PostgreSQL on Render (upgrade from SQLite)
```

---

## Test Your Web UI

Once deployed, test it:

### 1. Test Connection
```bash
# Visit your UI URL
https://your-deployed-url/
```
You should see "Connected to backend!" message

### 2. Create a Session (Support Person tab)
- Enter: `sp-001`
- Click Create Session
- Copy the session code

### 3. Join Session (Candidate tab)
- Paste the session code
- Click Join Session
- Confirm you can see session details

### 4. View Admin Dashboard (Admin tab)
- Click Load Sessions
- Confirm you see the session you created

---

## Connect Frontend to Backend

If you deployed to a different domain, update the API URL:

### In `web_ui/app.js` (line 2):
```javascript
// Change this:
const API_BASE = 'https://interview-platform-bdot.onrender.com';

// To your actual backend URL:
const API_BASE = 'https://your-backend-url.onrender.com';
```

Then redeploy the web UI.

---

## Add Custom Domain

### On Netlify:
1. Domain Management → Connect custom domain
2. Add CNAME record to your domain registrar
3. Wait 10-30 minutes for DNS propagation

### On Render:
1. Settings → Custom Domain
2. Add your domain
3. Add CNAME record to registrar
4. Wait 10-30 minutes

### On GitHub Pages:
1. Settings → Pages
2. Add custom domain
3. Add CNAME record to registrar
4. Wait 10-30 minutes

---

## Monitor Your Deployment

### Check Status:
- **Netlify:** Dashboard → Deploys
- **Render:** Dashboard → Your Service
- **GitHub Pages:** Repository → Actions

### View Logs:
- **Netlify:** Logs in deployment details
- **Render:** Service Logs tab
- **GitHub Pages:** Check GitHub Actions

### Test APIs:
```bash
# Health check
curl https://interview-platform-bdot.onrender.com/api/health

# Create session
curl -X POST https://interview-platform-bdot.onrender.com/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"support_person_id":"sp-001"}'
```

---

## Production Checklist

- [ ] Web UI deployed and accessible
- [ ] Backend API working
- [ ] Can create sessions
- [ ] Can join sessions
- [ ] Can view documents
- [ ] Admin dashboard loads
- [ ] All 3 tabs working
- [ ] Tested on mobile
- [ ] Custom domain configured (optional)
- [ ] Error messages display correctly

---

## Troubleshooting

### "Can't connect to backend"
1. Check API_BASE URL in `web_ui/app.js`
2. Verify backend is running: `curl https://interview-platform-bdot.onrender.com/api/health`
3. Check for CORS errors in browser console (F12)

### "Session code not working"
1. Confirm support person created the session successfully
2. Check code is entered correctly (uppercase)
3. Verify session is still active (admin dashboard)

### "Styles not loading"
1. Check `styles.css` file exists in deployed folder
2. Try hard refresh (Ctrl+Shift+R)
3. Check browser console for 404 errors

### "Buttons not responding"
1. Check `app.js` file exists
2. Open browser console (F12)
3. Check for JavaScript errors
4. Try in different browser

---

## Next Steps

1. ✅ Deploy Web UI
2. ✅ Test all three roles
3. 🔄 Customize styling (colors, logo, fonts)
4. 🔄 Add your branding
5. 🔄 Build mobile apps (iOS/Android)
6. 🔄 Add real-time WebSocket support
7. 🔄 Implement authentication

---

**Your platform is production-ready! 🚀**

Backend: https://interview-platform-bdot.onrender.com/
Web UI: (Choose deployment option above)
