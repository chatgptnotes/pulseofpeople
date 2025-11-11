-- =====================================================
-- COMPETITOR ANALYSIS - LEGAL DATA COLLECTION ONLY
-- =====================================================
-- Migration Date: 2025-11-09
-- Purpose: Track competitor social media (via legal APIs only)
-- Documentation: See docs/COMPETITOR_ANALYSIS_LEGAL_GUIDE.md
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. COMPETITORS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS competitors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Basic Info
  name VARCHAR(255) NOT NULL,
  party_name VARCHAR(255),
  party_acronym VARCHAR(50),
  leader_name VARCHAR(255),
  logo_url TEXT,
  color_code VARCHAR(7) DEFAULT '#6B7280',
  description TEXT,

  -- Geographic Focus
  country VARCHAR(100) DEFAULT 'India',
  state VARCHAR(100),
  district VARCHAR(100),
  constituency VARCHAR(100),

  -- Campaign Info
  campaign_slogan TEXT,
  estimated_budget DECIMAL(15,2),
  active_since DATE,

  -- Data Source (Legal compliance tracking)
  data_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'mention', 'brand24', 'official_api'
  data_source_note TEXT, -- e.g., "Subscription ID: mention-12345"
  last_synced_at TIMESTAMP,

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_competitors_party ON competitors(party_name);
CREATE INDEX IF NOT EXISTS idx_competitors_active ON competitors(is_active);
CREATE INDEX IF NOT EXISTS idx_competitors_state ON competitors(state);

-- =====================================================
-- 2. COMPETITOR SOCIAL MEDIA ACCOUNTS
-- =====================================================
CREATE TABLE IF NOT EXISTS competitor_social_accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,

  -- Platform Info
  platform VARCHAR(50) NOT NULL, -- 'facebook', 'twitter', 'instagram', 'youtube'
  handle VARCHAR(255) NOT NULL,
  profile_url TEXT,

  -- Public Metrics (from legal sources only)
  follower_count INTEGER DEFAULT 0,
  following_count INTEGER DEFAULT 0,
  post_count INTEGER DEFAULT 0,
  verified BOOLEAN DEFAULT FALSE,

  -- Account Details
  account_name VARCHAR(255),
  account_bio TEXT,

  -- Data Source (Legal compliance)
  data_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'official_api', 'mention', 'brand24'

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  last_updated_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_competitor_social_competitor ON competitor_social_accounts(competitor_id);
CREATE INDEX IF NOT EXISTS idx_competitor_social_platform ON competitor_social_accounts(platform);
CREATE UNIQUE INDEX IF NOT EXISTS idx_competitor_social_unique ON competitor_social_accounts(competitor_id, platform, handle);

-- =====================================================
-- 3. COMPETITOR POSTS (From Legal Sources ONLY)
-- =====================================================
CREATE TABLE IF NOT EXISTS competitor_posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
  social_account_id UUID REFERENCES competitor_social_accounts(id) ON DELETE CASCADE,

  -- Post Details
  platform VARCHAR(50) NOT NULL,
  post_id VARCHAR(255) NOT NULL,
  post_url TEXT,
  content TEXT,
  post_type VARCHAR(50), -- 'text', 'image', 'video', 'link'
  posted_at TIMESTAMP NOT NULL,

  -- Public Engagement Metrics (from legal APIs/services only)
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  shares_count INTEGER DEFAULT 0,
  views_count INTEGER DEFAULT 0,

  -- Calculated Metrics
  engagement_rate DECIMAL(5,2),

  -- AI Analysis (processed locally or via third-party services)
  sentiment_score DECIMAL(4,3), -- -1.000 to 1.000
  sentiment_label VARCHAR(20), -- 'positive', 'neutral', 'negative'

  -- Content Classification
  topics JSONB, -- ['education', 'healthcare']
  hashtags JSONB,
  mentions JSONB,
  language VARCHAR(10) DEFAULT 'en',

  -- Data Source (Legal compliance - CRITICAL)
  data_source VARCHAR(50) NOT NULL DEFAULT 'manual',
  -- Allowed values:
  -- 'manual' - Manually entered by user
  -- 'official_api' - From Facebook/Twitter/Instagram/YouTube official APIs
  -- 'mention' - From Mention.com subscription
  -- 'brand24' - From Brand24 subscription
  -- 'hootsuite' - From Hootsuite subscription

  -- Metadata
  is_flagged BOOLEAN DEFAULT FALSE, -- Flag for review
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_competitor_posts_competitor ON competitor_posts(competitor_id);
CREATE INDEX IF NOT EXISTS idx_competitor_posts_platform ON competitor_posts(platform);
CREATE INDEX IF NOT EXISTS idx_competitor_posts_posted_at ON competitor_posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_competitor_posts_engagement ON competitor_posts(engagement_rate DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_competitor_posts_unique ON competitor_posts(platform, post_id);

-- =====================================================
-- 4. COMPETITOR SENTIMENT HISTORY
-- =====================================================
CREATE TABLE IF NOT EXISTS competitor_sentiment_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,

  -- Time Period
  date DATE NOT NULL,
  period_type VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'monthly'

  -- Platform
  platform VARCHAR(50), -- NULL for overall sentiment

  -- Sentiment Metrics
  sentiment_score DECIMAL(4,3),
  positive_count INTEGER DEFAULT 0,
  neutral_count INTEGER DEFAULT 0,
  negative_count INTEGER DEFAULT 0,
  total_mentions INTEGER DEFAULT 0,

  -- Engagement
  total_engagement INTEGER DEFAULT 0,
  post_count INTEGER DEFAULT 0,
  avg_engagement_rate DECIMAL(5,2),

  -- Data Source
  data_source VARCHAR(50) DEFAULT 'calculated',

  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_history_competitor ON competitor_sentiment_history(competitor_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_history_date ON competitor_sentiment_history(date DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sentiment_history_unique ON competitor_sentiment_history(competitor_id, date, COALESCE(platform, ''));

-- =====================================================
-- 5. DATA SOURCE CONFIGURATIONS (Third-party Services)
-- =====================================================
CREATE TABLE IF NOT EXISTS competitor_data_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Service Details
  service_name VARCHAR(50) NOT NULL, -- 'mention', 'brand24', 'hootsuite'
  service_type VARCHAR(50) DEFAULT 'social_listening',

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  subscription_plan VARCHAR(50),
  subscription_expires_at TIMESTAMP,
  monthly_cost DECIMAL(10,2),

  -- Usage Tracking
  last_sync_at TIMESTAMP,
  sync_frequency_minutes INTEGER DEFAULT 60,

  -- API Limits
  monthly_quota INTEGER,
  quota_used INTEGER DEFAULT 0,
  quota_reset_at TIMESTAMP,

  -- Notes
  notes TEXT,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_data_sources_active ON competitor_data_sources(is_active);

-- =====================================================
-- 6. AUDIT LOG (Legal Compliance)
-- =====================================================
CREATE TABLE IF NOT EXISTS competitor_data_audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Activity Details
  action_type VARCHAR(50) NOT NULL, -- 'manual_entry', 'api_sync', 'export'
  data_source VARCHAR(50) NOT NULL,
  resource_type VARCHAR(50), -- 'competitor', 'post', 'sentiment'
  resource_id UUID,

  -- Details
  description TEXT,
  metadata JSONB,

  -- Legal Compliance Flags
  tos_compliant BOOLEAN DEFAULT TRUE,
  legal_basis TEXT, -- e.g., "Official API", "Mention subscription", "Manual entry"

  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON competitor_data_audit_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_action_type ON competitor_data_audit_log(action_type);

-- =====================================================
-- FUNCTIONS & TRIGGERS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to tables
DROP TRIGGER IF EXISTS update_competitors_updated_at ON competitors;
CREATE TRIGGER update_competitors_updated_at
BEFORE UPDATE ON competitors
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_competitor_social_updated_at ON competitor_social_accounts;
CREATE TRIGGER update_competitor_social_updated_at
BEFORE UPDATE ON competitor_social_accounts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_competitor_posts_updated_at ON competitor_posts;
CREATE TRIGGER update_competitor_posts_updated_at
BEFORE UPDATE ON competitor_posts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Calculate engagement rate automatically
CREATE OR REPLACE FUNCTION calculate_engagement_rate()
RETURNS TRIGGER AS $$
DECLARE
  follower_count INTEGER;
BEGIN
  -- Get follower count from social account
  SELECT follower_count INTO follower_count
  FROM competitor_social_accounts
  WHERE id = NEW.social_account_id;

  -- Calculate engagement rate
  IF follower_count > 0 THEN
    NEW.engagement_rate := ((NEW.likes_count + NEW.comments_count + NEW.shares_count)::DECIMAL / follower_count::DECIMAL) * 100;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS calculate_post_engagement ON competitor_posts;
CREATE TRIGGER calculate_post_engagement
BEFORE INSERT OR UPDATE ON competitor_posts
FOR EACH ROW EXECUTE FUNCTION calculate_engagement_rate();

-- =====================================================
-- AUDIT LOGGING TRIGGER
-- =====================================================
CREATE OR REPLACE FUNCTION log_competitor_data_access()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO competitor_data_audit_log (
    action_type,
    data_source,
    resource_type,
    resource_id,
    description,
    legal_basis
  ) VALUES (
    TG_OP,
    NEW.data_source,
    TG_TABLE_NAME,
    NEW.id,
    'Data accessed/modified via ' || NEW.data_source,
    CASE
      WHEN NEW.data_source = 'manual' THEN 'Manual user entry'
      WHEN NEW.data_source = 'official_api' THEN 'Official platform API (authorized)'
      WHEN NEW.data_source IN ('mention', 'brand24', 'hootsuite') THEN 'Third-party service subscription (authorized)'
      ELSE 'Unknown source - REVIEW REQUIRED'
    END
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply audit trigger to posts (most critical)
DROP TRIGGER IF EXISTS audit_competitor_posts ON competitor_posts;
CREATE TRIGGER audit_competitor_posts
AFTER INSERT OR UPDATE ON competitor_posts
FOR EACH ROW EXECUTE FUNCTION log_competitor_data_access();

-- =====================================================
-- SAMPLE DATA (Demo/Testing Only)
-- =====================================================

-- Insert a sample competitor for testing
INSERT INTO competitors (name, party_name, description, data_source)
VALUES
  ('DMK', 'Dravida Munnetra Kazhagam', 'Main opposition party in Tamil Nadu', 'manual'),
  ('ADMK', 'All India Anna Dravida Munnetra Kazhagam', 'Previous ruling party', 'manual'),
  ('BJP Tamil Nadu', 'Bharatiya Janata Party - Tamil Nadu', 'National party''s state unit', 'manual')
ON CONFLICT DO NOTHING;

-- =====================================================
-- INFORMATIONAL COMMENTS
-- =====================================================

COMMENT ON TABLE competitors IS 'Stores competitor profiles. Data collected via LEGAL methods only (APIs, third-party services, manual entry). See docs/COMPETITOR_ANALYSIS_LEGAL_GUIDE.md';

COMMENT ON COLUMN competitor_posts.data_source IS 'CRITICAL: Must be one of: manual, official_api, mention, brand24, hootsuite. NEVER set to scraped/bot/automated.';

COMMENT ON TABLE competitor_data_audit_log IS 'Audit log for legal compliance. Tracks all data collection activities and their legal basis.';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- ✅ This schema is designed for LEGAL data collection only
-- ✅ All data sources are tracked for compliance
-- ✅ Audit logging enabled for transparency
-- ✅ Works standalone (no tenants table dependency)

-- To apply: Run in Supabase SQL Editor or via CLI
