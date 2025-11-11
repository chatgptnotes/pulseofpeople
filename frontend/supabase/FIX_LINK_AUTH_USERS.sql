-- =====================================================
-- FIX: Link Auth Users to User Profiles
-- =====================================================
-- This version handles the type mismatch between tenant_id columns

-- Step 1: Check column types
SELECT
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_name = 'users'
AND column_name IN ('id', 'tenant_id', 'organization_id');

SELECT
    column_name,
    data_type,
    udt_name
FROM information_schema.columns
WHERE table_name = 'tenants'
AND column_name = 'id';

-- Step 2: Fix tenant_id column type if needed
DO $$
BEGIN
    -- Check if tenant_id is TEXT and needs to be UUID
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users'
        AND column_name = 'tenant_id'
        AND data_type = 'text'
    ) THEN
        -- First, drop the existing column
        ALTER TABLE users DROP COLUMN IF EXISTS tenant_id;
        -- Add it back as UUID
        ALTER TABLE users ADD COLUMN tenant_id UUID REFERENCES tenants(id);
    END IF;
END $$;

-- Step 3: Check if auth users exist
SELECT email, id, created_at
FROM auth.users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

-- Step 4: Delete existing user profiles (they have wrong IDs)
DELETE FROM users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

-- Step 5: Re-insert users with correct auth IDs
-- For Party A Admin
INSERT INTO public.users (
  id,
  email,
  name,
  role,
  permissions,
  tenant_id,
  organization_id,
  status,
  metadata
)
SELECT
  auth.users.id,
  'admin@party-a.com',
  'Party A Admin',
  'admin',
  ARRAY[
    'view_all',
    'edit_all',
    'manage_users',
    'export_data',
    'verify_submissions',
    'edit_settings',
    'manage_billing'
  ],
  t.id,  -- Now both are UUID
  t.organization_id,
  'active',
  jsonb_build_object(
    'onboarded', true,
    'role_title', 'Campaign Administrator',
    'department', 'Campaign Management'
  )::jsonb
FROM tenants t
CROSS JOIN auth.users
WHERE t.slug = 'party-a-kerala'
AND auth.users.email = 'admin@party-a.com';

-- For Party B Admin
INSERT INTO public.users (
  id,
  email,
  name,
  role,
  permissions,
  tenant_id,
  organization_id,
  status,
  metadata
)
SELECT
  auth.users.id,
  'admin@party-b.com',
  'Party B Admin',
  'admin',
  ARRAY[
    'view_all',
    'edit_all',
    'manage_users',
    'export_data',
    'verify_submissions',
    'edit_settings',
    'manage_billing'
  ],
  t.id,  -- Now both are UUID
  t.organization_id,
  'active',
  jsonb_build_object(
    'onboarded', true,
    'role_title', 'Campaign Administrator',
    'department', 'Campaign Management'
  )::jsonb
FROM tenants t
CROSS JOIN auth.users
WHERE t.slug = 'party-b-kerala'
AND auth.users.email = 'admin@party-b.com';

-- Step 6: Verify the linkage (with proper type casting)
SELECT
  u.email,
  u.name,
  u.role,
  t.name as tenant_name,
  t.subdomain,
  o.name as organization_name,
  CASE
    WHEN u.id IN (SELECT id FROM auth.users WHERE email = u.email)
    THEN '✓ Linked to Auth'
    ELSE '✗ Not Linked'
  END as auth_status
FROM users u
LEFT JOIN tenants t ON u.tenant_id = t.id  -- Both should be UUID now
LEFT JOIN organizations o ON u.organization_id = o.id
WHERE u.email IN ('admin@party-a.com', 'admin@party-b.com');

-- Step 7: Update the helper function to handle UUID
CREATE OR REPLACE FUNCTION get_user_tenant_id()
RETURNS UUID AS $$  -- Changed from TEXT to UUID
BEGIN
    RETURN (SELECT tenant_id FROM users WHERE id = auth.uid());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Step 8: Final verification
SELECT
  'Organizations' as component,
  COUNT(*) as count
FROM organizations
WHERE name IN ('Party A Kerala', 'Party B Kerala')
UNION ALL
SELECT
  'Tenants',
  COUNT(*)
FROM tenants
WHERE slug IN ('party-a-kerala', 'party-b-kerala')
UNION ALL
SELECT
  'Users',
  COUNT(*)
FROM users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com')
UNION ALL
SELECT
  'Auth Users',
  COUNT(*)
FROM auth.users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

-- =====================================================
-- TROUBLESHOOTING SECTION
-- =====================================================

-- If you still have issues, run these diagnostics:

-- Check all tenant_id columns across tables
SELECT
    t.table_name,
    c.column_name,
    c.data_type,
    c.udt_name
FROM information_schema.tables t
JOIN information_schema.columns c ON t.table_name = c.table_name
WHERE c.column_name = 'tenant_id'
AND t.table_schema = 'public'
ORDER BY t.table_name;

-- Check if users are properly linked
SELECT
    u.id as user_id,
    u.email,
    u.tenant_id,
    au.id as auth_id,
    au.email as auth_email,
    CASE WHEN u.id = au.id THEN '✓ Matched' ELSE '✗ Mismatch' END as status
FROM users u
FULL OUTER JOIN auth.users au ON u.email = au.email
WHERE u.email IN ('admin@party-a.com', 'admin@party-b.com')
   OR au.email IN ('admin@party-a.com', 'admin@party-b.com');