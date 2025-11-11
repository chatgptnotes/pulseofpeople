-- ============================================================================
-- INSERT SAMPLE DATA FOR TVK (Tamilaga Vettri Kazhagam)
-- ============================================================================
-- Run this if your tables are empty
-- ============================================================================

-- Insert TVK as the main organization
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    slug = EXCLUDED.slug,
    type = EXCLUDED.type,
    subscription_status = EXCLUDED.subscription_status,
    is_active = EXCLUDED.is_active;

-- Insert sample constituencies (Tamil Nadu)
INSERT INTO constituencies (organization_id, name, code, type, state, district, population, voter_count)
VALUES
    ('11111111-1111-1111-1111-111111111111', 'Chennai North', 'TN-01', 'parliament', 'Tamil Nadu', 'Chennai', 2100000, 1450000),
    ('11111111-1111-1111-1111-111111111111', 'Chennai Central', 'TN-02', 'parliament', 'Tamil Nadu', 'Chennai', 1950000, 1320000),
    ('11111111-1111-1111-1111-111111111111', 'Chennai South', 'TN-03', 'parliament', 'Tamil Nadu', 'Chennai', 2050000, 1410000),
    ('11111111-1111-1111-1111-111111111111', 'Coimbatore', 'TN-20', 'parliament', 'Tamil Nadu', 'Coimbatore', 1850000, 1280000),
    ('11111111-1111-1111-1111-111111111111', 'Madurai', 'TN-30', 'parliament', 'Tamil Nadu', 'Madurai', 1720000, 1190000)
ON CONFLICT (organization_id, code) DO UPDATE SET
    name = EXCLUDED.name,
    population = EXCLUDED.population,
    voter_count = EXCLUDED.voter_count;

-- Insert sample wards
INSERT INTO wards (organization_id, constituency_id, name, code, ward_number, population, voter_count)
VALUES
    ('11111111-1111-1111-1111-111111111111',
     (SELECT id FROM constituencies WHERE code = 'TN-01' LIMIT 1),
     'Anna Nagar', 'TN-01-W01', 1, 85000, 62000),
    ('11111111-1111-1111-1111-111111111111',
     (SELECT id FROM constituencies WHERE code = 'TN-01' LIMIT 1),
     'Kilpauk', 'TN-01-W02', 2, 78000, 56000),
    ('11111111-1111-1111-1111-111111111111',
     (SELECT id FROM constituencies WHERE code = 'TN-02' LIMIT 1),
     'Egmore', 'TN-02-W01', 1, 72000, 51000)
ON CONFLICT (constituency_id, code) DO UPDATE SET
    name = EXCLUDED.name,
    population = EXCLUDED.population,
    voter_count = EXCLUDED.voter_count;

-- Insert sample polling booths
DO $$
DECLARE
    constituency_id UUID;
    booth_num INTEGER;
    lat DECIMAL;
    lon DECIMAL;
BEGIN
    -- Get Chennai North constituency ID
    SELECT id INTO constituency_id FROM constituencies WHERE code = 'TN-01' LIMIT 1;

    IF constituency_id IS NOT NULL THEN
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
                (ARRAY['Government School', 'Community Hall', 'Municipal Office'])[floor(random() * 3 + 1)],
                lat,
                lon,
                floor(random() * 500 + 800)::INTEGER,
                floor(random() * 250 + 400)::INTEGER,
                floor(random() * 250 + 400)::INTEGER,
                (ARRAY['school', 'community_hall', 'government_office'])[floor(random() * 3 + 1)],
                random() > 0.2
            )
            ON CONFLICT (organization_id, constituency_id, booth_number)
            DO NOTHING;
        END LOOP;
    END IF;
END $$;

-- Verify insertions
SELECT
    'Data Insertion Summary' as summary,
    (SELECT COUNT(*) FROM organizations) as organizations,
    (SELECT COUNT(*) FROM constituencies) as constituencies,
    (SELECT COUNT(*) FROM wards) as wards,
    (SELECT COUNT(*) FROM polling_booths) as polling_booths;
