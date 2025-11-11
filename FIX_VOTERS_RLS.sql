-- ============================================================================
-- FIX VOTERS TABLE RLS POLICIES
-- Allow more roles to insert/update voters
-- ============================================================================
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard
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

-- Verify RLS is enabled
ALTER TABLE voters ENABLE ROW LEVEL SECURITY;

-- Grant necessary permissions
GRANT ALL ON voters TO authenticated;

-- Display success message
DO $$
BEGIN
    RAISE NOTICE 'SUCCESS: Voters RLS policies updated!';
    RAISE NOTICE 'Now the following roles can INSERT voters: admin, manager, analyst, user, volunteer, superadmin';
END $$;
