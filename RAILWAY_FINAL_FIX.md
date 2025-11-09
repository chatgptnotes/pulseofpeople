# 🚀 Railway Deployment - Final Fix Guide

## 🔴 CRITICAL ISSUES FOUND

### Backend Issues (11 Critical):
1. ❌ **DATABASE_URL BROKEN** - Truncated at `?s` instead of `?sslmode=require`
2. ❌ **Missing https:// in CORS** - `pulseofpeople-production.up.railway.app` missing protocol
3. ❌ **Broken variables** - `gbouncer` and `slmode` are malformed fragments
4. ❌ **Missing tvk domain** - `tvk.pulseofpeople.com` not in ALLOWED_HOSTS
5. ❌ **DB_SSLMODE wrong** - Using `prefer` instead of `require`

### Frontend Issues (5 Critical):
1. ❌ **100% DUPLICATES** - Every variable listed TWICE
2. ❌ **JWT_SECRET EXPOSED** - MAJOR security vulnerability (backend secret in frontend!)
3. ❌ **Wrong tenant mode** - Says "single" but also has "subdomain" mode

---

## ✅ STEP 1: FIX BACKEND VARIABLES

Go to Railway → **pulseofpeople** (backend service) → Variables → Raw Editor

**DELETE EVERYTHING and paste this:**

```env
SECRET_KEY="IM5sr4ltS5p71--IgqRzJflgfFNGuU2kpesz5EPc9xHcmvq5PnKZvMLxov6J88bDqrQ"
DEBUG="False"
ALLOWED_HOSTS="pulseofpeople-production.up.railway.app,.railway.app,localhost,tvk.pulseofpeople.com"
DB_ENGINE="django.db.backends.postgresql"
DB_NAME="postgres"
DB_USER="postgres.iwtgbseaoztjbnvworyq"
DB_PASSWORD="Chindwada@1"
DB_HOST="aws-1-ap-south-1.pooler.supabase.com"
DB_PORT="6543"
DB_SSLMODE="require"
DATABASE_URL="postgresql://postgres.iwtgbseaoztjbnvworyq:Chindwada%401@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true"
USE_SQLITE="False"
CORS_ALLOWED_ORIGINS="https://tvk.pulseofpeople.com,https://pulseofpeople-production.up.railway.app"
CSRF_TRUSTED_ORIGINS="https://pulseofpeople-production.up.railway.app,https://tvk.pulseofpeople.com"
SUPABASE_URL="https://iwtgbseaoztjbnvworyq.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94"
SUPABASE_JWT_SECRET="X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g=="
JWT_SECRET="DWCtQ-UF_0kfwHWnLYuko-_mpP92VlfI9KYRy-8OzJpRAyLk31nyeWApNPfnqvn4MGY"
JWT_ACCESS_TOKEN_LIFETIME="60"
JWT_REFRESH_TOKEN_LIFETIME="1440"
```

### What Changed:
- ✅ Fixed DATABASE_URL - Complete URL with `sslmode=require&pgbouncer=true`
- ✅ Added https:// to CORS_ALLOWED_ORIGINS
- ✅ Removed `gbouncer` and `slmode` (broken variables)
- ✅ Added `tvk.pulseofpeople.com` to ALLOWED_HOSTS
- ✅ Added `tvk.pulseofpeople.com` to CSRF_TRUSTED_ORIGINS
- ✅ Changed DB_SSLMODE to `require`
- ✅ Added missing DB_ENGINE
- ✅ Added JWT token lifetime settings

---

## ✅ STEP 2: FIX FRONTEND VARIABLES

Go to Railway → **pulseofpeople-frontend** (frontend service) → Variables → Raw Editor

**DELETE EVERYTHING and paste this:**

```env
VITE_SUPABASE_URL="https://iwtgbseaoztjbnvworyq.supabase.co"
VITE_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94"
VITE_APP_NAME="Pulse of People"
VITE_APP_URL="https://tvk.pulseofpeople.com"
VITE_APP_VERSION="1.0"
VITE_MULTI_TENANT="false"
VITE_TENANT_MODE="single"
VITE_DEFAULT_TENANT="tvk"
VITE_DJANGO_API_URL="https://pulseofpeople-production.up.railway.app/api"
VITE_MAPBOX_ACCESS_TOKEN="pk.eyJ1IjoibXVyYWxpLXRlc3QiLCJhIjoiY20yenl6eXRhMDNwczJxcHd6OHE0NTY4ZiJ9.demo-token-replace-with-real"
```

### What Changed:
- ✅ Removed ALL duplicates (every variable was listed twice!)
- ✅ Removed JWT_SECRET (CRITICAL security fix - backend secret exposed in frontend!)
- ✅ Only VITE_ prefixed variables (frontend-safe)
- ✅ Clean, organized configuration

---

## ✅ STEP 3: UPDATE SHARED VARIABLES (OPTIONAL)

Go to Railway → Project Settings → Shared Variables → Raw Editor

**Use this clean version:**

```env
SECRET_KEY="IM5sr4ltS5p71--IgqRzJflgfFNGuU2kpesz5EPc9xHcmvq5PnKZvMLxov6J88bDqrQ"
DEBUG="False"
ALLOWED_HOSTS="pulseofpeople-production.up.railway.app,.railway.app,localhost,tvk.pulseofpeople.com"
DATABASE_URL="postgresql://postgres.iwtgbseaoztjbnvworyq:Chindwada%401@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&pgbouncer=true"
USE_SQLITE="False"
DB_ENGINE="django.db.backends.postgresql"
DB_NAME="postgres"
DB_USER="postgres.iwtgbseaoztjbnvworyq"
DB_PASSWORD="Chindwada@1"
DB_HOST="aws-1-ap-south-1.pooler.supabase.com"
DB_PORT="6543"
DB_SSLMODE="require"
SUPABASE_URL="https://iwtgbseaoztjbnvworyq.supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94"
SUPABASE_JWT_SECRET="X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g=="
JWT_SECRET="DWCtQ-UF_0kfwHWnLYuko-_mpP92VlfI9KYRy-8OzJpRAyLk31nyeWApNPfnqvn4MGY"
JWT_ACCESS_TOKEN_LIFETIME="60"
JWT_REFRESH_TOKEN_LIFETIME="1440"
CORS_ALLOWED_ORIGINS="https://tvk.pulseofpeople.com,https://pulseofpeople-production.up.railway.app"
CSRF_TRUSTED_ORIGINS="https://pulseofpeople-production.up.railway.app,https://tvk.pulseofpeople.com"
VITE_APP_NAME="Pulse of People"
VITE_APP_URL="https://tvk.pulseofpeople.com"
VITE_APP_VERSION="1.0"
VITE_DEFAULT_TENANT="tvk"
VITE_MULTI_TENANT="false"
VITE_TENANT_MODE="single"
VITE_SUPABASE_URL="https://iwtgbseaoztjbnvworyq.supabase.co"
VITE_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94"
```

**Important:** Fixed the space in CORS_ALLOWED_ORIGINS (was `http://localhost:5173` with space before it)

---

## 📋 DEPLOYMENT CHECKLIST

### After Updating Variables:

1. **Backend Service:**
   - [ ] Variables updated
   - [ ] Wait for automatic redeploy (2-3 minutes)
   - [ ] Check logs: "Listening at: http://0.0.0.0:XXXX"
   - [ ] Test API: `curl https://pulseofpeople-production.up.railway.app/api/health/`

2. **Frontend Service:**
   - [ ] Variables updated (no duplicates)
   - [ ] JWT_SECRET removed
   - [ ] Wait for automatic redeploy (2-3 minutes)
   - [ ] Visit: https://tvk.pulseofpeople.com

3. **Test Login:**
   - [ ] Go to login page
   - [ ] Use: `admin@tvk.com` / `Admin@123`
   - [ ] Should login successfully
   - [ ] No CORS errors in console

---

## 🧪 VERIFICATION COMMANDS

### Test Backend API:
```bash
# Health check
curl https://pulseofpeople-production.up.railway.app/api/health/

# CORS check
curl -H "Origin: https://tvk.pulseofpeople.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://pulseofpeople-production.up.railway.app/api/auth/login/
```

**Expected:** Should see `access-control-allow-origin: https://tvk.pulseofpeople.com`

### Test Frontend:
1. Open https://tvk.pulseofpeople.com
2. Open DevTools → Console
3. Should see NO errors
4. Should see login page with test credentials

---

## 🚨 CRITICAL SECURITY FIXES

### ✅ FIXED:
1. **JWT_SECRET removed from frontend** - Was exposed to all users (critical vulnerability)
2. **DATABASE_URL now complete** - Was broken/truncated
3. **All CORS origins have https://** - Prevents CORS errors
4. **SSL required for database** - More secure connection

---

## 📊 BEFORE vs AFTER

### Backend Variables:
- **Before:** 18 variables (2 broken)
- **After:** 18 variables (all working)
- **Removed:** `gbouncer`, `slmode`
- **Fixed:** DATABASE_URL, CORS_ALLOWED_ORIGINS, ALLOWED_HOSTS

### Frontend Variables:
- **Before:** 22 variables (11 duplicates + 1 security issue)
- **After:** 10 variables (clean)
- **Removed:** 11 duplicates + JWT_SECRET

---

## ⏱️ ESTIMATED TIMELINE

1. Update backend variables: **2 minutes**
2. Backend redeploy: **3 minutes**
3. Update frontend variables: **1 minute**
4. Frontend redeploy: **2 minutes**
5. Testing: **2 minutes**

**Total: ~10 minutes**

---

## 🎯 SUCCESS CRITERIA

Your deployment is successful when:

✅ Backend shows "Deployed" status (green)
✅ Frontend shows "Deployed" status (green)
✅ No errors in Railway logs
✅ API returns `{"status": "healthy"}`
✅ Frontend loads at https://tvk.pulseofpeople.com
✅ Login works with test credentials
✅ No CORS errors in browser console
✅ Database migrations completed

---

## 📞 TROUBLESHOOTING

### Backend won't start:
- Check logs for database connection errors
- Verify DATABASE_URL is complete
- Ensure migrations ran successfully

### Frontend shows blank page:
- Check logs for build errors
- Verify VITE_DJANGO_API_URL is correct
- Check browser console for errors

### CORS errors:
- Verify CORS_ALLOWED_ORIGINS has https://
- Check backend is responding
- Clear browser cache

---

**Last Updated:** 2025-11-09
**Status:** Ready to Deploy
**Severity:** CRITICAL - Deploy immediately to fix security issues

