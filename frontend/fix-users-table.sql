-- =====================================================
-- FIX USERS TABLE - Add missing columns
-- =====================================================

-- Add missing columns to users table if they don't exist
DO $$
BEGIN
    -- Add is_super_admin column
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'is_super_admin'
    ) THEN
        ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added is_super_admin column';
    END IF;

    -- Add full_name column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'full_name'
    ) THEN
        ALTER TABLE users ADD COLUMN full_name TEXT;
        RAISE NOTICE 'Added full_name column';
    END IF;

    -- Add name column if it doesn't exist (fallback)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'name'
    ) THEN
        ALTER TABLE users ADD COLUMN name TEXT;
        RAISE NOTICE 'Added name column';
    END IF;

    -- Add role column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'role'
    ) THEN
        ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';
        RAISE NOTICE 'Added role column';
    END IF;

    -- Add status column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'status'
    ) THEN
        ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active';
        RAISE NOTICE 'Added status column';
    END IF;

    -- Add permissions column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'permissions'
    ) THEN
        ALTER TABLE users ADD COLUMN permissions TEXT[] DEFAULT ARRAY[]::TEXT[];
        RAISE NOTICE 'Added permissions column';
    END IF;

    -- Add organization_id column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'organization_id'
    ) THEN
        ALTER TABLE users ADD COLUMN organization_id UUID;
        RAISE NOTICE 'Added organization_id column';
    END IF;

    -- Add tenant_id column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'tenant_id'
    ) THEN
        ALTER TABLE users ADD COLUMN tenant_id UUID;
        RAISE NOTICE 'Added tenant_id column';
    END IF;

    -- Add constituency column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'constituency'
    ) THEN
        ALTER TABLE users ADD COLUMN constituency TEXT;
        RAISE NOTICE 'Added constituency column';
    END IF;

    -- Add ward column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'ward'
    ) THEN
        ALTER TABLE users ADD COLUMN ward TEXT;
        RAISE NOTICE 'Added ward column';
    END IF;

    -- Add state column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'state'
    ) THEN
        ALTER TABLE users ADD COLUMN state TEXT;
        RAISE NOTICE 'Added state column';
    END IF;

    -- Add district column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'district'
    ) THEN
        ALTER TABLE users ADD COLUMN district TEXT;
        RAISE NOTICE 'Added district column';
    END IF;

    -- Add avatar_url column if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'avatar_url'
    ) THEN
        ALTER TABLE users ADD COLUMN avatar_url TEXT;
        RAISE NOTICE 'Added avatar_url column';
    END IF;

END $$;

-- Insert superadmin user
INSERT INTO users (
    email,
    full_name,
    name,
    role,
    is_super_admin,
    status,
    permissions,
    constituency,
    state,
    created_at,
    updated_at
)
VALUES (
    'admin@tvk.com',
    'TVK Super Admin',
    'TVK Super Admin',
    'superadmin',
    TRUE,
    'active',
    ARRAY['*']::TEXT[],
    'All',
    'All States',
    NOW(),
    NOW()
)
ON CONFLICT (email)
DO UPDATE SET
    full_name = EXCLUDED.full_name,
    name = EXCLUDED.name,
    role = 'superadmin',
    is_super_admin = TRUE,
    status = 'active',
    permissions = ARRAY['*']::TEXT[],
    updated_at = NOW();

-- Insert test user
INSERT INTO users (
    email,
    full_name,
    name,
    role,
    is_super_admin,
    status,
    permissions,
    created_at,
    updated_at
)
VALUES (
    'user@tvk.com',
    'Field Worker',
    'Field Worker',
    'user',
    FALSE,
    'active',
    ARRAY['view_dashboard', 'submit_data']::TEXT[],
    NOW(),
    NOW()
)
ON CONFLICT (email)
DO UPDATE SET
    full_name = EXCLUDED.full_name,
    name = EXCLUDED.name,
    role = 'user',
    status = 'active',
    updated_at = NOW();

-- Verify users were created
SELECT
    id,
    email,
    full_name,
    name,
    role,
    is_super_admin,
    status
FROM users
WHERE email IN ('admin@tvk.com', 'user@tvk.com')
ORDER BY is_super_admin DESC;
