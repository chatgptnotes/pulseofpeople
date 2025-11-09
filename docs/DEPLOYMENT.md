# Production Deployment Guide

Complete guide for deploying Pulse of People platform to production.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Backend Deployment](#backend-deployment)
- [Frontend Deployment](#frontend-deployment)
- [Post-Deployment](#post-deployment)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Accounts
- [ ] Railway or Render account (backend hosting)
- [ ] Vercel account (frontend hosting)
- [ ] PostgreSQL database (Railway addon or Supabase)
- [ ] Redis instance (Railway addon or Upstash)
- [ ] AWS S3 bucket (optional, for file storage)
- [ ] SendGrid account (for emails)
- [ ] Sentry account (for error tracking)
- [ ] Domain name (for custom domain)

### Required Tools
- [ ] Git
- [ ] Node.js >= 18.0.0
- [ ] Python >= 3.10
- [ ] Railway CLI or Render CLI
- [ ] Vercel CLI

---

## Environment Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/pulseofpeople.git
cd pulseofpeople
```

### 2. Configure Backend Environment

Copy the production environment template:
```bash
cd backend
cp .env.production.example .env.production
```

Edit `.env.production` and set all required values:
- `SECRET_KEY` - Generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DEBUG=False`
- `ALLOWED_HOSTS` - Your production domains
- Database credentials
- Redis URL
- Email settings
- API keys

### 3. Configure Frontend Environment

```bash
cd frontend
cp .env.production.example .env.production
```

Edit `.env.production`:
- `VITE_DJANGO_API_URL` - Your backend API URL
- `VITE_MAPBOX_ACCESS_TOKEN` - Your Mapbox token
- `VITE_SENTRY_DSN` - Your Sentry DSN
- Other configuration values

---

## Database Setup

### Option 1: Railway PostgreSQL

1. Create Railway project:
```bash
railway init
```

2. Add PostgreSQL service:
```bash
railway add postgres
```

3. Get connection details:
```bash
railway variables
```

4. Update backend `.env.production` with database credentials

### Option 2: Supabase

1. Create Supabase project at https://supabase.com
2. Navigate to Settings → Database
3. Copy connection string
4. Update backend `.env.production`:
```env
DB_HOST=db.your-project-ref.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password
DB_SSLMODE=require
```

### Run Migrations

```bash
cd backend
python manage.py migrate --settings=config.settings_production
```

### Create Superuser

```bash
python manage.py createsuperuser --settings=config.settings_production
```

---

## Backend Deployment

### Option 1: Deploy to Railway

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

2. **Link to Railway project:**
```bash
cd backend
railway link
```

3. **Set environment variables:**
```bash
railway variables set SECRET_KEY="your-secret-key"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="your-domain.com"
# Set all other environment variables
```

4. **Deploy:**
```bash
railway up
```

5. **Run migrations:**
```bash
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
railway run python manage.py createsuperuser
```

6. **Check deployment:**
```bash
railway logs
railway open
```

### Option 2: Deploy to Render

1. **Create render.yaml:**
```yaml
services:
  - type: web
    name: pulseofpeople-backend
    env: python
    buildCommand: "pip install -r requirements.txt && python manage.py collectstatic --noinput"
    startCommand: "gunicorn config.wsgi:application"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DJANGO_SETTINGS_MODULE
        value: config.settings_production
```

2. **Connect to Render:**
   - Go to https://dashboard.render.com
   - New → Web Service
   - Connect your Git repository
   - Configure environment variables
   - Deploy

### Option 3: Docker Deployment

1. **Build Docker image:**
```bash
cd backend
docker build -t pulseofpeople-backend .
```

2. **Run with docker-compose:**
```bash
cd ..
docker-compose -f docker-compose.yml up -d
```

3. **Check logs:**
```bash
docker-compose logs -f backend
```

---

## Frontend Deployment

### Deploy to Vercel

1. **Install Vercel CLI:**
```bash
npm install -g vercel
```

2. **Login to Vercel:**
```bash
vercel login
```

3. **Deploy:**
```bash
cd frontend
vercel --prod
```

4. **Set environment variables in Vercel dashboard:**
   - Go to https://vercel.com/dashboard
   - Select your project
   - Settings → Environment Variables
   - Add all variables from `.env.production`

5. **Configure custom domain (optional):**
   - Domains → Add Domain
   - Follow DNS configuration instructions

### Alternative: Netlify

1. **Create netlify.toml:**
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

2. **Deploy:**
```bash
npm install -g netlify-cli
netlify login
netlify deploy --prod
```

---

## Post-Deployment

### 1. Verify Health Checks

```bash
# Backend health check
curl https://api.yourdomain.com/api/health/detailed/

# Frontend health check
curl https://yourdomain.com/
```

### 2. Configure DNS

Add the following DNS records:

| Type  | Name          | Value                          | TTL  |
|-------|---------------|--------------------------------|------|
| A     | @             | Vercel IP                      | Auto |
| CNAME | www           | cname.vercel-dns.com           | Auto |
| CNAME | api           | your-app.up.railway.app        | Auto |

### 3. Enable SSL/TLS

Both Railway and Vercel provide automatic SSL certificates.

For custom domains:
- Vercel: Automatic via Let's Encrypt
- Railway: Automatic via Let's Encrypt

### 4. Setup Monitoring

#### Sentry Error Tracking
```bash
# Already configured via environment variables
# Visit https://sentry.io to view errors
```

#### Uptime Monitoring
- Sign up for UptimeRobot or similar
- Monitor endpoints:
  - `https://yourdomain.com`
  - `https://api.yourdomain.com/api/health/`

### 5. Configure Automated Backups

```bash
# On your production server
cd backend/scripts
chmod +x backup_database.sh
chmod +x setup_cron.sh
./setup_cron.sh
```

Or configure Railway automated backups:
```bash
railway run python manage.py dbbackup
```

### 6. Setup CI/CD (Optional)

See [CI/CD Configuration Guide](CI_CD.md)

---

## Verification Checklist

After deployment, verify:

### Backend
- [ ] API health check returns 200
- [ ] Admin panel accessible at `/admin/`
- [ ] Database migrations completed
- [ ] Static files serving correctly
- [ ] CORS configured properly
- [ ] SSL/TLS enabled
- [ ] Environment variables set
- [ ] Logs accessible

### Frontend
- [ ] Homepage loads
- [ ] Login works
- [ ] API calls succeed
- [ ] Mapbox maps render
- [ ] SSL/TLS enabled
- [ ] Custom domain configured
- [ ] Analytics tracking

### Infrastructure
- [ ] Database accessible
- [ ] Redis cache working
- [ ] Celery workers running (if applicable)
- [ ] Email sending works
- [ ] File uploads work
- [ ] Backups configured
- [ ] Monitoring active

---

## Troubleshooting

### Backend Issues

#### "DisallowedHost" Error
**Problem:** Django rejecting requests
**Solution:**
```python
# In .env.production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,api.yourdomain.com
```

#### "Database connection failed"
**Problem:** Cannot connect to PostgreSQL
**Solution:**
- Verify database credentials
- Check database is running
- Verify SSL mode: `DB_SSLMODE=require`
- Check firewall/network rules

#### "Static files not loading"
**Problem:** CSS/JS files 404
**Solution:**
```bash
python manage.py collectstatic --noinput --clear
```

### Frontend Issues

#### "Network Error" when calling API
**Problem:** CORS or API URL misconfigured
**Solution:**
- Verify `VITE_DJANGO_API_URL` in frontend
- Verify `CORS_ALLOWED_ORIGINS` in backend
- Check browser console for specific error

#### "Mapbox not loading"
**Problem:** Invalid or missing Mapbox token
**Solution:**
```env
VITE_MAPBOX_ACCESS_TOKEN=pk.your-valid-token
```

### Performance Issues

#### Slow API responses
**Solutions:**
- Enable Redis caching
- Optimize database queries
- Add database indexes
- Scale Railway service

#### High memory usage
**Solutions:**
- Reduce Gunicorn workers
- Enable connection pooling
- Optimize queries with `.select_related()` and `.prefetch_related()`

---

## Rollback Procedure

If deployment fails:

### Backend Rollback
```bash
# Railway
railway down
railway rollback

# Or restore from backup
cd backend/scripts
./restore_database.sh --latest
```

### Frontend Rollback
```bash
# Vercel
vercel rollback
```

---

## Additional Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [Railway Documentation](https://docs.railway.app/)
- [Vercel Documentation](https://vercel.com/docs)

---

## Support

For deployment issues:
- GitHub Issues: https://github.com/yourusername/pulseofpeople/issues
- Email: support@pulseofpeople.com
- Documentation: https://docs.pulseofpeople.com
