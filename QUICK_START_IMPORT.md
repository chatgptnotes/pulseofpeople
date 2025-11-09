# 🚀 Quick Start: Import 264 Constituencies

## ⚠️ STEP 0: Fix PostGIS Trigger (REQUIRED FIRST!)
```
📄 FIX_TRIGGER_CLEAN.sql
```
**Action:** Copy → Paste in Supabase SQL Editor → Run
**Why:** Replaces a broken function that's blocking imports
**Time:** ~2 seconds

---

## ✅ Files Ready for Import

### 1️⃣ Pondicherry (30 constituencies) - START HERE
```
📄 IMPORT_ALL_CONSTITUENCIES.sql
```
**Action:** Copy → Paste in Supabase SQL Editor → Run
**Time:** ~5 seconds

---

### 2️⃣ Tamil Nadu (234 constituencies) - CHOOSE ONE OPTION

#### Option A: Single File (Fast)
```
📄 supabase/migrations/20251109140000_insert_all_234_constituencies.sql
```
**Size:** 919 KB
**Action:** Copy → Paste → Run
**Time:** 30-60 seconds
**Risk:** May timeout in browser

#### Option B: 4 Batches (Safer) ⭐ RECOMMENDED
```
📁 supabase/migrations/batches/
   📄 20251109140000_tn_batch1_insert_tn_constituencies.sql (186 KB - 59 constituencies)
   📄 20251109140000_tn_batch2_insert_tn_constituencies.sql (258 KB - 59 constituencies)
   📄 20251109140000_tn_batch3_insert_tn_constituencies.sql (235 KB - 59 constituencies)
   📄 20251109140000_tn_batch4_insert_tn_constituencies.sql (245 KB - 57 constituencies)
```
**Action:** Import each file one by one
**Time:** ~10-15 seconds per batch

---

## 🎯 Supabase SQL Editor URL
```
https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql/new
```

---

## ✅ Final Verification Query
```sql
SELECT
  COALESCE(state, '🎯 TOTAL') as state,
  COUNT(*) as constituencies
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY ROLLUP(state);
```

### Expected Result
```
Puducherry: 30
Tamil Nadu: 234
TOTAL: 264
```

---

## 📚 Full Documentation
See `CONSTITUENCY_IMPORT_GUIDE.md` for detailed step-by-step instructions.

---

**Status:** ✅ All files ready - awaiting import
**Last Updated:** 2025-11-09
