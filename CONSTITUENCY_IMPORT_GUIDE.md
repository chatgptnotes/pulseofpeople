# 🗳️ Complete Constituency Import Guide

## 📊 Overview

This guide will help you import all **264 constituencies** for TVK:
- **Tamil Nadu**: 234 Assembly constituencies (in 4 batches)
- **Pondicherry**: 30 Assembly constituencies (single file)

---

## ✅ Step 1: Import Pondicherry (30 constituencies)

### File Location
```
IMPORT_ALL_CONSTITUENCIES.sql
```

### Instructions
1. Open the file `IMPORT_ALL_CONSTITUENCIES.sql`
2. Copy ALL contents (Ctrl+A, Ctrl+C)
3. Go to Supabase SQL Editor:
   ```
   https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql/new
   ```
4. Paste the SQL and click **RUN**
5. Wait for completion (should take ~5 seconds)

### Expected Result
```
✅ Inserted 30 Pondicherry constituencies

| state       | constituencies | sc | st | general |
|-------------|----------------|----|----|---------|
| Puducherry  | 30             | 7  | 0  | 23      |
```

---

## ✅ Step 2: Import Tamil Nadu (234 constituencies)

You have **TWO OPTIONS**:

### Option A: Single Large File (Faster but may timeout)

**File Location:**
```
supabase/migrations/20251109140000_insert_all_234_constituencies.sql
```

**File Size:** 919 KB

**Pros:** One-step import
**Cons:** May timeout in browser due to large size

**Instructions:**
1. Open the file
2. Copy ALL contents
3. Paste in Supabase SQL Editor
4. Click **RUN**
5. Wait 30-60 seconds

---

### Option B: 4 Batched Files (Safer, recommended)

**File Location:**
```
supabase/migrations/batches/
├── 20251109140000_tn_batch1_insert_tn_constituencies.sql (186 KB - 59 constituencies)
├── 20251109140000_tn_batch2_insert_tn_constituencies.sql (258 KB - 59 constituencies)
├── 20251109140000_tn_batch3_insert_tn_constituencies.sql (235 KB - 59 constituencies)
└── 20251109140000_tn_batch4_insert_tn_constituencies.sql (245 KB - 57 constituencies)
```

**Pros:** Safer, won't timeout
**Cons:** Requires 4 separate runs

**Instructions:**

#### Batch 1 (Constituencies 1-59)
1. Open `20251109140000_tn_batch1_insert_tn_constituencies.sql`
2. Copy all contents
3. Paste in Supabase SQL Editor
4. Click **RUN**
5. Wait for completion (~10-15 seconds)
6. Verify: Should show "Batch 1: 59 constituencies inserted"

#### Batch 2 (Constituencies 60-118)
1. Open `20251109140000_tn_batch2_insert_tn_constituencies.sql`
2. Repeat steps 2-6
3. Verify: Should show "Batch 2: 59 constituencies inserted"

#### Batch 3 (Constituencies 119-177)
1. Open `20251109140000_tn_batch3_insert_tn_constituencies.sql`
2. Repeat steps 2-6
3. Verify: Should show "Batch 3: 59 constituencies inserted"

#### Batch 4 (Constituencies 178-234)
1. Open `20251109140000_tn_batch4_insert_tn_constituencies.sql`
2. Repeat steps 2-6
3. Verify: Should show "Batch 4: 57 constituencies inserted"

---

## ✅ Step 3: Final Verification

Run this query in Supabase SQL Editor to verify all 264 constituencies:

```sql
SELECT
  COALESCE(state, '🎯 TOTAL') as state,
  COUNT(*) as constituencies,
  COUNT(*) FILTER (WHERE reserved_category = 'sc') as sc,
  COUNT(*) FILTER (WHERE reserved_category = 'st') as st,
  COUNT(*) FILTER (WHERE reserved_category = 'general') as general
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY ROLLUP(state)
ORDER BY state NULLS LAST;
```

### Expected Final Result
```
| state       | constituencies | sc  | st | general |
|-------------|----------------|-----|----|---------|
| Puducherry  | 30             | 7   | 0  | 23      |
| Tamil Nadu  | 234            | 44  | 2  | 188     |
| 🎯 TOTAL    | 264            | 51  | 2  | 211     |
```

---

## 🔧 Troubleshooting

### Problem: "Timeout" error
**Solution:** Use Option B (batched files) instead of the single large file

### Problem: "Duplicate key value violates unique constraint"
**Solution:** Some constituencies already exist. This is OK, the SQL uses `ON CONFLICT` to update them.

### Problem: "Organization not found"
**Solution:** Each SQL file ensures the TVK organization exists first. Just re-run the file.

### Problem: Count doesn't match expected
**Solution:**
1. Check which batch failed
2. Re-run that specific batch
3. Verify again

---

## 📝 Import Checklist

- [ ] Pondicherry imported (30 constituencies)
- [ ] Tamil Nadu Batch 1 imported (59 constituencies)
- [ ] Tamil Nadu Batch 2 imported (59 constituencies)
- [ ] Tamil Nadu Batch 3 imported (59 constituencies)
- [ ] Tamil Nadu Batch 4 imported (57 constituencies)
- [ ] Final verification shows 264 total constituencies
- [ ] All boundaries (GeoJSON) loaded correctly

---

## 🎉 Success Criteria

After completing all steps, you should have:
- ✅ 264 total constituencies in the database
- ✅ 30 Pondicherry constituencies (4 regions)
- ✅ 234 Tamil Nadu constituencies (38 districts)
- ✅ Full GeoJSON boundaries for all Tamil Nadu constituencies
- ✅ Correct reserved categories (SC/ST/General) for all constituencies

---

**Last Updated:** 2025-11-09
**Total Import Time:** ~5-10 minutes (batched approach)
