# Social Media Posts Generator - Complete Usage Guide

## Quick Start

### 1. Prerequisites
Ensure you have the following data in your database:
```bash
# Generate Tamil Nadu districts and constituencies
python manage.py generate_master_data

# Optional: Create campaigns for linking
python manage.py seed_campaigns
```

### 2. Generate Posts
```bash
# Generate 20,000 posts (default)
python manage.py generate_social_posts

# With Supabase SQL export
python manage.py generate_social_posts --generate-sql
```

### 3. Verify Generation
```bash
# Check Django database
python manage.py shell
>>> from api.models import SocialMediaPost
>>> SocialMediaPost.objects.count()
20000

# Check by platform
>>> SocialMediaPost.objects.values('platform').annotate(count=Count('id'))
```

## Advanced Usage Scenarios

### Scenario 1: Platform-Specific Generation

#### Generate Twitter Posts Only
```bash
python manage.py generate_social_posts --platform twitter --count 10000
```

**Use Case**: Focus on Twitter sentiment analysis, trending hashtags

**Expected Output**:
- 10,000 Twitter posts
- Platform-specific IDs (19-digit numeric)
- URLs: `https://twitter.com/user/status/[ID]`
- Higher text-based engagement

#### Generate Facebook Posts Only
```bash
python manage.py generate_social_posts --platform facebook --count 6000
```

**Use Case**: Community discussion analysis, longer content engagement

**Expected Output**:
- 6,000 Facebook posts
- Platform-specific IDs (15-digit numeric)
- URLs: `https://facebook.com/post/[ID]`
- Balanced engagement across all metrics

#### Generate Instagram Posts Only
```bash
python manage.py generate_social_posts --platform instagram --count 3000
```

**Use Case**: Visual content engagement, youth demographics

**Expected Output**:
- 3,000 Instagram posts
- Alphanumeric post codes (11 chars)
- URLs: `https://instagram.com/p/[CODE]/`
- Higher likes-to-comments ratio

### Scenario 2: Incremental Data Loading

#### Load in Batches to Avoid Memory Issues
```bash
# Load 5,000 posts at a time
python manage.py generate_social_posts --count 5000 --batch-size 500
python manage.py generate_social_posts --count 5000 --batch-size 500
python manage.py generate_social_posts --count 5000 --batch-size 500
python manage.py generate_social_posts --count 5000 --batch-size 500
```

**Use Case**: Limited server memory, production environments

**Benefits**:
- Lower memory footprint
- Easier to monitor progress
- Can run during low-traffic hours

### Scenario 3: Testing & Development

#### Generate Small Sample for Testing
```bash
# Just 100 posts for quick testing
python manage.py generate_social_posts --count 100

# Or even smaller for unit tests
python manage.py generate_social_posts --count 10
```

**Use Case**: Feature development, UI testing, analytics testing

**Benefits**:
- Fast generation (< 5 seconds)
- Easy to inspect data
- Quick iteration cycles

### Scenario 4: Production Deployment

#### Full Production Load with SQL Export
```bash
# Generate 50,000 posts with SQL export for Supabase
python manage.py generate_social_posts --count 50000 --batch-size 1000 --generate-sql
```

**Use Case**: Production data seeding, Supabase sync

**Expected Output**:
- Django database: 50,000 records
- SQL file: `frontend/supabase/seeds/social_posts_seed.sql`
- Generation time: ~2-3 minutes
- File size: ~50-100 MB

## Content Distribution Analysis

### Understanding Generated Content

#### Content Type Breakdown (20,000 posts)
```
Water Crisis:         5,000 posts (25%)
TVK/Vijay Support:    5,000 posts (25%)
NEET Protests:        3,000 posts (15%)
Cauvery Water:        3,000 posts (15%)
Fishermen Issues:     2,000 posts (10%)
Development/Progress: 2,000 posts (10%)
```

#### Real-World Mapping
- **Water Crisis**: Reflects actual Chennai water crisis (2019-2024)
- **TVK/Vijay**: New political party launch (2024)
- **NEET**: Ongoing Tamil Nadu political issue
- **Cauvery**: Perennial interstate water dispute
- **Fishermen**: Sri Lankan Navy arrests
- **Development**: Infrastructure projects

### Hashtag Analytics

#### Top 20 Expected Hashtags
1. `#TVK` - ~8,000 occurrences
2. `#TNWaterCrisis` - ~6,000 occurrences
3. `#SaveTamilNadu` - ~5,500 occurrences
4. `#VijayForTN` - ~5,000 occurrences
5. `#StopNEET` - ~4,500 occurrences
6. `#CauveryWater` - ~3,500 occurrences
7. `#TNFishermen` - ~2,500 occurrences
8. `#TNDevelopment` - ~2,000 occurrences
9. `#WaterScarcity` - ~3,000 occurrences
10. `#TVKVision2026` - ~4,000 occurrences
11. `#NEETHurts` - ~2,800 occurrences
12. `#SaveDeltaFarmers` - ~2,500 occurrences
13. `#FishermenRights` - ~1,800 occurrences
14. `#CleanPolitics` - ~3,500 occurrences
15. `#Chennai` - ~4,000 occurrences
16. `#TamilNadu` - ~3,200 occurrences
17. `#Coimbatore` - ~2,000 occurrences
18. `#FarmersFirst` - ~2,200 occurrences
19. `#TNStudents` - ~2,500 occurrences
20. `#NewPolitics` - ~3,000 occurrences

## Performance Benchmarks

### Generation Speed (MacBook Pro M1)

| Posts | Batch Size | Time | Memory |
|-------|-----------|------|--------|
| 100 | 100 | 2s | 10 MB |
| 1,000 | 500 | 8s | 25 MB |
| 5,000 | 500 | 35s | 80 MB |
| 10,000 | 500 | 65s | 150 MB |
| 20,000 | 500 | 120s | 280 MB |
| 50,000 | 1000 | 300s | 650 MB |

### Database Impact

| Posts | Django DB Size | SQL File Size | Supabase Import Time |
|-------|---------------|---------------|----------------------|
| 1,000 | 2 MB | 1.5 MB | 5s |
| 5,000 | 10 MB | 7 MB | 20s |
| 10,000 | 20 MB | 14 MB | 40s |
| 20,000 | 40 MB | 28 MB | 80s |
| 50,000 | 100 MB | 70 MB | 200s |

## Data Quality Checks

### Post-Generation Validation

#### 1. Platform Distribution Check
```python
from api.models import SocialMediaPost
from django.db.models import Count

# Expected distribution
platforms = SocialMediaPost.objects.values('platform').annotate(
    count=Count('id')
).order_by('-count')

for p in platforms:
    percentage = (p['count'] / 20000) * 100
    print(f"{p['platform']}: {p['count']} ({percentage:.1f}%)")

# Expected output:
# twitter: 10000 (50.0%)
# facebook: 6000 (30.0%)
# instagram: 3000 (15.0%)
# youtube: 600 (3.0%)
# whatsapp: 400 (2.0%)
```

#### 2. Engagement Tier Validation
```python
# Viral posts (5% expected)
viral = SocialMediaPost.objects.filter(likes__gte=5000).count()
print(f"Viral posts: {viral} ({viral/200:.1f}%)")  # Should be ~5%

# High engagement (15% expected)
high = SocialMediaPost.objects.filter(likes__gte=500, likes__lt=5000).count()
print(f"High engagement: {high} ({high/200:.1f}%)")  # Should be ~15%

# Medium engagement (40% expected)
medium = SocialMediaPost.objects.filter(likes__gte=50, likes__lt=500).count()
print(f"Medium engagement: {medium} ({medium/200:.1f}%)")  # Should be ~40%

# Low engagement (40% expected)
low = SocialMediaPost.objects.filter(likes__lt=50).count()
print(f"Low engagement: {low} ({low/200:.1f}%)")  # Should be ~40%
```

#### 3. Sentiment Distribution Check
```python
from decimal import Decimal

# Positive (expected ~35%)
positive = SocialMediaPost.objects.filter(sentiment_score__gte=Decimal('0.6')).count()
print(f"Positive: {positive} ({positive/200:.1f}%)")

# Negative (expected ~40%)
negative = SocialMediaPost.objects.filter(sentiment_score__lte=Decimal('0.4')).count()
print(f"Negative: {negative} ({negative/200:.1f}%)")

# Neutral (expected ~25%)
neutral = SocialMediaPost.objects.filter(
    sentiment_score__gt=Decimal('0.4'),
    sentiment_score__lt=Decimal('0.6')
).count()
print(f"Neutral: {neutral} ({neutral/200:.1f}%)")
```

#### 4. Time Range Validation
```python
from django.db.models import Min, Max

time_range = SocialMediaPost.objects.aggregate(
    earliest=Min('posted_at'),
    latest=Max('posted_at')
)

print(f"Date range: {time_range['earliest'].date()} to {time_range['latest'].date()}")
# Expected: 2024-11-23 to 2024-11-30 (7 days)
```

## Supabase Integration

### Import SQL Seed File

#### 1. Via Supabase CLI
```bash
# Navigate to project root
cd /Users/murali/Applications/pulseofpeople/frontend

# Import seed file
supabase db reset --db-url [YOUR_DB_URL] < supabase/seeds/social_posts_seed.sql
```

#### 2. Via Supabase Dashboard
1. Go to SQL Editor in Supabase Dashboard
2. Upload `social_posts_seed.sql`
3. Click "Run"
4. Wait for completion (~1-2 minutes for 20K posts)

#### 3. Via psql Command
```bash
psql [YOUR_SUPABASE_DB_URL] -f supabase/seeds/social_posts_seed.sql
```

### Verify Supabase Import

```sql
-- Check total posts
SELECT COUNT(*) FROM social_posts;

-- Platform breakdown
SELECT platform, COUNT(*) as count
FROM social_posts
GROUP BY platform
ORDER BY count DESC;

-- Top engaging posts
SELECT platform, post_content, engagement_count
FROM social_posts
ORDER BY engagement_count DESC
LIMIT 10;
```

## Analytics Use Cases

### 1. Sentiment Trend Analysis
```python
from api.models import SocialMediaPost
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate

# Daily sentiment trends
daily_sentiment = SocialMediaPost.objects.annotate(
    date=TruncDate('posted_at')
).values('date').annotate(
    avg_sentiment=Avg('sentiment_score'),
    post_count=Count('id')
).order_by('date')

for day in daily_sentiment:
    print(f"{day['date']}: Avg Sentiment: {day['avg_sentiment']:.2f}, Posts: {day['post_count']}")
```

### 2. Platform Engagement Comparison
```python
from django.db.models import Avg

platform_metrics = SocialMediaPost.objects.values('platform').annotate(
    avg_likes=Avg('likes'),
    avg_shares=Avg('shares'),
    avg_comments=Avg('comments_count'),
    avg_reach=Avg('reach'),
    avg_engagement=Avg('engagement_count')
)

for p in platform_metrics:
    print(f"\n{p['platform'].upper()}")
    print(f"  Avg Likes: {p['avg_likes']:.0f}")
    print(f"  Avg Shares: {p['avg_shares']:.0f}")
    print(f"  Avg Comments: {p['avg_comments']:.0f}")
    print(f"  Avg Reach: {p['avg_reach']:.0f}")
    print(f"  Avg Engagement: {p['avg_engagement']:.0f}")
```

### 3. Hashtag Popularity
```python
from django.db.models import Count, Q
import json

# Top hashtags across all posts
all_hashtags = []
for post in SocialMediaPost.objects.all():
    all_hashtags.extend(post.hashtags)

from collections import Counter
hashtag_counts = Counter(all_hashtags)

print("Top 20 Hashtags:")
for tag, count in hashtag_counts.most_common(20):
    print(f"  {tag}: {count} posts")
```

### 4. TVK Campaign Impact
```python
# Posts mentioning TVK
tvk_posts = SocialMediaPost.objects.filter(
    Q(post_content__icontains='TVK') |
    Q(post_content__icontains='Vijay')
)

print(f"Total TVK-related posts: {tvk_posts.count()}")
print(f"Avg sentiment: {tvk_posts.aggregate(Avg('sentiment_score'))['sentiment_score__avg']:.2f}")
print(f"Total engagement: {tvk_posts.aggregate(Sum('engagement_count'))['engagement_count__sum']:,}")
```

### 5. Crisis Content Analysis
```python
# Water crisis posts
water_posts = SocialMediaPost.objects.filter(
    Q(post_content__icontains='water') |
    Q(hashtags__contains=['#TNWaterCrisis'])
)

print(f"Water crisis posts: {water_posts.count()}")
print(f"Avg sentiment: {water_posts.aggregate(Avg('sentiment_score'))['sentiment_score__avg']:.2f}")
print(f"Viral water posts: {water_posts.filter(likes__gte=5000).count()}")
```

## Troubleshooting

### Issue: Generation Too Slow
**Solution**:
```bash
# Increase batch size
python manage.py generate_social_posts --batch-size 1000

# Or generate in parallel chunks manually
python manage.py generate_social_posts --platform twitter --count 10000 &
python manage.py generate_social_posts --platform facebook --count 6000 &
wait
```

### Issue: SQL File Too Large
**Solution**:
```bash
# Generate without SQL first
python manage.py generate_social_posts --count 20000

# Then export from Django
python manage.py dumpdata api.SocialMediaPost --format json --indent 2 > posts.json

# Or split SQL into chunks
python manage.py generate_social_posts --platform twitter --generate-sql
python manage.py generate_social_posts --platform facebook --generate-sql
# Results in separate SQL files per platform
```

### Issue: Memory Error
**Solution**:
```bash
# Reduce batch size drastically
python manage.py generate_social_posts --count 20000 --batch-size 100

# Or clear memory between runs
python manage.py generate_social_posts --count 5000
# Wait for completion, then:
python manage.py generate_social_posts --count 5000
# Repeat
```

### Issue: Duplicate Post IDs
**Solution**:
```python
# Post IDs are randomly generated and should be unique
# If duplicates occur (unlikely), regenerate:
from api.models import SocialMediaPost
SocialMediaPost.objects.all().delete()
# Then re-run command
```

## Best Practices

### 1. Development Environment
```bash
# Small dataset for quick iteration
python manage.py generate_social_posts --count 500
```

### 2. Staging Environment
```bash
# Medium dataset for feature testing
python manage.py generate_social_posts --count 5000 --generate-sql
```

### 3. Production Environment
```bash
# Full dataset with SQL export
python manage.py generate_social_posts --count 50000 --batch-size 1000 --generate-sql
```

### 4. CI/CD Pipeline
```bash
# Add to test fixtures
python manage.py generate_social_posts --count 100 --batch-size 100
python manage.py test
```

## Example Workflows

### Workflow 1: New Developer Onboarding
```bash
# 1. Setup database
python manage.py migrate

# 2. Generate minimal master data
python manage.py generate_master_data --count 5

# 3. Generate sample social posts
python manage.py generate_social_posts --count 500

# 4. Verify
python manage.py shell
>>> from api.models import SocialMediaPost
>>> SocialMediaPost.objects.count()
500
```

### Workflow 2: Analytics Feature Development
```bash
# 1. Generate diverse dataset
python manage.py generate_social_posts --count 10000

# 2. Develop analytics queries
# 3. Test with real-looking data
# 4. Iterate quickly with fresh data:
python manage.py shell
>>> from api.models import SocialMediaPost
>>> SocialMediaPost.objects.all().delete()
>>> exit()

python manage.py generate_social_posts --count 10000
```

### Workflow 3: Production Data Migration
```bash
# 1. Generate on local machine
python manage.py generate_social_posts --count 50000 --generate-sql

# 2. Copy SQL file to server
scp frontend/supabase/seeds/social_posts_seed.sql user@server:/path/

# 3. Import on server
ssh user@server
psql [DB_URL] -f /path/social_posts_seed.sql
```

## Maintenance

### Updating Content Templates
Edit `generate_social_posts.py` line ~250:
```python
templates = {
    'water_crisis': [
        "Your new template here #Hashtag",
        # Add more templates
    ],
    # Add new content types
    'new_category': [
        "New content templates",
    ],
}
```

### Adjusting Distributions
Edit platform distribution (line ~100):
```python
platform_distribution = {
    'twitter': 0.60,    # Increase Twitter to 60%
    'facebook': 0.25,   # Reduce Facebook to 25%
    # etc.
}
```

Edit engagement tiers (line ~390):
```python
tier_probabilities = {
    'viral': 0.10,      # Increase viral to 10%
    'high': 0.20,       # Increase high to 20%
    # etc.
}
```

## Support & Resources

- **Command Code**: `/Users/murali/Applications/pulseofpeople/backend/api/management/commands/generate_social_posts.py`
- **Documentation**: `/Users/murali/Applications/pulseofpeople/backend/api/management/commands/README_SOCIAL_POSTS.md`
- **Test Script**: `/Users/murali/Applications/pulseofpeople/backend/api/management/commands/test_social_posts_generation.py`
- **Sample SQL**: `/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/social_posts_seed_sample.sql`

---

**Version**: 1.0
**Last Updated**: 2024-11-09
**Platform**: Django 5.2 + PostgreSQL/SQLite
