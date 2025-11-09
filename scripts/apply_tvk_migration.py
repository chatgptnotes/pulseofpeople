#!/usr/bin/env python3
"""
Apply TVK migration to update organization from placeholder to TVK
"""

import os
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("UPDATING ORGANIZATION TO TVK")
print("=" * 60)

try:
    # Update primary organization to TVK
    print("\n📝 Updating primary organization to TVK...")

    result = supabase.table('organizations').update({
        'name': 'Tamilaga Vettri Kazhagam',
        'slug': 'tvk',
        'type': 'political_party',
        'subscription_status': 'active',
        'logo_url': '/TVKAsset1_1024x1024.webp',
        'website': 'https://www.tvk.org.in',
        'primary_contact_name': 'Vijay',
        'primary_contact_email': 'contact@tvk.org.in',
        'primary_contact_phone': '+91-44-XXXXXXXX',
        'settings': {
            'party_color': '#FFD700',
            'party_symbol': 'Rising Sun',
            'established_year': 2023,
            'headquarters': 'Chennai, Tamil Nadu',
            'social_media': {
                'twitter': '@TVKOfficial',
                'facebook': 'TVKOfficial',
                'instagram': '@tvk_official'
            }
        },
        'metadata': {
            'party_full_name': 'Tamilaga Vettri Kazhagam',
            'party_short_name': 'TVK',
            'founder': 'Vijay',
            'ideology': 'Social Democracy',
            'alliance': 'Independent',
            'state': 'Tamil Nadu',
            'focus_areas': [
                'Youth Empowerment',
                'Social Justice',
                'Economic Development',
                'Education Reform',
                'Healthcare Access'
            ]
        }
    }).eq('id', '11111111-1111-1111-1111-111111111111').execute()

    print("✅ Primary organization updated to TVK!")

    # Update other organizations to competitors
    print("\n📝 Updating competitor organizations...")

    # DMK
    supabase.table('organizations').update({
        'name': 'Dravida Munnetra Kazhagam',
        'slug': 'dmk',
        'metadata': {
            'party_full_name': 'Dravida Munnetra Kazhagam',
            'party_short_name': 'DMK',
            'note': 'Competitor party data for analysis'
        }
    }).eq('id', '22222222-2222-2222-2222-222222222222').execute()

    # AIADMK
    supabase.table('organizations').update({
        'name': 'All India Anna Dravida Munnetra Kazhagam',
        'slug': 'aiadmk',
        'metadata': {
            'party_full_name': 'All India Anna Dravida Munnetra Kazhagam',
            'party_short_name': 'AIADMK',
            'note': 'Competitor party data for analysis'
        }
    }).eq('id', '33333333-3333-3333-3333-333333333333').execute()

    print("✅ Competitor organizations updated!")

    # Verify the update
    print("\n📊 VERIFICATION")
    print("-" * 60)

    orgs = supabase.table('organizations').select('*').execute()

    for org in orgs.data:
        print(f"\n{org['name']} ({org['slug']})")
        print(f"  Type: {org['type']}")
        print(f"  Status: {org['subscription_status']}")
        if org['logo_url']:
            print(f"  Logo: {org['logo_url']}")
        if org['website']:
            print(f"  Website: {org['website']}")

    # Count voters for TVK
    print("\n📊 VOTER COUNT FOR TVK")
    print("-" * 60)

    voter_count = supabase.table('voters')\
        .select('id', count='exact')\
        .eq('organization_id', '11111111-1111-1111-1111-111111111111')\
        .execute()

    print(f"TVK has {voter_count.count:,} voters in the database")

    print("\n" + "=" * 60)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 60)
    print("\n🎉 Your Pulse of People platform is now branded for TVK!")

except Exception as e:
    print(f"\n❌ Error during migration: {e}")
    import traceback
    traceback.print_exc()
