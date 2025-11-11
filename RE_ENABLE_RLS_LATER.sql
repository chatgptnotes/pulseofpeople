-- ============================================================================
-- RE-ENABLE RLS ON VOTERS TABLE (Run this AFTER testing)
-- This re-enables security with proper policies
-- ============================================================================
-- Run this AFTER you've successfully added voters and want to secure the table
-- ============================================================================

-- Step 1: Enable Row Level Security
ALTER TABLE voters ENABLE ROW LEVEL SECURITY;

-- Step 2: Create proper RLS policies
-- Allow authenticated users to SELECT voters in their organization
CREATE POLICY "voters_select_own_org" ON voters
    FOR SELECT
    TO authenticated
    USING (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
        OR
        (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) = 'superadmin'
    );

-- Allow authenticated users to INSERT voters into their organization
CREATE POLICY "voters_insert_own_org" ON voters
    FOR INSERT
    TO authenticated
    WITH CHECK (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
    );

-- Allow authenticated users to UPDATE voters in their organization
CREATE POLICY "voters_update_own_org" ON voters
    FOR UPDATE
    TO authenticated
    USING (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
    )
    WITH CHECK (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
    );

-- Allow admins to DELETE voters in their organization
CREATE POLICY "voters_delete_own_org" ON voters
    FOR DELETE
    TO authenticated
    USING (
        organization_id = (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1)
        AND
        (SELECT role FROM users WHERE id = auth.uid() LIMIT 1) IN ('admin', 'superadmin', 'manager')
    );

-- Verify policies are created
SELECT
    policyname,
    cmd as operation
FROM pg_policies
WHERE tablename = 'voters'
ORDER BY policyname;

DO $$
BEGIN
    RAISE NOTICE '✅ RLS has been re-enabled with organization-based policies';
END $$;
