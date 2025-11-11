-- =====================================================
-- STATES MASTER TABLE
-- Tamil Nadu & Pondicherry
-- Date: 2025-11-07
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =====================================================
-- 1. CREATE STATES TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS states (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_tamil TEXT NOT NULL,
    name_local TEXT,                          -- Same as name_tamil for these states

    -- Statistics
    total_districts INTEGER DEFAULT 0,
    total_constituencies INTEGER DEFAULT 0,
    total_voters BIGINT DEFAULT 0,
    total_polling_booths INTEGER DEFAULT 0,
    area_km2 DECIMAL(10,2),
    population BIGINT,

    -- Geographic center
    center_lat DECIMAL(10,8),
    center_lng DECIMAL(11,8),
    center_point GEOGRAPHY(POINT, 4326),

    -- Boundary data (GeoJSON)
    geojson JSONB,                            -- Store state boundary polygon

    -- Administrative info
    capital TEXT,
    largest_city TEXT,
    state_type TEXT,                          -- 'State' or 'Union Territory'
    official_language TEXT,
    formation_date DATE,

    -- Electoral info
    lok_sabha_seats INTEGER,
    rajya_sabha_seats INTEGER,

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,

    -- Constraints
    CONSTRAINT valid_state_code CHECK (code IN ('TN', 'PY', 'KA', 'KL', 'AP', 'TS'))
);

-- Create indexes
CREATE INDEX idx_states_code ON states(code);
CREATE INDEX idx_states_name ON states(name);
CREATE INDEX idx_states_tenant ON states(tenant_id);
CREATE INDEX idx_states_center_point ON states USING GIST(center_point);

-- =====================================================
-- 2. INSERT SEED DATA
-- =====================================================

INSERT INTO states (
    code,
    name,
    name_tamil,
    total_districts,
    total_constituencies,
    total_voters,
    area_km2,
    population,
    center_lat,
    center_lng,
    capital,
    largest_city,
    state_type,
    official_language,
    formation_date,
    lok_sabha_seats,
    rajya_sabha_seats
) VALUES
(
    'TN',
    'Tamil Nadu',
    'தமிழ்நாடு',
    38,                         -- Districts
    234,                        -- Assembly constituencies
    62900000,                   -- Total voters (approx 63 million registered voters)
    130060,                     -- Area in sq km
    72100000,                   -- Population (2021 estimate)
    11.1271,                    -- Center latitude (approximate center of TN)
    78.6569,                    -- Center longitude
    'Chennai',
    'Chennai',
    'State',
    'Tamil',
    '1956-11-01',               -- Reorganisation Act 1956
    39,                         -- Lok Sabha seats
    18                          -- Rajya Sabha seats
),
(
    'PY',
    'Puducherry',
    'புதுச்சேரி',
    4,                          -- Districts
    30,                         -- Assembly constituencies
    1000000,                    -- Total voters (approx 1 million)
    479,                        -- Area in sq km
    1400000,                    -- Population
    11.9416,                    -- Center latitude (Puducherry city)
    79.8083,                    -- Center longitude
    'Puducherry',
    'Puducherry',
    'Union Territory',
    'Tamil, French',
    '1954-11-01',               -- Transfer from French to Indian Union
    1,                          -- Lok Sabha seat
    3                           -- Rajya Sabha seats
);

-- =====================================================
-- 3. CREATE TRIGGER FOR AUTO-UPDATING
-- =====================================================

CREATE OR REPLACE FUNCTION update_state_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_states_timestamp
    BEFORE UPDATE ON states
    FOR EACH ROW
    EXECUTE FUNCTION update_state_updated_at();

-- Trigger to auto-update center_point when lat/lng changes
CREATE OR REPLACE FUNCTION update_state_center_point()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.center_lat IS NOT NULL AND NEW.center_lng IS NOT NULL THEN
        NEW.center_point = ST_SetSRID(ST_MakePoint(NEW.center_lng, NEW.center_lat), 4326)::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_states_center_point
    BEFORE INSERT OR UPDATE OF center_lat, center_lng ON states
    FOR EACH ROW
    EXECUTE FUNCTION update_state_center_point();

-- =====================================================
-- 4. ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE states ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can read state data
CREATE POLICY states_select_policy ON states
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Policy: Only admins can modify state data
CREATE POLICY states_admin_policy ON states
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- =====================================================
-- 5. VIEWS
-- =====================================================

-- View for state overview
CREATE OR REPLACE VIEW state_overview AS
SELECT
    code,
    name,
    name_tamil,
    total_districts,
    total_constituencies,
    total_voters,
    ROUND(total_voters::DECIMAL / total_constituencies, 0) as avg_voters_per_constituency,
    area_km2,
    ROUND(population::DECIMAL / area_km2, 2) as population_density,
    capital,
    state_type
FROM states
ORDER BY code;

-- =====================================================
-- 6. HELPER FUNCTIONS
-- =====================================================

-- Function to get state statistics
CREATE OR REPLACE FUNCTION get_state_stats(p_state_code TEXT)
RETURNS TABLE (
    state_name TEXT,
    districts INTEGER,
    constituencies INTEGER,
    voters BIGINT,
    booths INTEGER,
    area DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.name,
        s.total_districts,
        s.total_constituencies,
        s.total_voters,
        s.total_polling_booths,
        s.area_km2
    FROM states s
    WHERE s.code = p_state_code;
END;
$$ LANGUAGE plpgsql;

-- Function to update state statistics from child tables
CREATE OR REPLACE FUNCTION refresh_state_statistics()
RETURNS void AS $$
BEGIN
    -- Update district counts
    UPDATE states s
    SET total_districts = (
        SELECT COUNT(*)
        FROM districts d
        WHERE d.state_code = s.code
    );

    -- Update constituency counts
    UPDATE states s
    SET total_constituencies = (
        SELECT COUNT(*)
        FROM assembly_constituencies ac
        WHERE ac.state_code = s.code
    );

    -- Update voter counts
    UPDATE states s
    SET total_voters = (
        SELECT COALESCE(SUM(total_voters), 0)
        FROM assembly_constituencies ac
        WHERE ac.state_code = s.code
    );

    -- Update polling booth counts
    UPDATE states s
    SET total_polling_booths = (
        SELECT COUNT(*)
        FROM polling_booths pb
        JOIN assembly_constituencies ac ON pb.constituency_code = ac.code
        WHERE ac.state_code = s.code
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 7. COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE states IS 'Master table of Indian states and union territories covered by the platform';
COMMENT ON COLUMN states.code IS 'Two-letter state code (TN, PY, KA, etc.)';
COMMENT ON COLUMN states.center_point IS 'Geographic center of state for map display';
COMMENT ON COLUMN states.geojson IS 'State boundary polygon in GeoJSON format';
COMMENT ON COLUMN states.total_voters IS 'Total registered voters (updated from constituencies)';

-- =====================================================
-- 8. VALIDATION QUERIES
-- =====================================================

-- Verify data
-- SELECT * FROM states;

-- Check state overview
-- SELECT * FROM state_overview;

-- Test statistics function
-- SELECT * FROM get_state_stats('TN');

-- =====================================================
-- END OF MIGRATION
-- =====================================================
