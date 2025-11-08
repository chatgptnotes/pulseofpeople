-- =====================================================
-- TV & BROADCAST ANALYSIS DATABASE SCHEMA
-- =====================================================
-- Migration Date: 2025-11-09
-- Purpose: Track TV channels, shows, and broadcast segments
-- =====================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. TV CHANNELS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS tv_channels (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

  -- Channel Info
  channel_code VARCHAR(100) UNIQUE NOT NULL, -- 'sun-news', 'thanthi-tv'
  name VARCHAR(255) NOT NULL,
  logo_url TEXT,
  language VARCHAR(50) NOT NULL, -- 'Tamil', 'English', 'Hindi'
  type VARCHAR(50) NOT NULL, -- 'news', 'entertainment', 'regional', 'national'

  -- Analytics
  viewership_count INTEGER DEFAULT 0,
  credibility_score DECIMAL(5,2) DEFAULT 0.00, -- 0.00 to 100.00
  bias VARCHAR(20) DEFAULT 'neutral', -- 'left', 'center', 'right', 'neutral'

  -- Broadcasting Info
  region VARCHAR(100), -- 'Tamil Nadu', 'National', 'Karnataka'
  prime_time_start TIME, -- '19:00'
  prime_time_end TIME, -- '23:00'

  -- Live Status
  is_live BOOLEAN DEFAULT FALSE,
  current_show VARCHAR(255),

  -- Data Source
  data_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'api', 'barc', 'trai'
  verified BOOLEAN DEFAULT FALSE,

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  notes TEXT,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tv_channels_language ON tv_channels(language);
CREATE INDEX IF NOT EXISTS idx_tv_channels_type ON tv_channels(type);
CREATE INDEX IF NOT EXISTS idx_tv_channels_region ON tv_channels(region);
CREATE INDEX IF NOT EXISTS idx_tv_channels_active ON tv_channels(is_active);

-- =====================================================
-- 2. TV SHOWS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS tv_shows (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES tv_channels(id) ON DELETE CASCADE,

  -- Show Info
  name VARCHAR(255) NOT NULL,
  description TEXT,
  show_type VARCHAR(50), -- 'news', 'debate', 'talk-show', 'documentary'

  -- Scheduling
  time_slot VARCHAR(50), -- '19:00-20:00', 'Prime Time'
  day_of_week VARCHAR(20)[], -- ['Monday', 'Tuesday', 'Wednesday']
  duration_minutes INTEGER, -- 60

  -- Analytics
  average_viewership INTEGER DEFAULT 0,
  sentiment_trend DECIMAL(4,3)[], -- Array of sentiment scores over time
  credibility_rating DECIMAL(5,2) DEFAULT 0.00,
  bias_score DECIMAL(4,3) DEFAULT 0.000, -- -1.000 to 1.000

  -- Content
  topics_discussed TEXT[], -- ['politics', 'economy', 'social']
  political_coverage_percent DECIMAL(5,2) DEFAULT 0.00,

  -- Host/Anchor
  anchor_name VARCHAR(255),
  guest_influence_score DECIMAL(5,2) DEFAULT 0.00,

  -- Status
  is_active BOOLEAN DEFAULT TRUE,
  last_aired_at TIMESTAMP,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tv_shows_channel ON tv_shows(channel_id);
CREATE INDEX IF NOT EXISTS idx_tv_shows_active ON tv_shows(is_active);

-- =====================================================
-- 3. BROADCAST SEGMENTS TABLE (Main Data)
-- =====================================================
CREATE TABLE IF NOT EXISTS broadcast_segments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES tv_channels(id) ON DELETE CASCADE,
  show_id UUID REFERENCES tv_shows(id) ON DELETE SET NULL,

  -- Segment Info
  channel_code VARCHAR(100) NOT NULL,
  show_name VARCHAR(255) NOT NULL,
  segment_title VARCHAR(500),
  segment_number INTEGER,

  -- Timing
  broadcast_date DATE NOT NULL,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP,
  duration_seconds INTEGER, -- Auto-calculated

  -- Content
  topic VARCHAR(500),
  description TEXT,
  transcription TEXT, -- Full text transcript
  summary TEXT, -- AI-generated summary
  keywords TEXT[], -- ['vijay', 'tvk', 'election']

  -- People/Entities Mentioned
  mentions TEXT[], -- ['Vijay', 'Stalin', 'Modi']
  political_parties TEXT[], -- ['TVK', 'DMK', 'BJP']
  politicians TEXT[], -- ['Vijay', 'M.K. Stalin']

  -- Sentiment Analysis
  sentiment VARCHAR(20) DEFAULT 'neutral', -- 'positive', 'negative', 'neutral'
  sentiment_score DECIMAL(4,3) DEFAULT 0.000, -- -1.000 to 1.000

  -- Engagement Metrics
  viewer_engagement_score DECIMAL(5,2) DEFAULT 0.00,
  social_media_mentions INTEGER DEFAULT 0,

  -- Media Assets
  clip_url TEXT, -- Video clip URL
  thumbnail_url TEXT,

  -- Priority & Alerts
  priority VARCHAR(20) DEFAULT 'medium', -- 'high', 'medium', 'low'
  is_flagged BOOLEAN DEFAULT FALSE,
  flag_reason TEXT,

  -- Status
  is_live BOOLEAN DEFAULT FALSE,
  processing_status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'

  -- Data Source
  data_source VARCHAR(50) DEFAULT 'manual', -- 'manual', 'api', 'rss', 'monitoring_service'

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_channel ON broadcast_segments(channel_id);
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_show ON broadcast_segments(show_id);
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_date ON broadcast_segments(broadcast_date DESC);
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_start_time ON broadcast_segments(start_time DESC);
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_sentiment ON broadcast_segments(sentiment);
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_priority ON broadcast_segments(priority);
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_live ON broadcast_segments(is_live);

-- Full-text search on transcription
CREATE INDEX IF NOT EXISTS idx_broadcast_segments_transcription
  ON broadcast_segments USING gin(to_tsvector('english', transcription));

-- =====================================================
-- 4. VIEWERSHIP DATA (BARC/TRAI Integration)
-- =====================================================
CREATE TABLE IF NOT EXISTS tv_viewership_data (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES tv_channels(id) ON DELETE CASCADE,
  show_id UUID REFERENCES tv_shows(id) ON DELETE CASCADE,

  -- Time Period
  date DATE NOT NULL,
  time_slot VARCHAR(50), -- '19:00-20:00'

  -- Metrics
  viewership_count INTEGER DEFAULT 0,
  tvr DECIMAL(5,3) DEFAULT 0.000, -- Television Rating Point
  reach_percentage DECIMAL(5,2) DEFAULT 0.00,

  -- Demographics (from BARC)
  age_group VARCHAR(20), -- '18-24', '25-34', '35-49', '50+'
  gender VARCHAR(20), -- 'male', 'female', 'all'
  socio_economic_class VARCHAR(10), -- 'sec-a', 'sec-b', 'sec-c'

  -- Geographic
  region VARCHAR(100),
  urban_rural VARCHAR(20), -- 'urban', 'rural', 'all'

  -- Data Source
  data_source VARCHAR(50) DEFAULT 'manual', -- 'barc', 'trai', 'manual'

  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_viewership_channel ON tv_viewership_data(channel_id);
CREATE INDEX IF NOT EXISTS idx_viewership_date ON tv_viewership_data(date DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_viewership_unique
  ON tv_viewership_data(channel_id, date, time_slot, COALESCE(age_group, ''), COALESCE(gender, ''));

-- =====================================================
-- 5. SENTIMENT TRENDS (Aggregated)
-- =====================================================
CREATE TABLE IF NOT EXISTS tv_sentiment_trends (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  channel_id UUID REFERENCES tv_channels(id) ON DELETE CASCADE,

  -- Time Period
  date DATE NOT NULL,
  period_type VARCHAR(20) DEFAULT 'daily', -- 'hourly', 'daily', 'weekly'

  -- Sentiment Metrics
  avg_sentiment_score DECIMAL(4,3),
  positive_count INTEGER DEFAULT 0,
  neutral_count INTEGER DEFAULT 0,
  negative_count INTEGER DEFAULT 0,
  total_segments INTEGER DEFAULT 0,

  -- Top Topics
  top_topics TEXT[],
  top_mentions TEXT[],

  -- Engagement
  total_engagement INTEGER DEFAULT 0,

  created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_sentiment_trends_channel ON tv_sentiment_trends(channel_id);
CREATE INDEX IF NOT EXISTS idx_sentiment_trends_date ON tv_sentiment_trends(date DESC);

-- =====================================================
-- TRIGGERS & FUNCTIONS
-- =====================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
DROP TRIGGER IF EXISTS update_tv_channels_updated_at ON tv_channels;
CREATE TRIGGER update_tv_channels_updated_at
BEFORE UPDATE ON tv_channels
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tv_shows_updated_at ON tv_shows;
CREATE TRIGGER update_tv_shows_updated_at
BEFORE UPDATE ON tv_shows
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_broadcast_segments_updated_at ON broadcast_segments;
CREATE TRIGGER update_broadcast_segments_updated_at
BEFORE UPDATE ON broadcast_segments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-calculate duration
CREATE OR REPLACE FUNCTION calculate_segment_duration()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.end_time IS NOT NULL AND NEW.start_time IS NOT NULL THEN
    NEW.duration_seconds := EXTRACT(EPOCH FROM (NEW.end_time - NEW.start_time))::INTEGER;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS calculate_broadcast_duration ON broadcast_segments;
CREATE TRIGGER calculate_broadcast_duration
BEFORE INSERT OR UPDATE ON broadcast_segments
FOR EACH ROW EXECUTE FUNCTION calculate_segment_duration();

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE tv_channels IS 'Stores TV channel information for Tamil Nadu and National channels';
COMMENT ON TABLE tv_shows IS 'Stores TV show schedules and analytics';
COMMENT ON TABLE broadcast_segments IS 'Main table storing individual broadcast segments with sentiment analysis';
COMMENT ON TABLE tv_viewership_data IS 'BARC/TRAI viewership data integration';
COMMENT ON TABLE tv_sentiment_trends IS 'Aggregated sentiment trends over time';

COMMENT ON COLUMN broadcast_segments.transcription IS 'Full text transcription for search and analysis. Consider using speech-to-text services like Google Cloud Speech or AWS Transcribe';
COMMENT ON COLUMN tv_viewership_data.data_source IS 'BARC (Broadcast Audience Research Council) is the official TV ratings provider in India';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
