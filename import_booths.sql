-- ============================================================================
-- POLLING BOOTHS IMPORT - Generated from CSV
-- ============================================================================
-- Generated: 2025-11-09T05:15:54.662Z
-- Total Booths: 5
-- ============================================================================

-- Ensure TVK organization exists
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES ('11111111-1111-1111-1111-111111111111', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO NOTHING;

-- Import polling booths (with constituency and ward lookup)
INSERT INTO polling_booths (
  organization_id,
  constituency_id,
  ward_id,
  booth_number,
  name,
  address,
  latitude,
  longitude,
  total_voters,
  male_voters,
  female_voters,
  transgender_voters,
  accessible,
  parking_available,
  landmark
) VALUES
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    (SELECT id FROM wards WHERE code = 'TN-AC-001-W-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    '001',
    'Government High School Anna Nagar',
    '"123 Main Street',
    Anna Nagar,
    Chennai - 600040",
    13.0827,
    80.2707,
    1500,
    750,
    false,
    false,
    'true'
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    (SELECT id FROM wards WHERE code = 'TN-AC-001-W-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    '002',
    'Corporation Primary School',
    '"456 Park Road',
    Anna Nagar,
    Chennai - 600040",
    13.0850,
    80.2720,
    1400,
    700,
    false,
    false,
    'false'
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    (SELECT id FROM wards WHERE code = 'TN-AC-001-W-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    '003',
    'Community Hall Anna Nagar',
    '"789 Lake Avenue',
    Anna Nagar,
    Chennai - 600040",
    13.0865,
    80.2735,
    1350,
    675,
    false,
    true,
    'true'
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    (SELECT id FROM wards WHERE code = 'TN-AC-001-W-002' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    '001',
    'Government Middle School',
    '"321 2nd Avenue',
    Anna Nagar,
    Chennai - 600040",
    13.0880,
    80.2750,
    1600,
    800,
    false,
    false,
    'true'
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    (SELECT id FROM wards WHERE code = 'TN-AC-001-W-002' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    '002',
    'Private School Building',
    '"654 3rd Cross',
    Anna Nagar,
    Chennai - 600040",
    13.0895,
    80.2765,
    1450,
    725,
    false,
    true,
    'false'
  )
ON CONFLICT (organization_id, constituency_id, booth_number) DO UPDATE SET
  name = EXCLUDED.name,
  address = EXCLUDED.address,
  latitude = EXCLUDED.latitude,
  longitude = EXCLUDED.longitude,
  total_voters = EXCLUDED.total_voters,
  male_voters = EXCLUDED.male_voters,
  female_voters = EXCLUDED.female_voters,
  transgender_voters = EXCLUDED.transgender_voters,
  accessible = EXCLUDED.accessible,
  parking_available = EXCLUDED.parking_available,
  landmark = EXCLUDED.landmark,
  updated_at = NOW();

-- Verify import
SELECT
  'Booths Import' as type,
  COUNT(*) as total_imported,
  COUNT(DISTINCT constituency_id) as constituencies_covered,
  COUNT(DISTINCT ward_id) as wards_covered,
  SUM(total_voters) as total_voters
FROM polling_booths
WHERE organization_id = '11111111-1111-1111-1111-111111111111';

-- Show breakdown by constituency
SELECT
  c.code as constituency_code,
  c.name as constituency_name,
  COUNT(pb.id) as booth_count,
  SUM(pb.total_voters) as total_voters,
  SUM(pb.male_voters) as male_voters,
  SUM(pb.female_voters) as female_voters
FROM constituencies c
LEFT JOIN polling_booths pb ON pb.constituency_id = c.id
WHERE c.organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY c.id, c.code, c.name
HAVING COUNT(pb.id) > 0
ORDER BY c.code;
