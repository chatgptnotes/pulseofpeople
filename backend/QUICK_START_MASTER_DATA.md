# Quick Start: Master Data Generation

## TL;DR

```bash
# 1. Navigate to backend
cd /Users/murali/Applications/pulseofpeople/backend

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run migrations (if not done)
python manage.py migrate

# 4. Generate ALL master data
python manage.py generate_master_data

# 5. (Optional) Clear and regenerate
python manage.py generate_master_data --clear
```

## What You Get

✅ **2 States**: Tamil Nadu, Puducherry
✅ **42 Districts**: All 38 TN + 4 Puducherry districts with population data
✅ **234 Constituencies**: Real Tamil Nadu assembly constituencies
✅ **10,000+ Polling Booths**: Realistic booth locations with GPS coordinates
✅ **10 Political Parties**: TVK, DMK, AIADMK, BJP, INC, PMK, MDMK, DMDK, CPI(M), NTK
✅ **25 Issue Categories**: Jobs, Water, NEET, Healthcare, Education, etc. with TVK stance
✅ **50 Voter Segments**: Youth, Farmers, Fishermen, IT Workers, Students, etc.
✅ **1 Organization**: TVK with enterprise subscription

## Execution Time

⏱️ **2-5 minutes** for complete dataset (~10,000 records)

## When to Run

🚀 **First Time Setup**: After initial database migration
🔄 **After Schema Changes**: When models are updated
🧪 **Before Testing**: To populate test database
📊 **Before Demos**: To show realistic data

## Verification

```bash
# Check record counts
python manage.py shell

>>> from api.models import *
>>> State.objects.count()        # Should be 2
>>> District.objects.count()     # Should be 42
>>> Constituency.objects.count() # Should be 234
>>> PollingBooth.objects.count() # Should be ~10,000
>>> IssueCategory.objects.count() # Should be 25
>>> VoterSegment.objects.count()  # Should be 50
>>> PoliticalParty.objects.count() # Should be 10
>>> Organization.objects.count()   # Should be 1
```

## Common Use Cases

### Fresh Development Setup
```bash
python manage.py migrate
python manage.py generate_master_data
python manage.py createsuperadmin
python manage.py seed_voters
```

### Reset Everything
```bash
python manage.py generate_master_data --clear
python manage.py createsuperadmin
```

### Production Initial Load
```bash
python manage.py migrate
python manage.py generate_master_data
# DO NOT use --clear in production!
```

## Sample Data Highlights

### Real Constituency Names
- Chennai: Gummidipoondi, Ponneri, Tiruvottiyur, Anna Nagar, T. Nagar, Mylapore
- Coimbatore: Sulur, Kavundampalayam, Coimbatore North/South, Singanallur
- Madurai: Melur, Madurai East/West/North/South, Thiruparankundram

### Critical Issues with TVK Stance
1. **Jobs & Employment** - Strongly Supportive (Priority 10)
2. **Water Supply** - Strongly Supportive (Priority 10)
3. **NEET Opposition** - Strongly Against (Priority 9)
4. **Cauvery Dispute** - Strongly Supportive of TN Rights (Priority 9)

### Top Voter Segments
1. **First-time Voters** - 3M voters (Priority 10)
2. **Youth (18-25)** - 8M voters (Priority 10)
3. **Farmers** - 10M voters (Priority 9)
4. **Women** - 35M voters (Priority 9)
5. **Fishermen** - 500K voters (Priority 9)

## Data Relationships

```
State (TN/PY)
  └── Districts (42)
       └── Constituencies (234)
            └── Polling Booths (10,000+)
                 └── Voters (to be added separately)

Organization (TVK)
  └── Users
       └── Assigned to: State/District/Constituency/Booth

Issue Categories (25) ←→ Voter Segments (50)
  └── Direct Feedback
  └── Field Reports
  └── Sentiment Data
```

## Next Steps After Generation

1. **Create Users**:
   ```bash
   python manage.py createsuperadmin
   ```

2. **Seed Additional Data**:
   ```bash
   python manage.py seed_voters
   python manage.py seed_campaigns
   python manage.py seed_events
   ```

3. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```

4. **Access Admin Panel**:
   http://127.0.0.1:8000/admin

## Troubleshooting

| Error | Solution |
|-------|----------|
| Command not found | Activate virtual environment: `source venv/bin/activate` |
| ModuleNotFoundError: faker | Install faker: `pip install faker` |
| Database locked | Stop Django server, then retry |
| Transaction error | Check database connection in settings.py |

## Documentation

📖 **Full Documentation**: `backend/api/management/commands/README_GENERATE_MASTER_DATA.md`
📋 **Project Guide**: `CLAUDE.md`
🔧 **Model Reference**: `backend/api/models.py`

## Support

💬 Questions? Check the full README or ask in project chat.
🐛 Found a bug? Report in GitHub issues.
✨ Feature request? Add to backlog.

---

**Last Updated**: 2025-11-09
**Version**: 1.0
**Command Location**: `/backend/api/management/commands/generate_master_data.py`
