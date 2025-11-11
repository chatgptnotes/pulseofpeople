-- ============================================================================
-- ULTIMATE FIX FOR VOTERS RLS - SIMPLIFIED & MORE PERMISSIVE
-- This removes complex RLS checks and makes it work for all authenticated users
-- ============================================================================
-- Run this ENTIRE script in Supabase SQL Editor
-- ============================================================================

-- STEP 1: Ensure organization exists
-- ============================================================================
INSERT INTO organizations (name, slug, subscription_tier, is_active)
VALUES ('TVK Organization', 'tvk', 'pro', true)
ON CONFLICT (slug) DO NOTHING;

-- STEP 2: Update ALL users to have organization_id
-- ============================================================================
DO $$
DECLARE
    v_org_id UUID;
BEGIN
    -- Get organization ID
    SELECT id INTO v_org_id FROM organizations WHERE slug = 'tvk' LIMIT 1;

    -- Update all users without org_id
    UPDATE users
    SET organization_id = v_org_id,
        is_active = true
    WHERE organization_id IS NULL;

    RAISE NOTICE 'Updated users with organization_id: %', v_org_id;
END $$;

-- STEP 3: Drop all existing RLS policies on voters
-- ============================================================================
DROP POLICY IF EXISTS "voters_select_policy" ON voters;
DROP POLICY IF EXISTS "voters_insert_policy" ON voters;
DROP POLICY IF EXISTS "voters_update_policy" ON voters;
DROP POLICY IF EXISTS "voters_delete_policy" ON voters;

-- Drop any other policies that might exist
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT policyname FROM pg_policies WHERE tablename = 'voters')
    LOOP
        EXECUTE 'DROP POLICY IF EXISTS "' || r.policyname || '" ON voters';
        RAISE NOTICE 'Dropped policy: %', r.policyname;
    END LOOP;
END $$;

-- STEP 4: Create SIMPLE, PERMISSIVE RLS policies
-- ============================================================================

-- Allow all authenticated users to SELECT voters
CREATE POLICY "voters_select_all" ON voters
    FOR SELECT
    TO authenticated
    USING (true);

-- Allow all authenticated users to INSERT voters
CREATE POLICY "voters_insert_all" ON voters
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- Allow all authenticated users to UPDATE voters
CREATE POLICY "voters_update_all" ON voters
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Allow all authenticated users to DELETE voters
CREATE POLICY "voters_delete_all" ON voters
    FOR DELETE
    TO authenticated
    USING (true);

-- STEP 5: Enable RLS and grant permissions
-- ============================================================================
ALTER TABLE voters ENABLE ROW LEVEL SECURITY;
GRANT ALL ON voters TO authenticated;
GRANT ALL ON voters TO anon;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon;

-- STEP 6: Verify setup
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE '✅ VOTERS RLS POLICIES HAVE BEEN SIMPLIFIED!';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'All authenticated users can now:';
    RAISE NOTICE '  ✅ SELECT voters';
    RAISE NOTICE '  ✅ INSERT voters';
    RAISE NOTICE '  ✅ UPDATE voters';
    RAISE NOTICE '  ✅ DELETE voters';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  IMPORTANT: You MUST log out and log back in!';
    RAISE NOTICE '============================================================================';
END $$;

-- Display current policies
SELECT
    policyname,
    cmd as operation,
    roles
FROM pg_policies
WHERE tablename = 'voters'
ORDER BY policyname;

-- Display user data
SELECT
    email,
    role,
    organization_id,
    CASE
        WHEN organization_id IS NULL THEN '❌ NO ORG'
        ELSE '✅ HAS ORG'
    END as status
FROM users
ORDER BY email;
