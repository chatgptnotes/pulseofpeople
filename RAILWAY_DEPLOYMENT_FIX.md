# 🚀 Railway Deployment - Complete Fix Guide

## 🔍 Root Cause Analysis

### Problems Identified:
1. **Build Phase Database Connection**: nixpacks.toml ran `collectstatic` during build, requiring database access before deployment
2. **No Database Migrations**: Migrations weren't running on startup, causing schema mismatches
3. **URL-Encoded Password**: Supabase password `Chindwada@1` needs URL encoding: `Chindwada%401`
4. **Python Version Mismatch**: Using python39 instead of python311
5. **Missing STATIC_ROOT**: collectstatic failed without proper static files configuration

### Error Chain:
```
Build Phase → Database Connection Fails → Django Crashes → 502 Bad Gateway → No CORS Headers
```

---

## ✅ Files Changed

### 1. `backend/nixpacks.toml`
**Changes:**
- ✅ Updated Python 3.9 → Python 3.11
- ✅ Removed database-dependent collectstatic from build phase
- ✅ Added migrations + collectstatic to startup command

**New Configuration:**
```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["echo 'Skipping collectstatic - will run on startup'"]

[start]
cmd = "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"
```

### 2. `backend/config/settings.py`
**Changes:**
- ✅ Added `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- ✅ Enhanced database connection with SSL requirements
- ✅ Added connection health checks and timeouts

### 3. `backend/requirements.txt`
**Changes:**
- ✅ Added `dj-database-url==2.3.0` for DATABASE_URL parsing

---

## 🔧 Railway Environment Variables

### Backend Service (pulseofpeople-production.up.railway.app)

Copy-paste these **exactly**:

```bash
# Database - CRITICAL: Use URL-encoded password
DATABASE_URL=postgresql://postgres:Chindwada%401@db.iwtgbseaoztjbnvworyq.supabase.co:5432/postgres?sslmode=require

# Database Mode
USE_SQLITE=False

# Django Security
DEBUG=False
SECRET_KEY=<GENERATE-A-STRONG-50-CHAR-RANDOM-KEY>
JWT_SECRET=<GENERATE-A-STRONG-50-CHAR-RANDOM-KEY>

# Domain Configuration
ALLOWED_HOSTS=tvk.pulseofpeople.com,pulseofpeople-production.up.railway.app

# CORS - Allow Frontend
CORS_ALLOWED_ORIGINS=https://tvk.pulseofpeople.com

# CSRF - Trust Frontend
CSRF_TRUSTED_ORIGINS=https://tvk.pulseofpeople.com,https://pulseofpeople-production.up.railway.app
```

**⚠️ IMPORTANT:**
- The password encoding: `@` → `%40` (so `Chindwada@1` becomes `Chindwada%401`)
- No quotes around any values
- No spaces after `=`

### Generate Secret Keys

Run this command locally to generate secure keys:

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50)); print('JWT_SECRET=' + secrets.token_urlsafe(50))"
```

Copy the output and replace the placeholders above.

---

### Frontend Service (tvk.pulseofpeople.com)

```bash
VITE_DJANGO_API_URL=https://pulseofpeople-production.up.railway.app/api
VITE_APP_NAME=Pulse of People
VITE_APP_URL=https://tvk.pulseofpeople.com
```

---

## 📝 Deployment Steps

### Step 1: Update Code (Coordinate with Teammate)
```bash
# After teammate's changes are merged
git pull origin main

# Verify these files are updated:
# - backend/nixpacks.toml
# - backend/config/settings.py
# - backend/requirements.txt

git push origin main
```

### Step 2: Configure Railway Backend
1. Go to Railway Dashboard → Backend Service
2. Click "Variables" tab
3. **DELETE** these old variables (if they exist):
   - `DB_HOST`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_PORT`
   - `DB_SSLMODE`

4. **ADD** the new variables from above section

### Step 3: Configure Railway Frontend
1. Go to Railway Dashboard → Frontend Service
2. Click "Variables" tab
3. Add the frontend variables from above

### Step 4: Redeploy
1. Backend will auto-redeploy when you push code
2. Or manually trigger: Backend Service → Deployments → "Redeploy"

### Step 5: Monitor Logs
1. Click on the latest deployment
2. Watch for:
   - ✅ "Running migrations..." (should show migration output)
   - ✅ "Collecting static files..." (should collect successfully)
   - ✅ "Listening at: http://0.0.0.0:XXXX" (gunicorn started)

---

## 🧪 Testing

### Test 1: Backend Health
Open browser console and run:

```javascript
fetch('https://pulseofpeople-production.up.railway.app/api/auth/login/', {
  method: 'OPTIONS',
  headers: { 'Origin': 'https://tvk.pulseofpeople.com' }
})
.then(r => {
  console.log('Status:', r.status);
  r.headers.forEach((v,k) => console.log(k + ':', v));
})
```

**Expected output:**
```
Status: 200
access-control-allow-origin: https://tvk.pulseofpeople.com
access-control-allow-methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
...
```

### Test 2: Login Flow
1. Go to https://tvk.pulseofpeople.com
2. Try logging in with test credentials
3. Should succeed without CORS errors

---

## 🚨 Troubleshooting

### If 502 Error Persists:
1. Check Railway backend logs for database connection errors
2. Verify DATABASE_URL has correct password encoding (`%40` not `@`)
3. Check Supabase → Settings → Database → Connection pooling is enabled

### If CORS Error Persists:
1. Verify `CORS_ALLOWED_ORIGINS=https://tvk.pulseofpeople.com` (exact match, no trailing slash)
2. Check backend logs for `corsheaders` middleware loading
3. Clear browser cache and hard refresh (Cmd+Shift+R on Mac)

### If Migrations Fail:
1. Check Supabase database is accessible
2. Try connecting manually: `psql "postgresql://postgres:Chindwada@1@db.iwtgbseaoztjbnvworyq.supabase.co:5432/postgres"`
3. Check Railway has network access to Supabase

---

## 📊 Expected Deployment Timeline

```
Code Push → Railway Detects Changes → 30 seconds
Build Phase (pip install) → 1-2 minutes
Start Phase (migrate + collectstatic) → 30-60 seconds
Gunicorn Ready → LIVE! 🎉

Total: ~3-4 minutes
```

---

## ✅ Success Checklist

- [ ] Code changes pushed to main branch
- [ ] Railway backend has all 8 environment variables
- [ ] Railway frontend has 3 environment variables
- [ ] SECRET_KEY and JWT_SECRET generated (not default values)
- [ ] Backend deployment shows "Listening at" in logs
- [ ] Frontend can call backend API without CORS errors
- [ ] Login functionality works end-to-end

---

**Last Updated:** 2025-11-08
**Status:** Ready for Deployment
