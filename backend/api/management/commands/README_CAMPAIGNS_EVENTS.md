# Campaign and Event Data Generation Guide

This guide explains how to use the management commands to generate realistic TVK campaigns and events data.

## Overview

Two management commands are available:

1. **`generate_campaigns`** - Generates 30 realistic TVK campaigns across 4 types
2. **`generate_events`** - Generates 150 realistic events across 4 types

## Prerequisites

Before running these commands, ensure you have:

1. ✅ **Master data loaded** (States, Districts, Constituencies)
   ```bash
   python manage.py generate_master_data
   ```

2. ✅ **Users created** (Managers, Analysts, Volunteers)
   ```bash
   python manage.py generate_users --count=100
   ```

## Command 1: Generate Campaigns

### Basic Usage

```bash
# Generate 30 campaigns
python manage.py generate_campaigns

# Clear existing campaigns and generate fresh
python manage.py generate_campaigns --clear
```

### What It Creates

**30 Campaigns distributed as:**

1. **Election Campaigns (35% - 10-11 campaigns)**
   - Large-scale assembly/parliamentary campaigns
   - Budget: ₹50L - ₹5Cr
   - Duration: 3-6 months
   - Examples:
     - 2026 Assembly Election - Chennai Region
     - Parliamentary Constituency Campaign - Central Chennai
     - By-Election Preparedness - Delta Districts

2. **Awareness Campaigns (30% - 9 campaigns)**
   - Statewide awareness drives
   - Budget: ₹10L - ₹50L
   - Duration: 1-3 months
   - Examples:
     - TVK Vision 2026 - Statewide Awareness
     - Corruption-Free Tamil Nadu Campaign
     - Youth Empowerment Initiative

3. **Issue-based Campaigns (25% - 7-8 campaigns)**
   - Focused on specific issues
   - Budget: ₹5L - ₹30L
   - Duration: 2-6 months
   - Examples:
     - Save TN Water - Community Mobilization
     - NEET Opposition - Students United
     - Fisher Community Rights Campaign

4. **Door-to-Door Campaigns (10% - 3 campaigns)**
   - Ward/booth-level canvassing
   - Budget: ₹2L - ₹15L
   - Duration: 1-2 months
   - Examples:
     - Ward-wise Voter Connect - Phase 1
     - Booth Saturation - Chennai Metro

### Campaign Status Distribution

- **Active**: 40% (12 campaigns) - Currently running
- **Planning**: 30% (9 campaigns) - Being planned
- **Completed**: 25% (7-8 campaigns) - Finished
- **Cancelled**: 5% (1-2 campaigns) - Cancelled

### Campaign Attributes

Each campaign includes:

- ✅ Campaign name and type
- ✅ Start/end dates (past 6 months to future 6 months)
- ✅ Budget and spent amounts (realistic based on status)
- ✅ Target constituency linkage
- ✅ Campaign manager assignment
- ✅ Team members (5-20 per campaign)
- ✅ Campaign goals (JSON):
  ```json
  {
    "voter_contacts": 50000,
    "events_planned": 20,
    "volunteers_mobilized": 200,
    "social_media_reach": 1000000,
    "booth_coverage": "80%"
  }
  ```
- ✅ Progress metrics (JSON):
  ```json
  {
    "voters_contacted": 35000,
    "events_completed": 15,
    "volunteers_active": 180,
    "social_media_impressions": 850000,
    "booths_covered": 65
  }
  ```

### Budget Tracking

Spending percentage by status:

- **Completed**: 85%-100% of budget spent
- **Active**: 30%-70% spent
- **Planning**: 0%-10% spent
- **Cancelled**: 10%-30% spent

### Output Statistics

After running, you'll see:

```
======================================================================
CAMPAIGN GENERATION STATISTICS
======================================================================

Total Campaigns Created: 30

Campaigns by Type:
  Election            : 11 ( 36.7%)
  Awareness           :  9 ( 30.0%)
  Issue Based         :  7 ( 23.3%)
  Door To Door        :  3 ( 10.0%)

Campaigns by Status:
  Planning            :  9 ( 30.0%)
  Active              : 12 ( 40.0%)
  Completed           :  8 ( 26.7%)
  Cancelled           :  1 (  3.3%)

Budget Summary:
  Total Budget Allocated: ₹458,500,000.00
  Total Amount Spent:     ₹198,235,750.00
  Overall Spent:          43.2%

  Average Campaign Budget: ₹15,283,333.33
======================================================================
```

---

## Command 2: Generate Events

### Basic Usage

```bash
# Generate 150 events
python manage.py generate_events

# Clear existing events and generate fresh
python manage.py generate_events --clear
```

### What It Creates

**150 Events distributed as:**

1. **Rallies (20% - 30 events)**
   - Large public gatherings
   - Expected attendance: 5,000-50,000
   - Budget: ₹2L-₹20L
   - Timing: 10am-1pm or 5pm-8pm (weekends)
   - Examples:
     - TVK Mega Rally - Marina Beach, Chennai
     - Youth Employment Rally - Coimbatore RS Puram
     - Farmers Rights Rally - Thanjavur

2. **Meetings (40% - 60 events)**
   - Town halls, community meetings
   - Expected attendance: 200-2,000
   - Budget: ₹20K-₹2L
   - Timing: 6pm-9pm (after work hours)
   - Examples:
     - Town Hall - Water Crisis Solutions - T Nagar
     - Youth Connect Meeting - Anna University
     - Fisher Community Dialogue - Ramanathapuram

3. **Door-to-Door (30% - 45 events)**
   - Ward-level canvassing
   - Expected attendance: 50-500 (households)
   - Budget: ₹5K-₹50K
   - Timing: 4pm-7pm
   - Examples:
     - Ward-15 Door Canvassing - Mylapore
     - Booth Coverage Drive - Adyar Zone

4. **Booth Visits (10% - 15 events)**
   - Booth monitoring/training
   - Expected attendance: 10-100
   - Budget: ₹2K-₹20K
   - Examples:
     - Booth Monitoring - Booth #042 T Nagar
     - Booth Agent Training - Multiple Booths

### Event Status Distribution

- **Completed**: 50% (75 events) - Past events
- **Ongoing**: 10% (15 events) - Happening now
- **Planned**: 35% (52-53 events) - Future events
- **Cancelled**: 5% (7-8 events) - Cancelled

### Temporal Distribution

- **Historical** (Last 3 months): 40%
- **Recent** (Last 2 weeks): 30%
- **Upcoming** (Next 3 months): 30%

### Event Attributes

Each event includes:

- ✅ Event name and type
- ✅ Start/end datetime (realistic timings)
- ✅ Location with GPS coordinates
- ✅ Ward and constituency linkage
- ✅ Expected and actual attendance
- ✅ Budget and expenses
- ✅ Organizer assignment
- ✅ Volunteer assignments (5-50 per event)
- ✅ Campaign linkage (70% linked)
- ✅ Realistic after-event notes
- ✅ Event photos (3-10 URLs for completed events)

### Attendance Tracking

- **Completed events**: 80%-120% of expected
- **Ongoing events**: 60%-90% of expected
- **Planned events**: 0 (not yet occurred)

### Budget Tracking

- **Completed events**: 90%-105% of budget spent
- **Ongoing events**: 40%-60% spent
- **Planned events**: 0%-20% spent (advance booking)

### Realistic Notes Examples

**Rally Notes:**
> "Very successful rally. Crowd response excellent. Key talking points: jobs, water, education. Media coverage good. Over 20 local reporters present."

**Meeting Notes:**
> "Town hall productive. 25 questions from audience, mostly about NEET and unemployment. Follow-up needed with student groups. Good engagement."

**Door-to-Door Notes:**
> "Door campaign covered 150 households. 60% positive response. Major concerns: water supply, sanitation."

**Booth Visit Notes:**
> "Booth inspection completed. Agent training satisfactory. Voter list verification 80% done. Need more volunteers for booth coverage."

### Output Statistics

After running, you'll see:

```
======================================================================
EVENT GENERATION STATISTICS
======================================================================

Total Events Created: 150

Events by Type:
  Rally               :  30 ( 20.0%)
  Meeting             :  60 ( 40.0%)
  Door To Door        :  45 ( 30.0%)
  Booth Visit         :  15 ( 10.0%)

Events by Status:
  Planned             :  53 ( 35.3%)
  Ongoing             :  15 ( 10.0%)
  Completed           :  75 ( 50.0%)
  Cancelled           :   7 (  4.7%)

Campaign Linkage:
  Events linked to campaigns: 105 (70.0%)

Attendance Summary:
  Total Expected Attendance:  328,450
  Total Actual Attendance:    185,230
  Achievement Rate:           56.4%

Budget Summary:
  Total Budget Allocated: ₹15,850,000.00
  Total Expenses:         ₹8,925,500.00
  Budget Utilization:     56.3%

  Average Event Budget:      ₹105,666.67
  Average Expected Attendance: 2,190
======================================================================
```

---

## Complete Workflow

### Step-by-step Data Generation

```bash
# 1. Generate master data (states, districts, constituencies)
python manage.py generate_master_data

# 2. Generate users (managers, analysts, volunteers)
python manage.py generate_users --count=100

# 3. Generate campaigns
python manage.py generate_campaigns

# 4. Generate events
python manage.py generate_events

# 5. (Optional) Generate voters
python manage.py generate_voters --count=1000

# 6. (Optional) Generate voter interactions
python manage.py generate_voter_interactions --count=500
```

### Verify Data

```bash
# Check campaigns
python manage.py shell
>>> from api.models import Campaign
>>> Campaign.objects.count()
30
>>> Campaign.objects.filter(status='active').count()
12

# Check events
>>> from api.models import Event
>>> Event.objects.count()
150
>>> Event.objects.filter(status='completed').count()
75
```

---

## Geographic Distribution

### Events by Region

- **Urban centers** (Chennai, Coimbatore, Madurai): 50%
- **District headquarters**: 30%
- **Rural areas**: 20%

### Specific Locations Used

**Chennai Areas:**
- Marina Beach, T Nagar, Mylapore, Adyar, Velachery
- Anna Nagar, Anna University, Kodambakkam

**Coimbatore:**
- RS Puram, Gandhipuram, Saibaba Colony, Peelamedu

**Other Districts:**
- Madurai, Trichy, Thanjavur, Salem, Vellore, Erode
- Tirunelveli, Ramanathapuram, Kanyakumari

---

## Data Relationships

### Campaign-Event Linkage

- 70% of events are linked to campaigns
- Events support campaign goals and metrics
- Campaign metrics updated based on event outcomes

### Team Assignments

**Campaigns:**
- Campaign manager: Manager/Analyst role
- Team members: 5-20 Users/Volunteers

**Events:**
- Organizer: Manager/Analyst role
- Volunteers: 5-50 based on event type

### Constituency Mapping

- All campaigns linked to target constituencies
- All events linked to constituencies
- Geographic data includes coordinates

---

## Tips & Best Practices

### 1. Run in Sequence

Always generate campaigns before events:
```bash
python manage.py generate_campaigns
python manage.py generate_events
```

### 2. Clear and Regenerate

To start fresh:
```bash
python manage.py generate_campaigns --clear
python manage.py generate_events --clear
```

### 3. Check Prerequisites

Verify master data exists:
```bash
python manage.py shell
>>> from api.models import Constituency, User
>>> Constituency.objects.count()  # Should be > 0
>>> User.objects.filter(profile__role='manager').count()  # Should be > 0
```

### 4. Monitor Performance

For large datasets, use database transactions (already implemented).

### 5. Customize as Needed

Edit the command files to:
- Adjust campaign/event counts
- Modify budget ranges
- Change temporal distributions
- Add more event types

---

## Troubleshooting

### Issue: "No constituencies found"

**Solution:**
```bash
python manage.py generate_master_data
```

### Issue: "No managers/analysts found"

**Solution:**
```bash
python manage.py generate_users --count=50
```

### Issue: "No campaigns found" (for events)

**Solution:**
```bash
python manage.py generate_campaigns
```

### Issue: Events not linking to campaigns

**Cause:** Campaign data missing or insufficient

**Solution:**
1. Verify campaigns exist
2. Re-run with `--clear` flag

---

## Database Schema

### Campaign Model Fields

```python
- campaign_name: CharField (200)
- campaign_type: election/awareness/issue_based/door_to_door
- start_date: DateField
- end_date: DateField
- status: planning/active/completed/cancelled
- budget: DecimalField (12, 2)
- spent_amount: DecimalField (12, 2)
- target_constituency: ForeignKey(Constituency)
- campaign_manager: ForeignKey(User)
- team_members: ManyToManyField(User)
- goals: JSONField
- metrics: JSONField
```

### Event Model Fields

```python
- event_name: CharField (200)
- event_type: rally/meeting/door_to_door/booth_visit/town_hall
- start_datetime: DateTimeField
- end_datetime: DateTimeField
- location: CharField (300)
- constituency: ForeignKey(Constituency)
- latitude/longitude: DecimalField
- expected_attendance: IntegerField
- actual_attendance: IntegerField
- organizer: ForeignKey(User)
- volunteers: ManyToManyField(User)
- campaign: ForeignKey(Campaign, nullable)
- budget: DecimalField (10, 2)
- expenses: DecimalField (10, 2)
- status: planned/ongoing/completed/cancelled
- notes: TextField
- photos: JSONField (list of URLs)
```

---

## Examples & Use Cases

### Example 1: Generate Full Dataset

```bash
# Complete setup
python manage.py generate_master_data
python manage.py generate_users --count=200
python manage.py generate_campaigns
python manage.py generate_events
```

### Example 2: Refresh Campaigns Only

```bash
python manage.py generate_campaigns --clear
```

### Example 3: Add More Events

```bash
# Modify generate_events.py event_distribution
# Then run
python manage.py generate_events --clear
```

### Example 4: Query Generated Data

```python
from api.models import Campaign, Event
from django.db.models import Sum, Count

# Campaign statistics
Campaign.objects.aggregate(
    total_budget=Sum('budget'),
    total_spent=Sum('spent_amount'),
    count=Count('id')
)

# Event statistics by type
Event.objects.values('event_type').annotate(
    count=Count('id'),
    total_attendance=Sum('actual_attendance')
)

# Active campaigns with events
Campaign.objects.filter(
    status='active'
).prefetch_related('events').annotate(
    event_count=Count('events')
)
```

---

## Performance Metrics

### Generation Time

- **Campaigns**: ~2-5 seconds (30 campaigns)
- **Events**: ~5-10 seconds (150 events)
- **Total**: ~10-15 seconds for both

### Database Operations

- Uses `bulk_create()` for efficiency
- Transaction management for data integrity
- Many-to-many relationships set post-creation

### Memory Usage

- Minimal memory footprint
- Data generated in batches
- No large file processing

---

## Support & Customization

For customization, edit:

1. **Campaign templates**: `_get_campaign_templates()` method
2. **Event names**: Rally/meeting/door-to-door name lists
3. **Budget ranges**: Adjust in template definitions
4. **Temporal distribution**: Modify `_get_event_timing()`
5. **Notes templates**: Update note generation methods

---

**Last Updated:** 2025-11-09
**Version:** 1.0
**Compatibility:** Django 5.2, PostgreSQL/SQLite
