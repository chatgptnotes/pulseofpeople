-- ============================================================================
-- COMPLETE FIX FOR VOTER INSERTION PERMISSION ERRORS
-- This script fixes both user organization_id AND RLS policies
-- ============================================================================
-- Run this ENTIRE script in Supabase SQL Editor
-- Link: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql
-- ============================================================================

-- STEP 1: Check if organizations exist, create one if needed
-- ============================================================================
DO $$
DECLARE
    v_org_count INTEGER;
    v_org_id UUID;
BEGIN
    -- Count organizations
    SELECT COUNT(*) INTO v_org_count FROM organizations;

    IF v_org_count = 0 THEN
        -- Create a default organization
        INSERT INTO organizations (name, slug, subscription_tier, is_active)
        VALUES ('TVK Organization', 'tvk', 'pro', true)
        RETURNING id INTO v_org_id;

        RAISE NOTICE 'Created default organization with ID: %', v_org_id;
    ELSE
        SELECT id INTO v_org_id FROM organizations LIMIT 1;
        RAISE NOTICE 'Using existing organization with ID: %', v_org_id;
    END IF;
END $$;

-- STEP 2: Update ALL users without organization_id
-- ============================================================================
DO $$
DECLARE
    v_org_id UUID;
    v_updated_count INTEGER;
BEGIN
    -- Get first organization ID
    SELECT id INTO v_org_id FROM organizations LIMIT 1;

    -- Update all users that don't have organization_id
    UPDATE users
    SET organization_id = v_org_id,
        is_active = true
    WHERE organization_id IS NULL;

    GET DIAGNOSTICS v_updated_count = ROW_COUNT;

    RAISE NOTICE 'Updated % users with organization_id: %', v_updated_count, v_org_id;
END $$;

-- STEP 3: Verify user data
-- ============================================================================
SELECT
    id,
    email,
    full_name,
    role,
    organization_id,
    is_active
FROM users
LIMIT 10;

-- STEP 4: Fix VOTERS table RLS policies
-- ============================================================================

-- Drop existing voters policies
DROP POLICY IF EXISTS "voters_select_policy" ON voters;
DROP POLICY IF EXISTS "voters_insert_policy" ON voters;
DROP POLICY IF EXISTS "voters_update_policy" ON voters;
DROP POLICY IF EXISTS "voters_delete_policy" ON voters;

-- Recreate voters policies with broader permissions
-- Allow all authenticated users to SELECT voters in their organization
CREATE POLICY "voters_select_policy" ON voters FOR SELECT TO authenticated
    USING (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
        OR
        (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) = 'superadmin'
    );

-- Allow admin, manager, analyst, user, volunteer to INSERT voters
CREATE POLICY "voters_insert_policy" ON voters FOR INSERT TO authenticated
    WITH CHECK (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
        AND
        (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'manager', 'analyst', 'user', 'volunteer', 'superadmin')
    );

-- Allow admin, manager, analyst to UPDATE voters
CREATE POLICY "voters_update_policy" ON voters FOR UPDATE TO authenticated
    USING (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
        AND
        (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'manager', 'analyst', 'superadmin')
    );

-- Allow admin, manager, superadmin to DELETE voters
CREATE POLICY "voters_delete_policy" ON voters FOR DELETE TO authenticated
    USING (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
        AND
        (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'manager', 'superadmin')
    );

-- STEP 5: Verify RLS is enabled and grant permissions
-- ============================================================================
ALTER TABLE voters ENABLE ROW LEVEL SECURITY;
GRANT ALL ON voters TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- STEP 6: Final verification
-- ============================================================================
DO $$
BEGIN
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'SUCCESS! Voter permissions have been fixed!';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Changes made:';
    RAISE NOTICE '1. All users now have organization_id assigned';
    RAISE NOTICE '2. RLS policies updated to allow INSERT for: admin, manager, analyst, user, volunteer, superadmin';
    RAISE NOTICE '3. Table permissions granted to authenticated users';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '1. Refresh your browser (Ctrl+F5 or Cmd+Shift+R)';
    RAISE NOTICE '2. Try adding a voter again';
    RAISE NOTICE '============================================================================';
END $$;

-- Display current policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename = 'voters'
ORDER BY policyname;
