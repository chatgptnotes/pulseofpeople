-- =====================================================
-- ROLE-BASED ACCESS CONTROL (RBAC) SYSTEM
-- Multi-Tenant Support with 3-Tier Role Hierarchy
-- Generated: 2025-10-28
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. UPDATE USERS TABLE FOR MULTI-TENANT RBAC
-- =====================================================

-- Add new columns to users table
ALTER TABLE users
ADD COLUMN IF NOT EXISTS organization_id UUID,
ADD COLUMN IF NOT EXISTS tenant_id TEXT, -- References tenant registry
ADD COLUMN IF NOT EXISTS is_super_admin BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS last_role_change TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS role_changed_by UUID;

-- Update role enum to include new roles
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users
ADD CONSTRAINT users_role_check CHECK (
    role IN (
        'super_admin',    -- Platform-level administrator
        'admin',          -- Organization administrator
        'manager',        -- Team manager
        'analyst',        -- Data analyst
        'viewer',         -- Read-only user
        'user',           -- Regular user
        'ward-coordinator',
        'social-media',
        'survey-team',
        'truth-team',
        'volunteer'       -- Field worker
    )
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_organization_id ON users(organization_id);
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);
CREATE INDEX IF NOT EXISTS idx_users_is_super_admin ON users(is_super_admin);

-- =====================================================
-- 2. ORGANIZATIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id TEXT UNIQUE NOT NULL, -- Links to tenant registry
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    logo_url TEXT,
    website TEXT,

    -- Organization settings
    settings JSONB DEFAULT '{}'::JSONB,
    features JSONB DEFAULT '{}'::JSONB, -- Feature flags
    branding JSONB DEFAULT '{}'::JSONB, -- Custom branding

    -- Subscription & billing
    subscription_tier TEXT DEFAULT 'basic' CHECK (
        subscription_tier IN ('trial', 'basic', 'standard', 'premium', 'enterprise')
    ),
    subscription_status TEXT DEFAULT 'active' CHECK (
        subscription_status IN ('active', 'suspended', 'cancelled', 'expired')
    ),
    trial_ends_at TIMESTAMPTZ,
    subscription_ends_at TIMESTAMPTZ,

    -- Contact information
    contact_name TEXT,
    contact_email TEXT,
    contact_phone TEXT,

    -- Location
    state TEXT,
    region TEXT,
    coverage_area TEXT[],

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending')),
    is_active BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_by UUID REFERENCES users(id),

    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_organizations_tenant_id ON organizations(tenant_id);
CREATE INDEX idx_organizations_slug ON organizations(slug);
CREATE INDEX idx_organizations_status ON organizations(status);
CREATE INDEX idx_organizations_subscription_tier ON organizations(subscription_tier);

-- =====================================================
-- 3. ROLES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    level INTEGER NOT NULL, -- Hierarchy level (1=highest)
    is_system_role BOOLEAN DEFAULT FALSE, -- Cannot be deleted
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE, -- NULL for platform roles

    -- Role configuration
    can_manage_users BOOLEAN DEFAULT FALSE,
    can_manage_settings BOOLEAN DEFAULT FALSE,
    can_view_analytics BOOLEAN DEFAULT FALSE,
    can_export_data BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_roles_name ON roles(name);
CREATE INDEX idx_roles_organization_id ON roles(organization_id);
CREATE INDEX idx_roles_level ON roles(level);

-- Insert default system roles
INSERT INTO roles (name, display_name, description, level, is_system_role, can_manage_users, can_manage_settings, can_view_analytics, can_export_data)
VALUES
    ('super_admin', 'Super Administrator', 'Platform-level administrator with full access to all organizations', 1, TRUE, TRUE, TRUE, TRUE, TRUE),
    ('admin', 'Administrator', 'Organization administrator with full access to their organization', 2, TRUE, TRUE, TRUE, TRUE, TRUE),
    ('manager', 'Manager', 'Team manager with user management capabilities', 3, TRUE, TRUE, FALSE, TRUE, TRUE),
    ('analyst', 'Analyst', 'Data analyst with analytics and reporting access', 4, TRUE, FALSE, FALSE, TRUE, TRUE),
    ('user', 'User', 'Regular user with standard access', 5, TRUE, FALSE, FALSE, TRUE, FALSE),
    ('viewer', 'Viewer', 'Read-only access to dashboards', 6, TRUE, FALSE, FALSE, TRUE, FALSE),
    ('volunteer', 'Volunteer', 'Field worker with data submission capabilities', 7, TRUE, FALSE, FALSE, FALSE, FALSE)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- 4. PERMISSIONS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL CHECK (
        category IN ('users', 'data', 'analytics', 'settings', 'billing', 'system')
    ),
    is_system_permission BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_permissions_name ON permissions(name);
CREATE INDEX idx_permissions_category ON permissions(category);

-- Insert default permissions
INSERT INTO permissions (name, display_name, description, category, is_system_permission)
VALUES
    -- User management
    ('view_users', 'View Users', 'View list of users in organization', 'users', TRUE),
    ('create_users', 'Create Users', 'Invite and create new users', 'users', TRUE),
    ('edit_users', 'Edit Users', 'Edit user information and roles', 'users', TRUE),
    ('delete_users', 'Delete Users', 'Remove users from organization', 'users', TRUE),
    ('manage_roles', 'Manage Roles', 'Create and assign roles', 'users', TRUE),

    -- Data management
    ('view_dashboard', 'View Dashboard', 'Access main dashboard', 'data', TRUE),
    ('view_analytics', 'View Analytics', 'Access analytics and reports', 'analytics', TRUE),
    ('view_reports', 'View Reports', 'Access detailed reports', 'analytics', TRUE),
    ('export_data', 'Export Data', 'Export data to CSV/Excel', 'data', TRUE),
    ('import_data', 'Import Data', 'Import data from files', 'data', TRUE),
    ('create_surveys', 'Create Surveys', 'Create and manage surveys', 'data', TRUE),
    ('view_surveys', 'View Surveys', 'View survey results', 'data', TRUE),

    -- Voter management
    ('view_voters', 'View Voters', 'Access voter database', 'data', TRUE),
    ('edit_voters', 'Edit Voters', 'Edit voter information', 'data', TRUE),
    ('delete_voters', 'Delete Voters', 'Remove voter records', 'data', TRUE),

    -- Field workers
    ('view_field_workers', 'View Field Workers', 'View field worker list', 'users', TRUE),
    ('manage_field_workers', 'Manage Field Workers', 'Add/remove field workers', 'users', TRUE),
    ('view_field_reports', 'View Field Reports', 'View reports from field', 'data', TRUE),
    ('submit_field_reports', 'Submit Field Reports', 'Submit field reports', 'data', TRUE),

    -- Social media
    ('view_social_media', 'View Social Media', 'Access social media monitoring', 'data', TRUE),
    ('manage_social_channels', 'Manage Social Channels', 'Add/remove social channels', 'settings', TRUE),

    -- Competitor analysis
    ('view_competitor_analysis', 'View Competitor Analysis', 'Access competitor data', 'analytics', TRUE),

    -- AI & Insights
    ('view_ai_insights', 'View AI Insights', 'Access AI-generated insights', 'analytics', TRUE),
    ('generate_ai_insights', 'Generate AI Insights', 'Trigger AI analysis', 'analytics', TRUE),

    -- Settings & Configuration
    ('view_settings', 'View Settings', 'View organization settings', 'settings', TRUE),
    ('edit_settings', 'Edit Settings', 'Modify organization settings', 'settings', TRUE),
    ('manage_billing', 'Manage Billing', 'Access billing and subscription', 'billing', TRUE),

    -- Alerts
    ('view_alerts', 'View Alerts', 'View system alerts', 'data', TRUE),
    ('manage_alerts', 'Manage Alerts', 'Create and configure alerts', 'settings', TRUE),

    -- System (Super Admin only)
    ('manage_organizations', 'Manage Organizations', 'Create/delete organizations', 'system', TRUE),
    ('view_all_data', 'View All Data', 'Access data across all organizations', 'system', TRUE),
    ('manage_system_settings', 'Manage System Settings', 'Configure platform-wide settings', 'system', TRUE),
    ('view_audit_logs', 'View Audit Logs', 'Access system audit logs', 'system', TRUE)
ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- 5. ROLE_PERMISSIONS TABLE (Many-to-Many)
-- =====================================================

CREATE TABLE IF NOT EXISTS role_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_by UUID REFERENCES users(id),

    UNIQUE(role_id, permission_id)
);

CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX idx_role_permissions_permission_id ON role_permissions(permission_id);

-- Assign permissions to default roles
-- Super Admin (all permissions)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'super_admin'
ON CONFLICT DO NOTHING;

-- Admin (all except system permissions)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'admin' AND p.category != 'system'
ON CONFLICT DO NOTHING;

-- Manager (user and basic data management)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'manager' AND p.name IN (
    'view_users', 'create_users', 'edit_users',
    'view_dashboard', 'view_analytics', 'view_reports',
    'view_field_workers', 'manage_field_workers',
    'view_field_reports', 'view_surveys', 'view_alerts'
)
ON CONFLICT DO NOTHING;

-- Analyst (analytics and reporting)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'analyst' AND p.name IN (
    'view_dashboard', 'view_analytics', 'view_reports', 'export_data',
    'view_surveys', 'view_field_reports', 'view_social_media',
    'view_competitor_analysis', 'view_ai_insights', 'view_alerts'
)
ON CONFLICT DO NOTHING;

-- User (basic access)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'user' AND p.name IN (
    'view_dashboard', 'view_analytics', 'view_reports',
    'view_surveys', 'view_field_reports', 'view_alerts'
)
ON CONFLICT DO NOTHING;

-- Viewer (read-only)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'viewer' AND p.name IN (
    'view_dashboard', 'view_analytics', 'view_reports', 'view_alerts'
)
ON CONFLICT DO NOTHING;

-- Volunteer (field work)
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r, permissions p
WHERE r.name = 'volunteer' AND p.name IN (
    'view_dashboard', 'submit_field_reports', 'view_surveys'
)
ON CONFLICT DO NOTHING;

-- =====================================================
-- 6. USER_PERMISSIONS TABLE (Custom User Permissions)
-- =====================================================

CREATE TABLE IF NOT EXISTS user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    granted BOOLEAN DEFAULT TRUE, -- FALSE to revoke specific permission

    granted_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    granted_by UUID REFERENCES users(id),
    expires_at TIMESTAMPTZ, -- Optional expiration

    UNIQUE(user_id, permission_id)
);

CREATE INDEX idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_permission_id ON user_permissions(permission_id);

-- =====================================================
-- 7. USER_ORGANIZATIONS TABLE (User-Org Relationship)
-- =====================================================

CREATE TABLE IF NOT EXISTS user_organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id),

    is_primary BOOLEAN DEFAULT FALSE, -- Primary organization for user
    joined_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    invited_by UUID REFERENCES users(id),

    UNIQUE(user_id, organization_id)
);

CREATE INDEX idx_user_organizations_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_organizations_organization_id ON user_organizations(organization_id);
CREATE INDEX idx_user_organizations_role_id ON user_organizations(role_id);

-- =====================================================
-- 8. AUDIT LOG FOR RBAC CHANGES
-- =====================================================

CREATE TABLE IF NOT EXISTS rbac_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action TEXT NOT NULL CHECK (
        action IN (
            'role_assigned', 'role_revoked', 'permission_granted',
            'permission_revoked', 'user_invited', 'user_removed',
            'organization_created', 'organization_updated'
        )
    ),
    actor_id UUID REFERENCES users(id), -- Who performed the action
    target_user_id UUID REFERENCES users(id), -- Affected user
    target_organization_id UUID REFERENCES organizations(id), -- Affected org

    old_value JSONB,
    new_value JSONB,
    metadata JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_rbac_audit_log_action ON rbac_audit_log(action);
CREATE INDEX idx_rbac_audit_log_actor_id ON rbac_audit_log(actor_id);
CREATE INDEX idx_rbac_audit_log_target_user_id ON rbac_audit_log(target_user_id);
CREATE INDEX idx_rbac_audit_log_created_at ON rbac_audit_log(created_at DESC);

-- =====================================================
-- 9. ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE rbac_audit_log ENABLE ROW LEVEL SECURITY;

-- Organizations: Super admins see all, others see their own
CREATE POLICY "Super admins can view all organizations"
    ON organizations FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.is_super_admin = TRUE
        )
    );

CREATE POLICY "Users can view their organization"
    ON organizations FOR SELECT
    TO authenticated
    USING (
        id IN (
            SELECT organization_id FROM user_organizations
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Super admins can manage organizations"
    ON organizations FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.is_super_admin = TRUE
        )
    );

-- Users: Can only view users in their organization
CREATE POLICY "Users can view users in their organization"
    ON users FOR SELECT
    TO authenticated
    USING (
        organization_id IN (
            SELECT organization_id FROM user_organizations
            WHERE user_id = auth.uid()
        )
        OR id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM users u
            WHERE u.id = auth.uid() AND u.is_super_admin = TRUE
        )
    );

-- Permissions: Everyone can view permissions
CREATE POLICY "Everyone can view permissions"
    ON permissions FOR SELECT
    TO authenticated
    USING (TRUE);

-- User Organizations: Users can view their memberships
CREATE POLICY "Users can view their organization memberships"
    ON user_organizations FOR SELECT
    TO authenticated
    USING (
        user_id = auth.uid()
        OR organization_id IN (
            SELECT organization_id FROM user_organizations uo
            JOIN users u ON u.id = uo.user_id
            WHERE uo.user_id = auth.uid()
            AND u.role IN ('admin', 'manager')
        )
        OR EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.is_super_admin = TRUE
        )
    );

-- =====================================================
-- 10. HELPER FUNCTIONS
-- =====================================================

-- Function to check if user has a specific permission
CREATE OR REPLACE FUNCTION user_has_permission(
    p_user_id UUID,
    p_permission_name TEXT
) RETURNS BOOLEAN AS $$
DECLARE
    has_perm BOOLEAN;
BEGIN
    -- Super admins have all permissions
    SELECT is_super_admin INTO has_perm
    FROM users
    WHERE id = p_user_id;

    IF has_perm THEN
        RETURN TRUE;
    END IF;

    -- Check role permissions
    SELECT EXISTS (
        SELECT 1
        FROM user_organizations uo
        JOIN role_permissions rp ON rp.role_id = uo.role_id
        JOIN permissions p ON p.id = rp.permission_id
        WHERE uo.user_id = p_user_id
        AND p.name = p_permission_name
    ) INTO has_perm;

    IF has_perm THEN
        RETURN TRUE;
    END IF;

    -- Check custom user permissions
    SELECT granted INTO has_perm
    FROM user_permissions up
    JOIN permissions p ON p.id = up.permission_id
    WHERE up.user_id = p_user_id
    AND p.name = p_permission_name
    AND (up.expires_at IS NULL OR up.expires_at > NOW());

    RETURN COALESCE(has_perm, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get user's effective permissions
CREATE OR REPLACE FUNCTION get_user_permissions(p_user_id UUID)
RETURNS TABLE(permission_name TEXT, permission_display TEXT) AS $$
BEGIN
    -- Super admins get all permissions
    IF EXISTS (SELECT 1 FROM users WHERE id = p_user_id AND is_super_admin = TRUE) THEN
        RETURN QUERY
        SELECT p.name, p.display_name
        FROM permissions p;
    ELSE
        -- Get permissions from role + custom permissions
        RETURN QUERY
        SELECT DISTINCT p.name, p.display_name
        FROM permissions p
        WHERE p.id IN (
            -- Role permissions
            SELECT rp.permission_id
            FROM user_organizations uo
            JOIN role_permissions rp ON rp.role_id = uo.role_id
            WHERE uo.user_id = p_user_id

            UNION

            -- Custom user permissions
            SELECT up.permission_id
            FROM user_permissions up
            WHERE up.user_id = p_user_id
            AND up.granted = TRUE
            AND (up.expires_at IS NULL OR up.expires_at > NOW())
        );
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is admin of organization
CREATE OR REPLACE FUNCTION is_organization_admin(
    p_user_id UUID,
    p_organization_id UUID
) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM user_organizations uo
        JOIN users u ON u.id = uo.user_id
        WHERE uo.user_id = p_user_id
        AND uo.organization_id = p_organization_id
        AND u.role IN ('admin', 'super_admin')
    ) OR EXISTS (
        SELECT 1 FROM users WHERE id = p_user_id AND is_super_admin = TRUE
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 11. TRIGGERS FOR AUTO-UPDATING TIMESTAMPS
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 12. VIEWS FOR EASY QUERYING
-- =====================================================

-- View: User permissions overview
CREATE OR REPLACE VIEW user_permissions_overview AS
SELECT
    u.id as user_id,
    u.name as user_name,
    u.email as user_email,
    u.role as user_role,
    u.is_super_admin,
    o.id as organization_id,
    o.name as organization_name,
    r.name as role_name,
    r.display_name as role_display_name,
    ARRAY_AGG(DISTINCT p.name) as permissions
FROM users u
LEFT JOIN user_organizations uo ON uo.user_id = u.id
LEFT JOIN organizations o ON o.id = uo.organization_id
LEFT JOIN roles r ON r.id = uo.role_id
LEFT JOIN role_permissions rp ON rp.role_id = r.id
LEFT JOIN permissions p ON p.id = rp.permission_id
GROUP BY u.id, u.name, u.email, u.role, u.is_super_admin, o.id, o.name, r.name, r.display_name;

-- View: Organization member counts
CREATE OR REPLACE VIEW organization_member_counts AS
SELECT
    o.id as organization_id,
    o.name as organization_name,
    o.tenant_id,
    COUNT(DISTINCT uo.user_id) as total_members,
    COUNT(DISTINCT CASE WHEN u.role = 'admin' THEN u.id END) as admin_count,
    COUNT(DISTINCT CASE WHEN u.role = 'user' THEN u.id END) as user_count,
    COUNT(DISTINCT CASE WHEN u.role = 'volunteer' THEN u.id END) as volunteer_count,
    COUNT(DISTINCT CASE WHEN u.status = 'active' THEN u.id END) as active_members
FROM organizations o
LEFT JOIN user_organizations uo ON uo.organization_id = o.id
LEFT JOIN users u ON u.id = uo.user_id
GROUP BY o.id, o.name, o.tenant_id;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Insert a comment for tracking
COMMENT ON TABLE organizations IS 'Multi-tenant organizations/tenants';
COMMENT ON TABLE roles IS 'Role definitions with hierarchy';
COMMENT ON TABLE permissions IS 'Granular permission definitions';
COMMENT ON TABLE role_permissions IS 'Maps roles to their permissions';
COMMENT ON TABLE user_permissions IS 'Custom user-specific permissions';
COMMENT ON TABLE user_organizations IS 'User membership in organizations';
COMMENT ON TABLE rbac_audit_log IS 'Audit trail for RBAC changes';