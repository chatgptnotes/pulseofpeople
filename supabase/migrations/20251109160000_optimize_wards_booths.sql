-- ============================================================================
-- OPTIMIZATION MIGRATION: Wards and Polling Booths Indexes
-- ============================================================================
-- Created: 2025-11-09 16:00:00
-- Purpose: Add performance indexes and constraints for bulk operations
-- ============================================================================

-- ============================================================================
-- WARDS TABLE OPTIMIZATIONS
-- ============================================================================

-- Additional indexes for fast lookups during bulk imports
CREATE INDEX IF NOT EXISTS idx_wards_code ON wards(code);
CREATE INDEX IF NOT EXISTS idx_wards_org_code ON wards(organization_id, code);
CREATE INDEX IF NOT EXISTS idx_wards_ward_number ON wards(constituency_id, ward_number);
CREATE INDEX IF NOT EXISTS idx_wards_name_search ON wards USING gin(to_tsvector('english', name));

-- Index for pagination and filtering
CREATE INDEX IF NOT EXISTS idx_wards_created_at ON wards(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_wards_updated_at ON wards(updated_at DESC);

-- Partial indexes for active wards (if you add is_active column later)
-- CREATE INDEX IF NOT EXISTS idx_wards_active ON wards(organization_id) WHERE is_active = true;

-- Add constraint for positive values
ALTER TABLE wards ADD CONSTRAINT IF NOT EXISTS wards_population_positive CHECK (population IS NULL OR population >= 0);
ALTER TABLE wards ADD CONSTRAINT IF NOT EXISTS wards_voter_count_positive CHECK (voter_count >= 0);
ALTER TABLE wards ADD CONSTRAINT IF NOT EXISTS wards_total_booths_positive CHECK (total_booths >= 0);
ALTER TABLE wards ADD CONSTRAINT IF NOT EXISTS wards_literacy_rate_valid CHECK (literacy_rate IS NULL OR (literacy_rate >= 0 AND literacy_rate <= 100));

-- ============================================================================
-- POLLING BOOTHS TABLE OPTIMIZATIONS
-- ============================================================================

-- Additional indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_booths_booth_number ON polling_booths(booth_number);
CREATE INDEX IF NOT EXISTS idx_booths_org_booth ON polling_booths(organization_id, booth_number);
CREATE INDEX IF NOT EXISTS idx_booths_name_search ON polling_booths USING gin(to_tsvector('english', name));

-- Composite index for unique booth identification
CREATE INDEX IF NOT EXISTS idx_booths_unique_lookup ON polling_booths(organization_id, constituency_id, booth_number);

-- Index for pagination and filtering
CREATE INDEX IF NOT EXISTS idx_booths_created_at ON polling_booths(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_booths_updated_at ON polling_booths(updated_at DESC);

-- Spatial index already exists (idx_booths_location) but ensure it's there
-- CREATE INDEX IF NOT EXISTS idx_booths_location ON polling_booths USING GIST(location);

-- Index for filtering by accessibility
CREATE INDEX IF NOT EXISTS idx_booths_accessible ON polling_booths(is_accessible) WHERE is_accessible = true;

-- Add constraints for data integrity
ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_total_voters_positive CHECK (total_voters >= 0);
ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_male_voters_positive CHECK (male_voters >= 0);
ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_female_voters_positive CHECK (female_voters >= 0);
ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_transgender_voters_positive CHECK (transgender_voters >= 0);

-- Constraint: Sum of gender voters should not exceed total voters
ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_gender_sum_valid
CHECK (male_voters + female_voters + transgender_voters <= total_voters);

-- Constraint: Valid GPS coordinates
ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_latitude_valid
CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90));

ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_longitude_valid
CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180));

-- Constraint: Priority level range
ALTER TABLE polling_booths ADD CONSTRAINT IF NOT EXISTS booths_priority_valid
CHECK (priority_level IS NULL OR (priority_level >= 1 AND priority_level <= 5));

-- ============================================================================
-- PERFORMANCE STATISTICS UPDATE
-- ============================================================================

-- Analyze tables to update statistics for query planner
ANALYZE wards;
ANALYZE polling_booths;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check indexes on wards
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'wards'
ORDER BY indexname;

-- Check indexes on polling_booths
SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'polling_booths'
ORDER BY indexname;

-- Check constraints on wards
SELECT
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'wards'::regclass
ORDER BY conname;

-- Check constraints on polling_booths
SELECT
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'polling_booths'::regclass
ORDER BY conname;

-- ============================================================================
-- PERFORMANCE TEST QUERIES
-- ============================================================================

-- Test ward lookup by code (should use index)
EXPLAIN ANALYZE
SELECT * FROM wards WHERE code = 'TN-AC-001-W-001';

-- Test booth lookup by booth_number (should use index)
EXPLAIN ANALYZE
SELECT * FROM polling_booths WHERE booth_number = '001';

-- Test booth lookup with composite key (should use index)
EXPLAIN ANALYZE
SELECT * FROM polling_booths
WHERE organization_id = '11111111-1111-1111-1111-111111111111'::uuid
  AND constituency_id = (SELECT id FROM constituencies WHERE code = 'TN-AC-001' LIMIT 1)
  AND booth_number = '001';

COMMENT ON TABLE wards IS 'Electoral wards with optimized indexes for bulk operations and fast lookups';
COMMENT ON TABLE polling_booths IS 'Polling booth locations with spatial indexes and data integrity constraints';
