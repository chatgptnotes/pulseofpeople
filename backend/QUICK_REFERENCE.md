# Quick Reference Guide

## Security, Testing & Optimization - Quick Commands

---

## Installation

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install
```

---

## Development

### Start Development Servers

```bash
# Backend (Django)
cd backend
python manage.py runserver

# Frontend (Vite)
cd frontend
npm run dev
```

### Apply Database Changes

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
python manage.py test

# Run specific test file
python manage.py test api.tests.test_models
python manage.py test api.tests.test_validators
python manage.py test api.tests.test_api_auth

# Run with parallel execution
python manage.py test --parallel

# Keep database between test runs (faster)
python manage.py test --keepdb

# Verbose output
python manage.py test --verbosity=2
```

### Test Coverage

```bash
cd backend

# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='api' manage.py test

# Generate report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

### Load Testing

```bash
cd backend

# Basic load test (Web UI)
locust -f locustfile.py --host=http://localhost:8000

# Headless load test
locust -f locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 1m --headless

# Stress test (1000 users)
locust -f locustfile.py --host=http://localhost:8000 \
  --users 1000 --spawn-rate 50 --run-time 5m --headless StressTest

# Endurance test (1 hour)
locust -f locustfile.py --host=http://localhost:8000 \
  --users 100 --spawn-rate 10 --run-time 1h EnduranceTest
```

### Frontend Tests

```bash
cd frontend

# Run unit tests
npm run test

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage

# E2E tests with Playwright
npx playwright test

# E2E tests with UI mode
npx playwright test --ui

# E2E tests headed (see browser)
npx playwright test --headed
```

---

## Security Operations

### 2FA Management

```python
# In Django shell
python manage.py shell

from django.contrib.auth.models import User
from api.services.two_factor_service import TwoFactorService

# Setup 2FA for a user
user = User.objects.get(username='admin')
setup_data = TwoFactorService.setup_2fa_for_user(user)
print(setup_data['backup_codes'])

# Check 2FA status
status = TwoFactorService.get_2fa_status(user)
print(status)

# Verify code
success, message = TwoFactorService.verify_2fa_code(user, '123456')
print(message)
```

### Input Validation Examples

```python
from api.validators import *

# Validate phone number
validate_phone_number('9876543210')  # OK
validate_phone_number('+919876543210')  # OK

# Validate email
validate_email('user@example.com')  # Returns True

# Sanitize HTML
clean = sanitize_html('<p>Hello <script>alert("xss")</script></p>')
# Returns: '<p>Hello </p>'

# Validate file
from django.core.files.uploadedfile import SimpleUploadedFile
file = request.FILES.get('upload')
validate_file_upload(file)  # Raises ValidationError if invalid
```

---

## Caching Operations

### Clear Cache

```bash
# Django shell
python manage.py shell

from django.core.cache import cache

# Clear all cache
cache.clear()

# Delete specific key
cache.delete('voter_stats_123')

# Get cache stats
import redis
r = redis.Redis(host='localhost', port=6379, db=1)
print(r.info('stats'))
```

### Set Cache

```python
from django.core.cache import cache
from django.conf import settings

# Cache data
cache_key = 'voter_stats_123'
data = {'total': 1000, 'active': 850}
cache.set(cache_key, data, settings.CACHE_TTL['voter_stats'])

# Get cached data
cached_data = cache.get(cache_key)

# Get or set (atomic)
data = cache.get_or_set(cache_key, expensive_function, timeout=300)
```

---

## Monitoring & Logging

### View Logs

```bash
# Real-time application logs
tail -f backend/logs/app.log

# Real-time error logs
tail -f backend/logs/error.log

# Real-time security logs
tail -f backend/logs/security.log

# View last 100 lines
tail -n 100 backend/logs/app.log

# Search logs
grep "ERROR" backend/logs/app.log
grep "Failed login" backend/logs/security.log
```

### Log from Code

```python
import logging

# Get logger
logger = logging.getLogger('api')
security_logger = logging.getLogger('api.security')

# Log levels
logger.debug('Debug message')
logger.info('Info message')
logger.warning('Warning message')
logger.error('Error message')
logger.critical('Critical message')

# Log with exception traceback
try:
    risky_operation()
except Exception as e:
    logger.error(f'Operation failed: {e}', exc_info=True)

# Security logging
security_logger.warning(
    f'Failed login attempt for {email} from {ip_address}'
)
```

---

## Database Operations

### Create Superuser

```bash
python manage.py createsuperuser
# Follow prompts
```

### Database Backup

```bash
# PostgreSQL
pg_dump -U postgres pulseofpeople > backup_$(date +%Y%m%d).sql

# SQLite
cp backend/db.sqlite3 backup_$(date +%Y%m%d).sqlite3
```

### Database Restore

```bash
# PostgreSQL
psql -U postgres pulseofpeople < backup_20251109.sql

# SQLite
cp backup_20251109.sqlite3 backend/db.sqlite3
```

### Check Database

```bash
python manage.py dbshell

# PostgreSQL
\dt  # List tables
\d+ api_userprofile  # Describe table
SELECT COUNT(*) FROM api_userprofile;
\q  # Quit

# SQLite
.tables  # List tables
.schema api_userprofile  # Show schema
SELECT COUNT(*) FROM api_userprofile;
.quit  # Quit
```

---

## Performance Checks

### Django System Check

```bash
# Development checks
python manage.py check

# Production checks
python manage.py check --deploy

# Security checks
python manage.py check --tag security
```

### Query Performance

```python
# Django shell
python manage.py shell

from django.db import connection
from django.conf import settings

# Enable query logging
settings.DEBUG = True

# Run your code
from api.models import DirectFeedback
feedback = DirectFeedback.objects.filter(status='pending')[:10]

# View queries
for query in connection.queries:
    print(f"{query['time']}: {query['sql']}")

# Reset query log
connection.queries_log.clear()
```

### Check Slow Queries

```bash
# PostgreSQL
psql -U postgres pulseofpeople

SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

---

## Production Deployment

### Collect Static Files

```bash
cd backend
python manage.py collectstatic --noinput
```

### Run with Gunicorn

```bash
gunicorn config.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --threads 2 \
  --timeout 60 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info
```

### Environment Variables Check

```bash
# Check if all required variables are set
python manage.py shell

import os
print("SECRET_KEY:", bool(os.environ.get('SECRET_KEY')))
print("DEBUG:", os.environ.get('DEBUG'))
print("DB_NAME:", os.environ.get('DB_NAME'))
print("REDIS_URL:", os.environ.get('REDIS_URL'))
print("SENTRY_DSN:", bool(os.environ.get('SENTRY_DSN')))
```

---

## Common Issues & Fixes

### Redis Connection Error

```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# Start Redis (Linux)
sudo systemctl start redis

# Start Redis (Mac)
brew services start redis

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:alpine
```

### Database Connection Error

```bash
# PostgreSQL
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check connection
psql -U postgres -h localhost -d pulseofpeople

# Reset database
python manage.py migrate --run-syncdb
```

### Rate Limiting Issues

```python
# Disable rate limiting temporarily (development only)
# In settings.py
RATELIMIT_ENABLE = False
```

### Clear All Caches

```bash
# Django cache
python manage.py shell -c "from django.core.cache import cache; cache.clear()"

# Redis
redis-cli FLUSHDB
```

---

## Useful Django Commands

```bash
# Create new app
python manage.py startapp myapp

# Create migrations
python manage.py makemigrations

# Show migrations
python manage.py showmigrations

# Migrate to specific migration
python manage.py migrate api 0006

# Rollback migration
python manage.py migrate api 0005

# SQL for migration
python manage.py sqlmigrate api 0007

# Shell with IPython
python manage.py shell

# Create test data
python manage.py shell < scripts/create_test_data.py
```

---

## Security Checks

### OWASP ZAP Scan

```bash
# Install OWASP ZAP
# https://www.zaproxy.org/download/

# Quick scan
zap-cli quick-scan http://localhost:8000

# Full scan
zap-cli active-scan http://localhost:8000
```

### Dependency Audit

```bash
# Backend
pip install safety
safety check

# Frontend
npm audit
npm audit fix
```

### Password Hash Upgrade

```bash
# If you change PASSWORD_HASHERS, upgrade existing passwords
python manage.py changepassword username
```

---

## Monitoring URLs

```
# Application
http://localhost:8000/admin/          # Django admin
http://localhost:8000/api/            # API root

# Development
http://localhost:5173/                # Frontend dev server
http://localhost:8000/metrics/        # Prometheus metrics (if enabled)

# Load Testing
http://localhost:8089/                # Locust web UI
```

---

## Emergency Procedures

### Application Down

1. Check logs: `tail -f logs/error.log`
2. Check database: `python manage.py dbshell`
3. Check Redis: `redis-cli ping`
4. Restart application server
5. Check Sentry for errors

### High CPU Usage

1. Check slow queries: `django-admin dbshell`
2. Review cache hit rate
3. Check for infinite loops in logs
4. Restart workers: `sudo systemctl restart gunicorn`

### Security Incident

1. Check security logs: `grep "SECURITY" logs/security.log`
2. Review failed login attempts
3. Check for suspicious patterns in access logs
4. Temporarily increase rate limits if needed
5. Report to security team

### Database Full

1. Check disk space: `df -h`
2. Archive old audit logs
3. Vacuum PostgreSQL: `VACUUM FULL;`
4. Clear old sessions: `python manage.py clearsessions`

---

## Support & Resources

- Django Docs: https://docs.djangoproject.com/
- DRF Docs: https://www.django-rest-framework.org/
- Redis Docs: https://redis.io/docs/
- Sentry Docs: https://docs.sentry.io/
- Locust Docs: https://docs.locust.io/

---

**Last Updated:** 2025-11-09
**Version:** 1.0
