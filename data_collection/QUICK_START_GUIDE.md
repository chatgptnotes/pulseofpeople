# Quick Start Guide - Polling Booth Data Collection

**For**: Agent 2 (Data Acquisition & Processing Specialist)
**Date**: 2025-11-09
**Status**: Ready to Begin Data Collection

---

## Mission Recap
Collect **25,000-30,000 polling booths** across **264 constituencies** (234 Tamil Nadu + 30 Puducherry) with complete ward and voter information.

---

## Files Created

1. **DATA_COLLECTION_REPORT.md** (824 lines)
   - Comprehensive research findings
   - All data sources with URLs
   - Complete acquisition strategy
   - Data schema and validation plan

2. **DATA_SOURCES_SUMMARY.csv** (25 sources)
   - Quick reference table of all sources
   - Priority rankings
   - Access methods and formats

3. **Directory Structure**:
   ```
   data_collection/
   ├── raw/
   │   ├── tamil_nadu/
   │   └── puducherry/
   └── processed/
   ```

---

## Recommended Starting Point (Choose One)

### Option A: GitHub Pre-Parsed Data (FASTEST - 2 hours)
**Best for**: Quick proof of concept, research access available

```bash
# 1. Clone polling station metadata
gh repo clone in-rolls/poll-station-metadata
cd poll-station-metadata

# 2. Extract data (requires 7zip)
7z x poll_station_metadata_all.7z

# 3. Filter for Tamil Nadu
grep "Tamil Nadu" poll_station_metadata_all.csv > tamil_nadu_booths.csv

# 4. Move to project directory
mv tamil_nadu_booths.csv /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/data_collection/raw/
```

**Expected Output**: ~20,000-25,000 Tamil Nadu booths with metadata (latitude, longitude, facilities)

**Data Fields**: State, district, AC, booth name, lat/long, officials, infrastructure details

---

### Option B: Official ECI Portal (CURRENT DATA - Manual)
**Best for**: Most up-to-date 2025 electoral rolls

**Steps**:
1. Visit: https://voters.eci.gov.in/download-eroll
2. Select State: Tamil Nadu (S22)
3. Select District: Chennai (start with Priority 1)
4. Select AC: 001 (Gummidipoondi) or 014 (Villivakkam)
5. Select Language: English
6. Select all Parts (polling stations)
7. Enter CAPTCHA
8. Download PDFs

**Save to**: `/Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/data_collection/raw/tamil_nadu/district_chennai/AC001_PDFs/`

**Parse PDFs**:
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("AC001_Part001.pdf") as pdf:
    for page in pdf.pages:
        table = page.extract_table()
        df = pd.DataFrame(table[1:], columns=table[0])
        df.to_csv("AC001_Part001.csv", index=False)
```

---

### Option C: Direct PDF Downloads from TN CEO (BATCH)
**Best for**: Bulk downloads without captcha

**URL Pattern**:
```
https://www.elections.tn.gov.in/Web/pslist/ac001.pdf
https://www.elections.tn.gov.in/Web/pslist/ac002.pdf
...
https://www.elections.tn.gov.in/Web/pslist/ac234.pdf
```

**Batch Download**:
```bash
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/data_collection/raw/tamil_nadu/

# Download all 234 constituencies
for i in {1..234}; do
  ac_num=$(printf "%03d" $i)
  wget "https://www.elections.tn.gov.in/Web/pslist/ac${ac_num}.pdf" -O "AC${ac_num}_pslist.pdf"
  sleep 2  # Rate limiting
done
```

---

## Priority 1 Target: Chennai (16 Constituencies)

**AC Numbers**: 001-016
**Estimated Booths**: ~3,000
**Time Estimate**: 3-4 hours (download + parse)

| AC No. | Constituency Name | Approx Booths |
|--------|-------------------|---------------|
| 001 | Gummidipoondi | 180 |
| 002 | Ponneri | 190 |
| 003 | Tiruvottiyur | 200 |
| 004 | Dr. Radhakrishnan Nagar | 220 |
| 005 | Perambur | 210 |
| 006 | Kolathur | 200 |
| 007 | Villivakkam | 180 |
| 008 | Thiru. Vi. Ka. Nagar | 190 |
| 009 | Egmore | 170 |
| 010 | Royapuram | 180 |
| 011 | Harbour | 160 |
| 012 | Chepauk - Thiruvallikeni | 150 |
| 013 | Thousand Lights | 180 |
| 014 | Anna Nagar | 200 |
| 015 | Virugambakkam | 190 |
| 016 | Saidapet | 180 |

---

## Data Schema (Target CSV)

**File**: `polling_booths_master.csv`

**Required Columns** (23 total):
```
state, district, assembly_constituency_number, assembly_constituency_name,
polling_station_number, polling_station_name, polling_station_address,
part_number, ward_number, ward_name, latitude, longitude,
voters_male, voters_female, voters_third_gender, voters_total,
building_type, accessible_for_disabled, electricity_available,
water_available, toilet_available, data_source, data_collection_date, notes
```

**Minimum Required** (can enrich later):
- state, district, assembly_constituency_number, assembly_constituency_name
- polling_station_number, polling_station_name, polling_station_address
- voters_male, voters_female, voters_total
- data_source, data_collection_date

---

## Validation Checklist (After Each Batch)

- [ ] All booths have unique IDs (AC_number + booth_number)
- [ ] Voter counts: Male + Female + Third Gender = Total
- [ ] No booths with 0 total voters
- [ ] At least 90% booths have addresses
- [ ] Constituency totals match official ECI statistics
- [ ] No duplicate booth entries

**Run Validation Script**:
```python
import pandas as pd

df = pd.read_csv("polling_booths_master.csv")

# Check totals
print(f"Total booths: {len(df)}")
print(f"Total voters: {df['voters_total'].sum()}")

# Check for duplicates
duplicates = df.duplicated(subset=['assembly_constituency_number', 'polling_station_number'])
print(f"Duplicate booths: {duplicates.sum()}")

# Check completeness
print(f"Missing addresses: {df['polling_station_address'].isna().sum()}")
print(f"Missing voter counts: {df['voters_total'].isna().sum()}")
```

---

## Tools Recommended

### PDF Parsing
```bash
pip install pdfplumber tabula-py pandas openpyxl
```

### Web Scraping (if needed)
```bash
pip install selenium webdriver-manager beautifulsoup4 requests
```

### Data Processing
```bash
pip install pandas numpy great-expectations dedupe
```

### Geocoding (optional)
```bash
pip install geopy googlemaps
```

---

## Expected Deliverables

### Checkpoint 1 (After Chennai - 16 AC)
- [ ] 3,000+ booths collected
- [ ] Data validation passed
- [ ] Sample uploaded to `/data_collection/processed/chennai_sample.csv`
- [ ] Progress report updated

### Checkpoint 2 (After Priority 1 Cities - 54 AC)
- [ ] 9,000+ booths collected
- [ ] Data quality report generated
- [ ] Ready to scale to remaining constituencies

### Final Deliverable (All 264 AC)
- [ ] 25,000+ booths collected
- [ ] `polling_booths_master.csv` complete
- [ ] `constituencies_master.csv` (264 rows)
- [ ] `wards_master.csv` (if available)
- [ ] Data quality report with 95%+ completeness

---

## Troubleshooting

### Issue: PDF parsing fails
**Solution**: Check if PDF is searchable (not scanned image)
```bash
pdftotext sample.pdf test.txt
cat test.txt  # Should show readable text
```
If empty, use OCR:
```bash
sudo apt install tesseract-ocr
tesseract sample.pdf output.txt
```

### Issue: ECI portal blocks automation
**Solution**:
1. Add delays between requests (5-10 seconds)
2. Use rotating proxies
3. Fall back to manual downloads for critical constituencies

### Issue: Missing GPS coordinates
**Solution**: Geocode addresses later using:
```python
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="pulseofpeople")
location = geolocator.geocode("Corporation Primary School, Villivakkam, Chennai 600049")
print(location.latitude, location.longitude)
```

---

## Time Estimates

| Task | Time (Solo) | Time (Team of 5) |
|------|-------------|------------------|
| Chennai (16 AC) | 4 hours | 1 hour |
| Priority 1 (54 AC) | 12 hours | 3 hours |
| All TN (234 AC) | 40 hours | 10 hours |
| Puducherry (30 AC) | 3 hours | 1 hour |
| Validation & Cleanup | 8 hours | 2 hours |
| **TOTAL** | **63 hours** | **17 hours** |

---

## Success Metrics (Target)

- **Total Booths**: 25,000+ (Target: 27,000)
- **Completeness**: 95%+ (All key fields populated)
- **Accuracy**: 98%+ (Verified against official sources)
- **Constituencies**: 264/264 (100%)
- **Geocoding**: 80%+ (GPS coordinates available)

---

## Contact & Support

**Questions?** Refer to:
- Full Report: `DATA_COLLECTION_REPORT.md`
- Source List: `DATA_SOURCES_SUMMARY.csv`
- Tamil Nadu CEO: ceo@tn.gov.in | 1800 4252 1950

---

**Good luck with data collection!**

**Next Update Expected**: After Checkpoint 1 (Chennai - 16 constituencies)
