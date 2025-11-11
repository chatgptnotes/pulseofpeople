# 📊 CSV Import Tool for Wards & Polling Booths

## 🚀 Quick Start

### **Step 1: Prepare Your CSV Files**

Use the provided templates in `csv_templates/`:
- `wards_template.csv` - Example ward data
- `booths_template.csv` - Example booth data

Or create your own following the format below.

---

### **Step 2: Run the Import Script**

```bash
# Import wards only
node import_wards_booths.js --wards csv_data/wards.csv

# Import booths only
node import_wards_booths.js --booths csv_data/booths.csv

# Import both (expects csv_data/wards.csv and csv_data/booths.csv)
node import_wards_booths.js --all
```

---

### **Step 3: Run Generated SQL**

The script creates SQL files:
- `import_wards.sql`
- `import_booths.sql`

Copy the SQL and run in [Supabase SQL Editor](https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql/new)

---

## 📋 CSV Format Requirements

### **Wards CSV Format**

Required columns:
```
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level,literacy_rate
```

**Example:**
```csv
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level,literacy_rate
TN-AC-001,Anna Nagar Ward 1,1,TN-AC-001-W-001,25000,18500,12,urban,medium,85.5
TN-AC-001,Anna Nagar Ward 2,2,TN-AC-001-W-002,22000,16200,10,urban,medium,88.2
```

**Column Descriptions:**
| Column | Required | Type | Example | Notes |
|--------|----------|------|---------|-------|
| constituency_code | ✅ | Text | TN-AC-001 | Must match existing constituency |
| ward_name | ✅ | Text | Anna Nagar Ward 1 | Ward display name |
| ward_number | ✅ | Number | 1 | Ward number within constituency |
| ward_code | ✅ | Text | TN-AC-001-W-001 | Unique ward code |
| population | ⚪ | Number | 25000 | Total population |
| voter_count | ⚪ | Number | 18500 | Registered voters |
| total_booths | ⚪ | Number | 12 | Number of polling booths |
| urbanization | ⚪ | Text | urban | urban, semi-urban, rural |
| income_level | ⚪ | Text | medium | low, medium, high |
| literacy_rate | ⚪ | Number | 85.5 | Percentage (0-100) |

---

### **Booths CSV Format**

Required columns:
```
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,transgender_voters,accessible,parking_available,landmark
```

**Example:**
```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,transgender_voters,accessible,parking_available,landmark
TN-AC-001,TN-AC-001-W-001,001,Government High School Anna Nagar,"123 Main St, Anna Nagar, Chennai",13.0827,80.2707,1500,750,748,2,true,true,Near Anna Nagar Tower
```

**Column Descriptions:**
| Column | Required | Type | Example | Notes |
|--------|----------|------|---------|-------|
| constituency_code | ✅ | Text | TN-AC-001 | Must match existing constituency |
| ward_code | ⚪ | Text | TN-AC-001-W-001 | Links to ward (optional) |
| booth_number | ✅ | Text | 001 | Unique booth number in constituency |
| booth_name | ✅ | Text | Govt High School | Booth location name |
| address | ⚪ | Text | 123 Main St... | Full address |
| latitude | ⚪ | Decimal | 13.0827 | GPS latitude |
| longitude | ⚪ | Decimal | 80.2707 | GPS longitude |
| total_voters | ⚪ | Number | 1500 | Total registered voters |
| male_voters | ⚪ | Number | 750 | Male voters |
| female_voters | ⚪ | Number | 748 | Female voters |
| transgender_voters | ⚪ | Number | 2 | Transgender voters |
| accessible | ⚪ | Boolean | true | Wheelchair accessible |
| parking_available | ⚪ | Boolean | false | Has parking |
| landmark | ⚪ | Text | Near Tower | Nearby landmark |

---

## 🎯 Workflow

### **Workflow 1: Import Wards First, Then Booths**

```bash
# 1. Create wards CSV
# 2. Generate wards SQL
node import_wards_booths.js --wards csv_data/wards.csv

# 3. Import wards SQL in Supabase
# (Run import_wards.sql)

# 4. Create booths CSV
# 5. Generate booths SQL
node import_wards_booths.js --booths csv_data/booths.csv

# 6. Import booths SQL in Supabase
# (Run import_booths.sql)
```

**Why this order?**
- Booths can reference wards via `ward_code`
- Ensures data integrity

---

### **Workflow 2: Import Both Together**

```bash
# Place your CSV files in csv_data/ folder
csv_data/
  wards.csv
  booths.csv

# Generate both SQL files
node import_wards_booths.js --all

# Run both SQL files in Supabase
# 1. import_wards.sql (first)
# 2. import_booths.sql (second)
```

---

## 📁 File Structure

```
pulseofpeople/
├── csv_templates/              # Example CSV files
│   ├── wards_template.csv
│   └── booths_template.csv
├── csv_data/                   # Your actual data (create this)
│   ├── wards.csv
│   └── booths.csv
├── import_wards_booths.js      # Import script
├── import_wards.sql            # Generated SQL (wards)
├── import_booths.sql           # Generated SQL (booths)
└── CSV_IMPORT_README.md        # This file
```

---

## ✅ Data Validation

The script performs basic validation:

**Wards:**
- ✅ Constituency code must exist
- ✅ Ward code must be unique
- ✅ Handles special characters in names (apostrophes, etc.)

**Booths:**
- ✅ Constituency code must exist
- ✅ Booth number must be unique per constituency
- ✅ Ward code is optional (booths can exist without wards)
- ✅ Boolean fields (accessible, parking) converted correctly

---

## 🔧 Troubleshooting

### **Error: File not found**
```
❌ Error: File not found: csv_data/wards.csv
```
**Solution:** Create the CSV file or check the path

---

### **Error: Constituency not found**
```sql
ERROR: null value in column "constituency_id"
```
**Solution:**
- Check `constituency_code` in your CSV
- Verify constituency exists:
  ```sql
  SELECT code, name FROM constituencies
  WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  ORDER BY code;
  ```

---

### **Error: Duplicate ward code**
```sql
ERROR: duplicate key value violates unique constraint "wards_organization_id_code_key"
```
**Solution:**
- The script uses `ON CONFLICT DO UPDATE`, so this shouldn't happen
- If it does, check for duplicate `ward_code` in your CSV

---

### **Error: Special characters in names**
If you see SQL syntax errors with names containing apostrophes:
**Solution:** The script handles this automatically by escaping quotes

---

## 📊 Sample Data

Test the import with sample data:

```bash
# Use the provided templates
cp csv_templates/wards_template.csv csv_data/wards.csv
cp csv_templates/booths_template.csv csv_data/booths.csv

# Generate SQL
node import_wards_booths.js --all

# Check the generated files
ls -lh import_*.sql
```

---

## 🎯 Production Tips

### **1. Data Collection**
- Get official booth data from CEO offices
- Use Google Maps API for GPS coordinates
- Validate voter counts against official records

### **2. Batch Processing**
- Import constituency-by-constituency
- Verify each batch before proceeding
- Keep backup of CSV files

### **3. Data Updates**
- Script uses `ON CONFLICT DO UPDATE`
- Safe to re-run with updated data
- Timestamps automatically updated

### **4. Large Datasets**
- For 1000+ records, split into batches
- Import 100-200 wards at a time
- Monitor database performance

---

## 📈 Scaling

**Current Setup:**
- ✅ Handles 100s of wards/booths easily
- ✅ Single CSV file per import

**For Thousands:**
- Split CSV into batches (by district/region)
- Import sequentially
- Example:
  ```bash
  node import_wards_booths.js --wards csv_data/chennai_wards.csv
  node import_wards_booths.js --wards csv_data/coimbatore_wards.csv
  # etc.
  ```

---

## 🔗 Related Files

- **Schema:** `supabase/migrations/PHASE2_*.sql`
- **Constituencies:** Already imported (264 total)
- **Templates:** `csv_templates/`
- **Guide:** `WARDS_AND_BOOTHS_IMPORT_GUIDE.md`

---

## 💡 Next Steps

1. ✅ Create `csv_data/` folder
2. ✅ Add your ward/booth CSV files
3. ✅ Run import script
4. ✅ Verify data in Supabase
5. ✅ Test in frontend application

---

**Questions?** See `WARDS_AND_BOOTHS_IMPORT_GUIDE.md` for detailed information.

**Last Updated:** 2025-11-09
