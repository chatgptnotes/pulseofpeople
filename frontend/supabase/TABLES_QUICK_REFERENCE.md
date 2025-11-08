# Pulse of People - Tables Quick Reference

## All Tables Summary

### User Management (2 tables)
1. **users** - User accounts with role-based access (admin, analyst, viewer, ward-coordinator, social-media, survey-team, truth-team)
2. **volunteers** - Field worker profiles and performance metrics

### Sentiment & Analytics (4 tables)
3. **sentiment_data** - Core sentiment analysis results (0-1 scale, emotions, languages, demographics)
4. **social_posts** - Social media posts with engagement metrics (Twitter, Facebook, Instagram, YouTube, WhatsApp, News, Blog)
5. **trending_topics** - Real-time trending keywords with volume and growth rates
6. **media_coverage** - News and media monitoring (TV, radio, print, online)

### Intelligence & Insights (4 tables)
7. **influencers** - Key voice identification (50 top influencers, engagement, risk levels)
8. **alerts** - Real-time alerts (sentiment spikes, volume surges, crisis detection)
9. **recommendations** - AI-generated strategic recommendations
10. **competitor_activity** - Opposition tracking (rallies, statements, campaigns)

### Field Operations (5 tables)
11. **field_reports** - Ground-level reports from volunteers
12. **surveys** - Survey campaigns with target demographics
13. **survey_questions** - Survey question bank (multiple choice, rating, text, yes/no)
14. **survey_responses** - Anonymized survey response data
15. **campaign_events** - Event planning and tracking (rallies, townhalls, meetings)

### Engagement (2 tables)
16. **voters** - Privacy-compliant voter database (hashed IDs, 50 segments)
17. **conversations** - Bot interactions and feedback (web, WhatsApp, Telegram, SMS, voice)

### Business Operations (2 tables)
18. **subscriptions** - Subscription management (₹6,000/month per area)
19. **demo_requests** - Demo request tracking (existing table)

### System (2 tables)
20. **audit_log** - Complete audit trail of all actions
21. **system_settings** - System configuration (JSON key-value store)

---

## Table Sizes (Estimated)

| Priority | Table | Expected Growth |
|----------|-------|-----------------|
| High | sentiment_data | Very High (thousands/day) |
| High | social_posts | Very High (thousands/day) |
| Medium | field_reports | Medium (hundreds/day) |
| Medium | survey_responses | Medium (hundreds/day) |
| Low | alerts | Low (tens/day) |
| Low | voters | Static (loaded once) |
| Low | influencers | Static (updated weekly) |

---

## Key Relationships

```
users (central hub)
  ├─→ field_reports.volunteer_id
  ├─→ volunteers.user_id
  ├─→ alerts.assignee
  ├─→ surveys.created_by
  ├─→ recommendations.reviewed_by
  └─→ conversations.assigned_to

sentiment_data (analytics core)
  ├─← social_posts (via source_id)
  ├─← field_reports (via source_id)
  └─← survey_responses (via source_id)

surveys (survey system)
  ├─→ survey_questions
  └─→ survey_responses
```

---

## Data Types Summary

### Enumerations

**User Roles:**
- admin, analyst, viewer, ward-coordinator, social-media, survey-team, truth-team

**Sentiment Polarity:**
- positive, negative, neutral

**Emotions (9):**
- anger, trust, fear, hope, pride, joy, sadness, surprise, disgust

**Languages (12):**
- en, hi, bn, mr, ta, te, gu, kn, ml, or, pa

**Issues (6):**
- Jobs, Infrastructure, Health, Education, Law & Order, Other

**Sources:**
- social_media, survey, field_report, news, direct_feedback

**Platforms:**
- twitter, facebook, instagram, youtube, whatsapp, news, blog

**Alert Severity:**
- low, medium, high, critical

**Alert Types:**
- sentiment_spike, volume_surge, crisis_detected, trend_change, competitor_activity, influencer_activity

**Alert Status:**
- active, acknowledged, resolved, dismissed

---

## Geographic Fields

Most tables include location tracking:
- `state` (TEXT) - Default: 'Kerala'
- `district` (TEXT)
- `ward` (TEXT)
- `location_lat` (DECIMAL 10,8)
- `location_lng` (DECIMAL 11,8)
- `location_point` (GEOGRAPHY) - PostGIS point for spatial queries

---

## Demographic Fields

Privacy-compliant anonymized demographics:
- `age_group` - 18-25, 26-35, 36-45, 46-55, 55+
- `gender` - male, female, other
- `education` - primary, secondary, graduate, postgraduate
- `income` - low, middle, high

---

## Common Timestamps

All tables include:
- `created_at` - Automatic on insert
- `updated_at` - Auto-updates on modification (via triggers)
- `timestamp` - Event/data timestamp

---

## Indexes Overview

Every table has optimized indexes for:
1. Primary key (UUID)
2. Timestamp columns (DESC for recent-first queries)
3. Foreign keys
4. Filter fields (status, type, role, etc.)
5. Geographic fields (GIST for PostGIS)
6. Array fields (GIN for array/JSONB)

---

## Row Level Security (RLS)

All tables have RLS enabled. Basic policy structure:

**Public Access:**
- demo_requests (insert only)

**Authenticated Access:**
- sentiment_data (read)
- social_posts (read)
- trending_topics (read)
- media_coverage (read)
- alerts (read)
- recommendations (read)
- campaign_events (read)

**Role-Based Access:**
- users (own data + admins)
- field_reports (own reports + ward coordinators + admins)
- voters (admins + analysts only - DPDP compliance)
- subscriptions (admins only)
- audit_log (admins only)
- system_settings (admins only)

**Ward-Based Access:**
- Ward coordinators can access data for their assigned ward

---

## Storage Estimates

Based on Kerala 2026 elections (140 constituencies, ~1000 wards):

| Table | Rows/Day | Size/Row | Daily Growth |
|-------|----------|----------|--------------|
| sentiment_data | 50,000 | 1 KB | 50 MB |
| social_posts | 30,000 | 2 KB | 60 MB |
| field_reports | 1,000 | 5 KB | 5 MB |
| survey_responses | 2,000 | 3 KB | 6 MB |
| **Total** | | | **~120 MB/day** |

Monthly: ~3.6 GB
Campaign (6 months): ~22 GB

---

## Performance Tips

1. **Use indexes** - All key fields are indexed
2. **Filter by timestamp** - Use date ranges to limit data
3. **Ward filtering** - Reduce data by geographic scope
4. **Materialized views** - Use pre-computed views for dashboards
5. **Batch operations** - Use bulk inserts for large data loads
6. **Archive old data** - Move data older than retention period

---

## Quick SQL Commands

**Check table sizes:**
```sql
SELECT tablename, pg_size_pretty(pg_total_relation_size('public.' || tablename))
FROM pg_tables WHERE schemaname = 'public'
ORDER BY pg_total_relation_size('public.' || tablename) DESC;
```

**Count records by table:**
```sql
SELECT 'sentiment_data' as table, COUNT(*) FROM sentiment_data
UNION ALL
SELECT 'social_posts', COUNT(*) FROM social_posts
UNION ALL
SELECT 'field_reports', COUNT(*) FROM field_reports;
```

**Recent data check:**
```sql
SELECT 'sentiment_data' as table, MAX(created_at) as latest FROM sentiment_data
UNION ALL
SELECT 'social_posts', MAX(created_at) FROM social_posts
UNION ALL
SELECT 'alerts', MAX(created_at) FROM alerts;
```

**Ward-wise data distribution:**
```sql
SELECT ward, COUNT(*) as count
FROM sentiment_data
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY ward
ORDER BY count DESC
LIMIT 20;
```

---

## Migration Checklist

- [ ] Backup existing database
- [ ] Enable required extensions (uuid-ossp, postgis)
- [ ] Run migration script
- [ ] Verify all 21 tables created
- [ ] Check all indexes created
- [ ] Verify RLS policies active
- [ ] Test basic queries
- [ ] Create first admin user
- [ ] Configure system_settings
- [ ] Test authentication & permissions
- [ ] Enable automated backups
- [ ] Set up monitoring

---

## Next Steps After Migration

1. **Create Admin User**
   ```sql
   INSERT INTO users (name, email, role, permissions)
   VALUES ('Admin User', 'admin@example.com', 'admin', ARRAY['view_all', 'edit_all', 'manage_users']);
   ```

2. **Configure System Settings**
   - Review and adjust alert thresholds
   - Set data retention periods
   - Configure social media refresh intervals

3. **Set Up Subscriptions**
   - Create subscription records for active clients
   - Configure billing schedules

4. **Import Initial Data**
   - Ward/district boundaries
   - Initial voter segments
   - System configurations

5. **Test Data Flow**
   - Insert test sentiment data
   - Verify analytics functions
   - Check alert generation
   - Test RLS policies

---

**Schema Version:** 1.0
**Migration File:** `supabase/migrations/20251027_create_all_tables.sql`
**Documentation:** `supabase/DATABASE_SCHEMA.md`
