-- =====================================================
-- Link Auth Users to User Profiles
-- =====================================================
-- This script properly links Supabase auth users to user profiles

-- Step 1: First, check if auth users exist
SELECT email, id, created_at
FROM auth.users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

-- Step 2: Delete existing user profiles (they have wrong IDs)
DELETE FROM users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

-- Step 3: Re-insert users with correct auth IDs
-- For Party A Admin
INSERT INTO public.users (
  id,  -- Now using the actual auth user ID
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
  auth.users.id,  -- Get the actual auth user ID
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
  t.id as tenant_id,
  t.organization_id,
  'active',
  jsonb_build_object(
    'onboarded', true,
    'role_title', 'Campaign Administrator',
    'department', 'Campaign Management'
  )
FROM tenants t
CROSS JOIN auth.users
WHERE t.slug = 'party-a-kerala'
AND auth.users.email = 'admin@party-a.com';

-- For Party B Admin
INSERT INTO public.users (
  id,  -- Now using the actual auth user ID
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
  auth.users.id,  -- Get the actual auth user ID
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
  t.id as tenant_id,
  t.organization_id,
  'active',
  jsonb_build_object(
    'onboarded', true,
    'role_title', 'Campaign Administrator',
    'department', 'Campaign Management'
  )
FROM tenants t
CROSS JOIN auth.users
WHERE t.slug = 'party-b-kerala'
AND auth.users.email = 'admin@party-b.com';

-- Step 4: Verify the linkage
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
LEFT JOIN tenants t ON u.tenant_id = t.id
LEFT JOIN organizations o ON u.organization_id = o.id
WHERE u.email IN ('admin@party-a.com', 'admin@party-b.com');

-- Step 5: Test the helper function
SELECT
  email,
  get_user_tenant_id() as detected_tenant_id,
  tenant_id as actual_tenant_id
FROM users
WHERE id = auth.uid();

-- =====================================================
-- If the above doesn't work, try this alternative:
-- =====================================================

-- Alternative: Create a function to properly link users
CREATE OR REPLACE FUNCTION link_auth_users()
RETURNS void AS $$
DECLARE
  v_auth_id_a UUID;
  v_auth_id_b UUID;
  v_tenant_id_a UUID;
  v_tenant_id_b UUID;
BEGIN
  -- Get auth user IDs
  SELECT id INTO v_auth_id_a FROM auth.users WHERE email = 'admin@party-a.com';
  SELECT id INTO v_auth_id_b FROM auth.users WHERE email = 'admin@party-b.com';

  -- Get tenant IDs
  SELECT id INTO v_tenant_id_a FROM tenants WHERE slug = 'party-a-kerala';
  SELECT id INTO v_tenant_id_b FROM tenants WHERE slug = 'party-b-kerala';

  -- Delete existing records
  DELETE FROM users WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

  -- Insert with correct IDs
  IF v_auth_id_a IS NOT NULL AND v_tenant_id_a IS NOT NULL THEN
    INSERT INTO users (id, email, name, role, permissions, tenant_id, organization_id, status, metadata)
    SELECT
      v_auth_id_a,
      'admin@party-a.com',
      'Party A Admin',
      'admin',
      ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing'],
      v_tenant_id_a,
      organization_id,
      'active',
      jsonb_build_object('onboarded', true, 'role_title', 'Campaign Administrator')
    FROM tenants WHERE id = v_tenant_id_a;

    RAISE NOTICE 'Linked Party A admin: %', v_auth_id_a;
  ELSE
    RAISE NOTICE 'Party A admin auth user not found or tenant not found';
  END IF;

  IF v_auth_id_b IS NOT NULL AND v_tenant_id_b IS NOT NULL THEN
    INSERT INTO users (id, email, name, role, permissions, tenant_id, organization_id, status, metadata)
    SELECT
      v_auth_id_b,
      'admin@party-b.com',
      'Party B Admin',
      'admin',
      ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing'],
      v_tenant_id_b,
      organization_id,
      'active',
      jsonb_build_object('onboarded', true, 'role_title', 'Campaign Administrator')
    FROM tenants WHERE id = v_tenant_id_b;

    RAISE NOTICE 'Linked Party B admin: %', v_auth_id_b;
  ELSE
    RAISE NOTICE 'Party B admin auth user not found or tenant not found';
  END IF;
END;
$$ LANGUAGE plpgsql;

-- Call the function
SELECT link_auth_users();

-- Clean up
DROP FUNCTION IF EXISTS link_auth_users();