-- =====================================================
-- Create Tenants for Party A and Party B
-- =====================================================
-- Run this SQL after running the multi-tenant migration
-- Execute in Supabase SQL Editor

-- First, ensure the migration has been run
-- If not, run: 20251029_single_db_multi_tenant.sql first

-- =====================================================
-- Step 1: Create Organizations for Both Parties
-- =====================================================

-- Create Organization for Party A
INSERT INTO public.organizations (
  id,
  name,
  display_name,
  description,
  contact_email,
  contact_phone,
  address,
  status,
  metadata
) VALUES (
  gen_random_uuid(),
  'Party A Kerala',
  'Party A - Kerala Campaign',
  'Political party focused on Kerala state elections 2026',
  'admin@party-a-kerala.com',
  '+91-9876543210',
  'Kerala, India',
  'active',
  jsonb_build_object(
    'type', 'political_party',
    'state', 'Kerala',
    'established', '2024',
    'color_theme', 'blue'
  )
) ON CONFLICT (name) DO NOTHING;

-- Create Organization for Party B
INSERT INTO public.organizations (
  id,
  name,
  display_name,
  description,
  contact_email,
  contact_phone,
  address,
  status,
  metadata
) VALUES (
  gen_random_uuid(),
  'Party B Kerala',
  'Party B - Kerala Campaign',
  'Political party focused on Kerala state elections 2026',
  'admin@party-b-kerala.com',
  '+91-9876543211',
  'Kerala, India',
  'active',
  jsonb_build_object(
    'type', 'political_party',
    'state', 'Kerala',
    'established', '2024',
    'color_theme', 'red'
  )
) ON CONFLICT (name) DO NOTHING;

-- =====================================================
-- Step 2: Create Tenants for Both Parties
-- =====================================================

-- Create Tenant for Party A
WITH org_a AS (
  SELECT id FROM organizations WHERE name = 'Party A Kerala'
)
INSERT INTO public.tenants (
  id,
  organization_id,
  slug,
  name,
  display_name,
  subdomain,
  custom_domain,
  branding,
  config,
  features,
  subscription_tier,
  subscription_status,
  subscription_start_date,
  subscription_end_date,
  monthly_fee,
  status,
  metadata
)
SELECT
  gen_random_uuid(),
  org_a.id,
  'party-a-kerala',
  'Party A Kerala Campaign',
  'Party A Kerala',
  'party-a',
  null, -- No custom domain initially
  jsonb_build_object(
    'primaryColor', '#1e40af',
    'secondaryColor', '#3b82f6',
    'accentColor', '#60a5fa',
    'logo', '/assets/images/party-a-logo.png',
    'favicon', '/assets/images/party-a-favicon.ico',
    'font', 'Inter',
    'theme', 'professional'
  ),
  jsonb_build_object(
    'state', 'Kerala',
    'districts', ARRAY['Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam', 'Idukki', 'Ernakulam'],
    'coverageArea', 'South Kerala',
    'wardCount', 1000,
    'expectedUsers', 200,
    'timezone', 'Asia/Kolkata',
    'language', 'en',
    'currency', 'INR'
  ),
  jsonb_build_object(
    'analytics', true,
    'surveys', true,
    'fieldReports', true,
    'socialMedia', true,
    'aiInsights', true,
    'voterDatabase', true,
    'bulkSMS', true,
    'whatsappIntegration', true,
    'advancedReporting', true,
    'customBranding', true
  ),
  'premium',
  'active',
  CURRENT_DATE,
  CURRENT_DATE + INTERVAL '1 year',
  12000.00,
  'active',
  jsonb_build_object(
    'onboardingCompleted', false,
    'dataImported', false,
    'teamSize', 'medium',
    'electionDate', '2026-04-01'
  )
FROM org_a
ON CONFLICT (slug) DO NOTHING;

-- Create Tenant for Party B
WITH org_b AS (
  SELECT id FROM organizations WHERE name = 'Party B Kerala'
)
INSERT INTO public.tenants (
  id,
  organization_id,
  slug,
  name,
  display_name,
  subdomain,
  custom_domain,
  branding,
  config,
  features,
  subscription_tier,
  subscription_status,
  subscription_start_date,
  subscription_end_date,
  monthly_fee,
  status,
  metadata
)
SELECT
  gen_random_uuid(),
  org_b.id,
  'party-b-kerala',
  'Party B Kerala Campaign',
  'Party B Kerala',
  'party-b',
  null, -- No custom domain initially
  jsonb_build_object(
    'primaryColor', '#dc2626',
    'secondaryColor', '#ef4444',
    'accentColor', '#f87171',
    'logo', '/assets/images/party-b-logo.png',
    'favicon', '/assets/images/party-b-favicon.ico',
    'font', 'Inter',
    'theme', 'bold'
  ),
  jsonb_build_object(
    'state', 'Kerala',
    'districts', ARRAY['Palakkad', 'Malappuram', 'Kozhikode', 'Wayanad', 'Kannur', 'Kasaragod', 'Thrissur'],
    'coverageArea', 'North Kerala',
    'wardCount', 950,
    'expectedUsers', 180,
    'timezone', 'Asia/Kolkata',
    'language', 'en',
    'currency', 'INR'
  ),
  jsonb_build_object(
    'analytics', true,
    'surveys', true,
    'fieldReports', true,
    'socialMedia', true,
    'aiInsights', true,
    'voterDatabase', true,
    'bulkSMS', true,
    'whatsappIntegration', true,
    'advancedReporting', true,
    'customBranding', true
  ),
  'premium',
  'active',
  CURRENT_DATE,
  CURRENT_DATE + INTERVAL '1 year',
  12000.00,
  'active',
  jsonb_build_object(
    'onboardingCompleted', false,
    'dataImported', false,
    'teamSize', 'medium',
    'electionDate', '2026-04-01'
  )
FROM org_b
ON CONFLICT (slug) DO NOTHING;

-- =====================================================
-- Step 3: Create Admin Users for Each Tenant
-- =====================================================

-- Note: First create auth users in Supabase Dashboard, then run this

-- Create admin for Party A
-- Email: admin@party-a.com
-- Password: Set in Supabase Auth Dashboard

-- After creating in Auth, run this to create profile:
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
  auth.uid() as id, -- This will be the actual auth user id
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
WHERE t.slug = 'party-a-kerala'
ON CONFLICT (email) DO UPDATE
SET
  tenant_id = EXCLUDED.tenant_id,
  organization_id = EXCLUDED.organization_id,
  role = EXCLUDED.role,
  permissions = EXCLUDED.permissions;

-- Create admin for Party B
-- Email: admin@party-b.com
-- Password: Set in Supabase Auth Dashboard

-- After creating in Auth, run this to create profile:
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
  auth.uid() as id, -- This will be the actual auth user id
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
WHERE t.slug = 'party-b-kerala'
ON CONFLICT (email) DO UPDATE
SET
  tenant_id = EXCLUDED.tenant_id,
  organization_id = EXCLUDED.organization_id,
  role = EXCLUDED.role,
  permissions = EXCLUDED.permissions;

-- =====================================================
-- Step 4: Create Some Sample Data for Each Tenant
-- =====================================================

-- Sample constituencies for Party A
WITH tenant_a AS (
  SELECT id FROM tenants WHERE slug = 'party-a-kerala'
)
INSERT INTO public.constituencies (
  id,
  tenant_id,
  name,
  state,
  district,
  total_voters,
  demographics,
  status,
  created_at,
  updated_at
)
SELECT
  gen_random_uuid(),
  tenant_a.id,
  constituency_name,
  'Kerala',
  district,
  voter_count,
  jsonb_build_object(
    'urban_percentage', 60,
    'rural_percentage', 40,
    'age_groups', jsonb_build_object(
      '18-30', 35,
      '31-45', 30,
      '46-60', 25,
      '60+', 10
    )
  ),
  'active',
  NOW(),
  NOW()
FROM tenant_a,
LATERAL (VALUES
  ('Thiruvananthapuram Central', 'Thiruvananthapuram', 185000),
  ('Kollam East', 'Kollam', 175000),
  ('Ernakulam North', 'Ernakulam', 195000)
) AS t(constituency_name, district, voter_count);

-- Sample constituencies for Party B
WITH tenant_b AS (
  SELECT id FROM tenants WHERE slug = 'party-b-kerala'
)
INSERT INTO public.constituencies (
  id,
  tenant_id,
  name,
  state,
  district,
  total_voters,
  demographics,
  status,
  created_at,
  updated_at
)
SELECT
  gen_random_uuid(),
  tenant_b.id,
  constituency_name,
  'Kerala',
  district,
  voter_count,
  jsonb_build_object(
    'urban_percentage', 45,
    'rural_percentage', 55,
    'age_groups', jsonb_build_object(
      '18-30', 32,
      '31-45', 28,
      '46-60', 28,
      '60+', 12
    )
  ),
  'active',
  NOW(),
  NOW()
FROM tenant_b,
LATERAL (VALUES
  ('Kozhikode North', 'Kozhikode', 180000),
  ('Kannur Central', 'Kannur', 170000),
  ('Thrissur West', 'Thrissur', 190000)
) AS t(constituency_name, district, voter_count);

-- =====================================================
-- Step 5: Verify Setup
-- =====================================================

-- Check organizations created
SELECT name, display_name, status FROM organizations
WHERE name IN ('Party A Kerala', 'Party B Kerala');

-- Check tenants created
SELECT slug, name, subdomain, status, subscription_tier
FROM tenants
WHERE slug IN ('party-a-kerala', 'party-b-kerala');

-- Check if RLS is working (should only show current tenant's data)
-- This query will be filtered based on the logged-in user's tenant
SELECT COUNT(*) as constituency_count, t.name as tenant_name
FROM constituencies c
JOIN tenants t ON c.tenant_id = t.id
GROUP BY t.name;

-- =====================================================
-- Instructions for Creating Auth Users
-- =====================================================

-- IMPORTANT: Before running the user INSERT statements above,
-- you must create the auth users in Supabase Dashboard:

-- 1. Go to Supabase Dashboard > Authentication > Users
-- 2. Click "Add User" > "Create New User"

-- For Party A Admin:
-- Email: admin@party-a.com
-- Password: SecurePassword123!
-- Auto Confirm Email: Yes

-- For Party B Admin:
-- Email: admin@party-b.com
-- Password: SecurePassword123!
-- Auto Confirm Email: Yes

-- 3. After creating auth users, get their IDs and update the INSERT statements above
-- 4. Or use the auth.uid() function if running while logged in as that user

-- =====================================================
-- Clean Up (if needed)
-- =====================================================

-- To remove test data and start over:
-- DELETE FROM constituencies WHERE tenant_id IN (SELECT id FROM tenants WHERE slug IN ('party-a-kerala', 'party-b-kerala'));
-- DELETE FROM users WHERE email IN ('admin@party-a.com', 'admin@party-b.com');
-- DELETE FROM tenants WHERE slug IN ('party-a-kerala', 'party-b-kerala');
-- DELETE FROM organizations WHERE name IN ('Party A Kerala', 'Party B Kerala');