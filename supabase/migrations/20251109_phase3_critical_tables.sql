-- ============================================================================
-- PULSE OF PEOPLE - PHASE 3: CRITICAL ANALYTICS TABLES
-- ============================================================================
-- Created: 2025-11-09
-- Purpose: Core analytics and monitoring tables
-- Dependencies: Phase 1 (organizations, users), Phase 2 (constituencies, wards, booths)
-- Priority: CRITICAL - These are needed to replace mock data
-- ============================================================================

-- ============================================================================
-- ANALYTICS: Sentiment Data (Central Repository)
-- ============================================================================

CREATE TABLE sentiment_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Sentiment Metrics
    sentiment DECIMAL(3, 2) NOT NULL CHECK (sentiment >= 0 AND sentiment <= 1),
    polarity VARCHAR(20) NOT NULL CHECK (polarity IN ('positive', 'negative', 'neutral')),
    intensity DECIMAL(3, 2) CHECK (intensity >= 0 AND intensity <= 1),
    emotion VARCHAR(50) CHECK (emotion IN ('anger', 'trust', 'fear', 'hope', 'pride', 'joy', 'sadness', 'surprise', 'disgust')),
    confidence DECIMAL(3, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),

    -- Context
    issue VARCHAR(100) NOT NULL,
    language VARCHAR(10) NOT NULL CHECK (language IN ('en', 'hi', 'bn', 'mr', 'ta', 'te', 'gu', 'kn', 'ml', 'or', 'pa')),
    source VARCHAR(50) NOT NULL CHECK (source IN ('social_media', 'survey', 'field_report', 'news', 'direct_feedback')),
    source_id UUID, -- References to social_posts, surveys, or field_reports

    -- Location
    constituency_id UUID REFERENCES constituencies(id) ON DELETE SET NULL,
    ward_id UUID REFERENCES wards(id) ON DELETE SET NULL,
    polling_booth_id UUID REFERENCES polling_booths(id) ON DELETE SET NULL,
    location GEOGRAPHY(POINT, 4326),

    -- Demographics (anonymized)
    age_group VARCHAR(20) CHECK (age_group IN ('18-25', '26-35', '36-45', '46-55', '55+')),
    gender VARCHAR(20) CHECK (gender IN ('male', 'female', 'other')),
    education VARCHAR(50) CHECK (education IN ('primary', 'secondary', 'graduate', 'postgraduate')),
    income VARCHAR(50) CHECK (income IN ('low', 'middle', 'high')),

    -- Metadata
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_sentiment_org_timestamp ON sentiment_data(organization_id, timestamp DESC);
CREATE INDEX idx_sentiment_issue ON sentiment_data(issue);
CREATE INDEX idx_sentiment_polarity ON sentiment_data(polarity);
CREATE INDEX idx_sentiment_source ON sentiment_data(source);
CREATE INDEX idx_sentiment_ward ON sentiment_data(ward_id);
CREATE INDEX idx_sentiment_booth ON sentiment_data(polling_booth_id);
CREATE INDEX idx_sentiment_location ON sentiment_data USING GIST(location);

COMMENT ON TABLE sentiment_data IS 'Central repository for all sentiment analysis results';

-- ============================================================================
-- SOCIAL MEDIA: Posts & Monitoring
-- ============================================================================

CREATE TABLE social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Post Identity
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('twitter', 'facebook', 'instagram', 'youtube', 'whatsapp', 'news', 'blog')),
    post_id VARCHAR(255), -- Platform-specific ID
    url TEXT,

    -- Content
    content TEXT NOT NULL,
    language VARCHAR(10) NOT NULL,
    hashtags TEXT[] DEFAULT ARRAY[]::TEXT[],
    mentions TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Author
    author_name VARCHAR(255) NOT NULL,
    author_handle VARCHAR(255),
    author_followers INTEGER DEFAULT 0,
    author_verified BOOLEAN DEFAULT false,

    -- Engagement Metrics
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2),

    -- Sentiment (denormalized for quick access)
    sentiment_score DECIMAL(3, 2),
    sentiment_polarity VARCHAR(20) CHECK (sentiment_polarity IN ('positive', 'negative', 'neutral')),

    -- Location
    location GEOGRAPHY(POINT, 4326),
    place_name VARCHAR(255),

    -- Metadata
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_social_org_timestamp ON social_posts(organization_id, timestamp DESC);
CREATE INDEX idx_social_platform ON social_posts(platform);
CREATE INDEX idx_social_author ON social_posts(author_handle);
CREATE INDEX idx_social_sentiment ON social_posts(sentiment_polarity);
CREATE INDEX idx_social_hashtags ON social_posts USING GIN(hashtags);
CREATE INDEX idx_social_mentions ON social_posts USING GIN(mentions);

COMMENT ON TABLE social_posts IS 'Social media posts with engagement metrics and sentiment';

-- ============================================================================
-- ALERTS: Real-Time Alert System
-- ============================================================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Alert Classification
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'sentiment_spike',
        'volume_surge',
        'crisis_detected',
        'trend_change',
        'competitor_activity',
        'influencer_activity',
        'booth_issue',
        'voter_complaint'
    )),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved', 'dismissed')),

    -- Alert Details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metrics JSONB, -- {current_value, previous_value, threshold, deviation}
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Location
    constituency_id UUID REFERENCES constituencies(id) ON DELETE SET NULL,
    ward_id UUID REFERENCES wards(id) ON DELETE SET NULL,
    polling_booth_id UUID REFERENCES polling_booths(id) ON DELETE SET NULL,

    -- Assignment
    assignee UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMPTZ,

    -- Resolution
    resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_alerts_org_created ON alerts(organization_id, created_at DESC);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_type ON alerts(type);
CREATE INDEX idx_alerts_assignee ON alerts(assignee);
CREATE INDEX idx_alerts_ward ON alerts(ward_id);

COMMENT ON TABLE alerts IS 'Real-time alert system for sentiment spikes and critical events';

-- ============================================================================
-- FIELD OPERATIONS: Field Reports
-- ============================================================================

CREATE TABLE field_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Volunteer
    volunteer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Location
    constituency_id UUID REFERENCES constituencies(id) ON DELETE SET NULL,
    ward_id UUID REFERENCES wards(id) ON DELETE SET NULL,
    polling_booth_id UUID REFERENCES polling_booths(id) ON DELETE SET NULL,
    location GEOGRAPHY(POINT, 4326),
    address TEXT,

    -- Report Details
    report_type VARCHAR(50) NOT NULL CHECK (report_type IN (
        'daily_summary',
        'event_feedback',
        'issue_report',
        'competitor_activity',
        'voter_interaction'
    )),
    title VARCHAR(255) NOT NULL,
    description TEXT,

    -- Content Arrays
    positive_reactions TEXT[] DEFAULT ARRAY[]::TEXT[],
    negative_reactions TEXT[] DEFAULT ARRAY[]::TEXT[],
    issues TEXT[] DEFAULT ARRAY[]::TEXT[],
    quotes TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Media
    media_attachments JSONB DEFAULT '[]'::jsonb, -- [{url, type, caption}]

    -- Metrics
    people_contacted INTEGER DEFAULT 0,
    sentiment_score DECIMAL(3, 2),

    -- Verification
    verification_status VARCHAR(20) DEFAULT 'pending' CHECK (verification_status IN (
        'pending',
        'verified',
        'rejected',
        'flagged'
    )),
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    verified_at TIMESTAMPTZ,
    verification_notes TEXT,

    -- Metadata
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_field_reports_org_timestamp ON field_reports(organization_id, timestamp DESC);
CREATE INDEX idx_field_reports_volunteer ON field_reports(volunteer_id);
CREATE INDEX idx_field_reports_ward ON field_reports(ward_id);
CREATE INDEX idx_field_reports_booth ON field_reports(polling_booth_id);
CREATE INDEX idx_field_reports_type ON field_reports(report_type);
CREATE INDEX idx_field_reports_verification ON field_reports(verification_status);
CREATE INDEX idx_field_reports_location ON field_reports USING GIST(location);

COMMENT ON TABLE field_reports IS 'Ground-level intelligence reports from field volunteers';

-- ============================================================================
-- NOTIFICATIONS: User Notification System
-- ============================================================================

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Notification Details
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'alert',
        'task_assigned',
        'report_verified',
        'mention',
        'system_update',
        'approval_required'
    )),
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    action_url TEXT,

    -- Status
    read_at TIMESTAMPTZ,
    dismissed_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_read ON notifications(user_id, read_at);
CREATE INDEX idx_notifications_type ON notifications(type);

COMMENT ON TABLE notifications IS 'User notification system for in-app alerts and updates';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS
ALTER TABLE sentiment_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Sentiment Data: Users can view their org's data
CREATE POLICY "Users can view org sentiment data"
    ON sentiment_data FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "System can insert sentiment data"
    ON sentiment_data FOR INSERT
    WITH CHECK (true);

-- Social Posts: Users can view their org's data
CREATE POLICY "Users can view org social posts"
    ON social_posts FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

-- Alerts: Users can view their org's alerts
CREATE POLICY "Users can view org alerts"
    ON alerts FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Managers can create alerts"
    ON alerts FOR INSERT
    WITH CHECK (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
    ));

CREATE POLICY "Assigned users can update alerts"
    ON alerts FOR UPDATE
    USING (
        assignee = auth.uid() OR
        organization_id IN (
            SELECT organization_id FROM users
            WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
        )
    );

-- Field Reports: Volunteers can view and create their own
CREATE POLICY "Volunteers can view their reports"
    ON field_reports FOR SELECT
    USING (
        volunteer_id = auth.uid() OR
        organization_id IN (
            SELECT organization_id FROM users
            WHERE id = auth.uid() AND role IN ('admin', 'manager', 'analyst', 'superadmin')
        )
    );

CREATE POLICY "Volunteers can create reports"
    ON field_reports FOR INSERT
    WITH CHECK (volunteer_id = auth.uid());

CREATE POLICY "Managers can verify reports"
    ON field_reports FOR UPDATE
    USING (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
    ));

-- Notifications: Users can view their own
CREATE POLICY "Users can view their notifications"
    ON notifications FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "System can create notifications"
    ON notifications FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Users can update their notifications"
    ON notifications FOR UPDATE
    USING (user_id = auth.uid());

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at
CREATE TRIGGER update_social_posts_updated_at
    BEFORE UPDATE ON social_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at
    BEFORE UPDATE ON alerts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_field_reports_updated_at
    BEFORE UPDATE ON field_reports
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ANALYTICS FUNCTIONS
-- ============================================================================

-- Function: Calculate overall sentiment for a time period
CREATE OR REPLACE FUNCTION calculate_overall_sentiment(
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    ward_filter UUID DEFAULT NULL
)
RETURNS DECIMAL AS $$
DECLARE
    avg_sentiment DECIMAL;
BEGIN
    SELECT AVG(sentiment)
    INTO avg_sentiment
    FROM sentiment_data
    WHERE timestamp >= start_time
      AND timestamp <= end_time
      AND (ward_filter IS NULL OR ward_id = ward_filter);

    RETURN COALESCE(avg_sentiment, 0.5);
END;
$$ LANGUAGE plpgsql;

-- Function: Get trending issues
CREATE OR REPLACE FUNCTION get_trending_issues(
    time_period VARCHAR DEFAULT '24h',
    limit_count INTEGER DEFAULT 5
)
RETURNS TABLE(issue VARCHAR, mention_count BIGINT, avg_sentiment DECIMAL) AS $$
DECLARE
    time_interval INTERVAL;
BEGIN
    -- Convert time_period to interval
    time_interval := CASE time_period
        WHEN '1h' THEN INTERVAL '1 hour'
        WHEN '6h' THEN INTERVAL '6 hours'
        WHEN '24h' THEN INTERVAL '24 hours'
        WHEN '7d' THEN INTERVAL '7 days'
        ELSE INTERVAL '24 hours'
    END;

    RETURN QUERY
    SELECT
        sd.issue,
        COUNT(*) as mention_count,
        AVG(sd.sentiment) as avg_sentiment
    FROM sentiment_data sd
    WHERE sd.timestamp >= NOW() - time_interval
    GROUP BY sd.issue
    ORDER BY mention_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function: Detect sentiment anomalies
CREATE OR REPLACE FUNCTION detect_sentiment_anomalies()
RETURNS TABLE(
    ward_id UUID,
    current_sentiment DECIMAL,
    avg_sentiment DECIMAL,
    deviation DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    WITH ward_stats AS (
        SELECT
            w.id,
            AVG(sd.sentiment) as current_avg,
            (
                SELECT AVG(sentiment)
                FROM sentiment_data
                WHERE ward_id = w.id
                  AND timestamp >= NOW() - INTERVAL '7 days'
                  AND timestamp < NOW() - INTERVAL '24 hours'
            ) as historical_avg
        FROM wards w
        LEFT JOIN sentiment_data sd ON w.id = sd.ward_id
        WHERE sd.timestamp >= NOW() - INTERVAL '24 hours'
        GROUP BY w.id
    )
    SELECT
        ws.id,
        ws.current_avg,
        ws.historical_avg,
        ABS(ws.current_avg - ws.historical_avg) as deviation
    FROM ward_stats ws
    WHERE ws.historical_avg IS NOT NULL
      AND ABS(ws.current_avg - ws.historical_avg) > 0.15
    ORDER BY deviation DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('sentiment_data', 'social_posts', 'alerts', 'field_reports', 'notifications')
ORDER BY table_name;

-- Verify functions created
SELECT routine_name
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name IN ('calculate_overall_sentiment', 'get_trending_issues', 'detect_sentiment_anomalies')
ORDER BY routine_name;

-- Test analytics functions
SELECT * FROM get_trending_issues('24h', 5);
SELECT * FROM detect_sentiment_anomalies();

COMMENT ON TABLE sentiment_data IS 'Phase 3: Critical analytics table - replaces mock sentiment data';
COMMENT ON TABLE social_posts IS 'Phase 3: Social media monitoring - replaces mock social posts';
COMMENT ON TABLE alerts IS 'Phase 3: Real-time alerting - replaces mock alerts';
COMMENT ON TABLE field_reports IS 'Phase 3: Field operations - replaces mock field reports';
COMMENT ON TABLE notifications IS 'Phase 3: User notifications - replaces mock notifications';
