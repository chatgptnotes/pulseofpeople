-- ============================================================================
-- CHECK AND FIX USER DATA
-- Ensure admin@tvk.com has proper organization_id
-- ============================================================================
-- Run this in Supabase SQL Editor
-- ============================================================================

-- 1. Check current user data
SELECT
    id,
    email,
    full_name,
    role,
    organization_id,
    is_active
FROM users
WHERE email = 'admin@tvk.com';

-- 2. Check organizations table
SELECT id, name, slug FROM organizations;

-- 3. If user doesn't have organization_id, update it
-- First, get the organization ID (replace with your actual org ID from step 2)
DO $$
DECLARE
    v_org_id UUID;
    v_user_id UUID;
BEGIN
    -- Get first organization ID
    SELECT id INTO v_org_id FROM organizations LIMIT 1;

    -- Get user ID for admin@tvk.com
    SELECT id INTO v_user_id FROM users WHERE email = 'admin@tvk.com';

    -- Update user with organization_id if it's null
    IF v_user_id IS NOT NULL AND v_org_id IS NOT NULL THEN
        UPDATE users
        SET organization_id = v_org_id,
            role = 'admin',
            is_active = true
        WHERE email = 'admin@tvk.com';

        RAISE NOTICE 'User updated successfully!';
        RAISE NOTICE 'User ID: %', v_user_id;
        RAISE NOTICE 'Organization ID: %', v_org_id;
    ELSE
        RAISE NOTICE 'User or Organization not found!';
    END IF;
END $$;

-- 4. Verify the update
SELECT
    u.id,
    u.email,
    u.full_name,
    u.role,
    u.organization_id,
    o.name as organization_name,
    u.is_active
FROM users u
LEFT JOIN organizations o ON u.organization_id = o.id
WHERE u.email = 'admin@tvk.com';

.