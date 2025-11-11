-- ============================================================================
-- PULSE OF PEOPLE - PHASE 1: CORE ENTITIES MIGRATION
-- ============================================================================
-- Created: 2025-11-09
-- Purpose: Foundation tables for organizations, users, permissions, audit logs
-- Dependencies: None (this is the first migration)
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable PostGIS for geographic data (needed for later phases)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- CORE: Organizations & Tenants
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

    -- Subscription info
    subscription_status VARCHAR(50) DEFAULT 'trial' CHECK (subscription_status IN ('trial', 'active', 'suspended', 'cancelled')),
    subscription_start_date DATE,
    subscription_end_date DATE,
    monthly_fee DECIMAL(10, 2) DEFAULT 6000.00,

    -- Contact info
    primary_contact_name VARCHAR(255),
    primary_contact_email VARCHAR(255),
    primary_contact_phone VARCHAR(20),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_active ON organizations(is_active);

COMMENT ON TABLE organizations IS 'Top-level organizations/tenants in the platform';

-- ============================================================================
-- CORE: Users & Authentication
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255), -- Managed by Django, nullable for SSO users

    -- Profile
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    avatar_url TEXT,
    bio TEXT,

    -- Role & Permissions
    role VARCHAR(50) NOT NULL DEFAULT 'user' CHECK (role IN (
        'superadmin',   -- Platform owner, all permissions
        'admin',        -- Organization owner, manage organization
        'manager',      -- Manage teams and campaigns
        'analyst',      -- View analytics, generate reports
        'user',         -- Standard user, manage assigned tasks
        'viewer',       -- Read-only access
        'volunteer'     -- Field operations only
    )),

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    email_verified_at TIMESTAMPTZ,
    last_login TIMESTAMPTZ,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Preferences
    preferences JSONB DEFAULT '{}'::jsonb,

    -- Security
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ,

    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_active ON users(is_active);

COMMENT ON TABLE users IS 'Platform users with role-based access control';

-- ============================================================================
-- PERMISSIONS & ACCESS CONTROL
-- ============================================================================

CREATE TABLE user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_key VARCHAR(100) NOT NULL,

    -- Permission categories:
    -- users.*         - User management
    -- voters.*        - Voter database
    -- booths.*        - Polling booth management
    -- social.*        - Social media monitoring
    -- media.*         - Media monitoring
    -- analytics.*     - Analytics and insights
    -- reports.*       - Report generation
    -- campaigns.*     - Campaign management
    -- field_workers.* - Field operations
    -- alerts.*        - Alert management

    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expires_at TIMESTAMPTZ,

    UNIQUE(user_id, permission_key)
);

CREATE INDEX idx_user_permissions_user ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_key ON user_permissions(permission_key);

COMMENT ON TABLE user_permissions IS 'Granular user permissions beyond role-based access';

-- ============================================================================
-- AUDIT LOGS
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Action details
    action VARCHAR(100) NOT NULL CHECK (action IN (
        'create', 'update', 'delete', 'view',
        'login', 'logout', 'login_failed',
        'export', 'import', 'bulk_upload',
        'permission_granted', 'permission_revoked',
        'status_changed', 'password_reset'
    )),

    -- Resource details
    resource_type VARCHAR(100),
    resource_id UUID,
    resource_name VARCHAR(255),

    -- Change tracking
    changes JSONB,
    previous_values JSONB,
    new_values JSONB,

    -- Request metadata
    ip_address INET,
    user_agent TEXT,
    request_method VARCHAR(10),
    request_path TEXT,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),

    -- Additional context
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_audit_logs_org_created ON audit_logs(organization_id, created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

COMMENT ON TABLE audit_logs IS 'Complete audit trail for all user actions and system events';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Organizations: Users can only see their own organization
CREATE POLICY "Users can view their organization"
    ON organizations FOR SELECT
    USING (id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Superadmins can view all organizations"
    ON organizations FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM users
        WHERE id = auth.uid() AND role = 'superadmin'
    ));

CREATE POLICY "Admins can update their organization"
    ON organizations FOR UPDATE
    USING (id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'superadmin')
    ));

-- Users: Can only see users in their organization
CREATE POLICY "Users can view organization members"
    ON users FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Admins can create users in their organization"
    ON users FOR INSERT
    WITH CHECK (
        organization_id IN (
            SELECT organization_id FROM users
            WHERE id = auth.uid() AND role IN ('admin', 'superadmin')
        )
    );

CREATE POLICY "Admins can update users in their organization"
    ON users FOR UPDATE
    USING (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
    ));

CREATE POLICY "Users can update their own profile"
    ON users FOR UPDATE
    USING (id = auth.uid());

-- Permissions: Users can view their own permissions
CREATE POLICY "Users can view their permissions"
    ON user_permissions FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Admins can view all permissions in org"
    ON user_permissions FOR SELECT
    USING (user_id IN (
        SELECT id FROM users
        WHERE organization_id IN (
            SELECT organization_id FROM users WHERE id = auth.uid()
        ) AND id IN (
            SELECT id FROM users WHERE id = auth.uid() AND role IN ('admin', 'superadmin')
        )
    ));

-- Audit Logs: Users can view logs in their organization
CREATE POLICY "Users can view audit logs in their organization"
    ON audit_logs FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "System can insert audit logs"
    ON audit_logs FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function: Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Log user creation to audit log
CREATE OR REPLACE FUNCTION log_user_creation()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_logs (
        organization_id,
        user_id,
        action,
        resource_type,
        resource_id,
        resource_name,
        new_values,
        ip_address
    ) VALUES (
        NEW.organization_id,
        NEW.created_by,
        'create',
        'user',
        NEW.id,
        NEW.full_name,
        jsonb_build_object(
            'email', NEW.email,
            'role', NEW.role,
            'username', NEW.username
        ),
        inet_client_addr()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_log_user_creation
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE FUNCTION log_user_creation();

-- Function: Check role hierarchy (prevent privilege escalation)
CREATE OR REPLACE FUNCTION check_role_hierarchy()
RETURNS TRIGGER AS $$
DECLARE
    creator_role VARCHAR(50);
    role_hierarchy_map JSONB;
BEGIN
    -- Define role hierarchy (higher number = higher privilege)
    role_hierarchy_map := '{
        "volunteer": 1,
        "viewer": 2,
        "user": 3,
        "analyst": 4,
        "manager": 5,
        "admin": 6,
        "superadmin": 7
    }'::jsonb;

    -- Get creator's role
    SELECT role INTO creator_role FROM users WHERE id = NEW.created_by;

    -- Superadmins can create any role
    IF creator_role = 'superadmin' THEN
        RETURN NEW;
    END IF;

    -- Others can only create roles below their level
    IF (role_hierarchy_map->>creator_role)::int <= (role_hierarchy_map->>NEW.role)::int THEN
        RAISE EXCEPTION 'Cannot create user with role % as %', NEW.role, creator_role;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_check_role_hierarchy
    BEFORE INSERT ON users
    FOR EACH ROW
    WHEN (NEW.created_by IS NOT NULL)
    EXECUTE FUNCTION check_role_hierarchy();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Get user's effective permissions
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(permission_key VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT up.permission_key
    FROM user_permissions up
    WHERE up.user_id = p_user_id
      AND (up.expires_at IS NULL OR up.expires_at > NOW());
END;
$$ LANGUAGE plpgsql;

-- Function: Check if user has permission
CREATE OR REPLACE FUNCTION has_permission(p_user_id UUID, p_permission VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    has_perm BOOLEAN;
BEGIN
    SELECT EXISTS(
        SELECT 1 FROM user_permissions
        WHERE user_id = p_user_id
          AND permission_key = p_permission
          AND (expires_at IS NULL OR expires_at > NOW())
    ) INTO has_perm;

    RETURN has_perm;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA FOR DEVELOPMENT
-- ============================================================================

-- Insert sample organization
INSERT INTO organizations (id, name, slug, type, subscription_status)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Democratic Alliance Party', 'dap', 'political_party', 'active'),
    ('22222222-2222-2222-2222-222222222222', 'Progressive Coalition', 'pc', 'political_party', 'trial'),
    ('33333333-3333-3333-3333-333333333333', 'Citizens Forum', 'cf', 'ngo', 'active');

-- Insert sample users (password: 'password123' - hashed with Django)
INSERT INTO users (id, organization_id, email, username, full_name, role, is_active, is_verified)
VALUES
    -- Organization 1: DAP
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', '11111111-1111-1111-1111-111111111111',
     'super@dap.org', 'superadmin', 'Super Admin', 'superadmin', true, true),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', '11111111-1111-1111-1111-111111111111',
     'admin@dap.org', 'admin_dap', 'John Admin', 'admin', true, true),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '11111111-1111-1111-1111-111111111111',
     'manager@dap.org', 'manager_dap', 'Jane Manager', 'manager', true, true),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', '11111111-1111-1111-1111-111111111111',
     'analyst@dap.org', 'analyst_dap', 'Bob Analyst', 'analyst', true, true),
    ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', '11111111-1111-1111-1111-111111111111',
     'user@dap.org', 'user_dap', 'Alice User', 'user', true, true),
    ('ffffffff-ffff-ffff-ffff-ffffffffffff', '11111111-1111-1111-1111-111111111111',
     'viewer@dap.org', 'viewer_dap', 'Charlie Viewer', 'viewer', true, true),

    -- Organization 2: PC
    ('10101010-1010-1010-1010-101010101010', '22222222-2222-2222-2222-222222222222',
     'admin@pc.org', 'admin_pc', 'Sarah Admin', 'admin', true, true),

    -- Organization 3: CF
    ('20202020-2020-2020-2020-202020202020', '33333333-3333-3333-3333-333333333333',
     'admin@cf.org', 'admin_cf', 'Mike Admin', 'admin', true, true);

-- Insert sample permissions
INSERT INTO user_permissions (user_id, permission_key, granted_by)
VALUES
    -- Manager permissions
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'users.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'users.create', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'campaigns.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', 'field_workers.manage', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),

    -- Analyst permissions
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'analytics.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'reports.generate', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
    ('dddddddd-dddd-dddd-dddd-dddddddddddd', 'social.view', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb');

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('organizations', 'users', 'user_permissions', 'audit_logs')
ORDER BY table_name;

-- Verify sample data
SELECT
    o.name AS organization,
    COUNT(u.id) AS user_count,
    array_agg(DISTINCT u.role) AS roles
FROM organizations o
LEFT JOIN users u ON o.id = u.organization_id
GROUP BY o.id, o.name
ORDER BY o.name;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

/*
-- To rollback this migration:

DROP TRIGGER IF EXISTS trigger_check_role_hierarchy ON users;
DROP TRIGGER IF EXISTS trigger_log_user_creation ON users;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_organizations_updated_at ON organizations;

DROP FUNCTION IF EXISTS check_role_hierarchy();
DROP FUNCTION IF EXISTS log_user_creation();
DROP FUNCTION IF EXISTS update_updated_at_column();
DROP FUNCTION IF EXISTS has_permission(UUID, VARCHAR);
DROP FUNCTION IF EXISTS get_user_permissions(UUID);

DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS user_permissions CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
*/
