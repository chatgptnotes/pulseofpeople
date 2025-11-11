-- ============================================================================
-- PULSE OF PEOPLE - PHASE 2: GEOGRAPHY & TERRITORY MIGRATION
-- ============================================================================
-- Created: 2025-11-09
-- Purpose: Tables for constituencies, wards, polling booths, and voters
-- Dependencies: Phase 1 (organizations, users)
-- ============================================================================

-- PostGIS should already be enabled from Phase 1, but ensure it's there
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
    boundaries JSONB, -- GeoJSON polygon/multipolygon
    geom GEOGRAPHY(MULTIPOLYGON, 4326), -- PostGIS geography for spatial queries

    -- Demographics
    population INTEGER,
    voter_count INTEGER DEFAULT 0,
    total_booths INTEGER DEFAULT 0,
    area_sq_km DECIMAL(10, 2),

    -- Political Info
    reserved_category VARCHAR(50), -- 'general', 'sc', 'st', 'obc', 'women'
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

COMMENT ON TABLE constituencies IS 'Electoral constituencies (Parliament/Assembly/Municipal)';

-- ============================================================================
-- GEOGRAPHY: Wards (Sub-divisions of constituencies)
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
    boundaries JSONB, -- GeoJSON polygon
    geom GEOGRAPHY(POLYGON, 4326),

    -- Demographics
    population INTEGER,
    voter_count INTEGER DEFAULT 0,
    total_booths INTEGER DEFAULT 0,
    demographics JSONB DEFAULT '{}'::jsonb, -- {age_groups, religions, castes, occupations}

    -- Socioeconomic Data
    income_level VARCHAR(50), -- 'low', 'middle', 'high'
    urbanization VARCHAR(50), -- 'urban', 'semi_urban', 'rural'
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

COMMENT ON TABLE wards IS 'Wards or divisions within constituencies';

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
    location GEOGRAPHY(POINT, 4326), -- PostGIS point for spatial queries
    landmark TEXT,

    -- Voter Stats
    total_voters INTEGER DEFAULT 0,
    male_voters INTEGER DEFAULT 0,
    female_voters INTEGER DEFAULT 0,
    transgender_voters INTEGER DEFAULT 0,

    -- Booth Details
    booth_type VARCHAR(50) DEFAULT 'regular', -- 'regular', 'auxiliary', 'special'
    is_accessible BOOLEAN DEFAULT true,
    facilities JSONB DEFAULT '[]'::jsonb, -- ['ramp', 'parking', 'water', 'electricity', 'toilet']

    -- Building Info
    building_name VARCHAR(255),
    building_type VARCHAR(100), -- 'school', 'community_hall', 'government_office'
    floor_number INTEGER,
    room_number VARCHAR(50),

    -- Operational Info
    is_active BOOLEAN DEFAULT true,
    last_used_election DATE,
    booth_level_officer VARCHAR(255),
    contact_number VARCHAR(20),

    -- Sentiment & Strategy
    party_strength JSONB, -- {party_a: 45, party_b: 35, party_c: 20}
    swing_potential VARCHAR(50), -- 'high', 'medium', 'low'
    priority_level INTEGER DEFAULT 3, -- 1-5 (5 = highest priority)

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

COMMENT ON TABLE polling_booths IS 'Polling booth locations with voter counts and logistics';

-- ============================================================================
-- VOTERS: Voter Database
-- ============================================================================

CREATE TABLE voters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    polling_booth_id UUID REFERENCES polling_booths(id) ON DELETE SET NULL,

    -- Voter Identity
    voter_id_number VARCHAR(50) NOT NULL,
    epic_number VARCHAR(50), -- Electoral Photo Identity Card
    aadhaar_number_hash VARCHAR(64), -- Hashed for privacy (DPDP compliance)

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
    caste_category VARCHAR(20), -- 'general', 'obc', 'sc', 'st'
    occupation VARCHAR(100),
    education VARCHAR(100),
    monthly_income_range VARCHAR(50),

    -- Family & Social Network
    family_head_id UUID REFERENCES voters(id),
    family_size INTEGER,
    influencer_score INTEGER DEFAULT 0, -- 0-100 based on social network

    -- Voting History
    voting_history JSONB DEFAULT '[]'::jsonb, -- [{year: 2024, voted: true, party: 'xyz'}]
    voter_turnout_rate DECIMAL(5, 2), -- Percentage
    first_time_voter BOOLEAN DEFAULT false,

    -- Political Sentiment
    sentiment VARCHAR(50) CHECK (sentiment IN ('strong_support', 'support', 'neutral', 'oppose', 'strong_oppose', 'undecided')),
    sentiment_score DECIMAL(5, 2), -- -100 to +100
    sentiment_last_updated TIMESTAMPTZ,
    preferred_party VARCHAR(100),
    previous_party_support VARCHAR(100),

    -- Issues & Concerns
    top_issues TEXT[], -- ['unemployment', 'water_supply', 'education']
    complaints_filed JSONB, -- [{issue: 'water', date: '2024-01-15', resolved: false}]
    benefits_received JSONB, -- [{scheme: 'ration_card', date: '2023-06-01'}]

    -- Engagement
    contacted_by_party BOOLEAN DEFAULT false,
    last_contact_date DATE,
    contact_method VARCHAR(50), -- 'door_to_door', 'phone', 'whatsapp', 'event'
    meeting_attendance INTEGER DEFAULT 0,
    rally_participation INTEGER DEFAULT 0,

    -- Tags & Categories
    tags TEXT[], -- ['senior_citizen', 'first_time_voter', 'influencer', 'undecided']
    voter_category VARCHAR(50), -- 'core_supporter', 'swing_voter', 'opponent'

    -- Data Quality
    data_quality_score INTEGER DEFAULT 50, -- 0-100
    verified BOOLEAN DEFAULT false,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,

    -- Privacy & Consent (DPDP Compliance)
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

COMMENT ON TABLE voters IS 'Comprehensive voter database with demographics and sentiment';

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS
ALTER TABLE constituencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE wards ENABLE ROW LEVEL SECURITY;
ALTER TABLE polling_booths ENABLE ROW LEVEL SECURITY;
ALTER TABLE voters ENABLE ROW LEVEL SECURITY;

-- Constituencies: Users can view their organization's constituencies
CREATE POLICY "Users can view their org constituencies"
    ON constituencies FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Admins can manage constituencies"
    ON constituencies FOR ALL
    USING (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'superadmin')
    ));

-- Wards: Same as constituencies
CREATE POLICY "Users can view their org wards"
    ON wards FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Admins can manage wards"
    ON wards FOR ALL
    USING (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
    ));

-- Polling Booths: Users can view, managers+ can edit
CREATE POLICY "Users can view their org booths"
    ON polling_booths FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));

CREATE POLICY "Managers can manage booths"
    ON polling_booths FOR ALL
    USING (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
    ));

-- Voters: Analysts+ can view, managers+ can edit
CREATE POLICY "Analysts can view their org voters"
    ON voters FOR SELECT
    USING (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'analyst', 'superadmin')
    ));

CREATE POLICY "Managers can manage voters"
    ON voters FOR INSERT
    WITH CHECK (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
    ));

CREATE POLICY "Managers can update voters"
    ON voters FOR UPDATE
    USING (organization_id IN (
        SELECT organization_id FROM users
        WHERE id = auth.uid() AND role IN ('admin', 'manager', 'superadmin')
    ));

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Trigger: Auto-update updated_at
CREATE TRIGGER update_constituencies_updated_at BEFORE UPDATE ON constituencies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wards_updated_at BEFORE UPDATE ON wards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_polling_booths_updated_at BEFORE UPDATE ON polling_booths
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_voters_updated_at BEFORE UPDATE ON voters
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function: Update constituency voter count when booth is updated
CREATE OR REPLACE FUNCTION update_constituency_voter_count()
RETURNS TRIGGER AS $$
BEGIN
    -- Update constituency total voters
    UPDATE constituencies
    SET voter_count = (
        SELECT COALESCE(SUM(total_voters), 0)
        FROM polling_booths
        WHERE constituency_id = NEW.constituency_id
    ),
    total_booths = (
        SELECT COUNT(*)
        FROM polling_booths
        WHERE constituency_id = NEW.constituency_id AND is_active = true
    )
    WHERE id = NEW.constituency_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_constituency_stats
    AFTER INSERT OR UPDATE ON polling_booths
    FOR EACH ROW
    EXECUTE FUNCTION update_constituency_voter_count();

-- Function: Update booth voter count when voter is added/updated
CREATE OR REPLACE FUNCTION update_booth_voter_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.polling_booth_id IS NOT NULL THEN
        UPDATE polling_booths
        SET
            total_voters = (
                SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id
            ),
            male_voters = (
                SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id AND gender = 'Male'
            ),
            female_voters = (
                SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id AND gender = 'Female'
            ),
            transgender_voters = (
                SELECT COUNT(*) FROM voters WHERE polling_booth_id = NEW.polling_booth_id AND gender IN ('Transgender', 'Other')
            )
        WHERE id = NEW.polling_booth_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_booth_stats
    AFTER INSERT OR UPDATE ON voters
    FOR EACH ROW
    EXECUTE FUNCTION update_booth_voter_count();

-- Function: Sync PostGIS geography from JSONB boundaries
CREATE OR REPLACE FUNCTION sync_geography_from_boundaries()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.boundaries IS NOT NULL THEN
        -- Convert GeoJSON to PostGIS geography
        NEW.geom = ST_GeogFromGeoJSON(NEW.boundaries::text);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_sync_constituency_geom
    BEFORE INSERT OR UPDATE ON constituencies
    FOR EACH ROW
    EXECUTE FUNCTION sync_geography_from_boundaries();

CREATE TRIGGER trigger_sync_ward_geom
    BEFORE INSERT OR UPDATE ON wards
    FOR EACH ROW
    EXECUTE FUNCTION sync_geography_from_boundaries();

-- Function: Sync PostGIS point from lat/long
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
    FOR EACH ROW
    EXECUTE FUNCTION sync_location_from_coordinates();

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function: Find booths within radius of a point
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
    SELECT
        pb.id,
        pb.name,
        ST_Distance(
            pb.location,
            ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326)::geography
        )::DECIMAL AS distance
    FROM polling_booths pb
    WHERE ST_DWithin(
        pb.location,
        ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326)::geography,
        p_radius_meters
    )
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

-- Function: Get voter statistics for a constituency
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
    SELECT
        COUNT(*)::BIGINT,
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

-- Insert sample constituencies (Tamil Nadu)
INSERT INTO constituencies (organization_id, name, code, type, state, district, population, voter_count) VALUES
('11111111-1111-1111-1111-111111111111', 'Chennai North', 'TN-01', 'parliament', 'Tamil Nadu', 'Chennai', 2100000, 1450000),
('11111111-1111-1111-1111-111111111111', 'Chennai Central', 'TN-02', 'parliament', 'Tamil Nadu', 'Chennai', 1950000, 1320000),
('11111111-1111-1111-1111-111111111111', 'Chennai South', 'TN-03', 'parliament', 'Tamil Nadu', 'Chennai', 2050000, 1410000),
('11111111-1111-1111-1111-111111111111', 'Coimbatore', 'TN-20', 'parliament', 'Tamil Nadu', 'Coimbatore', 1850000, 1280000),
('11111111-1111-1111-1111-111111111111', 'Madurai', 'TN-30', 'parliament', 'Tamil Nadu', 'Madurai', 1720000, 1190000);

-- Insert sample wards
INSERT INTO wards (organization_id, constituency_id, name, code, ward_number, population, voter_count) VALUES
('11111111-1111-1111-1111-111111111111',
 (SELECT id FROM constituencies WHERE code = 'TN-01' LIMIT 1),
 'Anna Nagar', 'TN-01-W01', 1, 85000, 62000),
('11111111-1111-1111-1111-111111111111',
 (SELECT id FROM constituencies WHERE code = 'TN-01' LIMIT 1),
 'Kilpauk', 'TN-01-W02', 2, 78000, 56000),
('11111111-1111-1111-1111-111111111111',
 (SELECT id FROM constituencies WHERE code = 'TN-02' LIMIT 1),
 'Egmore', 'TN-02-W01', 1, 72000, 51000);

-- Insert sample polling booths (10 booths)
DO $$
DECLARE
    constituency_id UUID;
    booth_num INTEGER;
    lat DECIMAL;
    lon DECIMAL;
BEGIN
    -- Get Chennai North constituency ID
    SELECT id INTO constituency_id FROM constituencies WHERE code = 'TN-01' LIMIT 1;

    -- Insert 10 sample booths
    FOR booth_num IN 1..10 LOOP
        -- Chennai coordinates: 13.0827°N, 80.2707°E (adding small random offset)
        lat := 13.0827 + (random() * 0.1 - 0.05);
        lon := 80.2707 + (random() * 0.1 - 0.05);

        INSERT INTO polling_booths (
            organization_id,
            constituency_id,
            booth_number,
            name,
            address,
            latitude,
            longitude,
            total_voters,
            male_voters,
            female_voters,
            building_type,
            is_accessible
        ) VALUES (
            '11111111-1111-1111-1111-111111111111',
            constituency_id,
            'B' || LPAD(booth_num::TEXT, 4, '0'),
            'Polling Booth ' || booth_num,
            (ARRAY['School Complex', 'Community Hall', 'Municipal Office'])[floor(random() * 3 + 1)],
            lat,
            lon,
            floor(random() * 500 + 800)::INTEGER,
            floor(random() * 250 + 400)::INTEGER,
            floor(random() * 250 + 400)::INTEGER,
            (ARRAY['school', 'community_hall', 'government_office'])[floor(random() * 3 + 1)],
            random() > 0.2
        );
    END LOOP;
END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('constituencies', 'wards', 'polling_booths', 'voters')
ORDER BY table_name;

-- Verify sample data
SELECT
    c.name AS constituency,
    COUNT(DISTINCT w.id) AS ward_count,
    COUNT(pb.id) AS booth_count
FROM constituencies c
LEFT JOIN wards w ON c.id = w.constituency_id
LEFT JOIN polling_booths pb ON c.id = pb.constituency_id
GROUP BY c.id, c.name
ORDER BY c.name;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

/*
-- To rollback this migration:

DROP TRIGGER IF EXISTS trigger_sync_booth_location ON polling_booths;
DROP TRIGGER IF EXISTS trigger_sync_ward_geom ON wards;
DROP TRIGGER IF EXISTS trigger_sync_constituency_geom ON constituencies;
DROP TRIGGER IF EXISTS trigger_update_booth_stats ON voters;
DROP TRIGGER IF EXISTS trigger_update_constituency_stats ON polling_booths;
DROP TRIGGER IF EXISTS update_voters_updated_at ON voters;
DROP TRIGGER IF EXISTS update_polling_booths_updated_at ON polling_booths;
DROP TRIGGER IF EXISTS update_wards_updated_at ON wards;
DROP TRIGGER IF EXISTS update_constituencies_updated_at ON constituencies;

DROP FUNCTION IF EXISTS get_constituency_stats(UUID);
DROP FUNCTION IF EXISTS find_booths_near(DECIMAL, DECIMAL, INTEGER);
DROP FUNCTION IF EXISTS sync_location_from_coordinates();
DROP FUNCTION IF EXISTS sync_geography_from_boundaries();
DROP FUNCTION IF EXISTS update_booth_voter_count();
DROP FUNCTION IF EXISTS update_constituency_voter_count();

DROP TABLE IF EXISTS voters CASCADE;
DROP TABLE IF EXISTS polling_booths CASCADE;
DROP TABLE IF EXISTS wards CASCADE;
DROP TABLE IF EXISTS constituencies CASCADE;
*/
