-- ============================================================================
-- VERIFICATION QUERY: Check all 264 constituencies are loaded
-- ============================================================================
-- Run this after importing Pondicherry and Tamil Nadu constituencies
-- ============================================================================

-- Query 1: Count by State (with TOTAL)
SELECT
  COALESCE(state, '🎯 TOTAL') as state,
  COUNT(*) as constituencies,
  COUNT(*) FILTER (WHERE reserved_category = 'sc') as sc_reserved,
  COUNT(*) FILTER (WHERE reserved_category = 'st') as st_reserved,
  COUNT(*) FILTER (WHERE reserved_category = 'general') as general
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY ROLLUP(state)
ORDER BY state NULLS LAST;

-- Expected Result:
-- | state       | constituencies | sc_reserved | st_reserved | general |
-- |-------------|----------------|-------------|-------------|---------|
-- | Puducherry  | 30             | 7           | 0           | 23      |
-- | Tamil Nadu  | 234            | 44          | 2           | 188     |
-- | 🎯 TOTAL    | 264            | 51          | 2           | 211     |

-- ============================================================================

-- Query 2: Simple Total Count
SELECT COUNT(*) as total_constituencies
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111';

-- Expected: 264

-- ============================================================================

-- Query 3: Count by District (shows distribution)
SELECT
  state,
  district,
  COUNT(*) as constituencies
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY state, district
ORDER BY state, district;

-- This shows all districts with their constituency counts

-- ============================================================================

-- Query 4: Check for missing boundaries (Tamil Nadu should have GeoJSON)
SELECT
  state,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE boundaries IS NOT NULL) as with_boundaries,
  COUNT(*) FILTER (WHERE boundaries IS NULL) as without_boundaries
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY state;

-- Tamil Nadu should have boundaries for all 234
-- Pondicherry may not have boundaries (we didn't include them)

-- ============================================================================
-- ✅ SUCCESS CRITERIA
-- ============================================================================
-- Query 1 should show:
--   - Puducherry: 30 constituencies
--   - Tamil Nadu: 234 constituencies
--   - TOTAL: 264 constituencies
--
-- Query 2 should return: 264
-- ============================================================================
