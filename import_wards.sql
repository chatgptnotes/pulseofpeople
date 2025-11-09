-- ============================================================================
-- WARDS IMPORT - Generated from CSV
-- ============================================================================
-- Generated: 2025-11-09T05:15:54.661Z
-- Total Wards: 5
-- ============================================================================

-- Ensure TVK organization exists
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES ('11111111-1111-1111-1111-111111111111', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO NOTHING;

-- Import wards (with constituency lookup)
INSERT INTO wards (
  organization_id,
  constituency_id,
  name,
  code,
  ward_number,
  population,
  voter_count,
  total_booths,
  urbanization,
  income_level,
  literacy_rate
) VALUES
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    'Anna Nagar Ward 1',
    'TN-AC-001-W-001',
    1,
    25000,
    18500,
    12,
    'urban',
    'medium',
    85.5
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    'Anna Nagar Ward 2',
    'TN-AC-001-W-002',
    2,
    22000,
    16200,
    10,
    'urban',
    'medium',
    88.2
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-001' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    'Anna Nagar Ward 3',
    'TN-AC-001-W-003',
    3,
    28000,
    20500,
    14,
    'urban',
    'high',
    90.1
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-002' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    'Kilpauk Ward 1',
    'TN-AC-002-W-001',
    1,
    30000,
    22000,
    15,
    'urban',
    'high',
    87.5
  ),
  (
    '11111111-1111-1111-1111-111111111111'::uuid,
    (SELECT id FROM constituencies WHERE code = 'TN-AC-002' AND organization_id = '11111111-1111-1111-1111-111111111111' LIMIT 1),
    'Kilpauk Ward 2',
    'TN-AC-002-W-002',
    2,
    27000,
    19800,
    13,
    'urban',
    'high',
    89.0
  )
ON CONFLICT (organization_id, code) DO UPDATE SET
  name = EXCLUDED.name,
  ward_number = EXCLUDED.ward_number,
  population = EXCLUDED.population,
  voter_count = EXCLUDED.voter_count,
  total_booths = EXCLUDED.total_booths,
  urbanization = EXCLUDED.urbanization,
  income_level = EXCLUDED.income_level,
  literacy_rate = EXCLUDED.literacy_rate,
  updated_at = NOW();

-- Verify import
SELECT
  'Wards Import' as type,
  COUNT(*) as total_imported,
  COUNT(DISTINCT constituency_id) as constituencies_covered
FROM wards
WHERE organization_id = '11111111-1111-1111-1111-111111111111';

-- Show breakdown by constituency
SELECT
  c.code as constituency_code,
  c.name as constituency_name,
  COUNT(w.id) as ward_count,
  SUM(w.total_booths) as total_booths
FROM constituencies c
LEFT JOIN wards w ON w.constituency_id = c.id
WHERE c.organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY c.id, c.code, c.name
HAVING COUNT(w.id) > 0
ORDER BY c.code;
