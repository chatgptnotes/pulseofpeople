# 🚀 Quick Reference: Wards & Booths Import

## ✅ What's Ready

### **1. CSV Templates**
📁 `csv_templates/`
- ✅ `wards_template.csv` - Sample ward data (5 wards)
- ✅ `booths_template.csv` - Sample booth data (5 booths)

### **2. Import Script**
📄 `import_wards_booths.js`
- ✅ Converts CSV → SQL
- ✅ Handles wards and booths
- ✅ Auto-lookups constituency/ward IDs
- ✅ Tested and working

### **3. Documentation**
- ✅ `CSV_IMPORT_README.md` - Comprehensive guide
- ✅ `WARDS_AND_BOOTHS_IMPORT_GUIDE.md` - Strategy guide

### **4. Sample Data (Ready to Import)**
📁 `csv_data/`
- ✅ `wards.csv` - 5 sample wards
- ✅ `booths.csv` - 5 sample booths

### **5. Generated SQL (Ready to Run)**
- ✅ `import_wards.sql` - Ready for Supabase
- ✅ `import_booths.sql` - Ready for Supabase

---

## 🎯 3-Step Import Process

### **Step 1: Prepare CSV Data**

**Option A:** Use sample data (for testing)
```bash
# Already done! Files are in csv_data/
csv_data/wards.csv
csv_data/booths.csv
```

**Option B:** Create your own data
```bash
# Edit the CSV files
nano csv_data/wards.csv
nano csv_data/booths.csv
```

---

### **Step 2: Generate SQL**

```bash
# Generate both wards and booths SQL
node import_wards_booths.js --all

# Or generate individually:
node import_wards_booths.js --wards csv_data/wards.csv
node import_wards_booths.js --booths csv_data/booths.csv
```

**Output:**
- ✅ `import_wards.sql` created
- ✅ `import_booths.sql` created

---

### **Step 3: Import to Supabase**

1. Open [Supabase SQL Editor](https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql/new)

2. **Import Wards First:**
   - Open `import_wards.sql`
   - Copy all contents
   - Paste in SQL Editor
   - Click **RUN**
   - Verify: Should show "5 wards imported"

3. **Import Booths Second:**
   - Open `import_booths.sql`
   - Copy all contents
   - Paste in SQL Editor
   - Click **RUN**
   - Verify: Should show "5 booths imported"

---

## 📊 CSV Format Quick Reference

### **Wards CSV**
```csv
constituency_code,ward_name,ward_number,ward_code,population,voter_count,total_booths,urbanization,income_level,literacy_rate
TN-AC-001,Anna Nagar Ward 1,1,TN-AC-001-W-001,25000,18500,12,urban,medium,85.5
```

**Required:**
- constituency_code (must exist in constituencies table)
- ward_name
- ward_code (unique)

**Optional but recommended:**
- ward_number, population, voter_count, etc.

---

### **Booths CSV**
```csv
constituency_code,ward_code,booth_number,booth_name,address,latitude,longitude,total_voters,male_voters,female_voters,transgender_voters,accessible,parking_available,landmark
TN-AC-001,TN-AC-001-W-001,001,Government High School,"123 Main St",13.0827,80.2707,1500,750,748,2,true,true,Near Tower
```

**Required:**
- constituency_code (must exist)
- booth_number (unique per constituency)
- booth_name

**Optional but recommended:**
- ward_code (links to ward)
- address, GPS coords, voter counts, etc.

---

## 🔧 Common Tasks

### **Add More Wards**
1. Edit `csv_data/wards.csv`
2. Add new rows
3. Run: `node import_wards_booths.js --wards csv_data/wards.csv`
4. Import generated `import_wards.sql` in Supabase

### **Add More Booths**
1. Edit `csv_data/booths.csv`
2. Add new rows
3. Run: `node import_wards_booths.js --booths csv_data/booths.csv`
4. Import generated `import_booths.sql` in Supabase

### **Update Existing Data**
- Script uses `ON CONFLICT DO UPDATE`
- Safe to re-import with updated CSV
- Existing records will be updated

### **Import Large Dataset**
- Split into batches of 100-200 records
- Import sequentially
- Example:
  ```bash
  node import_wards_booths.js --wards csv_data/batch1_wards.csv
  # (import SQL)
  node import_wards_booths.js --wards csv_data/batch2_wards.csv
  # (import SQL)
  ```

---

## ✅ Verification Queries

### **Check Wards Count**
```sql
SELECT
  c.code,
  c.name,
  COUNT(w.id) as ward_count,
  SUM(w.total_booths) as total_booths
FROM constituencies c
LEFT JOIN wards w ON w.constituency_id = c.id
WHERE c.organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY c.id
HAVING COUNT(w.id) > 0
ORDER BY c.code;
```

### **Check Booths Count**
```sql
SELECT
  c.code,
  c.name,
  COUNT(pb.id) as booth_count,
  SUM(pb.total_voters) as total_voters
FROM constituencies c
LEFT JOIN polling_booths pb ON pb.constituency_id = c.id
WHERE c.organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY c.id
HAVING COUNT(pb.id) > 0
ORDER BY c.code;
```

### **View Imported Data**
```sql
-- View wards
SELECT * FROM wards
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
ORDER BY code;

-- View booths
SELECT * FROM polling_booths
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
ORDER BY constituency_id, booth_number;
```

---

## 💡 Tips

1. **Start Small:** Import sample data first to test
2. **Validate CSV:** Check for typos in constituency codes
3. **Backup:** Keep original CSV files
4. **Incremental:** Import constituency-by-constituency
5. **GPS Coords:** Use Google Maps to get lat/long
6. **Voter Data:** Get official numbers from CEO office

---

## 📂 File Locations

```
pulseofpeople/
├── csv_templates/              ← Sample CSV files
│   ├── wards_template.csv
│   └── booths_template.csv
├── csv_data/                   ← Your data files
│   ├── wards.csv
│   └── booths.csv
├── import_wards_booths.js      ← Import script
├── import_wards.sql            ← Generated SQL (wards)
├── import_booths.sql           ← Generated SQL (booths)
├── CSV_IMPORT_README.md        ← Full documentation
└── QUICK_REFERENCE_WARDS_BOOTHS.md  ← This file
```

---

## 🎯 Next Steps

**To import sample data RIGHT NOW:**
```bash
# 1. Generate SQL (already done)
node import_wards_booths.js --all

# 2. Go to Supabase SQL Editor
open https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql/new

# 3. Run import_wards.sql
# 4. Run import_booths.sql
# 5. Done! 5 wards + 5 booths imported
```

**To add real data:**
1. Collect ward/booth data (Excel/CSV)
2. Format according to CSV templates
3. Save to `csv_data/` folder
4. Run import script
5. Import generated SQL

---

**Questions?** See `CSV_IMPORT_README.md` for detailed help.

**Last Updated:** 2025-11-09
