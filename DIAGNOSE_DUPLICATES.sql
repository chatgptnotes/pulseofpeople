-- ============================================================================
-- DIAGNOSE: Find duplicate or problematic constituencies
-- ============================================================================

-- Query 1: Find constituencies without boundaries (should be 0 for Tamil Nadu)
SELECT
  code,
  name,
  district,
  state,
  reserved_category
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  AND state = 'Tamil Nadu'
  AND boundaries IS NULL
ORDER BY code;

-- These 5 should not exist - Tamil Nadu should all have boundaries

-- ============================================================================

-- Query 2: Check for duplicate constituency codes
SELECT
  code,
  COUNT(*) as count,
  array_agg(name) as names
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY code
HAVING COUNT(*) > 1
ORDER BY code;

-- If any results, we have duplicates!

-- ============================================================================

-- Query 3: Check for duplicate constituency names
SELECT
  name,
  COUNT(*) as count,
  array_agg(code) as codes
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY name;

-- If any results, we have duplicates!

-- ============================================================================

-- Query 4: List ALL Tamil Nadu constituencies (check for unexpected ones)
SELECT
  code,
  name,
  district,
  CASE WHEN boundaries IS NULL THEN '❌ NO' ELSE '✅ YES' END as has_boundaries
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  AND state = 'Tamil Nadu'
ORDER BY code;

-- Count should be 234, all should have boundaries

-- ============================================================================

-- Query 5: Find constituencies with codes outside expected range
SELECT
  code,
  name,
  district
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  AND state = 'Tamil Nadu'
  AND (
    code NOT LIKE 'TN-AC-%'
    OR code < 'TN-AC-001'
    OR code > 'TN-AC-234'
  )
ORDER BY code;

-- Should be empty - all codes should be TN-AC-001 to TN-AC-234

-- ============================================================================
