-- ============================================================================
-- MINIMAL FIX: Just fix the broken function
-- ============================================================================
-- Simplest possible fix - just replace the broken function
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

-- That's it! The function now exists and won't error
-- The trigger can fire but the function does nothing

SELECT '✅ Fix applied - you can now import constituencies!' as status;
