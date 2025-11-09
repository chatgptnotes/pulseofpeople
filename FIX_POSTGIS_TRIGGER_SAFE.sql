-- ============================================================================
-- SAFE FIX: Disable PostGIS trigger to allow constituency import
-- ============================================================================
-- This version only touches tables that exist
-- ============================================================================

-- Step 1: Drop triggers only on tables that exist
DO $$
BEGIN
    -- Drop trigger on constituencies table (we know this exists)
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'constituencies'
    ) THEN
        DROP TRIGGER IF EXISTS trigger_sync_constituency_geom ON constituencies;
        RAISE NOTICE '✅ Dropped trigger on constituencies';
    END IF;

    -- Drop trigger on wards table (if it exists)
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'wards'
    ) THEN
        DROP TRIGGER IF EXISTS trigger_sync_ward_geom ON wards;
        RAISE NOTICE '✅ Dropped trigger on wards';
    END IF;

    -- Drop trigger on territories table (if it exists)
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'territories'
    ) THEN
        DROP TRIGGER IF EXISTS trigger_sync_territory_geom ON territories;
        RAISE NOTICE '✅ Dropped trigger on territories';
    END IF;
END $$;

-- Step 2: Drop the problematic function
DROP FUNCTION IF EXISTS sync_geography_from_boundaries();
RAISE NOTICE '✅ Dropped problematic function';

-- Step 3: Create a simple no-op function
CREATE OR REPLACE FUNCTION sync_geography_from_boundaries()
RETURNS TRIGGER AS $$
BEGIN
    -- Temporarily disabled - PostGIS setup needed
    -- Just return NEW without processing geom column
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

RAISE NOTICE '✅ Created no-op replacement function';

-- Step 4: Verify triggers are dropped
SELECT
  'Trigger Status' as check_type,
  COUNT(*) as trigger_count
FROM information_schema.triggers
WHERE trigger_name LIKE '%sync%geom%';

-- Expected: trigger_count = 0

RAISE NOTICE '✅ Fix complete - you can now import constituencies!';
