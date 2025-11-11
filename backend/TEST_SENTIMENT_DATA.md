# Testing Guide: Sentiment Data Generator

## Quick Verification Steps

### Step 1: Run with Small Dataset

```bash
cd /Users/murali/Applications/pulseofpeople/backend
source venv/bin/activate

# Generate 1,000 records for testing
python manage.py generate_sentiment_data --count 1000
```

**Expected output:**
```
================================================================================
SENTIMENT DATA GENERATOR - Tamil Nadu Real Crisis Scenarios (Nov 2024)
================================================================================

Verifying database...
  States (TN): 1
  Districts: 38
  Constituencies: 234
  Issue Categories: 9
  Voter Segments: 9
  Database verified!

Loading data structures...
  Data loaded!

Generating sentiment data records...
100%|███████████████████████████| 1000/1000 [00:01<00:00, 892.45record/s]

================================================================================
GENERATION COMPLETE
================================================================================

Total Records Created: 1,000
...
```

### Step 2: Verify Data in Django Shell

```bash
python manage.py shell
```

```python
from api.models import SentimentData, IssueCategory, District
from django.db.models import Count, Avg

# 1. Count total records
total = SentimentData.objects.count()
print(f"Total records: {total}")
# Expected: 1000

# 2. Check polarity distribution
polarity_dist = SentimentData.objects.values('polarity').annotate(count=Count('id'))
for item in polarity_dist:
    print(f"{item['polarity']}: {item['count']} ({item['count']/total*100:.1f}%)")
# Expected: Negative ~37%, Neutral ~32%, Positive ~31%

# 3. Check source distribution
source_dist = SentimentData.objects.values('source_type').annotate(count=Count('id'))
for item in source_dist:
    print(f"{item['source_type']}: {item['count']} ({item['count']/total*100:.1f}%)")
# Expected: direct_feedback ~40%, social_media ~35%, field_report ~20%, survey ~5%

# 4. Check date range
from django.db.models import Min, Max
date_range = SentimentData.objects.aggregate(
    min_date=Min('timestamp'),
    max_date=Max('timestamp')
)
print(f"Date range: {date_range['min_date']} to {date_range['max_date']}")
# Expected: Between Sept 1, 2024 and Nov 30, 2024

# 5. Check top districts
top_districts = SentimentData.objects.values('district__name').annotate(
    count=Count('id')
).order_by('-count')[:5]
for item in top_districts:
    print(f"{item['district__name']}: {item['count']}")
# Expected: Chennai, Coimbatore, Madurai at top

# 6. Check sentiment scores
avg_sentiment = SentimentData.objects.aggregate(
    avg_score=Avg('sentiment_score'),
    avg_confidence=Avg('confidence')
)
print(f"Avg sentiment score: {avg_sentiment['avg_score']:.2f}")
print(f"Avg confidence: {avg_sentiment['avg_confidence']:.2f}")
# Expected: avg_score ~0.45-0.55, avg_confidence ~0.75

# 7. Check issue distribution
issue_dist = SentimentData.objects.values('issue__name').annotate(
    count=Count('id')
).order_by('-count')
for item in issue_dist:
    print(f"{item['issue__name']}: {item['count']} ({item['count']/total*100:.1f}%)")
# Expected: Varies by mapping, but should show all major issues

# 8. Verify sentiment patterns for Water Supply
water_issue = IssueCategory.objects.filter(name__icontains='Healthcare').first()
if water_issue:
    water_sentiment = SentimentData.objects.filter(issue=water_issue).values('polarity').annotate(count=Count('id'))
    water_total = SentimentData.objects.filter(issue=water_issue).count()
    print(f"\nWater/Healthcare Sentiment:")
    for item in water_sentiment:
        print(f"  {item['polarity']}: {item['count']} ({item['count']/water_total*100:.1f}%)")
# Expected: More negative sentiment for water-related issues

# 9. Check geographic coverage
districts_covered = SentimentData.objects.values('district').distinct().count()
total_districts = District.objects.filter(state__code='TN').count()
print(f"\nDistricts covered: {districts_covered} / {total_districts}")
# Expected: Most or all 38 districts

# 10. Check ward distribution
ward_sample = SentimentData.objects.values('ward').distinct()[:10]
print(f"\nSample wards:")
for item in ward_sample:
    print(f"  {item['ward']}")
# Expected: Ward 1, Ward 23, Division 45, Zone 12, etc.
```

### Step 3: Verify Data Quality

```python
# Check for null values
null_checks = {
    'source_type': SentimentData.objects.filter(source_type__isnull=True).count(),
    'source_id': SentimentData.objects.filter(source_id__isnull=True).count(),
    'issue': SentimentData.objects.filter(issue__isnull=True).count(),
    'sentiment_score': SentimentData.objects.filter(sentiment_score__isnull=True).count(),
    'polarity': SentimentData.objects.filter(polarity__isnull=True).count(),
    'confidence': SentimentData.objects.filter(confidence__isnull=True).count(),
    'state': SentimentData.objects.filter(state__isnull=True).count(),
    'district': SentimentData.objects.filter(district__isnull=True).count(),
    'timestamp': SentimentData.objects.filter(timestamp__isnull=True).count(),
}

print("Null value check:")
for field, count in null_checks.items():
    status = "✓ OK" if count == 0 else f"✗ FAIL ({count} nulls)"
    print(f"  {field}: {status}")
# Expected: All should be OK (0 nulls) except voter_segment and constituency (allowed nulls)

# Check sentiment score ranges
invalid_scores = SentimentData.objects.filter(
    sentiment_score__lt=0
) | SentimentData.objects.filter(
    sentiment_score__gt=1
).count()
print(f"\nInvalid sentiment scores (< 0 or > 1): {invalid_scores}")
# Expected: 0

# Check confidence score ranges
invalid_confidence = SentimentData.objects.filter(
    confidence__lt=0
) | SentimentData.objects.filter(
    confidence__gt=1
).count()
print(f"Invalid confidence scores (< 0 or > 1): {invalid_confidence}")
# Expected: 0

# Check polarity mapping correctness
print("\nPolarity mapping check:")
negative_wrong = SentimentData.objects.filter(
    polarity='negative',
    sentiment_score__gte=0.4
).count()
neutral_wrong = SentimentData.objects.filter(
    polarity='neutral'
).exclude(
    sentiment_score__gte=0.4,
    sentiment_score__lte=0.6
).count()
positive_wrong = SentimentData.objects.filter(
    polarity='positive',
    sentiment_score__lte=0.6
).count()

print(f"  Negative with score >= 0.4: {negative_wrong} (should be 0)")
print(f"  Neutral with score outside 0.4-0.6: {neutral_wrong} (should be low)")
print(f"  Positive with score <= 0.6: {positive_wrong} (should be 0)")
```

### Step 4: Verify Time Distribution

```python
from datetime import datetime
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncHour

# Daily distribution
daily_dist = SentimentData.objects.annotate(
    date=TruncDate('timestamp')
).values('date').annotate(
    count=Count('id')
).order_by('-date')[:10]

print("Most recent 10 days:")
for item in daily_dist:
    print(f"  {item['date']}: {item['count']} records")
# Expected: More recent dates should have higher counts

# Hourly distribution
hourly_dist = SentimentData.objects.annotate(
    hour=TruncHour('timestamp')
).values('hour').annotate(
    count=Count('id')
).order_by('-count')[:5]

print("\nTop 5 hours:")
for item in hourly_dist:
    print(f"  {item['hour']}: {item['count']} records")
# Expected: Peak hours (7-9am, 12-2pm, 6-9pm) should appear

# Weekday distribution
from django.db.models.functions import ExtractWeekDay
weekday_dist = SentimentData.objects.annotate(
    weekday=ExtractWeekDay('timestamp')
).values('weekday').annotate(
    count=Count('id')
).order_by('weekday')

weekday_names = {
    1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
    5: 'Thursday', 6: 'Friday', 7: 'Saturday'
}

print("\nWeekday distribution:")
for item in weekday_dist:
    name = weekday_names.get(item['weekday'], 'Unknown')
    print(f"  {name}: {item['count']}")
# Expected: Weekdays (Mon-Fri) should have ~30% more than weekends
```

### Step 5: Verify Geographic Patterns

```python
# Check water crisis districts
water_crisis_districts = ['Coimbatore', 'Chennai', 'Salem', 'Tiruchirappalli', 'Erode']
healthcare_issue = IssueCategory.objects.filter(name__icontains='Healthcare').first()

if healthcare_issue:
    water_district_count = SentimentData.objects.filter(
        issue=healthcare_issue,
        district__name__in=water_crisis_districts
    ).count()
    total_healthcare = SentimentData.objects.filter(issue=healthcare_issue).count()

    if total_healthcare > 0:
        percentage = (water_district_count / total_healthcare) * 100
        print(f"Healthcare/Water issue in crisis districts: {water_district_count}/{total_healthcare} ({percentage:.1f}%)")
        # Expected: High percentage in water crisis districts

# Check coastal districts for fishermen issues
coastal_districts = ['Ramanathapuram', 'Nagapattinam', 'Pudukkottai', 'Thanjavur']
fishermen_issue = IssueCategory.objects.filter(name__icontains='Fishermen').first()

if fishermen_issue:
    coastal_count = SentimentData.objects.filter(
        issue=fishermen_issue,
        district__name__in=coastal_districts
    ).count()
    total_fishermen = SentimentData.objects.filter(issue=fishermen_issue).count()

    if total_fishermen > 0:
        percentage = (coastal_count / total_fishermen) * 100
        print(f"Fishermen issue in coastal districts: {coastal_count}/{total_fishermen} ({percentage:.1f}%)")
        # Expected: High percentage in coastal districts

# Check urban vs rural distribution
urban_districts = ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem']
urban_count = SentimentData.objects.filter(district__name__in=urban_districts).count()
urban_percentage = (urban_count / total) * 100
print(f"\nUrban districts (top 5): {urban_count}/{total} ({urban_percentage:.1f}%)")
# Expected: ~40-60% in urban districts
```

### Step 6: Performance Check

```python
import time

# Test query performance
start = time.time()
result = SentimentData.objects.filter(
    district__name='Chennai',
    polarity='negative',
    timestamp__gte=datetime(2024, 11, 1)
).count()
end = time.time()

print(f"\nQuery performance:")
print(f"  Chennai negative sentiment (Nov 2024): {result} records")
print(f"  Query time: {(end - start) * 1000:.2f}ms")
# Expected: < 100ms for indexed queries

# Test aggregation performance
start = time.time()
result = SentimentData.objects.values('district__name').annotate(
    avg_sentiment=Avg('sentiment_score'),
    count=Count('id')
).order_by('-count')
end = time.time()

print(f"  District aggregation: {len(result)} districts")
print(f"  Query time: {(end - start) * 1000:.2f}ms")
# Expected: < 200ms
```

## Full Dataset Test (50,000 records)

Once small tests pass, generate full dataset:

```bash
# Clear test data first (optional)
python manage.py shell
>>> from api.models import SentimentData
>>> SentimentData.objects.all().delete()
>>> exit()

# Generate full dataset
python manage.py generate_sentiment_data --count 50000

# Expected duration: 30-45 seconds
# Expected output: Statistics showing all distributions
```

## Verification Checklist

- [ ] Command runs without errors
- [ ] 50,000 records created
- [ ] Date range: Sept 1 - Nov 30, 2024
- [ ] Polarity distribution: ~37% negative, ~32% neutral, ~31% positive
- [ ] Source distribution: 40% direct, 35% social, 20% field, 5% survey
- [ ] Top districts: Chennai, Coimbatore, Madurai
- [ ] All 38 districts covered
- [ ] No null values in required fields
- [ ] Sentiment scores: 0.0 - 1.0 range
- [ ] Confidence scores: 0.0 - 1.0 range
- [ ] Polarity mapping correct
- [ ] Recent dates have more volume
- [ ] Peak hours visible in distribution
- [ ] Weekdays have more volume than weekends
- [ ] Issue-district mapping correct
- [ ] Query performance acceptable (< 200ms)

## Common Issues and Solutions

### Issue: Low record count
**Check**: Verify batch creation didn't fail
**Solution**: Check Django logs, reduce batch size

### Issue: Skewed distributions
**Check**: Random seed might be causing pattern
**Solution**: Re-run command, distributions are probabilistic

### Issue: Missing districts
**Check**: District data exists
**Solution**: Run `seed_political_data` command

### Issue: All same timestamp
**Check**: Timezone settings
**Solution**: Verify TIME_ZONE in Django settings

### Issue: Poor performance
**Check**: Database indexes
**Solution**: Run `python manage.py migrate` to ensure indexes exist

## SQL Verification Queries

```sql
-- Total count
SELECT COUNT(*) FROM api_sentimentdata;

-- Polarity distribution
SELECT polarity, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM api_sentimentdata), 1) as percentage
FROM api_sentimentdata
GROUP BY polarity;

-- Source distribution
SELECT source_type, COUNT(*) as count
FROM api_sentimentdata
GROUP BY source_type
ORDER BY count DESC;

-- Top districts
SELECT d.name, COUNT(*) as count
FROM api_sentimentdata s
JOIN api_district d ON s.district_id = d.id
GROUP BY d.name
ORDER BY count DESC
LIMIT 10;

-- Date range
SELECT
    MIN(DATE(timestamp)) as min_date,
    MAX(DATE(timestamp)) as max_date,
    COUNT(DISTINCT DATE(timestamp)) as unique_days
FROM api_sentimentdata;

-- Average scores
SELECT
    ROUND(AVG(sentiment_score), 2) as avg_sentiment,
    ROUND(AVG(confidence), 2) as avg_confidence
FROM api_sentimentdata;

-- Records by month
SELECT
    strftime('%Y-%m', timestamp) as month,
    COUNT(*) as count
FROM api_sentimentdata
GROUP BY month
ORDER BY month;
```

## Export for Analysis

```bash
# Export to CSV
python manage.py shell
```

```python
import csv
from api.models import SentimentData

# Export summary
with open('sentiment_summary.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Issue', 'District', 'Polarity', 'Sentiment Score', 'Confidence', 'Source', 'Timestamp'])

    for record in SentimentData.objects.select_related('issue', 'district').all()[:1000]:
        writer.writerow([
            record.issue.name,
            record.district.name,
            record.polarity,
            float(record.sentiment_score),
            float(record.confidence),
            record.source_type,
            record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        ])

print("Exported 1000 records to sentiment_summary.csv")
```

---

**Test Guide Version**: 1.0
**Last Updated**: 2024-11-09
