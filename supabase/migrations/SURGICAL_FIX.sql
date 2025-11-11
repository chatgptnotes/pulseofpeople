-- ============================================================================
-- SURGICAL FIX - Only fix the 4 Phase 1 tables
-- ============================================================================
-- This leaves all your other tables (social_posts, influencers, etc.) intact
-- Only recreates: organizations, users, user_permissions, audit_logs
-- ============================================================================

-- Drop only the 4 tables we're creating (leave everything else alone)
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS user_permissions CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- Don't drop shared functions - they're used by other tables!
-- We'll create our own versions or use what exists

-- Enable extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- PHASE 1: CORE ENTITIES
-- ============================================================================

CREATE TABLE organizations (
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

CREATE TABLE users (
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
    password_changed_at TIMESTAMPTZ
);

CREATE TABLE user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_key VARCHAR(100) NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ,
    UNIQUE(user_id, permission_key)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
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

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_active ON organizations(is_active);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);
CREATE INDEX idx_user_permissions_user ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_key ON user_permissions(permission_key);
CREATE INDEX idx_audit_logs_org_created ON audit_logs(organization_id, created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- ============================================================================
-- ENABLE RLS
-- ============================================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- FUNCTIONS (create if not exists, replace if exists)
-- ============================================================================

-- update_updated_at_column probably already exists from other tables, so just use it
-- If it doesn't exist, create it
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
        CREATE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $func$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $func$ LANGUAGE plpgsql;
    END IF;
END $$;

-- Create our specific functions
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(permission_key VARCHAR) AS $$
BEGIN
    RETURN QUERY SELECT up.permission_key FROM user_permissions up
    WHERE up.user_id = p_user_id AND (up.expires_at IS NULL OR up.expires_at > NOW());
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION has_permission(p_user_id UUID, p_permission VARCHAR)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS(SELECT 1 FROM user_permissions WHERE user_id = p_user_id
        AND permission_key = p_permission AND (expires_at IS NULL OR expires_at > NOW()));
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- RLS POLICIES
-- ============================================================================

CREATE POLICY "Users can view their organization" ON organizations FOR SELECT
    USING (id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can view organization members" ON users FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Users can view their permissions" ON user_permissions FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can view audit logs in their organization" ON audit_logs FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "System can insert audit logs" ON audit_logs FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

INSERT INTO organizations (id, name, slug, type, subscription_status, is_active) VALUES
('11111111-1111-1111-1111-111111111111', 'Democratic Alliance Party', 'dap', 'political_party', 'active', true),
('22222222-2222-2222-2222-222222222222', 'Progressive Coalition', 'pc', 'political_party', 'trial', true),
('33333333-3333-3333-3333-333333333333', 'Citizens Forum', 'cf', 'ngo', 'active', true);

INSERT INTO users (id, organization_id, email, username, full_name, role, is_active, is_verified) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111', 'super@dap.org', 'superadmin', 'Super Admin', 'superadmin', true, true),
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111', 'admin@dap.org', 'admin_dap', 'John Admin', 'admin', true, true),
('cccccccc-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111', 'manager@dap.org', 'manager_dap', 'Jane Manager', 'manager', true, true),
('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111', 'analyst@dap.org', 'analyst_dap', 'Bob Analyst', 'analyst', true, true),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '11111111-1111-1111-1111-111111111111', 'user@dap.org', 'user_dap', 'Alice User', 'user', true, true),
('ffffffff-ffff-ffff-ffff-ffffffffffff', '11111111-1111-1111-1111-111111111111', 'viewer@dap.org', 'viewer_dap', 'Charlie Viewer', 'viewer', true, true),
('10101010-1010-1010-1010-101010101010', '22222222-2222-2222-2222-222222222222', 'admin@pc.org', 'admin_pc', 'Sarah Admin', 'admin', true, true),
('20202020-2020-2020-2020-202020202020', '33333333-3333-3333-3333-333333333333', 'admin@cf.org', 'admin_cf', 'Mike Admin', 'admin', true, true);

INSERT INTO user_permissions (user_id, permission_key, granted_by) VALUES
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'users.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'users.create', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'campaigns.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'field_workers.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'analytics.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'reports.generate', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'social.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '✅ Phase 1 Complete!' as status;
SELECT 'Your other tables (social_posts, influencers, etc.) are still intact!' as note;

SELECT table_name,
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('organizations', 'users', 'user_permissions', 'audit_logs')
ORDER BY table_name;
