# Installation & Setup Guide

## Pulse of People - Security, Testing & Optimization

Quick start guide for installing and running the enhanced security and testing features.

---

## Prerequisites

- Python 3.10+
- Node.js 22.0.0+
- PostgreSQL 14+ (or SQLite for development)
- Redis 6+ (for caching and rate limiting)
- Git

---

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd pulseofpeople
```

---

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2.2 Install Dependencies

```bash
pip install -r requirements.txt
```

**New dependencies installed:**
- django-ratelimit (rate limiting)
- django-otp, pyotp, qrcode (2FA)
- python-magic (file validation)
- bleach (HTML sanitization)
- django-redis, redis (caching)
- sentry-sdk (error tracking)
- locust (load testing)
- factory-boy, faker (test data)

### 2.3 Install Redis

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Windows (WSL or Docker):**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Verify Redis:**
```bash
redis-cli ping
# Should return: PONG
```

### 2.4 Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
cd backend
cp .env.example .env  # If you have an example file
# OR create new .env
nano .env
```

**Development .env:**
```env
# Django
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite for development)
USE_SQLITE=True

# Redis
REDIS_URL=redis://127.0.0.1:6379/1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Application
API_VERSION=v1
APP_NAME=Pulse of People
APP_VERSION=1.0.0
```

**Production .env:**
```env
# Django
SECRET_KEY=<generate-strong-random-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
ENVIRONMENT=production

# Database (PostgreSQL)
USE_SQLITE=False
DB_NAME=pulseofpeople
DB_USER=postgres
DB_PASSWORD=<your-secure-password>
DB_HOST=your-db-host.com
DB_PORT=5432

# Redis
REDIS_URL=redis://your-redis-host:6379/1

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Sentry (optional but recommended)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Application
API_VERSION=v1
APP_NAME=Pulse of People
APP_VERSION=1.0.0
```

### 2.5 Create Database & Run Migrations

```bash
# Create database (PostgreSQL - if not using SQLite)
createdb pulseofpeople

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 2.6 Create Logs Directory

```bash
mkdir -p logs
chmod 755 logs
```

### 2.7 Run Development Server

```bash
python manage.py runserver
# Server runs at: http://127.0.0.1:8000
```

---

## Step 3: Frontend Setup

### 3.1 Install Dependencies

```bash
cd ../frontend
npm install
```

**New dependencies installed:**
- @testing-library/react
- @testing-library/jest-dom
- @testing-library/user-event
- @playwright/test
- @vitest/ui
- @vitest/coverage-v8
- jsdom

### 3.2 Configure Environment Variables

Create `.env` file in `frontend/` directory:

```bash
nano .env
```

**Development .env:**
```env
VITE_API_URL=http://127.0.0.1:8000
VITE_MAPBOX_ACCESS_TOKEN=your-mapbox-token
VITE_APP_NAME=Pulse of People
VITE_APP_VERSION=1.0.0
```

**Production .env:**
```env
VITE_API_URL=https://api.yourdomain.com
VITE_MAPBOX_ACCESS_TOKEN=your-mapbox-token
VITE_APP_NAME=Pulse of People
VITE_APP_VERSION=1.0.0
```

### 3.3 Run Development Server

```bash
npm run dev
# Server runs at: http://localhost:5173
```

---

## Step 4: Verify Installation

### 4.1 Check Backend

```bash
cd backend

# Run system check
python manage.py check

# Run tests
python manage.py test

# Check Redis connection
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'working')
>>> cache.get('test')
'working'
>>> exit()
```

### 4.2 Check Frontend

```bash
cd frontend

# Run tests
npm run test

# Build (should complete without errors)
npm run build
```

### 4.3 Access Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://127.0.0.1:8000/api/
- **Django Admin:** http://127.0.0.1:8000/admin/

---

## Step 5: Run Tests

### 5.1 Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run specific test modules
python manage.py test api.tests.test_models
python manage.py test api.tests.test_validators
python manage.py test api.tests.test_api_auth

# Run with coverage
pip install coverage
coverage run --source='api' manage.py test
coverage report
coverage html
# Open htmlcov/index.html in browser
```

### 5.2 Load Tests

```bash
cd backend

# Start load test (Web UI)
locust -f locustfile.py --host=http://127.0.0.1:8000
# Open http://localhost:8089 in browser

# Headless load test
locust -f locustfile.py --host=http://127.0.0.1:8000 \
  --users 100 --spawn-rate 10 --run-time 1m --headless
```

### 5.3 Frontend Tests

```bash
cd frontend

# Unit tests
npm run test

# E2E tests (install Playwright first)
npx playwright install
npx playwright test
```

---

## Step 6: Production Deployment

### 6.1 Backend Production Setup

```bash
cd backend

# Install production dependencies
pip install gunicorn argon2-cffi

# Collect static files
python manage.py collectstatic --noinput

# Run with Gunicorn
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --timeout 60 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info
```

### 6.2 Frontend Production Build

```bash
cd frontend

# Build for production
npm run build

# Preview production build
npm run preview
```

### 6.3 Configure Production Services

**Redis (Production):**
```bash
# Configure Redis with password
redis-cli
> CONFIG SET requirepass yourpassword
> AUTH yourpassword
> exit

# Update REDIS_URL in .env
REDIS_URL=redis://:yourpassword@localhost:6379/1
```

**PostgreSQL (Production):**
```bash
# Create production database
createdb pulseofpeople -O postgres

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**Nginx (Optional - Reverse Proxy):**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/backend/staticfiles/;
    }

    location /media/ {
        alias /path/to/backend/media/;
    }
}
```

---

## Step 7: Configure Monitoring

### 7.1 Sentry Setup

1. Create account at https://sentry.io
2. Create new Django project
3. Get DSN from project settings
4. Add to `.env`:
   ```env
   SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
   ```
5. Restart application

### 7.2 Log Monitoring

```bash
# Watch logs in real-time
tail -f backend/logs/app.log
tail -f backend/logs/error.log
tail -f backend/logs/security.log
```

---

## Step 8: Common Issues & Solutions

### Issue: Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Issue: Database Migration Error

```bash
# Reset database (DEVELOPMENT ONLY)
python manage.py flush
python manage.py migrate

# OR delete database and recreate
dropdb pulseofpeople
createdb pulseofpeople
python manage.py migrate
```

### Issue: Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Issue: Missing Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt --force-reinstall

# Frontend
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Tests Failing

```bash
# Clear cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Reset test database
python manage.py test --keepdb=False
```

---

## Step 9: Security Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to strong random value
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Configure CORS_ALLOWED_ORIGINS
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure Redis with password
- [ ] Set strong database password
- [ ] Enable Sentry monitoring
- [ ] Configure backup strategy
- [ ] Review security logs
- [ ] Run security audit: `python manage.py check --deploy`
- [ ] Update all dependencies
- [ ] Enable firewall rules
- [ ] Configure rate limiting
- [ ] Test 2FA functionality

---

## Step 10: Quick Commands Reference

### Development

```bash
# Backend
python manage.py runserver
python manage.py shell
python manage.py test
python manage.py makemigrations
python manage.py migrate

# Frontend
npm run dev
npm run build
npm run test
npm run lint
```

### Production

```bash
# Backend
gunicorn config.wsgi:application --bind 0.0.0.0:8000
python manage.py collectstatic --noinput
python manage.py check --deploy

# Frontend
npm run build
npm run preview
```

### Monitoring

```bash
# Logs
tail -f backend/logs/app.log
tail -f backend/logs/error.log

# Redis
redis-cli INFO stats

# Database
python manage.py dbshell
```

---

## Support

For detailed documentation, see:
- **SECURITY_TESTING_DOCUMENTATION.md** - Complete security & testing guide
- **QUICK_REFERENCE.md** - Common commands and troubleshooting
- **IMPLEMENTATION_SUMMARY.md** - Feature overview and checklist

---

**Installation Complete!** 🎉

Your Pulse of People platform is now set up with enterprise-grade security, comprehensive testing, and optimized performance.

Next steps:
1. Review documentation in SECURITY_TESTING_DOCUMENTATION.md
2. Run tests to verify everything works
3. Configure production environment variables
4. Deploy to production when ready

---

**Last Updated:** 2025-11-09
**Version:** 1.0
