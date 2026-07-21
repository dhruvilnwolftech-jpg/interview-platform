# Deployment Guide

## Local Development Setup

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r ../requirements.txt

# Initialize database
python -c "
from server import app, db
with app.app_context():
    db.create_all()
print('Database initialized successfully!')
"

# Start server
python server.py
```

The server will run on `http://localhost:5000`

### 2. Testing Backend

```bash
# In another terminal
cd tests
python test_api.py
```

Expected output:
```
=== Testing Health Endpoint ===
✓ Health check passed: {'status': 'ok', 'timestamp': '...'}

=== Testing Session Creation ===
✓ Session created
  Session ID: ...
  Document ID: ...
  Session Code: XXXXXX
...
RESULTS: 8 passed, 0 failed
```

### 3. Run Applications Locally

**Terminal 1 - Backend:**
```bash
cd backend
python server.py
```

**Terminal 2 - User App:**
```bash
cd user_app
python main.py
```

**Terminal 3 - Support Person App:**
```bash
cd support_person_app
python main.py
```

**Terminal 4 - Admin App:**
```bash
cd admin_app
python main.py
```

## Android APK Building

### Prerequisites

1. **Java Development Kit (JDK)**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install default-jdk
   
   # macOS
   brew install openjdk
   
   # Windows - Download from oracle.com
   ```

2. **Android SDK**
   ```bash
   # Using Android Studio (recommended)
   # Download from https://developer.android.com/studio
   
   # Or via command line
   mkdir -p ~/Android/Sdk
   cd ~/Android/Sdk
   wget https://dl.google.com/android/repository/commandlinetools-linux-XXXX.zip
   unzip commandlinetools-linux-XXXX.zip
   ```

3. **Build Tools**
   ```bash
   # In Android SDK Manager
   # Install: Build Tools 33.0.0+
   #          API Level 33+
   #          NDK 21.x or higher
   ```

4. **Buildozer and Dependencies**
   ```bash
   pip install buildozer cython pyjnius
   
   # Ubuntu/Debian additional
   sudo apt-get install build-essential libssl-dev libffi-dev \
       python3-dev openjdk-11-jdk-headless autoconf libtool
   ```

### Configuration

Set Android SDK and NDK paths:

```bash
# Linux/macOS
export ANDROID_SDK_ROOT=~/Android/Sdk
export ANDROID_NDK_ROOT=~/Android/Sdk/ndk/21.4.7075529

# Windows (in Command Prompt)
set ANDROID_SDK_ROOT=%USERPROFILE%\AppData\Local\Android\Sdk
set ANDROID_NDK_ROOT=%USERPROFILE%\AppData\Local\Android\Sdk\ndk\21.4.7075529
```

### Building APKs

#### User APK

```bash
# Update buildozer.spec
sed -i 's/source.dir = .*/source.dir = .\/user_app/' buildozer.spec
sed -i 's/package.name = .*/package.name = interview_user/' buildozer.spec

# Build
buildozer android debug

# APK location: bin/interview_user-0.1-debug.apk
```

#### Support Person APK

```bash
# Update buildozer.spec
sed -i 's/source.dir = .*/source.dir = .\/support_person_app/' buildozer.spec
sed -i 's/package.name = .*/package.name = interview_support/' buildozer.spec

# Build
buildozer android debug

# APK location: bin/interview_support-0.1-debug.apk
```

#### Admin APK

```bash
# Update buildozer.spec
sed -i 's/source.dir = .*/source.dir = .\/admin_app/' buildozer.spec
sed -i 's/package.name = .*/package.name = interview_admin/' buildozer.spec

# Build
buildozer android debug

# APK location: bin/interview_admin-0.1-debug.apk
```

### Installing APKs on Device

```bash
# Connect Android device with USB debugging enabled
adb devices

# Install APK
adb install -r bin/interview_user-0.1-debug.apk
adb install -r bin/interview_support-0.1-debug.apk
adb install -r bin/interview_admin-0.1-debug.apk

# Run app
adb shell am start -n org.example.interview_user/org.example.interview_user.MainActivity
```

## Production Deployment

### Server Deployment (AWS EC2 Example)

1. **Launch EC2 Instance**
   ```bash
   # Ubuntu 22.04 LTS
   # t3.small or larger
   # 20GB storage
   ```

2. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3.10 python3-pip python3-venv \
       nginx supervisor sqlite3 git
   ```

3. **Clone and Setup Application**
   ```bash
   git clone <repository-url> /opt/interview-platform
   cd /opt/interview-platform
   
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Setup Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://localhost:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

5. **Setup Supervisor** (`/etc/supervisor/conf.d/interview-platform.conf`)
   ```ini
   [program:interview-platform]
   directory=/opt/interview-platform
   command=/opt/interview-platform/venv/bin/python backend/server.py
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/interview-platform.err.log
   stdout_logfile=/var/log/interview-platform.out.log
   environment=FLASK_ENV=production,SECRET_KEY=<generate-random-key>
   ```

6. **SSL Certificate (Let's Encrypt)**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d your-domain.com
   ```

7. **Update Application Configuration**
   - Update `SERVER_URL` in APKs to use `https://your-domain.com`
   - Change `SECRET_KEY` in `.env`
   - Update `DATABASE_URL` if using PostgreSQL

### Production Environment Variables (`.env`)

```
FLASK_ENV=production
SECRET_KEY=<use-strong-random-key>
DATABASE_URL=postgresql://user:password@localhost/interview_db
DEBUG=False
CORS_ORIGINS=https://your-domain.com
```

### PostgreSQL Setup (Optional)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb interview_db

# Update connection string
DATABASE_URL=postgresql://interview_user:password@localhost/interview_db
```

### Database Backup

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 /opt/interview-platform/interview_platform.db ".backup /backups/interview_platform_$DATE.db"

# Add to crontab
0 2 * * * /path/to/backup-script.sh
```

### Monitoring

```bash
# Check application status
sudo supervisorctl status interview-platform

# View logs
tail -f /var/log/interview-platform.out.log
tail -f /var/log/interview-platform.err.log

# Monitor server
htop
```

### Security Hardening

1. **Firewall Rules**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **Update APK Server URLs**
   - Change from `http://localhost:5000` to `https://your-domain.com`
   - Rebuild APKs with new configuration

3. **HTTPS Only**
   - Enforce HTTPS redirect in Nginx
   - Use secure cookie settings in Flask

4. **Rate Limiting**
   - Consider adding rate limiting middleware
   - Implement request throttling for API endpoints

## Performance Optimization

### WebSocket Optimization

```python
# For production, consider using Redis for socket scaling
SOCKETIO_MESSAGE_QUEUE = 'redis://localhost:6379'
```

### Database Optimization

```sql
-- Create indexes for faster queries
CREATE INDEX idx_session_code ON interview_sessions(code);
CREATE INDEX idx_document_session ON documents(session_id);
CREATE INDEX idx_change_document ON document_changes(document_id);
CREATE INDEX idx_connection_session ON user_connections(session_id);
```

### Caching

Implement Redis caching for frequently accessed data:
```python
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

## Troubleshooting

### APK Connection Issues

1. **Check Network**
   ```bash
   # From device
   ping your-domain.com
   curl https://your-domain.com/api/health
   ```

2. **Update Server URL**
   - Verify `SERVER_URL` in APK source
   - Rebuild APK after changing
   - Clear app cache: `adb shell pm clear org.example.interview_user`

3. **Check Firewall**
   - Ensure port 443 (HTTPS) is open
   - WebSocket uses same port as HTTPS

### Database Issues

```bash
# Reset database
rm -f /opt/interview-platform/interview_platform.db

# Reinitialize
cd /opt/interview-platform
python -c "from backend.server import app, db; app.app_context().push(); db.create_all()"

# Restart application
sudo supervisorctl restart interview-platform
```

### Memory Issues

```bash
# Monitor memory usage
free -h
df -h

# Check application memory
ps aux | grep python
```

## Scaling

For larger deployments:

1. **Load Balancing**
   - Use Nginx load balancer
   - Deploy multiple backend instances
   - Use Redis for session sharing

2. **Database Replication**
   - Switch to PostgreSQL with replication
   - Use managed database services (AWS RDS)

3. **Caching Layer**
   - Add Redis for caching
   - Cache frequently accessed documents

4. **CDN**
   - Use CloudFront/CloudFlare for static assets
   - Cache API responses appropriately
