# Social Media Posts Generator - Quick Start

## One-Command Setup

```bash
# 1. Navigate to backend
cd /Users/murali/Applications/pulseofpeople/backend

# 2. Activate virtual environment (if not already active)
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# 3. Generate 20,000 posts
python manage.py generate_social_posts
```

## Common Commands

```bash
# Default: 20,000 posts
python manage.py generate_social_posts

# With Supabase SQL export
python manage.py generate_social_posts --generate-sql

# Custom count
python manage.py generate_social_posts --count 10000

# Specific platform
python manage.py generate_social_posts --platform twitter --count 5000

# Small test set
python manage.py generate_social_posts --count 100

# Production: 50K posts with SQL
python manage.py generate_social_posts --count 50000 --batch-size 1000 --generate-sql
```

## What You Get

### 20,000 Posts Distributed As:
- **Twitter**: 10,000 posts (50%)
- **Facebook**: 6,000 posts (30%)
- **Instagram**: 3,000 posts (15%)
- **YouTube**: 600 posts (3%)
- **WhatsApp**: 400 posts (2%)

### Content Categories:
- Water Crisis (25%)
- TVK/Vijay Support (25%)
- NEET Protests (15%)
- Cauvery Water (15%)
- Fishermen Issues (10%)
- Development (10%)

### Engagement Tiers:
- Viral: 1,000 posts (5K-50K likes)
- High: 3,000 posts (500-5K likes)
- Medium: 8,000 posts (50-500 likes)
- Low: 8,000 posts (5-50 likes)

## Verify Generation

```bash
# Django shell
python manage.py shell

>>> from api.models import SocialMediaPost
>>> SocialMediaPost.objects.count()
20000

>>> # Platform breakdown
>>> from django.db.models import Count
>>> SocialMediaPost.objects.values('platform').annotate(count=Count('id'))

>>> # Top posts
>>> SocialMediaPost.objects.order_by('-engagement_count')[:5]
```

## Output Files

### Django Database
- **Location**: `db.sqlite3` (or PostgreSQL)
- **Table**: `api_socialmediapost`
- **Records**: 20,000

### Supabase SQL (if `--generate-sql` used)
- **Location**: `/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/social_posts_seed.sql`
- **Size**: ~28 MB (20K posts)
- **Format**: PostgreSQL INSERT statements

## Expected Runtime

| Posts | Time | Memory |
|-------|------|--------|
| 100 | 2s | 10 MB |
| 1,000 | 8s | 25 MB |
| 10,000 | 65s | 150 MB |
| 20,000 | 120s | 280 MB |
| 50,000 | 300s | 650 MB |

## Sample Output

```
=== Generating 20,000 Social Media Posts ===

Loading reference data...
  - 38 districts loaded
  - 12 campaigns loaded
  - 15 issue categories loaded

Generating posts by platform:
  - twitter: 10,000 posts
  - facebook: 6,000 posts
  - instagram: 3,000 posts
  - youtube: 600 posts
  - whatsapp: 400 posts

Generating 10,000 twitter posts...
  Progress: 1,000/10,000 (10.0%)
  Progress: 2,000/10,000 (20.0%)
  ...

Saving 20,000 posts to database...
  Saved batch 1: 500/20,000 posts
  Saved batch 2: 1,000/20,000 posts
  ...
✓ All posts saved to database

=== STATISTICS ===

Platform Distribution:
  twitter        : 10,000 posts (50.0%)
  facebook       :  6,000 posts (30.0%)
  instagram      :  3,000 posts (15.0%)
  youtube        :    600 posts ( 3.0%)
  whatsapp       :    400 posts ( 2.0%)

Engagement Tiers:
  Viral (5K+ likes)  :  1,000 posts ( 5.0%)
  High (500-5K)      :  3,000 posts (15.0%)
  Medium (50-500)    :  8,000 posts (40.0%)
  Low (<50)          :  8,000 posts (40.0%)

Sentiment Distribution:
  Positive (≥0.6)    :  7,000 posts (35.0%)
  Neutral (0.4-0.6)  :  5,000 posts (25.0%)
  Negative (≤0.4)    :  8,000 posts (40.0%)

Total Engagement:
  Total Likes        : 2,456,789
  Total Shares       :   567,234
  Total Comments     :   234,567
  Total Reach        : 45,678,901
  Avg Engagement Rate: 7.13%

Date Range: 2024-11-23 to 2024-11-30

✓ Successfully generated 20,000 social media posts!
```

## Troubleshooting

### "No districts found"
```bash
python manage.py generate_master_data
```

### "Memory error"
```bash
python manage.py generate_social_posts --batch-size 100
```

### "Too slow"
```bash
python manage.py generate_social_posts --batch-size 1000
```

## Next Steps

1. **View in Django Admin**
   ```bash
   python manage.py runserver
   # Visit: http://127.0.0.1:8000/admin/api/socialmediapost/
   ```

2. **Export to Supabase**
   ```bash
   python manage.py generate_social_posts --generate-sql
   # Import: frontend/supabase/seeds/social_posts_seed.sql
   ```

3. **Run Analytics**
   ```python
   from api.models import SocialMediaPost
   from django.db.models import Avg, Sum

   # Sentiment by platform
   SocialMediaPost.objects.values('platform').annotate(
       avg_sentiment=Avg('sentiment_score')
   )

   # Total engagement
   SocialMediaPost.objects.aggregate(
       total_likes=Sum('likes'),
       total_reach=Sum('reach')
   )
   ```

## Documentation

- **Full README**: `api/management/commands/README_SOCIAL_POSTS.md`
- **Usage Guide**: `api/management/commands/USAGE_GUIDE_SOCIAL_POSTS.md`
- **Summary**: `SOCIAL_POSTS_GENERATION_SUMMARY.md`
- **This File**: `QUICK_START_SOCIAL_POSTS.md`

## Support

Questions? Check the detailed documentation:
```bash
cat api/management/commands/README_SOCIAL_POSTS.md
```

---

**TL;DR**: Run `python manage.py generate_social_posts` and get 20,000 realistic Tamil Nadu political posts in 2 minutes.

**Version**: 1.0 | **Status**: ✅ Ready to Use
