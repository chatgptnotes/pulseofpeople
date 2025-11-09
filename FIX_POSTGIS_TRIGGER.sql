-- ============================================================================
-- FIX: Disable PostGIS trigger to allow constituency import
-- ============================================================================
-- Issue: ST_GeogFromGeoJSON function doesn't exist
-- Solution: Temporarily disable trigger, import data, then fix PostGIS setup
-- ============================================================================

-- Step 1: Drop the problematic trigger if it exists
DROP TRIGGER IF EXISTS trigger_sync_constituency_geom ON constituencies;
DROP TRIGGER IF EXISTS trigger_sync_ward_geom ON wards;
DROP TRIGGER IF EXISTS trigger_sync_territory_geom ON territories;

-- Step 2: Drop the problematic function
DROP FUNCTION IF EXISTS sync_geography_from_boundaries();

-- Step 3: Create a simple no-op function (does nothing)
-- This prevents errors if other code references it
CREATE OR REPLACE FUNCTION sync_geography_from_boundaries()
RETURNS TRIGGER AS $$
BEGIN
    -- Temporarily disabled - PostGIS setup needed
    -- Just return NEW without processing geom column
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 4: Verify triggers are dropped
SELECT
  'Trigger Status' as check_type,
  COUNT(*) as trigger_count
FROM information_schema.triggers
WHERE trigger_name LIKE '%sync%geom%';

-- Expected: trigger_count = 0

-- ============================================================================
-- Now you can proceed with constituency import!
-- ============================================================================
-- After import, we can properly set up PostGIS if needed
