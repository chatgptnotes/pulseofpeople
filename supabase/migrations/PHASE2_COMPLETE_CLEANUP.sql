-- ============================================================================
-- PHASE 2 COMPLETE CLEANUP - Drop everything Phase 2 related first
-- ============================================================================
-- This thoroughly cleans up Phase 2 tables, indexes, triggers, and functions
-- Then recreates everything fresh
-- ============================================================================

-- Step 1: Drop all triggers first
DROP TRIGGER IF EXISTS trigger_sync_booth_location ON polling_booths CASCADE;
DROP TRIGGER IF EXISTS trigger_sync_ward_geom ON wards CASCADE;
DROP TRIGGER IF EXISTS trigger_sync_constituency_geom ON constituencies CASCADE;
DROP TRIGGER IF EXISTS trigger_update_booth_stats ON voters CASCADE;
DROP TRIGGER IF EXISTS trigger_update_constituency_stats ON polling_booths CASCADE;
DROP TRIGGER IF EXISTS update_voters_updated_at ON voters CASCADE;
DROP TRIGGER IF EXISTS update_polling_booths_updated_at ON polling_booths CASCADE;
DROP TRIGGER IF EXISTS update_wards_updated_at ON wards CASCADE;
DROP TRIGGER IF EXISTS update_constituencies_updated_at ON constituencies CASCADE;

-- Step 2: Drop all Phase 2 functions
DROP FUNCTION IF EXISTS get_constituency_stats(UUID) CASCADE;
DROP FUNCTION IF EXISTS find_booths_near(DECIMAL, DECIMAL, INTEGER) CASCADE;
DROP FUNCTION IF EXISTS sync_location_from_coordinates() CASCADE;
DROP FUNCTION IF EXISTS sync_geography_from_boundaries() CASCADE;
DROP FUNCTION IF EXISTS update_booth_voter_count() CASCADE;
DROP FUNCTION IF EXISTS update_constituency_voter_count() CASCADE;

-- Step 3: Drop all tables (CASCADE will drop indexes automatically)
DROP TABLE IF EXISTS voters CASCADE;
DROP TABLE IF EXISTS polling_booths CASCADE;
DROP TABLE IF EXISTS wards CASCADE;
DROP TABLE IF EXISTS constituencies CASCADE;

-- Enable PostGIS extension if needed
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- GEOGRAPHY: Constituencies
-- ============================================================================

CREATE TABLE constituencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    type VARCHAR(50) DEFAULT 'assembly' CHECK (type IN ('parliament', 'assembly', 'municipal', 'panchayat')),

    -- Geographic Info
    state VARCHAR(100),
    district VARCHAR(100),
    boundaries JSONB,
    geom GEOGRAPHY(MULTIPOLYGON, 4326),

    -- Demographics
    population INTEGER,
    voter_count INTEGER DEFAULT 0,
    total_booths INTEGER DEFAULT 0,
    area_sq_km DECIMAL(10, 2),

    -- Political Info
    reserved_category VARCHAR(50),
    last_election_year INTEGER,
    current_representative VARCHAR(255),
    current_party VARCHAR(100),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, code)
);

CREATE INDEX idx_constituencies_org ON constituencies(organization_id);
CREATE INDEX idx_constituencies_state ON constituencies(state);
CREATE INDEX idx_constituencies_type ON constituencies(type);
CREATE INDEX idx_constituencies_geom ON constituencies USING GIST(geom);

-- ============================================================================
-- GEOGRAPHY: Wards
-- ============================================================================

CREATE TABLE wards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    constituency_id UUID NOT NULL REFERENCES constituencies(id) ON DELETE CASCADE,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    ward_number INTEGER,

    -- Geographic Info
    boundaries JSONB,
    geom GEOGRAPHY(POLYGON, 4326),

    -- Demographics
    population INTEGER,
    voter_count INTEGER DEFAULT 0,
    total_booths INTEGER DEFAULT 0,
    demographics JSONB DEFAULT '{}'::jsonb,

    -- Socioeconomic Data
    income_level VARCHAR(50),
    urbanization VARCHAR(50),
    literacy_rate DECIMAL(5, 2),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(constituency_id, code)
);

CREATE INDEX idx_wards_constituency ON wards(constituency_id);
CREATE INDEX idx_wards_org ON wards(organization_id);
CREATE INDEX idx_wards_geom ON wards USING GIST(geom);

-- ============================================================================
-- GEOGRAPHY: Polling Booths
-- ============================================================================

CREATE TABLE polling_booths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    constituency_id UUID NOT NULL REFERENCES constituencies(id) ON DELETE CASCADE,
    ward_id UUID REFERENCES wards(id) ON DELETE SET NULL,

    -- Booth Identity
    booth_number VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,

    -- Location
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location GEOGRAPHY(POINT, 4326),
    landmark TEXT,

    -- Voter Stats
    total_voters INTEGER DEFAULT 0,
    male_voters INTEGER DEFAULT 0,
    female_voters INTEGER DEFAULT 0,
    transgender_voters INTEGER DEFAULT 0,

    -- Booth Details
    booth_type VARCHAR(50) DEFAULT 'regular',
    is_accessible BOOLEAN DEFAULT true,
    facilities JSONB DEFAULT '[]'::jsonb,

    -- Building Info
    building_name VARCHAR(255),
    building_type VARCHAR(100),
    floor_number INTEGER,
    room_number VARCHAR(50),

    -- Operational Info
    is_active BOOLEAN DEFAULT true,
    last_used_election DATE,
    booth_level_officer VARCHAR(255),
    contact_number VARCHAR(20),

    -- Sentiment & Strategy
    party_strength JSONB,
    swing_potential VARCHAR(50),
    priority_level INTEGER DEFAULT 3,

    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(organization_id, constituency_id, booth_number)
);

CREATE INDEX idx_booths_constituency ON polling_booths(constituency_id);
CREATE INDEX idx_booths_ward ON polling_booths(ward_id);
CREATE INDEX idx_booths_org ON polling_booths(organization_id);
CREATE INDEX idx_booths_location ON polling_booths USING GIST(location);
CREATE INDEX idx_booths_active ON polling_booths(is_active);
CREATE INDEX idx_booths_priority ON polling_booths(priority_level DESC);

-- ============================================================================
-- VOTERS: Voter Database
-- ============================================================================

CREATE TABLE voters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    polling_booth_id UUID REFERENCES polling_booths(id) ON DELETE SET NULL,

    -- Voter Identity
    voter_id_number VARCHAR(50) NOT NULL,
    epic_number VARCHAR(50),
    aadhaar_number_hash VARCHAR(64),

    -- Personal Info
    full_name VARCHAR(255) NOT NULL,
    gender VARCHAR(20) CHECK (gender IN ('Male', 'Female', 'Transgender', 'Other')),
    age INTEGER,
    date_of_birth DATE,

    -- Contact Info
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    whatsapp_number VARCHAR(20),

    -- Demographics
    religion VARCHAR(50),
    caste VARCHAR(50),
    caste_category VARCHAR(20),
    occupation VARCHAR(100),
    education VARCHAR(100),
    monthly_income_range VARCHAR(50),

    -- Family & Social Network
    family_head_id UUID REFERENCES voters(id),
    family_size INTEGER,
    influencer_score INTEGER DEFAULT 0,

    -- Voting History
    voting_history JSONB DEFAULT '[]'::jsonb,
    voter_turnout_rate DECIMAL(5, 2),
    first_time_voter BOOLEAN DEFAULT false,

    -- Political Sentiment
    sentiment VARCHAR(50) CHECK (sentiment IN ('strong_support', 'support', 'neutral', 'oppose', 'strong_oppose', 'undecided')),
    sentiment_score DECIMAL(5, 2),
    sentiment_last_updated TIMESTAMPTZ,
    preferred_party VARCHAR(100),
    previous_party_support VARCHAR(100),

    -- Issues & Concerns
    top_issues TEXT[],
    complaints_filed JSONB,
    benefits_received JSONB,

    -- Engagement
    contacted_by_party BOOLEAN DEFAULT false,
    last_contact_date DATE,
    contact_method VARCHAR(50),
    meeting_attendance INTEGER DEFAULT 0,
    rally_participation INTEGER DEFAULT 0,

    -- Tags & Categories
    tags TEXT[],
    voter_category VARCHAR(50),

    -- Data Quality
    data_quality_score INTEGER DEFAULT 50,
    verified BOOLEAN DEFAULT false,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,

    -- Privacy & Consent
    consent_given BOOLEAN DEFAULT false,
    consent_date DATE,
    data_retention_until DATE,

    -- Metadata
    notes TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by UUID REFERENCES users(id),

    UNIQUE(organization_id, voter_id_number)
);

CREATE INDEX idx_voters_org ON voters(organization_id);
CREATE INDEX idx_voters_booth ON voters(polling_booth_id);
CREATE INDEX idx_voters_sentiment ON voters(sentiment);
CREATE INDEX idx_voters_category ON voters(voter_category);
CREATE INDEX idx_voters_family ON voters(family_head_id);
CREATE INDEX idx_voters_name ON voters(full_name);
CREATE INDEX idx_voters_epic ON voters(epic_number);
CREATE INDEX idx_voters_phone ON voters(phone);
CREATE INDEX idx_voters_tags ON voters USING GIN(tags);
CREATE INDEX idx_voters_issues ON voters USING GIN(top_issues);

-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE constituencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE wards ENABLE ROW LEVEL SECURITY;
ALTER TABLE polling_booths ENABLE ROW LEVEL SECURITY;
ALTER TABLE voters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their org constituencies"
    ON constituencies FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Admins can manage constituencies"
    ON constituencies FOR ALL
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'superadmin')));

CREATE POLICY "Users can view their org wards"
    ON wards FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Admins can manage wards"
    ON wards FOR ALL
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')));

CREATE POLICY "Users can view their org booths"
    ON polling_booths FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid()));

CREATE POLICY "Managers can manage booths"
    ON polling_booths FOR ALL
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')));

CREATE POLICY "Analysts can view their org voters"
    ON voters FOR SELECT
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager', 'analyst', 'superadmin')));

CREATE POLICY "Managers can manage voters"
    ON voters FOR INSERT
    WITH CHECK (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')));

CREATE POLICY "Managers can update voters"
    ON voters FOR UPDATE
    USING (organization_id IN (SELECT organization_id FROM users WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')));

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

CREATE TRIGGER update_constituencies_updated_at BEFORE UPDATE ON constituencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wards_updated_at BEFORE UPDATE ON wards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_polling_booths_updated_at BEFORE UPDATE ON polling_booths
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voters_updated_at BEFORE UPDATE ON voters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE OR REPLACE FUNCTION update_constituency_voter_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE constituencies
    SET voter_count = (SELECT COALESCE(SUM(total_voters), 0) FROM polling_booths WHERE constituency_id = NEW.constituency_id),
        total_booths = (SELECT COUNT(*) FROM polling_booths WHERE constituency_id = NEW.constituency_id AND is_active = true)
    WHERE id = NEW.constituency_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_constituency_stats
    AFTER INSERT OR UPDATE ON polling_booths
    FOR EACH ROW EXECUTE FUNCTION update_constituency_voter_count();

CREATE OR REPLACE FUNCTION update_booth_voter_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.polling_booth_id IS NOT NULL THEN
        UPDATE polling_booths
        SET total_voters = (SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id),
            male_voters = (SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id AND gender = 'Male'),
            female_voters = (SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id AND gender = 'Female'),
            transgender_voters = (SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id AND gender IN ('Transgender', 'Other'))
        WHERE id = NEW.polling_booth_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_booth_stats
    AFTER INSERT OR UPDATE ON voters
    FOR EACH ROW EXECUTE FUNCTION update_booth_voter_count();

CREATE OR REPLACE FUNCTION sync_geography_from_boundaries()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.boundaries IS NOT NULL THEN
        NEW.geom = ST_GeogFromGeoJSON(NEW.boundaries::text);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_constituency_geom
    BEFORE INSERT OR UPDATE ON constituencies
    FOR EACH ROW EXECUTE FUNCTION sync_geography_from_boundaries();

CREATE TRIGGER trigger_sync_ward_geom
    BEFORE INSERT OR UPDATE ON wards
    FOR EACH ROW EXECUTE FUNCTION sync_geography_from_boundaries();

CREATE OR REPLACE FUNCTION sync_location_from_coordinates()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_booth_location
    BEFORE INSERT OR UPDATE ON polling_booths
    FOR EACH ROW EXECUTE FUNCTION sync_location_from_coordinates();

CREATE OR REPLACE FUNCTION find_booths_near(
    p_latitude DECIMAL,
    p_longitude DECIMAL,
    p_radius_meters INTEGER DEFAULT 5000
)
RETURNS TABLE(
    booth_id UUID,
    booth_name VARCHAR,
    distance_meters DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT pb.id, pb.name,
        ST_Distance(pb.location, ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326)::geography)::DECIMAL AS distance
    FROM polling_booths pb
    WHERE ST_DWithin(pb.location, ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326)::geography, p_radius_meters)
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_constituency_stats(p_constituency_id UUID)
RETURNS TABLE(
    total_voters BIGINT,
    male_voters BIGINT,
    female_voters BIGINT,
    support_count BIGINT,
    oppose_count BIGINT,
    undecided_count BIGINT,
    avg_sentiment DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT COUNT(*)::BIGINT,
        COUNT(*) FILTER (WHERE gender = 'Male')::BIGINT,
        COUNT(*) FILTER (WHERE gender = 'Female')::BIGINT,
        COUNT(*) FILTER (WHERE sentiment IN ('strong_support', 'support'))::BIGINT,
        COUNT(*) FILTER (WHERE sentiment IN ('oppose', 'strong_oppose'))::BIGINT,
        COUNT(*) FILTER (WHERE sentiment IN ('undecided', 'neutral'))::BIGINT,
        AVG(sentiment_score)::DECIMAL
    FROM voters v
    JOIN polling_booths pb ON v.polling_booth_id = pb.id
    WHERE pb.constituency_id = p_constituency_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE DATA
-- ============================================================================

INSERT INTO constituencies (organization_id, name, code, type, state, district, population, voter_count) VALUES
('11111111-1111-1111-1111-111111111111', 'Chennai North', 'TN-01', 'parliament', 'Tamil Nadu', 'Chennai', 2100000, 1450000),
('11111111-1111-1111-1111-111111111111', 'Chennai Central', 'TN-02', 'parliament', 'Tamil Nadu', 'Chennai', 1950000, 1320000),
('11111111-1111-1111-1111-111111111111', 'Chennai South', 'TN-03', 'parliament', 'Tamil Nadu', 'Chennai', 2050000, 1410000),
('11111111-1111-1111-1111-111111111111', 'Coimbatore', 'TN-20', 'parliament', 'Tamil Nadu', 'Coimbatore', 1850000, 1280000),
('11111111-1111-1111-1111-111111111111', 'Madurai', 'TN-30', 'parliament', 'Tamil Nadu', 'Madurai', 1720000, 1190000);

INSERT INTO wards (organization_id, constituency_id, name, code, ward_number, population, voter_count) VALUES
('11111111-1111-1111-1111-111111111111', (SELECT id FROM constituencies WHERE code = 'TN-01' LIMIT 1), 'Anna Nagar', 'TN-01-W01', 1, 85000, 62000),
('11111111-1111-1111-1111-111111111111', (SELECT id FROM constituencies WHERE code = 'TN-01' LIMIT 1), 'Kilpauk', 'TN-01-W02', 2, 78000, 56000),
('11111111-1111-1111-1111-111111111111', (SELECT id FROM constituencies WHERE code = 'TN-02' LIMIT 1), 'Egmore', 'TN-02-W01', 1, 72000, 51000);

DO $$
DECLARE
    constituency_id UUID;
    booth_num INTEGER;
    lat DECIMAL;
    lon DECIMAL;
BEGIN
    SELECT id INTO constituency_id FROM constituencies WHERE code = 'TN-01' LIMIT 1;
    FOR booth_num IN 1..10 LOOP
        lat := 13.0827 + (random() * 0.1 - 0.05);
        lon := 80.2707 + (random() * 0.1 - 0.05);
        INSERT INTO polling_booths (organization_id, constituency_id, booth_number, name, address, latitude, longitude, total_voters, male_voters, female_voters, building_type, is_accessible)
        VALUES ('11111111-1111-1111-1111-111111111111', constituency_id, 'B' || LPAD(booth_num::TEXT, 4, '0'), 'Polling Booth ' || booth_num,
            (ARRAY['School Complex', 'Community Hall', 'Municipal Office'])[floor(random() * 3 + 1)], lat, lon,
            floor(random() * 500 + 800)::INTEGER, floor(random() * 250 + 400)::INTEGER, floor(random() * 250 + 400)::INTEGER,
            (ARRAY['school', 'community_hall', 'government_office'])[floor(random() * 3 + 1)], random() > 0.2);
    END LOOP;
END $$;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

SELECT '✅ Phase 2 Complete!' as status;

SELECT table_name, (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns
FROM information_schema.tables t
WHERE table_schema = 'public' AND table_name IN ('constituencies', 'wards', 'polling_booths', 'voters')
ORDER BY table_name;
