# 🔧 Import Error Fix Guide

## ❌ Error You Encountered

```
ERROR: 42883: function st_geogfromgeojson(text) does not exist
HINT: No function matches the given name and argument types.
      You might need to add explicit type casts.
QUERY: NEW.geom = ST_GeogFromGeoJSON(NEW.boundaries::text)
CONTEXT: PL/pgSQL function sync_geography_from_boundaries() line 4 at assignment
```

---

## 🔍 Root Cause

There's a database trigger function `sync_geography_from_boundaries()` that tries to use PostGIS function `ST_GeogFromGeoJSON`, but:

1. PostGIS extension may not be fully enabled in your Supabase database
2. Or the function name is incorrect for your PostGIS version
3. This trigger fires when inserting constituencies with `boundaries` data

**The trigger is blocking all constituency imports!**

---

## ✅ Solution: Disable the Trigger Temporarily

### Step 1: Run the Fix SQL

**File:** `FIX_POSTGIS_TRIGGER.sql`

**What it does:**
1. Drops the problematic triggers on `constituencies`, `wards`, and `territories` tables
2. Drops the broken `sync_geography_from_boundaries()` function
3. Creates a simple no-op version that does nothing (prevents errors)
4. Verifies triggers are removed

**Instructions:**
1. Open `FIX_POSTGIS_TRIGGER.sql`
2. Copy ALL contents
3. Paste in Supabase SQL Editor: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql/new
4. Click **RUN**
5. Wait for completion (~2 seconds)

**Expected Result:**
```
✅ Triggers dropped
✅ Function replaced with no-op version
trigger_count: 0
```

---

### Step 2: Proceed with Constituency Import

After running the fix, you can now proceed with:

1. **Pondicherry Import** (30 constituencies)
   - File: `IMPORT_ALL_CONSTITUENCIES.sql`

2. **Tamil Nadu Import** (234 constituencies)
   - Option A: Single file `20251109140000_insert_all_234_constituencies.sql`
   - Option B: 4 batched files (recommended)

---

## 🎯 Why This Fix Works

**Before Fix:**
- INSERT → Trigger fires → Calls `ST_GeogFromGeoJSON` → ERROR (function doesn't exist)

**After Fix:**
- INSERT → Trigger fires → No-op function → SUCCESS
- The `boundaries` column still gets populated with GeoJSON
- Only the `geom` column (PostGIS geography) won't be auto-populated
- This is fine - we can fix PostGIS setup later

---

## 📝 Future: Proper PostGIS Setup

After importing all constituencies, if you need the `geom` column for advanced spatial queries, you can:

### Option 1: Enable PostGIS Properly
```sql
-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Check available PostGIS functions
SELECT proname FROM pg_proc WHERE proname LIKE '%geojson%';
```

### Option 2: Use Correct Function
The function might be named differently in your PostGIS version:
- `ST_GeomFromGeoJSON` (geometry, not geography)
- `ST_GeogFromGeoJSON` (geography - what we tried to use)

### Option 3: Keep it Disabled
If you're only using the `boundaries` JSON column for Mapbox rendering, you don't need the `geom` column at all!

---

## 🚀 Next Steps

**NOW:**
1. ✅ Run `FIX_POSTGIS_TRIGGER.sql`
2. ✅ Proceed with constituency imports

**LATER (Optional):**
1. Research PostGIS extension availability in Supabase
2. Set up proper geography column if needed for spatial queries
3. Re-enable trigger with correct function

---

## 🎯 Summary

| Step | Action | File | Time |
|------|--------|------|------|
| 0 | Fix trigger | `FIX_POSTGIS_TRIGGER.sql` | 2 sec |
| 1 | Import Pondicherry | `IMPORT_ALL_CONSTITUENCIES.sql` | 5 sec |
| 2 | Import Tamil Nadu | Batched files (4) | 10-15 min |
| 3 | Verify | SQL query | 2 sec |

**Total Time:** ~15-20 minutes

---

**Status:** ✅ Fix ready to apply
**Impact:** Unblocks all constituency imports
**Last Updated:** 2025-11-09
