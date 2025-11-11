# Supabase Seeds Creation - Summary Report

**Date:** 2024-11-30
**Project:** Pulse of People - Political Sentiment Analysis Platform
**Task:** Generate trending topics and alerts seed data for Supabase

---

## Files Created

### 1. trending_topics_seed.sql
**Location:** `/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/trending_topics_seed.sql`
**Size:** 199 lines
**Records:** 100 trending political topics

**Features:**
- Realistic Tamil Nadu political issues
- Topic categories:
  - Water Crisis: 25% (25 topics)
  - TVK/Political: 30% (30 topics)
  - NEET: 15% (15 topics)
  - Cauvery Dispute: 10% (10 topics)
  - Jobs/Employment: 10% (10 topics)
  - Fishermen Issues: 5% (5 topics)
  - Others: 5% (5 topics)
- Volume: 100-15,000 mentions
- Growth rates: 0.0-1.5 (0-150%)
- Sentiment scores: -1.0 to +1.0
- Platforms: Twitter, Facebook, Instagram, News
- Time distribution: Last 7 days
- UUID-based IDs for Supabase compatibility

**Database Structure:**
```sql
CREATE TABLE trending_topics (
  id UUID PRIMARY KEY,
  keyword TEXT NOT NULL,
  volume INTEGER NOT NULL,
  growth_rate DECIMAL(5,2),
  sentiment_score DECIMAL(3,2),
  platforms TEXT[],
  time_period TEXT,
  timestamp TIMESTAMPTZ,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

**Sample Data:**
- "Vijay TVK" - 15,234 mentions, +122% growth, +0.72 sentiment
- "Chennai Water Crisis" - 8,432 mentions, +65% growth, -0.45 sentiment
- "NEET Opposition TN" - 5,892 mentions, +48% growth, -0.42 sentiment

---

### 2. alerts_seed.sql
**Location:** `/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/alerts_seed.sql`
**Size:** 355 lines
**Records:** 50 political alerts

**Features:**
- Alert type distribution:
  - Sentiment Spike: 40% (20 alerts)
  - Crisis Detection: 30% (15 alerts)
  - Competitor Activity: 15% (7-8 alerts)
  - Viral: 10% (5 alerts)
  - System: 5% (2-3 alerts)
- Severity distribution:
  - Critical: 10% (5 alerts)
  - High: 20% (10 alerts)
  - Medium: 40% (20 alerts)
  - Low: 30% (15 alerts)
- Status distribution:
  - Active: 80% (40 alerts)
  - Acknowledged: 15% (7-8 alerts)
  - Resolved: 5% (2-3 alerts)
- Time distribution: Last 48 hours (critical/high more recent)
- Geographic tagging: Districts (80%), Wards (50%)

**Database Structure:**
```sql
CREATE TABLE alerts (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  severity TEXT CHECK (severity IN ('low','medium','high','critical')),
  type TEXT CHECK (type IN ('sentiment_spike','crisis','competitor_activity','viral','system')),
  status TEXT DEFAULT 'active',
  timestamp TIMESTAMPTZ,
  ward TEXT,
  district TEXT,
  created_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ
);
```

**Sample Critical Alerts:**
1. "CRITICAL: Negative sentiment crash Coimbatore water crisis" - 65% drop in 6 hours
2. "CRITICAL: Viral post NEET student suicide - 15K shares" - 2 hours ago
3. "CRITICAL: Water mafia violence Chennai - media coverage spike"
4. "CRITICAL: TVK rally crowd estimate 50K+ exceeds permit"
5. "CRITICAL: Fishermen arrests by Sri Lanka Navy - 23 boats seized"

---

### 3. SUPABASE_SEEDS_README.md
**Location:** `/Users/murali/Applications/pulseofpeople/backend/SUPABASE_SEEDS_README.md`
**Size:** 806 lines
**Type:** Comprehensive documentation

**Contents:**
1. **Overview** - Seed files summary and data distribution
2. **Prerequisites** - Requirements and environment setup
3. **Installation** - 3 methods (SQL Editor, psql, direct connection)
4. **Running Seeds** - Step-by-step execution guide
5. **Table Structures** - Complete schema definitions with examples
6. **Verification Queries** - 19 queries to validate data:
   - Trending topics: count, top by volume, growth rate, sentiment
   - Alerts: count, by severity, by type, by status, by district
   - Geographic distribution
   - Time-based filtering
7. **Data Refresh Procedures** - Complete refresh, partial updates, archiving
8. **Frontend Integration** - React/TypeScript code examples:
   - Supabase client setup
   - Service functions for trending topics
   - Service functions for alerts
   - React component examples
   - Dashboard integration points
9. **Troubleshooting** - Common issues and solutions:
   - UUID extension errors
   - Permission issues
   - Duplicate key errors
   - Performance optimization
   - Data validation
10. **Maintenance Schedule** - Daily, weekly, monthly tasks

**Key Features:**
- Production-ready SQL with proper error handling
- PostgreSQL-compatible syntax
- Comprehensive indexes for performance
- Row-level security (RLS) compatible
- Real-time subscription ready
- Geographic filtering support

---

### 4. EXECUTE_ALL_SEEDS.sh
**Location:** `/Users/murali/Applications/pulseofpeople/backend/EXECUTE_ALL_SEEDS.sh`
**Size:** 364 lines
**Type:** Bash automation script
**Permissions:** Executable (chmod +x)

**Features:**
- Colored console output (red/green/yellow/blue)
- Environment validation
- Virtual environment management
- Django migrations handling
- Sequential execution of Django management commands:
  1. generate_master_data
  2. generate_users
  3. generate_sentiment_data
  4. generate_social_posts
  5. generate_field_reports
  6. generate_direct_feedback
  7. generate_voters
  8. generate_voter_interactions
  9. generate_campaigns
  10. generate_events
- Error tracking and reporting
- Success/failure summary
- Supabase seed instructions
- Database verification
- Next steps guidance

**Usage:**
```bash
cd /Users/murali/Applications/pulseofpeople/backend
bash EXECUTE_ALL_SEEDS.sh
```

**Output Sections:**
1. Environment validation
2. Virtual environment activation
3. Django migrations
4. Management commands execution
5. Supabase instructions
6. Database verification
7. Summary report

---

## Installation Instructions

### Method 1: Supabase SQL Editor (Recommended)

1. Go to [https://app.supabase.com](https://app.supabase.com)
2. Select your project
3. Click "SQL Editor" in left sidebar
4. Click "New Query"
5. Copy content from `trending_topics_seed.sql`
6. Paste and click "Run"
7. Repeat for `alerts_seed.sql`
8. Verify with: `SELECT COUNT(*) FROM trending_topics;`

### Method 2: psql Command Line

```bash
# Connect to Supabase
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"

# Run seed files
\i /Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/trending_topics_seed.sql
\i /Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/alerts_seed.sql

# Verify
SELECT COUNT(*) FROM trending_topics;  -- Expected: 100
SELECT COUNT(*) FROM alerts;           -- Expected: 50
```

### Method 3: Direct Connection String

```bash
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  -f /Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/trending_topics_seed.sql

psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  -f /Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/alerts_seed.sql
```

---

## Verification Queries

### Quick Verification
```sql
-- Count records
SELECT COUNT(*) FROM trending_topics;  -- Expected: 100
SELECT COUNT(*) FROM alerts;           -- Expected: 50

-- Check data distribution
SELECT time_period, COUNT(*) FROM trending_topics GROUP BY time_period;
SELECT severity, COUNT(*) FROM alerts GROUP BY severity;
```

### Detailed Verification
```sql
-- Top 10 trending topics
SELECT keyword, volume, growth_rate, sentiment_score
FROM trending_topics
ORDER BY volume DESC
LIMIT 10;

-- Critical alerts
SELECT title, description, timestamp, district
FROM alerts
WHERE severity = 'critical'
ORDER BY timestamp DESC;

-- Water crisis topics
SELECT keyword, volume, sentiment_score
FROM trending_topics
WHERE keyword ILIKE '%water%'
ORDER BY volume DESC;

-- Active high-priority alerts
SELECT title, severity, type, timestamp, district
FROM alerts
WHERE severity IN ('critical', 'high')
  AND status = 'active'
ORDER BY timestamp DESC;
```

---

## Frontend Integration

### Supabase Client Setup
```typescript
// src/lib/supabaseClient.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

### Fetch Trending Topics
```typescript
// src/services/trendingTopicsService.ts
import { supabase } from '../lib/supabaseClient';

export async function getTrendingTopics(limit = 20) {
  const { data, error } = await supabase
    .from('trending_topics')
    .select('*')
    .order('volume', { ascending: false })
    .limit(limit);

  if (error) throw error;
  return data;
}
```

### Fetch Alerts
```typescript
// src/services/alertsService.ts
import { supabase } from '../lib/supabaseClient';

export async function getCriticalAlerts() {
  const { data, error } = await supabase
    .from('alerts')
    .select('*')
    .eq('severity', 'critical')
    .eq('status', 'active')
    .order('timestamp', { ascending: false });

  if (error) throw error;
  return data;
}
```

### React Component
```typescript
// src/components/TrendingTopicsWidget.tsx
import { useEffect, useState } from 'react';
import { getTrendingTopics } from '../services/trendingTopicsService';

export function TrendingTopicsWidget() {
  const [topics, setTopics] = useState([]);

  useEffect(() => {
    getTrendingTopics(10).then(setTopics);
  }, []);

  return (
    <div>
      {topics.map(topic => (
        <div key={topic.id}>
          <h3>{topic.keyword}</h3>
          <p>Volume: {topic.volume.toLocaleString()}</p>
          <p>Growth: {(topic.growth_rate * 100).toFixed(1)}%</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Dashboard Integration Points

### Analytics Dashboard
- Display top 10 trending topics by volume
- Show sentiment distribution chart
- Visualize growth rate trends over time
- Filter by platform (Twitter, Facebook, Instagram, News)
- Time period selector (24h, 7d, 30d)

### Alerts Dashboard
- Show critical alerts in header notification banner
- Group alerts by severity with color coding
- Filter by district/ward for geographic targeting
- Allow status updates (acknowledge/resolve)
- Timeline view of alert history

### Geographic View (Mapbox)
- Plot alerts on map by district coordinates
- Color-code markers by severity (red=critical, orange=high, yellow=medium, green=low)
- Show trending topics by region
- Heat map of sentiment by district
- Click markers for detailed alert information

### Real-time Features
- Subscribe to new alerts
- Live trending topics updates
- Sentiment score changes
- Volume spike notifications

---

## Data Characteristics

### Trending Topics
- **Total Records:** 100
- **Time Range:** Last 7 days
- **Update Frequency:** Real-time to daily
- **Volume Range:** 100-15,234 mentions
- **Growth Range:** 0.0-1.22 (0-122%)
- **Sentiment Range:** -0.73 to +0.79

**Top 5 by Volume:**
1. Vijay TVK - 15,234 mentions
2. Vijay Political Entry - 14,567 mentions
3. TVK Vision 2026 - 12,876 mentions
4. TVK Rally Chennai - 11,234 mentions
5. Vijay Speech Chennai - 10,234 mentions

**Most Negative:**
1. NEET Student Suicide - sentiment -0.73
2. Fishermen Arrests SL Navy - sentiment -0.58
3. Water Mafia TN - sentiment -0.62

**Most Positive:**
1. TVK Flag Launch - sentiment +0.79
2. TVK Coimbatore Rally - sentiment +0.78
3. Vijay Speech Chennai - sentiment +0.77

### Alerts
- **Total Records:** 50
- **Time Range:** Last 48 hours
- **Critical:** 5 alerts (require immediate action)
- **High:** 10 alerts (urgent response needed)
- **Medium:** 20 alerts (monitor closely)
- **Low:** 15 alerts (routine monitoring)

**Geographic Coverage:**
- Chennai: 8 alerts
- Coimbatore: 4 alerts
- Ramanathapuram: 3 alerts
- Salem: 3 alerts
- Others: 32 alerts across TN

---

## Maintenance & Updates

### Daily Tasks
- Check critical and high-severity alerts
- Monitor trending topics volume spikes
- Verify API endpoint responses
- Review alert status changes

### Weekly Tasks
- Run verification queries
- Archive resolved alerts older than 7 days
- Update trending topics with fresh data
- Generate weekly sentiment report

### Monthly Tasks
- Full database vacuum and analyze
- Review and optimize indexes
- Archive historical data (30+ days)
- Generate monthly performance report
- Update seed files with new issues

---

## Technical Specifications

### Database Requirements
- PostgreSQL 14+
- UUID extension enabled
- TIMESTAMPTZ support
- Array data types support
- Check constraints support

### Performance Optimizations
- Indexes on keyword, timestamp, volume, growth_rate
- Indexes on severity, type, status, district
- Partitioning by timestamp (for large datasets)
- Regular VACUUM ANALYZE operations

### Security Considerations
- Row Level Security (RLS) policies
- Role-based access control
- Audit logging for data modifications
- Input validation on all fields
- Prepared statements to prevent SQL injection

---

## Testing Checklist

- [ ] Trending topics seed file runs without errors
- [ ] Alerts seed file runs without errors
- [ ] 100 trending topics inserted
- [ ] 50 alerts inserted
- [ ] All indexes created successfully
- [ ] Verification queries return expected counts
- [ ] Frontend can fetch trending topics
- [ ] Frontend can fetch alerts
- [ ] Geographic filtering works
- [ ] Severity filtering works
- [ ] Real-time subscriptions functional
- [ ] Performance acceptable (<100ms queries)

---

## Troubleshooting

### UUID Extension Error
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Permission Denied
- Use service role key instead of anon key
- Check Supabase Authentication > Policies

### Duplicate Key Error
```sql
TRUNCATE TABLE trending_topics;
TRUNCATE TABLE alerts;
```

### Slow Queries
```sql
ANALYZE trending_topics;
ANALYZE alerts;
VACUUM ANALYZE trending_topics;
VACUUM ANALYZE alerts;
```

---

## Next Steps

1. ✅ SQL seed files created
2. ✅ Documentation completed
3. ✅ Execution script ready
4. Run Supabase seeds (manual step)
5. Test frontend integration
6. Connect to dashboard components
7. Enable real-time subscriptions
8. Add geographic visualization
9. Implement alert notifications
10. Set up automated data refresh

---

## Resources

- **Documentation:** `/Users/murali/Applications/pulseofpeople/backend/SUPABASE_SEEDS_README.md`
- **SQL Seeds:** `/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/`
- **Execution Script:** `/Users/murali/Applications/pulseofpeople/backend/EXECUTE_ALL_SEEDS.sh`
- **Supabase Docs:** https://supabase.com/docs
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Report Generated:** 2024-11-30
**Status:** Ready for deployment
**Next Action:** Run Supabase seed files via SQL Editor or psql
