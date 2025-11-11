-- ============================================================================
-- CHECK VOTERS DATA AND RLS STATUS
-- Diagnostic query to see if data exists and why it's not fetching
-- ============================================================================

-- 1. Check if voters table has data
SELECT
    COUNT(*) as total_voters,
    COUNT(CASE WHEN verified = true THEN 1 END) as verified_voters,
    COUNT(CASE WHEN organization_id IS NOT NULL THEN 1 END) as voters_with_org
FROM voters;

-- 2. Sample voters data
SELECT
    id,
    full_name,
    age,
    gender,
    voter_id_number,
    phone,
    organization_id,
    created_at
FROM voters
LIMIT 5;

-- 3. Check if RLS is enabled
SELECT
    tablename,
    rowsecurity as rls_enabled,
    CASE
        WHEN rowsecurity = true THEN '⚠️  RLS IS ENABLED - May block data'
        ELSE '✅ RLS DISABLED - Should work'
    END as status
FROM pg_tables
WHERE tablename = 'voters';

-- 4. Check current RLS policies
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd as operation,
    CASE
        WHEN policyname LIKE '%all%' THEN '✅ Permissive policy'
        ELSE '⚠️  Restrictive policy'
    END as policy_type
FROM pg_policies
WHERE tablename = 'voters'
ORDER BY policyname;

-- 5. Check if voters are linked to organizations
SELECT
    o.name as organization_name,
    COUNT(v.id) as voter_count
FROM organizations o
LEFT JOIN voters v ON v.organization_id = o.id
GROUP BY o.id, o.name
ORDER BY voter_count DESC;

-- 6. Check table permissions
SELECT
    grantee,
    privilege_type
FROM information_schema.role_table_grants
WHERE table_name = 'voters'
AND grantee IN ('authenticated', 'anon', 'public')
ORDER BY grantee, privilege_type;

-- Summary
DO $$
DECLARE
    v_count INTEGER;
    v_rls BOOLEAN;
    v_policy_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count FROM voters;
    SELECT rowsecurity INTO v_rls FROM pg_tables WHERE tablename = 'voters';
    SELECT COUNT(*) INTO v_policy_count FROM pg_policies WHERE tablename = 'voters';

    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'VOTERS TABLE DIAGNOSTIC REPORT';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Total Voters: %', v_count;
    RAISE NOTICE 'RLS Enabled: %', v_rls;
    RAISE NOTICE 'RLS Policies: %', v_policy_count;
    RAISE NOTICE '';

    IF v_count = 0 THEN
        RAISE NOTICE '❌ NO DATA: Voters table is empty!';
    ELSIF v_rls = true AND v_policy_count = 0 THEN
        RAISE NOTICE '❌ PROBLEM: RLS enabled but NO policies - data will be blocked!';
    ELSIF v_rls = true THEN
        RAISE NOTICE '⚠️  RLS is enabled - check if policies allow SELECT';
    ELSE
        RAISE NOTICE '✅ RLS disabled - data should be accessible';
    END IF;

    RAISE NOTICE '============================================================================';
END $$;
