-- =====================================================
-- COMPETITOR ANALYSIS - DATABASE SCHEMA
-- =====================================================
-- Legal data collection only (APIs + Third-party services)
-- NO web scraping - all data from authorized sources
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. COMPETITORS TABLE
-- =====================================================
-- Stores competitor profiles (parties, candidates)
CREATE TABLE IF NOT EXISTS competitors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

  -- Basic Info
  name VARCHAR(255) NOT NULL,
  party_name VARCHAR(255),
  party_acronym VARCHAR(50),
  leader_name VARCHAR(255),
  logo_url TEXT,
  color_code VARCHAR(7) DEFAULT '#6B7280', -- Hex color for UI
  description TEXT,

  -- Geographic Focus
  country VARCHAR(100) DEFAULT 'India',
  state VARCHAR(100),
  district VARCHAR(100),
  constituency VARCHAR(100),
  geographic_focus JSONB, -- {type: 'state|district|constituency', regions: [...]}

  -- Campaign Info
  campaign_slogan TEXT,
  campaign_themes JSONB, -- ['education', 'healthcare', 'jobs']
  estimated_budget DECIMAL(15,2),
  active_since DATE,

  -- Data Source Tracking (Legal compliance)
  data_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'mention', 'brand24', 'hootsuite'
  data_source_config JSONB, -- API credentials, webhook URLs, etc.
  last_synced_at TIMESTAMP,

  -- Metadata
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,
  tags JSONB, -- ['main_opponent', 'coalition_partner', etc.]

  created_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_competitors_tenant ON competitors(tenant_id);
CREATE INDEX idx_competitors_party ON competitors(party_name);
CREATE INDEX idx_competitors_active ON competitors(is_active);
CREATE INDEX idx_competitors_constituency ON competitors(constituency);

-- =====================================================
-- 2. COMPETITOR SOCIAL MEDIA ACCOUNTS
-- =====================================================
-- Track competitor social media presence (public accounts only)
CREATE TABLE IF NOT EXISTS competitor_social_accounts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,

  -- Platform Info
  platform VARCHAR(50) NOT NULL, -- 'facebook', 'twitter', 'instagram', 'youtube', 'linkedin'
  handle VARCHAR(255) NOT NULL, -- @username or page name
  profile_url TEXT,

  -- Public Metrics (from official APIs or third-party services)
  follower_count INTEGER DEFAULT 0,
  following_count INTEGER DEFAULT 0,
  post_count INTEGER DEFAULT 0,
  verified BOOLEAN DEFAULT FALSE,

  -- Account Details
  account_name VARCHAR(255),
  account_bio TEXT,
  account_created_date DATE,

  -- Data Source (Legal compliance tracking)
  data_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'official_api', 'mention', 'brand24'
  api_credentials_encrypted TEXT, -- Encrypted if storing API keys

  -- Metadata
  is_active BOOLEAN DEFAULT TRUE,
  last_updated_at TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_competitor_social_competitor ON competitor_social_accounts(competitor_id);
CREATE INDEX idx_competitor_social_platform ON competitor_social_accounts(platform);
CREATE UNIQUE INDEX idx_competitor_social_unique ON competitor_social_accounts(competitor_id, platform, handle);

-- =====================================================
-- 3. COMPETITOR POSTS (Aggregated from Legal Sources)
-- =====================================================
-- Stores posts from competitors (via APIs or third-party services only)
CREATE TABLE IF NOT EXISTS competitor_posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
  social_account_id UUID REFERENCES competitor_social_accounts(id) ON DELETE CASCADE,

  -- Post Details
  platform VARCHAR(50) NOT NULL,
  post_id VARCHAR(255) NOT NULL, -- Platform-specific ID
  post_url TEXT,
  content TEXT,
  post_type VARCHAR(50), -- 'text', 'image', 'video', 'link', 'poll'
  media_urls JSONB, -- Array of image/video URLs
  posted_at TIMESTAMP NOT NULL,

  -- Engagement Metrics (public data only)
  likes_count INTEGER DEFAULT 0,
  comments_count INTEGER DEFAULT 0,
  shares_count INTEGER DEFAULT 0,
  retweets_count INTEGER DEFAULT 0,
  views_count INTEGER DEFAULT 0,
  reactions_breakdown JSONB, -- {like: 100, love: 50, angry: 10, ...}

  -- Analysis
  engagement_rate DECIMAL(5,2), -- Calculated: (likes+comments+shares)/followers * 100
  sentiment_score DECIMAL(4,3), -- -1.000 to 1.000 (from AI analysis)
  sentiment_label VARCHAR(20), -- 'positive', 'neutral', 'negative'

  -- Content Classification
  topics JSONB, -- ['education', 'healthcare', 'infrastructure']
  hashtags JSONB, -- ['#TVK', '#TamilNadu']
  mentions JSONB, -- ['@leader', '@party']
  keywords JSONB, -- Extracted keywords
  language VARCHAR(10) DEFAULT 'en',

  -- Data Source (Legal compliance)
  data_source VARCHAR(50) DEFAULT 'manual', -- 'official_api', 'mention', 'brand24', 'manual'
  raw_data JSONB, -- Original API response for audit trail

  -- Metadata
  is_viral BOOLEAN DEFAULT FALSE, -- Flag high-performing posts
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_competitor_posts_competitor ON competitor_posts(competitor_id);
CREATE INDEX idx_competitor_posts_platform ON competitor_posts(platform);
CREATE INDEX idx_competitor_posts_posted_at ON competitor_posts(posted_at DESC);
CREATE INDEX idx_competitor_posts_engagement ON competitor_posts(engagement_rate DESC);
CREATE UNIQUE INDEX idx_competitor_posts_unique ON competitor_posts(platform, post_id);

-- =====================================================
-- 4. COMPETITOR SENTIMENT HISTORY
-- =====================================================
-- Daily/weekly sentiment tracking
CREATE TABLE IF NOT EXISTS competitor_sentiment_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,

  -- Time Period
  date DATE NOT NULL,
  period_type VARCHAR(20) DEFAULT 'daily', -- 'daily', 'weekly', 'monthly'

  -- Platform-specific sentiment
  platform VARCHAR(50), -- NULL for overall sentiment

  -- Sentiment Metrics
  sentiment_score DECIMAL(4,3), -- Average sentiment (-1 to 1)
  positive_count INTEGER DEFAULT 0,
  neutral_count INTEGER DEFAULT 0,
  negative_count INTEGER DEFAULT 0,
  total_mentions INTEGER DEFAULT 0,

  -- Engagement Aggregates
  total_engagement INTEGER DEFAULT 0,
  post_count INTEGER DEFAULT 0,
  avg_engagement_rate DECIMAL(5,2),

  -- Data Source
  data_source VARCHAR(50) DEFAULT 'manual',

  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_sentiment_history_competitor ON competitor_sentiment_history(competitor_id);
CREATE INDEX idx_sentiment_history_date ON competitor_sentiment_history(date DESC);
CREATE UNIQUE INDEX idx_sentiment_history_unique ON competitor_sentiment_history(competitor_id, date, platform);

-- =====================================================
-- 5. COMPETITOR CAMPAIGNS
-- =====================================================
-- Track specific campaigns/initiatives by competitors
CREATE TABLE IF NOT EXISTS competitor_campaigns (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,

  -- Campaign Details
  campaign_name VARCHAR(255) NOT NULL,
  campaign_slogan TEXT,
  campaign_type VARCHAR(50), -- 'issue-based', 'personal-branding', 'attack-ad', 'grassroots'
  description TEXT,

  -- Timeline
  start_date DATE,
  end_date DATE,
  status VARCHAR(20) DEFAULT 'active', -- 'active', 'paused', 'completed'

  -- Performance Metrics (public data only)
  estimated_reach INTEGER,
  total_engagement INTEGER,
  sentiment_score DECIMAL(4,3),

  -- Platforms Used
  platforms JSONB, -- ['facebook', 'twitter', 'instagram']

  -- Topics/Themes
  topics JSONB,
  hashtags JSONB,

  -- Budget/Resources
  estimated_budget DECIMAL(15,2),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_competitor_campaigns_competitor ON competitor_campaigns(competitor_id);
CREATE INDEX idx_competitor_campaigns_status ON competitor_campaigns(status);

-- =====================================================
-- 6. COMPETITOR INFLUENCERS
-- =====================================================
-- Track influencers supporting competitors (public data only)
CREATE TABLE IF NOT EXISTS competitor_influencers (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,

  -- Influencer Details
  influencer_name VARCHAR(255) NOT NULL,
  platform VARCHAR(50) NOT NULL,
  handle VARCHAR(255) NOT NULL,
  profile_url TEXT,

  -- Metrics (public data only)
  follower_count INTEGER,
  engagement_rate DECIMAL(5,2),
  verified BOOLEAN DEFAULT FALSE,

  -- Relationship Tracking
  first_mentioned_at TIMESTAMP,
  last_mentioned_at TIMESTAMP,
  mention_count INTEGER DEFAULT 0,

  -- Influencer Category
  category VARCHAR(50), -- 'celebrity', 'journalist', 'activist', 'local-leader'

  -- Data Source
  data_source VARCHAR(50) DEFAULT 'manual',

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_competitor_influencers_competitor ON competitor_influencers(competitor_id);
CREATE INDEX idx_competitor_influencers_platform ON competitor_influencers(platform);

-- =====================================================
-- 7. COMPETITOR CRISIS ALERTS
-- =====================================================
-- Track PR crises, controversies, negative trends
CREATE TABLE IF NOT EXISTS competitor_crisis_alerts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,

  -- Crisis Details
  alert_type VARCHAR(50) NOT NULL, -- 'sentiment_drop', 'controversy', 'viral_negative', 'scandal'
  severity VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
  title VARCHAR(255) NOT NULL,
  description TEXT,

  -- Detection
  detected_at TIMESTAMP NOT NULL,
  detected_by VARCHAR(50), -- 'auto_sentiment', 'manual', 'mention', 'brand24'

  -- Metrics
  sentiment_drop DECIMAL(4,3), -- How much sentiment dropped
  negative_mentions INTEGER,
  platforms_affected JSONB,

  -- Resolution
  status VARCHAR(20) DEFAULT 'active', -- 'active', 'monitoring', 'resolved'
  resolved_at TIMESTAMP,
  resolution_notes TEXT,

  -- Related Content
  related_posts JSONB, -- Array of post IDs

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_crisis_alerts_competitor ON competitor_crisis_alerts(competitor_id);
CREATE INDEX idx_crisis_alerts_severity ON competitor_crisis_alerts(severity);
CREATE INDEX idx_crisis_alerts_status ON competitor_crisis_alerts(status);

-- =====================================================
-- 8. DATA SOURCE CONFIGURATIONS
-- =====================================================
-- Store third-party service configurations (encrypted credentials)
CREATE TABLE IF NOT EXISTS competitor_data_sources (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

  -- Service Details
  service_name VARCHAR(50) NOT NULL, -- 'mention', 'brand24', 'hootsuite', 'brandwatch'
  service_type VARCHAR(50) DEFAULT 'social_listening',

  -- Configuration (ENCRYPTED)
  api_key_encrypted TEXT, -- Use pgcrypto for encryption
  api_secret_encrypted TEXT,
  webhook_url TEXT,
  config JSONB, -- Service-specific settings

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  subscription_plan VARCHAR(50),
  subscription_expires_at TIMESTAMP,
  monthly_cost DECIMAL(10,2),

  -- Usage Tracking
  last_sync_at TIMESTAMP,
  sync_frequency_minutes INTEGER DEFAULT 60, -- How often to poll API

  -- Limits
  monthly_quota INTEGER, -- API calls per month
  quota_used INTEGER DEFAULT 0,
  quota_reset_at TIMESTAMP,

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_data_sources_tenant ON competitor_data_sources(tenant_id);
CREATE INDEX idx_data_sources_active ON competitor_data_sources(is_active);

-- =====================================================
-- 9. AUDIT LOG (Legal Compliance)
-- =====================================================
-- Track all data collection activities for compliance
CREATE TABLE IF NOT EXISTS competitor_data_audit_log (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

  -- Activity Details
  action_type VARCHAR(50) NOT NULL, -- 'api_call', 'manual_entry', 'sync', 'export'
  data_source VARCHAR(50) NOT NULL, -- 'mention', 'brand24', 'manual', 'official_api'
  resource_type VARCHAR(50), -- 'post', 'profile', 'sentiment'
  resource_id UUID,

  -- User
  user_id UUID REFERENCES users(id),

  -- Details
  description TEXT,
  metadata JSONB, -- Request/response details

  -- Legal Compliance
  tos_compliant BOOLEAN DEFAULT TRUE, -- Was this action ToS-compliant?
  consent_obtained BOOLEAN DEFAULT TRUE,

  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_log_tenant ON competitor_data_audit_log(tenant_id);
CREATE INDEX idx_audit_log_created_at ON competitor_data_audit_log(created_at DESC);
CREATE INDEX idx_audit_log_user ON competitor_data_audit_log(user_id);

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_social_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_sentiment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_influencers ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_crisis_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_data_audit_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies (Users can only see their tenant's data)
CREATE POLICY competitor_tenant_isolation ON competitors
  USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE POLICY competitor_social_tenant_isolation ON competitor_social_accounts
  USING (competitor_id IN (SELECT id FROM competitors WHERE tenant_id = current_setting('app.current_tenant_id')::UUID));

CREATE POLICY competitor_posts_tenant_isolation ON competitor_posts
  USING (competitor_id IN (SELECT id FROM competitors WHERE tenant_id = current_setting('app.current_tenant_id')::UUID));

-- Similar policies for other tables...

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

CREATE TRIGGER update_competitors_updated_at BEFORE UPDATE ON competitors
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitor_social_updated_at BEFORE UPDATE ON competitor_social_accounts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitor_posts_updated_at BEFORE UPDATE ON competitor_posts
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

CREATE TRIGGER calculate_post_engagement BEFORE INSERT OR UPDATE ON competitor_posts
  FOR EACH ROW EXECUTE FUNCTION calculate_engagement_rate();

-- =====================================================
-- SAMPLE DATA (For Development/Testing)
-- =====================================================

-- NOTE: This is demo data only. In production, populate via:
-- 1. Manual entry through Competitor Registry
-- 2. API integrations with third-party services
-- 3. Official platform APIs (for public data only)

-- Insert sample competitor (replace with real data)
-- INSERT INTO competitors (tenant_id, name, party_name, description, data_source)
-- VALUES (
--   'your-tenant-id',
--   'DMK',
--   'Dravida Munnetra Kazhagam',
--   'Main opposition party in Tamil Nadu',
--   'manual'
-- );

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

-- To apply this migration:
-- psql $DATABASE_URL -f database/migrations/competitor_tracking_schema.sql

-- Or using Supabase CLI:
-- supabase db reset
-- supabase migration up
