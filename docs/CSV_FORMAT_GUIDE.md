# CSV Format Guide: Wards and Polling Booths

## Table of Contents
1. [Overview](#overview)
2. [Wards CSV Format](#wards-csv-format)
3. [Polling Booths CSV Format](#polling-booths-csv-format)
4. [Data Formats and Validation](#data-formats-and-validation)
5. [Example CSV Files](#example-csv-files)
6. [Validation Rules](#validation-rules)
7. [Error Messages Explained](#error-messages-explained)
8. [Tips and Best Practices](#tips-and-best-practices)

---

## Overview

This guide provides detailed specifications for CSV files used to import ward and polling booth data into the Pulse of People platform.

**Key Requirements:**
- Files must be saved as CSV (Comma Separated Values)
- UTF-8 encoding required
- First row must contain column headers (exact names)
- No empty rows between data
- Maximum file size: 50 MB

**Supported Workflows:**
1. Create new records (INSERT)
2. Update existing records (UPDATE) - match by code
3. Bulk import (thousands of rows)

---

## Wards CSV Format

### Required Columns

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `constituency_code` | String(50) | ✅ Yes | Must match existing constituency code | `TN-AC-001` |
| `ward_name` | String(255) | ✅ Yes | Official ward name | `Anna Nagar Ward 1` |
| `ward_number` | Integer | ✅ Yes | Sequential number within constituency | `1` |
| `ward_code` | String(50) | ✅ Yes | Unique ward identifier | `TN-AC-001-W-001` |
| `population` | Integer | ❌ No | Total population | `25000` |
| `voter_count` | Integer | ❌ No | Registered voters | `18500` |
| `total_booths` | Integer | ❌ No | Number of polling booths | `12` |
| `urbanization` | String(50) | ❌ No | Urban classification | `urban` |
| `income_level` | String(50) | ❌ No | Economic classification | `medium` |

### Optional Columns

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `literacy_rate` | Decimal(5,2) | Percentage literacy | `85.50` |
| `boundaries` | JSON | GeoJSON polygon | See GeoJSON example below |
| `demographics` | JSON | Demographic breakdown | `{"age_groups": {...}}` |

### Ward Code Format

**Standard Format:** `{STATE}-AC-{CONST_NUM}-W-{WARD_NUM}`

**Examples:**
- `TN-AC-001-W-001` (Tamil Nadu, Constituency 1, Ward 1)
- `TN-AC-234-W-025` (Tamil Nadu, Constituency 234, Ward 25)
- `PY-AC-001-W-003` (Puducherry, Constituency 1, Ward 3)

**Rules:**
- STATE: 2-letter code (TN, PY)
- CONST_NUM: 3-digit zero-padded constituency number
- WARD_NUM: 3-digit zero-padded ward number
- Must be globally unique

### CSV Template - Wards

```csv
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level
TN-AC-001,Anna Nagar Ward 1,1,TN-AC-001-W-001,25000,18500,12,urban,medium
TN-AC-001,Anna Nagar Ward 2,2,TN-AC-001-W-002,22000,16200,10,urban,medium
TN-AC-001,Anna Nagar Ward 3,3,TN-AC-001-W-003,28000,20500,14,urban,high
TN-AC-002,Kilpauk Ward 1,1,TN-AC-002-W-001,30000,22000,15,urban,high
TN-AC-002,Kilpauk Ward 2,2,TN-AC-002-W-002,18000,13500,9,semi-urban,medium
```

**Download Template:** `csv_templates/wards_template.csv`

---

## Polling Booths CSV Format

### Required Columns

| Column Name | Data Type | Required | Description | Example |
|-------------|-----------|----------|-------------|---------|
| `constituency_code` | String(50) | ✅ Yes | Must match existing constituency | `TN-AC-001` |
| `ward_code` | String(50) | ❌ No* | Ward code (optional if no wards) | `TN-AC-001-W-001` |
| `booth_number` | String(50) | ✅ Yes | Official booth number | `001` or `001A` |
| `booth_name` | String(255) | ✅ Yes | Official booth name | `Government High School` |
| `address` | Text | ✅ Yes | Full address | `123 Main St, Anna Nagar` |
| `latitude` | Decimal(10,8) | ✅ Yes | GPS latitude (decimal degrees) | `13.08270000` |
| `longitude` | Decimal(11,8) | ✅ Yes | GPS longitude (decimal degrees) | `80.27070000` |
| `total_voters` | Integer | ✅ Yes | Total registered voters | `1500` |
| `male_voters` | Integer | ❌ No | Male voters | `750` |
| `female_voters` | Integer | ❌ No | Female voters | `750` |
| `accessible` | Boolean | ❌ No | Wheelchair accessible | `true` or `false` |
| `landmark` | Text | ❌ No | Nearby landmark | `Near Anna Nagar Tower` |

*Note: `ward_code` is optional if your constituency doesn't use wards

### Optional Columns

| Column Name | Data Type | Description | Example |
|-------------|-----------|-------------|---------|
| `transgender_voters` | Integer | Third gender voters | `0` |
| `parking_available` | Boolean | Parking facility | `true` |
| `facilities` | JSON | Additional facilities | `{"toilets": true, "ramp": true}` |
| `is_active` | Boolean | Currently active booth | `true` |

### Booth Number Format

**Flexible Formats:**
- Numeric: `001`, `002`, `003`
- Alphanumeric: `001A`, `001B`, `002A`
- Prefix: `AC001-001`, `AC001-002`
- Custom: Any format up to 50 characters

**Best Practice:** Use official Election Commission booth numbers

### GPS Coordinates

**Latitude (India Range):**
- Minimum: `8.0` (southernmost point)
- Maximum: `37.0` (northernmost point)
- Decimal places: 6-8 recommended for accuracy

**Longitude (India Range):**
- Minimum: `68.0` (westernmost point)
- Maximum: `97.0` (easternmost point)
- Decimal places: 6-8 recommended for accuracy

**Example Coordinates:**
- Chennai: `13.0827, 80.2707`
- Coimbatore: `11.0168, 76.9558`
- Madurai: `9.9252, 78.1198`
- Puducherry: `11.9416, 79.8083`

**Tools to Find Coordinates:**
- Google Maps: Right-click → "What's here?"
- GPS device: Use decimal degrees format
- Geocoding API: Convert addresses to coordinates

### CSV Template - Polling Booths

```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,accessible,landmark
TN-AC-001,TN-AC-001-W-001,001,Government High School Anna Nagar,"123 Main St, Anna Nagar, Chennai - 600040",13.08270000,80.27070000,1500,750,750,true,Near Anna Nagar Tower
TN-AC-001,TN-AC-001-W-001,002,Corporation Primary School Anna Nagar,"456 Park Rd, Anna Nagar, Chennai - 600040",13.08500000,80.27200000,1400,700,700,false,Opposite Corporation Park
TN-AC-001,TN-AC-001-W-001,003,Community Hall Anna Nagar,"789 Lake View, Anna Nagar, Chennai - 600040",13.08900000,80.27500000,1600,800,800,true,Next to Anna Nagar Lake
TN-AC-001,TN-AC-001-W-002,004,Panchayat Union Primary School,"321 Temple St, Anna Nagar, Chennai - 600040",13.09200000,80.27800000,1550,775,775,true,Behind Sri Temple
TN-AC-001,TN-AC-001-W-002,005,Government Girls School,"654 Market Rd, Anna Nagar, Chennai - 600040",13.09500000,80.28100000,1450,725,725,false,Near Market
```

**Download Template:** `csv_templates/booths_template.csv`

---

## Data Formats and Validation

### String/Text Fields

**Rules:**
- No line breaks within fields (use spaces instead)
- Enclose in double quotes if contains commas: `"123 Main St, Chennai"`
- Maximum length varies by column (see tables above)
- UTF-8 encoding for special characters (Tamil, etc.)

**Examples:**
```csv
# Correct
ward_name,address
Anna Nagar Ward 1,"123 Main St, Anna Nagar"
அண்ணா நகர் வார்டு 1,"456 Park Rd, Chennai"

# Incorrect (address has unquoted comma)
Anna Nagar Ward 1,123 Main St, Anna Nagar
```

### Integer Fields

**Rules:**
- Whole numbers only (no decimals, no commas)
- Positive values (≥ 0)
- No thousand separators

**Examples:**
```csv
# Correct
population,voter_count,total_booths
25000,18500,12
1000,750,3

# Incorrect
25,000,18500,12  # Has comma separator
25000.5,18500,12  # Has decimal
```

### Decimal Fields

**Rules:**
- Use period (`.`) as decimal separator
- Maximum precision varies by field
- No thousand separators

**Examples:**
```csv
# Correct
latitude,longitude,literacy_rate
13.08270000,80.27070000,85.50
11.01680000,76.95580000,78.25

# Incorrect
13.082,70000,80.270,70000,85.50  # Too many decimals
13,0827,80,2707,85.50  # Comma separator
```

### Boolean Fields

**Accepted Values:**

| True | False |
|------|-------|
| `true` | `false` |
| `TRUE` | `FALSE` |
| `1` | `0` |
| `yes` | `no` |
| `YES` | `NO` |

**Examples:**
```csv
# All valid
accessible,parking_available,is_active
true,false,true
TRUE,FALSE,1
yes,no,YES
1,0,1
```

### Enumerated Fields

#### Urbanization

**Valid Values:** `urban`, `semi-urban`, `rural`

**Case-insensitive:** `URBAN`, `Urban`, `urban` all accepted

```csv
# Correct
urbanization
urban
semi-urban
rural

# Incorrect
urbanization
city  # Invalid value
suburban  # Use semi-urban
```

#### Income Level

**Valid Values:** `low`, `medium`, `high`

```csv
# Correct
income_level
low
medium
high

# Incorrect
income_level
poor  # Use low
rich  # Use high
```

### JSON Fields

**Format:** Valid JSON string (optional)

**Examples:**

**Demographics:**
```json
{
  "age_groups": {
    "18-25": 5000,
    "26-35": 7000,
    "36-50": 8000,
    "51+": 5500
  },
  "religions": {
    "hindu": 18000,
    "muslim": 3000,
    "christian": 2500,
    "other": 500
  }
}
```

**Facilities:**
```json
{
  "toilets": true,
  "wheelchair_ramp": true,
  "drinking_water": true,
  "parking_spaces": 10
}
```

**In CSV:**
```csv
ward_code,demographics
TN-AC-001-W-001,"{""age_groups"": {""18-25"": 5000}}"
```

**Note:** JSON in CSV requires:
- Entire JSON wrapped in double quotes
- Internal double quotes escaped with `""`

**Recommendation:** Leave JSON fields empty initially, add via UI later

---

## Example CSV Files

### Example 1: Minimal Wards CSV

```csv
constituency_code,ward_name,ward_number,ward_code
TN-AC-001,Ward 1,1,TN-AC-001-W-001
TN-AC-001,Ward 2,2,TN-AC-001-W-002
TN-AC-001,Ward 3,3,TN-AC-001-W-003
```

### Example 2: Complete Wards CSV

```csv
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level,literacy_rate
TN-AC-001,Anna Nagar Ward 1,1,TN-AC-001-W-001,25000,18500,12,urban,medium,85.50
TN-AC-001,Anna Nagar Ward 2,2,TN-AC-001-W-002,22000,16200,10,urban,medium,83.20
TN-AC-001,Anna Nagar Ward 3,3,TN-AC-001-W-003,28000,20500,14,urban,high,90.15
```

### Example 3: Minimal Booths CSV

```csv
constituency_code,booth_number,booth_name,address,latitude,longitude,total_voters
TN-AC-001,001,Govt School,"123 Main St",13.0827,80.2707,1500
TN-AC-001,002,Community Hall,"456 Park Rd",13.0850,80.2720,1400
```

### Example 4: Complete Booths CSV

```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,transgender_voters,accessible,parking_available,landmark
TN-AC-001,TN-AC-001-W-001,001,Government High School Anna Nagar,"123 Main St, Anna Nagar, Chennai - 600040",13.08270000,80.27070000,1500,750,748,2,true,true,Near Anna Nagar Tower
TN-AC-001,TN-AC-001-W-001,002,Corporation Primary School,"456 Park Rd, Anna Nagar, Chennai - 600040",13.08500000,80.27200000,1400,700,698,2,false,false,Opposite Corporation Park
```

### Example 5: Multi-Constituency Import

```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,accessible,landmark
TN-AC-001,TN-AC-001-W-001,001,School A,"Address A",13.0827,80.2707,1500,750,750,true,Landmark A
TN-AC-001,TN-AC-001-W-001,002,School B,"Address B",13.0850,80.2720,1400,700,700,false,Landmark B
TN-AC-002,TN-AC-002-W-001,001,School C,"Address C",13.1000,80.2800,1600,800,800,true,Landmark C
TN-AC-002,TN-AC-002-W-001,002,School D,"Address D",13.1020,80.2850,1550,775,775,true,Landmark D
```

---

## Validation Rules

### Pre-Import Validation

The system performs these checks **before** importing:

#### Wards Validation

1. **File Format**
   - ✅ File is CSV format
   - ✅ UTF-8 encoding
   - ✅ First row has headers

2. **Required Columns**
   - ✅ All required columns present
   - ✅ Column names exact match (case-sensitive)

3. **Data Integrity**
   - ✅ `constituency_code` exists in system
   - ✅ `ward_code` is unique (INSERT) or exists (UPDATE)
   - ✅ `ward_number` is positive integer
   - ✅ `population` ≥ `voter_count` (if both provided)

4. **Data Types**
   - ✅ Numbers are valid integers/decimals
   - ✅ Booleans are valid true/false values
   - ✅ Enums match allowed values

#### Booths Validation

1. **File Format** (same as wards)

2. **Required Columns** (same as wards)

3. **Data Integrity**
   - ✅ `constituency_code` exists
   - ✅ `ward_code` exists (if provided)
   - ✅ `booth_number` unique within constituency
   - ✅ GPS coordinates within India range
   - ✅ `male_voters + female_voters + transgender_voters = total_voters`

4. **Geographic Validation**
   - ✅ Latitude: 8.0 to 37.0
   - ✅ Longitude: 68.0 to 97.0
   - ✅ Coordinates not in water (optional check)

### Post-Import Validation

After successful import, the system:

1. **Updates Counts**
   - Updates ward `total_booths` count
   - Updates constituency booth counts

2. **Generates PostGIS Data**
   - Creates `location` point from lat/long
   - Creates `geom` polygon from boundaries (if provided)

3. **Triggers Notifications**
   - Sends confirmation email
   - Logs audit trail

---

## Error Messages Explained

### Common Error Messages

#### "File format not recognized"

**Cause:** File is not a valid CSV
**Solution:**
- Save as CSV (not Excel, not TXT)
- Use UTF-8 encoding
- Check for binary/hidden characters

#### "Missing required column: {column_name}"

**Cause:** CSV doesn't have required column
**Solution:**
- Add missing column to CSV
- Check spelling (case-sensitive)
- Ensure first row has headers

#### "Constituency not found: {code}"

**Cause:** Constituency code doesn't exist in system
**Solution:**
- Verify constituency code is correct
- Import constituencies first
- Check for typos (case-sensitive)

#### "Duplicate ward code: {code}"

**Cause:** Ward code already exists (for INSERT)
**Solution:**
- Use unique ward code
- Or update existing record (system auto-detects)

#### "Ward not found: {code}"

**Cause:** Ward code doesn't exist (for booth import)
**Solution:**
- Import wards first
- Check ward code spelling
- Verify ward was imported successfully

#### "Invalid GPS coordinates at row {n}"

**Cause:** Lat/long outside valid range
**Solution:**
- Check latitude: 8.0 to 37.0
- Check longitude: 68.0 to 97.0
- Ensure decimal format (not DMS)
- Verify coordinates not swapped

#### "Voter count mismatch at row {n}"

**Cause:** `male + female + transgender ≠ total`
**Solution:**
- Recalculate totals
- Check for data entry errors
- Ensure all fields are numbers

#### "Invalid value for {field}: {value}"

**Cause:** Value doesn't match allowed enum
**Solution:**
- For `urbanization`: use urban/semi-urban/rural
- For `income_level`: use low/medium/high
- For `accessible`: use true/false

#### "Booth number already exists: {number}"

**Cause:** Duplicate booth number in same constituency
**Solution:**
- Use unique booth numbers
- Or update existing booth

### Warning Messages

**Warnings don't stop import, but should be reviewed:**

#### "Population less than voter count at row {n}"

**Cause:** `population < voter_count`
**Impact:** Data inconsistency
**Action:** Verify data, update if needed

#### "No GPS coordinates provided at row {n}"

**Cause:** Latitude/longitude empty
**Impact:** Booth won't appear on map
**Action:** Add coordinates later via UI

#### "No ward assigned to booth at row {n}"

**Cause:** `ward_code` is empty
**Impact:** Booth linked to constituency only
**Action:** Assign ward later if needed

#### "Unusually high voter count at row {n}"

**Cause:** `total_voters > 5000` (threshold)
**Impact:** None (just a flag)
**Action:** Verify count is correct

---

## Tips and Best Practices

### Before You Start

1. **Plan Your Data Structure**
   - Decide on ward numbering scheme
   - Choose booth number format
   - Standardize naming conventions

2. **Collect Official Data**
   - Get data from Election Commission
   - Use official booth names/numbers
   - Verify GPS coordinates

3. **Prepare Your Tools**
   - Use Excel/Google Sheets for editing
   - Keep backups of original data
   - Test with small sample first

### Creating CSV Files

1. **Use Templates**
   - Download provided templates
   - Keep column order consistent
   - Don't rename headers

2. **Data Entry**
   - Enter data row by row
   - Copy-paste from official sources
   - Use formulas for calculations (voter totals)

3. **Save Properly**
   - File → Save As → CSV (Comma delimited)
   - Choose UTF-8 encoding
   - Don't use "CSV UTF-8" (Excel) - use regular CSV

### Validating Before Upload

1. **Check Required Fields**
   - All required columns filled
   - No empty rows
   - No extra spaces

2. **Verify Data**
   - Constituency codes match exactly
   - Ward codes are unique
   - Booth numbers are unique per constituency
   - GPS coordinates are reasonable

3. **Test Import**
   - Upload small sample (10 rows) first
   - Review validation results
   - Fix errors before uploading full file

### During Upload

1. **Monitor Progress**
   - Watch progress bar
   - Note any warnings
   - Download error report if needed

2. **Review Results**
   - Check import summary
   - Verify counts match expected
   - Look for skipped rows

3. **Handle Errors**
   - Download error report
   - Fix errors in original CSV
   - Re-upload corrected file

### After Upload

1. **Verify on Map**
   - Check booths appear on map
   - Verify locations are correct
   - Check ward boundaries (if uploaded)

2. **Data Quality Check**
   - Spot-check random samples
   - Verify voter counts
   - Check for duplicate entries

3. **Update as Needed**
   - Fix any errors via UI
   - Or re-upload corrected CSV
   - Document changes

### Common Workflows

**Workflow 1: New Constituency Setup**
```
1. Verify constituency exists in system
2. Prepare wards CSV
3. Upload wards
4. Verify wards on map
5. Prepare booths CSV
6. Upload booths
7. Verify booths on map
8. Add boundaries (optional)
```

**Workflow 2: Update Existing Data**
```
1. Export current data
2. Make changes in Excel
3. Save as CSV
4. Upload (system auto-updates)
5. Verify changes
```

**Workflow 3: Large-Scale Import**
```
1. Split data into chunks (5000 rows each)
2. Upload chunk 1
3. Verify and fix errors
4. Upload chunk 2
5. Repeat until complete
6. Final verification
```

### Troubleshooting Tips

**If upload fails:**
1. Check file size (< 50 MB)
2. Verify CSV format (not Excel)
3. Check encoding (UTF-8)
4. Remove empty rows
5. Validate required columns
6. Test with smaller sample

**If booths don't appear on map:**
1. Verify GPS coordinates
2. Check latitude/longitude not swapped
3. Ensure coordinates in decimal degrees
4. Zoom in closer (booths appear at ward level)
5. Clear browser cache

**If data seems wrong:**
1. Export and review
2. Compare with original source
3. Check for data transformation errors
4. Re-upload if needed

---

## Additional Resources

- **Sample CSV Files**: `/csv_templates/` directory
- **API Documentation**: `API_REFERENCE.md`
- **User Guide**: `USER_GUIDE_WARDS_BOOTHS.md`
- **Support**: support@pulseofpeople.com

---

**Last Updated**: November 9, 2025
**Version**: 1.0
**For**: Pulse of People Platform
