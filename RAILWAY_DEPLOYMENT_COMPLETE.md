# Railway Deployment - Final Steps Guide

## Current Status

✅ **Backend Service**: Deployed and running at `https://pulseofpeople-production.up.railway.app/`
✅ **Code Repository**: All fixes committed to GitHub (latest: `8f63112`)
✅ **Nixpacks Configuration**: Both backend and frontend configured correctly
⏳ **Frontend Service**: Ready to deploy (needs Railway service creation)

---

## Frontend Deployment - Step by Step

### Step 1: Create Frontend Service in Railway

1. Go to Railway dashboard: https://railway.app/
2. Open project **"noble-charisma"** (where your backend is deployed)
3. Click **"+ New"** button
4. Select **"GitHub Repo"**
5. Choose repository: `chatgptnotes/pulseofpeople`
6. **IMPORTANT**: Set **Root Directory** to: `frontend`

### Step 2: Configure Frontend Environment Variables

In the Railway frontend service settings, add these **service-specific variables**:

```bash
# Required Variables
VITE_API_URL=https://pulseofpeople-production.up.railway.app

# Optional Variables (for branding)
VITE_APP_NAME=Pulse of People
VITE_APP_VERSION=1.0
VITE_MULTI_TENANT=false

# If using Supabase (add your actual values)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

**Important Notes:**
- Use **"Service Variables"** (not "Shared Variables")
- Each service has its own environment variables
- Backend and Frontend variables don't conflict because they're in separate services

### Step 3: Deploy Frontend

Railway will automatically deploy after:
1. Service is created
2. Root directory is set to `frontend`
3. Environment variables are configured

Or manually trigger deployment:
1. Go to frontend service in Railway
2. Click **"Deployments"** tab
3. Click **"Deploy"** button

### Step 4: Get Frontend URL

After deployment succeeds:
1. Railway will provide a URL like: `https://pulseofpeople-production.up.railway.app` (different subdomain)
2. Copy this URL for testing

---

## Backend Environment Variables (Already Configured)

These should already be set in your backend service (in shared variables or service variables):

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=pulseofpeople-production.up.railway.app,.railway.app
USE_SQLITE=True

# CORS Settings (add frontend URL after it's deployed)
CORS_ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app

# Optional: PostgreSQL Database
DATABASE_URL=postgresql://user:password@host:port/dbname
USE_SQLITE=False  # Change to False if using PostgreSQL
```

**Note**: Backend already has hardcoded Railway domain support, so it will work even if ALLOWED_HOSTS isn't set.

---

## Post-Deployment Tasks

### 1. Update Backend CORS for Frontend

After frontend is deployed and you have its URL:

1. Go to backend service in Railway
2. Add/update environment variable:
   ```bash
   CORS_ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app,http://localhost:5173
   ```
3. Restart backend service (or wait for auto-redeploy)

**Good news**: Backend already auto-accepts all `.railway.app` domains, so frontend will work immediately!

### 2. Test the Deployment

**Backend API Test:**
```bash
curl https://pulseofpeople-production.up.railway.app/api/
```
Expected: API response or 404 (both are good - means Django is running)

**Frontend Test:**
1. Visit frontend URL in browser
2. Check if it loads without errors
3. Open browser DevTools → Console (check for errors)
4. Try logging in or using API features

### 3. Check Logs

**Backend Logs:**
1. Go to Railway → Backend Service → Deployments
2. Click on latest deployment
3. View logs for errors

**Frontend Logs:**
1. Go to Railway → Frontend Service → Deployments
2. Click on latest deployment
3. Check build logs for warnings

---

## Configuration Summary

### Backend (Django)

**File**: `backend/nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["python39", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[phases.build]
cmds = ["python manage.py collectstatic --noinput"]

[start]
cmd = "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"
```

**Key Features:**
- ✅ Hardcoded Railway domain in ALLOWED_HOSTS (works without env vars)
- ✅ Auto-detects CORS scheme (http/https) based on domain
- ✅ Strips whitespace from environment variables
- ✅ Fallback to SQLite if DATABASE_URL not set
- ✅ Production-ready with gunicorn

### Frontend (React + Vite)

**File**: `frontend/nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["nodejs_22"]

[phases.install]
cmds = ["npm install --legacy-peer-deps --ignore-scripts"]

[phases.build]
cmds = ["npm run build"]

[start]
cmd = "npm run preview -- --host 0.0.0.0 --port $PORT"
```

**Key Features:**
- ✅ Node 22 (required for Supabase packages)
- ✅ `--legacy-peer-deps` (resolves package conflicts)
- ✅ `--ignore-scripts` (skips husky postinstall)
- ✅ Vite preview mode with Railway port binding

---

## Troubleshooting

### Frontend: "Failed to fetch" or CORS errors

**Problem**: Frontend can't connect to backend API

**Solutions**:
1. Check `VITE_API_URL` environment variable in frontend service
2. Verify backend CORS_ALLOWED_ORIGINS includes frontend URL
3. Check backend logs for CORS errors
4. Ensure backend has `.railway.app` wildcard in ALLOWED_HOSTS

### Frontend: Build fails with Node version error

**Problem**: "Unsupported engine" error for Supabase packages

**Solution**: Verify `frontend/nixpacks.toml` has `nixPkgs = ["nodejs_22"]`

### Frontend: Build fails with package-lock.json error

**Problem**: "npm ci can only install packages when package.json and package-lock.json are in sync"

**Solution**: Verify `frontend/nixpacks.toml` uses `npm install --legacy-peer-deps` (not `npm ci`)

### Frontend: Build fails with "husky - .git can't be found"

**Problem**: Husky postinstall script fails in Railway environment

**Solution**: Verify `frontend/nixpacks.toml` has `--ignore-scripts` flag in install command

### Backend: DisallowedHost error

**Problem**: "Invalid HTTP_HOST header"

**Solution**: Backend already has hardcoded Railway domain - redeploy to get latest code (commit `8f63112`)

### Backend: CORS missing scheme error

**Problem**: "Origin is missing scheme or netloc"

**Solution**: Backend now auto-adds schemes - redeploy to get latest code (commit `7e0cc9b`)

---

## Cost Estimate

Railway Pricing (as of 2025):

### Development/Hobby Plan
- **Free Tier**: $5 worth of usage included
- **Usage-based pricing**: ~$0.000463/min for each service
- **Estimated cost**:
  - Backend: ~$10-15/month
  - Frontend: ~$5-10/month
  - **Total**: ~$15-25/month for both services

### Tips to Reduce Costs:
1. Use **Sleep on Idle** for non-production environments
2. Scale down unused services
3. Use SQLite instead of managed PostgreSQL (saves ~$5/month)
4. Monitor usage in Railway dashboard

---

## Optional: Add PostgreSQL Database

If you need PostgreSQL instead of SQLite:

1. In Railway project, click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway will automatically inject `DATABASE_URL` into all services
3. Update backend environment variables:
   ```bash
   USE_SQLITE=False
   ```
4. Run migrations via Railway shell:
   ```bash
   python manage.py migrate
   ```

---

## Git Commit History

Recent commits that fixed deployment issues:

```
8f63112 chore: Update package-lock.json with resolved peer dependencies
63d77a5 fix: Update frontend nixpacks to Node 22 and skip postinstall scripts
7e0cc9b fix: Auto-add URL schemes to CORS origins and strip whitespace
0609cbd fix: Hardcode Railway domain in ALLOWED_HOSTS as fallback
```

---

## Next Steps Checklist

- [ ] Create frontend service in Railway (same project as backend)
- [ ] Set Root Directory to `frontend`
- [ ] Add frontend environment variables (VITE_API_URL, etc.)
- [ ] Wait for deployment to complete
- [ ] Copy frontend URL from Railway
- [ ] Test frontend in browser
- [ ] Update backend CORS_ALLOWED_ORIGINS (optional - already has wildcard)
- [ ] Test API calls from frontend
- [ ] Monitor logs for errors
- [ ] (Optional) Add PostgreSQL database
- [ ] (Optional) Set up custom domain

---

## Support Resources

- Railway Documentation: https://docs.railway.app/
- Railway Discord: https://discord.gg/railway
- Django Deployment Guide: https://docs.djangoproject.com/en/stable/howto/deployment/
- Vite Production Build: https://vitejs.dev/guide/build.html

---

**Last Updated**: 2025-11-08
**Status**: Backend deployed, Frontend ready for deployment
**Repository**: https://github.com/chatgptnotes/pulseofpeople.git
