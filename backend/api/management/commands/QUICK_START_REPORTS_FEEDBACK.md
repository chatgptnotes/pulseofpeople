# Quick Start Guide: Field Reports & Direct Feedback

## TL;DR

Generate 3,000 field reports and 5,000 citizen feedback submissions with realistic Tamil Nadu political sentiment data.

---

## One-Command Setup

```bash
# Activate virtual environment first
cd /Users/murali/Applications/pulseofpeople/backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows

# Generate all test data
python manage.py generate_field_reports --count 3000
python manage.py generate_direct_feedback --count 5000
```

---

## What Gets Generated

### Field Reports (3,000 total)

| Type | Count | Examples |
|------|-------|----------|
| Daily Summaries | 1,500 | "Ward-15 field visit: 45 families met, water supply top concern" |
| Event Feedback | 750 | "TVK rally: 5,000+ attendance, very enthusiastic crowd" |
| Issue Reports | 450 | "URGENT: Water crisis in Ward-23, no supply for 3 days" |
| Competitor Activity | 150 | "DMK small rally observed, 200 attendees" |
| Booth Reports | 150 | "Booth 042: 60% households covered, database updated" |

**Key Features:**
- ✅ Last 60 days of data
- ✅ 70% verified, 25% pending, 5% disputed
- ✅ Realistic Tamil names and locations
- ✅ Linked to issue categories and voter segments
- ✅ Peak reporting 6-8 PM (after field work)

---

### Direct Feedback (5,000 total)

| Issue | Count | Examples |
|-------|-------|----------|
| Water Supply | 1,100 | "No water for 5 days. Tanker water Rs.1200. Children fetching water 2km away." |
| Jobs/Employment | 900 | "Engineering grad, 3 years no job. Only call center Rs.15k offers." |
| Agriculture | 600 | "Cauvery water not coming. Paddy dying. Input costs doubled." |
| NEET Opposition | 500 | "Daughter 95% in 12th, NEET failed. Doctor dream shattered." |
| Healthcare | 450 | "PHC no doctor for 20 days. Pregnant women traveling 30km." |
| Education | 400 | "School has no building. 300 students studying under trees." |
| Fishermen Rights | 300 | "Husband arrested by SL Navy 3rd time. Family starving." |
| Cauvery Water | 250 | "Karnataka not releasing water. Delta farmers suffering." |
| Others | 500 | "Roads damaged, potholes everywhere. 2-wheeler accidents daily." |

**Key Features:**
- ✅ Last 90 days of data
- ✅ AI analysis: sentiment (0.1-0.9), urgency (low/medium/high/urgent)
- ✅ 60% analyzed, 20% reviewed, 15% pending, 5% escalated
- ✅ Realistic citizen demographics (age 18-75, 60% male, 40% female)
- ✅ All 42 TN districts covered
- ✅ Issue-district correlation (water→Coimbatore, fishermen→coastal)

---

## Prerequisites Check

```bash
# 1. Check if master data exists
python manage.py shell -c "from api.models import State, District; print(f'States: {State.objects.count()}, Districts: {District.objects.count()}')"

# Expected: States: 1 (TN), Districts: 42

# 2. Check if volunteers exist
python manage.py shell -c "from django.contrib.auth.models import User; print(f'Volunteers: {User.objects.filter(profile__role__in=[\"volunteer\", \"user\"]).count()}')"

# Expected: At least 50-500 users

# 3. Check if issue categories exist
python manage.py shell -c "from api.models import IssueCategory; print(f'Issues: {IssueCategory.objects.count()}')"

# Expected: At least 10-20 categories
```

**If any check fails, run:**

```bash
python manage.py generate_master_data      # Creates states, districts, constituencies
python manage.py seed_political_data       # Creates issue categories, voter segments
python manage.py generate_users --count 500  # Creates volunteers
```

---

## Verification

### Check Field Reports

```bash
python manage.py shell
```

```python
from api.models import FieldReport

# Total reports
FieldReport.objects.count()  # 3000

# By type
FieldReport.objects.filter(report_type='daily_summary').count()  # 1500
FieldReport.objects.filter(report_type='event_feedback').count()  # 750

# By verification status
FieldReport.objects.filter(verification_status='verified').count()  # 2100
FieldReport.objects.filter(verification_status='pending').count()  # 750

# Recent reports
FieldReport.objects.order_by('-timestamp')[:5]
```

### Check Direct Feedback

```python
from api.models import DirectFeedback

# Total feedback
DirectFeedback.objects.count()  # 5000

# By status
DirectFeedback.objects.filter(status='analyzed').count()  # 3000
DirectFeedback.objects.filter(status='reviewed').count()  # 1000
DirectFeedback.objects.filter(status='escalated').count()  # 250

# By urgency
DirectFeedback.objects.filter(ai_urgency='urgent').count()  # 1000
DirectFeedback.objects.filter(ai_urgency='high').count()  # 3000

# By sentiment
DirectFeedback.objects.filter(ai_sentiment_polarity='negative').count()  # 4000

# Sample urgent water crisis
DirectFeedback.objects.filter(
    issue_category__name__icontains='Water',
    ai_urgency='urgent'
).first()
```

---

## Sample Queries

### Top 10 Most Active Reporters

```python
from django.db.models import Count

top_reporters = FieldReport.objects.values('volunteer__username').annotate(
    report_count=Count('id')
).order_by('-report_count')[:10]

for reporter in top_reporters:
    print(f"{reporter['volunteer__username']}: {reporter['report_count']} reports")
```

### Issue Distribution by District

```python
issue_by_district = DirectFeedback.objects.values(
    'district__name', 'issue_category__name'
).annotate(
    count=Count('id')
).order_by('-count')[:20]

for item in issue_by_district:
    print(f"{item['district__name']} - {item['issue_category__name']}: {item['count']}")
```

### Urgent Unresolved Feedback

```python
urgent_pending = DirectFeedback.objects.filter(
    ai_urgency__in=['urgent', 'high'],
    status='pending'
).order_by('-submitted_at')

print(f"Urgent pending: {urgent_pending.count()}")
for fb in urgent_pending[:10]:
    print(f"{fb.citizen_name} - {fb.issue_category.name} - {fb.ward}")
```

### Sentiment Trend (Last 30 Days)

```python
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg

thirty_days_ago = timezone.now() - timedelta(days=30)

avg_sentiment = DirectFeedback.objects.filter(
    submitted_at__gte=thirty_days_ago,
    ai_sentiment_score__isnull=False
).aggregate(Avg('ai_sentiment_score'))

print(f"Average sentiment (last 30 days): {avg_sentiment['ai_sentiment_score__avg']:.2f}")
```

---

## Performance Notes

- **Field Reports**: ~30 seconds for 3,000 records
- **Direct Feedback**: ~45 seconds for 5,000 records
- **Bulk Insert**: 500 records per transaction
- **Progress Updates**: Every 500 records
- **Database Size**: ~21 MB total

---

## Cleanup

### Delete All Generated Data

```bash
python manage.py shell
```

```python
from api.models import FieldReport, DirectFeedback

# Delete field reports
FieldReport.objects.all().delete()

# Delete direct feedback
DirectFeedback.objects.all().delete()
```

### Delete Only Test Data (Keep Real Data)

```python
from django.utils import timezone
from datetime import timedelta

# Delete field reports older than 90 days
old_date = timezone.now() - timedelta(days=90)
FieldReport.objects.filter(timestamp__lt=old_date).delete()

# Delete unverified reports older than 30 days
old_unverified = timezone.now() - timedelta(days=30)
FieldReport.objects.filter(
    verification_status='pending',
    timestamp__lt=old_unverified
).delete()
```

---

## Troubleshooting

| Error | Solution |
|-------|----------|
| "No volunteers found" | `python manage.py generate_users --count 500` |
| "Tamil Nadu state not found" | `python manage.py generate_master_data` |
| "No issue categories" | `python manage.py seed_political_data` |
| Slow performance | Normal - bulk insert is optimized |
| Duplicate data on re-run | Safe - uses `ignore_conflicts=True` |

---

## Next Steps

After generating data, use it for:

1. **Dashboard Development**: Build charts, maps, heatmaps
2. **API Testing**: Test filtering, sorting, pagination
3. **Analytics**: Sentiment trends, issue distribution
4. **Workflow Testing**: Verification, escalation, review flows
5. **Performance Testing**: Load testing with realistic data volumes

---

## Full Documentation

For detailed information, see:
- `/backend/api/management/commands/README_FIELD_REPORTS_AND_FEEDBACK.md`

---

**Quick Reference**: Keep this file handy for rapid data generation during development!

**Version**: 1.0 | **Last Updated**: 2024-11-09
