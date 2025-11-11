# Pulse of People - Analytics & Reporting System

## Complete Analytics and Reporting System Implementation

### Overview
This document provides a comprehensive guide to the production-ready analytics and reporting system built for the Pulse of People platform. The system includes 10 analytics endpoints, automated report generation, PDF/Excel exports, scheduled reports, and interactive dashboards.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Analytics Endpoints](#analytics-endpoints)
3. [Report Generation](#report-generation)
4. [Export Functionality](#export-functionality)
5. [Automated Reports](#automated-reports)
6. [Data Aggregation](#data-aggregation)
7. [Frontend Components](#frontend-components)
8. [Installation & Setup](#installation--setup)
9. [API Reference](#api-reference)
10. [Best Practices](#best-practices)

---

## System Architecture

### Backend Components
```
backend/
├── api/
│   ├── models_analytics.py          # Analytics aggregation models
│   ├── views/
│   │   ├── analytics.py             # 10 analytics endpoints
│   │   ├── reports.py               # Report generation endpoints
│   │   └── export.py                # Export API
│   ├── utils/
│   │   ├── pdf_generator.py         # PDF report generation
│   │   └── excel_exporter.py        # Excel export utilities
│   ├── tasks.py                     # Celery background tasks
│   ├── management/commands/
│   │   └── aggregate_analytics.py   # Data aggregation command
│   └── urls/
│       └── analytics_urls.py        # URL routing
└── config/
    └── celery.py                    # Celery configuration
```

### Frontend Components
```
frontend/src/pages/
├── Analytics/
│   └── AnalyticsDashboard.tsx       # Main analytics dashboard
└── Reports/
    └── ReportBuilder.tsx            # Custom report builder UI
```

---

## Analytics Endpoints

### 1. Voter Analytics
**Endpoint:** `GET /api/analytics/voters/`

**Query Parameters:**
- `date_from`, `date_to` - Date range filter
- `state`, `district`, `constituency` - Geographic filters
- `aggregation` - Aggregation level (daily, weekly, monthly)

**Response:**
```json
{
  "total_voters": 45234,
  "by_sentiment": {
    "strong_supporter": 15000,
    "supporter": 12000,
    "neutral": 10000,
    "opposition": 5234,
    "strong_opposition": 3000
  },
  "by_gender": {
    "male": 23000,
    "female": 22000,
    "other": 234
  },
  "by_age_group": {
    "18-25": 8000,
    "26-35": 12000,
    "36-45": 10000,
    "46-60": 9000,
    "60+": 6234
  },
  "growth_trend": [
    {"date": "2025-11-01", "count": 44000, "new": 50},
    {"date": "2025-11-02", "count": 44050, "new": 55}
  ],
  "by_constituency": [...]
}
```

### 2. Campaign Analytics
**Endpoint:** `GET /api/analytics/campaigns/`

**Response:**
```json
{
  "total_campaigns": 25,
  "active_campaigns": 8,
  "completed_campaigns": 17,
  "total_reach": 150000,
  "total_budget": 500000.00,
  "total_spent": 450000.00,
  "avg_roi": 2.5,
  "total_interactions": 25000,
  "total_conversions": 5000,
  "conversion_rate": 20.0,
  "weekly_trend": [...]
}
```

### 3. Interaction Analytics
**Endpoint:** `GET /api/analytics/interactions/`

**Response:**
```json
{
  "total_interactions": 35000,
  "by_type": {
    "phone_calls": 15000,
    "door_to_door": 10000,
    "events": 8000,
    "social_media": 2000
  },
  "total_conversions": 7000,
  "conversion_rate": 20.0,
  "avg_response_rate": 65.5,
  "active_volunteers": 250,
  "daily_trend": [...]
}
```

### 4. Geographic Analytics
**Endpoint:** `GET /api/analytics/geographic/`

**Response:**
```json
{
  "state_breakdown": [
    {"state": "Tamil Nadu", "total_voters": 45234, "supporters": 30000}
  ],
  "district_breakdown": [...],
  "constituency_breakdown": [...],
  "heatmap_data": [
    {"lat": 13.0827, "lng": 80.2707, "value": 5000, "name": "Booth 1"}
  ],
  "coverage_summary": {
    "total_states": 1,
    "total_districts": 38,
    "total_constituencies": 234,
    "mapped_booths": 500
  }
}
```

### 5. Sentiment Analytics
**Endpoint:** `GET /api/analytics/sentiment/`

**Response:**
```json
{
  "overall_sentiment_score": 45.5,
  "sentiment_distribution": {
    "positive": 15000,
    "negative": 5000,
    "neutral": 8000
  },
  "sentiment_velocity": 2.5,
  "sentiment_trend": [...],
  "by_issue": [
    {"issue": "Employment", "score": 0.65, "mentions": 5000}
  ],
  "by_location": [...]
}
```

### 6. Social Media Analytics
**Endpoint:** `GET /api/analytics/social-media/`

**Response:**
```json
{
  "platforms": {
    "facebook": {
      "followers": 150000,
      "reach": 450000,
      "engagement_rate": 4.5,
      "post_count": 125
    }
  },
  "top_posts": [...],
  "best_posting_times": ["09:00", "13:00", "19:00"],
  "trending_hashtags": ["#TVK", "#PeopleFirst"],
  "follower_growth": [...]
}
```

### 7. Field Report Analytics
**Endpoint:** `GET /api/analytics/field-reports/`

**Response:**
```json
{
  "total_reports": 1250,
  "by_type": {
    "daily_summary": 500,
    "event_feedback": 300,
    "issue_report": 250
  },
  "by_status": {
    "pending": 100,
    "verified": 1000,
    "disputed": 150
  },
  "top_volunteers": [...],
  "geographic_distribution": [...],
  "avg_response_time": "4.5 hours"
}
```

### 8. Polling Booth Analytics
**Endpoint:** `GET /api/analytics/polling-booths/`

**Response:**
```json
{
  "total_booths": 15000,
  "total_voters": 5000000,
  "avg_voters_per_booth": 333,
  "mapped_booths": 12000,
  "unmapped_booths": 3000,
  "coverage_percentage": 80.0,
  "accessible_booths": 13500,
  "by_constituency": [...]
}
```

### 9. Comparative Analytics
**Endpoint:** `GET /api/analytics/compare/`

**Query Parameters:**
- `type` - constituencies, districts, time_periods
- `item1`, `item2` - IDs to compare

**Response:**
```json
{
  "comparison_type": "constituencies",
  "item1": {
    "name": "Constituency A",
    "total_voters": 50000,
    "supporters": 30000
  },
  "item2": {
    "name": "Constituency B",
    "total_voters": 45000,
    "supporters": 25000
  }
}
```

### 10. Predictive Analytics
**Endpoint:** `GET /api/analytics/predictions/`

**Response:**
```json
{
  "voter_turnout_prediction": {
    "estimated_turnout": 68.5,
    "confidence": 0.82,
    "factors": ["Historical data", "Current sentiment"]
  },
  "sentiment_forecast": {...},
  "risk_areas": [...],
  "opportunities": [...]
}
```

---

## Report Generation

### Available Report Types

#### 1. Executive Summary Report
**Endpoint:** `POST /api/reports/executive-summary/`

**Request:**
```json
{
  "date_from": "2025-11-01",
  "date_to": "2025-11-08",
  "format": "pdf"
}
```

**Features:**
- Key metrics dashboard
- Top 5 insights
- Risks and opportunities
- Recommendations
- Professional PDF with charts

#### 2. Campaign Performance Report
**Endpoint:** `POST /api/reports/campaign-performance/`

**Includes:**
- Campaign overview
- Reach and engagement metrics
- Budget utilization
- Team performance
- ROI analysis

#### 3. Constituency Report
**Endpoint:** `POST /api/reports/constituency/`

**Includes:**
- Voter demographics
- Sentiment analysis
- Key issues
- Booth coverage
- Volunteer activity

#### 4. Daily Activity Report
**Endpoint:** `POST /api/reports/daily-activity/`

**Auto-generated daily at 6 PM**
- Interactions logged today
- Field reports submitted
- New voters added
- Tasks completed

#### 5. Weekly Summary Report
**Endpoint:** `POST /api/reports/weekly-summary/`

**Auto-generated every Monday**
- Week's key metrics
- Week-over-week changes
- Top performers
- Issues requiring attention

#### 6. Volunteer Performance Report
**Endpoint:** `POST /api/reports/volunteer-performance/`

**Includes:**
- Individual volunteer metrics
- Leaderboard
- Areas covered
- Quality scores

#### 7. Custom Report Builder
**Endpoint:** `POST /api/reports/custom/`

**Request:**
```json
{
  "metrics": ["total_voters", "sentiment_score"],
  "filters": {
    "date_from": "2025-11-01",
    "date_to": "2025-11-08",
    "state": "1"
  },
  "visualizations": [
    {
      "type": "bar",
      "metric": "total_voters",
      "title": "Voter Count by Constituency"
    }
  ],
  "format": "pdf",
  "save_as_template": true,
  "template_name": "My Custom Report"
}
```

---

## Export Functionality

### Export API
**Endpoint:** `POST /api/export/`

**Request:**
```json
{
  "resource": "voters",
  "format": "csv",
  "filters": {
    "date_from": "2025-11-01",
    "date_to": "2025-11-08"
  },
  "fields": ["name", "phone", "sentiment"]
}
```

**Supported Resources:**
- voters
- interactions
- feedback
- field_reports
- polling_booths
- sentiment_data
- campaigns

**Supported Formats:**
- CSV
- Excel
- JSON
- PDF

### Quick Export (Synchronous)
**Endpoint:** `GET /api/export/quick/csv/{resource}/`

Maximum 1000 rows, immediate download.

### Export Status
**Endpoint:** `GET /api/export/{job_id}/status/`

Check progress of large export jobs.

### Export Download
**Endpoint:** `GET /api/export/{job_id}/download/`

Download completed export file (expires in 24 hours).

---

## Automated Reports

### Celery Tasks

#### Daily Report
**Schedule:** Every day at 6 PM
**Task:** `api.tasks.generate_daily_report`

```python
@shared_task
def generate_daily_report():
    # Collects today's data
    # Generates PDF report
    # Emails to admins
```

#### Weekly Report
**Schedule:** Every Monday at 9 AM
**Task:** `api.tasks.generate_weekly_report`

#### Monthly Report
**Schedule:** 1st of every month at 10 AM
**Task:** `api.tasks.generate_monthly_report`

#### Scheduled Custom Reports
**Task:** `api.tasks.generate_scheduled_report(template_id)`

Users can create custom report templates and schedule them to run:
- Daily
- Weekly
- Monthly

### Email Delivery
Reports are automatically emailed to specified recipients with download links.

---

## Data Aggregation

### Management Command
**Usage:**
```bash
# Aggregate yesterday's data
python manage.py aggregate_analytics

# Aggregate specific date
python manage.py aggregate_analytics --date 2025-11-09

# Backfill last 30 days
python manage.py aggregate_analytics --backfill 30

# Force re-aggregation
python manage.py aggregate_analytics --force
```

### Automated Aggregation
**Schedule:** Runs hourly via Celery Beat

Aggregates:
- Daily voter statistics
- Daily interaction statistics
- Daily sentiment statistics
- Weekly campaign statistics

### Aggregation Models
1. **DailyVoterStats** - Daily voter metrics by location
2. **DailyInteractionStats** - Daily interaction metrics
3. **DailySentimentStats** - Daily sentiment metrics
4. **WeeklyCampaignStats** - Weekly campaign performance

---

## Frontend Components

### Analytics Dashboard
**Location:** `/frontend/src/pages/Analytics/AnalyticsDashboard.tsx`

**Features:**
- 4 tabs: Voters, Campaigns, Interactions, Sentiment
- Interactive charts (Line, Bar, Pie)
- Date range filters
- Geographic filters
- Export to PDF/Excel
- Real-time data refresh

**Usage:**
```tsx
import AnalyticsDashboard from './pages/Analytics/AnalyticsDashboard';

<Route path="/analytics" element={<AnalyticsDashboard />} />
```

### Report Builder
**Location:** `/frontend/src/pages/Reports/ReportBuilder.tsx`

**Features:**
- 4-step wizard
- Select metrics
- Configure visualizations (drag-and-drop)
- Set filters and date ranges
- Save as template
- Schedule recurring reports
- Preview before generation

**Wizard Steps:**
1. Select Metrics
2. Configure Visualizations
3. Set Filters
4. Generate Report

---

## Installation & Setup

### 1. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements_analytics.txt
```

**Dependencies:**
- reportlab==4.2.2 (PDF generation)
- openpyxl==3.1.5 (Excel export)
- matplotlib==3.9.4 (Charts)
- celery==5.4.0 (Background tasks)
- redis==5.2.1 (Celery broker)
- pandas==2.2.3 (Data processing)

### 2. Install Redis
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu
sudo apt-get install redis-server
sudo systemctl start redis
```

### 3. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Start Celery Worker
```bash
celery -A config worker -l info
```

### 5. Start Celery Beat (Scheduler)
```bash
celery -A config beat -l info
```

### 6. Update URLs
Add to `config/urls.py`:
```python
from api.urls.analytics_urls import urlpatterns as analytics_urls

urlpatterns = [
    # ... existing urls
    path('api/', include(analytics_urls)),
]
```

### 7. Frontend Dependencies
```bash
cd frontend
npm install recharts date-fns
```

---

## API Reference

### Base URL
```
http://localhost:8000/api/
```

### Authentication
All endpoints require JWT authentication:
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/analytics/voters/
```

### Rate Limiting
- Analytics endpoints: 100 requests/minute
- Report generation: 10 requests/hour
- Exports: 20 requests/hour

### Error Responses
```json
{
  "error": "Error message here",
  "details": "Additional error details"
}
```

**HTTP Status Codes:**
- 200: Success
- 201: Created
- 202: Accepted (async job created)
- 400: Bad Request
- 401: Unauthorized
- 404: Not Found
- 410: Gone (expired)
- 429: Too Many Requests
- 500: Server Error

---

## Best Practices

### Performance Optimization
1. **Use Aggregated Data**: Query `DailyVoterStats` instead of raw voter data
2. **Apply Filters**: Always use date range and geographic filters
3. **Limit Results**: Use pagination for large datasets
4. **Cache Results**: Cache frequently accessed analytics for 5-15 minutes
5. **Background Jobs**: Use Celery for exports > 10K rows

### Report Generation
1. **Schedule Off-Peak**: Run automated reports during low-traffic hours
2. **Email Delivery**: Use Celery tasks for email delivery
3. **File Cleanup**: Expired reports are auto-deleted after 24-72 hours
4. **Template Reuse**: Save frequently used reports as templates

### Data Quality
1. **Aggregate Daily**: Run aggregation hourly to keep data fresh
2. **Validate Input**: Validate date ranges and filters
3. **Monitor Tasks**: Use Flower to monitor Celery tasks
4. **Error Handling**: Log errors and send alerts for failed reports

### Security
1. **Permission Checks**: Verify user has access to requested data
2. **Data Isolation**: Filter by organization in multi-tenant setup
3. **Rate Limiting**: Implement rate limiting on expensive endpoints
4. **Secure Downloads**: Use signed URLs with expiration

---

## Monitoring & Debugging

### Celery Monitoring with Flower
```bash
pip install flower
celery -A config flower
```

Access at: `http://localhost:5555`

### Django Admin
Access aggregated data:
- http://localhost:8000/admin/api/dailyvoterstats/
- http://localhost:8000/admin/api/generatedreport/
- http://localhost:8000/admin/api/exportjob/

### Logs
```bash
# Celery worker logs
tail -f celery.log

# Django logs
tail -f django.log
```

---

## Production Deployment

### Environment Variables
```bash
# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password

# Storage (for report files)
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

### Supervisor Configuration
```ini
[program:celery_worker]
command=/path/to/venv/bin/celery -A config worker -l info
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true

[program:celery_beat]
command=/path/to/venv/bin/celery -A config beat -l info
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
```

---

## Summary

This analytics and reporting system provides:
- **10 Analytics Endpoints** covering all aspects of political campaigning
- **7 Report Types** with PDF and Excel export
- **Automated Scheduling** for daily, weekly, and monthly reports
- **Custom Report Builder** with drag-and-drop visualization configuration
- **Background Processing** using Celery for heavy operations
- **Data Aggregation** for fast query performance
- **Interactive Dashboards** with real-time charts
- **Export API** supporting CSV, Excel, JSON, and PDF

All components are production-ready, well-documented, and scalable.
