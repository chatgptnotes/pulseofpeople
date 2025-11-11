-- ============================================================================
-- DIAGNOSTIC SCRIPT - Check Phase 2 Tables
-- ============================================================================
-- Copy and paste this into Supabase SQL Editor to see Phase 2 table state
-- ============================================================================

-- 1. What Phase 2 tables exist?
SELECT 'PHASE 2 TABLES:' as info;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('constituencies', 'wards', 'polling_booths', 'voters')
ORDER BY table_name;

-- 2. Column counts for each table
SELECT '---' as separator;
SELECT 'COLUMN COUNTS:' as info;
SELECT table_name,
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('constituencies', 'wards', 'polling_booths', 'voters')
ORDER BY table_name;

-- 3. Row counts
SELECT '---' as separator;
SELECT 'ROW COUNTS:' as info;

DO $$
DECLARE
    rec RECORD;
    row_count INTEGER;
    sql_query TEXT;
BEGIN
    FOR rec IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name IN ('constituencies', 'wards', 'polling_booths', 'voters')
        ORDER BY table_name
    LOOP
        sql_query := 'SELECT COUNT(*) FROM ' || rec.table_name;
        EXECUTE sql_query INTO row_count;
        RAISE NOTICE '% has % rows', rec.table_name, row_count;
    END LOOP;
END $$;

-- 4. Check if functions exist
SELECT '---' as separator;
SELECT 'PHASE 2 FUNCTIONS:' as info;
SELECT proname as function_name
FROM pg_proc
WHERE proname IN (
    'update_constituency_voter_count',
    'update_booth_voter_count',
    'sync_geography_from_boundaries',
    'sync_location_from_coordinates',
    'find_booths_near',
    'get_constituency_stats'
)
ORDER BY proname;
