-- ============================================================================
-- FIX SLOW LOGIN ISSUE - Update RLS Functions to Use JWT Claims
-- ============================================================================
-- This removes the circular reference by reading from JWT instead of
-- querying the users table

-- Backup existing functions (just in case)
-- You can restore these if needed

-- ============================================================================
-- STEP 1: Update get_user_role() to use JWT claims
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS VARCHAR AS $$
DECLARE
    user_role VARCHAR;
BEGIN
    -- Read role from JWT user_metadata instead of querying users table
    -- This eliminates the circular reference
    user_role := COALESCE(
        (auth.jwt() -> 'user_metadata' ->> 'role')::VARCHAR,
        'user'  -- Default fallback
    );

    RETURN user_role;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION public.get_user_role() IS
'Returns user role from JWT claims. No database query = no circular reference.';


-- ============================================================================
-- STEP 2: Update get_user_organization_id() to use JWT claims
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_user_organization_id()
RETURNS UUID AS $$
DECLARE
    org_id UUID;
BEGIN
    -- Read organization_id from JWT user_metadata instead of querying users table
    -- This eliminates the circular reference
    org_id := (auth.jwt() -> 'user_metadata' ->> 'organization_id')::UUID;

    RETURN org_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

COMMENT ON FUNCTION public.get_user_organization_id() IS
'Returns organization ID from JWT claims. No database query = no circular reference.';


-- ============================================================================
-- STEP 3: Verify the functions work correctly
-- ============================================================================

-- Test the functions (run these after creating a test user with metadata)
-- SELECT get_user_role();
-- SELECT get_user_organization_id();


-- ============================================================================
-- NOTES FOR IMPLEMENTATION:
-- ============================================================================

-- 1. Users created via Supabase Auth Admin API must include user_metadata:
--    {
--      "email": "user@example.com",
--      "password": "password",
--      "user_metadata": {
--        "role": "admin",
--        "organization_id": "uuid-here"
--      }
--    }

-- 2. Existing users need to have their JWT updated with metadata
--    Run: backend/update_user_metadata.py (to be created)

-- 3. These functions are marked STABLE which allows PostgreSQL to cache them
--    within a single query, improving performance further

-- 4. The SECURITY DEFINER means the function runs with the privileges of the
--    user who created it (typically superuser), allowing it to bypass RLS

-- ============================================================================
-- ROLLBACK (if needed):
-- ============================================================================

-- If you need to rollback to the old version that queries the database:
-- (Don't run this unless you need to rollback)

/*
CREATE OR REPLACE FUNCTION public.get_user_role()
RETURNS VARCHAR AS $$
BEGIN
    RETURN (
        SELECT role
        FROM users
        WHERE id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION public.get_user_organization_id()
RETURNS UUID AS $$
BEGIN
    RETURN (
        SELECT organization_id
        FROM users
        WHERE id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
*/
