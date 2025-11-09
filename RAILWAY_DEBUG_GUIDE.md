# Railway Deployment Debugging Guide

## 🔍 How to Debug Railway Deployment (Web Dashboard)

### Step 1: Check Backend Deployment Status

1. Go to https://railway.app/
2. Click on **PULSE OF PEOPLE** project
3. Click on **pulseofpeople** (backend service)
4. Click on **Deployments** tab

**Look for:**
- ✅ Green "Deployed" status
- ⚠️ Yellow "Building" status
- ❌ Red "Failed" status

### Step 2: Check Backend Logs

1. Click on the latest deployment
2. Scroll through the logs
3. Look for these sections:

#### **Build Phase:**
```
#1 [internal] load build context
#2 [internal] load metadata
...
pip install -r requirements.txt
```

**Common errors:**
- `ERROR: Could not find a version that satisfies the requirement`
- `ModuleNotFoundError`

#### **Migration Phase:**
```
Running migrations...
Operations to perform:
  Apply all migrations: ...
Running migrations:
  Applying contenttypes.0001_initial... OK
```

**Common errors:**
- `django.db.utils.OperationalError: could not connect to server`
- `FATAL: password authentication failed`
- `SSL connection has been closed unexpectedly`

#### **Startup Phase:**
```
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXX
```

**Common errors:**
- `ModuleNotFoundError: No module named 'gunicorn'`
- `django.core.exceptions.ImproperlyConfigured`
- `CORS` errors

### Step 3: Check Environment Variables

1. Click on **Variables** tab
2. Verify these critical variables exist:

**Must Have:**
```
DATABASE_URL (not truncated)
SECRET_KEY
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS
USE_SQLITE=False
```

**Check for:**
- ❌ Broken values (truncated URLs)
- ❌ Missing https:// in CORS origins
- ❌ Duplicate variables
- ❌ Invalid variable names (gbouncer, slmode)

### Step 4: Check Frontend Deployment Status

1. Click on **pulseofpeople-frontend** service
2. Click on **Deployments** tab
3. Check latest deployment logs

#### **Build Phase:**
```
npm install
...
vite build
...
✓ built in XXXms
```

**Common errors:**
- `Module not found`
- `TypeScript errors`
- `Build failed with X errors`

#### **Deploy Phase:**
```
Deploying...
Deployment successful
```

### Step 5: Test API Endpoints

**Open a new terminal and run:**

```bash
# Test backend health
curl https://pulseofpeople-production.up.railway.app/api/health/

# Expected: {"status": "healthy"} or similar
# If error: "502 Bad Gateway" = backend not running
# If error: "Connection refused" = backend crashed
```

**Test CORS:**
```bash
curl -H "Origin: https://tvk.pulseofpeople.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://pulseofpeople-production.up.railway.app/api/auth/login/
```

**Expected headers:**
```
access-control-allow-origin: https://tvk.pulseofpeople.com
access-control-allow-methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
```

### Step 6: Check Frontend in Browser

1. Open https://tvk.pulseofpeople.com (or your Railway frontend URL)
2. Open DevTools (F12)
3. Check **Console** tab for errors:

**Common errors:**
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
Access to fetch blocked by CORS policy
TypeError: Cannot read property 'XXX' of undefined
```

4. Check **Network** tab:
- Look for failed requests (red)
- Check API calls to backend
- Verify response status codes

### Step 7: Common Issues & Solutions

#### Issue 1: "502 Bad Gateway"
**Cause:** Backend not responding
**Fix:**
1. Check backend logs for crashes
2. Verify DATABASE_URL is correct
3. Ensure migrations completed
4. Check PORT variable

#### Issue 2: CORS Errors
**Cause:** Missing or incorrect CORS configuration
**Fix:**
1. Add https:// to all CORS origins
2. Ensure frontend domain is in CORS_ALLOWED_ORIGINS
3. Check CSRF_TRUSTED_ORIGINS includes frontend domain

#### Issue 3: Database Connection Failed
**Cause:** Invalid DATABASE_URL or network issues
**Fix:**
1. Check DATABASE_URL format
2. Verify password encoding (@ = %40)
3. Use pooler connection (port 6543)
4. Ensure sslmode=require

#### Issue 4: Frontend Blank Page
**Cause:** Build errors or missing env variables
**Fix:**
1. Check build logs for errors
2. Verify all VITE_ variables are set
3. Check VITE_DJANGO_API_URL points to backend
4. Clear browser cache

#### Issue 5: Authentication Not Working
**Cause:** Supabase configuration issues
**Fix:**
1. Verify VITE_SUPABASE_URL is correct
2. Check VITE_SUPABASE_ANON_KEY is valid
3. Ensure Supabase project is active
4. Check users table exists in Supabase

---

## 🧪 Quick Verification Checklist

### Backend:
- [ ] Latest deployment shows "Deployed" status
- [ ] No errors in deployment logs
- [ ] Migrations completed successfully
- [ ] Gunicorn started and listening
- [ ] API health endpoint responds
- [ ] DATABASE_URL is complete (not truncated)
- [ ] CORS headers are correct

### Frontend:
- [ ] Latest deployment shows "Deployed" status
- [ ] Build completed with no errors
- [ ] No duplicate environment variables
- [ ] JWT_SECRET removed (security)
- [ ] VITE_DJANGO_API_URL points to backend
- [ ] Page loads in browser
- [ ] No console errors

### Database:
- [ ] Supabase project is active
- [ ] Database credentials are correct
- [ ] SSL/TLS connection enabled
- [ ] Users table exists
- [ ] Pooler connection working

---

## 📊 Expected Log Output

### Successful Backend Deployment:
```
✓ Building...
✓ Installing dependencies...
✓ Running migrations...
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
✓ Collecting static files...
✓ Starting gunicorn...
  [INFO] Listening at: http://0.0.0.0:8000
  [INFO] Booting worker with pid: 123
✓ Deployment successful
```

### Successful Frontend Deployment:
```
✓ Installing dependencies...
✓ Building with Vite...
  vite v5.x.x building for production...
  ✓ 150 modules transformed
  ✓ built in 15.2s
✓ Deployment successful
```

---

## 🆘 Getting More Help

If you're still stuck:

1. **Copy deployment logs** and share them
2. **Screenshot error messages** from browser console
3. **Run verification commands** and share output
4. **Check Railway status page**: https://status.railway.app/

---

**Last Updated:** 2025-11-09
**Railway CLI Version:** 4.11.0

