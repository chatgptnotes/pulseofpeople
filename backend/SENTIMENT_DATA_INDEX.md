# Sentiment Data Generator - File Index

## Overview

This document provides an index of all files related to the sentiment data generator for the Pulse of People platform.

**Created Date**: November 9, 2024
**Total Records Generated**: 50,000 (configurable)
**Data Period**: September 1 - November 30, 2024
**Based On**: Real Tamil Nadu crisis scenarios

---

## Files Created

### 1. Main Command File
**Location**: `/Users/murali/Applications/pulseofpeople/backend/api/management/commands/generate_sentiment_data.py`
**Size**: 19 KB
**Purpose**: Django management command to generate 50,000 realistic sentiment data records

**Key Features**:
- Generates data based on REAL Tamil Nadu crisis scenarios
- Supports configurable record count and batch size
- Uses numpy for statistical distributions (beta, normal, exponential)
- Progress tracking with tqdm
- Bulk creation in batches for performance
- Comprehensive statistics output

**Usage**:
```bash
python manage.py generate_sentiment_data
python manage.py generate_sentiment_data --count 100000
python manage.py generate_sentiment_data --batch-size 2000
```

---

### 2. Comprehensive Documentation
**Location**: `/Users/murali/Applications/pulseofpeople/backend/SENTIMENT_DATA_GENERATOR.md`
**Size**: 12 KB
**Purpose**: Full documentation of the sentiment data generator

**Contents**:
- Overview and usage instructions
- Prerequisites and requirements
- Real crisis scenarios simulated
- Data generation logic explained
- Time, geographic, and source distributions
- Sentiment scoring algorithms
- Output statistics format
- Technical implementation details
- Performance optimizations
- Troubleshooting guide
- Integration points
- Example output

---

### 3. Crisis Scenarios Reference
**Location**: `/Users/murali/Applications/pulseofpeople/backend/CRISIS_SCENARIOS_2024.md`
**Size**: 11 KB
**Purpose**: Detailed documentation of real Tamil Nadu crisis scenarios from November 2024

**Contents**:
- 10 major crisis scenarios with full details
- Geographic distribution maps
- Sentiment patterns (visual bars)
- Data volume percentages
- Key issues for each crisis
- Timeline of events (Sept-Nov 2024)
- Heat map of affected districts
- Overall sentiment trends
- Crisis severity index
- Data sources and references

**Crisis Scenarios**:
1. Water Crisis (20% of data)
2. Jobs & Unemployment (18%)
3. Agriculture & Farmers (12%)
4. NEET Opposition (10%)
5. Cauvery Water Dispute (8%)
6. Healthcare Access (8%)
7. Education (7%)
8. Fishermen Rights (5%)
9. Infrastructure (5%)
10. Cyclone Fengal (4%)

---

### 4. Testing Guide
**Location**: `/Users/murali/Applications/pulseofpeople/backend/TEST_SENTIMENT_DATA.md`
**Size**: 14 KB
**Purpose**: Step-by-step testing and verification guide

**Contents**:
- Quick verification steps
- Django shell verification commands
- Data quality checks
- Time distribution verification
- Geographic pattern validation
- Performance benchmarks
- Full dataset test procedure
- Verification checklist
- Common issues and solutions
- SQL verification queries
- CSV export instructions

**Verification Areas**:
- Record count validation
- Polarity distribution
- Source distribution
- Date range verification
- District coverage
- Null value checks
- Score range validation
- Polarity mapping correctness
- Time patterns
- Geographic patterns
- Query performance

---

### 5. Quick Reference
**Location**: `/Users/murali/Applications/pulseofpeople/backend/api/management/commands/README_SENTIMENT_DATA.md`
**Size**: 4.6 KB
**Purpose**: Quick reference guide for developers

**Contents**:
- Quick start commands
- Command options table
- Crisis scenarios summary table
- Data distribution tables
- Sentiment scoring table
- Prerequisites
- Expected output statistics
- Performance metrics
- Troubleshooting table
- Real-world context
- Integration points
- Testing tips
- Next steps

---

## Quick Start

### 1. Prerequisites
```bash
# Ensure required data exists
python manage.py seed_political_data

# Verify dependencies
pip install numpy tqdm
```

### 2. Generate Data
```bash
# Navigate to backend
cd /Users/murali/Applications/pulseofpeople/backend
source venv/bin/activate

# Generate 50,000 records (default)
python manage.py generate_sentiment_data

# OR custom count
python manage.py generate_sentiment_data --count 25000
```

### 3. Verify Data
```bash
# Quick verification
python manage.py shell
>>> from api.models import SentimentData
>>> SentimentData.objects.count()
50000
>>> exit()
```

---

## File Relationships

```
SENTIMENT_DATA_INDEX.md (this file)
├── api/management/commands/generate_sentiment_data.py (main command)
│   ├── Uses: numpy, tqdm, Django ORM
│   └── Creates: 50,000 SentimentData records
│
├── SENTIMENT_DATA_GENERATOR.md (comprehensive docs)
│   ├── References: generate_sentiment_data.py
│   └── Explains: All features, logic, usage
│
├── CRISIS_SCENARIOS_2024.md (crisis details)
│   ├── Source: Real TN issues (Nov 2024)
│   └── Used by: generate_sentiment_data.py
│
├── TEST_SENTIMENT_DATA.md (testing guide)
│   ├── Tests: generate_sentiment_data.py output
│   └── Validates: Data quality, distributions
│
└── api/management/commands/README_SENTIMENT_DATA.md (quick ref)
    ├── Quick version of: SENTIMENT_DATA_GENERATOR.md
    └── For: Developer reference
```

---

## Data Flow

```
1. User runs command:
   python manage.py generate_sentiment_data

2. Command verifies database:
   - Tamil Nadu state exists
   - 38 districts exist
   - Issue categories exist
   - Constituencies exist

3. Command loads data structures:
   - All districts
   - All constituencies
   - All issues
   - All voter segments

4. Command defines crisis scenarios:
   - Water crisis → Coimbatore, Chennai, etc.
   - Cauvery dispute → Thanjavur, Tiruvarur, etc.
   - Cyclone → Cuddalore, Viluppuram, etc.
   - And 7 more scenarios

5. For each of 50,000 records:
   a. Select issue by distribution (20% water, 18% jobs, etc.)
   b. Select district based on issue (water → Coimbatore, etc.)
   c. Select constituency within district
   d. Generate sentiment score using beta distribution
   e. Generate confidence using normal distribution
   f. Select source (40% direct, 35% social, etc.)
   g. Generate timestamp with realistic patterns
   h. Create SentimentData object

6. Bulk create in batches of 1000

7. Display comprehensive statistics:
   - Total records
   - Date range
   - Issue breakdown
   - Polarity breakdown
   - Source breakdown
   - Top districts
   - Geographic coverage
```

---

## Key Statistics (Expected)

### For 50,000 Records:

**Generation Time**: 30-45 seconds
**Storage Size**: 15-20 MB
**Processing Speed**: 1,000-1,500 records/second

**Distributions**:
- Negative sentiment: ~37.5% (18,750)
- Neutral sentiment: ~32.3% (16,125)
- Positive sentiment: ~30.3% (15,125)

**Geographic Coverage**:
- All 38 Tamil Nadu districts
- Urban districts: ~50% of data
- Semi-urban: ~30% of data
- Rural: ~20% of data

**Top Districts**:
1. Chennai: ~16.5%
2. Coimbatore: ~14.2%
3. Madurai: ~10.0%
4. Tiruchirappalli: ~6.9%
5. Salem: ~6.0%

---

## Technical Details

### Technologies Used
- **Python**: 3.10+
- **Django**: 5.2
- **NumPy**: 2.3.4+ (statistical distributions)
- **tqdm**: Progress tracking
- **PostgreSQL/SQLite**: Database

### Statistical Methods
- **Beta Distribution**: Sentiment score generation
- **Normal Distribution**: Confidence scores
- **Exponential Distribution**: Timestamp generation (favoring recent)
- **Weighted Random**: District selection, hour selection

### Performance Optimizations
- Bulk creation (1000 records per batch)
- Pre-loaded data structures
- Single transaction per batch
- Database index usage
- Lazy evaluation

---

## Integration Examples

### 1. Sentiment Dashboard
```python
from api.models import SentimentData
from django.db.models import Count, Avg

# Get sentiment by district
sentiment_by_district = SentimentData.objects.values(
    'district__name'
).annotate(
    avg_sentiment=Avg('sentiment_score'),
    count=Count('id')
).order_by('-count')
```

### 2. Time Series Analysis
```python
from django.db.models.functions import TruncDate

# Daily sentiment trend
daily_trend = SentimentData.objects.annotate(
    date=TruncDate('timestamp')
).values('date').annotate(
    avg_sentiment=Avg('sentiment_score'),
    count=Count('id')
).order_by('date')
```

### 3. Issue Prioritization
```python
# Issues by volume and negative sentiment
issue_priority = SentimentData.objects.filter(
    polarity='negative'
).values('issue__name').annotate(
    count=Count('id')
).order_by('-count')
```

### 4. Geographic Heatmap
```python
# District-level sentiment for Mapbox
district_sentiment = SentimentData.objects.values(
    'district__name',
    'district__code'
).annotate(
    avg_sentiment=Avg('sentiment_score'),
    negative_count=Count('id', filter=Q(polarity='negative')),
    total_count=Count('id')
).order_by('district__name')
```

---

## Next Steps After Generation

1. **Verify Data**: Run tests from `TEST_SENTIMENT_DATA.md`
2. **Run Analytics**: `python manage.py aggregate_analytics`
3. **Test Dashboard**: Load frontend and check visualizations
4. **Test Filtering**: Filter by date, district, issue, polarity
5. **Test Maps**: Verify geographic visualization on Mapbox
6. **Export Reports**: Generate CSV/PDF reports
7. **Performance Test**: Query performance with 50K records
8. **Scale Test**: Try with 100K or 250K records

---

## Maintenance

### Adding New Crisis Scenarios

Edit `generate_sentiment_data.py`:

```python
# In define_crisis_scenarios() method
self.issue_distribution = {
    'Water Supply': 20.0,
    'Jobs/Employment': 18.0,
    'New Crisis': 5.0,  # Add new crisis
    # Adjust others to total 100%
}

self.issue_district_map = {
    'New Crisis': ['District1', 'District2'],  # Affected districts
}

self.issue_sentiment_patterns = {
    'New Crisis': {'positive': 20, 'neutral': 30, 'negative': 50},
}
```

### Updating Time Period

```python
# In generate_sentiment_data() method
end_date = datetime(2025, 2, 28)    # Update end date
start_date = datetime(2024, 12, 1)   # Update start date
```

### Adding New Sources

```python
# In define_crisis_scenarios() method
self.source_distribution = {
    'direct_feedback': 40.0,
    'social_media': 35.0,
    'field_report': 20.0,
    'new_source': 5.0,  # Add new source
}
```

---

## Support

**For Issues**:
1. Check `TEST_SENTIMENT_DATA.md` troubleshooting section
2. Review `SENTIMENT_DATA_GENERATOR.md` for detailed explanations
3. Verify prerequisites are met
4. Check Django logs for errors

**For Questions**:
- Review `CRISIS_SCENARIOS_2024.md` for data context
- Check `README_SENTIMENT_DATA.md` for quick answers
- Test with small dataset first (--count 1000)

---

## Version History

**v1.0** (2024-11-09)
- Initial release
- 50,000 record generation
- 10 real crisis scenarios
- 38 districts coverage
- Sept-Nov 2024 time period
- Statistical distributions
- Comprehensive documentation

---

**Index Version**: 1.0
**Last Updated**: 2024-11-09
**Status**: Production Ready
**Maintainer**: Pulse of People Development Team
