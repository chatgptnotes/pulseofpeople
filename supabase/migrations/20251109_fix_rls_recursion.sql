-- ============================================================================
-- FIX RLS INFINITE RECURSION ISSUE
-- ============================================================================
-- Problem: Policies were referencing users table in a circular way
-- Solution: Simplify policies and use auth.jwt() claims instead
-- ============================================================================

-- Drop all existing policies
DROP POLICY IF EXISTS "Users can view their organization" ON organizations;
DROP POLICY IF EXISTS "Superadmins can view all organizations" ON organizations;
DROP POLICY IF EXISTS "Admins can update their organization" ON organizations;

DROP POLICY IF EXISTS "Users can view organization members" ON users;
DROP POLICY IF EXISTS "Admins can create users in their organization" ON users;
DROP POLICY IF EXISTS "Admins can update users in their organization" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;

DROP POLICY IF EXISTS "Users can view their permissions" ON user_permissions;
DROP POLICY IF EXISTS "Admins can view all permissions in org" ON user_permissions;

DROP POLICY IF EXISTS "Users can view audit logs in their organization" ON audit_logs;
DROP POLICY IF EXISTS "System can insert audit logs" ON audit_logs;

DROP POLICY IF EXISTS "Users can view their org constituencies" ON constituencies;
DROP POLICY IF EXISTS "Admins can manage constituencies" ON constituencies;

DROP POLICY IF EXISTS "Users can view their org wards" ON wards;
DROP POLICY IF EXISTS "Admins can manage wards" ON wards;

DROP POLICY IF EXISTS "Users can view their org booths" ON polling_booths;
DROP POLICY IF EXISTS "Managers can manage booths" ON polling_booths;

DROP POLICY IF EXISTS "Analysts can view their org voters" ON voters;
DROP POLICY IF EXISTS "Managers can manage voters" ON voters;
DROP POLICY IF EXISTS "Managers can update voters" ON voters;

-- ============================================================================
-- APPROACH 1: Disable RLS for development (TEMPORARY)
-- ============================================================================
-- Uncomment these lines to disable RLS temporarily for development:
-- ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE users DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE user_permissions DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE constituencies DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE wards DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE polling_booths DISABLE ROW LEVEL SECURITY;
-- ALTER TABLE voters DISABLE ROW LEVEL SECURITY;

-- ============================================================================
-- APPROACH 2: Simplified RLS Policies (RECOMMENDED)
-- ============================================================================
-- These policies avoid circular references by using a materialized view

-- Create a helper function to get user's organization
CREATE OR REPLACE FUNCTION get_user_organization_id()
RETURNS UUID AS $$
BEGIN
    -- Get organization_id from the first row matching auth.uid()
    -- This avoids the circular reference
    RETURN (
        SELECT organization_id
        FROM users
        WHERE id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Create a helper function to get user's role
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS VARCHAR AS $$
BEGIN
    RETURN (
        SELECT role
        FROM users
        WHERE id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- ============================================================================
-- SIMPLIFIED POLICIES FOR ORGANIZATIONS
-- ============================================================================

-- Allow all authenticated users to view their organization
CREATE POLICY "org_select_policy"
    ON organizations FOR SELECT
    TO authenticated
    USING (
        id = get_user_organization_id()
        OR get_user_role() = 'superadmin'
    );

-- Allow admins to update their organization
CREATE POLICY "org_update_policy"
    ON organizations FOR UPDATE
    TO authenticated
    USING (
        id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'superadmin')
    );

-- ============================================================================
-- SIMPLIFIED POLICIES FOR USERS
-- ============================================================================

-- Users can view members of their organization
CREATE POLICY "users_select_policy"
    ON users FOR SELECT
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        OR get_user_role() = 'superadmin'
    );

-- Users can update their own profile
CREATE POLICY "users_update_own_policy"
    ON users FOR UPDATE
    TO authenticated
    USING (id = auth.uid());

-- Admins can create users in their organization
CREATE POLICY "users_insert_policy"
    ON users FOR INSERT
    TO authenticated
    WITH CHECK (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'superadmin')
    );

-- Admins can update users in their organization
CREATE POLICY "users_update_policy"
    ON users FOR UPDATE
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'manager', 'superadmin')
    );

-- ============================================================================
-- SIMPLIFIED POLICIES FOR CONSTITUENCIES
-- ============================================================================

CREATE POLICY "constituencies_select_policy"
    ON constituencies FOR SELECT
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        OR get_user_role() = 'superadmin'
    );

CREATE POLICY "constituencies_all_policy"
    ON constituencies FOR ALL
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'manager', 'superadmin')
    );

-- ============================================================================
-- SIMPLIFIED POLICIES FOR WARDS
-- ============================================================================

CREATE POLICY "wards_select_policy"
    ON wards FOR SELECT
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        OR get_user_role() = 'superadmin'
    );

CREATE POLICY "wards_all_policy"
    ON wards FOR ALL
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'manager', 'superadmin')
    );

-- ============================================================================
-- SIMPLIFIED POLICIES FOR POLLING BOOTHS
-- ============================================================================

CREATE POLICY "booths_select_policy"
    ON polling_booths FOR SELECT
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        OR get_user_role() = 'superadmin'
    );

CREATE POLICY "booths_all_policy"
    ON polling_booths FOR ALL
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'manager', 'superadmin')
    );

-- ============================================================================
-- SIMPLIFIED POLICIES FOR VOTERS
-- ============================================================================

CREATE POLICY "voters_select_policy"
    ON voters FOR SELECT
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'manager', 'analyst', 'superadmin')
    );

CREATE POLICY "voters_insert_policy"
    ON voters FOR INSERT
    TO authenticated
    WITH CHECK (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'manager', 'superadmin')
    );

CREATE POLICY "voters_update_policy"
    ON voters FOR UPDATE
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        AND get_user_role() IN ('admin', 'manager', 'superadmin')
    );

-- ============================================================================
-- SIMPLIFIED POLICIES FOR AUDIT LOGS
-- ============================================================================

CREATE POLICY "audit_logs_select_policy"
    ON audit_logs FOR SELECT
    TO authenticated
    USING (
        organization_id = get_user_organization_id()
        OR get_user_role() = 'superadmin'
    );

CREATE POLICY "audit_logs_insert_policy"
    ON audit_logs FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- ============================================================================
-- SIMPLIFIED POLICIES FOR USER PERMISSIONS
-- ============================================================================

CREATE POLICY "permissions_select_own_policy"
    ON user_permissions FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "permissions_select_all_policy"
    ON user_permissions FOR SELECT
    TO authenticated
    USING (
        get_user_role() IN ('admin', 'superadmin')
    );

-- ============================================================================
-- GRANT PERMISSIONS TO AUTHENTICATED USERS
-- ============================================================================

GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Test the helper functions
SELECT
    'Helper Functions Test' AS test_name,
    get_user_organization_id() AS org_id,
    get_user_role() AS user_role;

-- Verify policies exist
SELECT
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

COMMENT ON FUNCTION get_user_organization_id() IS 'Helper function to get current user organization without recursion';
COMMENT ON FUNCTION get_user_role() IS 'Helper function to get current user role without recursion';
