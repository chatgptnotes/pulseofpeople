# 🏛️ Wards and Polling Booths Import Guide

## 📊 Data Hierarchy

```
Organization (TVK)
  └── Constituency (264 total: 234 TN + 30 Puducherry)
        └── Ward (Multiple per constituency)
              └── Polling Booth (Multiple per ward)
```

---

## 📋 Table Schemas

### **Wards Table**
```sql
wards (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    constituency_id UUID NOT NULL,       -- Links to constituencies table

    -- Basic Info
    name VARCHAR(255) NOT NULL,          -- Ward name (e.g., "Anna Nagar Ward 1")
    code VARCHAR(50) NOT NULL,           -- Unique code (e.g., "TN-AC-001-W-001")
    ward_number INTEGER,                 -- Ward number within constituency

    -- Geographic Info
    boundaries JSONB,                    -- GeoJSON polygon for ward boundaries
    geom GEOGRAPHY(POLYGON, 4326),       -- PostGIS geometry (auto-populated)

    -- Demographics
    population INTEGER,
    voter_count INTEGER DEFAULT 0,
    total_booths INTEGER DEFAULT 0,
    demographics JSONB DEFAULT '{}'::jsonb,
    income_level VARCHAR(50),            -- low, medium, high
    urbanization VARCHAR(50),            -- urban, semi-urban, rural
    literacy_rate DECIMAL(5, 2),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

### **Polling Booths Table**
```sql
polling_booths (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL,
    constituency_id UUID NOT NULL,       -- Links to constituencies
    ward_id UUID,                        -- Optional: Links to wards

    -- Booth Identity
    booth_number VARCHAR(50) NOT NULL,   -- Official booth number (e.g., "001", "002A")
    name VARCHAR(255) NOT NULL,          -- Booth name (e.g., "Government High School")

    -- Location
    address TEXT,                        -- Full address
    latitude DECIMAL(10, 8),             -- GPS coordinates
    longitude DECIMAL(11, 8),
    location GEOGRAPHY(POINT, 4326),     -- PostGIS point (auto-populated)
    landmark TEXT,                       -- Nearby landmark

    -- Voter Demographics
    total_voters INTEGER DEFAULT 0,
    male_voters INTEGER DEFAULT 0,
    female_voters INTEGER DEFAULT 0,
    transgender_voters INTEGER DEFAULT 0,

    -- Accessibility & Facilities
    accessible BOOLEAN DEFAULT false,    -- Wheelchair accessible
    parking_available BOOLEAN DEFAULT false,
    facilities JSONB DEFAULT '{}'::jsonb,

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
)
```

---

## 🎯 Recommended Import Approach

### **Option 1: Comprehensive Official Data** ⭐ BEST FOR ACCURACY

**Source:** Tamil Nadu CEO Office / Puducherry CEO Office

**Data Format:** Excel/CSV files from Election Commission

**Steps:**
1. Download official ward and booth data from CEO websites
2. Convert to CSV format
3. Create import scripts to load into database
4. Validate data quality

**Pros:**
- ✅ Official, accurate data
- ✅ Complete voter counts
- ✅ Verified locations

**Cons:**
- ⚠️ Requires manual data collection
- ⚠️ May need data cleaning

---

### **Option 2: Incremental/Phased Import** ⭐ BEST FOR GETTING STARTED

**Approach:** Import data constituency-by-constituency as you collect it

**Steps:**
1. Start with high-priority constituencies (e.g., Chennai, Coimbatore)
2. Import wards first, then booths
3. Gradually expand coverage

**Pros:**
- ✅ Can start immediately
- ✅ Easier to manage and validate
- ✅ Flexible

**Cons:**
- ⚠️ Incomplete initial coverage

---

### **Option 3: CSV Bulk Upload via Admin UI** ⭐ BEST FOR EASE

**Approach:** Create a CSV upload feature in the admin panel

**Steps:**
1. Prepare CSV templates for wards and booths
2. Upload via admin UI
3. System validates and imports

**Pros:**
- ✅ User-friendly
- ✅ No SQL knowledge required
- ✅ Can update data easily

**Cons:**
- ⚠️ Requires building upload UI first

---

## 📄 CSV Templates

### **Wards CSV Template**
```csv
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level
TN-AC-001,Anna Nagar Ward 1,1,TN-AC-001-W-001,25000,18500,12,urban,medium
TN-AC-001,Anna Nagar Ward 2,2,TN-AC-001-W-002,22000,16200,10,urban,medium
TN-AC-002,Kilpauk Ward 1,1,TN-AC-002-W-001,30000,22000,15,urban,high
```

### **Polling Booths CSV Template**
```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,accessible,landmark
TN-AC-001,TN-AC-001-W-001,001,Government High School Anna Nagar,"123 Main St, Anna Nagar",13.0827,80.2707,1500,750,750,true,Near Anna Nagar Tower
TN-AC-001,TN-AC-001-W-001,002,Corporation Primary School,"456 Park Rd, Anna Nagar",13.0850,80.2720,1400,700,700,false,Opposite Park
```

---

## 🛠️ SQL Import Template

### **Import Wards (with constituency lookup)**

```sql
-- Example: Import wards for one constituency
INSERT INTO wards (
    organization_id,
    constituency_id,
    name,
    code,
    ward_number,
    population,
    voter_count,
    total_booths,
    urbanization,
    income_level
)
SELECT
    '11111111-1111-1111-1111-111111111111'::uuid,  -- TVK org ID
    c.id,                                           -- Look up constituency ID
    'Anna Nagar Ward 1',
    'TN-AC-001-W-001',
    1,
    25000,
    18500,
    12,
    'urban',
    'medium'
FROM constituencies c
WHERE c.code = 'TN-AC-001'
  AND c.organization_id = '11111111-1111-1111-1111-111111111111';
```

### **Import Polling Booths (with ward lookup)**

```sql
-- Example: Import booths for one ward
INSERT INTO polling_booths (
    organization_id,
    constituency_id,
    ward_id,
    booth_number,
    name,
    address,
    latitude,
    longitude,
    total_voters,
    male_voters,
    female_voters,
    accessible,
    landmark
)
SELECT
    '11111111-1111-1111-1111-111111111111'::uuid,
    c.id,
    w.id,
    '001',
    'Government High School Anna Nagar',
    '123 Main St, Anna Nagar, Chennai - 600040',
    13.0827,
    80.2707,
    1500,
    750,
    750,
    true,
    'Near Anna Nagar Tower'
FROM constituencies c
JOIN wards w ON w.constituency_id = c.id
WHERE c.code = 'TN-AC-001'
  AND w.code = 'TN-AC-001-W-001'
  AND c.organization_id = '11111111-1111-1111-1111-111111111111';
```

---

## 📊 Data Sources

### **Tamil Nadu**
- **Official:** Tamil Nadu CEO Office - https://www.tn.gov.in/ceo
- **Voter Data:** https://ceotnelection.gov.in
- **Booth Info:** Electoral rolls published before elections

### **Puducherry**
- **Official:** Puducherry CEO Office
- **Voter Data:** https://ceopuducherry.py.gov.in

### **Alternative Sources**
- **MyNeta.info** - Constituency and booth-level data
- **Election Commission of India** - https://eci.gov.in
- **Existing databases/datasets** - Academic/NGO sources

---

## 🚀 Quick Start: Import Sample Data

I can create a sample import with:
- **5 constituencies** (Chennai-based)
- **20-30 wards** (4-6 per constituency)
- **100-150 booths** (5-7 per ward)

This gives you:
1. Working data to test the system
2. Template for importing more data
3. Understanding of data structure

**Would you like me to:**
1. ✅ Create sample ward/booth data for testing?
2. ✅ Create a CSV-to-SQL import script?
3. ✅ Build an admin UI upload feature?
4. ✅ All of the above?

---

## 📝 Best Practice Workflow

### **Phase 1: Setup & Testing**
1. Import sample wards/booths for 5 constituencies
2. Test the UI with this data
3. Validate data structure

### **Phase 2: Priority Constituencies**
1. Identify high-priority constituencies (e.g., major cities)
2. Collect official data for these constituencies
3. Import via CSV or SQL

### **Phase 3: Full Coverage**
1. Systematically import remaining constituencies
2. Use bulk CSV upload or batched SQL imports
3. Validate completeness

---

## 🎯 Recommended Next Steps

1. **Immediate:** Create sample data for testing (I can do this now)
2. **Short-term:** Build CSV upload UI in admin panel
3. **Long-term:** Partner with Election Commission or NGOs for official data

**What would you like me to help with first?**

---

**Last Updated:** 2025-11-09
**Status:** 🟢 Ready to import wards and booths
