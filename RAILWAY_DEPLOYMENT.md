# Railway Deployment Guide - Monorepo

This guide shows how to deploy the Pulse of People monorepo to Railway with separate backend and frontend services.

## Prerequisites

- GitHub repository pushed: https://github.com/chatgptnotes/pulseofpeople
- Railway account: https://railway.app

## Deployment Steps

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose `chatgptnotes/pulseofpeople`

### Step 2: Delete the Default Service

Railway will create one service automatically, but we need TWO services (backend + frontend).

1. Click on the auto-created service
2. Click "Settings" tab
3. Scroll down and click "Delete Service"

### Step 3: Create Backend Service

1. Click "+ New" in the top right
2. Select "GitHub Repo"
3. Choose `chatgptnotes/pulseofpeople`
4. Service will be created

#### Configure Backend Service:

1. **Click on the service** → Go to "Settings" tab
2. **Service Name**: Change to `backend`
3. **Root Directory**: Set to `backend`
4. **Start Command**: Will auto-detect from `nixpacks.toml`

#### Set Backend Environment Variables:

Go to "Variables" tab and add:

```env
SECRET_KEY=your-django-secret-key-here-generate-one
DEBUG=False
ALLOWED_HOSTS=${{RAILWAY_PUBLIC_DOMAIN}}
DATABASE_URL=${{Postgres.DATABASE_URL}}

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS (will be updated after frontend is deployed)
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.railway.app
```

**Generate SECRET_KEY** (run locally):
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 4: Add PostgreSQL Database

1. Click "+ New" in Railway project
2. Select "Database" → "Add PostgreSQL"
3. Database will be created and automatically linked to backend service
4. `DATABASE_URL` variable will be auto-injected

### Step 5: Run Database Migrations

1. Click on backend service
2. Go to "Settings" tab
3. Scroll to "Deploy" section
4. Add this to "Build Command" (optional, or run via Railway shell):
   ```bash
   python manage.py migrate
   ```

Or run migrations via Railway shell:
1. Click "Shell" tab
2. Run: `python manage.py migrate`
3. Run: `python manage.py createsuperuser` (optional)

### Step 6: Create Frontend Service

1. Click "+ New" in the project
2. Select "GitHub Repo"
3. Choose `chatgptnotes/pulseofpeople` again
4. New service will be created

#### Configure Frontend Service:

1. **Click on the service** → Go to "Settings" tab
2. **Service Name**: Change to `frontend`
3. **Root Directory**: Set to `frontend`
4. **Start Command**: Will auto-detect from `nixpacks.toml`

#### Set Frontend Environment Variables:

Go to "Variables" tab and add:

```env
VITE_API_URL=https://your-backend-domain.railway.app
VITE_APP_NAME=Pulse of People
VITE_APP_VERSION=1.0
VITE_MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token-here
```

**Update backend URL**:
1. Copy the backend service public URL (from backend service page)
2. Paste it as `VITE_API_URL` value

### Step 7: Update Backend CORS

Now that frontend is deployed:

1. Go to backend service → "Variables" tab
2. Update `CORS_ALLOWED_ORIGINS`:
   ```env
   CORS_ALLOWED_ORIGINS=https://your-frontend-domain.railway.app
   ```
3. Click "Redeploy" to apply changes

### Step 8: Generate Domain Names (Optional)

Railway auto-generates domains, but you can customize them:

**Backend**:
1. Go to backend service → "Settings" tab
2. Scroll to "Networking"
3. Click "Generate Domain" or customize it
4. Example: `pulseofpeople-backend.up.railway.app`

**Frontend**:
1. Go to frontend service → "Settings" tab
2. Scroll to "Networking"
3. Click "Generate Domain" or customize it
4. Example: `pulseofpeople.up.railway.app`

### Step 9: Verify Deployment

1. **Backend Health Check**:
   - Visit: `https://your-backend-domain.railway.app/admin/`
   - Should see Django admin login

2. **Frontend Check**:
   - Visit: `https://your-frontend-domain.railway.app/`
   - Should see the Pulse of People app

3. **API Connection**:
   - Login to frontend
   - Check browser console for API calls
   - Should connect to backend successfully

## Troubleshooting

### Backend Issues

**Build Fails**:
- Check that `backend/nixpacks.toml` exists
- Check that `requirements.txt` includes `gunicorn`
- Check Railway logs in "Deployments" tab

**Database Connection Fails**:
- Verify `DATABASE_URL` is set (should be automatic)
- Run migrations: `python manage.py migrate`
- Check PostgreSQL service is running

**Static Files Not Loading**:
- Make sure `python manage.py collectstatic` runs in build
- Check `STATIC_ROOT` in `settings.py`

### Frontend Issues

**Build Fails**:
- Check that `frontend/nixpacks.toml` exists
- Verify `package.json` has `preview` script
- Check Railway logs

**Can't Connect to Backend**:
- Verify `VITE_API_URL` is set correctly
- Check backend CORS settings allow frontend domain
- Check browser console for CORS errors

**Environment Variables Not Loading**:
- Vite requires `VITE_` prefix for env vars
- Redeploy after changing env vars

## Cost Estimate

**Railway Pricing** (as of 2025):
- **Starter Plan**: $5/month (500 hours)
- **Developer Plan**: $20/month (unlimited hours)

**Estimated Monthly Cost**:
- Backend service: ~$5
- Frontend service: ~$5
- PostgreSQL: ~$5
- **Total**: ~$15-20/month

**Free Tier**:
- $5 free credit/month
- Good for testing/development

## Updating the Application

**Automatic Deployments**:
Railway auto-deploys on git push to main branch.

```bash
# Make changes locally
git add .
git commit -m "feat: your changes"
git push origin main

# Railway will auto-deploy both services
```

## Custom Domain (Optional)

1. Go to service → "Settings" → "Networking"
2. Click "Custom Domain"
3. Add your domain (e.g., `app.pulseofpeople.com`)
4. Update DNS records as shown
5. SSL certificates are automatic

## Monitoring

**Railway Dashboard**:
- View logs in "Deployments" tab
- Monitor resource usage
- Set up alerts for errors

**Health Checks**:
- Backend: `/admin/` or `/api/health/`
- Frontend: Homepage loads correctly

## Backup Strategy

**Database Backups**:
1. Railway provides automatic backups
2. Manual backup: Use Railway CLI
   ```bash
   railway db:backup
   ```

**Code Backups**:
- Code is in GitHub (automatic versioning)
- Can rollback to any commit in Railway

## Support

**Railway Docs**: https://docs.railway.app
**Railway Discord**: https://discord.gg/railway
**Repository Issues**: https://github.com/chatgptnotes/pulseofpeople/issues

---

**Last Updated**: 2025-11-08
**Version**: 1.0
