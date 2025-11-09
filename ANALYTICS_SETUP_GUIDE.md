# Analytics System - Quick Setup Guide

## Step-by-Step Installation

### 1. Install Analytics Dependencies

```bash
cd /Users/murali/Downloads/pulseofpeople/backend

# Install analytics packages
pip install reportlab==4.2.2
pip install weasyprint==63.1
pip install openpyxl==3.1.5
pip install matplotlib==3.9.4
pip install seaborn==0.13.2
pip install plotly==5.24.1
pip install celery==5.4.0
pip install redis==5.2.1
pip install django-celery-beat==2.7.0
pip install pandas==2.2.3
pip install numpy==2.2.3
```

Or install from requirements file:
```bash
pip install -r requirements_analytics.txt
```

### 2. Install and Start Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Update Django Settings

Add to `backend/config/settings.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'

# Email Configuration (for report delivery)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  # For development
# For production:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@example.com'
# EMAIL_HOST_PASSWORD = 'your-password'
```

### 4. Update Django INSTALLED_APPS

Add to `backend/config/settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'django_celery_beat',
]
```

### 5. Update __init__.py

Create/update `backend/config/__init__.py`:

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 6. Update URL Configuration

Add to `backend/config/urls.py`:

```python
from django.urls import path, include
from api.urls import analytics_urls

urlpatterns = [
    # ... existing patterns
    path('api/', include('api.urls.analytics_urls')),
]
```

### 7. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8. Create Aggregated Data Tables

The migration should create:
- `api_dailyvoterstats`
- `api_dailyinteractionstats`
- `api_dailysentimentstats`
- `api_weeklycampaignstats`
- `api_reporttemplate`
- `api_generatedreport`
- `api_exportjob`

### 9. Start Django Server

```bash
cd backend
python manage.py runserver
```

### 10. Start Celery Worker (New Terminal)

```bash
cd /Users/murali/Downloads/pulseofpeople/backend
source venv/bin/activate  # Activate virtual environment

celery -A config worker -l info
```

Expected output:
```
 -------------- celery@hostname v5.4.0
---- **** -----
--- * ***  * -- Darwin-24.2.0-arm64-arm-64bit
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         pulseofpeople:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ----
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . api.tasks.generate_daily_report
  . api.tasks.generate_weekly_report
  ...
```

### 11. Start Celery Beat Scheduler (New Terminal)

```bash
cd /Users/murali/Downloads/pulseofpeople/backend
source venv/bin/activate

celery -A config beat -l info
```

Expected output:
```
celery beat v5.4.0 is starting.
__    -    ... ready.
LocalTime -> 2025-11-09 ...
Configuration ->
    . broker -> redis://localhost:6379/0
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> celery.beat.PersistentScheduler
```

### 12. Aggregate Sample Data

```bash
python manage.py aggregate_analytics --backfill 7
```

This will create aggregated data for the last 7 days.

### 13. Test Analytics Endpoints

**Test Voter Analytics:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/analytics/voters/
```

**Test Campaign Analytics:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/analytics/campaigns/
```

**Test Report Generation:**
```bash
curl -X POST http://localhost:8000/api/reports/executive-summary/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "date_from": "2025-11-01",
       "date_to": "2025-11-09",
       "format": "pdf"
     }'
```

Response:
```json
{
  "report_id": "uuid-here",
  "status": "pending",
  "message": "Report generation started."
}
```

### 14. Frontend Setup

```bash
cd /Users/murali/Downloads/pulseofpeople/frontend

# Install chart library
npm install recharts

# Install date utilities
npm install date-fns
```

### 15. Add Routes to Frontend

Update `frontend/src/App.tsx`:

```tsx
import AnalyticsDashboard from './pages/Analytics/AnalyticsDashboard';
import ReportBuilder from './pages/Reports/ReportBuilder';

// Add routes
<Route path="/analytics" element={<AnalyticsDashboard />} />
<Route path="/reports/builder" element={<ReportBuilder />} />
```

### 16. Start Frontend

```bash
cd /Users/murali/Downloads/pulseofpeople/frontend
npm run dev
```

Access at: `http://localhost:5173/analytics`

---

## Monitoring & Debugging

### 1. Install Flower (Celery Monitoring)

```bash
pip install flower
```

### 2. Start Flower

```bash
celery -A config flower
```

Access at: `http://localhost:5555`

### 3. Check Celery Tasks

**List registered tasks:**
```bash
celery -A config inspect registered
```

**Check active tasks:**
```bash
celery -A config inspect active
```

**Check scheduled tasks:**
```bash
celery -A config inspect scheduled
```

### 4. Django Admin

Access aggregated data at:
- http://localhost:8000/admin/api/dailyvoterstats/
- http://localhost:8000/admin/api/generatedreport/
- http://localhost:8000/admin/api/exportjob/

---

## Testing the System

### 1. Test Analytics Endpoints

Create a test script `test_analytics.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Test voter analytics
response = requests.get(f"{BASE_URL}/analytics/voters/", headers=headers)
print("Voter Analytics:", response.json())

# Test campaign analytics
response = requests.get(f"{BASE_URL}/analytics/campaigns/", headers=headers)
print("Campaign Analytics:", response.json())

# Test sentiment analytics
response = requests.get(f"{BASE_URL}/analytics/sentiment/", headers=headers)
print("Sentiment Analytics:", response.json())
```

### 2. Test Report Generation

```python
# Generate executive summary
data = {
    "date_from": "2025-11-01",
    "date_to": "2025-11-09",
    "format": "pdf"
}

response = requests.post(
    f"{BASE_URL}/reports/executive-summary/",
    headers=headers,
    json=data
)
print("Report:", response.json())
```

### 3. Test Export

```python
# Create export job
export_data = {
    "resource": "feedback",
    "format": "csv",
    "filters": {
        "date_from": "2025-11-01",
        "date_to": "2025-11-09"
    }
}

response = requests.post(
    f"{BASE_URL}/export/",
    headers=headers,
    json=export_data
)
print("Export Job:", response.json())
```

---

## Common Issues & Solutions

### Issue 1: Celery worker not starting
**Solution:**
- Check Redis is running: `redis-cli ping`
- Check virtual environment is activated
- Verify CELERY_BROKER_URL in settings

### Issue 2: Tasks not executing
**Solution:**
- Check Celery worker logs
- Verify Celery beat is running
- Check task is registered: `celery -A config inspect registered`

### Issue 3: Import errors
**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements_analytics.txt

# Clear Python cache
find . -type d -name __pycache__ -exec rm -r {} +
```

### Issue 4: Charts not rendering in PDF
**Solution:**
- Install matplotlib dependencies:
  ```bash
  pip install matplotlib seaborn pillow
  ```

### Issue 5: Frontend charts not showing
**Solution:**
- Verify recharts is installed: `npm list recharts`
- Check browser console for errors
- Verify API is returning data

---

## Production Checklist

- [ ] Redis configured with persistence
- [ ] Celery running with supervisor/systemd
- [ ] Email backend configured (SMTP)
- [ ] File storage configured (Supabase/S3)
- [ ] Rate limiting enabled
- [ ] SSL/HTTPS enabled
- [ ] Monitoring tools installed (Flower, Sentry)
- [ ] Backup strategy for aggregated data
- [ ] Log rotation configured
- [ ] Performance testing completed

---

## Next Steps

1. **Populate Data**: Add sample voters, feedback, and field reports
2. **Run Aggregation**: `python manage.py aggregate_analytics --backfill 30`
3. **Test Reports**: Generate reports through the UI
4. **Schedule Reports**: Create report templates with schedules
5. **Monitor**: Use Flower to monitor Celery tasks

---

## Support

For issues or questions:
1. Check logs: `tail -f celery.log`
2. Check Django admin: http://localhost:8000/admin/
3. Check Flower: http://localhost:5555/
4. Review documentation: `ANALYTICS_SYSTEM.md`
