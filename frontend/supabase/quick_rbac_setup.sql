-- =====================================================
-- QUICK RBAC SETUP - Simplified Version
-- Adds RBAC columns to existing users table and seeds data
-- =====================================================

-- Step 1: Add RBAC columns to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS organization_id UUID,
ADD COLUMN IF NOT EXISTS tenant_id TEXT,
ADD COLUMN IF NOT EXISTS is_super_admin BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS permissions TEXT[] DEFAULT ARRAY[]::TEXT[],
ADD COLUMN IF NOT EXISTS ward TEXT,
ADD COLUMN IF NOT EXISTS constituency TEXT,
ADD COLUMN IF NOT EXISTS state TEXT,
ADD COLUMN IF NOT EXISTS district TEXT,
ADD COLUMN IF NOT EXISTS last_role_change TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS role_changed_by UUID;

-- Step 2: Update role constraint to include all roles
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users
ADD CONSTRAINT users_role_check CHECK (
    role IN (
        'super_admin',
        'admin',
        'manager',
        'analyst',
        'viewer',
        'user',
        'ward-coordinator',
        'social-media',
        'survey-team',
        'truth-team',
        'volunteer'
    )
);

-- Step 3: Add indexes
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_is_super_admin ON users(is_super_admin);

-- Step 4: Seed test users with proper IDs matching auth users
-- Note: These IDs should match the auth.users IDs created earlier

-- Get auth user IDs
DO $$
DECLARE
    super_admin_id UUID;
    admin_id UUID;
    manager_id UUID;
    analyst_id UUID;
    user_id UUID;
    viewer_id UUID;
    coordinator_id UUID;
    social_id UUID;
    survey_id UUID;
    truth_id UUID;
    volunteer_id UUID;
BEGIN
    -- Fetch auth user IDs
    SELECT id INTO super_admin_id FROM auth.users WHERE email = 'superadmin@pulseofpeople.com';
    SELECT id INTO admin_id FROM auth.users WHERE email = 'admin@bettroi.com';
    SELECT id INTO manager_id FROM auth.users WHERE email = 'manager@bettroi.com';
    SELECT id INTO analyst_id FROM auth.users WHERE email = 'analyst@bettroi.com';
    SELECT id INTO user_id FROM auth.users WHERE email = 'user@bettroi.com';
    SELECT id INTO viewer_id FROM auth.users WHERE email = 'viewer@bettroi.com';
    SELECT id INTO coordinator_id FROM auth.users WHERE email = 'coordinator@bettroi.com';
    SELECT id INTO social_id FROM auth.users WHERE email = 'social@bettroi.com';
    SELECT id INTO survey_id FROM auth.users WHERE email = 'survey@bettroi.com';
    SELECT id INTO truth_id FROM auth.users WHERE email = 'truth@bettroi.com';
    SELECT id INTO volunteer_id FROM auth.users WHERE email = 'volunteer@bettroi.com';

    -- Insert or update users
    -- Super Admin
    INSERT INTO users (id, name, email, role, is_super_admin, status, permissions, constituency, state)
    VALUES (
        super_admin_id,
        'Super Admin',
        'superadmin@pulseofpeople.com',
        'super_admin',
        TRUE,
        'active',
        ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions',
              'manage_organizations', 'view_all_data', 'manage_system_settings', 'view_audit_logs',
              'manage_billing', 'create_surveys', 'view_voters', 'edit_voters', 'delete_voters',
              'manage_field_workers', 'manage_social_channels', 'generate_ai_insights'],
        'All Organizations',
        'All States'
    )
    ON CONFLICT (id) DO UPDATE
    SET
        name = EXCLUDED.name,
        role = EXCLUDED.role,
        is_super_admin = EXCLUDED.is_super_admin,
        permissions = EXCLUDED.permissions,
        updated_at = NOW();

    -- Admin
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        admin_id,
        'John Doe',
        'admin@bettroi.com',
        'admin',
        'active',
        ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing'],
        'All'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Manager
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        manager_id,
        'Mike Manager',
        'manager@bettroi.com',
        'manager',
        'active',
        ARRAY['view_users', 'create_users', 'edit_users', 'view_analytics', 'view_reports', 'export_data', 'manage_field_workers'],
        'Central District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Analyst
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        analyst_id,
        'Jane Smith',
        'analyst@bettroi.com',
        'analyst',
        'active',
        ARRAY['view_analytics', 'verify_submissions', 'export_data', 'view_reports', 'view_ai_insights'],
        'Central District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- User
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        user_id,
        'Sam User',
        'user@bettroi.com',
        'user',
        'active',
        ARRAY['view_dashboard', 'view_analytics', 'view_reports', 'view_surveys'],
        'South District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Viewer
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        viewer_id,
        'Bob Wilson',
        'viewer@bettroi.com',
        'viewer',
        'active',
        ARRAY['view_dashboard', 'view_analytics', 'view_reports'],
        'South District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Ward Coordinator
    INSERT INTO users (id, name, email, role, status, permissions, ward, constituency)
    VALUES (
        coordinator_id,
        'Priya Sharma',
        'coordinator@bettroi.com',
        'ward-coordinator',
        'active',
        ARRAY['submit_data', 'view_ward_data', 'verify_local', 'view_dashboard', 'submit_field_reports'],
        'Ward 15',
        'North District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Social Media Manager
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        social_id,
        'Rahul Kumar',
        'social@bettroi.com',
        'social-media',
        'active',
        ARRAY['submit_data', 'view_social_trends', 'view_social_media', 'manage_social_channels'],
        'East District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Survey Team
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        survey_id,
        'Anjali Patel',
        'survey@bettroi.com',
        'survey-team',
        'active',
        ARRAY['submit_data', 'view_survey_results', 'create_surveys', 'view_surveys'],
        'West District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Truth Team
    INSERT INTO users (id, name, email, role, status, permissions, constituency)
    VALUES (
        truth_id,
        'Vikram Singh',
        'truth@bettroi.com',
        'truth-team',
        'active',
        ARRAY['submit_data', 'verify_submissions', 'view_alerts', 'view_competitor_analysis'],
        'Central District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

    -- Volunteer
    INSERT INTO users (id, name, email, role, status, permissions, ward, constituency)
    VALUES (
        volunteer_id,
        'Rita Volunteer',
        'volunteer@bettroi.com',
        'volunteer',
        'active',
        ARRAY['view_dashboard', 'submit_field_reports', 'view_surveys'],
        'Ward 8',
        'West District'
    )
    ON CONFLICT (id) DO UPDATE
    SET name = EXCLUDED.name, role = EXCLUDED.role, permissions = EXCLUDED.permissions, updated_at = NOW();

END $$;

-- Step 5: Verify
SELECT
    email,
    role,
    is_super_admin,
    array_length(permissions, 1) as permission_count,
    status
FROM users
ORDER BY
    CASE role
        WHEN 'super_admin' THEN 1
        WHEN 'admin' THEN 2
        WHEN 'manager' THEN 3
        WHEN 'analyst' THEN 4
        WHEN 'user' THEN 5
        WHEN 'viewer' THEN 6
        ELSE 7
    END;

-- =====================================================
-- SUCCESS!
-- =====================================================
-- All 11 users have been added to the users table
-- with proper RBAC columns and permissions.
--
-- You can now login at: http://localhost:3000/login
--
-- Test accounts (all passwords: "password"):
-- - superadmin@pulseofpeople.com (Super Admin)
-- - admin@bettroi.com (Admin)
-- - manager@bettroi.com (Manager)
-- - analyst@bettroi.com (Analyst)
-- - user@bettroi.com (User)
-- - viewer@bettroi.com (Viewer)
-- - coordinator@bettroi.com (Ward Coordinator)
-- - social@bettroi.com (Social Media)
-- - survey@bettroi.com (Survey Team)
-- - truth@bettroi.com (Truth Team)
-- - volunteer@bettroi.com (Volunteer)
-- =====================================================
