-- =====================================================
-- CONSTITUENCY MASTER DATA TABLES
-- Tamil Nadu & Pondicherry Assembly Constituencies
-- Date: 2025-11-06
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =====================================================
-- 1. ASSEMBLY CONSTITUENCIES MASTER TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS assembly_constituencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Basic Information
    code TEXT UNIQUE NOT NULL, -- e.g., TN001, TN002, PY01
    constituency_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    name_tamil TEXT, -- Tamil language name

    -- Location
    state_code TEXT NOT NULL, -- TN for Tamil Nadu, PY for Pondicherry
    district_code TEXT NOT NULL,
    center_lat DECIMAL(10, 8),
    center_lng DECIMAL(11, 8),
    center_point GEOGRAPHY(POINT, 4326), -- PostGIS point for spatial queries

    -- Reservation Information
    reservation_type TEXT NOT NULL CHECK (reservation_type IN (
        'Unreserved',
        'Scheduled Castes',
        'Scheduled Tribes',
        'Women',
        'Muslims',
        'Christians',
        'Landholders',
        'Commerce and Industry',
        'Labour and Trade Unions',
        'Europeans',
        'Anglo-Indians',
        'University'
    )),
    last_reserved INTEGER, -- Year when current reservation was applied

    -- Electoral Details
    parliamentary_constituency TEXT,
    total_voters INTEGER DEFAULT 0,
    polling_booths INTEGER DEFAULT 0,
    area_km2 DECIMAL(10, 2),

    -- Metadata
    formation_year INTEGER,
    remarks TEXT,

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT unique_constituency_per_state UNIQUE (state_code, constituency_number),
    CONSTRAINT valid_state_code CHECK (state_code IN ('TN', 'PY'))
);

-- Create indexes
CREATE INDEX idx_constituencies_code ON assembly_constituencies(code);
CREATE INDEX idx_constituencies_district ON assembly_constituencies(district_code);
CREATE INDEX idx_constituencies_state ON assembly_constituencies(state_code);
CREATE INDEX idx_constituencies_reservation ON assembly_constituencies(reservation_type);
CREATE INDEX idx_constituencies_parliamentary ON assembly_constituencies(parliamentary_constituency);
CREATE INDEX idx_constituencies_tenant ON assembly_constituencies(tenant_id);
CREATE INDEX idx_constituencies_center_point ON assembly_constituencies USING GIST(center_point);

-- =====================================================
-- 2. ELECTED MEMBERS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS elected_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Constituency Reference
    constituency_code TEXT NOT NULL REFERENCES assembly_constituencies(code) ON DELETE CASCADE,

    -- Member Information
    member_name TEXT NOT NULL,
    political_party TEXT NOT NULL,
    alliance TEXT, -- e.g., DMK Alliance, AIADMK Alliance, NDA, UPA

    -- Election Details
    election_year INTEGER NOT NULL,
    term_start DATE NOT NULL,
    term_end DATE,

    -- Vote Details
    votes_received INTEGER,
    vote_percentage DECIMAL(5, 2),
    victory_margin INTEGER,
    total_valid_votes INTEGER,

    -- Status
    is_current_member BOOLEAN DEFAULT FALSE,

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT unique_member_per_term UNIQUE (constituency_code, election_year)
);

-- Create indexes
CREATE INDEX idx_elected_members_constituency ON elected_members(constituency_code);
CREATE INDEX idx_elected_members_party ON elected_members(political_party);
CREATE INDEX idx_elected_members_election_year ON elected_members(election_year DESC);
CREATE INDEX idx_elected_members_current ON elected_members(is_current_member);
CREATE INDEX idx_elected_members_tenant ON elected_members(tenant_id);

-- =====================================================
-- 3. POLLING BOOTHS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS polling_booths (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Basic Information
    booth_number TEXT NOT NULL,
    booth_name TEXT NOT NULL,

    -- Constituency Reference
    constituency_code TEXT NOT NULL REFERENCES assembly_constituencies(code) ON DELETE CASCADE,

    -- Location
    location_lat DECIMAL(10, 8) NOT NULL,
    location_lng DECIMAL(11, 8) NOT NULL,
    location_point GEOGRAPHY(POINT, 4326),
    address TEXT NOT NULL,

    -- Electoral Details
    total_voters INTEGER DEFAULT 0,
    male_voters INTEGER DEFAULT 0,
    female_voters INTEGER DEFAULT 0,
    other_voters INTEGER DEFAULT 0,

    -- Accessibility
    is_accessible BOOLEAN DEFAULT TRUE,
    facilities TEXT[], -- ['Ramp', 'Wheelchair', 'Separate Queue for Elderly']

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT unique_booth_per_constituency UNIQUE (constituency_code, booth_number)
);

-- Create indexes
CREATE INDEX idx_polling_booths_constituency ON polling_booths(constituency_code);
CREATE INDEX idx_polling_booths_location ON polling_booths USING GIST(location_point);
CREATE INDEX idx_polling_booths_tenant ON polling_booths(tenant_id);

-- =====================================================
-- 4. RESERVATION STATISTICS VIEW
-- =====================================================

CREATE OR REPLACE VIEW constituency_reservation_stats AS
SELECT
    state_code,
    reservation_type,
    COUNT(*) as constituency_count,
    SUM(total_voters) as total_voters,
    ROUND(AVG(total_voters)) as avg_voters_per_constituency,
    ROUND(AVG(polling_booths)) as avg_booths_per_constituency
FROM assembly_constituencies
GROUP BY state_code, reservation_type
ORDER BY state_code, constituency_count DESC;

-- =====================================================
-- 5. DISTRICT-WISE CONSTITUENCY VIEW
-- =====================================================

CREATE OR REPLACE VIEW district_constituency_summary AS
SELECT
    district_code,
    state_code,
    COUNT(*) as total_constituencies,
    COUNT(CASE WHEN reservation_type = 'Scheduled Castes' THEN 1 END) as sc_reserved,
    COUNT(CASE WHEN reservation_type = 'Scheduled Tribes' THEN 1 END) as st_reserved,
    COUNT(CASE WHEN reservation_type = 'Unreserved' THEN 1 END) as unreserved,
    SUM(total_voters) as total_voters,
    SUM(polling_booths) as total_booths
FROM assembly_constituencies
GROUP BY district_code, state_code
ORDER BY state_code, district_code;

-- =====================================================
-- 6. CURRENT MEMBERS VIEW
-- =====================================================

CREATE OR REPLACE VIEW current_members_view AS
SELECT
    ac.code as constituency_code,
    ac.constituency_number,
    ac.name as constituency_name,
    ac.district_code,
    ac.state_code,
    ac.reservation_type,
    em.member_name,
    em.political_party,
    em.alliance,
    em.election_year,
    em.term_start,
    em.term_end,
    em.votes_received,
    em.vote_percentage,
    em.victory_margin
FROM assembly_constituencies ac
LEFT JOIN elected_members em ON ac.code = em.constituency_code AND em.is_current_member = TRUE
ORDER BY ac.state_code, ac.constituency_number;

-- =====================================================
-- 7. TRIGGERS FOR AUTO-UPDATING
-- =====================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_constituency_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_assembly_constituencies_timestamp
    BEFORE UPDATE ON assembly_constituencies
    FOR EACH ROW
    EXECUTE FUNCTION update_constituency_updated_at();

CREATE TRIGGER update_elected_members_timestamp
    BEFORE UPDATE ON elected_members
    FOR EACH ROW
    EXECUTE FUNCTION update_constituency_updated_at();

CREATE TRIGGER update_polling_booths_timestamp
    BEFORE UPDATE ON polling_booths
    FOR EACH ROW
    EXECUTE FUNCTION update_constituency_updated_at();

-- Update center_point when lat/lng changes
CREATE OR REPLACE FUNCTION update_center_point()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.center_lat IS NOT NULL AND NEW.center_lng IS NOT NULL THEN
        NEW.center_point = ST_SetSRID(ST_MakePoint(NEW.center_lng, NEW.center_lat), 4326)::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_constituency_center_point
    BEFORE INSERT OR UPDATE OF center_lat, center_lng ON assembly_constituencies
    FOR EACH ROW
    EXECUTE FUNCTION update_center_point();

CREATE TRIGGER update_booth_location_point
    BEFORE INSERT OR UPDATE OF location_lat, location_lng ON polling_booths
    FOR EACH ROW
    EXECUTE FUNCTION update_center_point();

-- =====================================================
-- 8. ROW LEVEL SECURITY POLICIES
-- =====================================================

-- Enable RLS
ALTER TABLE assembly_constituencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE elected_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE polling_booths ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can read constituency data
CREATE POLICY constituency_select_policy ON assembly_constituencies
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY elected_members_select_policy ON elected_members
    FOR SELECT
    USING (auth.role() = 'authenticated');

CREATE POLICY polling_booths_select_policy ON polling_booths
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Policy: Only admins can insert/update/delete constituency data
CREATE POLICY constituency_admin_policy ON assembly_constituencies
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

CREATE POLICY elected_members_admin_policy ON elected_members
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

CREATE POLICY polling_booths_admin_policy ON polling_booths
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- =====================================================
-- 9. HELPER FUNCTIONS
-- =====================================================

-- Function to get constituencies by district
CREATE OR REPLACE FUNCTION get_constituencies_by_district(
    p_district_code TEXT,
    p_state_code TEXT DEFAULT 'TN'
)
RETURNS TABLE (
    code TEXT,
    name TEXT,
    reservation_type TEXT,
    total_voters INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ac.code,
        ac.name,
        ac.reservation_type,
        ac.total_voters
    FROM assembly_constituencies ac
    WHERE ac.district_code = p_district_code
    AND ac.state_code = p_state_code
    ORDER BY ac.constituency_number;
END;
$$ LANGUAGE plpgsql;

-- Function to find nearby polling booths
CREATE OR REPLACE FUNCTION find_nearby_booths(
    p_lat DECIMAL,
    p_lng DECIMAL,
    p_radius_meters INTEGER DEFAULT 5000,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    booth_id UUID,
    booth_name TEXT,
    constituency_name TEXT,
    address TEXT,
    distance_meters DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        pb.id,
        pb.booth_name,
        ac.name,
        pb.address,
        ST_Distance(
            pb.location_point,
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography
        ) as distance_meters
    FROM polling_booths pb
    JOIN assembly_constituencies ac ON pb.constituency_code = ac.code
    WHERE ST_DWithin(
        pb.location_point,
        ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography,
        p_radius_meters
    )
    ORDER BY distance_meters
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to get election history for a constituency
CREATE OR REPLACE FUNCTION get_constituency_election_history(
    p_constituency_code TEXT
)
RETURNS TABLE (
    election_year INTEGER,
    member_name TEXT,
    political_party TEXT,
    alliance TEXT,
    vote_percentage DECIMAL,
    victory_margin INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        em.election_year,
        em.member_name,
        em.political_party,
        em.alliance,
        em.vote_percentage,
        em.victory_margin
    FROM elected_members em
    WHERE em.constituency_code = p_constituency_code
    ORDER BY em.election_year DESC;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 10. COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE assembly_constituencies IS 'Master table of Tamil Nadu and Pondicherry assembly constituencies with reservation information';
COMMENT ON TABLE elected_members IS 'Historical and current elected members for each constituency';
COMMENT ON TABLE polling_booths IS 'Polling booth locations and details for each constituency';

COMMENT ON COLUMN assembly_constituencies.reservation_type IS 'Type of reservation: Unreserved, SC, ST, Women, Muslims, Christians, etc.';
COMMENT ON COLUMN assembly_constituencies.center_point IS 'Geographic center of constituency for spatial queries';
COMMENT ON COLUMN elected_members.is_current_member IS 'TRUE if this member is currently serving';

-- =====================================================
-- END OF MIGRATION
-- =====================================================
