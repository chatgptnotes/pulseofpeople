-- =====================================================
-- TENANT REGISTRY - Central Multi-Tenant Management
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================================================
-- TENANTS TABLE
-- =====================================================

CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,  -- kerala-2026, tamilnadu-2026
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,

    -- Supabase connection details
    supabase_url TEXT NOT NULL,
    supabase_project_id TEXT UNIQUE NOT NULL,
    supabase_anon_key TEXT NOT NULL,
    supabase_region TEXT NOT NULL DEFAULT 'ap-south-1',

    -- Contact information
    contact_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT,
    organization_name TEXT,

    -- Subscription details
    subscription_status TEXT DEFAULT 'trial' CHECK (subscription_status IN ('trial', 'active', 'suspended', 'cancelled', 'expired')),
    subscription_tier TEXT DEFAULT 'standard' CHECK (subscription_tier IN ('basic', 'standard', 'premium', 'enterprise')),
    subscription_start TIMESTAMPTZ DEFAULT NOW(),
    subscription_end TIMESTAMPTZ,
    trial_end_date TIMESTAMPTZ DEFAULT NOW() + INTERVAL '14 days',

    -- Billing
    monthly_fee DECIMAL(10, 2) DEFAULT 6000.00,
    currency TEXT DEFAULT 'INR',
    billing_cycle TEXT DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'quarterly', 'yearly')),
    billing_email TEXT,
    last_payment_date TIMESTAMPTZ,
    next_billing_date TIMESTAMPTZ,
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'overdue', 'failed')),

    -- Coverage details
    coverage_area TEXT NOT NULL,  -- "Kerala State", "Tamil Nadu - Chennai District"
    state TEXT NOT NULL,
    districts TEXT[] DEFAULT ARRAY[]::TEXT[],
    ward_count INTEGER DEFAULT 0,
    expected_users INTEGER DEFAULT 50,

    -- Configuration
    enabled_features JSONB DEFAULT '["dashboard", "analytics", "field-reports", "surveys", "social-media"]'::JSONB,
    custom_settings JSONB DEFAULT '{}'::JSONB,
    data_residency TEXT DEFAULT 'india' CHECK (data_residency IN ('india', 'singapore', 'us', 'eu')),

    -- Branding
    branding JSONB DEFAULT '{
        "logo": "",
        "primaryColor": "#3b82f6",
        "secondaryColor": "#8b5cf6",
        "customDomain": null
    }'::JSONB,
    custom_domain TEXT UNIQUE,

    -- Limits
    max_users INTEGER DEFAULT 100,
    max_wards INTEGER DEFAULT 1000,
    max_storage_gb INTEGER DEFAULT 50,
    max_api_calls_per_hour INTEGER DEFAULT 10000,

    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'deleted')),
    is_demo BOOLEAN DEFAULT FALSE,

    -- Metadata
    notes TEXT,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    activated_at TIMESTAMPTZ,
    suspended_at TIMESTAMPTZ,
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_status ON tenants(status);
CREATE INDEX idx_tenants_subscription_status ON tenants(subscription_status);
CREATE INDEX idx_tenants_custom_domain ON tenants(custom_domain);
CREATE INDEX idx_tenants_state ON tenants(state);

-- =====================================================
-- TENANT CREDENTIALS (Encrypted)
-- =====================================================

CREATE TABLE tenant_credentials (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,

    -- Encrypted credentials (use pgcrypto)
    supabase_service_key TEXT NOT NULL,  -- Encrypted with pgp_sym_encrypt
    database_url TEXT NOT NULL,          -- Encrypted with pgp_sym_encrypt
    database_password TEXT NOT NULL,     -- Encrypted with pgp_sym_encrypt

    -- API keys for integrations
    api_keys JSONB DEFAULT '{}'::JSONB,  -- Store encrypted third-party API keys

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    last_rotated TIMESTAMPTZ,

    UNIQUE(tenant_id)
);

CREATE INDEX idx_tenant_credentials_tenant ON tenant_credentials(tenant_id);

-- =====================================================
-- TENANT USAGE TRACKING
-- =====================================================

CREATE TABLE tenant_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,
    date DATE NOT NULL,

    -- API usage
    api_calls BIGINT DEFAULT 0,
    api_calls_peak_hour INTEGER DEFAULT 0,

    -- Storage
    storage_used_gb DECIMAL(10, 3) DEFAULT 0,
    storage_media_gb DECIMAL(10, 3) DEFAULT 0,
    storage_database_gb DECIMAL(10, 3) DEFAULT 0,

    -- Users
    active_users INTEGER DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    new_users INTEGER DEFAULT 0,

    -- Data records
    sentiment_records_created BIGINT DEFAULT 0,
    social_posts_created BIGINT DEFAULT 0,
    field_reports_created BIGINT DEFAULT 0,
    survey_responses_created BIGINT DEFAULT 0,

    -- Performance metrics
    avg_response_time_ms INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    error_rate DECIMAL(5, 2) DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    UNIQUE(tenant_id, date)
);

CREATE INDEX idx_tenant_usage_tenant_date ON tenant_usage(tenant_id, date DESC);

-- =====================================================
-- TENANT EVENTS (Audit Log)
-- =====================================================

CREATE TABLE tenant_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,

    event_type TEXT NOT NULL,  -- created, activated, suspended, upgraded, etc.
    event_category TEXT CHECK (event_category IN ('lifecycle', 'billing', 'configuration', 'security', 'performance')),

    -- Event details
    description TEXT,
    metadata JSONB DEFAULT '{}'::JSONB,

    -- Who triggered the event
    triggered_by TEXT,  -- 'system', 'admin', 'tenant-admin', email
    ip_address INET,

    severity TEXT DEFAULT 'info' CHECK (severity IN ('info', 'warning', 'error', 'critical')),

    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_tenant_events_tenant ON tenant_events(tenant_id);
CREATE INDEX idx_tenant_events_timestamp ON tenant_events(timestamp DESC);
CREATE INDEX idx_tenant_events_type ON tenant_events(event_type);

-- =====================================================
-- TENANT DEPLOYMENTS (Tracking)
-- =====================================================

CREATE TABLE tenant_deployments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,

    deployment_type TEXT NOT NULL CHECK (deployment_type IN ('migration', 'update', 'rollback', 'hotfix')),
    version TEXT NOT NULL,

    -- Migration details
    migration_files TEXT[] DEFAULT ARRAY[]::TEXT[],
    success BOOLEAN,
    error_message TEXT,

    -- Timing
    started_at TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    duration_seconds INTEGER,

    -- Who deployed
    deployed_by TEXT,

    metadata JSONB DEFAULT '{}'::JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_tenant_deployments_tenant ON tenant_deployments(tenant_id);
CREATE INDEX idx_tenant_deployments_started ON tenant_deployments(started_at DESC);

-- =====================================================
-- TENANT HEALTH CHECKS
-- =====================================================

CREATE TABLE tenant_health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE NOT NULL,

    -- Health status
    status TEXT NOT NULL CHECK (status IN ('healthy', 'degraded', 'unhealthy', 'unknown')),
    health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),

    -- Checks performed
    database_accessible BOOLEAN,
    database_response_time_ms INTEGER,
    api_accessible BOOLEAN,
    api_response_time_ms INTEGER,
    storage_accessible BOOLEAN,
    auth_accessible BOOLEAN,

    -- Issues detected
    issues JSONB DEFAULT '[]'::JSONB,
    warnings JSONB DEFAULT '[]'::JSONB,

    checked_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_tenant_health_tenant ON tenant_health_checks(tenant_id);
CREATE INDEX idx_tenant_health_checked ON tenant_health_checks(checked_at DESC);
CREATE INDEX idx_tenant_health_status ON tenant_health_checks(status);

-- =====================================================
-- SYSTEM SETTINGS (Global Configuration)
-- =====================================================

CREATE TABLE system_settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    category TEXT,
    is_public BOOLEAN DEFAULT FALSE,  -- Can tenants see this?
    updated_by TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Insert default settings
INSERT INTO system_settings (key, value, description, category) VALUES
('provisioning.auto_create_admin', 'true', 'Automatically create admin user on tenant creation', 'provisioning'),
('provisioning.trial_duration_days', '14', 'Default trial period in days', 'provisioning'),
('billing.grace_period_days', '7', 'Days before suspending for non-payment', 'billing'),
('health.check_interval_minutes', '5', 'How often to check tenant health', 'monitoring'),
('deployment.auto_migrate', 'true', 'Automatically run migrations on all tenants', 'deployment'),
('features.default_enabled', '["dashboard", "analytics", "field-reports", "surveys"]', 'Default enabled features for new tenants', 'features'),
('limits.default_max_users', '100', 'Default maximum users per tenant', 'limits'),
('limits.default_max_storage_gb', '50', 'Default storage limit in GB', 'limits');

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Function to encrypt credentials
CREATE OR REPLACE FUNCTION encrypt_credential(credential TEXT, encryption_key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(pgp_sym_encrypt(credential, encryption_key), 'base64');
END;
$$ LANGUAGE plpgsql;

-- Function to decrypt credentials
CREATE OR REPLACE FUNCTION decrypt_credential(encrypted_credential TEXT, encryption_key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(decode(encrypted_credential, 'base64'), encryption_key);
END;
$$ LANGUAGE plpgsql;

-- Function to get active tenants count
CREATE OR REPLACE FUNCTION get_active_tenants_count()
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM tenants WHERE status = 'active' AND subscription_status IN ('active', 'trial'));
END;
$$ LANGUAGE plpgsql;

-- Function to calculate tenant health score
CREATE OR REPLACE FUNCTION calculate_tenant_health_score(tenant_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    score INTEGER := 100;
    latest_check tenant_health_checks%ROWTYPE;
    tenant_info tenants%ROWTYPE;
BEGIN
    -- Get latest health check
    SELECT * INTO latest_check
    FROM tenant_health_checks
    WHERE tenant_id = tenant_uuid
    ORDER BY checked_at DESC
    LIMIT 1;

    -- Get tenant info
    SELECT * INTO tenant_info
    FROM tenants
    WHERE id = tenant_uuid;

    -- Deduct points for issues
    IF latest_check.database_accessible = FALSE THEN score := score - 30; END IF;
    IF latest_check.api_accessible = FALSE THEN score := score - 25; END IF;
    IF latest_check.storage_accessible = FALSE THEN score := score - 15; END IF;
    IF latest_check.auth_accessible = FALSE THEN score := score - 20; END IF;

    -- Deduct for slow response times
    IF latest_check.database_response_time_ms > 1000 THEN score := score - 5; END IF;
    IF latest_check.api_response_time_ms > 2000 THEN score := score - 5; END IF;

    -- Deduct for subscription issues
    IF tenant_info.payment_status = 'overdue' THEN score := score - 10; END IF;
    IF tenant_info.subscription_status = 'suspended' THEN score := score - 20; END IF;

    RETURN GREATEST(score, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to get tenant by slug
CREATE OR REPLACE FUNCTION get_tenant_by_slug(tenant_slug TEXT)
RETURNS tenants AS $$
DECLARE
    tenant_record tenants%ROWTYPE;
BEGIN
    SELECT * INTO tenant_record
    FROM tenants
    WHERE slug = tenant_slug AND status = 'active';

    RETURN tenant_record;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tenant_credentials_updated_at
    BEFORE UPDATE ON tenant_credentials
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Log tenant status changes
CREATE OR REPLACE FUNCTION log_tenant_status_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.status IS DISTINCT FROM NEW.status THEN
        INSERT INTO tenant_events (tenant_id, event_type, event_category, description, triggered_by, severity)
        VALUES (
            NEW.id,
            'status_changed',
            'lifecycle',
            format('Status changed from %s to %s', OLD.status, NEW.status),
            'system',
            CASE WHEN NEW.status = 'suspended' THEN 'warning'
                 WHEN NEW.status = 'deleted' THEN 'critical'
                 ELSE 'info' END
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER log_tenant_status_change_trigger
    AFTER UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION log_tenant_status_change();

-- =====================================================
-- ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_deployments ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_health_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Only super admins can access tenant registry
-- These policies assume you have a separate admin authentication system

-- Public read for active tenants (for subdomain routing)
CREATE POLICY tenants_public_read ON tenants
    FOR SELECT
    USING (status = 'active' AND subscription_status IN ('active', 'trial'));

-- Admin full access (modify based on your admin auth setup)
CREATE POLICY tenants_admin_all ON tenants
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Credentials - only service role access
CREATE POLICY tenant_credentials_admin_only ON tenant_credentials
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');

-- Usage - read-only for tenants to see their own usage
CREATE POLICY tenant_usage_read_own ON tenant_usage
    FOR SELECT
    USING (auth.jwt()->>'role' = 'service_role');

-- Events - read access for admin
CREATE POLICY tenant_events_admin_read ON tenant_events
    FOR SELECT
    USING (auth.jwt()->>'role' = 'service_role');

-- System settings public read for public settings
CREATE POLICY system_settings_public_read ON system_settings
    FOR SELECT
    USING (is_public = true);

-- =====================================================
-- VIEWS
-- =====================================================

-- View for tenant overview
CREATE OR REPLACE VIEW tenant_overview AS
SELECT
    t.id,
    t.slug,
    t.name,
    t.display_name,
    t.status,
    t.subscription_status,
    t.subscription_tier,
    t.coverage_area,
    t.state,
    t.ward_count,
    t.created_at,
    t.subscription_start,
    t.subscription_end,
    t.trial_end_date,
    t.monthly_fee,
    t.payment_status,
    t.next_billing_date,

    -- Latest health check
    (SELECT status FROM tenant_health_checks WHERE tenant_id = t.id ORDER BY checked_at DESC LIMIT 1) as health_status,
    (SELECT health_score FROM tenant_health_checks WHERE tenant_id = t.id ORDER BY checked_at DESC LIMIT 1) as health_score,

    -- Usage stats (last 7 days)
    (SELECT SUM(api_calls) FROM tenant_usage WHERE tenant_id = t.id AND date >= CURRENT_DATE - 7) as api_calls_7d,
    (SELECT AVG(active_users) FROM tenant_usage WHERE tenant_id = t.id AND date >= CURRENT_DATE - 7) as avg_active_users_7d,
    (SELECT MAX(storage_used_gb) FROM tenant_usage WHERE tenant_id = t.id AND date >= CURRENT_DATE - 7) as current_storage_gb

FROM tenants t
WHERE t.status != 'deleted';

-- View for tenants needing attention
CREATE OR REPLACE VIEW tenants_requiring_attention AS
SELECT
    t.id,
    t.slug,
    t.name,
    t.status,
    t.subscription_status,
    t.payment_status,
    t.trial_end_date,
    t.next_billing_date,

    CASE
        WHEN t.payment_status = 'overdue' THEN 'Payment overdue'
        WHEN t.trial_end_date < NOW() + INTERVAL '3 days' AND t.subscription_status = 'trial' THEN 'Trial ending soon'
        WHEN (SELECT health_score FROM tenant_health_checks WHERE tenant_id = t.id ORDER BY checked_at DESC LIMIT 1) < 50 THEN 'Health issues'
        WHEN t.subscription_end < NOW() + INTERVAL '7 days' THEN 'Subscription ending soon'
        ELSE 'Other'
    END as attention_reason,

    (SELECT health_score FROM tenant_health_checks WHERE tenant_id = t.id ORDER BY checked_at DESC LIMIT 1) as health_score

FROM tenants t
WHERE t.status = 'active'
  AND (
    t.payment_status = 'overdue'
    OR (t.trial_end_date < NOW() + INTERVAL '3 days' AND t.subscription_status = 'trial')
    OR (SELECT health_score FROM tenant_health_checks WHERE tenant_id = t.id ORDER BY checked_at DESC LIMIT 1) < 50
    OR t.subscription_end < NOW() + INTERVAL '7 days'
  );

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE tenants IS 'Central registry of all tenants in the multi-tenant system';
COMMENT ON TABLE tenant_credentials IS 'Encrypted credentials for tenant database access';
COMMENT ON TABLE tenant_usage IS 'Daily usage tracking per tenant';
COMMENT ON TABLE tenant_events IS 'Audit log of all tenant lifecycle events';
COMMENT ON TABLE tenant_deployments IS 'Tracking of deployments and migrations per tenant';
COMMENT ON TABLE tenant_health_checks IS 'Health monitoring results per tenant';

-- =====================================================
-- END OF TENANT REGISTRY SCHEMA
-- =====================================================
