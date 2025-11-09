# 🚂 Railway Deployment Guide - Frontend & Backend

## 📍 Current Deployment Status

**Both frontend and backend are deployed on Railway**

### Deployment URLs
- **Frontend**: [Your Railway Frontend URL]
- **Backend API**: [Your Railway Backend URL]
- **Database**: Supabase Cloud

---

## 🔧 Railway-Specific Configuration

### Frontend Configuration

#### 1. **Create `railway.json` for Frontend**

```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "npm run build"
  },
  "deploy": {
    "startCommand": "npm run preview",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. **Update `package.json` Scripts**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview --host 0.0.0.0 --port $PORT",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  }
}
```

**Key Changes:**
- `--host 0.0.0.0` - Bind to all interfaces
- `--port $PORT` - Use Railway's dynamic port

#### 3. **Environment Variables (Railway Dashboard)**

Go to: Railway Dashboard → Your Project → Frontend Service → Variables

```bash
# Frontend Environment Variables
VITE_API_URL=https://your-backend.railway.app/api
VITE_MAPBOX_ACCESS_TOKEN=pk.your_mapbox_token
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key

# Railway-specific
NODE_VERSION=18
NPM_VERSION=9
```

---

### Backend Configuration

#### 1. **Create `railway.json` for Backend**

```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt"
  },
  "deploy": {
    "startCommand": "gunicorn pulseofpeople.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. **Update `requirements.txt`**

Add if not present:
```
gunicorn==21.2.0
whitenoise==6.6.0
psycopg2-binary==2.9.9
```

#### 3. **Update `settings.py` for Railway**

```python
# settings.py

import os
from pathlib import Path

# Railway-specific settings
RAILWAY_ENVIRONMENT = os.getenv('RAILWAY_ENVIRONMENT', 'development')

# Allowed hosts
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',  # Allow all Railway subdomains
    'your-custom-domain.com',  # If you have custom domain
]

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://your-frontend.railway.app",
    "https://your-custom-domain.com",
]

# Static files (WhiteNoise for Railway)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... other middleware
]

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database from environment (Railway PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE'),
        'USER': os.getenv('PGUSER'),
        'PASSWORD': os.getenv('PGPASSWORD'),
        'HOST': os.getenv('PGHOST'),
        'PORT': os.getenv('PGPORT', 5432),
    }
}
```

#### 4. **Environment Variables (Railway Dashboard)**

Go to: Railway Dashboard → Your Project → Backend Service → Variables

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
DJANGO_SETTINGS_MODULE=pulseofpeople.settings

# Database (Auto-populated by Railway if using Railway PostgreSQL)
PGHOST=containers-us-west-xxx.railway.app
PGPORT=5432
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=xxx

# Or use Supabase
DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:5432/postgres

# CORS
CORS_ALLOWED_ORIGINS=https://your-frontend.railway.app

# Python version
PYTHON_VERSION=3.11
```

---

## 🚀 Deployment Commands

### Quick Deploy Both Services

```bash
# Navigate to project root
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople

# Install Railway CLI if not installed
brew install railway

# Login to Railway
railway login

# Link to your project
railway link

# Deploy frontend
cd frontend
railway up

# Deploy backend
cd ../backend
railway up
```

---

## 🔄 Update Deployment

### Frontend Updates
```bash
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/frontend

# Make your changes, then:
git add .
git commit -m "Update frontend"
git push

# Railway auto-deploys on git push (if enabled)
# Or manually trigger:
railway up
```

### Backend Updates
```bash
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/backend

# Make your changes, then:
git add .
git commit -m "Update backend API"
git push

# Auto-deploy or manual:
railway up
```

---

## 📊 Monitor Deployments

### Railway Dashboard
```
https://railway.app/dashboard
```

**Features:**
- ✅ Real-time logs
- ✅ Deployment status
- ✅ Resource usage (CPU, Memory)
- ✅ Environment variables management
- ✅ Custom domains
- ✅ Build logs

### View Logs
```bash
# Frontend logs
railway logs --service frontend

# Backend logs
railway logs --service backend

# Follow logs (live)
railway logs --service backend --follow
```

---

## 🔗 Connect Frontend to Backend

### Update Frontend API Base URL

**File:** `frontend/src/config/api.ts` (or wherever API config is)

```typescript
// Production API URL (Railway backend)
export const API_BASE_URL = import.meta.env.VITE_API_URL ||
  'https://your-backend.railway.app/api';

// Example API client
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

**Railway Environment Variable:**
```
VITE_API_URL=https://pulseofpeople-backend.railway.app/api
```

---

## 🗄️ Database Options on Railway

### Option 1: Use Supabase (Current Setup)
✅ **Recommended** - You're already using Supabase

```bash
# Backend environment variables
DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres

# Or separate variables
PGHOST=db.xxx.supabase.co
PGPORT=5432
PGDATABASE=postgres
PGUSER=postgres
PGPASSWORD=your-password
```

### Option 2: Railway PostgreSQL
Add a PostgreSQL service in Railway:
1. Railway Dashboard → New → Database → PostgreSQL
2. Railway auto-injects `DATABASE_URL`
3. Run migrations: `railway run python manage.py migrate`

---

## 🚨 Important Railway Considerations

### 1. **Port Binding**
Railway assigns a dynamic `$PORT` environment variable.

**Frontend (Vite):**
```json
"preview": "vite preview --host 0.0.0.0 --port $PORT"
```

**Backend (Django):**
```bash
gunicorn app.wsgi:application --bind 0.0.0.0:$PORT
```

### 2. **Static Files**
Use WhiteNoise for serving Django static files:
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]
```

### 3. **Database Migrations**
Run after each deployment:
```bash
railway run python manage.py migrate
```

Or add to `railway.json`:
```json
{
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn app.wsgi:application --bind 0.0.0.0:$PORT"
  }
}
```

### 4. **Environment Variables**
- Set via Railway Dashboard (persisted)
- Or via CLI: `railway variables set KEY=VALUE`

### 5. **Custom Domains**
Railway Dashboard → Settings → Domains → Add Custom Domain
```
frontend: app.pulseofpeople.com
backend: api.pulseofpeople.com
```

---

## 📋 Pre-Deployment Checklist

### Frontend
- [ ] `VITE_API_URL` points to Railway backend
- [ ] Mapbox token added
- [ ] Supabase credentials added
- [ ] Build command works: `npm run build`
- [ ] Preview command works: `npm run preview`
- [ ] Port binding uses `$PORT`

### Backend
- [ ] `gunicorn` in requirements.txt
- [ ] `whitenoise` configured
- [ ] Database URL configured
- [ ] `ALLOWED_HOSTS` includes `.railway.app`
- [ ] `CORS_ALLOWED_ORIGINS` includes frontend URL
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Migrations applied: `python manage.py migrate`

---

## 🔧 Troubleshooting

### Frontend Build Fails
```bash
# Check logs
railway logs --service frontend

# Common fixes:
# 1. Ensure Node version is correct
railway variables set NODE_VERSION=18

# 2. Clear build cache
railway run npm cache clean --force

# 3. Check build command
railway run npm run build
```

### Backend Won't Start
```bash
# Check logs
railway logs --service backend

# Common issues:
# 1. Port not bound correctly
# Fix: gunicorn --bind 0.0.0.0:$PORT

# 2. Database not connected
# Fix: Check DATABASE_URL or PGHOST variables

# 3. Static files missing
railway run python manage.py collectstatic --noinput
```

### CORS Errors
```python
# backend/settings.py
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.railway.app",  # Update this!
]
```

### 502 Bad Gateway
```bash
# Check if backend is running
railway status

# Restart backend
railway restart --service backend
```

---

## 🎯 Quick Commands Reference

```bash
# Deploy
railway up

# Logs
railway logs --follow

# Run command
railway run python manage.py migrate

# Environment variables
railway variables
railway variables set KEY=VALUE

# Service status
railway status

# Restart
railway restart

# Open dashboard
railway open
```

---

## 📚 Railway Documentation

- **Main Docs**: https://docs.railway.app
- **Deploy Django**: https://docs.railway.app/guides/django
- **Deploy React**: https://docs.railway.app/guides/react
- **Environment Variables**: https://docs.railway.app/develop/variables
- **Custom Domains**: https://docs.railway.app/deploy/exposing-your-app

---

## ✅ Deployment Verification

After deployment, verify:

### 1. **Frontend Accessible**
```bash
curl -I https://your-frontend.railway.app
# Should return: 200 OK
```

### 2. **Backend API Responding**
```bash
curl https://your-backend.railway.app/api/health
# Should return: {"status": "ok"}
```

### 3. **Database Connected**
```bash
railway run --service backend python manage.py dbshell
# Should connect to database
```

### 4. **CORS Working**
```javascript
// Test in browser console on frontend URL
fetch('https://your-backend.railway.app/api/constituencies/')
  .then(r => r.json())
  .then(console.log)
// Should not show CORS error
```

---

## 🚀 Production Optimization

### 1. **Add Health Check Endpoint**
```python
# backend/urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('health/', health_check),
    # ...
]
```

### 2. **Enable Monitoring**
Railway Dashboard → Service → Metrics
- CPU usage
- Memory usage
- Network traffic

### 3. **Set Up Alerts**
Railway can send alerts for:
- Deployment failures
- High resource usage
- Service downtime

---

**Status**: ✅ Railway-optimized configuration complete!

**Next Steps:**
1. Update environment variables in Railway Dashboard
2. Commit and push configuration files
3. Verify deployment URLs
4. Test frontend → backend connectivity
