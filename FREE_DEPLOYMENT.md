# Free Deployment Guide - Render.com + Your Domain

## Complete Step-by-Step Instructions

### Prerequisites
- ✅ Domain purchased (you have this)
- ✅ GitHub account (free)
- ✅ Render.com account (free)

---

## Phase 1: Prepare Your Code (10 minutes)

### Step 1.1: Create `Procfile`
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT backend.server:app
```

### Step 1.2: Create `runtime.txt`
```
python-3.10.12
```

### Step 1.3: Update `requirements_minimal.txt`
```
flask==2.3.3
flask-socketio==5.3.4
python-socketio==5.9.0
python-engineio==4.7.1
websocket-client==10.4
flask-sqlalchemy==3.0.5
sqlalchemy==1.4.48
python-dotenv==1.0.0
requests==2.31.0
gunicorn==20.1.0
eventlet==0.33.3
```

### Step 1.4: Create `.gitignore`
```
venv/
__pycache__/
*.pyc
.env
*.db
.DS_Store
```

---

## Phase 2: Push to GitHub (10 minutes)

### Step 2.1: Create GitHub Account
1. Go to https://github.com
2. Click "Sign up"
3. Create account with email

### Step 2.2: Create Repository
1. Click "+" → "New repository"
2. Name: `interview-platform`
3. Make it **Public**
4. Click "Create repository"

### Step 2.3: Push Code
```powershell
cd C:\Users\dell\Desktop\my_project

git init
git add .
git commit -m "Initial commit - Interview Platform"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/interview-platform.git
git push -u origin main
```

**Replace YOUR_USERNAME with your GitHub username**

---

## Phase 3: Deploy on Render.com (5 minutes)

### Step 3.1: Create Render Account
1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub

### Step 3.2: Deploy Service
1. **In Render Dashboard** → Click "New +"
2. **Select** "Web Service"
3. **Connect GitHub**
   - Authorize Render to access GitHub
   - Select your repository
4. **Configure:**
   - Service Name: `interview-platform`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements_minimal.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT backend.server:app`
5. **Click** "Create Web Service"

**Wait 2-3 minutes...**

### Step 3.3: Get Your Render URL
- Copy the URL from Render dashboard (e.g., `interview-platform-xyz.onrender.com`)

---

## Phase 4: Connect Your Domain (10 minutes)

### Step 4.1: Add Custom Domain in Render
1. **In Render Dashboard** → Your Service
2. **Go to** "Settings"
3. **Find** "Custom Domain"
4. **Enter your domain** (e.g., `yourdomain.com`)
5. **Click** "Add"
6. **Render shows you** the CNAME value

### Step 4.2: Update DNS at Your Registrar
Example for GoDaddy:

1. **Login to your domain registrar**
2. **Go to** DNS Settings
3. **Add/Update CNAME Record:**
   - **Type:** CNAME
   - **Name:** @ (or subdomain like "interview")
   - **Value:** [Copy from Render]
   - **TTL:** 3600
4. **Save**

**Wait 15-30 minutes for DNS propagation**

---

## Phase 5: Test Deployment (5 minutes)

### Test 1: Health Check
```bash
curl https://yourdomain.com/api/health
```

Expected response:
```json
{"status": "ok", "timestamp": "..."}
```

### Test 2: Welcome
```bash
curl https://yourdomain.com/
```

### Test 3: Create Session
```bash
curl -X POST https://yourdomain.com/api/sessions \
  -H "Content-Type: application/json" \
  -d "{\"support_person_id\": \"sp-001\"}"
```

Expected response:
```json
{
  "session_id": "...",
  "code": "ABC123",
  "document_id": "...",
  "created_at": "..."
}
```

---

## Troubleshooting

### Problem: "Build Failed"
**Solution:**
1. Check `requirements_minimal.txt` has no version conflicts
2. Ensure `Procfile` is correct
3. Check `runtime.txt` has Python 3.10

### Problem: Domain Not Working
**Solution:**
1. Wait 30 minutes for DNS propagation
2. Check CNAME record is correct at registrar
3. Verify domain in Render settings

### Problem: WebSocket Not Working
**Solution:**
1. Ensure using `eventlet` worker (in Procfile)
2. Check websocket-client is installed
3. Use `wss://` for HTTPS connections

---

## Monitoring Your Deployment

### View Logs
- **In Render Dashboard** → Your Service → "Logs"

### Restart Service
- **In Render Dashboard** → Your Service → "Settings" → "Restart"

### Update Code
1. Make changes locally
2. Git push to GitHub
3. Render auto-deploys

---

## Free Tier Limitations

✅ **Included:**
- Python 3.10
- 0.5 CPU cores
- 512 MB RAM
- SQLite database
- Custom domain
- SSL certificate (free)

⚠️ **Limitations:**
- Free tier spins down after 15 min inactivity
- 5 concurrent connections
- 10 GB storage
- Not for high-traffic production

**Upgrade to paid:** $7/month for production use

---

## Cost Breakdown

| Item | Cost |
|------|------|
| Render.com Free Tier | **FREE** |
| Your Domain | ~$10/year (you have it) |
| SSL Certificate | **FREE** (Render provides) |
| Database (SQLite) | **FREE** |
| **Total** | **FREE** |

---

## Next Steps After Deployment

1. **Update Client Code**
   - Change API URL from `localhost:5000` to `https://yourdomain.com`

2. **Build Web UI** (Optional)
   - Create React/Vue dashboard
   - Connect to your API

3. **Scale If Needed**
   - Upgrade to paid Render tier ($7/month)
   - Add database upgrades
   - Add Redis caching

4. **Monitor Performance**
   - Check Render dashboard logs
   - Monitor API response times
   - Track active sessions

---

## Reference

- **Render Docs:** https://render.com/docs
- **Flask Deployment:** https://flask.palletsprojects.com/en/2.3.x/deploying/
- **Socket.IO Deployment:** https://python-socketio.readthedocs.io/en/latest/

---

## Support

If deployment fails:
1. Check the error in Render logs
2. Verify `Procfile` syntax
3. Ensure `requirements_minimal.txt` is valid
4. Check GitHub repository is public
5. Verify domain DNS settings

---

**Your platform will be LIVE and FREE! 🚀**
