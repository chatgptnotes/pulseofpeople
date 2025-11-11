-- ============================================================================
-- FIX RLS INFINITE RECURSION - FINAL VERSION
-- ============================================================================
-- Execute this directly in Supabase SQL Editor
-- ============================================================================

-- Drop problematic existing policies
DO $$
BEGIN
    -- Drop all policies that might cause recursion
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
EXCEPTION
    WHEN OTHERS THEN NULL;
END $$;

-- Create helper functions
CREATE OR REPLACE FUNCTION get_user_organization_id()
RETURNS UUID AS $$
BEGIN
    RETURN (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1);
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

CREATE OR REPLACE FUNCTION get_user_role()
RETURNS VARCHAR AS $$
BEGIN
    RETURN (SELECT role FROM users WHERE id = auth.uid() LIMIT 1);
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Organizations policies
CREATE POLICY "org_select_policy" ON organizations FOR SELECT TO authenticated
    USING (id = get_user_organization_id() OR get_user_role() = 'superadmin');

CREATE POLICY "org_update_policy" ON organizations FOR UPDATE TO authenticated
    USING (id = get_user_organization_id() AND get_user_role() IN ('admin', 'superadmin'));

-- Users policies
CREATE POLICY "users_select_policy" ON users FOR SELECT TO authenticated
    USING (organization_id = get_user_organization_id() OR get_user_role() = 'superadmin');

CREATE POLICY "users_update_own_policy" ON users FOR UPDATE TO authenticated
    USING (id = auth.uid());

CREATE POLICY "users_insert_policy" ON users FOR INSERT TO authenticated
    WITH CHECK (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'superadmin'));

CREATE POLICY "users_update_policy" ON users FOR UPDATE TO authenticated
    USING (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'manager', 'superadmin'));

-- Constituencies policies
CREATE POLICY "constituencies_select_policy" ON constituencies FOR SELECT TO authenticated
    USING (organization_id = get_user_organization_id() OR get_user_role() = 'superadmin');

CREATE POLICY "constituencies_all_policy" ON constituencies FOR ALL TO authenticated
    USING (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'manager', 'superadmin'));

-- Wards policies
CREATE POLICY "wards_select_policy" ON wards FOR SELECT TO authenticated
    USING (organization_id = get_user_organization_id() OR get_user_role() = 'superadmin');

CREATE POLICY "wards_all_policy" ON wards FOR ALL TO authenticated
    USING (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'manager', 'superadmin'));

-- Polling booths policies
CREATE POLICY "booths_select_policy" ON polling_booths FOR SELECT TO authenticated
    USING (organization_id = get_user_organization_id() OR get_user_role() = 'superadmin');

CREATE POLICY "booths_all_policy" ON polling_booths FOR ALL TO authenticated
    USING (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'manager', 'superadmin'));

-- Voters policies
CREATE POLICY "voters_select_policy" ON voters FOR SELECT TO authenticated
    USING (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'manager', 'analyst', 'superadmin'));

CREATE POLICY "voters_insert_policy" ON voters FOR INSERT TO authenticated
    WITH CHECK (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'manager', 'superadmin'));

CREATE POLICY "voters_update_policy" ON voters FOR UPDATE TO authenticated
    USING (organization_id = get_user_organization_id() AND get_user_role() IN ('admin', 'manager', 'superadmin'));

-- Audit logs policies
CREATE POLICY "audit_logs_select_policy" ON audit_logs FOR SELECT TO authenticated
    USING (organization_id = get_user_organization_id() OR get_user_role() = 'superadmin');

CREATE POLICY "audit_logs_insert_policy" ON audit_logs FOR INSERT TO authenticated
    WITH CHECK (true);

-- User permissions policies
CREATE POLICY "permissions_select_own_policy" ON user_permissions FOR SELECT TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "permissions_select_all_policy" ON user_permissions FOR SELECT TO authenticated
    USING (get_user_role() IN ('admin', 'superadmin'));

-- Grant permissions
GRANT USAGE ON SCHEMA public TO authenticated, anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated, anon;
