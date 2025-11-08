-- =====================================================
-- DISTRICTS MASTER TABLE
-- Tamil Nadu (38) & Pondicherry (4) = 42 Districts
-- Date: 2025-11-07
-- =====================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- =====================================================
-- 1. CREATE DISTRICTS TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS districts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    name_tamil TEXT NOT NULL,
    name_local TEXT,

    -- State relationship
    state_code TEXT NOT NULL REFERENCES states(code) ON DELETE CASCADE,

    -- Geographic data
    center_lat DECIMAL(10,8),
    center_lng DECIMAL(11,8),
    center_point GEOGRAPHY(POINT, 4326),
    area_km2 DECIMAL(10,2),
    geojson JSONB,                            -- District boundary polygon

    -- Electoral data
    total_constituencies INTEGER DEFAULT 0,
    total_voters BIGINT DEFAULT 0,
    total_polling_booths INTEGER DEFAULT 0,

    -- Administrative info
    headquarters TEXT,
    formation_year INTEGER,
    population BIGINT,
    literacy_rate DECIMAL(5,2),
    sex_ratio INTEGER,                        -- Females per 1000 males

    -- Multi-tenancy
    tenant_id TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL
);

-- Create indexes
CREATE INDEX idx_districts_state ON districts(state_code);
CREATE INDEX idx_districts_code ON districts(code);
CREATE INDEX idx_districts_name ON districts(name);
CREATE INDEX idx_districts_tenant ON districts(tenant_id);
CREATE INDEX idx_districts_center_point ON districts USING GIST(center_point);

-- =====================================================
-- 2. INSERT TAMIL NADU DISTRICTS (38)
-- =====================================================

INSERT INTO districts (code, name, name_tamil, state_code, headquarters, center_lat, center_lng, formation_year) VALUES

-- Tamil Nadu Districts (alphabetically by code)
('TN01', 'Ariyalur', 'அரியலூர்', 'TN', 'Ariyalur', 11.1401, 79.0766, 1995),
('TN02', 'Chengalpattu', 'செங்கல்பட்டு', 'TN', 'Chengalpattu', 12.6917, 79.9752, 2019),
('TN03', 'Chennai', 'சென்னை', 'TN', 'Chennai', 13.0827, 80.2707, 1956),
('TN04', 'Coimbatore', 'கோயம்புத்தூர்', 'TN', 'Coimbatore', 11.0168, 76.9558, 1956),
('TN05', 'Cuddalore', 'கடலூர்', 'TN', 'Cuddalore', 11.7480, 79.7714, 1956),
('TN06', 'Dharmapuri', 'தர்மபுரி', 'TN', 'Dharmapuri', 12.1211, 78.1582, 1965),
('TN07', 'Dindigul', 'திண்டுக்கல்', 'TN', 'Dindigul', 10.3673, 77.9803, 1985),
('TN08', 'Erode', 'ஈரோடு', 'TN', 'Erode', 11.3410, 77.7172, 1979),
('TN09', 'Kallakurichi', 'கள்ளக்குறிச்சி', 'TN', 'Kallakurichi', 11.7401, 78.9597, 2019),
('TN10', 'Kanchipuram', 'காஞ்சிபுரம்', 'TN', 'Kanchipuram', 12.8342, 79.7036, 1956),
('TN11', 'Kanyakumari', 'கன்னியாகுமரி', 'TN', 'Nagercoil', 8.0883, 77.5385, 1956),
('TN12', 'Karur', 'கரூர்', 'TN', 'Karur', 10.9601, 78.0766, 1995),
('TN13', 'Krishnagiri', 'கிருஷ்ணகிரி', 'TN', 'Krishnagiri', 12.5186, 78.2137, 2004),
('TN14', 'Madurai', 'மதுரை', 'TN', 'Madurai', 9.9252, 78.1198, 1956),
('TN15', 'Mayiladuthurai', 'மயிலாடுதுறை', 'TN', 'Mayiladuthurai', 11.1028, 79.6550, 2020),
('TN16', 'Nagapattinam', 'நாகப்பட்டினம்', 'TN', 'Nagapattinam', 10.7672, 79.8449, 1991),
('TN17', 'Namakkal', 'நாமக்கல்', 'TN', 'Namakkal', 11.2189, 78.1677, 1996),
('TN18', 'Nilgiris', 'நீலகிரி', 'TN', 'Udhagamandalam (Ooty)', 11.4064, 76.6932, 1956),
('TN19', 'Perambalur', 'பெரம்பலூர்', 'TN', 'Perambalur', 11.2325, 78.8800, 1995),
('TN20', 'Pudukkottai', 'புதுக்கோட்டை', 'TN', 'Pudukkottai', 10.3833, 78.8000, 1974),
('TN21', 'Ramanathapuram', 'இராமநாதபுரம்', 'TN', 'Ramanathapuram', 9.3639, 78.8395, 1956),
('TN22', 'Ranipet', 'ராணிப்பேட்டை', 'TN', 'Ranipet', 12.9249, 79.3369, 2019),
('TN23', 'Salem', 'சேலம்', 'TN', 'Salem', 11.6643, 78.1460, 1956),
('TN24', 'Sivagangai', 'சிவகங்கை', 'TN', 'Sivagangai', 9.8477, 78.4815, 1984),
('TN25', 'Tenkasi', 'தென்காசி', 'TN', 'Tenkasi', 8.9600, 77.3152, 2019),
('TN26', 'Thanjavur', 'தஞ்சாவூர்', 'TN', 'Thanjavur', 10.7870, 79.1378, 1956),
('TN27', 'Theni', 'தேனி', 'TN', 'Theni', 10.0104, 77.4977, 1997),
('TN28', 'Thoothukudi', 'தூத்துக்குடி', 'TN', 'Thoothukudi', 8.7642, 78.1348, 1986),
('TN29', 'Tiruchirappalli', 'திருச்சிராப்பள்ளி', 'TN', 'Tiruchirappalli', 10.7905, 78.7047, 1956),
('TN30', 'Tirunelveli', 'திருநெல்வேலி', 'TN', 'Tirunelveli', 8.7139, 77.7567, 1956),
('TN31', 'Tirupathur', 'திருப்பத்தூர்', 'TN', 'Tirupathur', 12.4980, 78.5718, 2019),
('TN32', 'Tiruppur', 'திருப்பூர்', 'TN', 'Tiruppur', 11.1085, 77.3411, 2009),
('TN33', 'Tiruvallur', 'திருவள்ளூர்', 'TN', 'Tiruvallur', 13.1434, 79.9099, 1997),
('TN34', 'Tiruvannamalai', 'திருவண்ணாமலை', 'TN', 'Tiruvannamalai', 12.2253, 79.0747, 1989),
('TN35', 'Tiruvarur', 'திருவாரூர்', 'TN', 'Tiruvarur', 10.7730, 79.6345, 1991),
('TN36', 'Vellore', 'வேலூர்', 'TN', 'Vellore', 12.9165, 79.1325, 1989),
('TN37', 'Viluppuram', 'விழுப்புரம்', 'TN', 'Viluppuram', 11.9401, 79.4861, 1993),
('TN38', 'Virudhunagar', 'விருதுநகர்', 'TN', 'Virudhunagar', 9.5810, 77.9624, 1985);

-- =====================================================
-- 3. INSERT PONDICHERRY DISTRICTS (4)
-- =====================================================

INSERT INTO districts (code, name, name_tamil, state_code, headquarters, center_lat, center_lng, formation_year) VALUES

-- Pondicherry/Puducherry Districts
('PY01', 'Puducherry', 'புதுச்சேரி', 'PY', 'Puducherry', 11.9416, 79.8083, 1954),
('PY02', 'Karaikal', 'காரைக்கால்', 'PY', 'Karaikal', 10.9254, 79.8380, 1954),
('PY03', 'Mahe', 'மாஹே', 'PY', 'Mahe', 11.7008, 75.5368, 1954),
('PY04', 'Yanam', 'ஆனம்', 'PY', 'Yanam', 16.7333, 82.2167, 1954);

-- =====================================================
-- 4. CREATE TRIGGERS
-- =====================================================

CREATE OR REPLACE FUNCTION update_district_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_districts_timestamp
    BEFORE UPDATE ON districts
    FOR EACH ROW
    EXECUTE FUNCTION update_district_updated_at();

-- Trigger to auto-update center_point when lat/lng changes
CREATE OR REPLACE FUNCTION update_district_center_point()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.center_lat IS NOT NULL AND NEW.center_lng IS NOT NULL THEN
        NEW.center_point = ST_SetSRID(ST_MakePoint(NEW.center_lng, NEW.center_lat), 4326)::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_districts_center_point
    BEFORE INSERT OR UPDATE OF center_lat, center_lng ON districts
    FOR EACH ROW
    EXECUTE FUNCTION update_district_center_point();

-- =====================================================
-- 5. ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE districts ENABLE ROW LEVEL SECURITY;

-- Policy: All authenticated users can read district data
CREATE POLICY districts_select_policy ON districts
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Policy: Only admins can modify district data
CREATE POLICY districts_admin_policy ON districts
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM users
            WHERE id = auth.uid()
            AND role IN ('admin', 'super_admin')
        )
    );

-- =====================================================
-- 6. VIEWS
-- =====================================================

-- View for district summary by state
CREATE OR REPLACE VIEW district_summary_by_state AS
SELECT
    s.code as state_code,
    s.name as state_name,
    COUNT(d.id) as total_districts,
    SUM(d.total_constituencies) as total_constituencies,
    SUM(d.total_voters) as total_voters,
    ROUND(AVG(d.area_km2), 2) as avg_area_km2
FROM states s
LEFT JOIN districts d ON s.code = d.state_code
GROUP BY s.code, s.name
ORDER BY s.code;

-- View for district details with state info
CREATE OR REPLACE VIEW district_details AS
SELECT
    d.code,
    d.name,
    d.name_tamil,
    d.headquarters,
    d.state_code,
    s.name as state_name,
    d.total_constituencies,
    d.total_voters,
    d.total_polling_booths,
    d.area_km2,
    d.formation_year,
    d.center_lat,
    d.center_lng
FROM districts d
JOIN states s ON d.state_code = s.code
ORDER BY d.state_code, d.name;

-- =====================================================
-- 7. HELPER FUNCTIONS
-- =====================================================

-- Function to get districts by state
CREATE OR REPLACE FUNCTION get_districts_by_state(p_state_code TEXT)
RETURNS TABLE (
    code TEXT,
    name TEXT,
    name_tamil TEXT,
    headquarters TEXT,
    constituencies INTEGER,
    voters BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.code,
        d.name,
        d.name_tamil,
        d.headquarters,
        d.total_constituencies,
        d.total_voters
    FROM districts d
    WHERE d.state_code = p_state_code
    ORDER BY d.name;
END;
$$ LANGUAGE plpgsql;

-- Function to get district statistics
CREATE OR REPLACE FUNCTION get_district_stats(p_district_code TEXT)
RETURNS TABLE (
    district_name TEXT,
    state_name TEXT,
    constituencies INTEGER,
    voters BIGINT,
    booths INTEGER,
    area DECIMAL,
    population BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.name,
        s.name,
        d.total_constituencies,
        d.total_voters,
        d.total_polling_booths,
        d.area_km2,
        d.population
    FROM districts d
    JOIN states s ON d.state_code = s.code
    WHERE d.code = p_district_code;
END;
$$ LANGUAGE plpgsql;

-- Function to update district statistics from constituencies
CREATE OR REPLACE FUNCTION refresh_district_statistics()
RETURNS void AS $$
BEGIN
    -- Update constituency counts
    UPDATE districts d
    SET total_constituencies = (
        SELECT COUNT(*)
        FROM assembly_constituencies ac
        WHERE ac.district_code = d.code
    );

    -- Update voter counts
    UPDATE districts d
    SET total_voters = (
        SELECT COALESCE(SUM(total_voters), 0)
        FROM assembly_constituencies ac
        WHERE ac.district_code = d.code
    );

    -- Update polling booth counts
    UPDATE districts d
    SET total_polling_booths = (
        SELECT COUNT(*)
        FROM polling_booths pb
        JOIN assembly_constituencies ac ON pb.constituency_code = ac.code
        WHERE ac.district_code = d.code
    );

    -- Also refresh state statistics
    PERFORM refresh_state_statistics();
END;
$$ LANGUAGE plpgsql;

-- Function to find nearest districts to a point
CREATE OR REPLACE FUNCTION find_nearest_districts(
    p_lat DECIMAL,
    p_lng DECIMAL,
    p_limit INTEGER DEFAULT 5
)
RETURNS TABLE (
    district_code TEXT,
    district_name TEXT,
    state_code TEXT,
    distance_meters DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.code,
        d.name,
        d.state_code,
        ST_Distance(
            d.center_point,
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography
        ) as distance_meters
    FROM districts d
    WHERE d.center_point IS NOT NULL
    ORDER BY distance_meters
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE districts IS 'Master table of Tamil Nadu and Pondicherry districts';
COMMENT ON COLUMN districts.code IS 'Unique district code (TN01-TN38, PY01-PY04)';
COMMENT ON COLUMN districts.center_point IS 'Geographic center of district for map display';
COMMENT ON COLUMN districts.total_constituencies IS 'Number of assembly constituencies in district (auto-updated)';
COMMENT ON COLUMN districts.formation_year IS 'Year when district was formed/separated';

-- =====================================================
-- 9. VALIDATION QUERIES
-- =====================================================

-- Verify all districts inserted
-- SELECT state_code, COUNT(*) as district_count
-- FROM districts
-- GROUP BY state_code
-- ORDER BY state_code;
-- Expected: TN=38, PY=4

-- Check district details
-- SELECT * FROM district_details ORDER BY state_code, name;

-- Test functions
-- SELECT * FROM get_districts_by_state('TN');
-- SELECT * FROM get_district_stats('TN03');
-- SELECT * FROM find_nearest_districts(13.0827, 80.2707, 5);

-- =====================================================
-- END OF MIGRATION
-- =====================================================
