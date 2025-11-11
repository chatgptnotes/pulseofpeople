# Pulse of People - Sample Data Generation Guide

## Overview
This guide provides specifications for generating realistic, production-like sample data for the Pulse of People platform while respecting foreign key constraints and hierarchical relationships.

---

## 1. GEOGRAPHIC HIERARCHY SETUP

### 1.1 States (Start Here)
**Sample Data**: 5-10 major Indian states
```
State Examples:
- Tamil Nadu (TN) - region: South
- Maharashtra (MH) - region: West
- Uttar Pradesh (UP) - region: North
- Karnataka (KA) - region: South
- West Bengal (WB) - region: East

Constraints:
- code must be unique (2-3 char state abbreviation)
- name must be unique
- total_districts = count of related districts (denormalized)
- total_constituencies = count of related constituencies (denormalized)
```

**Recommended Volume**: 3-5 states for testing, 28 for full India

### 1.2 Districts (Per State)
**Hierarchical**: state_id is REQUIRED

```
Example structure for Tamil Nadu:
- Chennai District (code: TN-CH)
- Coimbatore District (code: TN-CO)
- Madurai District (code: TN-MA)
- Villupuram District (code: TN-VI)

Constraints:
- unique_together(state_id, name)
- unique code across all districts
- population can be realistic (1-5 million)
- area_sq_km should be reasonable (100-5000)
- total_wards = count of subdivisions
```

**Recommended Volume**: 3-4 districts per state (9-20 total)

### 1.3 Constituencies (Assembly & Parliamentary)
**Hierarchical**: state_id is REQUIRED, district_id is optional

```
Constituency Rules:
- Must have valid state_id (FK constraint)
- district_id can be NULL (for constituencies crossing districts)
- constituency_type: 'assembly' OR 'parliamentary'
- number: 1-294 for assembly, 1-543 for parliamentary
- reserved_for: 'general', 'sc', or 'st'
- total_voters: typically 500K-1M per assembly seat
- geojson_data: JSON polygon for Mapbox visualization
- center_lat, center_lng: decimal coordinates with 8 decimal places

Example:
{
  "state_id": 1 (Tamil Nadu),
  "constituency_type": "assembly",
  "name": "Chennai Central AC",
  "code": "TN-CC",
  "number": 23,
  "reserved_for": "general",
  "total_voters": 850000,
  "center_lat": 13.04939385,
  "center_lng": 80.27205555,
  "geojson_data": { "type": "Polygon", "coordinates": [[...]] }
}
```

**Recommended Volume**: 2-3 constituencies per district (6-12 total)

### 1.4 Polling Booths
**Hierarchical**: state_id, district_id, constituency_id ALL REQUIRED

```
Booth Naming Convention:
- booth_number: '001', '002A', '003', etc. (unique per constituency)
- name: School/Building name + location
- building_name: "XYZ Government School"
- area: Locality name (should match ward names in Voter table)

Voter Distribution Per Booth:
- total_voters: 500-1500 voters per booth
- male_voters: ~50% of total
- female_voters: ~48% of total
- other_voters: ~2% of total

Example:
{
  "state_id": 1,
  "district_id": 2,
  "constituency_id": 5,
  "booth_number": "001",
  "name": "Sri Ramakrishna School, Mylapore",
  "building_name": "Sri Ramakrishna School",
  "area": "Mylapore",
  "total_voters": 1200,
  "male_voters": 600,
  "female_voters": 576,
  "other_voters": 24,
  "latitude": 13.03445678,
  "longitude": 80.26789123,
  "is_active": true,
  "is_accessible": true
}
```

**Recommended Volume**: 10-20 booths per constituency (100-240 total)

---

## 2. VOTER DATABASE

### 2.1 Voter Demographics

**Voter ID Generation**:
- Format: "{state_code}-{district_code}-{sequence}"
- Example: "TN-CH-0000001"
- MUST be unique and indexed

**Name Generation**:
- Use realistic Tamil/Indian names from a seed database
- first_name: common Indian first names
- last_name: common surnames
- middle_name: optional (leave blank 20% of time)

**Age Distribution** (for 18+ voting population):
```
18-25: 20%
26-35: 22%
36-45: 20%
46-60: 22%
60+:   16%
```

**Gender Distribution**:
- male: 52%
- female: 46%
- other: 2%

**Contact Information**:
- phone: 10-digit Indian phone number (starting 9x)
- email: optional (30% have email)
- alternate_phone: 20% of voters have alternate contact

**Address Mapping**:
- ward: MUST match valid wards in the constituency
- address_line1, address_line2: realistic street names
- landmark: nearby identifiable feature
- pincode: valid Indian postcode for the area
- latitude, longitude: random within booth's coordinates ±0.01

### 2.2 Political Data

**Party Affiliation Distribution** (realistic for Tamil Nadu):
```
TVK: 25%
DMK: 20%
AIADMK: 18%
BJP: 12%
Congress: 8%
Neutral: 10%
Unknown: 7%
```

**Sentiment Breakdown** (per party affiliation):
```
TVK supporters sentiment:
  - strong_supporter: 35%
  - supporter: 40%
  - neutral: 15%
  - opposition: 7%
  - strong_opposition: 3%

AIADMK supporters:
  - strong_supporter: 30%
  - supporter: 38%
  - neutral: 18%
  - opposition: 9%
  - strong_opposition: 5%

[Similar distributions for other parties]
```

**Influence Level**:
- high: 5% (opinion leaders, community figures)
- medium: 25% (active in community)
- low: 70% (typical voters)

**Engagement History**:
- contact_frequency: 0-10 (Poisson distribution, mean=2)
- last_contacted_at: within past 90 days (recent engagement)
- interaction_count: correlate with contact_frequency
- positive_interactions: 60-80% of total interactions
- negative_interactions: 20-40% of interactions
- preferred_communication: distribution:
  - phone: 40%
  - whatsapp: 35%
  - door_to_door: 15%
  - sms: 7%
  - email: 3%

### 2.3 Voter Tags
```
Example tags (JSON array):
["frequent_voter", "opinion_leader", "youth_engagement"]
["low_engagement", "needs_follow_up"]
["event_attendee", "donor"]

Tag Guidelines:
- 0-5 tags per voter
- Use consistent tag names
- Keep for segmentation purposes
```

### 2.4 Voter Volume Recommendations

For testing:
- Small: 1,000 voters (1 constituency)
- Medium: 10,000 voters (3 constituencies)
- Large: 100,000+ voters (10+ constituencies)

For full platform testing:
- 1-2 million voters across all constituencies

---

## 3. VOTER INTERACTIONS

### 3.1 Interaction Generation Rules

**Per Active Voter**: 0-10 interactions in past 90 days

**Distribution by Type**:
- phone_call: 40%
- door_visit: 30%
- event_meeting: 15%
- whatsapp: 10%
- sms: 3%
- email: 2%

**Sentiment Per Interaction**:
- positive: 70% (convince, satisfied)
- neutral: 20% (information sharing)
- negative: 10% (disagreement, complaint)

**Follow-up Logic**:
- If sentiment is negative: 60% require follow-up
- If sentiment is neutral: 20% require follow-up
- If sentiment is positive: 5% require follow-up
- follow_up_date: typically 5-14 days after interaction

**Duration**:
- phone_call: 5-20 minutes (normal: 10)
- door_visit: 10-45 minutes (normal: 20)
- event_meeting: 30-120 minutes (normal: 60)
- other: NULL

### 3.2 Issues Discussed (JSON)
```
Examples:
["water_supply", "road_maintenance"]
["education", "healthcare"]
["unemployment", "farmer_support"]

Map to IssueCategory table for consistency
```

### 3.3 Database Considerations
- Create index on (voter_id, -interaction_date) for quick retrieval
- Bulk insert for large volumes to improve performance
- Spread interactions across past 90 days

---

## 4. FEEDBACK & FIELD REPORTS

### 4.1 Direct Feedback Volume

**Per Constituency**:
- Active feedback: 50-200 per month
- Peak periods: before elections (2-3x increase)

**Status Distribution** (current state):
```
pending: 30%
analyzing: 15%
analyzed: 20%
reviewed: 25%
escalated: 7%
resolved: 3%
```

**Sentiment Scores** (normalized 0-1):
```
Positive feedback (polarity='positive'):
  - ai_sentiment_score: 0.6-1.0 (mean: 0.78)
  - ai_confidence: 0.75-0.95 (mean: 0.85)

Negative feedback (polarity='negative'):
  - ai_sentiment_score: 0.0-0.4 (mean: 0.22)
  - ai_confidence: 0.75-0.95 (mean: 0.85)

Neutral feedback (polarity='neutral'):
  - ai_sentiment_score: 0.4-0.6 (mean: 0.50)
  - ai_confidence: 0.60-0.85 (mean: 0.73)
```

**Urgency Assignment**:
```
Based on issue type and sentiment:
- Critical issues (water, healthcare): 30% urgent
- Infrastructure issues: 20% high
- Social issues: 10% high
- General feedback: 5% high
```

### 4.2 Field Reports Volume

**Per Booth Agent**: 2-5 reports per week

**Report Type Distribution**:
- daily_summary: 50%
- event_feedback: 25%
- issue_report: 15%
- competitor_activity: 7%
- booth_report: 3%

**Verification Status**:
- pending: 15% (recent reports)
- verified: 75% (trusted agents)
- disputed: 10% (needs review)

**Media Attachments**:
- 40% of reports have 1-3 media URLs
- Real image URLs from Supabase storage
- Realistic crowd sizes: 50-5000 people

---

## 5. SENTIMENT DATA AGGREGATION

### 5.1 Sentiment Score Computation

**Formula** (simplified):
```
sentiment_score = (0.4 * ai_sentiment) + 
                  (0.3 * sentiment_from_interactions) + 
                  (0.3 * sentiment_from_reports)
```

**Confidence** (quality metric):
```
confidence = min(ai_confidence, 0.95)
If multiple sources: confidence *= 1.05 (capped at 0.95)
```

### 5.2 Daily Aggregation Rules

**DailySentimentStats**:
- Group by: date, state, district, constituency, issue
- Calculate:
  - avg_sentiment_score
  - sentiment_velocity (today vs yesterday trend)
  - Count by polarity (positive|negative|neutral)
  - Source breakdown (feedback, field_reports, social, surveys)

**Example Computation**:
```python
date = '2025-11-09'
constituency_id = 5
issue_id = 3

# Aggregate all sentiment data for this combination
positive_count = SentimentData.objects.filter(
    timestamp__date=date,
    constituency_id=constituency_id,
    issue_id=issue_id,
    polarity='positive'
).count()

avg_sentiment = SentimentData.objects.filter(
    timestamp__date=date,
    constituency_id=constituency_id,
    issue_id=issue_id
).aggregate(Avg('sentiment_score'))

sentiment_velocity = (
    today_avg_sentiment - 
    yesterday_avg_sentiment
) / yesterday_avg_sentiment
```

---

## 6. CAMPAIGNS & EVENTS

### 6.1 Campaign Volume

**Per Constituency**: 2-4 campaigns per year

**Campaign Budget** (INR):
- Small awareness: 100K - 500K
- Medium campaign: 500K - 2M
- Large election campaign: 2M - 10M+

**Budget Allocation**:
```
spent_amount should be 60-95% of budget
Remaining held as contingency
```

**Status Progression**:
```
planning → active → completed (typical)
planning → cancelled (5% of campaigns)
Can also be: active → completed, active → cancelled
```

### 6.2 Event Volume

**Per Campaign**: 5-20 events

**Event Type Distribution**:
```
rally: 30% (large, high-attendance)
meeting: 35% (medium, targeted)
door_to_door: 20% (ongoing)
booth_visit: 10%
town_hall: 5%
```

**Attendance Metrics**:
- expected_attendance: 50-5000 (by type)
- actual_attendance: 60-90% of expected
- Boost for major events: rally, town_hall

**Status Distribution**:
```
planned: 40% (future events)
ongoing: 10%
completed: 45%
cancelled: 5%
```

### 6.3 Social Media Posts

**Per Campaign**: 10-50 posts

**Platform Distribution**:
```
Facebook: 35%
Twitter/X: 30%
WhatsApp: 20%
Instagram: 10%
YouTube: 5%
```

**Engagement Metrics** (realistic ranges):
```
For Facebook (avg 1000 followers):
  - reach: 500-2000
  - impressions: 800-3000
  - likes: 20-200
  - shares: 5-50
  - comments: 5-30

For Twitter (avg 500 followers):
  - reach: 300-1000
  - impressions: 400-1500
  - likes: 10-100
  - shares: 3-20
  - comments: 5-20

Sentiment score: correlate with engagement ratio
```

---

## 7. ADMINISTRATIVE STRUCTURES

### 7.1 Issue Categories

**Hierarchical Structure** (parent-child):
```
Root Issues:
├── Infrastructure
│   ├── Water Supply
│   ├── Roads & Transportation
│   ├── Public Facilities
│   └── Drainage

├── Social Welfare
│   ├── Education
│   ├── Healthcare
│   ├── Senior Citizens
│   └── Women's Safety

├── Economic
│   ├── Employment
│   ├── Business Support
│   └── Agriculture

├── Safety & Security
│   ├── Police Response
│   ├── Crime Prevention
│   └── Traffic Safety

├── Environment
│   ├── Pollution Control
│   ├── Green Spaces
│   └── Waste Management
```

**Priority Levels**:
- High priority: 5-10 (water, healthcare, safety)
- Medium: 2-5 (infrastructure, social)
- Low: 0-2 (general suggestions)

### 7.2 Voter Segments

**Recommended Segments** (for Tamil Nadu):
```
1. Fishermen (population: 500K, priority: high)
2. Farmers (population: 2M, priority: high)
3. Small Traders (population: 1.5M, priority: medium)
4. Students & Youth (population: 3M, priority: high)
5. Senior Citizens (population: 800K, priority: medium)
6. Women Entrepreneurs (population: 300K, priority: medium)
7. Daily Wage Laborers (population: 1.5M, priority: high)
8. Business Community (population: 500K, priority: medium)
9. IT Professionals (population: 400K, priority: low)
10. Homemakers (population: 2M, priority: medium)
```

**Key Issues Per Segment**:
- Fishermen: fishing rights, fuel prices, weather warnings
- Farmers: irrigation, crop prices, fertilizer subsidy
- Youth: employment, education, recreation
- etc.

### 7.3 Political Parties

**Include Major Parties**:
```
TVK (target party) - status: state
DMK - status: state
AIADMK - status: state
BJP - status: national
Congress - status: national
ADMK - status: state
Smaller regional parties
```

---

## 8. ANALYTICS AGGREGATION

### 8.1 Daily Stats Computation

**DailyVoterStats**:
- Run daily (preferably off-peak)
- Aggregate Voter records for each (date, state, district, constituency)
- Calculate sentiment distribution
- Calculate age group distribution
- Store for quick dashboard queries

**DailyInteractionStats**:
- Aggregate VoterInteraction records
- Count by interaction_type
- Calculate response_rate = conversions / total_contacts
- Identify top volunteers

**DailySentimentStats**:
- Aggregate SentimentData records
- Group by issue
- Calculate velocity (trend)
- Track source breakdown

### 8.2 Weekly/Monthly Aggregations

**WeeklyCampaignStats**:
- Aggregate Campaign and Event data
- Calculate total reach, ROI, engagement
- Run every Monday morning

---

## 9. DATA GENERATION BEST PRACTICES

### 9.1 Referential Integrity

```python
# GOOD: Create with valid foreign keys
state = State.objects.create(name="Tamil Nadu", code="TN")
district = District.objects.create(
    state=state,  # FK constraint satisfied
    name="Chennai",
    code="TN-CH"
)

# BAD: Will raise IntegrityError
district = District.objects.create(
    state_id=99999,  # Non-existent state
    name="Chennai"
)
```

### 9.2 Batch Operations

```python
# GOOD: Bulk create for performance
booths = [PollingBooth(...) for i in range(1000)]
PollingBooth.objects.bulk_create(booths, batch_size=500)

# BAD: Creates N database roundtrips
for booth_data in booth_list:
    PollingBooth.objects.create(**booth_data)
```

### 9.3 Temporal Realism

```python
# Spread data across reasonable time windows
from datetime import timedelta
from django.utils import timezone

base_date = timezone.now() - timedelta(days=90)
for i in range(1000):
    voter_interaction = VoterInteraction(
        voter=voter,
        interaction_date=base_date + timedelta(
            days=random.randint(0, 90)
        ),
        ...
    )
```

### 9.4 Consistency Checks

Before finalizing data:
```
- Verify all FK references exist
- Check denormalized counts (total_voters, total_constituencies)
- Validate sentiment scores are 0.0-1.0
- Ensure geographic coordinates are valid
- Check for unique constraint violations (especially codes)
- Verify status values match choices
```

---

## 10. SQL QUERIES FOR VALIDATION

### Quick Validation Queries

```sql
-- Count records by table
SELECT 'Voters' as table_name, COUNT(*) as count FROM api_voter
UNION ALL
SELECT 'Interactions', COUNT(*) FROM api_voterinteraction
UNION ALL
SELECT 'Feedback', COUNT(*) FROM api_directfeedback
UNION ALL
SELECT 'Field Reports', COUNT(*) FROM api_fieldreport
UNION ALL
SELECT 'Polling Booths', COUNT(*) FROM api_pollingbooth
UNION ALL
SELECT 'Constituencies', COUNT(*) FROM api_constituency
ORDER BY count DESC;

-- Check FK integrity
SELECT COUNT(*) as orphaned_voters 
FROM api_voter v
WHERE v.constituency_id IS NOT NULL 
  AND NOT EXISTS (
    SELECT 1 FROM api_constituency c 
    WHERE c.id = v.constituency_id
  );

-- Verify sentiment scores are normalized
SELECT COUNT(*) as invalid_scores
FROM api_sentimentdata
WHERE sentiment_score < 0.0 OR sentiment_score > 1.0;

-- Check geographic consistency
SELECT COUNT(*) FROM api_pollingbooth
WHERE state_id IS NULL OR district_id IS NULL OR constituency_id IS NULL;
```

---

## 11. SAMPLE GENERATION SCRIPTS

### 11.1 Mini Dataset (1 Constituency)

```
- 1 State
- 1 District  
- 1 Constituency
- 20 Polling Booths
- 10,000 Voters
- 1,000 Voter Interactions
- 500 Direct Feedback submissions
- 100 Field Reports
- 5 Campaigns
- 20 Events
- 50 Social Media Posts
```

**Time to Generate**: ~5-10 minutes
**Database Size**: ~100 MB

### 11.2 Standard Dataset (5 Constituencies)

```
- 2-3 States
- 5-7 Districts
- 5 Constituencies
- 100 Polling Booths
- 50,000 Voters
- 5,000 Voter Interactions
- 2,500 Direct Feedback
- 500 Field Reports
- 25 Campaigns
- 100 Events
- 250 Social Posts
```

**Time to Generate**: ~30-60 minutes
**Database Size**: ~500 MB

### 11.3 Large Dataset (50 Constituencies)

```
- 10-15 States
- 50-70 Districts
- 50 Constituencies
- 1,000 Polling Booths
- 500,000 Voters
- 50,000 Voter Interactions
- 25,000 Direct Feedback
- 5,000 Field Reports
- 250 Campaigns
- 1,000 Events
- 2,500 Social Posts
```

**Time to Generate**: ~2-4 hours
**Database Size**: ~2-3 GB

---

## 12. CHECKLIST FOR REALISTIC DATA

Before declaring data generation complete:

- [ ] All geographic hierarchy constraints satisfied
- [ ] No orphaned foreign key references
- [ ] Sentiment scores all in 0.0-1.0 range
- [ ] Dates and times spread realistically over time periods
- [ ] Party affiliation ratios match target state demographics
- [ ] Voter sentiment distribution reasonable per party
- [ ] Engagement metrics follow realistic distributions
- [ ] Denormalized counts updated (total_voters, total_constituencies, etc.)
- [ ] Unique constraints verified (voter_id, constituency codes, etc.)
- [ ] Analytics aggregation tables populated correctly
- [ ] No unintended NULL values in required fields
- [ ] All image/file URLs valid or placeholder
- [ ] Tags and JSON fields properly formatted
- [ ] Audit logs created for historical records
- [ ] Multiple organization support if using multi-tenant feature

