# Production Setup Quick Start

Fast-track production deployment guide for Pulse of People platform.

## Overview

This guide will help you deploy the platform to production in under 2 hours.

**Stack:**
- Backend: Django + PostgreSQL + Redis + Celery
- Frontend: React + TypeScript + Vite
- Hosting: Railway (backend) + Vercel (frontend)

---

## Quick Start (30 Minutes)

### 1. Prerequisites (5 min)

Create accounts for:
- [Railway](https://railway.app) - Backend hosting
- [Vercel](https://vercel.com) - Frontend hosting
- [SendGrid](https://sendgrid.com) - Email service
- [Sentry](https://sentry.io) - Error tracking

### 2. Fork & Clone (2 min)

```bash
git clone https://github.com/yourusername/pulseofpeople.git
cd pulseofpeople
```

### 3. Backend Setup (10 min)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Create new project
railway init

# Add PostgreSQL
railway add postgres

# Add Redis
railway add redis

# Set environment variables
railway variables set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="your-app.railway.app"

# Deploy backend
cd backend
railway up

# Run migrations
railway run python manage.py migrate
railway run python manage.py createsuperuser
```

### 4. Frontend Setup (10 min)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy frontend
cd ../frontend
vercel --prod

# Set environment variables in Vercel dashboard
# VITE_DJANGO_API_URL = https://your-backend.railway.app
# VITE_MAPBOX_ACCESS_TOKEN = your-mapbox-token
```

### 5. Verify Deployment (3 min)

```bash
# Check backend health
curl https://your-backend.railway.app/api/health/

# Check frontend
open https://your-app.vercel.app
```

---

## Detailed Setup (2 Hours)

### Backend Deployment

#### Step 1: Database Setup

**Option A: Railway PostgreSQL**
```bash
railway add postgres
# Credentials auto-populated in DATABASE_URL
```

**Option B: Supabase**
1. Create project at https://supabase.com
2. Get database credentials from Settings → Database
3. Set in Railway:
```bash
railway variables set DB_HOST="db.your-project.supabase.co"
railway variables set DB_NAME="postgres"
railway variables set DB_USER="postgres"
railway variables set DB_PASSWORD="your-password"
railway variables set DB_PORT="5432"
railway variables set DB_SSLMODE="require"
```

#### Step 2: Redis Setup

```bash
railway add redis
# REDIS_URL auto-populated
```

#### Step 3: Environment Variables

Set all required variables:

```bash
# Django
railway variables set SECRET_KEY="your-secret-key-here"
railway variables set DEBUG="False"
railway variables set ALLOWED_HOSTS="your-app.railway.app,yourdomain.com"

# Security
railway variables set CORS_ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
railway variables set CSRF_TRUSTED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Email (SendGrid)
railway variables set EMAIL_HOST="smtp.sendgrid.net"
railway variables set EMAIL_HOST_USER="apikey"
railway variables set EMAIL_HOST_PASSWORD="your-sendgrid-api-key"
railway variables set DEFAULT_FROM_EMAIL="noreply@yourdomain.com"

# Monitoring
railway variables set SENTRY_DSN="your-sentry-dsn"

# Optional: File Storage (AWS S3)
railway variables set USE_S3="True"
railway variables set AWS_ACCESS_KEY_ID="your-aws-key"
railway variables set AWS_SECRET_ACCESS_KEY="your-aws-secret"
railway variables set AWS_STORAGE_BUCKET_NAME="pulseofpeople-media"
```

#### Step 4: Deploy

```bash
cd backend
railway up

# Watch deployment
railway logs
```

#### Step 5: Post-Deployment

```bash
# Run migrations
railway run python manage.py migrate

# Collect static files
railway run python manage.py collectstatic --noinput

# Create superuser
railway run python manage.py createsuperuser

# Test health endpoint
curl https://your-app.railway.app/api/health/detailed/
```

---

### Frontend Deployment

#### Step 1: Environment Setup

Create `frontend/.env.production`:

```env
VITE_DJANGO_API_URL=https://your-backend.railway.app
VITE_MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token
VITE_SENTRY_DSN=your-sentry-dsn
VITE_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
VITE_APP_NAME=Pulse of People
VITE_APP_URL=https://yourdomain.com
```

#### Step 2: Deploy to Vercel

```bash
cd frontend

# Deploy
vercel --prod

# Or configure via Vercel dashboard:
# 1. Import Git repository
# 2. Framework Preset: Vite
# 3. Build Command: npm run build
# 4. Output Directory: dist
# 5. Add environment variables
```

#### Step 3: Configure Environment in Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings → Environment Variables
4. Add all variables from `.env.production`

---

### Custom Domain Setup

#### Backend Domain (api.yourdomain.com)

**Railway:**
1. Go to Railway dashboard → Settings
2. Domains → Add Custom Domain
3. Enter `api.yourdomain.com`
4. Add CNAME record to your DNS:
   ```
   CNAME api -> your-app.up.railway.app
   ```

#### Frontend Domain (yourdomain.com)

**Vercel:**
1. Go to Vercel dashboard → Settings
2. Domains → Add Domain
3. Follow DNS configuration instructions:
   ```
   A @ -> 76.76.21.21
   CNAME www -> cname.vercel-dns.com
   ```

#### SSL/TLS

Both Railway and Vercel provide automatic SSL certificates via Let's Encrypt.

---

## Monitoring Setup

### Sentry Error Tracking

1. Create project at https://sentry.io
2. Get DSN from Settings → Client Keys
3. Set in environment variables:
   ```bash
   railway variables set SENTRY_DSN="your-dsn"
   ```
4. Frontend: Add to `.env.production`:
   ```env
   VITE_SENTRY_DSN=your-sentry-dsn
   ```

### Uptime Monitoring

1. Sign up for [UptimeRobot](https://uptimerobot.com)
2. Add monitors:
   - Backend: `https://api.yourdomain.com/api/health/`
   - Frontend: `https://yourdomain.com`
3. Configure alerts (email/SMS)

---

## Backup Configuration

### Automated Database Backups

**Method 1: Railway Backups (Recommended)**
```bash
# Enable automatic backups in Railway dashboard
# Settings → Database → Backups
```

**Method 2: Custom Script**
```bash
# On a server with cron
cd backend/scripts
chmod +x backup_database.sh setup_cron.sh
./setup_cron.sh
```

---

## Performance Optimization

### Backend

1. **Enable Redis Caching:**
   ```bash
   railway variables set REDIS_URL="your-redis-url"
   ```

2. **Database Connection Pooling:**
   ```bash
   railway variables set DB_CONN_MAX_AGE="600"
   ```

3. **Gunicorn Workers:**
   ```toml
   # railway.toml
   startCommand = "gunicorn config.wsgi:application --workers 4 --threads 2"
   ```

### Frontend

1. **Build Optimizations** (already configured):
   - Code splitting
   - Tree shaking
   - Minification
   - Gzip compression

2. **Vercel CDN** (automatic):
   - Global edge network
   - Asset caching
   - Brotli compression

---

## Security Checklist

- [ ] DEBUG=False in production
- [ ] Unique SECRET_KEY generated
- [ ] ALLOWED_HOSTS configured
- [ ] CORS_ALLOWED_ORIGINS restricted
- [ ] SSL/TLS enabled
- [ ] Security headers configured
- [ ] Database uses SSL (sslmode=require)
- [ ] No secrets in code
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled

---

## Common Issues

### "DisallowedHost" Error
```bash
railway variables set ALLOWED_HOSTS="your-app.railway.app,yourdomain.com"
```

### "CORS Error"
```bash
railway variables set CORS_ALLOWED_ORIGINS="https://yourdomain.com"
```

### "Database Connection Failed"
Check database credentials:
```bash
railway variables
```

### "Static Files Not Loading"
```bash
railway run python manage.py collectstatic --noinput --clear
```

---

## Cost Estimates

**Monthly Costs (approximate):**

| Service | Plan | Cost |
|---------|------|------|
| Railway (Hobby) | 5GB RAM, 5GB storage | $5 |
| Railway PostgreSQL | Addon | Included |
| Railway Redis | Addon | Included |
| Vercel (Hobby) | Unlimited bandwidth | $0 |
| SendGrid (Free) | 100 emails/day | $0 |
| Sentry (Developer) | 5K errors/month | $0 |
| **Total** | | **~$5/month** |

**Production/Scale:**
- Railway Pro: $20/month
- Vercel Pro: $20/month
- SendGrid Essentials: $20/month
- Sentry Team: $26/month
- **Total:** ~$86/month

---

## Next Steps

1. ✅ Review [PRODUCTION_CHECKLIST.md](../PRODUCTION_CHECKLIST.md)
2. ✅ Read [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
3. ✅ Configure monitoring and alerts
4. ✅ Setup automated backups
5. ✅ Train your team
6. ✅ Plan for scaling

---

## Support

- **Documentation:** https://github.com/yourusername/pulseofpeople/docs
- **Issues:** https://github.com/yourusername/pulseofpeople/issues
- **Email:** support@pulseofpeople.com
