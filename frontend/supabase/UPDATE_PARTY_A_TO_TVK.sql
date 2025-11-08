-- =============================================================================
-- Update party-a Tenant to TVK (Tamilaga Vettri Kazhagam)
-- =============================================================================
-- This script updates the party-a tenant with TVK branding and configuration
-- Run this after setting up the multi-tenant database schema

-- Step 1: Update organization for party-a to TVK
UPDATE organizations
SET
    name = 'TVK Tamil Nadu',
    display_name = 'Tamilaga Vettri Kazhagam',
    slug = 'org-party-a',
    metadata = jsonb_build_object(
        'party_name', 'Tamilaga Vettri Kazhagam',
        'abbreviation', 'TVK',
        'founded', '2024-02-02',
        'leader', 'Vijay',
        'headquarters', 'Chennai, Tamil Nadu',
        'party_type', 'Regional',
        'election_symbol', 'Rising Sun',
        'target_election', '2026 Tamil Nadu Assembly',
        'motto', 'Pirappokkum Ella Uyirkkum'
    ),
    updated_at = NOW()
WHERE slug = 'org-party-a';

-- Step 2: Update tenant configuration with TVK branding
UPDATE tenants
SET
    name = 'TVK Tamil Nadu Campaign 2026',
    display_name = 'TVK - Tamilaga Vettri Kazhagam',
    subdomain = 'party-a',
    slug = 'tvk-tamil-nadu',
    branding = jsonb_build_object(
        'primaryColor', '#dc2626',      -- Red
        'secondaryColor', '#fbbf24',     -- Yellow/Gold
        'accent', '#f59e0b',             -- Amber
        'background', '#fef3c7',         -- Light Yellow
        'logo', '/assets/images/tvk-logo.png',
        'theme', 'red-yellow',
        'heroTitle', 'TVK - Building Progressive Tamil Nadu',
        'motto', 'Pirappokkum Ella Uyirkkum - All Lives are Equal by Birth',
        'tagline', 'Victory for Tamil Nadu',
        'fonts', jsonb_build_object(
            'heading', 'Roboto, Tamil Sangam MN, sans-serif',
            'body', 'Open Sans, Noto Sans Tamil, sans-serif'
        )
    ),
    features = jsonb_build_object(
        'analytics', true,
        'surveys', true,
        'fieldReports', true,
        'socialMedia', true,
        'volunteerManagement', true,
        'boothManagement', true,
        'digitalCampaigning', true,
        'youthEngagement', true,
        'educationInitiatives', true,
        'socialJusticeTracking', true
    ),
    config = jsonb_build_object(
        'state', 'Tamil Nadu',
        'language', 'Tamil',
        'secondaryLanguage', 'English',
        'totalDistricts', 38,
        'totalConstituencies', 234,
        'targetYear', '2026',
        'partySymbol', 'rising-sun',
        'focusAreas', jsonb_build_array(
            'Youth Empowerment',
            'Education Revolution',
            'Healthcare for All',
            'Farmer Welfare',
            'Industrial Growth',
            'Clean Governance'
        ),
        'keyInitiatives', jsonb_build_array(
            'Free Quality Education',
            '10 Lakh Jobs Creation',
            'Startup Ecosystem',
            'Universal Healthcare',
            'Direct Farmer Procurement',
            'Zero Corruption'
        )
    ),
    metadata = jsonb_build_object(
        'partyAffiliation', 'TVK',
        'regionalParty', true,
        'nationalPresence', false,
        'founded', '2024-02-02',
        'founder', 'Vijay',
        'statePresident', 'Vijay',
        'totalMembers', '100000+',
        'youthWing', 'TVK Youth Force',
        'womenWing', 'TVK Womens Wing',
        'socialMedia', jsonb_build_object(
            'twitter', '@TVKOfficial',
            'facebook', 'TVKTamilNadu',
            'instagram', 'tvk_official',
            'youtube', 'TVKChannel'
        ),
        'electionHistory', jsonb_build_array(
            jsonb_build_object(
                'year', '2026',
                'type', 'Assembly',
                'status', 'Upcoming',
                'target', 'Form Government'
            )
        )
    ),
    updated_at = NOW()
WHERE subdomain = 'party-a';

-- Step 3: Create TVK-specific constituencies in Tamil Nadu
INSERT INTO constituencies (id, tenant_id, name, state, metadata, created_at, updated_at)
VALUES
    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Chennai Central', 'Tamil Nadu',
     '{"district": "Chennai", "voters": 250000, "urbanRural": "Urban", "tvkSupport": "45%", "keyIssues": ["Employment", "Infrastructure", "Education"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Coimbatore South', 'Tamil Nadu',
     '{"district": "Coimbatore", "voters": 225000, "urbanRural": "Urban", "tvkSupport": "48%", "keyIssues": ["Industrial Development", "Youth Employment", "Healthcare"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Madurai Central', 'Tamil Nadu',
     '{"district": "Madurai", "voters": 210000, "urbanRural": "Urban", "tvkSupport": "42%", "keyIssues": ["Water Scarcity", "Healthcare", "Education"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Tiruchirappalli West', 'Tamil Nadu',
     '{"district": "Tiruchirappalli", "voters": 195000, "urbanRural": "Semi-Urban", "tvkSupport": "40%", "keyIssues": ["Agriculture", "Employment", "Infrastructure"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Salem West', 'Tamil Nadu',
     '{"district": "Salem", "voters": 185000, "urbanRural": "Semi-Urban", "tvkSupport": "38%", "keyIssues": ["Industrial Growth", "Education", "Healthcare"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Tirunelveli', 'Tamil Nadu',
     '{"district": "Tirunelveli", "voters": 175000, "urbanRural": "Semi-Urban", "tvkSupport": "35%", "keyIssues": ["Agriculture", "Water Management", "Employment"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Erode East', 'Tamil Nadu',
     '{"district": "Erode", "voters": 180000, "urbanRural": "Semi-Urban", "tvkSupport": "41%", "keyIssues": ["Textile Industry", "Employment", "Education"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Vellore', 'Tamil Nadu',
     '{"district": "Vellore", "voters": 190000, "urbanRural": "Semi-Urban", "tvkSupport": "37%", "keyIssues": ["Healthcare", "Education", "Infrastructure"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Thoothukudi', 'Tamil Nadu',
     '{"district": "Thoothukudi", "voters": 170000, "urbanRural": "Semi-Urban", "tvkSupport": "39%", "keyIssues": ["Port Development", "Fishing Industry", "Environment"]}', NOW(), NOW()),

    (gen_random_uuid(), (SELECT id FROM tenants WHERE subdomain = 'party-a'), 'Thanjavur', 'Tamil Nadu',
     '{"district": "Thanjavur", "voters": 165000, "urbanRural": "Rural", "tvkSupport": "36%", "keyIssues": ["Agriculture", "Water Resources", "Rural Development"]}', NOW(), NOW())
ON CONFLICT DO NOTHING;

-- Step 4: Create sample volunteer data for TVK
INSERT INTO users (id, email, username, role, metadata, created_at, updated_at, tenant_id)
SELECT
    gen_random_uuid(),
    'volunteer' || generate_series || '@tvk.org',
    'tvk_volunteer_' || generate_series,
    'user',
    jsonb_build_object(
        'designation', CASE
            WHEN generate_series <= 3 THEN 'District Coordinator'
            WHEN generate_series <= 10 THEN 'Constituency Manager'
            ELSE 'Field Volunteer'
        END,
        'district', (ARRAY['Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Erode'])[1 + (generate_series % 5)],
        'joinedDate', '2024-' || LPAD((2 + (generate_series % 10))::text, 2, '0') || '-' || LPAD((1 + (generate_series % 28))::text, 2, '0')
    ),
    NOW(),
    NOW(),
    (SELECT id FROM tenants WHERE subdomain = 'party-a')
FROM generate_series(1, 20)
ON CONFLICT DO NOTHING;

-- Step 5: Verify the updates
SELECT
    t.subdomain,
    t.display_name,
    t.branding->>'primaryColor' as primary_color,
    t.branding->>'theme' as theme,
    t.config->>'state' as state,
    o.name as org_name
FROM tenants t
JOIN organizations o ON o.id = t.organization_id
WHERE t.subdomain = 'party-a';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'TVK configuration successfully applied to party-a tenant!';
    RAISE NOTICE 'Access the TVK landing page at: http://party-a.localhost:5173';
END $$;