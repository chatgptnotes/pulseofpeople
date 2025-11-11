# Quick Reference: generate_sentiment_data

## Quick Start

```bash
# Activate virtual environment
cd /Users/murali/Applications/pulseofpeople/backend
source venv/bin/activate

# Generate 50,000 records (default)
python manage.py generate_sentiment_data

# Generate custom amount
python manage.py generate_sentiment_data --count 100000
```

## Command Options

| Option | Default | Description |
|--------|---------|-------------|
| `--count` | 50000 | Number of records to generate |
| `--batch-size` | 1000 | Batch size for bulk creation |

## Real Crisis Scenarios (Nov 2024)

| Issue | % of Data | Sentiment Pattern | Key Districts |
|-------|-----------|-------------------|---------------|
| Water Crisis | 20% | 60% negative | Coimbatore, Chennai, Salem |
| Jobs/Employment | 18% | 45% negative | Urban centers |
| Agriculture | 12% | 55% negative | Delta region, Salem |
| NEET Opposition | 10% | 45% positive | Urban, students |
| Cauvery Dispute | 8% | 70% negative | Thanjavur, Tiruvarur |
| Healthcare | 8% | 35% negative | Urban centers |
| Education | 7% | 30% negative | Urban centers |
| Fishermen Rights | 5% | 60% negative | Coastal districts |
| Infrastructure | 5% | 30% negative | Statewide |
| Cyclone Relief | 4% | 50% negative | Cuddalore, Viluppuram |
| Other | 3% | 25% negative | Statewide |

## Data Distributions

### Source Distribution
- Direct Feedback: 40%
- Social Media: 35%
- Field Report: 20%
- Survey: 5%

### Geographic Distribution
- Urban districts (7): 50% of records
- Semi-urban/affected (15): 30% of records
- Rural districts (16): 20% of records

### Time Period
- **Range**: September 1 - November 30, 2024 (90 days)
- **Pattern**: More recent = more volume (exponential distribution)
- **Peak Hours**: 7-9am, 12-2pm, 6-9pm IST
- **Weekdays**: 30% higher volume than weekends

## Sentiment Scoring

| Score Range | Polarity | Distribution |
|-------------|----------|--------------|
| 0.0 - 0.4 | Negative | Beta(2, 5) |
| 0.4 - 0.6 | Neutral | Beta(2, 2) |
| 0.6 - 1.0 | Positive | Beta(5, 2) |

**Confidence**: Normal distribution (μ=0.75, σ=0.15)

## Prerequisites

```bash
# Required commands to run first
python manage.py seed_political_data

# Optional but recommended
python manage.py import_electoral_data
```

## Expected Output Statistics

```
Total Records Created: 50,000
Date Range: Sept 1, 2024 - Nov 30, 2024

Issue Breakdown:
  Water Supply: ~10,000 (20%)
  Jobs: ~9,000 (18%)
  Agriculture: ~6,000 (12%)
  ...

Polarity Breakdown:
  Negative: ~37% (18,500)
  Neutral: ~32% (16,000)
  Positive: ~31% (15,500)

Source Breakdown:
  Direct Feedback: ~20,000 (40%)
  Social Media: ~17,500 (35%)
  Field Report: ~10,000 (20%)
  Survey: ~2,500 (5%)

Top Districts:
  1. Chennai: ~16.5%
  2. Coimbatore: ~14.2%
  3. Madurai: ~10.0%
  ...

Geographic Coverage: 38/38 districts
```

## Performance

- **Generation Speed**: ~1,000-1,500 records/second
- **Duration**: 30-45 seconds for 50,000 records
- **Memory**: ~50-100 MB peak usage
- **Storage**: ~15-20 MB for 50,000 records

## Troubleshooting

| Error | Solution |
|-------|----------|
| "State not found" | Run `seed_political_data` first |
| "No districts found" | Run `seed_political_data` first |
| "No issue categories" | Run `seed_political_data` first |
| Slow performance | Increase `--batch-size` to 2000 |
| Memory errors | Decrease `--batch-size` to 500 |

## Real-World Context

This generator simulates authentic Tamil Nadu political sentiment based on:

1. **Water Crisis**: 26 districts affected, Chennai groundwater depleted (46/51 firkas over-exploited)
2. **Cyclone Fengal**: Devastated 2.11 lakh hectares agricultural land (Nov 2024)
3. **Fishermen Arrests**: 530 arrests by Sri Lankan Navy in 2024
4. **Cauvery Dispute**: Delta region protests (Aug-Oct 2024)
5. **NEET Protests**: Statewide opposition movement

## Integration Points

Generated data integrates with:
- Sentiment Analysis Dashboard
- Geographic Heatmaps (Mapbox)
- Trend Analysis Charts
- Issue Prioritization Reports
- Voter Segment Analytics
- Campaign Planning Tools

## Testing

```bash
# Test with small dataset first
python manage.py generate_sentiment_data --count 1000

# Verify data in Django admin or shell
python manage.py shell
>>> from api.models import SentimentData
>>> SentimentData.objects.count()
>>> SentimentData.objects.values('polarity').annotate(count=Count('id'))
```

## Next Steps

After generating data:

1. Run analytics aggregation: `python manage.py aggregate_analytics`
2. Test dashboard visualization
3. Verify geographic distribution on maps
4. Test filtering by date, district, issue
5. Export reports for analysis

---

**Quick Reference Version**: 1.0
**Last Updated**: 2024-11-09
