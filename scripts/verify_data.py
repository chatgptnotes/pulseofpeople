#!/usr/bin/env python3
"""
Quick verification script to check voter data in Supabase
"""

import os
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("VOTER DATA VERIFICATION")
print("=" * 60)

# 1. Total voter count
print("\n📊 VOTER STATISTICS")
print("-" * 60)

try:
    # Get total count
    result = supabase.table('voters').select('id', count='exact').execute()
    total_voters = result.count
    print(f"Total Voters: {total_voters:,}")

    # Get sentiment distribution
    print("\n🎯 SENTIMENT DISTRIBUTION")
    sentiments = supabase.table('voters')\
        .select('sentiment')\
        .execute()

    from collections import Counter
    sentiment_counts = Counter([v['sentiment'] for v in sentiments.data])
    for sentiment, count in sorted(sentiment_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_voters) * 100
        print(f"  {sentiment:20s}: {count:6,} ({percentage:5.2f}%)")

    # Get booth distribution
    print("\n🏢 BOOTH DISTRIBUTION (Top 10)")
    booths = supabase.table('polling_booths')\
        .select('id, name, booth_number')\
        .execute()

    for booth in booths.data[:10]:
        booth_voters = supabase.table('voters')\
            .select('id', count='exact')\
            .eq('polling_booth_id', booth['id'])\
            .execute()
        print(f"  {booth['name']:30s} ({booth['booth_number']}): {booth_voters.count:6,} voters")

    # Get sample voters
    print("\n👥 SAMPLE VOTERS (First 5)")
    print("-" * 60)
    sample_voters = supabase.table('voters')\
        .select('full_name, age, gender, sentiment, voter_category')\
        .limit(5)\
        .execute()

    for voter in sample_voters.data:
        print(f"  {voter['full_name']:25s} | Age: {voter['age']:2d} | {voter['gender']:6s} | "
              f"{voter['sentiment']:15s} | {voter['voter_category']}")

    print("\n" + "=" * 60)
    print("✅ VERIFICATION COMPLETE!")
    print("=" * 60)

except Exception as e:
    print(f"❌ Error during verification: {e}")
