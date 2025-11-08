-- # Data Import Guide
## How to Import Real Tamil Nadu Constituency Data

**Last Updated**: 2025-11-07
**Status**: Ready for import

---

## Overview

This guide explains how to import complete, accurate constituency data for all 234 Tamil Nadu and 30 Pondicherry assembly constituencies into your database.

---

## Quick Start - Run Migrations First

### Step 1: Run All Migration Files in Order

```bash
cd /Users/murali/1backup/pulseofpeople6nov/voter

# 1. States table
psql $DATABASE_URL -f supabase/migrations/20251107_create_states_table.sql

# 2. Districts table
psql $DATABASE_URL -f supabase/migrations/20251107_create_districts_table.sql

# 3. Constituency master tables (already created)
psql $DATABASE_URL -f supabase/migrations/20251106_create_constituency_master.sql

# 4. Political parties
psql $DATABASE_URL -f supabase/migrations/20251108_create_political_parties.sql

# 5. Sample constituency data (optional - for testing)
psql $DATABASE_URL -f supabase/seeds/02_complete_constituencies_seed.sql
```

### Step 2: Verify Schema

```sql
-- Check all tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN (
    'states',
    'districts',
    'assembly_constituencies',
    'elected_members',
    'polling_booths',
    'political_parties',
    'political_alliances'
)
ORDER BY table_name;

-- Should return 7 tables
```

---

## Data Sources

### Official Government Sources

#### 1. **Election Commission of India (ECI)** 🏛️

**Main Website**: https://eci.gov.in

**Direct Links**:
- **2021 TN Election Results**: https://results.eci.gov.in/AcResultGenJune2021/statewiseS22.htm
- **Statistical Reports**: https://eci.gov.in/statistical-report/statistical-reports
- **Constituency Details**: https://eci.gov.in/delimitation/final-order

**What to Download**:
- Complete list of 234 constituencies
- Reservation status (SC/ST/General)
- 2021 election results (winner, votes, vote share)
- Parliamentary constituency mapping

#### 2. **Tamil Nadu Chief Electoral Officer** 📊

**Main Website**: https://www.elections.tn.gov.in

**Direct Links**:
- **Current MLA List**: https://www.elections.tn.gov.in/tamilnadu_mla.aspx
- **Constituency Information**: Available on CEO portal
- **Voter Statistics**: District-wise and constituency-wise

**What to Download**:
- Current MLA names and photos
- Constituency headquarters/addresses
- Voter demographics (age, gender breakdown)
- Polling booth lists (CSV downloads)

#### 3. **Tamil Nadu Legislative Assembly** 🏛️

**Main Website**: https://www.tn.gov.in/department/5

**What to Get**:
- Official MLA directory
- Contact information
- Constituency profiles

---

## Data Format Required

### For assembly_constituencies table

| Field | Type | Example | Source |
|-------|------|---------|--------|
| code | TEXT | 'TN001' | Auto-assign sequentially |
| constituency_number | INTEGER | 1 | From ECI list |
| name | TEXT | 'Gummidipoondi' | From ECI |
| name_tamil | TEXT | 'கும்மிடிப்பூண்டி' | From TN CEO website |
| state_code | TEXT | 'TN' | Fixed (TN or PY) |
| district_code | TEXT | 'TN33' | Map to districts table |
| reservation_type | TEXT | 'Scheduled Castes' | From ECI delimitation |
| parliamentary_constituency | TEXT | 'Thiruvallur (SC)' | From ECI |
| center_lat | DECIMAL | 13.4074 | Google Maps / OSM |
| center_lng | DECIMAL | 80.1119 | Google Maps / OSM |
| total_voters | INTEGER | 285000 | From TN CEO statistics |
| polling_booths | INTEGER | 285 | From TN CEO |

### For elected_members table

| Field | Type | Example | Source |
|-------|------|---------|--------|
| constituency_code | TEXT | 'TN001' | Link to constituency |
| member_name | TEXT | 'K. Selvam' | From 2021 results |
| political_party | TEXT | 'DMK' | From 2021 results |
| alliance | TEXT | 'DMK Alliance' | From coalition info |
| election_year | INTEGER | 2021 | Fixed |
| term_start | DATE | '2021-05-07' | Election result date |
| term_end | DATE | '2026-05-06' | 5 years from start |
| votes_received | INTEGER | 108523 | From ECI results |
| vote_percentage | DECIMAL | 52.3 | From ECI results |
| victory_margin | INTEGER | 15234 | Winner votes - Runner-up votes |
| total_valid_votes | INTEGER | 207500 | From ECI results |
| is_current_member | BOOLEAN | TRUE | TRUE for 2021 winners |

---

## Step-by-Step Import Process

### Method 1: Using Excel/Google Sheets (Easiest)

#### Step 1: Download and Organize Data

1. Go to ECI 2021 TN Results page
2. Download constituency-wise results (usually available as PDF or HTML)
3. Create a new Google Sheet or Excel file
4. Create columns matching the database fields

#### Step 2: Create Master Spreadsheet

**Template Structure**:
```
| Constituency# | Name | Tamil Name | District | Reservation | PC | Winner | Party | Votes | Vote% |
|--------------|------|------------|----------|-------------|-----|--------|-------|-------|-------|
| 1 | Gummidipoondi | கும்மிடிப்பூண்டி | Thiruvallur | SC | Thiruvallur | K. Selvam | DMK | 108523 | 52.3 |
```

#### Step 3: Add Geographic Data

For each constituency, use Google Maps:
1. Search "[Constituency Name] Tamil Nadu assembly"
2. Right-click on the constituency area center
3. Click on coordinates to copy
4. Add to your spreadsheet

#### Step 4: Generate SQL

Use this Excel formula in a new column:
```excel
="INSERT INTO assembly_constituencies (code, constituency_number, name, name_tamil, state_code, district_code, reservation_type, parliamentary_constituency, center_lat, center_lng) VALUES ('"&
"TN"&TEXT(A2,"000")&"', "&
A2&", '"&
B2&"', '"&
C2&"', 'TN', '"&
D2&"', '"&
E2&"', '"&
F2&"', "&
G2&", "&
H2&");"
```

#### Step 5: Export and Run

1. Copy all generated SQL INSERT statements
2. Save to a file: `03_full_constituencies_data.sql`
3. Run: `psql $DATABASE_URL -f supabase/seeds/03_full_constituencies_data.sql`

---

### Method 2: Using Python Script (Automated)

Create a Python script to scrape and import data:

```python
#!/usr/bin/env python3
"""
Import Tamil Nadu Constituency Data
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import psycopg2
from geopy.geocoders import Nominatim

# Database connection
conn = psycopg2.connect("your_database_url")
cur = conn.cursor()

# Scrape ECI results
def scrape_eci_results():
    url = "https://results.eci.gov.in/AcResultGenJune2021/partywiseresult-S22.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Parse table data
    # ... (implementation depends on HTML structure)

    return constituencies_data

# Get coordinates for constituency
def get_coordinates(constituency_name):
    geolocator = Nominatim(user_agent="tn_constituency_importer")
    location = geolocator.geocode(f"{constituency_name}, Tamil Nadu, India")
    if location:
        return location.latitude, location.longitude
    return None, None

# Insert constituency
def insert_constituency(data):
    query = """
    INSERT INTO assembly_constituencies (
        code, constituency_number, name, name_tamil, state_code,
        district_code, reservation_type, parliamentary_constituency,
        center_lat, center_lng
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (code) DO UPDATE SET
        name = EXCLUDED.name,
        center_lat = EXCLUDED.center_lat,
        center_lng = EXCLUDED.center_lng
    """
    cur.execute(query, data)
    conn.commit()

# Main execution
if __name__ == "__main__":
    constituencies = scrape_eci_results()

    for const in constituencies:
        lat, lng = get_coordinates(const['name'])
        const['lat'] = lat
        const['lng'] = lng
        insert_constituency(const)

    print(f"Imported {len(constituencies)} constituencies")

    cur.close()
    conn.close()
```

---

### Method 3: Manual Entry with Web Interface

If you prefer a UI-based approach:

1. Create an admin panel in your React app
2. Add a "Constituency Management" page
3. Create a form with all fields
4. Import constituencies one by one or via CSV upload
5. Use React Hook Form + Supabase client for insertions

---

## Quick Import - Pre-Made Data Files

### Download Community-Created Datasets

Check these sources for pre-formatted data:

1. **GitHub Repositories**:
   - Search: "Tamil Nadu constituencies JSON"
   - Look for election-related open-source projects
   - Example: India Assembly Elections dataset

2. **Kaggle Datasets**:
   - Search: "Indian Assembly Elections"
   - Download CSV files
   - Convert to SQL format

3. **Data.gov.in**:
   - Official Indian government open data portal
   - Search for electoral datasets

---

## Validation After Import

### Run These Queries to Verify

```sql
-- 1. Check total count
SELECT state_code, COUNT(*) as total
FROM assembly_constituencies
GROUP BY state_code;
-- Expected: TN=234, PY=30

-- 2. Check reservation distribution (TN)
SELECT
    reservation_type,
    COUNT(*) as count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) as percentage
FROM assembly_constituencies
WHERE state_code = 'TN'
GROUP BY reservation_type;
-- Expected: SC=44 (18.8%), ST=3 (1.3%), Unreserved=187 (79.9%)

-- 3. Check for missing data
SELECT
    code,
    name,
    CASE
        WHEN center_lat IS NULL THEN 'Missing coordinates'
        WHEN district_code IS NULL THEN 'Missing district'
        WHEN reservation_type IS NULL THEN 'Missing reservation type'
        ELSE 'Complete'
    END as status
FROM assembly_constituencies
WHERE center_lat IS NULL
   OR district_code IS NULL
   OR reservation_type IS NULL;
-- Expected: 0 rows (all data complete)

-- 4. Check current MLAs count
SELECT
    political_party,
    COUNT(*) as seats
FROM elected_members
WHERE is_current_member = TRUE
  AND election_year = 2021
GROUP BY political_party
ORDER BY seats DESC;
-- Expected: DMK=133, AIADMK=66, INC=18, etc.

-- 5. Verify party alliance totals
SELECT
    pp.alliance,
    SUM(pp.tn_mlas_2021) as total_seats
FROM political_parties pp
WHERE pp.alliance IS NOT NULL
GROUP BY pp.alliance;
-- Expected: DMK Alliance (INDIA) = 159, AIADMK Alliance (NDA) = 75

-- 6. Check geographic data integrity
SELECT COUNT(*) as constituencies_with_coordinates
FROM assembly_constituencies
WHERE center_point IS NOT NULL;
-- Should equal total constituencies (264)

-- 7. District-wise distribution
SELECT
    d.name as district,
    d.state_code,
    COUNT(ac.code) as constituencies
FROM districts d
LEFT JOIN assembly_constituencies ac ON d.code = ac.district_code
GROUP BY d.name, d.state_code
HAVING COUNT(ac.code) = 0;
-- Expected: 0 rows (all districts should have constituencies)
```

---

## Troubleshooting

### Problem 1: Coordinates Not Accurate

**Solution**: Use constituency headquarters or assembly hall location
```bash
# Use Google Maps API for bulk geocoding
# Or use geopy library in Python
pip install geopy
```

### Problem 2: Tamil Names Missing

**Solution**:
1. Visit TN CEO website (official Tamil names)
2. Use Google Translate API for bulk translation
3. Manual verification recommended for accuracy

### Problem 3: District Mapping Unclear

**Solution**:
```sql
-- List all districts with codes
SELECT code, name, name_tamil FROM districts WHERE state_code = 'TN' ORDER BY name;

-- Match constituency to district based on name similarity
-- Example: "Coimbatore North" belongs to district "Coimbatore" (TN04)
```

### Problem 4: Reservation Types Confusing

**Reference**:
- **SC (Scheduled Castes)**: 44 constituencies in TN
- **ST (Scheduled Tribes)**: 3 constituencies in TN (Bargur, Gudalur, Palani)
- **Unreserved (General)**: 187 constituencies in TN

Check official ECI delimitation order for exact list.

---

## Automated Import Script (Bash)

Save this as `import_constituencies.sh`:

```bash
#!/bin/bash

# Tamil Nadu Constituency Data Import Script
# Usage: ./import_constituencies.sh

set -e  # Exit on error

echo "🚀 Starting Tamil Nadu Constituency Data Import..."

# Check if database URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable not set"
    exit 1
fi

# Run migrations in order
echo "📦 Running migrations..."

echo "  1/4 Creating states table..."
psql $DATABASE_URL -f supabase/migrations/20251107_create_states_table.sql

echo "  2/4 Creating districts table..."
psql $DATABASE_URL -f supabase/migrations/20251107_create_districts_table.sql

echo "  3/4 Creating constituency tables..."
psql $DATABASE_URL -f supabase/migrations/20251106_create_constituency_master.sql

echo "  4/4 Creating political parties..."
psql $DATABASE_URL -f supabase/migrations/20251108_create_political_parties.sql

# Import seed data
echo "🌱 Importing seed data..."

echo "  - Importing constituency data..."
psql $DATABASE_URL -f supabase/seeds/02_complete_constituencies_seed.sql

# Validate data
echo "✅ Validating imported data..."

psql $DATABASE_URL -c "
SELECT
    'States' as entity, COUNT(*) as count FROM states
UNION ALL
SELECT
    'Districts', COUNT(*) FROM districts
UNION ALL
SELECT
    'Constituencies', COUNT(*) FROM assembly_constituencies
UNION ALL
SELECT
    'Political Parties', COUNT(*) FROM political_parties
UNION ALL
SELECT
    'Current MLAs', COUNT(*) FROM elected_members WHERE is_current_member = TRUE;
"

echo "✨ Import complete!"
echo ""
echo "Next steps:"
echo "  1. Review imported data in Supabase dashboard"
echo "  2. Import complete constituency list (all 264)"
echo "  3. Import polling booth data"
echo "  4. Add TVK party structure"
```

Make it executable:
```bash
chmod +x import_constituencies.sh
./import_constituencies.sh
```

---

## Next Steps After Import

### 1. Import Polling Booths (~70,000 records)

Download booth-level data from TN CEO:
- Go to https://www.elections.tn.gov.in
- Navigate to "Electoral Rolls" section
- Download booth-wise voter lists
- Extract booth names, numbers, addresses, and coordinates

### 2. Add Historical Election Data

Import results from previous elections (2016, 2011, 2006):
```sql
INSERT INTO elected_members (
    constituency_code, member_name, political_party, alliance,
    election_year, term_start, term_end, votes_received,
    vote_percentage, is_current_member
) VALUES ...
```

### 3. Add GeoJSON Boundaries

For map visualization:
1. Download constituency shapefiles from:
   - DataMeet India: https://github.com/datameet/indian-election-data
   - Election Commission GIS portal
2. Convert to GeoJSON format
3. Store in `geojson` column

### 4. Build API Services

Once data is imported, create TypeScript services:
```typescript
// src/services/api/constituencyService.ts
export const getConstituenciesByDistrict = async (districtCode: string) => {
    const { data, error } = await supabase
        .from('assembly_constituencies')
        .select('*')
        .eq('district_code', districtCode);
    return data;
};
```

---

## Summary

### What You Have Now ✅

- ✅ Complete database schema (states, districts, constituencies, MLAs, parties)
- ✅ Sample data for testing (Chennai, Coimbatore, Madurai constituencies)
- ✅ All TN political parties with 2021 results
- ✅ TVK party entry ready
- ✅ RLS policies configured
- ✅ Helper functions for spatial queries

### What You Need to Do ⏳

1. ⏳ Import complete 234 TN constituencies (use methods above)
2. ⏳ Import 30 Pondicherry constituencies
3. ⏳ Verify all data with validation queries
4. ⏳ Add polling booth data (optional for now, can load on-demand)
5. ⏳ Test geographic queries (nearby booths, district boundaries)

### Time Estimate

- **Quick Method** (using existing datasets): 2-4 hours
- **Manual Entry** (Excel + Google Maps): 8-12 hours
- **Automated Script** (Python): 4-6 hours initial setup, then automatic

---

## Resources

- **ECI Main Site**: https://eci.gov.in
- **TN CEO**: https://www.elections.tn.gov.in
- **2021 Results**: https://results.eci.gov.in/AcResultGenJune2021/statewiseS22.htm
- **Wikipedia**: https://en.wikipedia.org/wiki/2021_Tamil_Nadu_Legislative_Assembly_election
- **DataMeet**: https://github.com/datameet/indian-election-data

---

**Last Updated**: 2025-11-07
**Status**: Ready for data import
**Next Action**: Choose import method and execute
