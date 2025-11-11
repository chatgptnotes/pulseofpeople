-- ============================================================================
-- CLEAN FIX: Replace broken PostGIS function
-- ============================================================================
-- This replaces the function that's causing import errors
-- ============================================================================

-- Replace the broken function with a working no-op version
CREATE OR REPLACE FUNCTION sync_geography_from_boundaries()
RETURNS TRIGGER AS $$
BEGIN
    -- Temporarily disabled - PostGIS not configured
    -- Just return NEW without processing geom column
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Verify the function was created
SELECT
    'Function created successfully' as status,
    proname as function_name,
    pg_get_function_identity_arguments(oid) as arguments
FROM pg_proc
WHERE proname = 'sync_geography_from_boundaries';
