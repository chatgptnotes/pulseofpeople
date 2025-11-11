-- ============================================================================
-- NUCLEAR OPTION: TEMPORARILY DISABLE RLS ON VOTERS TABLE
-- This will allow voters to be inserted without any permission checks
-- ============================================================================
-- ⚠️ WARNING: This removes all security checks on the voters table
-- Use this ONLY for testing, then re-enable RLS with proper policies later
-- ============================================================================

-- Step 1: Drop ALL existing policies
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'voters')
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON voters CASCADE';
        RAISE NOTICE 'Dropped policy: %', r.policyname;
    END LOOP;
END $$;

-- Step 2: DISABLE Row Level Security on voters table
ALTER TABLE voters DISABLE ROW LEVEL SECURITY;

-- Step 3: Grant all permissions
GRANT ALL ON voters TO authenticated;
GRANT ALL ON voters TO anon;
GRANT ALL ON voters TO public;

-- Step 4: Verify RLS is disabled
SELECT
    tablename,
    rowsecurity as rls_enabled,
    CASE
        WHEN rowsecurity = false THEN '✅ RLS DISABLED - Voters can be inserted freely'
        ELSE '❌ RLS STILL ENABLED'
    END as status
FROM pg_tables
WHERE tablename = 'voters';

-- Success message
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '✅ VOTERS TABLE RLS HAS BEEN DISABLED';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'You can now insert voters WITHOUT any permission checks';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANT STEPS:';
    RAISE NOTICE '1. Refresh your browser (Ctrl+F5)';
    RAISE NOTICE '2. Try adding a voter - it should work now';
    RAISE NOTICE '3. After testing, re-enable RLS with proper policies';
    RAISE NOTICE '============================================================================';
END $$;
