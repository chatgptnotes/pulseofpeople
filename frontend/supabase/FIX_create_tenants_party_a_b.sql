-- =====================================================
-- FIX: Create Tenants for Party A and Party B
-- =====================================================
-- This version handles the missing metadata column in users table

-- =====================================================
-- Step 0: Add metadata column to users table if missing
-- =====================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'metadata') THEN
        ALTER TABLE users ADD COLUMN metadata JSONB DEFAULT '{}'::JSONB;
    END IF;
END $$;

-- Also ensure organization_id exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'users' AND column_name = 'organization_id') THEN
        ALTER TABLE users ADD COLUMN organization_id UUID REFERENCES organizations(id);
    END IF;
END $$;

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
  null,
  jsonb_build_object(
    'primaryColor', '#1e40af',
    'secondaryColor', '#3b82f6',
    'accentColor', '#60a5fa',
    'logo', '/assets/images/logo.png',
    'favicon', '/favicon.ico',
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
  null,
  jsonb_build_object(
    'primaryColor', '#dc2626',
    'secondaryColor', '#ef4444',
    'accentColor', '#f87171',
    'logo', '/assets/images/logo.png',
    'favicon', '/favicon.ico',
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

-- IMPORTANT: First create auth users in Supabase Dashboard, then run this

-- Note: We'll insert users without specifying the ID initially
-- The actual auth user IDs will be linked later

-- Create admin for Party A
INSERT INTO public.users (
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
  permissions = EXCLUDED.permissions,
  metadata = EXCLUDED.metadata;

-- Create admin for Party B
INSERT INTO public.users (
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
  permissions = EXCLUDED.permissions,
  metadata = EXCLUDED.metadata;

-- =====================================================
-- Step 4: Create Sample Constituencies for Testing
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
) AS t(constituency_name, district, voter_count)
ON CONFLICT DO NOTHING;

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
) AS t(constituency_name, district, voter_count)
ON CONFLICT DO NOTHING;

-- =====================================================
-- Step 5: Verification Queries
-- =====================================================

-- Check organizations created
SELECT name, display_name, status FROM organizations
WHERE name IN ('Party A Kerala', 'Party B Kerala');

-- Check tenants created
SELECT slug, name, subdomain, status, subscription_tier
FROM tenants
WHERE slug IN ('party-a-kerala', 'party-b-kerala');

-- Check users created
SELECT email, name, role, tenant_id
FROM users
WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

-- Check constituencies created (should show count by tenant)
SELECT t.name as tenant_name, COUNT(c.id) as constituency_count
FROM constituencies c
JOIN tenants t ON c.tenant_id = t.id
GROUP BY t.name;

-- =====================================================
-- IMPORTANT: After running this script
-- =====================================================

-- 1. Create auth users in Supabase Dashboard:
--    - admin@party-a.com with password: SecurePassword123!
--    - admin@party-b.com with password: SecurePassword123!

-- 2. Link auth users to profiles by updating the ID:
--    UPDATE users SET id = (SELECT id FROM auth.users WHERE auth.users.email = users.email)
--    WHERE email IN ('admin@party-a.com', 'admin@party-b.com');

-- 3. Test login:
--    - Party A: http://party-a.localhost:5173
--    - Party B: http://party-b.localhost:5173