-- ============================================================================
-- FIX & COMPLETE MIGRATION
-- ============================================================================
-- This migration fixes existing tables and adds any missing columns/tables
-- Safe to run even if some parts already exist
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- FIX ORGANIZATIONS TABLE
-- ============================================================================

-- Add missing columns to organizations if they don't exist
DO $$
BEGIN
    -- Add slug column if missing
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='slug') THEN
        ALTER TABLE organizations ADD COLUMN slug VARCHAR(100);
    END IF;

    -- Add other missing columns
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='type') THEN
        ALTER TABLE organizations ADD COLUMN type VARCHAR(50) DEFAULT 'political_party' CHECK (type IN ('political_party', 'campaign', 'ngo', 'advocacy_group'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='logo_url') THEN
        ALTER TABLE organizations ADD COLUMN logo_url TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='website') THEN
        ALTER TABLE organizations ADD COLUMN website TEXT;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='settings') THEN
        ALTER TABLE organizations ADD COLUMN settings JSONB DEFAULT '{}'::jsonb;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='is_active') THEN
        ALTER TABLE organizations ADD COLUMN is_active BOOLEAN DEFAULT true;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='subscription_status') THEN
        ALTER TABLE organizations ADD COLUMN subscription_status VARCHAR(50) DEFAULT 'trial' CHECK (subscription_status IN ('trial', 'active', 'suspended', 'cancelled'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='subscription_start_date') THEN
        ALTER TABLE organizations ADD COLUMN subscription_start_date DATE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='subscription_end_date') THEN
        ALTER TABLE organizations ADD COLUMN subscription_end_date DATE;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='monthly_fee') THEN
        ALTER TABLE organizations ADD COLUMN monthly_fee DECIMAL(10, 2) DEFAULT 6000.00;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='primary_contact_name') THEN
        ALTER TABLE organizations ADD COLUMN primary_contact_name VARCHAR(255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='primary_contact_email') THEN
        ALTER TABLE organizations ADD COLUMN primary_contact_email VARCHAR(255);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='primary_contact_phone') THEN
        ALTER TABLE organizations ADD COLUMN primary_contact_phone VARCHAR(20);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='metadata') THEN
        ALTER TABLE organizations ADD COLUMN metadata JSONB DEFAULT '{}'::jsonb;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='created_at') THEN
        ALTER TABLE organizations ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='updated_at') THEN
        ALTER TABLE organizations ADD COLUMN updated_at TIMESTAMPTZ DEFAULT NOW();
    END IF;
END $$;

-- Update existing organizations with slugs if they don't have them
UPDATE organizations
SET slug = LOWER(REGEXP_REPLACE(name, '[^a-zA-Z0-9]+', '-', 'g'))
WHERE slug IS NULL;

-- Now make slug NOT NULL and UNIQUE
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='organizations' AND column_name='slug') THEN
        ALTER TABLE organizations ALTER COLUMN slug SET NOT NULL;

        -- Add unique constraint if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'organizations_slug_key') THEN
            ALTER TABLE organizations ADD CONSTRAINT organizations_slug_key UNIQUE (slug);
        END IF;
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_active ON organizations(is_active);

-- ============================================================================
-- CREATE OTHER TABLES
-- ============================================================================

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url TEXT,
    bio TEXT,
    role VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (role IN ('superadmin', 'admin', 'manager', 'analyst', 'user', 'viewer', 'volunteer')),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    preferences JSONB DEFAULT '{}'::jsonb,
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ,
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX IF NOT EXISTS idx_users_org ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

-- User permissions table
CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_key VARCHAR(100) NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ,
    UNIQUE(user_id, permission_key)
);

CREATE INDEX IF NOT EXISTS idx_user_permissions_user ON user_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_key ON user_permissions(permission_key);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'view', 'login', 'logout', 'login_failed', 'export', 'import', 'bulk_upload', 'permission_granted', 'permission_revoked', 'status_changed', 'password_reset')),
    resource_type VARCHAR(100),
    resource_id UUID,
    resource_name VARCHAR(255),
    changes JSONB,
    previous_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_org_created ON audit_logs(organization_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- ============================================================================
-- ENABLE RLS
-- ============================================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- CREATE FUNCTIONS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION log_user_creation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (organization_id, user_id, action, resource_type, resource_id, resource_name, new_values)
    VALUES (NEW.organization_id, NEW.created_by, 'create', 'user', NEW.id, NEW.full_name,
            jsonb_build_object('email', NEW.email, 'role', NEW.role, 'username', NEW.username));
    RETURN NEW;
EXCEPTION WHEN OTHERS THEN
    RETURN NEW; -- Don't fail user creation if audit log fails
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_role_hierarchy()
RETURNS TRIGGER AS $$
DECLARE
    creator_role VARCHAR(50);
    role_hierarchy_map JSONB;
BEGIN
    role_hierarchy_map := '{"volunteer": 1, "viewer": 2, "user": 3, "analyst": 4, "manager": 5, "admin": 6, "superadmin": 7}'::jsonb;
    SELECT role INTO creator_role FROM users WHERE id = NEW.created_by;
    IF creator_role = 'superadmin' THEN RETURN NEW; END IF;
    IF (role_hierarchy_map->>creator_role)::int <= (role_hierarchy_map->>NEW.role)::int THEN
        RAISE EXCEPTION 'Cannot create user with role % as %', NEW.role, creator_role;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(permission_key VARCHAR) AS $$
BEGIN
    RETURN QUERY SELECT up.permission_key FROM user_permissions up
    WHERE up.user_id = p_user_id AND (up.expires_at IS NULL OR up.expires_at > NOW());
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION has_permission(p_user_id UUID, p_permission VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE has_perm BOOLEAN;
BEGIN
    SELECT EXISTS(SELECT 1 FROM user_permissions WHERE user_id = p_user_id AND permission_key = p_permission
        AND (expires_at IS NULL OR expires_at > NOW())) INTO has_perm;
    RETURN has_perm;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CREATE TRIGGERS
-- ============================================================================

DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS trigger_log_user_creation ON users;
CREATE TRIGGER trigger_log_user_creation AFTER INSERT ON users
    FOR EACH ROW EXECUTE FUNCTION log_user_creation();

DROP TRIGGER IF EXISTS trigger_check_role_hierarchy ON users;
CREATE TRIGGER trigger_check_role_hierarchy BEFORE INSERT ON users
    FOR EACH ROW WHEN (NEW.created_by IS NOT NULL) EXECUTE FUNCTION check_role_hierarchy();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

-- Drop existing policies to recreate them
DROP POLICY IF EXISTS "Users can view their organization" ON organizations;
DROP POLICY IF EXISTS "Superadmins can view all organizations" ON organizations;
DROP POLICY IF EXISTS "Admins can update their organization" ON organizations;
DROP POLICY IF EXISTS "Users can view organization members" ON users;
DROP POLICY IF EXISTS "Admins can create users in their organization" ON users;
DROP POLICY IF EXISTS "Admins can update users in their organization" ON users;
DROP POLICY IF EXISTS "Users can update their own profile" ON users;
DROP POLICY IF EXISTS "Users can view their permissions" ON user_permissions;
DROP POLICY IF EXISTS "Users can view audit logs in their organization" ON audit_logs;
DROP POLICY IF EXISTS "System can insert audit logs" ON audit_logs;

-- Organizations policies
CREATE POLICY "Users can view their organization" ON organizations FOR SELECT
    USING (id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Superadmins can view all organizations" ON organizations FOR SELECT
    USING (EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'superadmin'));

CREATE POLICY "Admins can update their organization" ON organizations FOR UPDATE
    USING (id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'superadmin')));

-- Users policies
CREATE POLICY "Users can view organization members" ON users FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Admins can create users in their organization" ON users FOR INSERT
    WITH CHECK (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'superadmin')));

CREATE POLICY "Admins can update users in their organization" ON users FOR UPDATE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')));

CREATE POLICY "Users can update their own profile" ON users FOR UPDATE
    USING (id = auth.uid());

-- Permissions policies
CREATE POLICY "Users can view their permissions" ON user_permissions FOR SELECT
    USING (user_id = auth.uid());

-- Audit logs policies
CREATE POLICY "Users can view audit logs in their organization" ON audit_logs FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "System can insert audit logs" ON audit_logs FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

-- Insert sample organizations
INSERT INTO organizations (id, name, slug, type, subscription_status)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Democratic Alliance Party', 'dap', 'political_party', 'active'),
    ('22222222-2222-2222-2222-222222222222', 'Progressive Coalition', 'pc', 'political_party', 'trial'),
    ('33333333-3333-3333-3333-333333333333', 'Citizens Forum', 'cf', 'ngo', 'active')
ON CONFLICT (id) DO NOTHING;

-- Insert sample users
INSERT INTO users (id, organization_id, email, username, full_name, role, is_active, is_verified)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'super@dap.org', 'superadmin', 'Super Admin', 'superadmin', true, true),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', 'admin@dap.org', 'admin_dap', 'John Admin', 'admin', true, true),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111', 'manager@dap.org', 'manager_dap', 'Jane Manager', 'manager', true, true),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111', 'analyst@dap.org', 'analyst_dap', 'Bob Analyst', 'analyst', true, true),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '11111111-1111-1111-1111-111111111111', 'user@dap.org', 'user_dap', 'Alice User', 'user', true, true),
    ('ffffffff-ffff-ffff-ffff-ffffffffffff', '11111111-1111-1111-1111-111111111111', 'viewer@dap.org', 'viewer_dap', 'Charlie Viewer', 'viewer', true, true),
    ('10101010-1010-1010-1010-101010101010', '22222222-2222-2222-2222-222222222222', 'admin@pc.org', 'admin_pc', 'Sarah Admin', 'admin', true, true),
    ('20202020-2020-2020-2020-202020202020', '33333333-3333-3333-3333-333333333333', 'admin@cf.org', 'admin_cf', 'Mike Admin', 'admin', true, true)
ON CONFLICT (id) DO NOTHING;

-- Insert sample permissions
INSERT INTO user_permissions (user_id, permission_key, granted_by)
VALUES
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'users.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'users.create', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'campaigns.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'field_workers.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'analytics.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'reports.generate', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'social.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb')
ON CONFLICT (user_id, permission_key) DO NOTHING;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '✅ Phase 1 Complete!' as status;

SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('organizations', 'users', 'user_permissions', 'audit_logs')
ORDER BY table_name;
