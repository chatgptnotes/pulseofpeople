-- ============================================================================
-- Migration: Update Primary Organization to TVK (Tamilaga Vettri Kazhagam)
-- Date: 2025-11-09
-- Description: Updates the main organization from placeholder to TVK
-- ============================================================================

-- Update primary organization to TVK
UPDATE organizations
SET
    name = 'Tamilaga Vettri Kazhagam',
    slug = 'tvk',
    type = 'political_party',
    subscription_status = 'active',
    logo_url = '/TVKAsset1_1024x1024.webp',
    website = 'https://www.tvk.org.in',
    primary_contact_name = 'Vijay',
    primary_contact_email = 'contact@tvk.org.in',
    primary_contact_phone = '+91-44-XXXXXXXX',
    settings = jsonb_build_object(
        'party_color', '#FFD700',
        'party_symbol', 'Rising Sun',
        'established_year', 2023,
        'headquarters', 'Chennai, Tamil Nadu',
        'social_media', jsonb_build_object(
            'twitter', '@TVKOfficial',
            'facebook', 'TVKOfficial',
            'instagram', '@tvk_official'
        )
    ),
    metadata = jsonb_build_object(
        'party_full_name', 'Tamilaga Vettri Kazhagam',
        'party_short_name', 'TVK',
        'founder', 'Vijay',
        'ideology', 'Social Democracy',
        'alliance', 'Independent',
        'state', 'Tamil Nadu',
        'focus_areas', jsonb_build_array(
            'Youth Empowerment',
            'Social Justice',
            'Economic Development',
            'Education Reform',
            'Healthcare Access'
        )
    ),
    updated_at = NOW()
WHERE id = '11111111-1111-1111-1111-111111111111';

-- Update other sample organizations to be competitors/test accounts
UPDATE organizations
SET
    name = 'Dravida Munnetra Kazhagam',
    slug = 'dmk',
    type = 'political_party',
    subscription_status = 'active',
    metadata = jsonb_build_object(
        'party_full_name', 'Dravida Munnetra Kazhagam',
        'party_short_name', 'DMK',
        'note', 'Competitor party data for analysis'
    )
WHERE id = '22222222-2222-2222-2222-222222222222';

UPDATE organizations
SET
    name = 'All India Anna Dravida Munnetra Kazhagam',
    slug = 'aiadmk',
    type = 'political_party',
    subscription_status = 'active',
    metadata = jsonb_build_object(
        'party_full_name', 'All India Anna Dravida Munnetra Kazhagam',
        'party_short_name', 'AIADMK',
        'note', 'Competitor party data for analysis'
    )
WHERE id = '33333333-3333-3333-3333-333333333333';

-- Verify the update
SELECT
    id,
    name,
    slug,
    type,
    subscription_status,
    logo_url,
    website
FROM organizations
WHERE id = '11111111-1111-1111-1111-111111111111';

-- Add comment
COMMENT ON TABLE organizations IS 'Organizations table - Primary org is TVK (Tamilaga Vettri Kazhagam)';
