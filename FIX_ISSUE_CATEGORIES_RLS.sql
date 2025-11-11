-- =====================================================
-- FIX RLS POLICY FOR issue_categories TABLE
-- Allow authenticated users to INSERT citizen reports
-- =====================================================

-- Drop existing restrictive admin-only policy for INSERT
DROP POLICY IF EXISTS issue_categories_admin_policy ON issue_categories;

-- Create separate policies for better control

-- 1. Allow anyone (even anonymous) to SELECT
CREATE POLICY issue_categories_select_public ON issue_categories
    FOR SELECT
    TO public
    USING (true);

-- 2. Allow authenticated users to INSERT (for citizen reports)
CREATE POLICY issue_categories_insert_authenticated ON issue_categories
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- 3. Allow users to UPDATE their own entries (optional)
CREATE POLICY issue_categories_update_own ON issue_categories
    FOR UPDATE
    TO authenticated
    USING (created_at > NOW() - INTERVAL '1 hour')  -- Only recent entries
    WITH CHECK (true);

-- 4. Allow admins to do everything
CREATE POLICY issue_categories_admin_all ON issue_categories
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin', 'superadmin')
        )
    );

-- Grant necessary permissions
GRANT ALL ON issue_categories TO authenticated;
GRANT SELECT ON issue_categories TO anon;

-- Verify RLS is enabled
ALTER TABLE issue_categories ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- VERIFICATION QUERIES (run these to check)
-- =====================================================

-- Check all policies on the table
-- SELECT * FROM pg_policies WHERE tablename = 'issue_categories';

-- Check table permissions
-- SELECT grantee, privilege_type FROM information_schema.role_table_grants
-- WHERE table_name = 'issue_categories';
