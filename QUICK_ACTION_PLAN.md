# Pulse of People - Quick Action Plan

**Generated:** November 9, 2025

---

## IMMEDIATE ACTIONS (This Week)

### Day 1-2: Database Foundation

```bash
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople
```

**Create these 5 critical tables first:**

1. **sentiment_data** - Core analytics table
2. **social_posts** - Social media monitoring
3. **alerts** - Real-time alerting
4. **field_reports** - Ground intelligence
5. **notifications** - User notifications

**SQL Migration File:** Create `/supabase/migrations/20251109_phase3_critical_tables.sql`

### Day 3-4: Fix Top 10 Mock Data Files

**Priority Files to Fix:**

1. `/frontend/src/pages/Dashboard.tsx` - Main dashboard
2. `/frontend/src/pages/AnalyticsDashboard.tsx` - Analytics
3. `/frontend/src/pages/BoothsList.tsx` - Booths list
4. `/frontend/src/pages/WardsList.tsx` - Wards list
5. `/frontend/src/pages/dashboards/SuperAdminDashboard.tsx` - Super admin
6. `/frontend/src/services/realTimeService.ts` - Real-time service
7. `/frontend/src/components/AlertsPanel.tsx` - Alerts
8. `/frontend/src/components/SentimentTrends.tsx` - Sentiment trends
9. `/frontend/src/components/NotificationCenter.tsx` - Notifications
10. `/frontend/src/pages/InfluencerTracking.tsx` - Influencers

**Pattern to Follow:**

```typescript
// BEFORE (Mock Data)
const [data, setData] = useState(mockData);

// AFTER (Real Supabase)
const [data, setData] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);

useEffect(() => {
  async function fetchData() {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from('table_name')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      setData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }
  fetchData();
}, []);
```

### Day 5: Add Error Handling & Loading States

**Add to all components:**

```typescript
if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage error={error} />;
if (!data) return <EmptyState />;
```

---

## WEEK 2: Core Features

### Database Completion

Create remaining tables:
- [ ] influencers
- [ ] trending_topics
- [ ] media_coverage
- [ ] competitor_activity
- [ ] surveys, survey_questions, survey_responses
- [ ] campaign_events
- [ ] conversations

### Analytics Implementation

Create PostgreSQL functions:
- [ ] `calculate_overall_sentiment(start, end, ward)`
- [ ] `get_trending_issues(period, limit)`
- [ ] `detect_sentiment_anomalies()`

### RLS Policies

Add RLS to all new tables:

```sql
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org data"
    ON table_name FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));
```

---

## WEEK 3-4: Replace All Mock Data

### Service Layer Approach

Create centralized services:

**File:** `/frontend/src/services/supabase/sentiment.service.ts`

```typescript
import { supabase } from './index';

export const sentimentService = {
  async getOverallSentiment(startDate, endDate, ward) {
    const { data, error } = await supabase
      .rpc('calculate_overall_sentiment', {
        start_time: startDate,
        end_time: endDate,
        ward_filter: ward
      });
    if (error) throw error;
    return data;
  },

  async getTrendingIssues(period, limit) {
    const { data, error } = await supabase
      .rpc('get_trending_issues', {
        time_period: period,
        limit_count: limit
      });
    if (error) throw error;
    return data;
  }
};
```

**File:** `/frontend/src/services/supabase/alerts.service.ts`

```typescript
export const alertsService = {
  async getActiveAlerts() {
    const { data, error } = await supabase
      .from('alerts')
      .select('*')
      .eq('status', 'active')
      .order('severity', { ascending: false })
      .order('created_at', { ascending: false });
    if (error) throw error;
    return data;
  }
};
```

### Use React Query for Caching

```bash
npm install @tanstack/react-query
```

```typescript
import { useQuery } from '@tanstack/react-query';

function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['sentiment', 'overall'],
    queryFn: () => sentimentService.getOverallSentiment(
      new Date(Date.now() - 24 * 60 * 60 * 1000),
      new Date(),
      null
    ),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;

  return <div>Sentiment: {data}</div>;
}
```

---

## WEEK 5-6: Testing & Quality

### Install Testing Dependencies

```bash
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom
```

### Write Tests

**Unit Test Example:**

```typescript
// hasPermission.test.ts
import { describe, it, expect } from 'vitest';
import { hasPermission } from './rbac';

describe('hasPermission', () => {
  it('should return true for superadmin', () => {
    const user = { role: 'superadmin', permissions: [] };
    expect(hasPermission(user, 'any.permission')).toBe(true);
  });

  it('should check permissions array for other roles', () => {
    const user = { role: 'admin', permissions: ['users.create'] };
    expect(hasPermission(user, 'users.create')).toBe(true);
    expect(hasPermission(user, 'users.delete')).toBe(false);
  });
});
```

---

## PRODUCTION DEPLOYMENT CHECKLIST

### Pre-Deployment

- [ ] Run all migrations on production Supabase
- [ ] Verify RLS policies in production
- [ ] Set up environment variables in Vercel
- [ ] Configure custom domain
- [ ] Set up automated backups

### Environment Variables

```bash
# .env.production
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_APP_URL=https://pulseofpeople.com
VITE_MULTI_TENANT=false
```

### Vercel Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel --prod
```

### Post-Deployment

- [ ] Test all authentication flows
- [ ] Test all role-based access
- [ ] Verify data upload works
- [ ] Check analytics dashboards
- [ ] Monitor error logs

---

## PERFORMANCE OPTIMIZATION

### Critical Optimizations

1. **Add Indexes:**

```sql
-- Add composite index for common query
CREATE INDEX idx_sentiment_data_org_timestamp
ON sentiment_data(organization_id, timestamp DESC);

-- Add partial index for active records
CREATE INDEX idx_booths_active
ON polling_booths(organization_id)
WHERE is_active = true;
```

2. **Create Materialized View:**

```sql
CREATE MATERIALIZED VIEW dashboard_metrics AS
SELECT
  organization_id,
  COUNT(*) as total_booths,
  SUM(total_voters) as total_voters,
  AVG(sentiment_score) as avg_sentiment
FROM polling_booths
GROUP BY organization_id;

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_metrics;
```

3. **Implement Caching:**

```typescript
// Use React Query with aggressive caching
const { data } = useQuery({
  queryKey: ['dashboard-metrics'],
  queryFn: getDashboardMetrics,
  staleTime: 10 * 60 * 1000, // 10 minutes
  cacheTime: 30 * 60 * 1000, // 30 minutes
});
```

---

## CRITICAL FILES TO REVIEW

### High Priority

1. `/frontend/src/pages/Dashboard.tsx` - 100 lines of mock data
2. `/frontend/src/pages/AnalyticsDashboard.tsx` - 150 lines of mock functions
3. `/frontend/src/services/realTimeService.ts` - Entire mock service
4. `/frontend/src/services/crisisDetection.ts` - Mock crisis events
5. `/frontend/src/services/recommendationsEngine.ts` - Mock AI recommendations

### Database Migrations

1. `/supabase/migrations/20251109_phase1_core_entities.sql` - ✅ Done
2. `/supabase/migrations/20251109_phase2_geography_territory.sql` - ✅ Done
3. `/supabase/migrations/20251109_phase3_critical_tables.sql` - ❌ Need to create
4. `/supabase/migrations/20251109_phase4_analytics_tables.sql` - ❌ Need to create
5. `/supabase/migrations/20251109_phase5_rls_completion.sql` - ❌ Need to create

---

## CODE QUALITY CHECKS

### Before Committing

```bash
# Lint
npm run lint

# Type check
npm run type-check

# Build test
npm run build

# Run tests
npm run test
```

### Pre-Production Checklist

- [ ] No console.log statements
- [ ] No commented code
- [ ] All TODOs resolved
- [ ] TypeScript strict mode passes
- [ ] ESLint zero errors
- [ ] All tests passing
- [ ] Bundle size < 500KB

---

## MONITORING SETUP

### Error Tracking

```bash
npm install @sentry/react @sentry/tracing
```

```typescript
// main.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

### Analytics

```typescript
// Track page views
useEffect(() => {
  gtag('event', 'page_view', {
    page_path: location.pathname,
  });
}, [location]);

// Track user actions
const handleClick = () => {
  gtag('event', 'button_click', {
    event_category: 'engagement',
    event_label: 'dashboard_export',
  });
};
```

---

## SUPPORT & RESOURCES

### Documentation Links

- Supabase Docs: https://supabase.com/docs
- React Query: https://tanstack.com/query/latest
- Vercel Deployment: https://vercel.com/docs

### Key Commands

```bash
# Development
npm run dev

# Database
psql $DATABASE_URL -f migration.sql

# Deployment
vercel --prod

# Logs
vercel logs
```

---

## SUCCESS CRITERIA

### Week 1 ✅
- 5 critical tables created
- 10 top files migrated from mock to real data
- Basic error handling added

### Week 2 ✅
- All database tables created
- RLS policies implemented
- Analytics functions created

### Week 3-4 ✅
- All mock data replaced
- React Query implemented
- Performance optimized

### Week 5-6 ✅
- 80% test coverage
- Production deployed
- Monitoring set up

---

**Next Steps:** Start with Day 1-2 database foundation tasks immediately.
