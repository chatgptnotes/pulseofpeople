-- ============================================================================
-- DELETE OLD SAMPLE CONSTITUENCIES
-- ============================================================================
-- Remove 5 old constituencies with wrong code format (TN-01, TN-02, etc.)
-- These are old sample data, not the real 234 constituencies
-- ============================================================================

-- Show what will be deleted first
SELECT
  'Will DELETE these 5 constituencies:' as action,
  code,
  name,
  district
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  AND state = 'Tamil Nadu'
  AND code NOT LIKE 'TN-AC-%'
ORDER BY code;

-- Expected to show: TN-01, TN-02, TN-03, TN-20, TN-30

-- ============================================================================

-- Delete the old sample constituencies
DELETE FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  AND state = 'Tamil Nadu'
  AND code NOT LIKE 'TN-AC-%';

-- Should delete 5 rows

-- ============================================================================

-- Verify the deletion
SELECT
  '✅ Deletion complete' as status,
  COUNT(*) as remaining_tn_constituencies
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  AND state = 'Tamil Nadu';

-- Should show: 234

-- ============================================================================

-- Final verification: Total count
SELECT
  COALESCE(state, '🎯 TOTAL') as state,
  COUNT(*) as constituencies
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY ROLLUP(state)
ORDER BY state NULLS LAST;

-- Expected:
-- Puducherry: 30
-- Tamil Nadu: 234
-- TOTAL: 264

-- ============================================================================
