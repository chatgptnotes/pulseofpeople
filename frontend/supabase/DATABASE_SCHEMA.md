# Pulse of People - Database Schema Documentation

## Overview

This document describes the complete Supabase database schema for the BETTROI Voter Sentiment Dashboard (Pulse of People). The schema supports a comprehensive political intelligence platform with real-time sentiment analysis, social media monitoring, field operations, and voter engagement tracking.

## Quick Start

### Applying the Migration

To create all tables in your Supabase instance:

1. Navigate to your Supabase project dashboard
2. Go to the SQL Editor
3. Copy the contents of `migrations/20251027_create_all_tables.sql`
4. Execute the SQL script
5. Verify all tables are created successfully

Alternatively, using Supabase CLI:

```bash
supabase db push
```

## Database Architecture

### Core Components

The database consists of **20 main tables** organized into functional groups:

#### 1. User Management
- `users` - User accounts with role-based access
- `volunteers` - Field worker profiles and performance metrics

#### 2. Sentiment & Analytics
- `sentiment_data` - Core sentiment analysis results
- `social_posts` - Social media posts and engagement
- `trending_topics` - Real-time trending keywords
- `media_coverage` - News and media monitoring

#### 3. Intelligence & Insights
- `influencers` - Key voice identification and tracking
- `alerts` - Real-time alerts and notifications
- `recommendations` - AI-generated strategic recommendations
- `competitor_activity` - Opposition tracking

#### 4. Field Operations
- `field_reports` - Ground-level reports from volunteers
- `surveys` - Survey campaigns
- `survey_questions` - Survey question bank
- `survey_responses` - Survey response data
- `campaign_events` - Event planning and tracking

#### 5. Engagement
- `voters` - Privacy-compliant voter database
- `conversations` - Bot interactions and feedback

#### 6. Business Operations
- `subscriptions` - Subscription and billing management
- `demo_requests` - Demo request tracking

#### 7. System
- `audit_log` - System audit trail
- `system_settings` - Configuration management

## Data Model Details

### Sentiment Data Flow

```
Data Sources (Social Media, Surveys, Field Reports)
    ↓
sentiment_data (central repository)
    ↓
Analytics & Visualization
    ↓
Alerts & Recommendations
```

### Key Features

#### Multi-Language Support
Supports 12 languages for sentiment analysis:
- English (en)
- Hindi (hi)
- Bengali (bn)
- Marathi (mr)
- Tamil (ta)
- Telugu (te)
- Gujarati (gu)
- Kannada (kn)
- Malayalam (ml)
- Odia (or)
- Punjabi (pa)

#### Emotion Detection
Tracks 9 distinct emotions:
- Anger, Trust, Fear, Hope, Pride, Joy, Sadness, Surprise, Disgust

#### Geographic Intelligence
- PostGIS integration for spatial queries
- Ward-level granularity
- Coordinates-based tracking
- Heatmap support

## Security & Privacy

### Row Level Security (RLS)

All tables have RLS enabled with role-based policies:

**Role Hierarchy:**
1. **Admin** - Full access to all data
2. **Analyst** - Read access to analytics, can verify submissions
3. **Ward Coordinator** - Access to ward-specific data
4. **Social Media Monitor** - Social media data access
5. **Survey Team** - Survey data access
6. **Truth Team** - Verification capabilities
7. **Viewer** - Read-only dashboard access

### Data Privacy Compliance (DPDP Act)

The schema implements privacy-first principles:

1. **Voter Data Protection**
   - Voter IDs are hashed
   - Demographics are anonymized
   - Consent tracking required
   - Configurable data retention periods

2. **Survey Responses**
   - Respondent IDs are anonymized
   - Demographics stored separately
   - No personally identifiable information

3. **Field Reports**
   - Location data can be aggregated
   - Media attachments stored securely
   - Verification workflow

4. **Audit Trail**
   - All data access logged
   - User actions tracked
   - IP address recording

## Indexes & Performance

### Critical Indexes

Each table has optimized indexes for:
- Primary lookups (by ID)
- Time-series queries (timestamp columns)
- Geographic queries (PostGIS GIST indexes)
- Full-text search (GIN indexes on arrays)
- Foreign key relationships

### Example Queries

**Get overall sentiment for the last 24 hours:**
```sql
SELECT calculate_overall_sentiment(
    NOW() - INTERVAL '24 hours',
    NOW(),
    NULL  -- No ward filter
);
```

**Find trending issues:**
```sql
SELECT * FROM get_trending_issues('24h', 5);
```

**Detect sentiment anomalies:**
```sql
SELECT * FROM detect_sentiment_anomalies();
```

**Ward-wise sentiment summary:**
```sql
SELECT * FROM ward_sentiment_summary;
```

## Analytics Functions

### Built-in Functions

1. **`calculate_overall_sentiment(start_time, end_time, ward_filter)`**
   - Calculates average sentiment for a time period
   - Optional ward filtering
   - Returns: DECIMAL (0-1 scale)

2. **`get_trending_issues(time_period, limit_count)`**
   - Identifies trending issues by mention count
   - Returns: TABLE(issue, mention_count, avg_sentiment)

3. **`detect_sentiment_anomalies()`**
   - Identifies sentiment spikes using statistical analysis
   - 2-sigma deviation threshold
   - Returns: TABLE with deviation metrics

### Materialized Views

Key views for dashboard performance:

1. **`dashboard_metrics`** - Real-time dashboard KPIs
2. **`top_influencers`** - Top 50 influencers by influence score
3. **`ward_sentiment_summary`** - Ward-level sentiment aggregation

## Data Relationships

### Primary Relationships

```
users
  ├─→ field_reports (volunteer_id)
  ├─→ volunteers (user_id)
  ├─→ alerts (assignee)
  ├─→ surveys (created_by)
  └─→ recommendations (reviewed_by)

surveys
  ├─→ survey_questions
  └─→ survey_responses

sentiment_data
  ├─→ social_posts (source_id)
  ├─→ field_reports (source_id)
  └─→ survey_responses (source_id)
```

## Maintenance

### Automatic Updates

- **`updated_at` triggers**: Automatically update on row modification
- All major tables have auto-updating timestamps

### Data Retention

Default retention policies:
- Sentiment data: 365 days
- Social posts: 90 days (configurable)
- Audit logs: 730 days
- Voter data: Based on consent period

Configure via `system_settings` table:
```sql
UPDATE system_settings
SET value = '180'
WHERE key = 'data_retention_days';
```

## Extension Requirements

The schema requires these PostgreSQL extensions:

1. **uuid-ossp** - UUID generation
2. **postgis** - Geographic/spatial data support

These are automatically created in the migration script.

## Table Details

### sentiment_data
**Purpose:** Central repository for all sentiment analysis results

**Key Columns:**
- `sentiment` - Numerical score (0-1)
- `polarity` - positive/negative/neutral
- `emotion` - Detected emotion
- `confidence` - Analysis confidence score
- `language` - Source language
- `source` - Data origin
- Location fields (state, district, ward, coordinates)
- Demographic fields (age_group, gender, education, income)

**Indexes:** issue, timestamp, ward, source, polarity, emotion, location_point

**Use Cases:**
- Real-time sentiment tracking
- Trend analysis
- Geographic intelligence
- Issue-based insights

### social_posts
**Purpose:** Social media content with engagement metrics

**Key Columns:**
- `platform` - twitter/facebook/instagram/youtube/whatsapp/news/blog
- `content` - Post text
- `author_*` - Author details and metrics
- `likes`, `shares`, `comments`, `reach` - Engagement
- `hashtags`, `mentions` - Content analysis
- `sentiment_score` - Denormalized sentiment

**Indexes:** platform, timestamp, author_handle, sentiment, hashtags (GIN)

**Use Cases:**
- Social media monitoring
- Influencer tracking
- Viral content detection
- Platform-wise analysis

### influencers
**Purpose:** Key voice identification and tracking

**Key Columns:**
- `name`, `handle`, `avatar` - Profile info
- `platforms[]` - Active platforms
- `total_followers`, `engagement_rate` - Reach metrics
- `influence_score` - Calculated influence (0-100)
- `category` - Influencer type
- `political_lean` - Political alignment
- `credibility_score`, `risk_level` - Risk assessment

**Indexes:** handle, category, influence_score, risk_level, platforms (GIN)

**Use Cases:**
- Influencer outreach
- Risk monitoring
- Coalition building
- Opposition tracking

### alerts
**Purpose:** Real-time alert system

**Key Columns:**
- `severity` - low/medium/high/critical
- `type` - Alert category
- `status` - active/acknowledged/resolved/dismissed
- `metrics` - Current vs previous values
- `recommendations[]` - Suggested actions
- `assignee` - Responsible user

**Indexes:** severity, status, timestamp, type, ward, assignee

**Use Cases:**
- Crisis detection
- Sentiment spike alerts
- Competitor activity monitoring
- Action triggering

### field_reports
**Purpose:** Ground intelligence from volunteers

**Key Columns:**
- `volunteer_id` - Submitter
- Location (coordinates, address, ward)
- `report_type` - daily_summary/event_feedback/issue_report/competitor_activity
- Content arrays (positive/negative reactions, issues, quotes)
- `verification_status` - Quality control
- `media_attachments[]` - Supporting media

**Indexes:** volunteer, ward, timestamp, verification, type, location_point

**Use Cases:**
- Field intelligence
- Event tracking
- Issue identification
- Volunteer performance

### surveys & survey_responses
**Purpose:** Polling and survey management

**Key Tables:**
- `surveys` - Campaign configuration
- `survey_questions` - Question bank
- `survey_responses` - Response data

**Features:**
- Target demographic filtering
- Statistical analysis (confidence, margin of error)
- JSONB answers for flexibility
- Anonymous respondent tracking

**Use Cases:**
- Public opinion polling
- Issue prioritization
- Demographic analysis
- Campaign feedback

### voters
**Purpose:** Privacy-compliant voter database

**Key Columns:**
- `voter_id_hash` - Anonymized identifier
- Demographics (age_group, gender, education, income)
- `segment` - 50 planned segments
- `sentiment_score` - Voter sentiment
- `consent_given`, `consent_date` - Privacy compliance
- `data_retention_period` - Configurable retention

**Indexes:** ward, segment, age_group, sentiment, consent

**Privacy Features:**
- All IDs hashed
- Consent tracking
- Automatic retention management
- RLS restricted to admins/analysts only

**Use Cases:**
- Voter segmentation
- Targeted outreach
- Demographic analysis
- Compliance reporting

### recommendations
**Purpose:** AI-generated strategic recommendations

**Key Columns:**
- `type` - event/messaging/resource_allocation/outreach/crisis_response
- `priority` - low/medium/high/urgent
- `confidence_score` - AI confidence
- `rationale` - Explanation
- `suggested_actions[]` - Action items
- `estimated_impact` - Expected outcome
- `status` - Implementation tracking

**Indexes:** type, priority, status, generated_date

**Use Cases:**
- Strategic planning
- Resource allocation
- Crisis response
- Campaign optimization

## Migration History

| Date | File | Description |
|------|------|-------------|
| 2025-10-22 | `20251022190808_create_demo_requests_table.sql` | Initial demo requests table |
| 2025-10-27 | `20251027_create_all_tables.sql` | Complete schema with all 20 tables |

## Backup & Recovery

### Recommended Backup Strategy

1. **Automated Backups** - Enable Supabase automated daily backups
2. **Critical Tables** - Extra backups for:
   - sentiment_data
   - voters
   - survey_responses
   - field_reports

3. **Export Schedule**
   - Daily: sentiment_data (last 24h)
   - Weekly: Full database dump
   - Monthly: Archive to cold storage

### Recovery Procedures

1. **Point-in-time recovery** available via Supabase dashboard
2. **Selective restore** for specific tables
3. **Audit log** for tracking data changes

## Monitoring

### Key Metrics to Monitor

1. **Table Sizes**
   ```sql
   SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
   FROM pg_tables
   WHERE schemaname = 'public'
   ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
   ```

2. **Index Usage**
   ```sql
   SELECT * FROM pg_stat_user_indexes
   WHERE schemaname = 'public'
   ORDER BY idx_scan DESC;
   ```

3. **Slow Queries** - Monitor via Supabase dashboard

## Troubleshooting

### Common Issues

**Issue:** RLS blocking queries
**Solution:** Check user authentication and role assignments

**Issue:** Slow geographic queries
**Solution:** Verify PostGIS indexes are created

**Issue:** Large table sizes
**Solution:** Implement data retention policies

## Support & Contact

For issues or questions about the database schema:
- Review this documentation
- Check Supabase logs
- Contact: Animal-i Initiative (Dubai HQ)

## Version

**Schema Version:** 1.0
**Last Updated:** 2025-10-27
**Compatible With:** Supabase PostgreSQL 15+

---

**Note:** This schema is designed for the Kerala 2026 elections and can be adapted for other electoral contexts.
