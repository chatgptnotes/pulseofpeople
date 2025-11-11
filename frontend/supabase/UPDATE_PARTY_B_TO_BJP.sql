-- =====================================================
-- Update Party B to BJP (Bharatiya Janata Party)
-- =====================================================

-- First, fix the RLS policies (from previous fix)
DROP POLICY IF EXISTS tenants_view_policy ON tenants;
DROP POLICY IF EXISTS tenants_manage_policy ON tenants;
DROP POLICY IF EXISTS tenants_access_policy ON tenants;

CREATE POLICY tenants_public_read ON tenants
    FOR SELECT
    USING (true);

-- Update Organization for BJP
UPDATE organizations
SET
  name = 'BJP Kerala',
  display_name = 'Bharatiya Janata Party - Kerala',
  description = 'BJP Kerala State Unit - Empowering Kerala with Development and Good Governance',
  contact_email = 'admin@bjp-kerala.com',
  metadata = jsonb_build_object(
    'type', 'political_party',
    'state', 'Kerala',
    'established', '1980',
    'color_theme', 'saffron',
    'symbol', 'lotus',
    'slogan', 'Sabka Saath, Sabka Vikas, Sabka Vishwas',
    'website', 'https://bjp.org'
  )
WHERE name = 'Party B Kerala';

-- Update Tenant for BJP with proper branding
UPDATE tenants
SET
  slug = 'bjp-kerala',
  name = 'BJP Kerala Campaign 2026',
  display_name = 'BJP Kerala',
  subdomain = 'party-b',
  branding = jsonb_build_object(
    'primaryColor', '#FF9933',  -- Saffron color
    'secondaryColor', '#FF6B00', -- Darker saffron
    'accentColor', '#FFA500',    -- Orange accent
    'backgroundColor', '#FFF5F0', -- Light saffron background
    'logo', '/assets/images/bjp-logo.png',
    'favicon', '/assets/images/bjp-favicon.ico',
    'font', 'Inter',
    'theme', 'saffron',
    'heroTitle', 'BJP Kerala - Building a Stronger Tomorrow',
    'heroSubtitle', 'Empowering Every Citizen with Development & Good Governance',
    'heroDescription', 'Join the movement for a prosperous Kerala. Together, we build a state that leads in development, preserves culture, and ensures welfare for all.',
    'motto', 'Sabka Saath, Sabka Vikas, Sabka Vishwas, Sabka Prayas',
    'features', ARRAY[
      'Digital Governance',
      'Youth Empowerment',
      'Women Leadership',
      'Infrastructure Development',
      'Cultural Heritage',
      'Economic Growth'
    ]
  ),
  config = jsonb_build_object(
    'state', 'Kerala',
    'districts', ARRAY['Thiruvananthapuram', 'Kollam', 'Pathanamthitta', 'Alappuzha', 'Kottayam', 'Idukki', 'Ernakulam', 'Thrissur', 'Palakkad', 'Malappuram', 'Kozhikode', 'Wayanad', 'Kannur', 'Kasaragod'],
    'coverageArea', 'Entire Kerala State',
    'wardCount', 1500,
    'expectedUsers', 500,
    'timezone', 'Asia/Kolkata',
    'language', 'en',
    'currency', 'INR',
    'partySymbol', 'lotus',
    'electionSymbol', '🪷'
  ),
  features = jsonb_build_object(
    'analytics', true,
    'surveys', true,
    'fieldReports', true,
    'socialMedia', true,
    'aiInsights', true,
    'voterDatabase', true,
    'bulkSMS', true,
    'whatsappIntegration', true,
    'advancedReporting', true,
    'customBranding', true,
    'digitalCampaigning', true,
    'boothManagement', true
  ),
  metadata = jsonb_build_object(
    'onboardingCompleted', true,
    'dataImported', false,
    'teamSize', 'large',
    'electionDate', '2026-04-01',
    'partyAffiliation', 'BJP',
    'nationalParty', true,
    'founded', '1980-04-06',
    'headquarters', 'New Delhi',
    'president', 'JP Nadda',
    'statePresident', 'K Surendran'
  )
WHERE slug = 'party-b-kerala';

-- Update user to BJP admin
UPDATE users
SET
  name = 'BJP Kerala Admin',
  metadata = jsonb_build_object(
    'onboarded', true,
    'role_title', 'State Campaign Administrator',
    'department', 'BJP Kerala IT Cell',
    'designation', 'Digital Campaign Manager'
  )
WHERE email = 'admin@party-b.com';

-- Create some BJP-specific constituencies
DELETE FROM constituencies WHERE tenant_id = (SELECT id FROM tenants WHERE subdomain = 'party-b');

WITH bjp_tenant AS (
  SELECT id FROM tenants WHERE subdomain = 'party-b'
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
  bjp_tenant.id,
  constituency_name,
  'Kerala',
  district,
  voter_count,
  jsonb_build_object(
    'urban_percentage', urban_pct,
    'rural_percentage', rural_pct,
    'age_groups', jsonb_build_object(
      '18-30', 35,
      '31-45', 30,
      '46-60', 25,
      '60+', 10
    ),
    'bjp_support_estimate', support_est
  ),
  'active',
  NOW(),
  NOW()
FROM bjp_tenant,
LATERAL (VALUES
  ('Thiruvananthapuram', 'Thiruvananthapuram', 195000, 70, 30, '28%'),
  ('Nemom', 'Thiruvananthapuram', 185000, 65, 35, '45%'),
  ('Palakkad', 'Palakkad', 190000, 60, 40, '35%'),
  ('Manjeshwar', 'Kasaragod', 175000, 55, 45, '42%'),
  ('Thrissur', 'Thrissur', 200000, 75, 25, '32%')
) AS t(constituency_name, district, voter_count, urban_pct, rural_pct, support_est);

-- Verify the update
SELECT
  t.subdomain,
  t.name,
  t.display_name,
  t.branding->>'primaryColor' as primary_color,
  t.branding->>'heroTitle' as hero_title,
  o.name as org_name
FROM tenants t
JOIN organizations o ON t.organization_id = o.id
WHERE t.subdomain = 'party-b';