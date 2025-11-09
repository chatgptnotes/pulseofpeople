-- ============================================================================
-- OPTIMIZATION MIGRATION: Wards and Polling Booths Indexes
-- ============================================================================
-- Created: 2025-11-09 16:00:00
-- Purpose: Add performance indexes and constraints for bulk operations
-- Fixed: Removed IF NOT EXISTS from constraints (not supported in PostgreSQL)
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

-- Add constraints for positive values (using DO block to handle duplicates)
DO $$
BEGIN
    -- Wards constraints
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'wards_population_positive') THEN
        ALTER TABLE wards ADD CONSTRAINT wards_population_positive CHECK (population IS NULL OR population >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'wards_voter_count_positive') THEN
        ALTER TABLE wards ADD CONSTRAINT wards_voter_count_positive CHECK (voter_count >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'wards_total_booths_positive') THEN
        ALTER TABLE wards ADD CONSTRAINT wards_total_booths_positive CHECK (total_booths >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'wards_literacy_rate_valid') THEN
        ALTER TABLE wards ADD CONSTRAINT wards_literacy_rate_valid CHECK (literacy_rate IS NULL OR (literacy_rate >= 0 AND literacy_rate <= 100));
    END IF;
END $$;

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

-- Index for filtering by accessibility
CREATE INDEX IF NOT EXISTS idx_booths_accessible ON polling_booths(is_accessible) WHERE is_accessible = true;

-- Add constraints for data integrity (using DO block)
DO $$
BEGIN
    -- Polling booths voter count constraints
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_total_voters_positive') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_total_voters_positive CHECK (total_voters >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_male_voters_positive') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_male_voters_positive CHECK (male_voters >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_female_voters_positive') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_female_voters_positive CHECK (female_voters >= 0);
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_transgender_voters_positive') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_transgender_voters_positive CHECK (transgender_voters >= 0);
    END IF;

    -- Gender sum validation
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_gender_sum_valid') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_gender_sum_valid
        CHECK (male_voters + female_voters + transgender_voters <= total_voters);
    END IF;

    -- GPS coordinate validation
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_latitude_valid') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_latitude_valid
        CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90));
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_longitude_valid') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_longitude_valid
        CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180));
    END IF;

    -- Priority level validation
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'booths_priority_valid') THEN
        ALTER TABLE polling_booths ADD CONSTRAINT booths_priority_valid
        CHECK (priority_level IS NULL OR (priority_level >= 1 AND priority_level <= 5));
    END IF;
END $$;

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
-- SUMMARY
-- ============================================================================

DO $$
DECLARE
    ward_index_count INT;
    booth_index_count INT;
    ward_constraint_count INT;
    booth_constraint_count INT;
BEGIN
    SELECT COUNT(*) INTO ward_index_count FROM pg_indexes WHERE tablename = 'wards';
    SELECT COUNT(*) INTO booth_index_count FROM pg_indexes WHERE tablename = 'polling_booths';
    SELECT COUNT(*) INTO ward_constraint_count FROM pg_constraint WHERE conrelid = 'wards'::regclass;
    SELECT COUNT(*) INTO booth_constraint_count FROM pg_constraint WHERE conrelid = 'polling_booths'::regclass;

    RAISE NOTICE '✅ Migration completed successfully!';
    RAISE NOTICE '📊 Wards table: % indexes, % constraints', ward_index_count, ward_constraint_count;
    RAISE NOTICE '📊 Polling booths table: % indexes, % constraints', booth_index_count, booth_constraint_count;
END $$;
