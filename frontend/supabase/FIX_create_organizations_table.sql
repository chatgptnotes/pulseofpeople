-- =====================================================
-- FIX: Create Organizations Table for Multi-Tenant Setup
-- =====================================================
-- Run this BEFORE the multi-tenant migration
-- This creates the organizations table with the correct structure

-- Drop the existing organizations table if it has wrong structure
DROP TABLE IF EXISTS organizations CASCADE;

-- Create Organizations table (parent of tenants)
CREATE TABLE IF NOT EXISTS organizations (
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

-- Create indexes
CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_status ON organizations(status);

-- Create user_organizations table for many-to-many relationship
CREATE TABLE IF NOT EXISTS user_organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member',
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, organization_id)
);

CREATE INDEX idx_user_organizations_user_id ON user_organizations(user_id);
CREATE INDEX idx_user_organizations_organization_id ON user_organizations(organization_id);

-- Enable RLS
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_organizations ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies
CREATE POLICY organizations_view_policy ON organizations
    FOR SELECT
    USING (true);  -- Organizations are public to view

CREATE POLICY organizations_manage_policy ON organizations
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.is_super_admin = true
        )
    );

CREATE POLICY user_organizations_view_policy ON user_organizations
    FOR SELECT
    USING (
        user_id = auth.uid()
        OR
        EXISTS (
            SELECT 1 FROM users
            WHERE users.id = auth.uid()
            AND users.is_super_admin = true
        )
    );

-- Now the multi-tenant migration will work correctly!
-- After running this, you can run:
-- 1. 20251029_single_db_multi_tenant.sql
-- 2. create_tenants_party_a_b.sql