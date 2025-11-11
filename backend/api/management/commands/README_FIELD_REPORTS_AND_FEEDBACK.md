# Field Reports & Direct Feedback Generation Commands

This document describes two Django management commands that generate realistic test data for the Pulse of People platform.

## Overview

- **`generate_field_reports.py`**: Creates 3,000 field reports from volunteers/booth agents
- **`generate_direct_feedback.py`**: Creates 5,000 direct citizen feedback submissions

Both commands generate realistic Tamil Nadu political sentiment data following TVK party patterns.

---

## Command 1: Generate Field Reports

### Purpose
Generate realistic field reports from party volunteers and booth agents covering various activities like daily summaries, event feedback, issue reports, competitor activity, and booth assessments.

### Usage

```bash
# Generate default 3,000 field reports
python manage.py generate_field_reports

# Generate custom number of reports
python manage.py generate_field_reports --count 5000
```

### Parameters

- `--count`: Number of field reports to generate (default: 3000)

### Data Distribution

#### 1. Report Types (Total: 3,000)

| Report Type | Count | Percentage | Description |
|-------------|-------|------------|-------------|
| daily_summary | 1,500 | 50% | Daily field visit summaries |
| event_feedback | 750 | 25% | Rally/meeting feedback |
| issue_report | 450 | 15% | Urgent issues from ground |
| competitor_activity | 150 | 5% | Opposition party activities |
| booth_report | 150 | 5% | Booth-level assessments |

#### 2. Verification Status

| Status | Percentage | Description |
|--------|------------|-------------|
| verified | 70% | Verified by supervisors |
| pending | 25% | Awaiting verification |
| disputed | 5% | Needs re-verification |

#### 3. Geographic Distribution

- **Urban areas** (Chennai, Coimbatore, Madurai): 45%
- **Semi-urban**: 35%
- **Rural**: 20%
- Covers all active constituencies in Tamil Nadu

#### 4. Time Distribution

- **Date Range**: Last 60 days
- **Volume**: More recent dates have higher volume
- **Peak Hours**: 6-8 PM (after field work)
- **Pattern**: Weekdays > Weekends

#### 5. Content Patterns

**Daily Summary Examples:**
- "Ward-15 field visit completed. Met 45 families, mostly positive response to TVK vision. Water supply remains top concern."
- "Booth-042 coverage: 60% households contacted. Youth showing strong interest in employment programs."

**Event Feedback Examples:**
- "TVK rally in T Nagar: Estimated 5,000+ attendance. Crowd very enthusiastic. Key topics: jobs, water, corruption-free governance."
- "Town hall meeting successful. 200+ participants asked about healthcare, education access. Very positive sentiment."

**Issue Reports Examples:**
- "URGENT: Water crisis worsening in Ward-23. Residents without supply for 3 days. Immediate attention needed."
- "Multiple families in Adyar report job loss due to factory closure. Economic distress high."

**Competitor Activity Examples:**
- "DMK organized small rally in Anna Nagar. ~200 attendees. Focus on government schemes."
- "AIADMK booth setup observed in Velachery. Distributing pamphlets about freebies."

#### 6. Linked Data

Each report includes:
- 1-3 issue categories (water, jobs, NEET, healthcare, etc.)
- Voter segments met (fishermen, farmers, youth, students)
- Crowd size for events (50-10,000, realistic distribution)
- Positive/negative reactions as JSON lists
- Geographic tags (ward, constituency, district)

### Output Statistics

The command provides comprehensive statistics:

```
=== FIELD REPORTS GENERATION STATISTICS ===
daily_summary: 1500 (50.0%)
event_feedback: 750 (25.0%)
issue_report: 450 (15.0%)
competitor_activity: 150 (5.0%)
booth_report: 150 (5.0%)

Verification Status:
verified: 2100 (70.0%)
pending: 750 (25.0%)
disputed: 150 (5.0%)

Date Range: 2024-09-10 to 2024-11-09

Top 5 Reporters:
  volunteer_user_123: 45 reports
  booth_agent_456: 38 reports
  ...

Total Field Reports: 3000
```

---

## Command 2: Generate Direct Feedback

### Purpose
Generate realistic direct citizen feedback submissions with AI sentiment analysis, representing real Tamil Nadu citizen concerns.

### Usage

```bash
# Generate default 5,000 feedback submissions
python manage.py generate_direct_feedback

# Generate custom number
python manage.py generate_direct_feedback --count 10000
```

### Parameters

- `--count`: Number of feedback submissions to generate (default: 5000)

### Data Distribution

#### 1. Issue Distribution (Total: 5,000)

| Issue | Count | Percentage | Key Concerns |
|-------|-------|------------|--------------|
| Water Supply | 1,100 | 22% | No supply, tanker costs, groundwater depletion |
| Jobs/Employment | 900 | 18% | Unemployment, low wages, factory closures |
| Agriculture/Farmers | 600 | 12% | Irrigation, input costs, MSP, debt |
| NEET Opposition | 500 | 10% | Medical admissions, rural student access |
| Healthcare | 450 | 9% | Doctor shortage, hospital infrastructure |
| Education | 400 | 8% | School infrastructure, teacher shortage, fees |
| Fishermen Rights | 300 | 6% | SL Navy arrests, livelihood protection |
| Cauvery Water | 250 | 5% | Interstate dispute, agriculture impact |
| Others | 500 | 10% | Infrastructure, electricity, roads, garbage |

#### 2. Status Distribution

| Status | Percentage | Description |
|--------|------------|-------------|
| analyzed | 60% | AI processing completed |
| reviewed | 20% | Human verified |
| pending | 15% | Awaiting analysis |
| escalated | 5% | Critical issues flagged |

#### 3. Demographics

**Age Distribution:**
- Range: 18-75 years
- Peak: 25-45 years (working age population)
- Average: ~35 years

**Gender Distribution:**
- Male: 60%
- Female: 35%
- Other: 5%

**Contact Details:**
- Phone: 100% (Indian format: +91XXXXXXXXXX)
- Email: 30% (younger demographic more likely)

**Geographic Spread:**
- All 42 Tamil Nadu districts covered
- Urban/Rural: 55% urban, 45% rural
- Issue-district correlation (e.g., water → Coimbatore, fishermen → coastal)

#### 4. Time Distribution

- **Date Range**: Last 90 days (Sept-Nov 2024)
- **Volume Pattern**:
  - 40% in last 15 days
  - 30% in 16-45 days
  - 30% in 46-90 days
- **Event Spikes**: After protests, natural disasters, policy announcements

#### 5. Message Templates

**Water Crisis:**
```
"No water supply for 5 days in our Ward-12 area. Tanker water very expensive
at Rs.1200 per load. Children missing school to fetch water from far away.
How will we survive summer?"

Expected Action: "Immediate restoration of regular water supply. Permanent
solution for water crisis."
```

**Jobs:**
```
"Engineering graduate, 3 years searching for job. Only call center offers
with Rs.15000 salary. Need good manufacturing jobs in Tamil Nadu."

Expected Action: "Government should create quality jobs with decent salary
and job security."
```

**NEET:**
```
"My daughter scored 95% in 12th but couldn't clear NEET. Dreams of becoming
doctor shattered. Please remove NEET for TN."

Expected Action: "Abolish NEET and restore state board based medical admissions."
```

**Fishermen:**
```
"My husband arrested by SL Navy 3rd time this year. Family starving. We just
want to fish in our waters."

Expected Action: "Protect Indian fishermen from SL Navy and secure our fishing
rights."
```

#### 6. AI Analysis Fields

Each feedback includes realistic AI-generated analysis:

**Sentiment Score** (0.0-1.0):
- Crisis issues (water, jobs, agriculture): 0.10-0.35 (highly negative)
- NEET: 0.15-0.40 (negative)
- Other issues: 0.20-0.50 (negative to neutral)

**Polarity:**
- Positive: ~5%
- Negative: ~80%
- Neutral: ~15%

**Urgency:**
- Low: 5%
- Medium: 15%
- High: 60%
- Urgent: 20%

**Confidence:** 0.70-0.95 (AI confidence in analysis)

**Extracted Issues:** JSON array
```json
["Water shortage", "Tanker water costs", "Irregular supply"]
```

**AI Summary:** Concise 1-2 sentence summary
```
"Citizen reporting severe water crisis affecting daily life. Issue requires
immediate administrative attention."
```

**Metadata:**
```json
{
  "model": "sentiment-analyzer-v2.1",
  "processing_time_ms": 450,
  "language_detected": "en",
  "keywords": ["water", "crisis", "urgent", "family", "children"]
}
```

### Output Statistics

```
=== DIRECT FEEDBACK GENERATION STATISTICS ===

Feedback by Status:
analyzed: 3000 (60.0%)
reviewed: 1000 (20.0%)
pending: 750 (15.0%)
escalated: 250 (5.0%)

Sentiment Polarity:
negative: 4000 (80.0%)
neutral: 750 (15.0%)
positive: 250 (5.0%)

Urgency Levels:
urgent: 1000 (20.0%)
high: 3000 (60.0%)
medium: 750 (15.0%)
low: 250 (5.0%)

Date Range: 2024-08-10 to 2024-11-09

Top 5 Districts:
  Chennai: 1200 submissions
  Coimbatore: 850 submissions
  Madurai: 620 submissions
  Salem: 480 submissions
  Tiruchirappalli: 390 submissions

Average Citizen Age: 35.2 years

Total Direct Feedback: 5000
```

---

## Prerequisites

### 1. Database Setup

Ensure these models have seed data:

```bash
# Run in this order
python manage.py generate_master_data  # States, districts, constituencies
python manage.py seed_political_data   # Issue categories, voter segments, parties
python manage.py generate_users        # Volunteers and booth agents
```

### 2. Required Models

Both commands need these models populated:
- `State` (Tamil Nadu)
- `District` (42 districts)
- `Constituency` (Assembly constituencies)
- `IssueCategory` (Water, Jobs, NEET, etc.)
- `VoterSegment` (Fishermen, Farmers, Youth, etc.)
- `User` (Volunteers/booth agents with 'volunteer' or 'user' role)
- `PoliticalParty` (DMK, AIADMK, BJP, etc.)

### 3. Database Performance

These commands use bulk insertion for performance:

- Batch size: 500 records per transaction
- Progress updates every 500 records
- Total time: ~30 seconds for 3,000 reports, ~45 seconds for 5,000 feedback

---

## Data Quality Features

### 1. Realistic Patterns

✅ **Geographic Correlation:**
- Water issues concentrated in Coimbatore, Chennai
- Fishermen issues in coastal districts (Ramanathapuram, Tuticorin)
- Agriculture issues in delta regions (Thanjavur, Nagapattinam)

✅ **Temporal Patterns:**
- More recent data has higher volume
- Event-driven spikes (after rallies, protests)
- Field reports peak 6-8 PM (after field work)
- Feedback submission peaks during daytime

✅ **Demographic Realism:**
- Tamil names (using Faker en_IN locale)
- Age distribution matches voting population
- Gender representation realistic
- Phone numbers in Indian format

✅ **Content Authenticity:**
- Based on real Tamil Nadu issues
- Citizen voice and language patterns
- Realistic monetary amounts (tanker water, salaries, costs)
- Specific locations and ward numbers

### 2. AI Analysis Realism

✅ **Sentiment Mapping:**
- Crisis issues → Low sentiment scores
- Urgent issues → High urgency flags
- Negative polarity dominates (80%)
- Confidence varies realistically (70-95%)

✅ **Issue Extraction:**
- Keywords extracted from message
- Multiple issues tagged (1-3 per feedback)
- Voter segment correlation
- Summary generation follows pattern

### 3. Verification Workflows

✅ **Field Reports:**
- 70% verified by supervisors
- Verification notes added
- Disputed reports flagged with reasons
- Timestamp tracking (reported → verified → reviewed)

✅ **Direct Feedback:**
- 60% AI analyzed
- 20% human reviewed
- 5% escalated for urgent action
- Analysis timestamps maintained

---

## Usage Examples

### Complete Data Generation Flow

```bash
# Step 1: Generate master geographic data
python manage.py generate_master_data

# Step 2: Seed political data (issues, segments, parties)
python manage.py seed_political_data

# Step 3: Create users (volunteers, booth agents)
python manage.py generate_users --count 500

# Step 4: Generate field reports
python manage.py generate_field_reports --count 3000

# Step 5: Generate direct feedback
python manage.py generate_direct_feedback --count 5000

# Step 6: (Optional) Generate sentiment aggregates
python manage.py generate_sentiment_data
```

### Verify Generated Data

```bash
# Check field reports
python manage.py shell
>>> from api.models import FieldReport
>>> FieldReport.objects.count()
3000
>>> FieldReport.objects.filter(report_type='daily_summary').count()
1500
>>> FieldReport.objects.filter(verification_status='verified').count()
2100

# Check direct feedback
>>> from api.models import DirectFeedback
>>> DirectFeedback.objects.count()
5000
>>> DirectFeedback.objects.filter(status='analyzed').count()
3000
>>> DirectFeedback.objects.filter(ai_sentiment_polarity='negative').count()
4000
```

### Query Examples

```python
# Find urgent water crisis feedback
urgent_water = DirectFeedback.objects.filter(
    issue_category__name__icontains='Water',
    ai_urgency='urgent',
    status='pending'
)

# Get unverified field reports from last 7 days
from django.utils import timezone
from datetime import timedelta

recent_unverified = FieldReport.objects.filter(
    timestamp__gte=timezone.now() - timedelta(days=7),
    verification_status='pending'
)

# Top issues by constituency
from django.db.models import Count

issue_by_constituency = DirectFeedback.objects.values(
    'constituency__name', 'issue_category__name'
).annotate(
    count=Count('id')
).order_by('-count')[:20]
```

---

## Troubleshooting

### Issue: "No volunteers found"

**Solution:**
```bash
python manage.py generate_users --count 500
```

### Issue: "Tamil Nadu state not found"

**Solution:**
```bash
python manage.py generate_master_data
```

### Issue: "No issue categories found"

**Solution:**
```bash
python manage.py seed_political_data
```

### Issue: Slow performance

**Optimization:**
- Commands use bulk_create (500 records/batch)
- Many-to-many relations added after bulk insert
- Transactions prevent partial data
- Indexes on foreign keys improve queries

### Issue: Duplicate data on re-run

**Behavior:**
- Commands use `ignore_conflicts=True` in bulk_create
- Re-running is safe but may create duplicates
- Use `FieldReport.objects.all().delete()` to clean first

---

## Database Impact

### Storage Requirements

| Model | Records | Avg Size | Total Size |
|-------|---------|----------|------------|
| FieldReport | 3,000 | ~2 KB | ~6 MB |
| DirectFeedback | 5,000 | ~3 KB | ~15 MB |
| **Total** | **8,000** | - | **~21 MB** |

### Index Coverage

Both models have optimized indexes:

**FieldReport:**
- `volunteer`, `timestamp`
- `ward`, `booth_number`
- `constituency`, `district`
- `verification_status`, `report_type`

**DirectFeedback:**
- `status`, `submitted_at`
- `constituency`, `district`, `ward`
- `issue_category`, `voter_segment`
- `ai_urgency`, `ai_sentiment_polarity`

---

## Integration with Frontend

### API Endpoints (Expected)

```
GET /api/field-reports/
GET /api/field-reports/{id}/
GET /api/field-reports/stats/

GET /api/direct-feedback/
GET /api/direct-feedback/{id}/
GET /api/direct-feedback/stats/
GET /api/direct-feedback/urgent/
```

### Dashboard Visualizations

Use this data for:
1. **Issue Heatmaps**: Geographic distribution of issues
2. **Sentiment Trends**: Time-series sentiment analysis
3. **Urgency Dashboard**: Critical issues requiring action
4. **Volunteer Activity**: Reporter leaderboards and metrics
5. **Verification Queue**: Pending verification workflow
6. **Escalation Alerts**: Urgent feedback notifications

---

## Data Maintenance

### Cleanup Commands

```bash
# Delete all field reports
python manage.py shell -c "from api.models import FieldReport; FieldReport.objects.all().delete()"

# Delete all direct feedback
python manage.py shell -c "from api.models import DirectFeedback; DirectFeedback.objects.all().delete()"

# Delete unverified reports older than 30 days
python manage.py shell -c "from api.models import FieldReport; from django.utils import timezone; from datetime import timedelta; FieldReport.objects.filter(verification_status='pending', timestamp__lt=timezone.now()-timedelta(days=30)).delete()"
```

### Backup Before Generation

```bash
# Export existing data
python manage.py dumpdata api.FieldReport api.DirectFeedback > backup_reports_feedback.json

# Restore if needed
python manage.py loaddata backup_reports_feedback.json
```

---

## License & Attribution

- **Author**: Pulse of People Platform Team
- **Purpose**: Test data generation for TVK political sentiment analysis
- **Data**: Fictional but realistic Tamil Nadu citizen feedback patterns
- **Privacy**: All names, phone numbers, and locations are randomly generated

---

## Support

For issues or questions:
1. Check prerequisites are met
2. Review error messages in console output
3. Verify database migrations are applied
4. Check Django logs for detailed errors

**Generated with**: Django Management Commands
**Version**: 1.0
**Last Updated**: 2024-11-09
