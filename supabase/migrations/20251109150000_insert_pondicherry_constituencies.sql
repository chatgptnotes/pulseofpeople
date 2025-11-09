-- ============================================================================
-- INSERT PONDICHERRY (PUDUCHERRY) CONSTITUENCIES
-- ============================================================================
-- Pondicherry has 30 Assembly constituencies across 4 regions
-- 1. Puducherry region: 23 seats
-- 2. Karaikal region: 5 seats
-- 3. Mahe region: 1 seat
-- 4. Yanam region: 1 seat
-- ============================================================================

-- Ensure TVK organization exists
INSERT INTO organizations (id, name, slug, type, subscription_status, is_active)
VALUES ('11111111-1111-1111-1111-111111111111', 'Tamilaga Vettri Kazhagam', 'tvk', 'political_party', 'active', true)
ON CONFLICT (id) DO NOTHING;

-- Insert all 30 Pondicherry Assembly Constituencies
INSERT INTO constituencies (
  organization_id,
  name,
  code,
  type,
  state,
  district,
  population,
  voter_count,
  total_booths,
  reserved_category,
  last_election_year
) VALUES
  -- PUDUCHERRY REGION (23 constituencies)
  ('11111111-1111-1111-1111-111111111111', 'Yanam', 'PY-AC-001', 'assembly', 'Puducherry', 'Yanam', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Mahe', 'PY-AC-002', 'assembly', 'Puducherry', 'Mahe', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Thirubuvanai', 'PY-AC-003', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'sc', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Oupalam', 'PY-AC-004', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Nettapakkam', 'PY-AC-005', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Mangalam', 'PY-AC-006', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'sc', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Villianur', 'PY-AC-007', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Ozhukarai', 'PY-AC-008', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Kadirkamam', 'PY-AC-009', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Indira Nagar', 'PY-AC-010', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Kalapet', 'PY-AC-011', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Muthialpet', 'PY-AC-012', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Raj Bhavan', 'PY-AC-013', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Pondicherry North', 'PY-AC-014', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Pondicherry South', 'PY-AC-015', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Lawspet', 'PY-AC-016', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Thattanchavady', 'PY-AC-017', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'sc', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Ariankuppam', 'PY-AC-018', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Manavely', 'PY-AC-019', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Ossudu', 'PY-AC-020', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Bahour', 'PY-AC-021', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Embalam', 'PY-AC-022', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'sc', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Nellithope', 'PY-AC-023', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021),

  -- KARAIKAL REGION (5 constituencies)
  ('11111111-1111-1111-1111-111111111111', 'Karaikal North', 'PY-AC-024', 'assembly', 'Puducherry', 'Karaikal', NULL, 0, 0, 'sc', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Karaikal South', 'PY-AC-025', 'assembly', 'Puducherry', 'Karaikal', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Thirunallar', 'PY-AC-026', 'assembly', 'Puducherry', 'Karaikal', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Neravy', 'PY-AC-027', 'assembly', 'Puducherry', 'Karaikal', NULL, 0, 0, 'general', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Kottucherry', 'PY-AC-028', 'assembly', 'Puducherry', 'Karaikal', NULL, 0, 0, 'general', 2021),

  -- Reserved constituencies
  ('11111111-1111-1111-1111-111111111111', 'Mudaliarpet', 'PY-AC-029', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'sc', 2021),
  ('11111111-1111-1111-1111-111111111111', 'Kamaraj Nagar', 'PY-AC-030', 'assembly', 'Puducherry', 'Puducherry', NULL, 0, 0, 'general', 2021)
ON CONFLICT (organization_id, code) DO UPDATE SET
  name = EXCLUDED.name,
  district = EXCLUDED.district,
  reserved_category = EXCLUDED.reserved_category;

-- Verify Pondicherry insertions
SELECT
  'Pondicherry Constituencies' as summary,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE reserved_category = 'sc') as sc_reserved,
  COUNT(*) FILTER (WHERE reserved_category = 'general') as general,
  COUNT(DISTINCT district) as regions
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
  AND code LIKE 'PY-AC-%';

-- Overall summary
SELECT
  state,
  COUNT(*) as constituencies,
  COUNT(*) FILTER (WHERE reserved_category = 'sc') as sc,
  COUNT(*) FILTER (WHERE reserved_category = 'st') as st,
  COUNT(*) FILTER (WHERE reserved_category = 'general') as general
FROM constituencies
WHERE organization_id = '11111111-1111-1111-1111-111111111111'
GROUP BY state
ORDER BY state;
