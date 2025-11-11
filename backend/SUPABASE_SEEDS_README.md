# Supabase Seeds Documentation

## Overview

This document provides comprehensive instructions for seeding Supabase database tables with realistic Tamil Nadu political data for the Pulse of People platform.

## Table of Contents

1. [Seed Files](#seed-files)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Running Seeds](#running-seeds)
5. [Table Structures](#table-structures)
6. [Verification Queries](#verification-queries)
7. [Data Refresh Procedures](#data-refresh-procedures)
8. [Integration with Frontend](#integration-with-frontend)
9. [Troubleshooting](#troubleshooting)

---

## Seed Files

### Available Seed Files

| File | Records | Purpose | Location |
|------|---------|---------|----------|
| `trending_topics_seed.sql` | 100 | Political trending topics with sentiment | `/frontend/supabase/seeds/` |
| `alerts_seed.sql` | 50 | Real-time political alerts | `/frontend/supabase/seeds/` |

### Data Distribution

#### Trending Topics (100 records)
- **Water Crisis**: 25% (25 topics)
- **TVK/Political**: 30% (30 topics)
- **NEET**: 15% (15 topics)
- **Cauvery Dispute**: 10% (10 topics)
- **Jobs/Employment**: 10% (10 topics)
- **Fishermen Issues**: 5% (5 topics)
- **Others**: 5% (5 topics)

#### Alerts (50 records)
- **Sentiment Spike**: 40% (20 alerts)
- **Crisis Detection**: 30% (15 alerts)
- **Competitor Activity**: 15% (7-8 alerts)
- **Viral**: 10% (5 alerts)
- **System**: 5% (2-3 alerts)

**Severity Distribution:**
- Critical: 10% (5 alerts)
- High: 20% (10 alerts)
- Medium: 40% (20 alerts)
- Low: 30% (15 alerts)

---

## Prerequisites

### Requirements

1. **Supabase Account**: Active Supabase project
2. **PostgreSQL Access**: Either via Supabase SQL Editor or psql CLI
3. **Permissions**: Database admin permissions to create tables and insert data

### Environment Setup

```bash
# Supabase Project URL
SUPABASE_URL=https://your-project.supabase.co

# Supabase Anon/Public Key
SUPABASE_ANON_KEY=your-anon-key

# Supabase Service Role Key (for admin operations)
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

---

## Installation

### Method 1: Supabase SQL Editor (Recommended)

1. **Navigate to Supabase Dashboard**
   - Go to https://app.supabase.com
   - Select your project

2. **Open SQL Editor**
   - Click "SQL Editor" in left sidebar
   - Click "New Query"

3. **Copy Seed File Content**
   - Open seed file locally
   - Copy entire SQL content

4. **Paste and Execute**
   - Paste into SQL Editor
   - Click "Run" button

5. **Verify Results**
   - Check console output for success messages
   - Run verification queries (see below)

### Method 2: psql Command Line

```bash
# Connect to Supabase database
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"

# Run seed file
\i /path/to/pulseofpeople/frontend/supabase/seeds/trending_topics_seed.sql
\i /path/to/pulseofpeople/frontend/supabase/seeds/alerts_seed.sql

# Quit psql
\q
```

### Method 3: Direct Connection String

```bash
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  -f /path/to/trending_topics_seed.sql

psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres" \
  -f /path/to/alerts_seed.sql
```

---

## Running Seeds

### Step-by-Step Execution

#### 1. Run Trending Topics Seed

```sql
-- Execute trending_topics_seed.sql
-- This will:
-- 1. Create trending_topics table
-- 2. Create indexes
-- 3. Insert 100 trending topics
```

**Expected Output:**
```
CREATE EXTENSION
CREATE TABLE
CREATE INDEX (4 indexes)
TRUNCATE TABLE
INSERT 0 100
```

#### 2. Run Alerts Seed

```sql
-- Execute alerts_seed.sql
-- This will:
-- 1. Create alerts table
-- 2. Create indexes
-- 3. Insert 50 alerts
```

**Expected Output:**
```
CREATE EXTENSION
CREATE TABLE
CREATE INDEX (5 indexes)
TRUNCATE TABLE
INSERT 0 50
```

#### 3. Verify Installation

```sql
-- Check trending topics count
SELECT COUNT(*) FROM trending_topics;
-- Expected: 100

-- Check alerts count
SELECT COUNT(*) FROM alerts;
-- Expected: 50
```

---

## Table Structures

### trending_topics Table

```sql
CREATE TABLE trending_topics (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  keyword TEXT NOT NULL,
  volume INTEGER NOT NULL,
  growth_rate DECIMAL(5,2),
  sentiment_score DECIMAL(3,2),
  platforms TEXT[],
  time_period TEXT,
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
- `idx_trending_topics_keyword` - Keyword lookup
- `idx_trending_topics_timestamp` - Time-based queries
- `idx_trending_topics_volume` - Volume sorting
- `idx_trending_topics_growth_rate` - Growth rate sorting

**Sample Row:**
```json
{
  "id": "a1b2c3d4-e5f6-4a7b-8c9d-000000000001",
  "keyword": "Chennai Water Crisis",
  "volume": 8432,
  "growth_rate": 0.65,
  "sentiment_score": -0.45,
  "platforms": ["twitter", "facebook", "news"],
  "time_period": "24h",
  "timestamp": "2024-11-30T10:00:00Z"
}
```

### alerts Table

```sql
CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  severity TEXT CHECK (severity IN ('low','medium','high','critical')),
  type TEXT CHECK (type IN ('sentiment_spike','crisis','competitor_activity','viral','system')),
  status TEXT DEFAULT 'active' CHECK (status IN ('active','acknowledged','resolved')),
  timestamp TIMESTAMPTZ DEFAULT NOW(),
  ward TEXT,
  district TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Indexes:**
- `idx_alerts_severity` - Severity filtering
- `idx_alerts_type` - Type filtering
- `idx_alerts_status` - Status filtering
- `idx_alerts_timestamp` - Time-based queries
- `idx_alerts_district` - Geographic filtering

**Sample Row:**
```json
{
  "id": "c1r2i3t4-i5c6-4a7l-8a9l-000000000001",
  "title": "CRITICAL: Negative sentiment crash Coimbatore water crisis",
  "description": "Sentiment dropped 65% in 6 hours...",
  "severity": "critical",
  "type": "sentiment_spike",
  "status": "active",
  "timestamp": "2024-11-30T08:15:00Z",
  "ward": "Ward-23",
  "district": "Coimbatore"
}
```

---

## Verification Queries

### Trending Topics Verification

#### 1. Count Total Records
```sql
SELECT COUNT(*) FROM trending_topics;
-- Expected: 100
```

#### 2. Top 10 by Volume
```sql
SELECT keyword, volume, growth_rate, sentiment_score
FROM trending_topics
ORDER BY volume DESC
LIMIT 10;
```

#### 3. Highest Growth Rate
```sql
SELECT keyword, volume, growth_rate, sentiment_score
FROM trending_topics
ORDER BY growth_rate DESC
LIMIT 10;
```

#### 4. Most Negative Sentiment
```sql
SELECT keyword, volume, sentiment_score
FROM trending_topics
ORDER BY sentiment_score ASC
LIMIT 10;
```

#### 5. Most Positive Sentiment
```sql
SELECT keyword, volume, sentiment_score
FROM trending_topics
ORDER BY sentiment_score DESC
LIMIT 10;
```

#### 6. Distribution by Time Period
```sql
SELECT time_period, COUNT(*) as count
FROM trending_topics
GROUP BY time_period
ORDER BY count DESC;
```

#### 7. Distribution by Platform
```sql
SELECT UNNEST(platforms) as platform, COUNT(*) as count
FROM trending_topics
GROUP BY platform
ORDER BY count DESC;
```

#### 8. Water Crisis Topics
```sql
SELECT keyword, volume, sentiment_score
FROM trending_topics
WHERE keyword ILIKE '%water%'
ORDER BY volume DESC;
```

#### 9. TVK Political Topics
```sql
SELECT keyword, volume, sentiment_score
FROM trending_topics
WHERE keyword ILIKE '%TVK%' OR keyword ILIKE '%Vijay%'
ORDER BY volume DESC;
```

### Alerts Verification

#### 1. Count Total Alerts
```sql
SELECT COUNT(*) FROM alerts;
-- Expected: 50
```

#### 2. Alerts by Severity
```sql
SELECT severity, COUNT(*) as count
FROM alerts
GROUP BY severity
ORDER BY CASE severity
  WHEN 'critical' THEN 1
  WHEN 'high' THEN 2
  WHEN 'medium' THEN 3
  WHEN 'low' THEN 4
END;
```

#### 3. Alerts by Type
```sql
SELECT type, COUNT(*) as count
FROM alerts
GROUP BY type
ORDER BY count DESC;
```

#### 4. Alerts by Status
```sql
SELECT status, COUNT(*) as count
FROM alerts
GROUP BY status;
```

#### 5. Critical Alerts
```sql
SELECT title, description, timestamp, district
FROM alerts
WHERE severity = 'critical'
ORDER BY timestamp DESC;
```

#### 6. Active High-Severity Alerts
```sql
SELECT title, severity, type, timestamp, district
FROM alerts
WHERE severity IN ('critical', 'high')
  AND status = 'active'
ORDER BY timestamp DESC;
```

#### 7. Recent 24h Alerts
```sql
SELECT title, severity, type, timestamp
FROM alerts
WHERE timestamp > NOW() - INTERVAL '24 hours'
ORDER BY timestamp DESC;
```

#### 8. Alerts by District
```sql
SELECT district, COUNT(*) as count
FROM alerts
WHERE district IS NOT NULL
GROUP BY district
ORDER BY count DESC;
```

#### 9. Water Crisis Alerts
```sql
SELECT title, severity, timestamp, district
FROM alerts
WHERE title ILIKE '%water%' OR description ILIKE '%water%'
ORDER BY severity, timestamp DESC;
```

#### 10. Sentiment Spike Alerts
```sql
SELECT title, severity, timestamp, district
FROM alerts
WHERE type = 'sentiment_spike'
ORDER BY timestamp DESC;
```

---

## Data Refresh Procedures

### Complete Refresh (Delete and Re-seed)

```sql
-- Truncate tables
TRUNCATE TABLE trending_topics;
TRUNCATE TABLE alerts;

-- Re-run seed files
\i /path/to/trending_topics_seed.sql
\i /path/to/alerts_seed.sql
```

### Partial Refresh (Add New Data)

```sql
-- Add new trending topic
INSERT INTO trending_topics (keyword, volume, growth_rate, sentiment_score, platforms, time_period)
VALUES ('New Topic', 1000, 0.5, 0.3, ARRAY['twitter'], '24h');

-- Add new alert
INSERT INTO alerts (title, description, severity, type, status, district)
VALUES (
  'New Alert Title',
  'Detailed description...',
  'medium',
  'sentiment_spike',
  'active',
  'Chennai'
);
```

### Update Existing Data

```sql
-- Update trending topic volume
UPDATE trending_topics
SET volume = volume + 100,
    growth_rate = growth_rate + 0.1,
    updated_at = NOW()
WHERE keyword = 'Chennai Water Crisis';

-- Update alert status
UPDATE alerts
SET status = 'acknowledged',
    updated_at = NOW()
WHERE id = 'c1r2i3t4-i5c6-4a7l-8a9l-000000000001';
```

### Archive Old Data

```sql
-- Create archive tables
CREATE TABLE trending_topics_archive AS SELECT * FROM trending_topics;
CREATE TABLE alerts_archive AS SELECT * FROM alerts;

-- Delete old data (older than 30 days)
DELETE FROM trending_topics
WHERE timestamp < NOW() - INTERVAL '30 days';

DELETE FROM alerts
WHERE timestamp < NOW() - INTERVAL '30 days'
  AND status = 'resolved';
```

---

## Integration with Frontend

### React Frontend Integration

#### 1. Supabase Client Setup

```typescript
// src/lib/supabaseClient.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
```

#### 2. Fetch Trending Topics

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

export async function getTrendingTopicsByGrowth(limit = 20) {
  const { data, error } = await supabase
    .from('trending_topics')
    .select('*')
    .order('growth_rate', { ascending: false })
    .limit(limit);

  if (error) throw error;
  return data;
}
```

#### 3. Fetch Alerts

```typescript
// src/services/alertsService.ts
import { supabase } from '../lib/supabaseClient';

export async function getActiveAlerts(severity?: string) {
  let query = supabase
    .from('alerts')
    .select('*')
    .eq('status', 'active')
    .order('timestamp', { ascending: false });

  if (severity) {
    query = query.eq('severity', severity);
  }

  const { data, error } = await query;
  if (error) throw error;
  return data;
}

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

export async function updateAlertStatus(id: string, status: string) {
  const { data, error } = await supabase
    .from('alerts')
    .update({ status, updated_at: new Date().toISOString() })
    .eq('id', id)
    .select();

  if (error) throw error;
  return data;
}
```

#### 4. React Component Example

```typescript
// src/components/TrendingTopicsWidget.tsx
import { useEffect, useState } from 'react';
import { getTrendingTopics } from '../services/trendingTopicsService';

export function TrendingTopicsWidget() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTopics() {
      try {
        const data = await getTrendingTopics(10);
        setTopics(data);
      } catch (error) {
        console.error('Error loading trending topics:', error);
      } finally {
        setLoading(false);
      }
    }
    loadTopics();
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="trending-topics">
      <h2>Trending Topics</h2>
      {topics.map((topic) => (
        <div key={topic.id} className="topic-item">
          <h3>{topic.keyword}</h3>
          <p>Volume: {topic.volume.toLocaleString()}</p>
          <p>Growth: {(topic.growth_rate * 100).toFixed(1)}%</p>
          <p>Sentiment: {topic.sentiment_score.toFixed(2)}</p>
        </div>
      ))}
    </div>
  );
}
```

### Dashboard Integration Points

#### Analytics Dashboard
- Display top 10 trending topics by volume
- Show sentiment distribution chart
- Visualize growth rate trends

#### Alerts Dashboard
- Show critical alerts in header notification
- Group alerts by severity
- Filter by district/ward
- Allow status updates (acknowledge/resolve)

#### Geographic View (Mapbox)
- Plot alerts on map by district
- Color-code by severity
- Show trending topics by region

---

## Troubleshooting

### Common Issues

#### 1. UUID Extension Not Found

**Error:**
```
ERROR: type "uuid" does not exist
```

**Solution:**
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

#### 2. Permission Denied

**Error:**
```
ERROR: permission denied for table trending_topics
```

**Solution:**
- Use service role key instead of anon key
- Grant permissions in Supabase Dashboard > Authentication > Policies

#### 3. Duplicate Key Error

**Error:**
```
ERROR: duplicate key value violates unique constraint "trending_topics_pkey"
```

**Solution:**
```sql
-- Truncate table before re-running
TRUNCATE TABLE trending_topics;
```

#### 4. Table Already Exists

**Error:**
```
ERROR: relation "trending_topics" already exists
```

**Solution:**
```sql
-- Drop table first
DROP TABLE IF EXISTS trending_topics;
-- Re-run seed file
```

#### 5. Date/Time Issues

**Error:**
```
ERROR: invalid input syntax for type timestamp
```

**Solution:**
- Ensure PostgreSQL timezone is set: `SET timezone = 'UTC';`
- Use `TIMESTAMPTZ` instead of `TIMESTAMP`

### Performance Optimization

#### 1. Slow Queries

```sql
-- Analyze table statistics
ANALYZE trending_topics;
ANALYZE alerts;

-- Check index usage
SELECT * FROM pg_stat_user_indexes
WHERE relname IN ('trending_topics', 'alerts');
```

#### 2. Add Missing Indexes

```sql
-- Add custom indexes if needed
CREATE INDEX idx_trending_topics_sentiment ON trending_topics(sentiment_score DESC);
CREATE INDEX idx_alerts_district_severity ON alerts(district, severity);
```

#### 3. Vacuum Tables

```sql
-- Clean up dead rows
VACUUM ANALYZE trending_topics;
VACUUM ANALYZE alerts;
```

### Data Validation

```sql
-- Check for null values
SELECT COUNT(*) FROM trending_topics WHERE keyword IS NULL;
SELECT COUNT(*) FROM alerts WHERE title IS NULL;

-- Check for invalid severity values
SELECT DISTINCT severity FROM alerts;

-- Check timestamp ranges
SELECT MIN(timestamp), MAX(timestamp) FROM trending_topics;
SELECT MIN(timestamp), MAX(timestamp) FROM alerts;

-- Check for duplicate keywords
SELECT keyword, COUNT(*)
FROM trending_topics
GROUP BY keyword
HAVING COUNT(*) > 1;
```

---

## Maintenance Schedule

### Daily Tasks
- Check critical alerts
- Monitor data freshness (timestamps)
- Verify API endpoint responses

### Weekly Tasks
- Run verification queries
- Archive resolved alerts older than 7 days
- Update trending topics with fresh data

### Monthly Tasks
- Full database vacuum
- Review and optimize indexes
- Archive old data (30+ days)
- Generate performance reports

---

## Support

### Resources
- **Supabase Docs**: https://supabase.com/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Project Repository**: /Users/murali/Applications/pulseofpeople

### Contact
For issues or questions:
1. Check this documentation first
2. Review Supabase logs in Dashboard
3. Test queries in SQL Editor
4. Consult team for complex issues

---

**Document Version**: 1.0
**Last Updated**: 2024-11-30
**Maintained By**: Pulse of People Development Team
