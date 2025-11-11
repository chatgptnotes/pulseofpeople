# Database Schema - Quick Reference

## Core Tables Summary

### Authentication (5 tables)
- **auth_user** - Django built-in user authentication
- **api_userprofile** - Extended profile with roles and 2FA
- **api_organization** - Multi-tenant support
- **api_permission** - 67 granular permissions
- **api_rolepermission** / **api_userpermission** - RBAC mapping

### Geographic (4 tables)
- **api_state** - Indian states (28 total)
- **api_district** - Districts within states (600+ total)
- **api_constituency** - Electoral constituencies (4,000+ total)
- **api_pollingbooth** - Voting stations (1M+ total)

### Voters & Engagement (4 tables)
- **api_voter** - Voter database (millions)
- **api_voterinteraction** - Interaction tracking (millions)
- **api_boothagent** - Booth-level workers
- **api_volunteerprofile** - Volunteer profiles

### Feedback & Analysis (3 tables)
- **api_directfeedback** - Citizen feedback with AI analysis
- **api_fieldreport** - Ground-level reports from workers
- **api_sentimentdata** - Aggregated sentiment scores

### Campaigns (3 tables)
- **api_campaign** - Campaign management
- **api_event** - Event tracking (rallies, meetings, door-to-door)
- **api_socialmediapost** - Social media tracking

### Administration (8 tables)
- **api_issuecategory** - Issue types (hierarchical)
- **api_votersegment** - Voter demographic segments
- **api_politicalparty** - Political parties database
- **api_alert** - Critical alerts/notifications
- **api_notification** - User notifications (Supabase sync)
- **api_auditlog** - Compliance audit trail
- **api_uploadedfile** - File metadata (Supabase Storage)
- **api_expense** - Campaign/event expenses

### Analytics (4 tables)
- **api_dailyvoterstats** - Daily voter aggregation
- **api_dailyinteractionstats** - Daily interaction metrics
- **api_dailysentimentstats** - Daily sentiment trends
- **api_weeklycampaignstats** - Weekly campaign metrics

### Reporting (3 tables)
- **api_reporttemplate** - Custom report templates
- **api_generatedreport** - Generated report tracking
- **api_exportjob** - Data export jobs

### Bulk Operations (2 tables)
- **api_bulkuploadjob** - Bulk upload tracking
- **api_bulkuploaderror** - Error tracking per row

---

## Key Relationships

```
State (1) ──many─→ District ──many─→ Constituency ──many─→ PollingBooth
          ├─many→ Voter
          └─many→ IssueCategory

Voter (1) ──many─→ VoterInteraction
                  ├─from─ UserProfile (admin assignment)
                  └─to─ ContactedBy (User)

DirectFeedback/FieldReport ──→ SentimentData ──→ DailySentimentStats

Campaign ──many─→ Event ──many─→ Expense
        ├─many→ SocialMediaPost
        └─many→ TeamMembers (Users)

UserProfile (1) ──OneToOne─→ BoothAgent/VolunteerProfile
            ├─many→ Organization
            └─many→ Permission (via UserPermission)
```

---

## Column Type Quick Reference

| Type | Usage | Examples |
|------|-------|----------|
| CharField(max_length) | Text fields | names, codes, phone |
| TextField | Long text | descriptions, notes |
| IntegerField | Whole numbers | counts, ages, costs |
| DecimalField(max_digits, decimal_places) | Money/percentages | 10,2 for currency, 4,2 for scores |
| DateField | Date only | date_of_birth, report_date |
| DateTimeField | Date + time | created_at, interaction_date |
| BooleanField | True/False | is_active, is_verified |
| ImageField | Image uploads | avatar, photo |
| URLField | Web addresses | website, avatar_url |
| UUIDField | Unique IDs | feedback_id, report_id |
| JSONField | Structured data | tags, voting_history, metadata |
| ForeignKey | Link to another table | state_id → State.id |
| ManyToManyField | Multi-select | team_members, key_issues |

---

## Constraints Checklist

### Unique Constraints
```
- auth_user.username
- api_userprofile.user_id (OneToOne)
- api_organization.slug
- api_permission.name
- api_state.name, api_state.code
- api_district.code
- api_constituency.code
- api_constituency (state_id, code)
- api_district (state_id, name)
- api_pollingbooth (constituency_id, booth_number)
- api_voter.voter_id
- api_volunteerprofile.volunteer_id
- api_directfeedback.feedback_id
- api_fieldreport.report_id
- api_notification.supabase_id
- api_bulkuploadjob.job_id
```

### Foreign Key Constraints
```
All models must satisfy:
- user_id → auth_user.id (nullable if optional)
- state_id → api_state.id
- district_id → api_district.id
- constituency_id → api_constituency.id
- organization_id → api_organization.id
- issue_category_id → api_issuecategory.id
- etc.
```

### Validation Rules
```
- Age: 18-120 (MinValueValidator, MaxValueValidator)
- Sentiment Score: 0.0-1.0
- Rating: 0-5
- Percentages: 0-100
- Status: must match CHOICES definition
```

---

## Performance Indexes

### Query Optimization (Most Used Indexes)
```
Voters:
  - voter_id (lookup by ID)
  - (constituency_id, ward) (geographic filter)
  - (party_affiliation) (segment by party)
  - (sentiment) (sentiment analysis)
  - (-created_at) (recent voters)

Interactions:
  - (voter_id, -interaction_date) (voter history)
  - (contacted_by_id) (agent performance)
  - (interaction_type) (type analytics)

Feedback:
  - (status) (workflow filtering)
  - (-submitted_at) (recent feedback)
  - (constituency_id) (geographic)
  - (issue_category_id) (topic analysis)

Polling Booths:
  - (constituency_id) (booth lookup)
  - (booth_number) (official ID)
  - (is_active) (operational booths)

Geographic:
  - (state_id, name) (district lookup)
  - (state_id, constituency_type) (AC/PC)
```

---

## Typical Query Patterns

### Get all voters in a constituency
```python
Voter.objects.filter(constituency_id=5)
```

### Get interactions for a voter
```python
voter.voterinteraction_set.all()
# or
VoterInteraction.objects.filter(voter_id=voter_id)
```

### Sentiment by issue in a constituency
```python
SentimentData.objects.filter(
    constituency_id=5,
    issue_id=3
).aggregate(Avg('sentiment_score'))
```

### Recent feedback pending review
```python
DirectFeedback.objects.filter(
    status='pending'
).order_by('-submitted_at')[:50]
```

### Campaign ROI calculation
```python
campaign = Campaign.objects.get(id=1)
roi = ((campaign.spent_amount - campaign.budget) / 
       campaign.budget * 100)
```

---

## Migration Safe Practices

### Running Migrations
```bash
# Show pending migrations
python manage.py showmigrations

# Run migrations
python manage.py migrate

# Roll back specific migration
python manage.py migrate api 0009  # Goes back to 0009

# Create new migration after model changes
python manage.py makemigrations
python manage.py migrate
```

### Current State
```
Latest Migration: 0010_merge_20251109_0533
Conflicting Branches: 0007 (security_and_performance vs workstream2_core_models)
Resolution: Merged at 0010

Next Action: Check if 0011 is needed or start fresh schema
```

---

## Data Volume Guidelines

| Table | Small | Medium | Large |
|-------|-------|--------|-------|
| Voter | 10K | 50K | 500K+ |
| VoterInteraction | 1K | 5K | 50K+ |
| DirectFeedback | 500 | 2.5K | 25K+ |
| FieldReport | 100 | 500 | 5K+ |
| Campaign | 5 | 25 | 250+ |
| Event | 20 | 100 | 1K+ |
| PollingBooth | 100 | 500 | 1K+ |
| Constituency | 5 | 25 | 250+ |
| State | 1 | 3 | 28 |

---

## Common Data Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| IntegrityError: UNIQUE constraint failed | Duplicate value in unique field | Check voter_id, booth_number, codes |
| NOT NULL constraint failed | Missing required field | Verify required FK references |
| FOREIGN KEY constraint failed | Invalid FK reference | Ensure parent record exists first |
| Decimal value exceeds precision | Wrong decimal places | Use decimal(10,2) for currency |
| Status value not in choices | Invalid status value | Use only defined choices |
| Invalid coordinate (lat/lng) | Out of range value | Latitude -90 to 90, Longitude -180 to 180 |

---

## Database Size Estimates

```
Empty Database: ~50 MB (schema only)
Small Dataset (1 constituency): ~100 MB
Medium Dataset (5 constituencies): ~500 MB
Large Dataset (50 constituencies): ~2-3 GB
Full India Coverage: ~15-20 GB
```

---

## Backup & Recovery

### Backup Commands
```bash
# PostgreSQL
pg_dump pulse_of_people > backup_2025_11_09.sql

# SQLite
cp db.sqlite3 db.sqlite3.backup

# With compression
pg_dump pulse_of_people | gzip > backup.sql.gz
```

### Restore Commands
```bash
# PostgreSQL
psql pulse_of_people < backup_2025_11_09.sql

# SQLite
cp db.sqlite3.backup db.sqlite3
```

---

## File Locations

- **Models**: `/backend/api/models.py` (1,439 lines)
- **Analytics Models**: `/backend/api/models_analytics.py` (394 lines)
- **Migrations**: `/backend/api/migrations/`
- **This Schema**: `/DATABASE_SCHEMA_ANALYSIS.md`
- **Data Guide**: `/SAMPLE_DATA_GENERATION_GUIDE.md`

---

## Contact & Support

For database-related issues:
1. Check migration history: `python manage.py showmigrations`
2. Validate constraints with SQL queries (see SAMPLE_DATA_GENERATION_GUIDE.md)
3. Review model definitions in models.py for field specifications
4. Check audit logs for user action tracking

---

**Last Updated**: 2025-11-09
**Schema Version**: 1.0
**Total Tables**: 50+ (38 custom + Django built-ins)
**Status**: Production-Ready with Full RBAC

