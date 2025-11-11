-- =====================================================
-- COMPLETE FIX: Single Database Multi-Tenant Setup
-- =====================================================
-- This script sets up everything needed for multi-tenant
-- Run this INSTEAD of the other migrations

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- STEP 1: Clean up any existing conflicting tables
-- =====================================================

DROP TABLE IF EXISTS tenant_operations_log CASCADE;
DROP TABLE IF EXISTS tenant_provisioning_log CASCADE;
DROP TABLE IF EXISTS tenant_credentials CASCADE;
DROP TABLE IF EXISTS user_organizations CASCADE;
DROP TABLE IF EXISTS tenants CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;

-- =====================================================
-- STEP 2: Create Organizations Table (Parent of Tenants)
-- =====================================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT UNIQUE NOT NULL,
    display_name TEXT,
    description TEXT,

    -- Contact information
    contact_email TEXT,
    contact_phone TEXT,
    address TEXT,

    -- Organization settings
    settings JSONB DEFAULT '{}'::JSONB,
    features JSONB DEFAULT '{}'::JSONB,

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending')),

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB
);

CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_status ON organizations(status);

-- =====================================================
-- STEP 3: Create Tenants Table (Single Database)
-- =====================================================

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

    -- Identification
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,

    -- Subdomain routing
    subdomain TEXT UNIQUE,
    custom_domain TEXT UNIQUE,

    -- Branding
    branding JSONB DEFAULT '{
        "primaryColor": "#3b82f6",
        "secondaryColor": "#8b5cf6",
        "logo": "/assets/images/logo.png",
        "favicon": "/favicon.ico"
    }'::JSONB,

    -- Configuration
    config JSONB DEFAULT '{}'::JSONB,
    features JSONB DEFAULT '{}'::JSONB,

    -- Subscription
    subscription_tier TEXT DEFAULT 'standard',
    subscription_status TEXT DEFAULT 'active',
    subscription_start_date TIMESTAMPTZ DEFAULT NOW(),
    subscription_end_date TIMESTAMPTZ,
    monthly_fee DECIMAL(10, 2) DEFAULT 6000.00,

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'deleted')),

    -- Metadata
    metadata JSONB DEFAULT '{}'::JSONB,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_tenants_organization_id ON tenants(organization_id);
CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX idx_tenants_status ON tenants(status);

-- =====================================================
-- STEP 4: Create User-Organization Relationship
-- =====================================================

CREATE TABLE user_organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, organization_id)
);

CREATE INDEX idx_user_organizations_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_organizations_organization_id ON user_organizations(organization_id);

-- =====================================================
-- STEP 5: Add tenant_id to all domain tables
-- =====================================================

-- Add tenant_id to users table if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'tenant_id') THEN
        ALTER TABLE users ADD COLUMN tenant_id UUID REFERENCES tenants(id);
        CREATE INDEX idx_users_tenant_id ON users(tenant_id);
    END IF;
END $$;

-- Add tenant_id to constituencies table if it exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'constituencies') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                       WHERE table_name = 'constituencies' AND column_name = 'tenant_id') THEN
            ALTER TABLE constituencies ADD COLUMN tenant_id UUID REFERENCES tenants(id);
            CREATE INDEX idx_constituencies_tenant_id ON constituencies(tenant_id);
        END IF;
    ELSE
        -- Create constituencies table
        CREATE TABLE constituencies (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID REFERENCES tenants(id),
            name TEXT NOT NULL,
            state TEXT,
            district TEXT,
            total_voters INTEGER,
            demographics JSONB DEFAULT '{}'::JSONB,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW()
        );
        CREATE INDEX idx_constituencies_tenant_id ON constituencies(tenant_id);
    END IF;
END $$;

-- =====================================================
-- STEP 6: Create Audit Tables
-- =====================================================

CREATE TABLE tenant_provisioning_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    performed_by UUID REFERENCES users(id),
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE tenant_operations_audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    operation TEXT NOT NULL,
    performed_by UUID REFERENCES users(id),
    old_values JSONB,
    new_values JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- STEP 7: Create Helper Functions
-- =====================================================

-- Function to get current user's tenant_id
CREATE OR REPLACE FUNCTION get_user_tenant_id()
RETURNS UUID AS $$
BEGIN
    RETURN (SELECT tenant_id FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is super admin
CREATE OR REPLACE FUNCTION is_super_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN COALESCE((SELECT is_super_admin FROM users WHERE id = auth.uid()), false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN COALESCE(
        (SELECT role IN ('admin', 'super_admin') FROM users WHERE id = auth.uid()),
        false
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to create tenant with audit
CREATE OR REPLACE FUNCTION create_tenant_with_audit(
    p_org_id UUID,
    p_slug TEXT,
    p_name TEXT,
    p_subdomain TEXT,
    p_config JSONB DEFAULT '{}'::JSONB
)
RETURNS UUID AS $$
DECLARE
    v_tenant_id UUID;
BEGIN
    -- Create tenant
    INSERT INTO tenants (
        organization_id,
        slug,
        name,
        display_name,
        subdomain,
        config
    ) VALUES (
        p_org_id,
        p_slug,
        p_name,
        p_name,
        p_subdomain,
        p_config
    ) RETURNING id INTO v_tenant_id;

    -- Audit
    INSERT INTO tenant_provisioning_audit (
        tenant_id,
        action,
        performed_by,
        details
    ) VALUES (
        v_tenant_id,
        'created',
        auth.uid(),
        jsonb_build_object(
            'slug', p_slug,
            'subdomain', p_subdomain
        )
    );

    RETURN v_tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- STEP 8: Enable Row Level Security
-- =====================================================

ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_provisioning_audit ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_operations_audit ENABLE ROW LEVEL SECURITY;

-- Enable RLS on constituencies if it exists
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'constituencies') THEN
        ALTER TABLE constituencies ENABLE ROW LEVEL SECURITY;
    END IF;
END $$;

-- =====================================================
-- STEP 9: Create RLS Policies
-- =====================================================

-- Organizations: viewable by members and super admins
CREATE POLICY organizations_view_policy ON organizations
    FOR SELECT
    USING (
        is_super_admin() = true
        OR
        id IN (
            SELECT organization_id FROM user_organizations
            WHERE user_id = auth.uid()
        )
    );

-- Organizations: manageable by super admins only
CREATE POLICY organizations_manage_policy ON organizations
    FOR ALL
    USING (is_super_admin() = true);

-- Tenants: viewable by org members and super admins
CREATE POLICY tenants_view_policy ON tenants
    FOR SELECT
    USING (
        is_super_admin() = true
        OR
        organization_id IN (
            SELECT organization_id FROM user_organizations
            WHERE user_id = auth.uid()
        )
        OR
        id = get_user_tenant_id()
    );

-- Tenants: manageable by admins and super admins
CREATE POLICY tenants_manage_policy ON tenants
    FOR ALL
    USING (
        is_super_admin() = true
        OR
        (is_admin() = true AND organization_id IN (
            SELECT organization_id FROM user_organizations
            WHERE user_id = auth.uid()
        ))
    );

-- User organizations: viewable by members and super admins
CREATE POLICY user_organizations_view_policy ON user_organizations
    FOR SELECT
    USING (
        user_id = auth.uid()
        OR
        is_super_admin() = true
    );

-- Constituencies: tenant isolated
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'constituencies') THEN
        EXECUTE 'CREATE POLICY constituencies_tenant_isolation ON constituencies
            FOR ALL
            USING (
                tenant_id = get_user_tenant_id()
                OR
                is_super_admin() = true
            )';
    END IF;
END $$;

-- =====================================================
-- STEP 10: Create View for Super Admin Stats
-- =====================================================

CREATE OR REPLACE VIEW super_admin_stats AS
SELECT
    (SELECT COUNT(*) FROM organizations WHERE status = 'active') as total_organizations,
    (SELECT COUNT(*) FROM tenants WHERE status = 'active') as total_tenants,
    (SELECT COUNT(*) FROM users WHERE is_super_admin = false) as total_users,
    (SELECT SUM(monthly_fee) FROM tenants WHERE subscription_status = 'active') as monthly_revenue;

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Run these to verify setup:
-- SELECT * FROM organizations;
-- SELECT * FROM tenants;
-- SELECT * FROM user_organizations;
-- SELECT current_setting('server_version');

-- =====================================================
-- SUCCESS! Now you can run create_tenants_party_a_b.sql
-- =====================================================