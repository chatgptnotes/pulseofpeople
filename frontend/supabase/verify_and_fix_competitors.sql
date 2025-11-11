-- =====================================================
-- COMPETITOR TRACKING - VERIFY AND FIX
-- =====================================================
-- Run this in Supabase SQL Editor to check and fix the competitors data
--
-- Instructions:
-- 1. Go to your Supabase project dashboard
-- 2. Click "SQL Editor" in the left sidebar
-- 3. Copy and paste this entire file
-- 4. Click "Run" button
-- 5. Check the results in the "Results" panel
-- =====================================================

-- Step 1: Check if competitors table exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_tables WHERE tablename = 'competitors') THEN
        RAISE NOTICE '✅ Table "competitors" exists';
    ELSE
        RAISE NOTICE '❌ Table "competitors" does NOT exist - run migration first!';
    END IF;
END $$;

-- Step 2: Count existing competitors
SELECT
    CASE
        WHEN COUNT(*) = 0 THEN '⚠️ Table is EMPTY - no competitors found'
        ELSE '✅ Found ' || COUNT(*) || ' competitors'
    END as status,
    COUNT(*) as total_count
FROM competitors;

-- Step 3: Show existing competitors (if any)
SELECT
    id,
    name,
    party_name,
    color_code,
    data_source,
    is_active,
    created_at
FROM competitors
ORDER BY created_at DESC;

-- Step 4: Check RLS policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual
FROM pg_policies
WHERE tablename = 'competitors';

-- Step 5: Insert sample data (if table is empty)
-- This will safely add the 3 sample competitors without duplicates
INSERT INTO competitors (name, party_name, description, color_code, data_source, is_active)
VALUES
    ('DMK', 'Dravida Munnetra Kazhagam', 'Main opposition party in Tamil Nadu', '#E41E26', 'manual', true),
    ('ADMK', 'All India Anna Dravida Munnetra Kazhagam', 'Previous ruling party', '#138808', 'manual', true),
    ('BJP Tamil Nadu', 'Bharatiya Janata Party - Tamil Nadu', 'National party''s state unit', '#FF9933', 'manual', true)
ON CONFLICT (name) DO NOTHING
RETURNING id, name, party_name;

-- Step 6: Final verification - show all competitors
SELECT
    '✅ FINAL RESULT: ' || COUNT(*) || ' competitors in database' as summary,
    json_agg(json_build_object(
        'name', name,
        'party_name', party_name,
        'color_code', color_code,
        'is_active', is_active
    )) as competitors_list
FROM competitors;

-- Step 7: Test if RLS is blocking SELECT queries
-- This should show TRUE if RLS is enabled
SELECT
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename = 'competitors';

-- =====================================================
-- TROUBLESHOOTING NOTES:
-- =====================================================
-- If you see "Table does not exist":
--   → Run the migration file: 20251109_competitor_tracking.sql first
--
-- If you see "Table is EMPTY":
--   → Step 5 above will insert sample data
--
-- If you see data but CompetitorRegistry shows nothing:
--   → Check browser console for errors
--   → RLS policies might be blocking (see Step 4 output)
--
-- If RLS is blocking:
--   → Run: ALTER TABLE competitors DISABLE ROW LEVEL SECURITY;
--   → Or adjust RLS policies to allow SELECT for authenticated users
-- =====================================================
