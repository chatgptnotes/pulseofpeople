# GitHub Electoral Data Import Guide

Get 20,000+ polling booths from GitHub in 1-2 hours! 🚀

## 🎯 What This Does

This automated script:
- ✅ Downloads 989K polling station dataset from GitHub
- ✅ Extracts Tamil Nadu + Puducherry data (~20,000-25,000 booths)
- ✅ Converts to Pulse of People CSV format
- ✅ Includes GPS coordinates, infrastructure data, voter counts
- ✅ Removes duplicates and validates data
- ✅ Generates ready-to-upload CSV files

**Source:** https://github.com/in-rolls/poll-station-metadata
**Data Period:** 2018-2019 (can be updated with 2025 PDFs later)

---

## ⚡ Quick Start (Copy-Paste Commands)

### Step 1: Install Dependencies (First Time Only)

```bash
# Install git (if not already installed)
git --version || brew install git

# Install 7z archive tool
7z || brew install p7zip
```

### Step 2: Run the Conversion Script

```bash
cd /Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/data_collection

python3 convert_github_data.py
```

**Wait time:**
- Download: 5-10 minutes (depends on internet speed)
- Extraction: 2-3 minutes (processing 989K records)
- Conversion: 1-2 minutes (filtering & formatting)
- **Total: 10-15 minutes**

### Step 3: Review Generated Files

```bash
# Check output directory
ls -lh converted_csvs/

# View first 10 rows
head -n 10 converted_csvs/polling_booths_from_github.csv

# Count total rows
wc -l converted_csvs/polling_booths_from_github.csv
```

### Step 4: Upload to System

**Option A: Via Web Interface** (Recommended)
1. Login: http://localhost:5173
2. Click **Maps** icon in left sidebar
3. Select **Upload Booths**
4. Choose constituency from dropdown
5. Upload: `converted_csvs/polling_booths_from_github.csv`
6. Review import summary
7. Click "Confirm Import"

**Option B: Via API** (Bulk Upload)
```bash
# Get your JWT token first (login via web)
TOKEN="your_jwt_token_here"

curl -X POST http://localhost:8000/api/geography/polling-booths/bulk-import/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@converted_csvs/polling_booths_from_github.csv"
```

---

## 📊 What Data You'll Get

### Polling Booth Fields (21 columns)

| Field | Example | Description |
|-------|---------|-------------|
| `code` | TN-AC001-B001 | Unique booth identifier |
| `booth_number` | 001 | Booth number within constituency |
| `name` | Government Higher Secondary School | Polling station name |
| `address` | 123 Anna Nagar Main Rd, Chennai 600040 | Full address |
| `latitude` | 13.0827 | GPS latitude (-90 to 90) |
| `longitude` | 80.2707 | GPS longitude (-180 to 180) |
| `total_voters` | 1523 | Total registered voters |
| `male_voters` | 765 | Male voters |
| `female_voters` | 758 | Female voters |
| `transgender_voters` | 0 | Transgender voters |
| `building_type` | Government School | Type of building |
| `is_accessible` | true | Wheelchair accessible |
| `has_electricity` | true | Electricity available |
| `has_water` | true | Drinking water available |
| `has_toilet` | true | Toilet facilities |
| `state` | Tamil Nadu | State name |
| `district` | Chennai | District name |
| `ac_name` | Chennai Central | Assembly constituency |
| `ac_no` | 007 | AC number |
| `data_source` | GitHub: in-rolls/poll-station-metadata | Source |
| `data_date` | 2018-2019 | Data collection period |

### Sample Data

```csv
code,booth_number,name,address,latitude,longitude,total_voters,male_voters,female_voters,transgender_voters,building_type,is_accessible,has_electricity,has_water,has_toilet,state,district,ac_name,ac_no,data_source,data_date
TN-AC007-B001,001,Corporation High School Anna Nagar,"123 Anna Nagar Main Road, Chennai 600040",13.0827,80.2707,1523,765,758,0,Government School,true,true,true,true,Tamil Nadu,Chennai,Chennai Central,007,GitHub: in-rolls/poll-station-metadata,2018-2019
```

---

## 📁 Directory Structure After Running

```
data_collection/
├── convert_github_data.py          # ← The script
├── github_data/                    # ← Downloaded data (auto-created)
│   └── poll-station-metadata/
│       ├── poll_station_metadata_all.7z  (compressed: ~150 MB)
│       └── poll_station_metadata_all.csv (extracted: ~500 MB)
└── converted_csvs/                 # ← YOUR OUTPUT FILES
    ├── polling_booths_from_github.csv   (~5-10 MB, 20K+ rows)
    └── conversion_summary.txt           (statistics report)
```

---

## 🔍 Expected Results

### Statistics

| Metric | Expected Value |
|--------|----------------|
| Total records in dataset | 989,000+ |
| Tamil Nadu records | 18,000-22,000 |
| Puducherry records | 2,000-3,000 |
| **Final CSV rows** | **20,000-25,000** |
| Duplicates removed | 100-500 |
| Invalid records skipped | 50-200 |
| GPS coordinates coverage | 70-80% |
| Infrastructure data coverage | 90%+ |

### Tamil Nadu Coverage

**Districts with data:**
- Chennai (16 constituencies, ~3,000 booths)
- Coimbatore (~1,500 booths)
- Madurai (~1,200 booths)
- Tiruchirappalli (~1,000 booths)
- Salem (~1,000 booths)
- ...and 29 more districts

**Total:** 234 constituencies, ~20,000 booths

### Puducherry Coverage

**Constituencies:** 30 (all union territory)
**Booths:** ~2,000-3,000

---

## ✅ Data Quality Checks

The script automatically:
- ✅ Validates GPS coordinates (-90 to 90 lat, -180 to 180 lon)
- ✅ Checks voter counts (male + female + trans = total)
- ✅ Removes duplicates (by unique booth code)
- ✅ Skips invalid records (missing name, zero voters)
- ✅ Normalizes text (trim whitespace, handle "NA" values)
- ✅ Generates summary statistics

---

## 🆘 Troubleshooting

### Error: "git: command not found"

**Solution:**
```bash
brew install git
```

### Error: "7z: command not found"

**Solution:**
```bash
brew install p7zip
```

### Error: "Permission denied"

**Solution:**
```bash
chmod +x convert_github_data.py
```

### Error: "ModuleNotFoundError: No module named 'xyz'"

**Solution:** Python standard library only, no pip installs needed!

### Script runs but no output

**Check:**
```bash
# Verify extraction completed
ls -lh github_data/poll-station-metadata/poll_station_metadata_all.csv

# Check conversion output
ls -lh converted_csvs/
```

### CSV has 0 rows

**Possible causes:**
- Extraction failed (check github_data/ directory)
- Wrong state filter (edit TARGET_STATES in script)

---

## 🔄 Re-running the Script

The script is **idempotent** - safe to run multiple times:

- ✅ **Already cloned?** Skips re-cloning
- ✅ **Already extracted?** Skips re-extraction
- ✅ **Conversion only?** Runs in <1 minute

To force fresh download:
```bash
rm -rf github_data/
python3 convert_github_data.py
```

---

## 📈 Next Steps After Import

### 1. Verify Data in System

**Via Web Interface:**
1. Login: http://localhost:5173
2. Navigate: Maps → Booths List
3. Check filters work (district, constituency, voters)
4. Try search by booth name
5. View on map (Maps → Booths Map)

**Via API:**
```bash
# List all booths (paginated)
curl http://localhost:8000/api/geography/polling-booths/ \
  -H "Authorization: Bearer $TOKEN"

# Filter by state
curl http://localhost:8000/api/geography/polling-booths/?state=Tamil%20Nadu \
  -H "Authorization: Bearer $TOKEN"

# Count total
curl http://localhost:8000/api/geography/polling-booths/count/ \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Update with 2025 Data (Optional)

**For key constituencies:**
1. Download 2025 PDFs from CEO Tamil Nadu
2. Extract booth lists using Tabula
3. Compare with GitHub data
4. Update changed booths only

**Script available:** `download_tn_booths.py`

### 3. Add Missing GPS Coordinates

**Using Geocoding API:**
```python
# Install geopy
pip install geopy

# Geocode addresses
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="pulseofpeople")
location = geolocator.geocode("123 Anna Nagar, Chennai")
print(location.latitude, location.longitude)
```

### 4. Verify Data Integrity

**Run validation queries:**
```sql
-- Check for duplicate booth numbers
SELECT constituency_id, booth_number, COUNT(*)
FROM polling_booths
GROUP BY constituency_id, booth_number
HAVING COUNT(*) > 1;

-- Check voter count consistency
SELECT * FROM polling_booths
WHERE male_voters + female_voters + transgender_voters != total_voters;

-- Check GPS coordinate validity
SELECT * FROM polling_booths
WHERE latitude < -90 OR latitude > 90
   OR longitude < -180 OR longitude > 180;
```

---

## 🎯 Success Criteria

Your import is successful if:

- ✅ 20,000+ booths imported
- ✅ 95%+ have complete names and addresses
- ✅ 70%+ have GPS coordinates
- ✅ All voter counts are positive
- ✅ No duplicates found
- ✅ Data appears in Booths List page
- ✅ Maps display booth locations
- ✅ Filters and search work correctly

---

## 📊 Sample Conversion Output

```
================================================================================
 🗳️  GitHub Electoral Data Converter - Pulse of People
================================================================================
 Source: in-rolls/poll-station-metadata
 Target: Tamil Nadu + Puducherry
 Expected: ~20,000-25,000 polling booths
================================================================================

📋 Checking dependencies...
  ✅ git installed
  ✅ 7z installed

📥 Step 1: Cloning GitHub repository...
  ✅ Cloned to: github_data/poll-station-metadata

📦 Step 2: Extracting archive...
  📦 Extracting poll_station_metadata_all.7z (this may take 2-3 minutes)...
  ✅ Extracted: github_data/poll-station-metadata/poll_station_metadata_all.csv

🔄 Step 3: Converting data to Pulse of People format...
  📖 Reading: github_data/poll-station-metadata/poll_station_metadata_all.csv
  🎯 Filtering for: Tamil Nadu, Puducherry
  📊 Processed: 21,456 booths...

  💾 Writing polling booths CSV...
  ✅ Created: converted_csvs/polling_booths_from_github.csv
  📊 Total booths: 21,456

================================================================================
 📊 CONVERSION SUMMARY
================================================================================

📥 Input Data:
  Total records processed: 989,124
  Tamil Nadu records: 19,234
  Puducherry records: 2,222

📤 Output Data:
  Wards identified: 264
  Polling booths created: 21,456
  Duplicates removed: 234
  Invalid records skipped: 76

📁 Output Files:
  polling_booths_from_github.csv
    Size: 8.45 MB
    Rows: 21,456
    Location: /Users/murali/.../converted_csvs/polling_booths_from_github.csv

✅ Next Steps:
  1. Review the CSV file
  2. Login to your Pulse of People system
  3. Navigate to: Maps → Upload Booths
  4. Upload the CSV file
  5. Verify imported data in Booths List

================================================================================
```

---

## 🔗 Useful Links

- **GitHub Repository:** https://github.com/in-rolls/poll-station-metadata
- **Dataset Documentation:** https://github.com/in-rolls/poll-station-metadata/blob/master/README.md
- **Data Schema:** See polling_booths_template.csv
- **Upload Interface:** http://localhost:5173 → Maps → Upload Booths
- **API Reference:** docs/API_REFERENCE.md

---

## 📞 Support

**Script issues:**
- Check `conversion_summary.txt` for detailed stats
- Review error messages in terminal
- Ensure dependencies are installed (git, 7z)

**Data quality issues:**
- Original dataset is from 2018-2019
- Update with 2025 PDFs for current data
- Use geocoding API for missing GPS

**Upload issues:**
- Check CSV format matches template
- Ensure constituency_id exists in database
- Verify JWT token is valid

---

**Last Updated:** 2025-11-09
**Version:** 1.0
**Estimated Time:** 10-15 minutes
**Output:** 20,000+ polling booths ready to import 🎉
