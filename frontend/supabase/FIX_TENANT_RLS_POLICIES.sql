-- =====================================================
-- FIX: Allow Anonymous Access to Tenants Table
-- =====================================================
-- The tenants table needs to be publicly readable for subdomain detection
-- before users log in

-- Drop existing restrictive policies
DROP POLICY IF EXISTS tenants_view_policy ON tenants;
DROP POLICY IF EXISTS tenants_manage_policy ON tenants;
DROP POLICY IF EXISTS tenants_access_policy ON tenants;

-- Create new policies

-- Policy 1: Allow EVERYONE to VIEW tenants (needed for subdomain detection)
CREATE POLICY tenants_public_read ON tenants
    FOR SELECT
    USING (true);  -- Allow all reads

-- Policy 2: Only admins can INSERT/UPDATE/DELETE tenants
CREATE POLICY tenants_admin_write ON tenants
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND (users.role = 'admin' OR users.role = 'super_admin' OR users.is_super_admin = true)
        )
    );

CREATE POLICY tenants_admin_update ON tenants
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND (users.role = 'admin' OR users.role = 'super_admin' OR users.is_super_admin = true)
        )
    );

CREATE POLICY tenants_admin_delete ON tenants
    FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND (users.role = 'admin' OR users.role = 'super_admin' OR users.is_super_admin = true)
        )
    );

-- Verify RLS is enabled
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;

-- Also check organizations table (might be needed)
DROP POLICY IF EXISTS organizations_view_policy ON organizations;
DROP POLICY IF EXISTS organizations_access_policy ON organizations;

-- Allow public read on organizations too
CREATE POLICY organizations_public_read ON organizations
    FOR SELECT
    USING (true);

-- Only admins can modify organizations
CREATE POLICY organizations_admin_write ON organizations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.is_super_admin = true
        )
    );

-- Test the fix
SELECT
    slug,
    subdomain,
    name,
    status
FROM tenants
WHERE subdomain IN ('party-a', 'party-b');

-- This should return 2 rows without authentication