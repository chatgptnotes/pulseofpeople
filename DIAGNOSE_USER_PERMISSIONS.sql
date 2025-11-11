-- ============================================================================
-- DIAGNOSE USER PERMISSIONS
-- Check what's wrong with the current user's permissions
-- ============================================================================
-- Run this in Supabase SQL Editor to see what the problem is
-- ============================================================================

-- 1. Check ALL users and their organization_id
SELECT
    id,
    email,
    full_name,
    role,
    organization_id,
    is_active,
    CASE
        WHEN organization_id IS NULL THEN '❌ NO ORG ID'
        ELSE '✅ HAS ORG ID'
    END as status
FROM users
ORDER BY email;

-- 2. Check organizations
SELECT
    id,
    name,
    slug,
    is_active,
    created_at
FROM organizations;

-- 3. Check current RLS policies on voters table
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd as command,
    qual as using_expression,
    with_check
FROM pg_policies
WHERE tablename = 'voters'
ORDER BY policyname;

-- 4. Check if RLS is enabled on voters table
SELECT
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE tablename = 'voters';

-- 5. Test query to simulate what happens when inserting
-- This will show you if your current setup allows inserts
DO $$
DECLARE
    v_test_user_id UUID;
    v_test_org_id UUID;
    v_test_role TEXT;
BEGIN
    -- Get a test user
    SELECT id, organization_id, role
    INTO v_test_user_id, v_test_org_id, v_test_role
    FROM users
    WHERE email LIKE '%@tvk.com' OR email LIKE '%@%'
    LIMIT 1;

    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'TEST USER DETAILS:';
    RAISE NOTICE 'User ID: %', v_test_user_id;
    RAISE NOTICE 'Organization ID: %', v_test_org_id;
    RAISE NOTICE 'Role: %', v_test_role;
    RAISE NOTICE '============================================================================';

    IF v_test_org_id IS NULL THEN
        RAISE WARNING '⚠️  PROBLEM: User has NO organization_id!';
    ELSE
        RAISE NOTICE '✅ User has organization_id';
    END IF;

    IF v_test_role IN ('admin', 'manager', 'analyst', 'user', 'volunteer', 'superadmin') THEN
        RAISE NOTICE '✅ User role is allowed to INSERT voters';
    ELSE
        RAISE WARNING '⚠️  PROBLEM: User role "%" is NOT allowed to INSERT voters!', v_test_role;
    END IF;
END $$;
