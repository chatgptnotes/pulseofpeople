# Deployment Guide - Pulse of People Platform

## Quick Reference

**Local Development:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Database: SQLite (local file)

**Production:**
- Frontend: https://www.pulseofpeople.com (Vercel)
- Backend: https://pulseofpeople-backend.onrender.com (Render)
- Database: PostgreSQL (Supabase Cloud)

---

## Environment Variables Summary

### Backend Environment Variables

#### Development (/.env)
```env
SECRET_KEY=django-insecure-development-key-change-in-production-k-lz$^&9-j@#cn(c4**fhr8r&fhm46&rq%952d0&=%)u32s\(g
DEBUG=True
USE_SQLITE=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://127.0.0.1:8000
```

#### Production (Render Environment Variables)
```env
# Django Core
SECRET_KEY=django-insecure-%\5wu$@chhaxd4=+xjcsu=8^6s#$y@-jw4yn%l#0*_ldb\pn=%
DEBUG=False
ALLOWED_HOSTS=pulseofpeople-backend.onrender.com,.onrender.com,pulseofpeople.com,www.pulseofpeople.com

# Database (PostgreSQL on Supabase)
USE_SQLITE=False
DB_NAME=postgres
DB_USER=postgres.iwtgbseaoztjbnvworyq
DB_PASSWORD=Chindwada@1
DB_HOST=aws-1-ap-south-1.pooler.supabase.com
DB_PORT=6543
DB_SSLMODE=require

# Supabase Auth
SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94
SUPABASE_JWT_SECRET=X6j+39tynhesQLZuzPc9IXP8H9UONWcKmkKdonFBnrvIqXMO+T+PACOWxpks6fVaKoPblX0FPyI3vc3X5J1x7g==

# CORS & Security
CORS_ALLOWED_ORIGINS=https://www.pulseofpeople.com,https://pulseofpeople.com
CSRF_TRUSTED_ORIGINS=https://www.pulseofpeople.com,https://pulseofpeople-backend.onrender.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# URLs
FRONTEND_URL=https://www.pulseofpeople.com
BACKEND_URL=https://pulseofpeople-backend.onrender.com
```

---

### Frontend Environment Variables

#### Development (/.env)
```env
# Supabase
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94

# Backend API
VITE_API_URL=http://localhost:8000/api
VITE_DJANGO_API_URL=http://localhost:8000/api
VITE_BACKEND_URL=http://localhost:8000

# App Settings
VITE_APP_URL=http://localhost:5173
VITE_ENVIRONMENT=development
VITE_DEV_MODE=true
VITE_MULTI_TENANT=false
```

#### Production (Vercel Environment Variables)
Set these in Vercel Dashboard → Project Settings → Environment Variables:

```env
# Supabase (same as development)
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94

# Backend API (production)
VITE_API_URL=https://pulseofpeople-backend.onrender.com/api
VITE_DJANGO_API_URL=https://pulseofpeople-backend.onrender.com/api
VITE_BACKEND_URL=https://pulseofpeople-backend.onrender.com

# App Settings
VITE_APP_URL=https://www.pulseofpeople.com
VITE_ENVIRONMENT=production
VITE_DEV_MODE=false
VITE_MULTI_TENANT=false

# Mapbox (get production token)
VITE_MAPBOX_ACCESS_TOKEN=your-production-mapbox-token
```

---

## Deployment Steps

### Backend Deployment (Render)

1. **Create Web Service on Render:**
   - Repository: Link your GitHub repo
   - Branch: `main`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn config.wsgi:application`

2. **Add Environment Variables:**
   - Copy all production variables from above
   - Set in Render Dashboard → Environment → Environment Variables

3. **Database Migration:**
   ```bash
   # Run migrations on Render (or via shell)
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

4. **Custom Domain:**
   - Add CNAME record: `api.pulseofpeople.com` → `pulseofpeople-backend.onrender.com`
   - Or use default: `pulseofpeople-backend.onrender.com`

### Frontend Deployment (Vercel)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login and Deploy:**
   ```bash
   cd frontend
   vercel login
   vercel
   ```

3. **Configure Project:**
   - Project Name: `bettroi-voter-sentiment-dashboard`
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Add Environment Variables:**
   - Go to Vercel Dashboard → Project Settings → Environment Variables
   - Add all production variables from above

5. **Custom Domain:**
   - Add domain: `www.pulseofpeople.com`
   - Vercel will provide DNS instructions (usually CNAME or A record)

### Database Setup (Supabase)

**Already Configured:**
- Project: `pulseofpeople` (iwtgbseaoztjbnvworyq)
- Region: `ap-south-1` (Mumbai)
- Database Password: `Chindwada@1`
- Connection: Session Pooler (Port 6543)

**Run Migrations:**
```bash
# Local: Apply Django migrations to Supabase PostgreSQL
cd backend
source venv/bin/activate
export USE_SQLITE=False
python manage.py migrate
```

---

## Health Checks

### Backend Health Check
```bash
# Development
curl http://localhost:8000/api/health/

# Production
curl https://pulseofpeople-backend.onrender.com/api/health/
```

### Frontend Health Check
```bash
# Development
curl http://localhost:5173/

# Production
curl https://www.pulseofpeople.com/
```

### Database Health Check
```bash
# Test PostgreSQL connection
psql "postgresql://postgres.iwtgbseaoztjbnvworyq:Chindwada@1@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

---

## Troubleshooting

### CORS Errors
**Symptom:** Frontend can't connect to backend

**Solution:**
1. Check `CORS_ALLOWED_ORIGINS` in backend .env
2. Ensure frontend URL is included (with protocol: `https://`)
3. Check `CSRF_TRUSTED_ORIGINS` includes both frontend and backend URLs

### Database Connection Errors
**Symptom:** `django.db.utils.OperationalError`

**Solution:**
1. Check `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`
2. Ensure `DB_SSLMODE=require` for Supabase
3. Verify IP allowlist in Supabase Dashboard (set to allow all: `0.0.0.0/0`)

### Authentication Not Working
**Symptom:** Login fails or JWT invalid

**Solution:**
1. Check `SUPABASE_JWT_SECRET` matches Supabase Dashboard → Settings → API → JWT Secret
2. Verify `SUPABASE_ANON_KEY` is correct
3. Check token expiry (tokens expire after 1 hour by default)

### Build Failures
**Symptom:** Vercel/Render build fails

**Solution:**
1. Check Node version (should be >=18.0.0)
2. Check Python version (should be 3.10+)
3. Verify all dependencies in `requirements.txt` / `package.json`
4. Check build logs for specific errors

---

## Security Checklist

- [ ] Change `SECRET_KEY` in production (never use development key)
- [ ] Set `DEBUG=False` in production
- [ ] Enable SSL redirect (`SECURE_SSL_REDIRECT=True`)
- [ ] Set secure cookies (`SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`)
- [ ] Restrict `ALLOWED_HOSTS` to your domains only
- [ ] Rotate database password regularly
- [ ] Enable Supabase RLS policies
- [ ] Configure proper CORS origins (no wildcards in production)
- [ ] Set up Sentry for error tracking
- [ ] Enable rate limiting
- [ ] Review Django security settings: https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

---

## Monitoring

### Backend Logs (Render)
```
Render Dashboard → Your Service → Logs
```

### Frontend Logs (Vercel)
```
Vercel Dashboard → Your Project → Deployments → [Latest] → View Function Logs
```

### Database Metrics (Supabase)
```
Supabase Dashboard → Project → Reports
```

---

## Backup & Recovery

### Database Backups (Supabase)
- Automatic daily backups (Point-in-Time Recovery enabled)
- Manual backup: Supabase Dashboard → Database → Backups

### Code Backups
- Git repository on GitHub
- Vercel/Render automatically deploy from Git

---

## Cost Estimates

### Current Setup (Development)
- Frontend (Vercel): **Free** (Hobby plan)
- Backend (Render): **Free** (Free tier)
- Database (Supabase): **Free** (Free tier - 500MB, 2GB bandwidth)

### Production Estimates (when scaled)
- Frontend (Vercel): **$20/month** (Pro plan)
- Backend (Render): **$7-25/month** (Starter/Standard plan)
- Database (Supabase): **$25/month** (Pro plan - 8GB, 50GB bandwidth)

**Total: ~$52-70/month**

---

## Support

- Supabase Dashboard: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
- Render Dashboard: https://dashboard.render.com
- Vercel Dashboard: https://vercel.com/dashboard
- GitHub Repo: (add your repo URL here)

---

**Last Updated:** 2025-11-09
**Maintained by:** Pulse of People Team
