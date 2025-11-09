-- ============================================================================
-- SAFE PHASE 1 COMPLETION
-- ============================================================================
-- This migration safely completes Phase 1 even if some tables already exist
-- Uses CREATE TABLE IF NOT EXISTS to avoid errors
-- ============================================================================

-- Enable extensions if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- ORGANIZATIONS (may already exist)
-- ============================================================================

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    type VARCHAR(50) DEFAULT 'political_party' CHECK (type IN ('political_party', 'campaign', 'ngo', 'advocacy_group')),
    logo_url TEXT,
    website TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    subscription_status VARCHAR(50) DEFAULT 'trial' CHECK (subscription_status IN ('trial', 'active', 'suspended', 'cancelled')),
    subscription_start_date DATE,
    subscription_end_date DATE,
    monthly_fee DECIMAL(10, 2) DEFAULT 6000.00,
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(20),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_organizations_active ON organizations(is_active);

-- ============================================================================
-- USERS
-- ============================================================================

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

-- ============================================================================
-- USER PERMISSIONS
-- ============================================================================

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

-- ============================================================================
-- AUDIT LOGS
-- ============================================================================

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
-- RLS POLICIES (using DO block to avoid errors if already exist)
-- ============================================================================

DO $$
BEGIN
    -- Organizations policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view their organization' AND tablename = 'organizations') THEN
        CREATE POLICY "Users can view their organization" ON organizations FOR SELECT
        USING (id IN (SELECT organization_id FROM users WHERE id = auth.uid()));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Superadmins can view all organizations' AND tablename = 'organizations') THEN
        CREATE POLICY "Superadmins can view all organizations" ON organizations FOR SELECT
        USING (EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'superadmin'));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Admins can update their organization' AND tablename = 'organizations') THEN
        CREATE POLICY "Admins can update their organization" ON organizations FOR UPDATE
        USING (id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'superadmin')));
    END IF;

    -- Users policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view organization members' AND tablename = 'users') THEN
        CREATE POLICY "Users can view organization members" ON users FOR SELECT
        USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Admins can create users in their organization' AND tablename = 'users') THEN
        CREATE POLICY "Admins can create users in their organization" ON users FOR INSERT
        WITH CHECK (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'superadmin')));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Admins can update users in their organization' AND tablename = 'users') THEN
        CREATE POLICY "Admins can update users in their organization" ON users FOR UPDATE
        USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can update their own profile' AND tablename = 'users') THEN
        CREATE POLICY "Users can update their own profile" ON users FOR UPDATE
        USING (id = auth.uid());
    END IF;

    -- Permissions policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view their permissions' AND tablename = 'user_permissions') THEN
        CREATE POLICY "Users can view their permissions" ON user_permissions FOR SELECT
        USING (user_id = auth.uid());
    END IF;

    -- Audit logs policies
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'Users can view audit logs in their organization' AND tablename = 'audit_logs') THEN
        CREATE POLICY "Users can view audit logs in their organization" ON audit_logs FOR SELECT
        USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'System can insert audit logs' AND tablename = 'audit_logs') THEN
        CREATE POLICY "System can insert audit logs" ON audit_logs FOR INSERT
        WITH CHECK (true);
    END IF;
END $$;

-- ============================================================================
-- FUNCTIONS
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
    INSERT INTO audit_logs (organization_id, user_id, action, resource_type, resource_id, resource_name, new_values, ip_address)
    VALUES (NEW.organization_id, NEW.created_by, 'create', 'user', NEW.id, NEW.full_name,
            jsonb_build_object('email', NEW.email, 'role', NEW.role, 'username', NEW.username), inet_client_addr());
    RETURN NEW;
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
-- TRIGGERS (drop first to avoid duplicates)
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
-- SAMPLE DATA (only insert if tables are empty)
-- ============================================================================

-- Insert organizations if table is empty
INSERT INTO organizations (id, name, slug, type, subscription_status)
SELECT * FROM (VALUES
    ('11111111-1111-1111-1111-111111111111'::UUID, 'Democratic Alliance Party', 'dap', 'political_party', 'active'::VARCHAR),
    ('22222222-2222-2222-2222-222222222222'::UUID, 'Progressive Coalition', 'pc', 'political_party', 'trial'::VARCHAR),
    ('33333333-3333-3333-3333-333333333333'::UUID, 'Citizens Forum', 'cf', 'ngo', 'active'::VARCHAR)
) AS v(id, name, slug, type, subscription_status)
WHERE NOT EXISTS (SELECT 1 FROM organizations);

-- Insert users if table is empty
INSERT INTO users (id, organization_id, email, username, full_name, role, is_active, is_verified)
SELECT * FROM (VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'::UUID, '11111111-1111-1111-1111-111111111111'::UUID, 'super@dap.org', 'superadmin', 'Super Admin', 'superadmin', true, true),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID, '11111111-1111-1111-1111-111111111111'::UUID, 'admin@dap.org', 'admin_dap', 'John Admin', 'admin', true, true),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID, '11111111-1111-1111-1111-111111111111'::UUID, 'manager@dap.org', 'manager_dap', 'Jane Manager', 'manager', true, true),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd'::UUID, '11111111-1111-1111-1111-111111111111'::UUID, 'analyst@dap.org', 'analyst_dap', 'Bob Analyst', 'analyst', true, true),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'::UUID, '11111111-1111-1111-1111-111111111111'::UUID, 'user@dap.org', 'user_dap', 'Alice User', 'user', true, true),
    ('ffffffff-ffff-ffff-ffff-ffffffffffff'::UUID, '11111111-1111-1111-1111-111111111111'::UUID, 'viewer@dap.org', 'viewer_dap', 'Charlie Viewer', 'viewer', true, true),
    ('10101010-1010-1010-1010-101010101010'::UUID, '22222222-2222-2222-2222-222222222222'::UUID, 'admin@pc.org', 'admin_pc', 'Sarah Admin', 'admin', true, true),
    ('20202020-2020-2020-2020-202020202020'::UUID, '33333333-3333-3333-3333-333333333333'::UUID, 'admin@cf.org', 'admin_cf', 'Mike Admin', 'admin', true, true)
) AS v(id, organization_id, email, username, full_name, role, is_active, is_verified)
WHERE NOT EXISTS (SELECT 1 FROM users);

-- Insert permissions if table is empty
INSERT INTO user_permissions (user_id, permission_key, granted_by)
SELECT * FROM (VALUES
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID, 'users.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID, 'users.create', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID, 'campaigns.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc'::UUID, 'field_workers.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd'::UUID, 'analytics.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd'::UUID, 'reports.generate', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd'::UUID, 'social.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'::UUID)
) AS v(user_id, permission_key, granted_by)
WHERE NOT EXISTS (SELECT 1 FROM user_permissions);

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT 'Phase 1 Migration Complete!' as status;
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
  AND table_name IN ('organizations', 'users', 'user_permissions', 'audit_logs')
ORDER BY table_name;
