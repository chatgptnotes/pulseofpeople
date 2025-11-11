# Sample Voter Data Generation

This script generates 50,000+ realistic voter records for testing and development purposes.

## Features

- 🇮🇳 **Realistic Indian Demographics**: Names, castes, religions, occupations
- 📊 **Intelligent Distribution**: Voters distributed across polling booths
- 🎯 **Sentiment Analysis**: Pre-assigned political sentiments and scores
- 📱 **Contact Information**: Phone numbers, emails (40% have phones, 20% have email)
- 🏷️ **Smart Tagging**: Auto-assigned tags based on demographics
- 📈 **Voting History**: Past election participation records
- 🔒 **Privacy Compliant**: Aadhaar numbers hashed (DPDP compliance)

## Prerequisites

1. **Python 3.8+** installed
2. **Supabase project** set up with Phase 1 & Phase 2 migrations applied
3. **Polling booths** created in database (at least 1 booth required)

## Setup

### 1. Install Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the scripts directory:

```bash
# Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key  # NOT the anon key!
```

**Important**: Use the **service_role** key (not anon key) from your Supabase project settings:
- Go to: Project Settings → API → service_role key

### 3. Verify Database Setup

Before running, ensure:
- ✅ Phase 1 migration applied (organizations, users tables exist)
- ✅ Phase 2 migration applied (polling_booths table exists with data)
- ✅ At least one polling booth created

Check booth count:
```sql
SELECT COUNT(*) FROM polling_booths WHERE is_active = true;
```

## Usage

### Basic Run (50,000 voters)

```bash
python generate_sample_voters.py
```

### Customize Configuration

Edit the script constants at the top:

```python
TOTAL_VOTERS = 50000   # Change total number of voters
BATCH_SIZE = 1000      # Adjust batch size for performance
ORGANIZATION_ID = '11111111-1111-1111-1111-111111111111'  # Target organization
```

### Run with Progress

```bash
python generate_sample_voters.py 2>&1 | tee generation.log
```

## Generated Data

### Voter Profile Includes:

**Identity**
- Voter ID Number (TN2020123456 format)
- EPIC Number (Electoral Card)
- Aadhaar Hash (privacy-compliant)

**Demographics**
- Full Name (realistic Indian names)
- Age: 18-80 (Gaussian distribution around 45)
- Gender: 52% Male, 47% Female, 1% Other
- Religion: Hindu (65%), Muslim (15%), Christian (8%), Other (12%)
- Caste Category: General (30%), OBC (40%), SC (20%), ST (10%)
- Education: From "No Formal Education" to "PhD"
- Occupation: 20 realistic occupations
- Income Range: 6 brackets

**Political**
- Sentiment: strong_support, support, neutral, oppose, strong_oppose, undecided
- Sentiment Score: -100 to +100
- Voter Category: core_supporter (35%), swing_voter (40%), opponent (25%)
- Preferred Party: Assigned based on sentiment
- Top Issues: 1-5 issues from 14 options

**Engagement**
- Contact Status: 30% contacted by party
- Contact Method: door_to_door, phone, whatsapp, event, rally
- Meeting Attendance: 0-10 meetings
- Rally Participation: 0-5 rallies

**Quality Metrics**
- Verified: 40% verified voters
- Data Quality Score: 40-100
- Consent Given: 60% given consent

**Tags** (Auto-assigned based on profile)
- senior_citizen, first_time_voter, youth, women, undecided
- educated, farmer, business_owner, influencer, minority

## Performance

- **Speed**: ~1,000 voters/second (depends on network)
- **Memory**: ~500MB peak (batched inserts)
- **Duration**: 50,000 voters in ~5-10 minutes

### Batch Size Tuning

- **Small Batches (500)**: Slower but more reliable
- **Medium Batches (1000)**: Balanced (recommended)
- **Large Batches (5000)**: Faster but may timeout

## Output Example

```
🚀 Starting voter data generation...
Target: 50,000 voters
Batch size: 1,000

📍 Fetching polling booths...
✅ Found 10 polling booths

📊 Distribution: ~5000 voters per booth

🏢 Booth 1/10: Polling Booth 1 (B0001)
   Generating 5,000 voters...
   ✓ Inserted 1,000/5,000 voters (1,000 total)
   ✓ Inserted 2,000/5,000 voters (2,000 total)
   ...
   ✓ Inserted 5,000/5,000 voters (5,000 total)

...

============================================================
✅ Voter generation complete!
Total voters inserted: 50,000

📊 Generating statistics...
Total records in database: 50,000

💡 Next steps:
  1. Verify data in Supabase dashboard
  2. Run: SELECT * FROM voters LIMIT 10;
  3. Check constituency stats: SELECT * FROM get_constituency_stats('constituency_id');
```

## Verification

### Check voter count by booth

```sql
SELECT
    pb.name,
    pb.booth_number,
    COUNT(v.id) as voter_count
FROM polling_booths pb
LEFT JOIN voters v ON v.polling_booth_id = pb.id
GROUP BY pb.id, pb.name, pb.booth_number
ORDER BY voter_count DESC;
```

### Check sentiment distribution

```sql
SELECT
    sentiment,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM voters
GROUP BY sentiment
ORDER BY count DESC;
```

### Check gender distribution

```sql
SELECT
    gender,
    COUNT(*) as count,
    AVG(age) as avg_age
FROM voters
GROUP BY gender;
```

### Get constituency statistics

```sql
SELECT * FROM get_constituency_stats('constituency-id-here');
```

## Troubleshooting

### Error: "No polling booths found"
- **Solution**: Run Phase 2 migration first to create polling booths

### Error: "Authentication failed"
- **Solution**: Check SUPABASE_SERVICE_KEY (use service_role key, not anon key)

### Error: "Timeout during insert"
- **Solution**: Reduce BATCH_SIZE from 1000 to 500

### Slow performance
- **Solutions**:
  - Increase BATCH_SIZE (if network is stable)
  - Run from server closer to Supabase region
  - Check Supabase dashboard for database load

## Cleanup

### Delete all generated voters

```sql
DELETE FROM voters WHERE organization_id = '11111111-1111-1111-1111-111111111111';
```

### Re-run with fresh data

```sql
-- Delete voters only
DELETE FROM voters;

-- Re-run script
python generate_sample_voters.py
```

## Data Quality

The script generates high-quality, realistic data:

✅ **Realistic names** from curated Indian names list
✅ **Age distribution** follows census patterns
✅ **Occupation-education correlation** (e.g., doctors are graduates)
✅ **Income-education correlation** (educated voters have higher income)
✅ **Sentiment logic** (supporters have positive scores, opponents negative)
✅ **Tag intelligence** (senior citizens are 60+, youth are <35)
✅ **Contact patterns** (influencers more likely to be contacted)
✅ **Privacy compliance** (Aadhaar hashed, consent tracked)

## License

MIT License - Free to use for testing and development

---

**Need help?** Check the main project README or create an issue.
