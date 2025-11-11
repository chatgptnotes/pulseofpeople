# Monitoring & Analytics Setup Guide

## Overview

This guide covers the complete monitoring and analytics setup for the Pulse of People platform in production.

---

## 1. Vercel Analytics Setup

### Enable Vercel Analytics

**Step 1: Install Package**
```bash
cd frontend
npm install @vercel/analytics @vercel/speed-insights
```

**Step 2: Add to Application**

Update `frontend/src/main.tsx`:
```typescript
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/react';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
    <Analytics />
    <SpeedInsights />
  </React.StrictMode>,
);
```

**Step 3: Deploy**
```bash
npm run build
vercel --prod
```

### Access Analytics Dashboard

1. Go to https://vercel.com/dashboard
2. Select project: `frontend`
3. Navigate to "Analytics" tab

**Metrics Available:**
- Real-time visitors
- Page views
- Top pages
- Geographic distribution
- Device breakdown
- Referrer sources

---

## 2. Error Tracking with Sentry (Recommended)

### Setup Sentry

**Step 1: Create Sentry Account**
- Go to https://sentry.io
- Create free account
- Create new project (React)

**Step 2: Install Sentry SDK**
```bash
cd frontend
npm install @sentry/react @sentry/tracing
```

**Step 3: Initialize Sentry**

Update `frontend/src/main.tsx`:
```typescript
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

if (import.meta.env.VITE_ENVIRONMENT === 'production') {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [new BrowserTracing()],
    environment: import.meta.env.VITE_ENVIRONMENT,
    tracesSampleRate: 1.0,
    beforeSend(event, hint) {
      // Filter out errors from browser extensions
      if (event.exception) {
        const error = hint.originalException;
        if (error && error.message && error.message.match(/chrome-extension/i)) {
          return null;
        }
      }
      return event;
    },
  });
}
```

**Step 4: Add Environment Variable**
```bash
# Add to Vercel environment variables
VITE_SENTRY_DSN=your-sentry-dsn-here
```

**Step 5: Redeploy**
```bash
vercel --prod
```

### Sentry Dashboard Features

- Real-time error tracking
- Stack traces and breadcrumbs
- User context and session replays
- Performance monitoring
- Release tracking
- Email/Slack alerts

---

## 3. Uptime Monitoring

### UptimeRobot Setup (Free)

**Step 1: Create Account**
- Go to https://uptimerobot.com
- Sign up for free account (50 monitors included)

**Step 2: Add Monitor**
1. Click "Add New Monitor"
2. Monitor Type: HTTP(s)
3. Friendly Name: "Pulse of People - Frontend"
4. URL: `https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app`
5. Monitoring Interval: 5 minutes
6. Click "Create Monitor"

**Step 3: Add API Monitor**
1. Add another monitor
2. Friendly Name: "Pulse of People - Backend API"
3. URL: `https://pulseofpeople-backend.railway.app/api/health`
4. Monitoring Interval: 5 minutes

**Step 4: Setup Alerts**
1. Go to Settings → Alert Contacts
2. Add email address
3. Add phone number for SMS (optional)
4. Configure Slack/Discord webhook (optional)

### Better Stack (Formerly Better Uptime) - Alternative

**Features:**
- Status pages
- Incident management
- On-call scheduling
- Advanced alerting

**Setup:**
```bash
# Add monitoring endpoint to frontend
# Create /api/health endpoint
```

---

## 4. Performance Monitoring

### Vercel Speed Insights

**Enable in Dashboard:**
1. Go to Project Settings
2. Navigate to "Speed Insights"
3. Click "Enable"

**Metrics Tracked:**
- Time to First Byte (TTFB)
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
- First Input Delay (FID)

### Web Vitals Reporting

Add custom web vitals reporting:

```typescript
// frontend/src/utils/reportWebVitals.ts
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric: any) {
  // Send to your analytics endpoint
  const body = JSON.stringify(metric);
  const url = `${import.meta.env.VITE_API_URL}/analytics/webvitals`;

  if (navigator.sendBeacon) {
    navigator.sendBeacon(url, body);
  } else {
    fetch(url, { body, method: 'POST', keepalive: true });
  }
}

export function reportWebVitals() {
  getCLS(sendToAnalytics);
  getFID(sendToAnalytics);
  getFCP(sendToAnalytics);
  getLCP(sendToAnalytics);
  getTTFB(sendToAnalytics);
}
```

---

## 5. Database Monitoring

### Supabase Dashboard

**Access Monitoring:**
1. Go to https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
2. Navigate to "Database" → "Query Performance"

**Key Metrics:**
- Active connections
- Query execution time
- Slow query log
- Database size
- Cache hit ratio

**Setup Alerts:**
1. Go to Project Settings
2. Navigate to "Integrations"
3. Add webhook for Slack/Discord
4. Configure alert thresholds:
   - Database size > 80%
   - Connection pool > 80%
   - Slow queries > 1 second

### Query Performance Monitoring

Create monitoring queries:

```sql
-- Check active connections
SELECT count(*) FROM pg_stat_activity;

-- Find slow queries
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check database size
SELECT pg_size_pretty(pg_database_size(current_database()));

-- Monitor table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
```

---

## 6. API Monitoring

### Backend Health Checks

Create health check endpoints in Django:

```python
# backend/api/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=503)
```

### Monitor API Response Times

Use Pingdom or similar:
1. Create account at https://www.pingdom.com
2. Add transaction check for API endpoints
3. Set up alerts for slow responses (> 2 seconds)

---

## 7. Log Aggregation

### Vercel Logs

**View Deployment Logs:**
```bash
# Recent logs
vercel logs

# Specific deployment
vercel logs [deployment-url]

# Follow logs in real-time
vercel logs --follow

# Filter by type
vercel logs --type=error
```

**Log Retention:**
- Free tier: 1 day
- Pro tier: 30 days
- Enterprise: Custom

### Railway Logs

**Access Logs:**
1. Go to Railway Dashboard
2. Select "pulseofpeople-backend" project
3. View logs in real-time
4. Filter by severity (info, warning, error)

**Export Logs:**
```bash
# Using Railway CLI
railway logs --tail 1000 > backend-logs.txt
```

### Centralized Logging (Optional)

**Using Logflare:**
```bash
npm install logflare

# Configure in src/main.tsx
import { Logflare } from 'logflare';

const logger = new Logflare({
  sourceToken: import.meta.env.VITE_LOGFLARE_SOURCE,
  apiKey: import.meta.env.VITE_LOGFLARE_KEY,
});

// Use throughout app
logger.info('User logged in', { userId: user.id });
```

---

## 8. Custom Monitoring Dashboard

### Create Monitoring Dashboard

```typescript
// frontend/src/pages/MonitoringDashboard.tsx
import React, { useEffect, useState } from 'react';

interface SystemStatus {
  frontend: 'healthy' | 'degraded' | 'down';
  backend: 'healthy' | 'degraded' | 'down';
  database: 'healthy' | 'degraded' | 'down';
  lastCheck: string;
}

export default function MonitoringDashboard() {
  const [status, setStatus] = useState<SystemStatus | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/health`
        );
        const data = await response.json();
        setStatus(data);
      } catch (error) {
        console.error('Health check failed:', error);
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">System Status</h1>
      {/* Render status indicators */}
    </div>
  );
}
```

---

## 9. Alerting Configuration

### Critical Alerts

Set up alerts for:

**1. Downtime Alerts**
- Frontend unavailable
- Backend API errors
- Database connection failures

**2. Performance Alerts**
- Response time > 3 seconds
- Error rate > 5%
- CPU usage > 80%
- Memory usage > 80%

**3. Security Alerts**
- Failed login attempts > 10/minute
- Suspicious API requests
- SSL certificate expiration (< 30 days)

### Alert Channels

Configure multiple channels:
- **Email**: Primary alerts
- **SMS**: Critical alerts only
- **Slack**: Team notifications
- **Discord**: Development team
- **PagerDuty**: On-call escalation

### Example Alert Configuration

```yaml
# Example alerting rules
alerts:
  - name: Frontend Down
    condition: uptime < 99%
    severity: critical
    channels: [email, sms, slack]

  - name: High Error Rate
    condition: error_rate > 5%
    severity: warning
    channels: [email, slack]

  - name: Slow Response
    condition: response_time > 3000ms
    severity: warning
    channels: [slack]

  - name: Database Connection Pool
    condition: connections > 80%
    severity: warning
    channels: [email, slack]
```

---

## 10. Monitoring Checklist

### Daily Checks
- [ ] Check Vercel deployment status
- [ ] Review error logs in Sentry
- [ ] Verify uptime monitors are green
- [ ] Check database connection pool

### Weekly Checks
- [ ] Review analytics trends
- [ ] Check performance metrics
- [ ] Review slow query logs
- [ ] Check disk space usage
- [ ] Review security alerts

### Monthly Checks
- [ ] Review and optimize bundle size
- [ ] Check for dependency updates
- [ ] Review and archive old logs
- [ ] Test backup restoration
- [ ] Review and update alert thresholds
- [ ] Check SSL certificate expiration

---

## 11. Monitoring Commands

### Quick Monitoring Commands

```bash
# Check deployment status
vercel ls

# View recent logs
vercel logs --tail 100

# Check build status
vercel inspect [deployment-url]

# Monitor database
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity;"

# Check API health
curl https://pulseofpeople-backend.railway.app/api/health

# Test frontend
curl -I https://frontend-avfwstn4w-chatgptnotes-6366s-projects.vercel.app
```

---

## 12. Incident Response

### When Downtime Occurs

**1. Immediate Actions:**
```bash
# Check deployment status
vercel ls

# Check logs for errors
vercel logs --type=error

# Check backend health
curl https://pulseofpeople-backend.railway.app/api/health

# Check database
# Login to Supabase dashboard
```

**2. Rollback if Needed:**
```bash
# List recent deployments
vercel ls

# Promote previous working deployment
vercel promote [previous-deployment-url]
```

**3. Communicate:**
- Update status page
- Notify users via email/announcement
- Post incident update to team channel

**4. Post-Mortem:**
- Document what happened
- Identify root cause
- Implement preventive measures
- Update runbooks

---

## Summary

### Monitoring Stack

| Component | Tool | Status | Dashboard |
|-----------|------|--------|-----------|
| Analytics | Vercel Analytics | ✅ Active | https://vercel.com/dashboard |
| Error Tracking | Sentry | ⏳ Pending Setup | https://sentry.io |
| Uptime | UptimeRobot | ⏳ Pending Setup | https://uptimerobot.com |
| Performance | Vercel Speed Insights | ✅ Active | https://vercel.com/dashboard |
| Database | Supabase Dashboard | ✅ Active | https://supabase.com/dashboard |
| Logs | Vercel + Railway | ✅ Active | Multiple |

### Next Steps

1. **Install Vercel Analytics** (5 minutes)
   ```bash
   npm install @vercel/analytics @vercel/speed-insights
   ```

2. **Setup Sentry** (15 minutes)
   - Create account
   - Install SDK
   - Configure DSN

3. **Configure UptimeRobot** (10 minutes)
   - Add frontend monitor
   - Add backend monitor
   - Setup alerts

4. **Enable Speed Insights** (2 minutes)
   - Enable in Vercel dashboard

5. **Create Status Dashboard** (30 minutes)
   - Build internal monitoring page
   - Add system health checks

**Total Setup Time**: ~1 hour

---

**Last Updated**: November 9, 2025
**Status**: Monitoring infrastructure ready for implementation
