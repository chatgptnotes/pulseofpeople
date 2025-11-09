# Quick Start: Campaigns & Events Data Generation

## TL;DR - Just Run These

```bash
# 1. Activate virtual environment
cd /Users/murali/Applications/pulseofpeople/backend
source venv/bin/activate

# 2. Generate campaigns (30 campaigns)
python manage.py generate_campaigns

# 3. Generate events (150 events)
python manage.py generate_events
```

## What You Get

### Campaigns (30 total)

| Type | Count | Budget Range | Examples |
|------|-------|--------------|----------|
| Election | 11 (35%) | ₹50L - ₹5Cr | 2026 Assembly Election - Chennai |
| Awareness | 9 (30%) | ₹10L - ₹50L | TVK Vision 2026, Youth Empowerment |
| Issue-based | 7 (25%) | ₹5L - ₹30L | NEET Opposition, Water Rights |
| Door-to-door | 3 (10%) | ₹2L - ₹15L | Ward-wise Voter Connect |

**Status:** 40% Active, 30% Planning, 25% Completed, 5% Cancelled

### Events (150 total)

| Type | Count | Attendance | Budget | Timing |
|------|-------|------------|--------|--------|
| Rallies | 30 (20%) | 5K-50K | ₹2L-₹20L | 10am-1pm, 5pm-8pm |
| Meetings | 60 (40%) | 200-2K | ₹20K-₹2L | 6pm-9pm |
| Door-to-door | 45 (30%) | 50-500 | ₹5K-₹50K | 4pm-7pm |
| Booth Visits | 15 (10%) | 10-100 | ₹2K-₹20K | Anytime |

**Status:** 50% Completed, 35% Planned, 10% Ongoing, 5% Cancelled

## Prerequisites Check

```bash
# Check constituencies exist
python manage.py shell -c "from api.models import Constituency; print(f'{Constituency.objects.count()} constituencies')"

# Check users exist
python manage.py shell -c "from api.models import User; print(f'{User.objects.filter(profile__role=\"manager\").count()} managers')"
```

**If zero:** Run these first:
```bash
python manage.py generate_master_data
python manage.py generate_users --count=100
```

## Command Options

### Generate Campaigns

```bash
# Generate 30 campaigns
python manage.py generate_campaigns

# Clear existing and regenerate
python manage.py generate_campaigns --clear
```

### Generate Events

```bash
# Generate 150 events
python manage.py generate_events

# Clear existing and regenerate
python manage.py generate_events --clear
```

## Key Features

### Campaigns Include:

- Campaign name, type, dates
- Budget allocated & spent (realistic %)
- Campaign manager + team (5-20 members)
- Target constituency
- Goals JSON (voter contacts, events, volunteers, reach)
- Metrics JSON (actual progress tracking)

### Events Include:

- Event name, type, date/time
- Location with GPS coordinates
- Expected & actual attendance
- Budget & expenses
- Organizer + volunteers (5-50)
- Campaign linkage (70%)
- Realistic after-event notes
- Photo URLs (completed events)

## Geographic Coverage

**Chennai:** Marina Beach, T Nagar, Mylapore, Adyar, Anna Nagar
**Coimbatore:** RS Puram, Gandhipuram, Saibaba Colony
**Other:** Madurai, Trichy, Thanjavur, Salem, Vellore, Erode

## Verification

```bash
# Count campaigns
python manage.py shell -c "from api.models import Campaign; print(Campaign.objects.count())"

# Count events
python manage.py shell -c "from api.models import Event; print(Event.objects.count())"

# Active campaigns
python manage.py shell -c "from api.models import Campaign; print(f'{Campaign.objects.filter(status=\"active\").count()} active')"

# Completed events
python manage.py shell -c "from api.models import Event; print(f'{Event.objects.filter(status=\"completed\").count()} completed')"
```

## Typical Output

### Campaigns
```
Total Campaigns Created: 30
Election: 11 (36.7%)
Awareness: 9 (30.0%)
Issue Based: 7 (23.3%)
Door To Door: 3 (10.0%)

Total Budget: ₹458,500,000
Total Spent: ₹198,235,750 (43.2%)
```

### Events
```
Total Events Created: 150
Rally: 30 (20.0%)
Meeting: 60 (40.0%)
Door To Door: 45 (30.0%)
Booth Visit: 15 (10.0%)

Expected Attendance: 328,450
Actual Attendance: 185,230 (56.4%)

Total Budget: ₹15,850,000
Total Expenses: ₹8,925,500 (56.3%)
```

## Common Issues

**"No constituencies found"**
→ `python manage.py generate_master_data`

**"No managers found"**
→ `python manage.py generate_users --count=100`

**"No campaigns found" (for events)**
→ `python manage.py generate_campaigns`

## Full Data Pipeline

```bash
# 1. Master data
python manage.py generate_master_data

# 2. Users
python manage.py generate_users --count=100

# 3. Campaigns
python manage.py generate_campaigns

# 4. Events
python manage.py generate_events

# 5. Voters (optional)
python manage.py generate_voters --count=1000

# 6. Interactions (optional)
python manage.py generate_voter_interactions --count=500
```

## Time Estimate

- Master data: ~5 seconds
- Users (100): ~10 seconds
- Campaigns (30): ~5 seconds
- Events (150): ~10 seconds
- **Total: ~30 seconds**

## Notes

- Events are 70% linked to campaigns
- Realistic Tamil Nadu locations with GPS
- Budget tracking based on status
- Team assignments automatic
- Notes/photos for completed events
- Temporal distribution: past/present/future

---

**Need more details?** See `README_CAMPAIGNS_EVENTS.md`

**Version:** 1.0 | **Updated:** 2025-11-09
