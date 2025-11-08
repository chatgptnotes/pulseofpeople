-- =====================================================
-- SINGLE DATABASE MULTI-TENANCY MIGRATION
-- Update schema for single-DB approach with subdomain routing
-- Date: 2025-10-29
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- 1. UPDATE TENANTS TABLE FOR SINGLE-DB MULTI-TENANCY
-- =====================================================

-- Drop columns related to separate database per tenant (if they exist)
ALTER TABLE IF EXISTS tenants
DROP COLUMN IF EXISTS supabase_url,
DROP COLUMN IF EXISTS supabase_project_id,
DROP COLUMN IF EXISTS supabase_anon_key,
DROP COLUMN IF EXISTS supabase_region;

-- Add new columns for single-DB multi-tenancy
ALTER TABLE tenants
ADD COLUMN IF NOT EXISTS organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS subdomain TEXT UNIQUE,  -- kerala, tamilnadu, etc.
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id),  -- Which admin created this tenant
ADD COLUMN IF NOT EXISTS admin_user_id UUID REFERENCES users(id);  -- Primary tenant admin

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_tenants_organization_id ON tenants(organization_id);
CREATE INDEX IF NOT EXISTS idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX IF NOT EXISTS idx_tenants_created_by ON tenants(created_by);

-- Update tenant_credentials table (no longer need separate DB credentials)
DROP TABLE IF EXISTS tenant_credentials CASCADE;

-- =====================================================
-- 2. ENSURE ALL DOMAIN TABLES HAVE TENANT_ID
-- =====================================================

-- List of tables that need tenant_id for data isolation
-- Add tenant_id column to each table if it doesn't exist

-- Users table (already has tenant_id from RBAC migration)
-- Just ensure index exists
CREATE INDEX IF NOT EXISTS idx_users_tenant_id ON users(tenant_id);

-- Sentiment data table (if exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'sentiment_data') THEN
        ALTER TABLE sentiment_data ADD COLUMN IF NOT EXISTS tenant_id TEXT;
        CREATE INDEX IF NOT EXISTS idx_sentiment_data_tenant_id ON sentiment_data(tenant_id);
    END IF;
END $$;

-- Social posts table
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'social_posts') THEN
        ALTER TABLE social_posts ADD COLUMN IF NOT EXISTS tenant_id TEXT;
        CREATE INDEX IF NOT EXISTS idx_social_posts_tenant_id ON social_posts(tenant_id);
    END IF;
END $$;

-- Surveys table
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'surveys') THEN
        ALTER TABLE surveys ADD COLUMN IF NOT EXISTS tenant_id TEXT;
        CREATE INDEX IF NOT EXISTS idx_surveys_tenant_id ON surveys(tenant_id);
    END IF;
END $$;

-- Survey responses table
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'survey_responses') THEN
        ALTER TABLE survey_responses ADD COLUMN IF NOT EXISTS tenant_id TEXT;
        CREATE INDEX IF NOT EXISTS idx_survey_responses_tenant_id ON survey_responses(tenant_id);
    END IF;
END $$;

-- Field reports table
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'field_reports') THEN
        ALTER TABLE field_reports ADD COLUMN IF NOT EXISTS tenant_id TEXT;
        CREATE INDEX IF NOT EXISTS idx_field_reports_tenant_id ON field_reports(tenant_id);
    END IF;
END $$;

-- Alerts table
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alerts') THEN
        ALTER TABLE alerts ADD COLUMN IF NOT EXISTS tenant_id TEXT;
        CREATE INDEX IF NOT EXISTS idx_alerts_tenant_id ON alerts(tenant_id);
    END IF;
END $$;

-- Voter database table
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'voters') THEN
        ALTER TABLE voters ADD COLUMN IF NOT EXISTS tenant_id TEXT;
        CREATE INDEX IF NOT EXISTS idx_voters_tenant_id ON voters(tenant_id);
    END IF;
END $$;

-- =====================================================
-- 3. CREATE COMPREHENSIVE RLS POLICIES
-- =====================================================

-- Function to get current user's tenant_id
CREATE OR REPLACE FUNCTION get_user_tenant_id()
RETURNS TEXT AS $$
BEGIN
    RETURN (SELECT tenant_id FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is super admin
CREATE OR REPLACE FUNCTION is_super_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (SELECT is_super_admin FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Generic tenant isolation policy creator
CREATE OR REPLACE FUNCTION create_tenant_isolation_policy(table_name TEXT)
RETURNS VOID AS $$
DECLARE
    policy_name TEXT;
BEGIN
    policy_name := table_name || '_tenant_isolation';

    -- Drop existing policy if it exists
    EXECUTE format('DROP POLICY IF EXISTS %I ON %I', policy_name, table_name);

    -- Create new policy
    EXECUTE format('
        CREATE POLICY %I ON %I
        FOR ALL
        USING (
            tenant_id = get_user_tenant_id()
            OR
            is_super_admin() = TRUE
            OR
            (is_admin() = TRUE AND tenant_id IN (
                SELECT t.slug FROM tenants t
                JOIN organizations o ON o.id = t.organization_id
                JOIN user_organizations uo ON uo.organization_id = o.id
                WHERE uo.user_id = auth.uid()
            ))
        )
        WITH CHECK (
            tenant_id = get_user_tenant_id()
            OR
            is_super_admin() = TRUE
        )', policy_name, table_name);
END;
$$ LANGUAGE plpgsql;

-- Apply tenant isolation to all tables with tenant_id
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'tenant_id'
        AND table_schema = 'public'
        AND table_name NOT IN ('users', 'organizations', 'roles', 'permissions')
    LOOP
        -- Enable RLS
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);

        -- Create tenant isolation policy
        PERFORM create_tenant_isolation_policy(tbl);
    END LOOP;
END $$;

-- Special policy for tenants table (admins can see their org's tenants)
DROP POLICY IF EXISTS tenants_access_policy ON tenants;
CREATE POLICY tenants_access_policy ON tenants
    FOR ALL
    USING (
        -- Super admins see all tenants
        is_super_admin() = TRUE
        OR
        -- Admins see tenants in their organizations
        (is_admin() = TRUE AND organization_id IN (
            SELECT organization_id FROM user_organizations
            WHERE user_id = auth.uid()
        ))
        OR
        -- Users see tenants they belong to
        slug = get_user_tenant_id()
    );

-- Special policy for organizations table
DROP POLICY IF EXISTS organizations_access_policy ON organizations;
CREATE POLICY organizations_access_policy ON organizations
    FOR ALL
    USING (
        is_super_admin() = TRUE
        OR
        id IN (
            SELECT organization_id FROM user_organizations
            WHERE user_id = auth.uid()
        )
    );

-- =====================================================
-- 4. CREATE ADMIN-TENANT RELATIONSHIP TRACKING
-- =====================================================

-- Tenant provisioning log
CREATE TABLE IF NOT EXISTS tenant_provisioning_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

    -- Provisioning details
    status TEXT NOT NULL CHECK (status IN ('initiated', 'in_progress', 'completed', 'failed')),
    provisioned_by UUID REFERENCES users(id),

    -- Steps completed
    steps_completed JSONB DEFAULT '[]'::JSONB,

    -- Errors
    error_message TEXT,
    error_details JSONB,

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_tenant_provisioning_log_tenant_id ON tenant_provisioning_log(tenant_id);
CREATE INDEX idx_tenant_provisioning_log_status ON tenant_provisioning_log(status);

-- Tenant operations audit log
CREATE TABLE IF NOT EXISTS tenant_operations_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

    operation TEXT NOT NULL CHECK (operation IN (
        'created', 'updated', 'suspended', 'activated',
        'deleted', 'subscription_changed', 'admin_assigned',
        'settings_updated', 'features_updated'
    )),

    performed_by UUID REFERENCES users(id),
    performed_by_role TEXT,

    -- Changes
    old_values JSONB,
    new_values JSONB,

    -- Context
    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_tenant_operations_log_tenant_id ON tenant_operations_log(tenant_id);
CREATE INDEX idx_tenant_operations_log_operation ON tenant_operations_log(operation);
CREATE INDEX idx_tenant_operations_log_performed_by ON tenant_operations_log(performed_by);
CREATE INDEX idx_tenant_operations_log_created_at ON tenant_operations_log(created_at DESC);

-- Enable RLS on new tables
ALTER TABLE tenant_provisioning_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_operations_log ENABLE ROW LEVEL SECURITY;

-- Policies for provisioning log (super admin and admins can see their org's tenants)
CREATE POLICY tenant_provisioning_log_access ON tenant_provisioning_log
    FOR SELECT
    USING (
        is_super_admin() = TRUE
        OR
        (is_admin() = TRUE AND tenant_id IN (
            SELECT t.id FROM tenants t
            JOIN organizations o ON o.id = t.organization_id
            JOIN user_organizations uo ON uo.organization_id = o.id
            WHERE uo.user_id = auth.uid()
        ))
    );

-- Policies for operations log
CREATE POLICY tenant_operations_log_access ON tenant_operations_log
    FOR SELECT
    USING (
        is_super_admin() = TRUE
        OR
        (is_admin() = TRUE AND tenant_id IN (
            SELECT t.id FROM tenants t
            JOIN organizations o ON o.id = t.organization_id
            JOIN user_organizations uo ON uo.organization_id = o.id
            WHERE uo.user_id = auth.uid()
        ))
    );

-- =====================================================
-- 5. UPDATE ORGANIZATIONS TABLE
-- =====================================================

-- Add admin owner tracking
ALTER TABLE organizations
ADD COLUMN IF NOT EXISTS owned_by_admin_id UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS total_tenants INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS active_tenants INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_organizations_owned_by ON organizations(owned_by_admin_id);

-- =====================================================
-- 6. CREATE HELPER FUNCTIONS
-- =====================================================

-- Function to get tenant by subdomain
CREATE OR REPLACE FUNCTION get_tenant_by_subdomain(p_subdomain TEXT)
RETURNS SETOF tenants AS $$
BEGIN
    RETURN QUERY
    SELECT * FROM tenants
    WHERE subdomain = p_subdomain
    AND status = 'active'
    AND subscription_status IN ('trial', 'active');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate user access to tenant
CREATE OR REPLACE FUNCTION user_can_access_tenant(p_user_id UUID, p_tenant_slug TEXT)
RETURNS BOOLEAN AS $$
DECLARE
    user_tenant TEXT;
    user_is_super BOOLEAN;
    user_is_admin BOOLEAN;
    tenant_org UUID;
    user_in_org BOOLEAN;
BEGIN
    -- Get user's tenant
    SELECT tenant_id, is_super_admin, role INTO user_tenant, user_is_super, user_is_admin
    FROM users WHERE id = p_user_id;

    -- Super admins can access all tenants
    IF user_is_super THEN
        RETURN TRUE;
    END IF;

    -- Check if user's tenant matches
    IF user_tenant = p_tenant_slug THEN
        RETURN TRUE;
    END IF;

    -- If user is admin, check if tenant belongs to their organization
    IF user_is_admin IN ('admin', 'manager') THEN
        SELECT t.organization_id INTO tenant_org
        FROM tenants t WHERE t.slug = p_tenant_slug;

        SELECT EXISTS(
            SELECT 1 FROM user_organizations
            WHERE user_id = p_user_id AND organization_id = tenant_org
        ) INTO user_in_org;

        RETURN user_in_org;
    END IF;

    RETURN FALSE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create tenant with logging
CREATE OR REPLACE FUNCTION create_tenant_with_audit(
    p_slug TEXT,
    p_name TEXT,
    p_display_name TEXT,
    p_organization_id UUID,
    p_subdomain TEXT,
    p_created_by UUID,
    p_coverage_area TEXT,
    p_state TEXT,
    p_subscription_tier TEXT DEFAULT 'standard'
)
RETURNS UUID AS $$
DECLARE
    new_tenant_id UUID;
    log_id UUID;
BEGIN
    -- Create tenant
    INSERT INTO tenants (
        slug, name, display_name, organization_id, subdomain,
        created_by, coverage_area, state, subscription_tier,
        subscription_status, status
    ) VALUES (
        p_slug, p_name, p_display_name, p_organization_id, p_subdomain,
        p_created_by, p_coverage_area, p_state, p_subscription_tier,
        'trial', 'active'
    ) RETURNING id INTO new_tenant_id;

    -- Create provisioning log
    INSERT INTO tenant_provisioning_log (
        tenant_id, status, provisioned_by, steps_completed
    ) VALUES (
        new_tenant_id, 'initiated', p_created_by, '["tenant_created"]'::JSONB
    ) RETURNING id INTO log_id;

    -- Create operations log
    INSERT INTO tenant_operations_log (
        tenant_id, operation, performed_by, performed_by_role,
        new_values
    ) VALUES (
        new_tenant_id, 'created', p_created_by,
        (SELECT role FROM users WHERE id = p_created_by),
        jsonb_build_object(
            'name', p_name,
            'subdomain', p_subdomain,
            'organization_id', p_organization_id
        )
    );

    -- Update organization tenant count
    UPDATE organizations
    SET total_tenants = total_tenants + 1,
        active_tenants = active_tenants + 1
    WHERE id = p_organization_id;

    RETURN new_tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- 7. CREATE VIEWS FOR EASY QUERYING
-- =====================================================

-- View: Tenant overview with organization info
CREATE OR REPLACE VIEW tenant_overview_with_org AS
SELECT
    t.id,
    t.slug,
    t.name,
    t.display_name,
    t.subdomain,
    t.status,
    t.subscription_status,
    t.subscription_tier,
    t.coverage_area,
    t.state,
    t.ward_count,
    t.expected_users,
    t.monthly_fee,
    t.created_at,

    -- Organization info
    o.id as organization_id,
    o.name as organization_name,
    o.owned_by_admin_id,
    u.name as admin_name,
    u.email as admin_email,

    -- Usage stats (last 7 days)
    (SELECT SUM(api_calls) FROM tenant_usage WHERE tenant_id = t.id AND date >= CURRENT_DATE - 7) as api_calls_7d,
    (SELECT AVG(active_users) FROM tenant_usage WHERE tenant_id = t.id AND date >= CURRENT_DATE - 7) as avg_active_users_7d,
    (SELECT MAX(storage_used_gb) FROM tenant_usage WHERE tenant_id = t.id AND date >= CURRENT_DATE - 7) as current_storage_gb

FROM tenants t
LEFT JOIN organizations o ON o.id = t.organization_id
LEFT JOIN users u ON u.id = o.owned_by_admin_id
WHERE t.status != 'deleted';

-- View: Super admin dashboard stats
CREATE OR REPLACE VIEW super_admin_stats AS
SELECT
    -- Admin counts
    (SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_super_admin = FALSE) as total_admins,
    (SELECT COUNT(*) FROM users WHERE role = 'admin' AND status = 'active') as active_admins,

    -- Organization counts
    (SELECT COUNT(*) FROM organizations WHERE status = 'active') as total_organizations,

    -- Tenant counts
    (SELECT COUNT(*) FROM tenants WHERE status = 'active') as total_tenants,
    (SELECT COUNT(*) FROM tenants WHERE subscription_status = 'trial') as trial_tenants,
    (SELECT COUNT(*) FROM tenants WHERE subscription_status = 'active') as active_tenants,
    (SELECT COUNT(*) FROM tenants WHERE subscription_status = 'suspended') as suspended_tenants,

    -- User counts
    (SELECT COUNT(*) FROM users WHERE status = 'active') as total_active_users,
    (SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE - 7) as new_users_7d,

    -- Revenue
    (SELECT SUM(monthly_fee) FROM tenants WHERE subscription_status = 'active') as monthly_recurring_revenue,
    (SELECT COUNT(*) FROM tenants WHERE payment_status = 'overdue') as overdue_payments,

    -- Timestamp
    NOW() as calculated_at;

-- =====================================================
-- 8. CREATE TRIGGERS
-- =====================================================

-- Trigger to log tenant status changes
CREATE OR REPLACE FUNCTION log_tenant_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status
       OR OLD.subscription_status IS DISTINCT FROM NEW.subscription_status THEN
        INSERT INTO tenant_operations_log (
            tenant_id, operation, performed_by, old_values, new_values
        ) VALUES (
            NEW.id,
            CASE
                WHEN NEW.status = 'suspended' THEN 'suspended'
                WHEN NEW.status = 'active' AND OLD.status = 'suspended' THEN 'activated'
                WHEN NEW.subscription_status != OLD.subscription_status THEN 'subscription_changed'
                ELSE 'updated'
            END,
            auth.uid(),
            jsonb_build_object('status', OLD.status, 'subscription_status', OLD.subscription_status),
            jsonb_build_object('status', NEW.status, 'subscription_status', NEW.subscription_status)
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS tenant_status_change_trigger ON tenants;
CREATE TRIGGER tenant_status_change_trigger
    AFTER UPDATE ON tenants
    FOR EACH ROW
    EXECUTE FUNCTION log_tenant_status_change();

-- =====================================================
-- 9. SEED DEFAULT DATA (Optional)
-- =====================================================

-- Update existing system settings for single-DB multi-tenancy
INSERT INTO system_settings (key, value, description, category) VALUES
('multi_tenancy.mode', '"single_database"', 'Multi-tenancy mode: single_database or database_per_tenant', 'system'),
('multi_tenancy.subdomain_enabled', 'true', 'Enable subdomain-based tenant routing', 'system'),
('multi_tenancy.max_tenants_per_org', '50', 'Maximum tenants an organization can create', 'limits'),
('provisioning.auto_setup_subdomain', 'true', 'Automatically configure subdomain DNS', 'provisioning'),
('provisioning.send_welcome_email', 'true', 'Send welcome email to new tenant admins', 'provisioning')
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    updated_at = NOW();

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- Add comments for documentation
COMMENT ON TABLE tenants IS 'Tenants in single-database multi-tenant system. Each tenant is identified by subdomain and belongs to an organization.';
COMMENT ON TABLE tenant_provisioning_log IS 'Tracks tenant provisioning progress and errors';
COMMENT ON TABLE tenant_operations_log IS 'Audit log for all tenant operations (create, update, suspend, etc.)';
COMMENT ON COLUMN tenants.subdomain IS 'Subdomain for tenant access (e.g., kerala.yourapp.com)';
COMMENT ON COLUMN tenants.organization_id IS 'Organization (admin) that owns this tenant';
COMMENT ON FUNCTION create_tenant_with_audit IS 'Create a new tenant with automatic audit logging';
COMMENT ON FUNCTION user_can_access_tenant IS 'Check if a user has access to a specific tenant';
COMMENT ON VIEW tenant_overview_with_org IS 'Tenant overview including organization and admin information';
COMMENT ON VIEW super_admin_stats IS 'Platform-wide statistics for super admin dashboard';
