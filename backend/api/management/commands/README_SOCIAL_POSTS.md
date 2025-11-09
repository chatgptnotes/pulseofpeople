# Generate Social Media Posts - Management Command

## Overview
Django management command to generate **20,000 realistic social media posts** for the Pulse of People platform with Tamil Nadu political context. The posts simulate real social media discourse around key political issues, TVK party, and regional concerns.

## Features

### 1. Realistic Platform Distribution
- **Twitter (50%)**: 10,000 posts - Political discourse, news, debates
- **Facebook (30%)**: 6,000 posts - Community discussions, longer posts
- **Instagram (15%)**: 3,000 posts - Visual content, youth engagement
- **YouTube (3%)**: 600 posts - Video content, speeches, debates
- **WhatsApp/News (2%)**: 400 posts - Messaging, media coverage

### 2. Content Categories
Six major content types with realistic distribution:

#### Water Crisis (25%)
- Water shortages across Tamil Nadu districts
- Groundwater depletion in Chennai
- Infrastructure failures
- Government accountability questions
- **Sentiment**: Negative (0.2-0.4)
- **Hashtags**: #TNWaterCrisis, #SaveTamilNadu, #WaterScarcity

#### TVK/Vijay Posts (25%)
- TVK party vision and policies
- Vijay's leadership and speeches
- Youth empowerment messaging
- Anti-corruption stance
- **Sentiment**: Positive (0.7-0.9)
- **Hashtags**: #TVK, #VijayForTN, #TVKVision2026, #CleanPolitics

#### NEET Protests (15%)
- Student suicides and mental health
- Rural student access issues
- Social justice concerns
- Demand for exemption
- **Sentiment**: Negative (0.3-0.5)
- **Hashtags**: #StopNEET, #NEETHurts, #AbolishNEET

#### Cauvery Water Dispute (15%)
- Karnataka water release issues
- Delta farmer struggles
- Supreme Court orders
- Agricultural crisis
- **Sentiment**: Negative (0.25-0.45)
- **Hashtags**: #CauveryWater, #SaveDeltaFarmers, #CauveryDispute

#### Fishermen Issues (10%)
- Sri Lankan Navy arrests
- Livelihood concerns
- Government inaction
- Safety demands
- **Sentiment**: Negative (0.3-0.5)
- **Hashtags**: #TNFishermen, #FishermenRights, #FishermenSafety

#### Development & Progress (10%)
- Infrastructure projects
- Healthcare expansion
- Education reforms
- Economic growth
- **Sentiment**: Positive (0.65-0.85)
- **Hashtags**: #TNDevelopment, #Progress, #SmartCity

### 3. Engagement Patterns

#### Viral Posts (5%)
- **Likes**: 5,000-50,000
- **Shares**: 1,000-10,000
- **Comments**: 500-5,000
- **Reach**: 50K-500K
- **Impressions**: 100K-1M

#### High Engagement (15%)
- **Likes**: 500-5,000
- **Shares**: 100-1,000
- **Comments**: 50-500
- **Reach**: 5K-50K
- **Impressions**: 10K-100K

#### Medium Engagement (40%)
- **Likes**: 50-500
- **Shares**: 10-100
- **Comments**: 5-50
- **Reach**: 500-5K
- **Impressions**: 1K-10K

#### Low Engagement (40%)
- **Likes**: 5-50
- **Shares**: 0-10
- **Comments**: 0-5
- **Reach**: 50-500
- **Impressions**: 100-1K

### 4. Author Distribution
- **Regular Citizens (60%)**: Organic community posts
- **Political Accounts (20%)**: Party handles, official accounts
- **Media Handles (10%)**: News outlets, journalists
- **Influencers (5%)**: Opinion leaders, activists
- **Anonymous (5%)**: Unattributed posts

### 5. Time Distribution
Posts distributed across **November 23-30, 2024** (7 days):

#### Peak Hours
- **Morning Rush (7-9am)**: 20% of posts
- **Lunch Break (12-2pm)**: 25% of posts
- **Evening Prime (6-9pm)**: 35% of posts
- **Late Night (10pm-12am)**: 10% of posts
- **Off Hours (12-7am, other)**: 10% of posts

#### Day Distribution
- **Weekdays**: 30% more volume than weekends
- **Event-driven spikes**: Rally days, announcements

### 6. Geographic Tagging
70% of posts tagged to specific districts with weighted distribution:

| District | Weight |
|----------|--------|
| Chennai | 25% |
| Coimbatore | 15% |
| Madurai | 10% |
| Salem | 8% |
| Tiruchirappalli | 7% |
| Tirunelveli | 6% |
| Erode | 5% |
| Vellore | 5% |
| Others | 19% |

## Usage

### Basic Usage
```bash
# Generate 20,000 posts (default)
python manage.py generate_social_posts

# Generate custom count
python manage.py generate_social_posts --count 10000

# Generate for specific platform
python manage.py generate_social_posts --platform twitter --count 5000

# Generate with Supabase SQL export
python manage.py generate_social_posts --generate-sql
```

### Advanced Options

#### 1. Custom Count
```bash
python manage.py generate_social_posts --count 50000
```

#### 2. Platform-Specific Generation
```bash
# Twitter only
python manage.py generate_social_posts --platform twitter --count 10000

# Facebook only
python manage.py generate_social_posts --platform facebook --count 6000

# Instagram only
python manage.py generate_social_posts --platform instagram --count 3000

# All platforms (default)
python manage.py generate_social_posts --platform all
```

#### 3. Batch Size Control
```bash
# Smaller batches (slower, less memory)
python manage.py generate_social_posts --batch-size 100

# Larger batches (faster, more memory)
python manage.py generate_social_posts --batch-size 1000
```

#### 4. Supabase SQL Export
```bash
# Generate Django records AND Supabase SQL seed file
python manage.py generate_social_posts --generate-sql
```
This creates: `/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/social_posts_seed.sql`

## Technical Implementation

### 1. Realistic Post IDs
Platform-specific ID formats:
- **Twitter**: 19-digit numeric IDs (e.g., `1234567890123456789`)
- **Facebook**: 15-digit numeric IDs (e.g., `123456789012345`)
- **Instagram**: 11-character alphanumeric codes (e.g., `CxYz123-_Ab`)
- **YouTube**: 11-character video IDs (e.g., `dQw4w9WgXcQ`)
- **WhatsApp/News**: UUID format

### 2. Realistic URLs
```python
# Twitter
https://twitter.com/user/status/1234567890123456789

# Facebook
https://facebook.com/post/123456789012345

# Instagram
https://instagram.com/p/CxYz123-_Ab/

# YouTube
https://youtube.com/watch?v=dQw4w9WgXcQ
```

### 3. Engagement Calculations
```python
# Engagement rate = (likes + shares + comments) / impressions × 100
# Average engagement: 2-5% (realistic for social media)

# Platform multipliers
twitter: 1.0
facebook: 0.8
instagram: 0.9
youtube: 1.2
whatsapp: 0.3
```

### 4. Sentiment Scoring
Uses `sentiment_score` decimal field (0.0-1.0):
- **0.0-0.4**: Negative (crisis, protests, problems)
- **0.4-0.6**: Neutral (informational, balanced)
- **0.6-1.0**: Positive (support, development, progress)

### 5. Campaign Linking
- TVK-related posts (25%) automatically linked to TVK campaigns
- 10% of other posts linked to random campaigns
- 65% of posts not linked to specific campaigns

## Output Statistics

After generation, the command prints detailed statistics:

### Example Output
```
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
```

## Database Schema

Posts saved to `api_socialmediapost` table with fields:

```python
platform            # twitter, facebook, instagram, youtube, whatsapp
post_content        # Full text content
post_url            # Platform-specific URL
post_id             # Platform-specific ID
posted_at           # Timestamp (distributed across 7 days)
reach               # Total users reached
impressions         # Total views
engagement_count    # likes + shares + comments
likes               # Like count
shares              # Share/retweet count
comments_count      # Comment count
sentiment_score     # 0.0-1.0 decimal
campaign_id         # FK to Campaign (nullable)
is_published        # Always True
is_promoted         # True for viral posts
hashtags            # JSON array
mentions            # JSON array
created_at          # Record creation timestamp
updated_at          # Record update timestamp
```

## Supabase SQL Export

When `--generate-sql` flag is used, generates PostgreSQL-compatible seed file:

### File Location
```
/Users/murali/Applications/pulseofpeople/frontend/supabase/seeds/social_posts_seed.sql
```

### SQL Features
- **Bulk INSERT statements** (all 20K posts)
- **UUID primary keys** for Supabase compatibility
- **PostgreSQL ARRAY syntax** for hashtags/mentions
- **Performance indexes** on key columns
- **ANALYZE command** for query optimization

### Example SQL
```sql
INSERT INTO social_posts (
    id, platform, post_content, post_url, post_id, posted_at,
    reach, impressions, engagement_count, likes, shares, comments_count,
    sentiment_score, campaign_id, is_published, is_promoted, hashtags, mentions,
    created_at, updated_at
) VALUES
(
    'a1b2c3d4-...', 'twitter', 'Water shortage in Chennai! When will this crisis end? #TNWaterCrisis #SaveTamilNadu',
    'https://twitter.com/user/status/1234567890123456789', '1234567890123456789', '2024-11-27 18:45:32',
    2500, 5000, 150, 120, 20, 10,
    0.35, NULL, true, false, ARRAY["#TNWaterCrisis","#SaveTamilNadu"], ARRAY["@TNGovt"],
    '2024-11-09 12:00:00', '2024-11-09 12:00:00'
),
...
```

## Performance

### Generation Speed
- **20,000 posts**: ~30-60 seconds
- **Batch size 500**: Optimal for memory/speed balance
- **Database writes**: Bulk insert for efficiency

### Memory Usage
- **20K posts in memory**: ~50-100 MB
- **Batch processing**: Prevents memory overflow
- **Transaction safety**: Rollback on errors

## Integration with Analytics

Generated posts can be used for:

1. **Sentiment Analysis Testing**
   - Verify AI sentiment scoring accuracy
   - Test sentiment trend visualizations
   - Geographic sentiment mapping

2. **Engagement Analytics**
   - Platform comparison reports
   - Viral content identification
   - Engagement rate calculations

3. **Campaign Performance**
   - TVK campaign reach analysis
   - Hashtag effectiveness tracking
   - Content type performance

4. **Geographic Insights**
   - District-wise sentiment trends
   - Regional issue identification
   - Urban vs rural engagement

## Hashtag Dictionary

Common hashtags by category:

### Political
- #TVK, #VijayForTN, #TVKVision2026, #NewPolitics, #CleanPolitics

### Issues
- #TNWaterCrisis, #StopNEET, #CauveryWater, #TNFishermen, #WaterScarcity

### Geographic
- #Chennai, #Coimbatore, #TamilNadu, #Madurai, #TNDevelopment

### Sentiment
- #SaveTamilNadu, #Progress, #FarmersFirst, #JobsForTN

## Mentions Dictionary

Common mentions by type:

### Government
- @TNGovt, @CMOTamilNadu, @ChennaiMetroWater

### Political
- @TVKOfficial, @ActorVijay, @TVKMedia

### Organizations
- @EducationMinTN, @CoastGuardIndia, @MEAIndia, @CauveryAuthority

## Troubleshooting

### Error: "No districts found"
```bash
# Run master data generation first
python manage.py generate_master_data
```

### Error: "No campaigns found"
```bash
# TVK campaigns needed for linking
python manage.py seed_campaigns
```

### Memory Issues
```bash
# Reduce batch size
python manage.py generate_social_posts --batch-size 100

# Or generate in smaller chunks
python manage.py generate_social_posts --count 5000
# Repeat 4 times
```

### Slow Generation
```bash
# Increase batch size
python manage.py generate_social_posts --batch-size 1000

# Skip SQL generation
python manage.py generate_social_posts  # (default, no --generate-sql flag)
```

## Data Quality

### Validation Checks
- ✅ All posts have valid timestamps (Nov 23-30, 2024)
- ✅ Sentiment scores within 0.0-1.0 range
- ✅ Engagement metrics realistic for tier
- ✅ Platform-specific post IDs and URLs
- ✅ Hashtags extracted from content + additional tags
- ✅ Geographic distribution matches Tamil Nadu demographics

### Realistic Patterns
- ✅ Time distribution matches human behavior (peak hours)
- ✅ Engagement follows power law (few viral, many low)
- ✅ Sentiment aligns with content type
- ✅ Platform multipliers reflect real-world usage
- ✅ Crisis content correlates with negative sentiment

## Future Enhancements

### Planned Features
- [ ] Multi-language support (Tamil + English)
- [ ] Reply thread generation
- [ ] Image URL attachment
- [ ] Video metadata
- [ ] Verified account indicators
- [ ] Retweet/quote tweet chains
- [ ] Trending hashtag boost
- [ ] Real-time API scraping integration

### Advanced Analytics
- [ ] Influencer network graphs
- [ ] Sentiment time series
- [ ] Viral prediction scoring
- [ ] Content clustering
- [ ] Fake news detection
- [ ] Bot account identification

## Related Commands

```bash
# Generate master data (districts, constituencies)
python manage.py generate_master_data

# Generate users (volunteers, booth agents)
python manage.py generate_users

# Generate campaigns
python manage.py seed_campaigns

# Aggregate analytics
python manage.py aggregate_analytics
```

## Support

For issues or questions:
1. Check Django logs: `backend/logs/django.log`
2. Verify database connection
3. Ensure sufficient disk space for SQL exports
4. Review statistics output for data quality

---

**Version**: 1.0
**Last Updated**: 2024-11-09
**Maintainer**: Pulse of People Development Team
