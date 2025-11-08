-- =====================================================
-- PULSE OF PEOPLE - COMPLETE DATABASE SCHEMA
-- BETTROI Voter Sentiment Dashboard
-- Generated: 2025-10-27
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =====================================================
-- 1. USERS & AUTHENTICATION
-- =====================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    avatar TEXT,
    role TEXT NOT NULL CHECK (role IN ('admin', 'analyst', 'viewer', 'ward-coordinator', 'social-media', 'survey-team', 'truth-team')),
    permissions TEXT[] DEFAULT ARRAY[]::TEXT[],
    ward TEXT,
    constituency TEXT,
    state TEXT DEFAULT 'Kerala',
    district TEXT,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    last_login TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_ward ON users(ward);
CREATE INDEX idx_users_status ON users(status);

-- =====================================================
-- 2. SENTIMENT DATA
-- =====================================================

CREATE TABLE sentiment_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    issue TEXT NOT NULL CHECK (issue IN ('Jobs', 'Infrastructure', 'Health', 'Education', 'Law & Order', 'Other')),
    sentiment DECIMAL(3, 2) NOT NULL CHECK (sentiment >= 0 AND sentiment <= 1),
    polarity TEXT NOT NULL CHECK (polarity IN ('positive', 'negative', 'neutral')),
    intensity DECIMAL(3, 2) CHECK (intensity >= 0 AND intensity <= 1),
    emotion TEXT CHECK (emotion IN ('anger', 'trust', 'fear', 'hope', 'pride', 'joy', 'sadness', 'surprise', 'disgust')),
    confidence DECIMAL(3, 2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    language TEXT NOT NULL CHECK (language IN ('en', 'hi', 'bn', 'mr', 'ta', 'te', 'gu', 'kn', 'ml', 'or', 'pa')),
    source TEXT NOT NULL CHECK (source IN ('social_media', 'survey', 'field_report', 'news', 'direct_feedback')),
    source_id UUID, -- References to social_posts, surveys, or field_reports
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Location data
    state TEXT,
    district TEXT,
    ward TEXT,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    location_point GEOGRAPHY(POINT, 4326), -- PostGIS point for spatial queries

    -- Demographic data (anonymized)
    age_group TEXT CHECK (age_group IN ('18-25', '26-35', '36-45', '46-55', '55+')),
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    education TEXT CHECK (education IN ('primary', 'secondary', 'graduate', 'postgraduate')),
    income TEXT CHECK (income IN ('low', 'middle', 'high')),

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_sentiment_data_issue ON sentiment_data(issue);
CREATE INDEX idx_sentiment_data_timestamp ON sentiment_data(timestamp DESC);
CREATE INDEX idx_sentiment_data_ward ON sentiment_data(ward);
CREATE INDEX idx_sentiment_data_source ON sentiment_data(source);
CREATE INDEX idx_sentiment_data_polarity ON sentiment_data(polarity);
CREATE INDEX idx_sentiment_data_emotion ON sentiment_data(emotion);
CREATE INDEX idx_sentiment_data_location_point ON sentiment_data USING GIST(location_point);

-- =====================================================
-- 3. SOCIAL MEDIA POSTS
-- =====================================================

CREATE TABLE social_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform TEXT NOT NULL CHECK (platform IN ('twitter', 'facebook', 'instagram', 'youtube', 'whatsapp', 'news', 'blog')),
    post_id TEXT UNIQUE, -- Platform-specific ID
    content TEXT NOT NULL,
    language TEXT NOT NULL,
    url TEXT,
    author_name TEXT NOT NULL,
    author_handle TEXT,
    author_followers INTEGER DEFAULT 0,
    author_verified BOOLEAN DEFAULT FALSE,

    -- Engagement metrics
    likes INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    reach INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5, 2),

    -- Content analysis
    hashtags TEXT[] DEFAULT ARRAY[]::TEXT[],
    mentions TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Sentiment (denormalized from sentiment_data for quick access)
    sentiment_score DECIMAL(3, 2),
    sentiment_polarity TEXT CHECK (sentiment_polarity IN ('positive', 'negative', 'neutral')),

    -- Location
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    place_name TEXT,

    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_social_posts_platform ON social_posts(platform);
CREATE INDEX idx_social_posts_timestamp ON social_posts(timestamp DESC);
CREATE INDEX idx_social_posts_author_handle ON social_posts(author_handle);
CREATE INDEX idx_social_posts_sentiment ON social_posts(sentiment_polarity);
CREATE INDEX idx_social_posts_hashtags ON social_posts USING GIN(hashtags);

-- =====================================================
-- 4. INFLUENCERS
-- =====================================================

CREATE TABLE influencers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    handle TEXT UNIQUE NOT NULL,
    avatar TEXT,
    platforms TEXT[] NOT NULL,
    total_followers BIGINT DEFAULT 0,
    engagement_rate DECIMAL(5, 2),
    influence_score DECIMAL(5, 2) CHECK (influence_score >= 0 AND influence_score <= 100),

    -- Classification
    category TEXT CHECK (category IN ('political', 'celebrity', 'journalist', 'activist', 'business', 'academic', 'religious', 'local')),
    political_lean TEXT CHECK (political_lean IN ('left', 'center', 'right', 'neutral', 'unknown')),

    -- Metrics
    sentiment_score DECIMAL(3, 2),
    verified BOOLEAN DEFAULT FALSE,
    credibility_score DECIMAL(3, 2) CHECK (credibility_score >= 0 AND credibility_score <= 1),
    reach_estimate BIGINT,
    viral_posts INTEGER DEFAULT 0,
    mentions INTEGER DEFAULT 0,

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    last_active TIMESTAMPTZ,
    collaboration TEXT CHECK (collaboration IN ('high', 'medium', 'low', 'none')),
    risk_level TEXT CHECK (risk_level IN ('high', 'medium', 'low')),

    -- Location
    location TEXT,
    languages TEXT[] DEFAULT ARRAY[]::TEXT[],

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_influencers_handle ON influencers(handle);
CREATE INDEX idx_influencers_category ON influencers(category);
CREATE INDEX idx_influencers_influence_score ON influencers(influence_score DESC);
CREATE INDEX idx_influencers_risk_level ON influencers(risk_level);
CREATE INDEX idx_influencers_platforms ON influencers USING GIN(platforms);

-- =====================================================
-- 5. TRENDING TOPICS
-- =====================================================

CREATE TABLE trending_topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    keyword TEXT NOT NULL,
    volume INTEGER DEFAULT 0,
    growth_rate DECIMAL(5, 2),
    sentiment_score DECIMAL(3, 2),
    related_posts UUID[] DEFAULT ARRAY[]::UUID[], -- References to social_posts
    platforms TEXT[] DEFAULT ARRAY[]::TEXT[],
    time_period TEXT NOT NULL CHECK (time_period IN ('1h', '6h', '24h', '7d')),
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    last_updated TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_trending_topics_keyword ON trending_topics(keyword);
CREATE INDEX idx_trending_topics_timestamp ON trending_topics(timestamp DESC);
CREATE INDEX idx_trending_topics_volume ON trending_topics(volume DESC);
CREATE INDEX idx_trending_topics_growth ON trending_topics(growth_rate DESC);

-- =====================================================
-- 6. ALERTS
-- =====================================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    type TEXT NOT NULL CHECK (type IN ('sentiment_spike', 'volume_surge', 'crisis_detected', 'trend_change', 'competitor_activity', 'influencer_activity')),

    -- Context
    ward TEXT,
    district TEXT,
    issue TEXT,

    -- Metrics
    current_value DECIMAL(10, 2),
    previous_value DECIMAL(10, 2),
    change_percentage DECIMAL(5, 2),
    threshold DECIMAL(10, 2),

    -- Resolution
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved', 'dismissed')),
    assignee UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],

    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp DESC);
CREATE INDEX idx_alerts_type ON alerts(type);
CREATE INDEX idx_alerts_ward ON alerts(ward);
CREATE INDEX idx_alerts_assignee ON alerts(assignee);

-- =====================================================
-- 7. FIELD REPORTS
-- =====================================================

CREATE TABLE field_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    volunteer_id UUID REFERENCES users(id) NOT NULL,

    -- Location
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lng DECIMAL(11, 8) NOT NULL,
    location_point GEOGRAPHY(POINT, 4326),
    address TEXT,
    ward TEXT NOT NULL,
    district TEXT,

    -- Report details
    report_type TEXT NOT NULL CHECK (report_type IN ('daily_summary', 'event_feedback', 'issue_report', 'competitor_activity')),

    -- Content
    positive_reactions TEXT[] DEFAULT ARRAY[]::TEXT[],
    negative_reactions TEXT[] DEFAULT ARRAY[]::TEXT[],
    key_issues TEXT[] DEFAULT ARRAY[]::TEXT[],
    crowd_size INTEGER,
    quotes TEXT[] DEFAULT ARRAY[]::TEXT[],
    notes TEXT,

    -- Media
    media_attachments TEXT[] DEFAULT ARRAY[]::TEXT[], -- URLs to uploaded files

    -- Verification
    verification_status TEXT DEFAULT 'pending' CHECK (verification_status IN ('pending', 'verified', 'disputed')),
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    verification_notes TEXT,

    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_field_reports_volunteer ON field_reports(volunteer_id);
CREATE INDEX idx_field_reports_ward ON field_reports(ward);
CREATE INDEX idx_field_reports_timestamp ON field_reports(timestamp DESC);
CREATE INDEX idx_field_reports_verification ON field_reports(verification_status);
CREATE INDEX idx_field_reports_type ON field_reports(report_type);
CREATE INDEX idx_field_reports_location ON field_reports USING GIST(location_point);

-- =====================================================
-- 8. SURVEYS
-- =====================================================

CREATE TABLE surveys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'completed', 'archived')),

    -- Target demographics
    target_age_groups TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_locations TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_sample_size INTEGER,

    -- Results summary
    response_count INTEGER DEFAULT 0,
    response_rate DECIMAL(5, 2),
    confidence_level DECIMAL(5, 2),
    margin_of_error DECIMAL(5, 2),

    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ
);

CREATE INDEX idx_surveys_status ON surveys(status);
CREATE INDEX idx_surveys_created_by ON surveys(created_by);
CREATE INDEX idx_surveys_created_at ON surveys(created_at DESC);

-- =====================================================
-- 9. SURVEY QUESTIONS
-- =====================================================

CREATE TABLE survey_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id UUID REFERENCES surveys(id) ON DELETE CASCADE NOT NULL,
    question_order INTEGER NOT NULL,
    text TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('multiple_choice', 'rating', 'text', 'yes_no')),
    options JSONB, -- Array of options for multiple choice
    required BOOLEAN DEFAULT TRUE,
    sentiment_analysis BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_survey_questions_survey ON survey_questions(survey_id);
CREATE INDEX idx_survey_questions_order ON survey_questions(survey_id, question_order);

-- =====================================================
-- 10. SURVEY RESPONSES
-- =====================================================

CREATE TABLE survey_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    survey_id UUID REFERENCES surveys(id) ON DELETE CASCADE NOT NULL,
    respondent_id TEXT, -- Anonymized identifier

    -- Demographic info (anonymized)
    age_group TEXT CHECK (age_group IN ('18-25', '26-35', '36-45', '46-55', '55+')),
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    education TEXT CHECK (education IN ('primary', 'secondary', 'graduate', 'postgraduate')),
    location TEXT,
    ward TEXT,

    -- Answers stored as JSONB
    answers JSONB NOT NULL, -- { "question_id": "answer" }

    submitted_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_survey_responses_survey ON survey_responses(survey_id);
CREATE INDEX idx_survey_responses_submitted ON survey_responses(submitted_at DESC);
CREATE INDEX idx_survey_responses_location ON survey_responses(location);
CREATE INDEX idx_survey_responses_answers ON survey_responses USING GIN(answers);

-- =====================================================
-- 11. VOLUNTEERS (FIELD WORKERS)
-- =====================================================

CREATE TABLE volunteers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) UNIQUE,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    role TEXT NOT NULL CHECK (role IN ('coordinator', 'surveyor', 'social_monitor', 'truth_team', 'data_collector')),

    -- Assigned area
    state TEXT DEFAULT 'Kerala',
    district TEXT,
    ward TEXT,

    -- Performance metrics
    reports_submitted INTEGER DEFAULT 0,
    surveys_completed INTEGER DEFAULT 0,
    accuracy_score DECIMAL(3, 2) CHECK (accuracy_score >= 0 AND accuracy_score <= 1),
    total_hours DECIMAL(10, 2) DEFAULT 0,
    last_active TIMESTAMPTZ,

    -- Skills and status
    skills TEXT[] DEFAULT ARRAY[]::TEXT[],
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),

    joined_date TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_volunteers_user_id ON volunteers(user_id);
CREATE INDEX idx_volunteers_ward ON volunteers(ward);
CREATE INDEX idx_volunteers_status ON volunteers(status);
CREATE INDEX idx_volunteers_role ON volunteers(role);

-- =====================================================
-- 12. RECOMMENDATIONS
-- =====================================================

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type TEXT NOT NULL CHECK (type IN ('event', 'messaging', 'resource_allocation', 'outreach', 'crisis_response', 'strategic')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

    -- Analysis
    confidence_score DECIMAL(3, 2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    rationale TEXT,
    suggested_actions TEXT[] DEFAULT ARRAY[]::TEXT[],
    estimated_impact TEXT CHECK (estimated_impact IN ('low', 'medium', 'high')),

    -- Implementation
    timeline TEXT,
    resources_required TEXT[] DEFAULT ARRAY[]::TEXT[],
    target_audience TEXT[] DEFAULT ARRAY[]::TEXT[],
    location TEXT,

    -- Status
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'approved', 'implemented', 'rejected')),
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    review_notes TEXT,

    generated_date TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_recommendations_type ON recommendations(type);
CREATE INDEX idx_recommendations_priority ON recommendations(priority);
CREATE INDEX idx_recommendations_status ON recommendations(status);
CREATE INDEX idx_recommendations_generated ON recommendations(generated_date DESC);

-- =====================================================
-- 13. VOTER DATABASE (Privacy-Compliant)
-- =====================================================

CREATE TABLE voters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Basic info (anonymized/hashed where needed)
    voter_id_hash TEXT UNIQUE, -- Hashed voter ID for privacy

    -- Demographics (aggregated for analysis)
    age_group TEXT CHECK (age_group IN ('18-25', '26-35', '36-45', '46-55', '55+')),
    gender TEXT CHECK (gender IN ('male', 'female', 'other')),
    education TEXT CHECK (education IN ('primary', 'secondary', 'graduate', 'postgraduate')),
    income TEXT CHECK (income IN ('low', 'middle', 'high')),
    occupation TEXT,

    -- Location
    ward TEXT NOT NULL,
    district TEXT,
    state TEXT DEFAULT 'Kerala',

    -- Segmentation (50 planned segments)
    segment TEXT,
    voter_type TEXT, -- First-time, Regular, Swing, etc.

    -- Engagement
    contacted BOOLEAN DEFAULT FALSE,
    last_contact_date TIMESTAMPTZ,
    contact_method TEXT,
    sentiment_score DECIMAL(3, 2),

    -- Consent & Privacy
    consent_given BOOLEAN DEFAULT FALSE,
    consent_date TIMESTAMPTZ,
    data_retention_period INTEGER DEFAULT 365, -- Days

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_voters_ward ON voters(ward);
CREATE INDEX idx_voters_segment ON voters(segment);
CREATE INDEX idx_voters_age_group ON voters(age_group);
CREATE INDEX idx_voters_sentiment ON voters(sentiment_score);
CREATE INDEX idx_voters_consent ON voters(consent_given);

-- =====================================================
-- 14. MEDIA COVERAGE
-- =====================================================

CREATE TABLE media_coverage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    media_type TEXT NOT NULL CHECK (media_type IN ('news', 'tv', 'radio', 'print', 'online')),
    source_name TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    url TEXT,
    author TEXT,

    -- Sentiment
    sentiment_score DECIMAL(3, 2),
    sentiment_polarity TEXT CHECK (sentiment_polarity IN ('positive', 'negative', 'neutral')),
    tone TEXT CHECK (tone IN ('supportive', 'critical', 'balanced', 'promotional')),

    -- Classification
    issues TEXT[] DEFAULT ARRAY[]::TEXT[],
    entities_mentioned TEXT[] DEFAULT ARRAY[]::TEXT[], -- Politicians, parties mentioned

    -- Reach
    estimated_reach BIGINT,
    viewership_rating DECIMAL(5, 2),

    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_media_coverage_type ON media_coverage(media_type);
CREATE INDEX idx_media_coverage_published ON media_coverage(published_at DESC);
CREATE INDEX idx_media_coverage_sentiment ON media_coverage(sentiment_polarity);
CREATE INDEX idx_media_coverage_issues ON media_coverage USING GIN(issues);

-- =====================================================
-- 15. COMPETITOR TRACKING
-- =====================================================

CREATE TABLE competitor_activity (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    competitor_name TEXT NOT NULL,
    competitor_party TEXT,

    -- Activity details
    activity_type TEXT CHECK (activity_type IN ('rally', 'press_conference', 'social_post', 'statement', 'campaign_event', 'media_appearance')),
    description TEXT,
    issue TEXT,

    -- Sentiment & Impact
    sentiment_score DECIMAL(3, 2),
    estimated_reach BIGINT,
    public_reaction TEXT CHECK (public_reaction IN ('positive', 'negative', 'mixed', 'neutral')),

    -- Location
    location TEXT,
    ward TEXT,
    district TEXT,

    -- Media
    media_urls TEXT[] DEFAULT ARRAY[]::TEXT[],

    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_competitor_activity_competitor ON competitor_activity(competitor_name);
CREATE INDEX idx_competitor_activity_timestamp ON competitor_activity(timestamp DESC);
CREATE INDEX idx_competitor_activity_type ON competitor_activity(activity_type);
CREATE INDEX idx_competitor_activity_ward ON competitor_activity(ward);

-- =====================================================
-- 16. CAMPAIGN EVENTS
-- =====================================================

CREATE TABLE campaign_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    event_type TEXT CHECK (event_type IN ('rally', 'townhall', 'door_to_door', 'public_meeting', 'press_conference', 'volunteer_training')),

    -- Schedule
    scheduled_at TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER,
    status TEXT DEFAULT 'planned' CHECK (status IN ('planned', 'ongoing', 'completed', 'cancelled')),

    -- Location
    location_name TEXT NOT NULL,
    location_address TEXT,
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    ward TEXT,
    district TEXT,

    -- Metrics
    expected_attendance INTEGER,
    actual_attendance INTEGER,
    volunteer_count INTEGER,

    -- Issues/Topics
    issues_addressed TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Organizer
    organized_by UUID REFERENCES users(id),

    -- Feedback
    overall_sentiment DECIMAL(3, 2),
    feedback_summary TEXT,
    media_coverage_count INTEGER DEFAULT 0,

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_campaign_events_scheduled ON campaign_events(scheduled_at);
CREATE INDEX idx_campaign_events_status ON campaign_events(status);
CREATE INDEX idx_campaign_events_ward ON campaign_events(ward);
CREATE INDEX idx_campaign_events_type ON campaign_events(event_type);

-- =====================================================
-- 17. CONVERSATIONS (BOT INTERACTIONS)
-- =====================================================

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_identifier TEXT, -- Anonymized user ID

    -- Conversation details
    channel TEXT CHECK (channel IN ('web_bot', 'whatsapp', 'telegram', 'sms', 'voice')),
    type TEXT CHECK (type IN ('feedback', 'complaint', 'inquiry', 'suggestion', 'grievance')),

    -- Content
    messages JSONB NOT NULL, -- Array of message objects
    sentiment_score DECIMAL(3, 2),
    sentiment_polarity TEXT CHECK (sentiment_polarity IN ('positive', 'negative', 'neutral')),

    -- Classification
    issue TEXT,
    priority TEXT CHECK (priority IN ('low', 'medium', 'high', 'urgent')),

    -- Status
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    assigned_to UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,

    -- Location
    location TEXT,
    ward TEXT,

    started_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_conversations_channel ON conversations(channel);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_type ON conversations(type);
CREATE INDEX idx_conversations_started ON conversations(started_at DESC);
CREATE INDEX idx_conversations_ward ON conversations(ward);

-- =====================================================
-- 18. SUBSCRIPTION & BILLING (already exists as demo_requests)
-- =====================================================

-- Note: demo_requests table already exists from previous migration
-- We'll keep it for demo requests and add a separate subscriptions table

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_name TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    contact_email TEXT NOT NULL,
    contact_phone TEXT NOT NULL,

    -- Subscription details
    plan_type TEXT DEFAULT 'standard' CHECK (plan_type IN ('basic', 'standard', 'premium', 'enterprise')),
    monthly_fee DECIMAL(10, 2) DEFAULT 6000.00,
    billing_cycle TEXT DEFAULT 'monthly' CHECK (billing_cycle IN ('monthly', 'quarterly', 'yearly')),

    -- Coverage area
    coverage_area TEXT NOT NULL, -- Election area covered
    ward_count INTEGER,
    state TEXT DEFAULT 'Kerala',

    -- Status
    status TEXT DEFAULT 'trial' CHECK (status IN ('trial', 'active', 'suspended', 'cancelled', 'expired')),

    -- Dates
    start_date TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    end_date TIMESTAMPTZ,
    trial_end_date TIMESTAMPTZ,
    last_payment_date TIMESTAMPTZ,
    next_billing_date TIMESTAMPTZ,

    -- Payment
    payment_method TEXT CHECK (payment_method IN ('razorpay', 'stripe', 'bank_transfer', 'other')),
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'overdue', 'failed')),

    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_email ON subscriptions(contact_email);
CREATE INDEX idx_subscriptions_billing_date ON subscriptions(next_billing_date);
CREATE INDEX idx_subscriptions_payment_status ON subscriptions(payment_status);

-- =====================================================
-- 19. AUDIT LOG
-- =====================================================

CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp DESC);

-- =====================================================
-- 20. SYSTEM SETTINGS
-- =====================================================

CREATE TABLE system_settings (
    key TEXT PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- =====================================================
-- TRIGGERS FOR AUTO-UPDATING updated_at
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_social_posts_updated_at BEFORE UPDATE ON social_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_influencers_updated_at BEFORE UPDATE ON influencers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_trending_topics_updated_at BEFORE UPDATE ON trending_topics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_field_reports_updated_at BEFORE UPDATE ON field_reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_surveys_updated_at BEFORE UPDATE ON surveys FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_volunteers_updated_at BEFORE UPDATE ON volunteers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_recommendations_updated_at BEFORE UPDATE ON recommendations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_voters_updated_at BEFORE UPDATE ON voters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_media_coverage_updated_at BEFORE UPDATE ON media_coverage FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_competitor_activity_updated_at BEFORE UPDATE ON competitor_activity FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_campaign_events_updated_at BEFORE UPDATE ON campaign_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sentiment_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE social_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE influencers ENABLE ROW LEVEL SECURITY;
ALTER TABLE trending_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE field_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE surveys ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE survey_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE volunteers ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE voters ENABLE ROW LEVEL SECURITY;
ALTER TABLE media_coverage ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Basic RLS Policies (can be customized based on requirements)

-- Users: Can read their own data, admins can read all
CREATE POLICY users_select_policy ON users FOR SELECT USING (
    auth.uid() = id OR
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
);

-- Sentiment Data: All authenticated users can read, specific roles can insert
CREATE POLICY sentiment_data_select_policy ON sentiment_data FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY sentiment_data_insert_policy ON sentiment_data FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Social Posts: All authenticated users can read
CREATE POLICY social_posts_select_policy ON social_posts FOR SELECT USING (auth.role() = 'authenticated');

-- Field Reports: Users can see their own reports, coordinators can see ward reports, admins see all
CREATE POLICY field_reports_select_policy ON field_reports FOR SELECT USING (
    volunteer_id = auth.uid() OR
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'analyst')) OR
    EXISTS (SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.ward = field_reports.ward AND u.role = 'ward-coordinator')
);

-- Alerts: All authenticated users can read
CREATE POLICY alerts_select_policy ON alerts FOR SELECT USING (auth.role() = 'authenticated');

-- Surveys: All authenticated users can read active surveys
CREATE POLICY surveys_select_policy ON surveys FOR SELECT USING (
    auth.role() = 'authenticated' AND status IN ('active', 'completed')
);

-- Survey Responses: Users can insert their own responses
CREATE POLICY survey_responses_insert_policy ON survey_responses FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Voters: Only admins and analysts can access voter data (DPDP compliance)
CREATE POLICY voters_select_policy ON voters FOR SELECT USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'analyst'))
);

-- Recommendations: All authenticated users can read
CREATE POLICY recommendations_select_policy ON recommendations FOR SELECT USING (auth.role() = 'authenticated');

-- Media Coverage: All authenticated users can read
CREATE POLICY media_coverage_select_policy ON media_coverage FOR SELECT USING (auth.role() = 'authenticated');

-- Competitor Activity: All authenticated users can read
CREATE POLICY competitor_activity_select_policy ON competitor_activity FOR SELECT USING (auth.role() = 'authenticated');

-- Campaign Events: All authenticated users can read
CREATE POLICY campaign_events_select_policy ON campaign_events FOR SELECT USING (auth.role() = 'authenticated');

-- Conversations: Users can access their assigned conversations, admins see all
CREATE POLICY conversations_select_policy ON conversations FOR SELECT USING (
    assigned_to = auth.uid() OR
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role IN ('admin', 'analyst'))
);

-- Subscriptions: Only admins can access
CREATE POLICY subscriptions_select_policy ON subscriptions FOR SELECT USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
);

-- Audit Log: Only admins can read
CREATE POLICY audit_log_select_policy ON audit_log FOR SELECT USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
);

-- System Settings: Only admins can access
CREATE POLICY system_settings_select_policy ON system_settings FOR SELECT USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')
);

-- =====================================================
-- FUNCTIONS FOR ANALYTICS
-- =====================================================

-- Function to calculate overall sentiment for a time period
CREATE OR REPLACE FUNCTION calculate_overall_sentiment(
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    ward_filter TEXT DEFAULT NULL
)
RETURNS DECIMAL AS $$
DECLARE
    avg_sentiment DECIMAL;
BEGIN
    SELECT AVG(sentiment)
    INTO avg_sentiment
    FROM sentiment_data
    WHERE timestamp BETWEEN start_time AND end_time
    AND (ward_filter IS NULL OR ward = ward_filter);

    RETURN COALESCE(avg_sentiment, 0);
END;
$$ LANGUAGE plpgsql;

-- Function to get trending issues
CREATE OR REPLACE FUNCTION get_trending_issues(
    time_period TEXT DEFAULT '24h',
    limit_count INTEGER DEFAULT 5
)
RETURNS TABLE(issue TEXT, mention_count BIGINT, avg_sentiment DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT
        sd.issue,
        COUNT(*)::BIGINT as mention_count,
        AVG(sd.sentiment)::DECIMAL as avg_sentiment
    FROM sentiment_data sd
    WHERE sd.timestamp > NOW() - (time_period || ' hours')::INTERVAL
    GROUP BY sd.issue
    ORDER BY mention_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to detect sentiment anomalies
CREATE OR REPLACE FUNCTION detect_sentiment_anomalies()
RETURNS TABLE(
    issue TEXT,
    current_sentiment DECIMAL,
    baseline_sentiment DECIMAL,
    deviation DECIMAL,
    is_spike BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH current_data AS (
        SELECT
            issue,
            AVG(sentiment) as current_avg
        FROM sentiment_data
        WHERE timestamp > NOW() - INTERVAL '6 hours'
        GROUP BY issue
    ),
    baseline_data AS (
        SELECT
            issue,
            AVG(sentiment) as baseline_avg,
            STDDEV(sentiment) as baseline_stddev
        FROM sentiment_data
        WHERE timestamp BETWEEN NOW() - INTERVAL '7 days' AND NOW() - INTERVAL '6 hours'
        GROUP BY issue
    )
    SELECT
        cd.issue,
        cd.current_avg::DECIMAL as current_sentiment,
        bd.baseline_avg::DECIMAL as baseline_sentiment,
        (cd.current_avg - bd.baseline_avg)::DECIMAL as deviation,
        (ABS(cd.current_avg - bd.baseline_avg) > 2 * bd.baseline_stddev)::BOOLEAN as is_spike
    FROM current_data cd
    JOIN baseline_data bd ON cd.issue = bd.issue
    WHERE ABS(cd.current_avg - bd.baseline_avg) > 2 * bd.baseline_stddev;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================

-- View for dashboard metrics
CREATE OR REPLACE VIEW dashboard_metrics AS
SELECT
    (SELECT AVG(sentiment) FROM sentiment_data WHERE timestamp > NOW() - INTERVAL '24 hours') as overall_sentiment,
    (SELECT COUNT(DISTINCT source_id) FROM sentiment_data WHERE timestamp > NOW() - INTERVAL '1 hour') as active_conversations,
    (SELECT COUNT(*) FROM alerts WHERE status = 'active' AND severity IN ('high', 'critical')) as critical_alerts,
    (SELECT COUNT(*) FROM social_posts WHERE timestamp > NOW() - INTERVAL '24 hours') as social_posts_24h,
    (SELECT COUNT(*) FROM field_reports WHERE timestamp > NOW() - INTERVAL '24 hours') as field_reports_24h,
    NOW() as last_updated;

-- View for top influencers
CREATE OR REPLACE VIEW top_influencers AS
SELECT
    id,
    name,
    handle,
    platforms,
    total_followers,
    engagement_rate,
    influence_score,
    sentiment_score,
    category,
    risk_level
FROM influencers
WHERE is_active = TRUE
ORDER BY influence_score DESC
LIMIT 50;

-- View for ward-wise sentiment summary
CREATE OR REPLACE VIEW ward_sentiment_summary AS
SELECT
    ward,
    district,
    COUNT(*) as data_points,
    AVG(sentiment) as avg_sentiment,
    COUNT(CASE WHEN polarity = 'positive' THEN 1 END) as positive_count,
    COUNT(CASE WHEN polarity = 'negative' THEN 1 END) as negative_count,
    COUNT(CASE WHEN polarity = 'neutral' THEN 1 END) as neutral_count,
    MAX(timestamp) as last_updated
FROM sentiment_data
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY ward, district
ORDER BY avg_sentiment DESC;

-- =====================================================
-- SEED DATA FOR TESTING (OPTIONAL)
-- =====================================================

-- Insert default system settings
INSERT INTO system_settings (key, value, description) VALUES
('alert_thresholds', '{"sentiment_spike": 0.3, "volume_surge": 2.0, "crisis_keywords": ["riot", "protest", "violence"]}', 'Threshold settings for alert generation'),
('social_media_refresh_interval', '30', 'Seconds between social media monitoring refreshes'),
('data_retention_days', '365', 'Number of days to retain sentiment data'),
('max_posts_per_query', '100', 'Maximum posts to fetch per social media query'),
('enable_real_time_alerts', 'true', 'Enable/disable real-time alert notifications');

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE sentiment_data IS 'Core sentiment analysis data from all sources';
COMMENT ON TABLE social_posts IS 'Social media posts with engagement metrics';
COMMENT ON TABLE influencers IS 'Key influencer profiles and metrics';
COMMENT ON TABLE alerts IS 'System-generated alerts and notifications';
COMMENT ON TABLE field_reports IS 'Ground-level reports from field workers';
COMMENT ON TABLE surveys IS 'Survey campaigns and configurations';
COMMENT ON TABLE voters IS 'Anonymized voter database (DPDP compliant)';
COMMENT ON TABLE recommendations IS 'AI-generated strategic recommendations';
COMMENT ON TABLE audit_log IS 'System audit trail for all actions';

-- =====================================================
-- END OF SCHEMA
-- =====================================================
