# Django Backend Deployment Guide - Render

## Overview
Deploy the Django backend to Render.com with PostgreSQL database (Supabase).

**Deployment URL**: https://pulseofpeople-backend.onrender.com
**Platform**: Render.com (Web Service)
**Database**: Supabase PostgreSQL (already configured)

---

## Prerequisites

✅ GitHub repository with backend code
✅ Render account (render.com)
✅ Supabase database credentials (already have)

---

## Step 1: Create New Web Service on Render

### 1.1 Navigate to Render Dashboard
- Go to https://dashboard.render.com
- Click **"New +"** button (top right)
- Select **"Web Service"**

### 1.2 Connect GitHub Repository
- Select **"Build and deploy from a Git repository"**
- Click **"Connect account"** if not already connected
- Find and select: `chatgptnotes/pulseofpeople`
- Click **"Connect"**

### 1.3 Configure Service Settings

**Basic Settings:**
```
Name: pulseofpeople-backend
Region: Oregon (US West) or closest to you
Branch: main
```

**Build Settings:**
```
Root Directory: backend
```

**Docker Settings:**
```
✓ Dockerfile
Dockerfile Path: backend/Dockerfile
Docker Command: (leave empty - uses CMD from Dockerfile)
```

**Instance Type:**
```
Free tier: Free
Paid tier: Starter ($7/month) - Recommended for production
```

---

## Step 2: Add Environment Variables

Click **"Environment"** tab and add these variables one by one:

### Required Environment Variables (11 total)

#### Django Core Settings

**1. SECRET_KEY**
```
GENERATE A NEW ONE! Run this locally:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

Example output:
django-insecure-abc123xyz789!@#$%^&*()_+-=[]{}|;:,.<>?
```

**2. DEBUG**
```
False
```

**3. ALLOWED_HOSTS**
```
pulseofpeople-backend.onrender.com,pulseofpeople.onrender.com,.onrender.com
```

#### Database Settings (Supabase PostgreSQL)

**4. DB_NAME**
```
postgres
```

**5. DB_USER**
```
postgres.iwtgbseaoztjbnvworyq
```

**6. DB_PASSWORD**
```
Chindwada@1
```

**7. DB_HOST**
```
aws-1-ap-south-1.pooler.supabase.com
```

**8. DB_PORT**
```
6543
```

**9. DB_SSLMODE**
```
require
```

**10. USE_SQLITE**
```
False
```

#### CORS Settings

**11. CORS_ALLOWED_ORIGINS**
```
https://pulseofpeople.onrender.com
```

#### Supabase Auth (Optional - if backend needs direct Supabase access)

**12. SUPABASE_URL**
```
https://iwtgbseaoztjbnvworyq.supabase.co
```

**13. SUPABASE_ANON_KEY**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94
```

**14. SUPABASE_JWT_SECRET**
```
X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g==
```

---

## Step 3: Deploy

1. **Review settings** - Double-check all environment variables
2. Click **"Create Web Service"**
3. Wait for deployment (~3-5 minutes)

### Expected Build Process:

```
✓ Cloning from GitHub
✓ Building Docker image (multi-stage build)
✓ Installing Python dependencies
✓ Collecting static files
✓ Running migrations (automatic)
✓ Starting Gunicorn server on port 8000
✓ Health check passes
✓ Service goes Live
```

---

## Step 4: Run Database Migrations

### Option 1: Automatic (if migrations are set up)
Migrations should run automatically during deployment.

### Option 2: Manual (via Render Shell)

1. Go to your service in Render dashboard
2. Click **"Shell"** tab
3. Run:
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: create admin user
```

---

## Step 5: Update Frontend to Use Backend API

Update your frontend environment variables in Render:

**In Frontend Service Environment:**
```
Key: VITE_DJANGO_API_URL
Value: https://pulseofpeople-backend.onrender.com/api
```

Then trigger frontend redeploy:
```bash
git commit --allow-empty -m "chore: update backend API URL"
git push origin main
```

---

## Step 6: Verify Deployment

### 6.1 Check Health Endpoint
Visit: https://pulseofpeople-backend.onrender.com/api/health/

**Expected response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-09T10:30:00Z"
}
```

### 6.2 Check Django Admin
Visit: https://pulseofpeople-backend.onrender.com/admin/

Should show Django admin login page.

### 6.3 Test API Endpoints
```bash
# Test authentication endpoint
curl https://pulseofpeople-backend.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

## Troubleshooting

### Issue: Build Fails

**Check:**
1. Dockerfile path is correct: `backend/Dockerfile`
2. Root directory is set to `backend`
3. All dependencies in requirements.txt are valid

### Issue: Database Connection Error

**Check:**
1. All DB_* environment variables are correct
2. DB_SSLMODE is set to `require`
3. Supabase database is accessible (not paused)

### Issue: Static Files Not Loading

**Solution:**
```bash
# Run in Render Shell
python manage.py collectstatic --noinput
```

### Issue: CORS Errors from Frontend

**Check:**
1. CORS_ALLOWED_ORIGINS includes frontend URL
2. django-cors-headers is installed
3. CORS middleware is enabled in settings.py

---

## Monitoring & Logs

### View Logs
1. Go to Render dashboard → Your service
2. Click **"Logs"** tab
3. View real-time logs

### View Metrics
1. Click **"Metrics"** tab
2. Monitor CPU, memory, response times

---

## Cost

**Free Tier:**
- Sleeps after 15 minutes of inactivity
- 750 hours/month free
- Slower cold starts (~30 seconds)

**Starter Tier ($7/month):**
- Always running
- Instant response times
- Better for production

---

## Security Checklist

✅ DEBUG=False in production
✅ Strong SECRET_KEY (not the default)
✅ ALLOWED_HOSTS configured properly
✅ Database uses SSL (DB_SSLMODE=require)
✅ Supabase JWT secret is secret
✅ CORS origins are restricted
✅ Rate limiting enabled (django-ratelimit)

---

## Next Steps After Deployment

1. **Set up monitoring**: Configure Sentry (already in requirements)
2. **Enable caching**: Configure Redis if needed
3. **Set up backups**: Supabase handles database backups automatically
4. **Configure domain**: Add custom domain in Render settings
5. **Enable HTTPS**: Automatic with Render

---

## Quick Reference: Environment Variables

| Variable | Value | Required |
|----------|-------|----------|
| SECRET_KEY | (generate new) | Yes |
| DEBUG | False | Yes |
| ALLOWED_HOSTS | your-backend.onrender.com | Yes |
| DB_NAME | postgres | Yes |
| DB_USER | postgres.iwtgbseaoztjbnvworyq | Yes |
| DB_PASSWORD | Chindwada@1 | Yes |
| DB_HOST | aws-1-ap-south-1.pooler.supabase.com | Yes |
| DB_PORT | 6543 | Yes |
| DB_SSLMODE | require | Yes |
| USE_SQLITE | False | Yes |
| CORS_ALLOWED_ORIGINS | https://pulseofpeople.onrender.com | Yes |

---

## Support

- **Render Docs**: https://render.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/5.0/howto/deployment/
- **Issue Tracker**: https://github.com/chatgptnotes/pulseofpeople/issues

---

**Status**: Ready to Deploy ✅
**Last Updated**: 2025-11-09
