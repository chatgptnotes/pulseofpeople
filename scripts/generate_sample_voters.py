#!/usr/bin/env python3
"""
Generate Sample Voter Data for Pulse of People
Creates 50,000+ realistic voter records with Indian demographics
"""

import os
import sys
import random
import hashlib
from datetime import datetime, timedelta
from faker import Faker
from supabase import create_client, Client

# Initialize Faker with Indian locale
fake = Faker(['en_IN'])

# Supabase connection (from environment variables)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')  # Use service key for admin operations

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables required")
    print("\nSet them in your .env file or export:")
    print("  export SUPABASE_URL='https://your-project.supabase.co'")
    print("  export SUPABASE_SERVICE_KEY='your-service-key'")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration
TOTAL_VOTERS = 50000  # Total voters to generate
BATCH_SIZE = 1000     # Insert in batches to avoid memory issues
ORGANIZATION_ID = '11111111-1111-1111-1111-111111111111'  # Democratic Alliance Party

# Indian names database (curated lists)
FIRST_NAMES_MALE = [
    'Rajesh', 'Amit', 'Suresh', 'Anil', 'Vijay', 'Ramesh', 'Manoj', 'Sanjay', 'Rakesh', 'Ravi',
    'Ashok', 'Prakash', 'Dinesh', 'Ajay', 'Sandeep', 'Deepak', 'Vinod', 'Mukesh', 'Anand', 'Krishna',
    'Mahesh', 'Naresh', 'Sunil', 'Vishal', 'Rahul', 'Rohan', 'Arjun', 'Karthik', 'Pradeep', 'Naveen'
]

FIRST_NAMES_FEMALE = [
    'Priya', 'Sunita', 'Kavita', 'Anjali', 'Pooja', 'Neha', 'Sneha', 'Rekha', 'Geeta', 'Meena',
    'Asha', 'Usha', 'Sushma', 'Lakshmi', 'Saraswati', 'Parvati', 'Radha', 'Sita', 'Deepika', 'Anita',
    'Nisha', 'Ritu', 'Divya', 'Preeti', 'Swati', 'Shweta', 'Nikita', 'Ritu', 'Shruti', 'Bhavna'
]

LAST_NAMES = [
    'Kumar', 'Sharma', 'Singh', 'Patel', 'Reddy', 'Nair', 'Iyer', 'Rao', 'Joshi', 'Verma',
    'Gupta', 'Agarwal', 'Mukherjee', 'Das', 'Banerjee', 'Roy', 'Pillai', 'Menon', 'Desai', 'Mehta',
    'Kulkarni', 'Jain', 'Bhat', 'Shetty', 'Mishra', 'Pandey', 'Tiwari', 'Chaudhary', 'Khan', 'Ali'
]

RELIGIONS = ['Hindu', 'Muslim', 'Christian', 'Sikh', 'Buddhist', 'Jain', 'Other']
RELIGION_WEIGHTS = [0.65, 0.15, 0.08, 0.03, 0.02, 0.02, 0.05]

CASTES = ['General', 'OBC', 'SC', 'ST']
CASTE_WEIGHTS = [0.30, 0.40, 0.20, 0.10]

OCCUPATIONS = [
    'Software Engineer', 'Teacher', 'Doctor', 'Nurse', 'Shopkeeper', 'Farmer', 'Driver',
    'Mechanic', 'Electrician', 'Plumber', 'Accountant', 'Lawyer', 'Engineer', 'Student',
    'Retired', 'Homemaker', 'Business Owner', 'Security Guard', 'Cook', 'Tailor'
]

EDUCATION_LEVELS = [
    'No Formal Education', 'Primary', 'Secondary', 'Higher Secondary',
    'Graduate', 'Post Graduate', 'Professional Degree', 'PhD'
]
EDUCATION_WEIGHTS = [0.10, 0.15, 0.25, 0.20, 0.18, 0.08, 0.03, 0.01]

INCOME_RANGES = [
    '< 10,000', '10,000 - 25,000', '25,000 - 50,000', '50,000 - 1,00,000',
    '1,00,000 - 2,00,000', '> 2,00,000'
]
INCOME_WEIGHTS = [0.20, 0.30, 0.25, 0.15, 0.07, 0.03]

SENTIMENTS = ['strong_support', 'support', 'neutral', 'oppose', 'strong_oppose', 'undecided']
SENTIMENT_WEIGHTS = [0.15, 0.25, 0.20, 0.10, 0.05, 0.25]

VOTER_CATEGORIES = ['core_supporter', 'swing_voter', 'opponent']
CATEGORY_WEIGHTS = [0.35, 0.40, 0.25]

TOP_ISSUES = [
    'Employment', 'Water Supply', 'Electricity', 'Roads', 'Healthcare', 'Education',
    'Law & Order', 'Corruption', 'Inflation', 'Agriculture', 'Infrastructure',
    'Public Transport', 'Sanitation', 'Housing'
]

CONTACT_METHODS = ['door_to_door', 'phone', 'whatsapp', 'event', 'rally']

VOTER_TAGS = [
    'senior_citizen', 'first_time_voter', 'influencer', 'undecided', 'youth',
    'women', 'minority', 'disabled', 'educated', 'farmer', 'business_owner'
]


def generate_voter_id():
    """Generate a realistic voter ID number"""
    prefix = random.choice(['TN', 'KA', 'MH', 'DL'])
    year = random.randint(2010, 2024)
    serial = random.randint(100000, 999999)
    return f"{prefix}{year}{serial}"


def generate_epic_number():
    """Generate EPIC (Elector's Photo Identity Card) number"""
    prefix = random.choice(['TN', 'KA', 'MH', 'DL'])
    return f"{prefix}/{random.randint(10, 99)}/{random.randint(100000, 999999)}"


def hash_aadhaar(aadhaar):
    """Hash Aadhaar number for privacy (DPDP compliance)"""
    return hashlib.sha256(aadhaar.encode()).hexdigest()


def generate_phone():
    """Generate Indian mobile number"""
    return f"+91{random.randint(7000000000, 9999999999)}"


def calculate_sentiment_score(sentiment):
    """Convert sentiment to numerical score (-100 to +100)"""
    sentiment_scores = {
        'strong_support': random.randint(70, 100),
        'support': random.randint(30, 69),
        'neutral': random.randint(-15, 15),
        'oppose': random.randint(-69, -30),
        'strong_oppose': random.randint(-100, -70),
        'undecided': random.randint(-10, 10)
    }
    return sentiment_scores.get(sentiment, 0)


def generate_voting_history():
    """Generate realistic voting history"""
    history = []
    years = [2024, 2019, 2014, 2009]
    for year in years:
        if random.random() > 0.3:  # 70% chance of voting in each election
            history.append({
                'year': year,
                'voted': True,
                'party': random.choice(['Party A', 'Party B', 'Party C', 'NOTA'])
            })
    return history


def assign_tags(age, gender, sentiment, occupation, education):
    """Intelligently assign tags based on voter profile"""
    tags = []

    if age >= 60:
        tags.append('senior_citizen')
    if age <= 21:
        tags.append('first_time_voter')
    if age <= 35:
        tags.append('youth')
    if gender == 'Female':
        tags.append('women')
    if sentiment in ['undecided', 'neutral']:
        tags.append('undecided')
    if education in ['Graduate', 'Post Graduate', 'Professional Degree', 'PhD']:
        tags.append('educated')
    if occupation in ['Farmer', 'Agricultural Worker']:
        tags.append('farmer')
    if occupation in ['Business Owner', 'Shopkeeper']:
        tags.append('business_owner')

    # Random chance for influencer
    if random.random() < 0.05:
        tags.append('influencer')

    return tags


def generate_voter(booth_id, booth_org_id):
    """Generate a single voter record"""
    # Gender distribution: 52% Male, 47% Female, 1% Other
    gender_choice = random.random()
    if gender_choice < 0.52:
        gender = 'Male'
        first_name = random.choice(FIRST_NAMES_MALE)
    elif gender_choice < 0.99:
        gender = 'Female'
        first_name = random.choice(FIRST_NAMES_FEMALE)
    else:
        gender = random.choice(['Transgender', 'Other'])
        first_name = random.choice(FIRST_NAMES_MALE + FIRST_NAMES_FEMALE)

    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"

    # Age distribution: 18-80, skewed towards middle age
    age = int(random.gauss(45, 15))
    age = max(18, min(80, age))  # Clamp to 18-80

    date_of_birth = datetime.now() - timedelta(days=age * 365)

    # Contact info (40% have phone, 20% have email)
    phone = generate_phone() if random.random() < 0.4 else None
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@gmail.com" if random.random() < 0.2 else None
    whatsapp = phone if phone and random.random() < 0.7 else None

    # Demographics
    religion = random.choices(RELIGIONS, weights=RELIGION_WEIGHTS)[0]
    caste_category = random.choices(CASTES, weights=CASTE_WEIGHTS)[0]
    occupation = random.choice(OCCUPATIONS)
    education = random.choices(EDUCATION_LEVELS, weights=EDUCATION_WEIGHTS)[0]
    income_range = random.choices(INCOME_RANGES, weights=INCOME_WEIGHTS)[0]

    # Political sentiment
    sentiment = random.choices(SENTIMENTS, weights=SENTIMENT_WEIGHTS)[0]
    sentiment_score = calculate_sentiment_score(sentiment)
    voter_category = random.choices(VOTER_CATEGORIES, weights=CATEGORY_WEIGHTS)[0]

    # Issues and concerns
    num_issues = random.randint(1, 5)
    top_issues = random.sample(TOP_ISSUES, num_issues)

    # Engagement
    contacted = random.random() < 0.3  # 30% contacted
    last_contact = (datetime.now() - timedelta(days=random.randint(1, 180))).date() if contacted else None
    contact_method = random.choice(CONTACT_METHODS) if contacted else None

    # Influencer score (0-100, normal distribution around 30)
    influencer_score = int(max(0, min(100, random.gauss(30, 20))))

    # Voting history
    voting_history = generate_voting_history()
    voter_turnout_rate = (len([h for h in voting_history if h['voted']]) / len(voting_history) * 100) if voting_history else None
    first_time_voter = age <= 21

    # Tags
    tags = assign_tags(age, gender, sentiment, occupation, education)

    # Data quality (higher for verified voters)
    verified = random.random() < 0.4  # 40% verified
    data_quality_score = random.randint(70, 100) if verified else random.randint(40, 80)

    # Consent (60% given consent)
    consent_given = random.random() < 0.6

    return {
        'organization_id': booth_org_id,
        'polling_booth_id': booth_id,
        'voter_id_number': generate_voter_id(),
        'epic_number': generate_epic_number() if random.random() < 0.8 else None,
        'aadhaar_number_hash': hash_aadhaar(f"{random.randint(100000000000, 999999999999)}") if random.random() < 0.7 else None,
        'full_name': full_name,
        'gender': gender,
        'age': age,
        'date_of_birth': date_of_birth.date().isoformat(),
        'address': fake.address() if random.random() < 0.6 else None,
        'phone': phone,
        'email': email,
        'whatsapp_number': whatsapp,
        'religion': religion,
        'caste': random.choice(['Brahmin', 'Kshatriya', 'Vaishya', 'Shudra', 'Other']) if religion == 'Hindu' else None,
        'caste_category': caste_category,
        'occupation': occupation,
        'education': education,
        'monthly_income_range': income_range,
        'family_size': random.randint(1, 8),
        'influencer_score': influencer_score,
        'voting_history': voting_history,
        'voter_turnout_rate': voter_turnout_rate,
        'first_time_voter': first_time_voter,
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'sentiment_last_updated': (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat() if sentiment != 'undecided' else None,
        'preferred_party': random.choice(['Party A', 'Party B', 'Party C']) if sentiment in ['strong_support', 'support'] else None,
        'previous_party_support': random.choice(['Party A', 'Party B', 'Party C']) if random.random() < 0.5 else None,
        'top_issues': top_issues,
        'contacted_by_party': contacted,
        'last_contact_date': last_contact.isoformat() if last_contact else None,
        'contact_method': contact_method,
        'meeting_attendance': random.randint(0, 10) if contacted else 0,
        'rally_participation': random.randint(0, 5) if contacted else 0,
        'tags': tags,
        'voter_category': voter_category,
        'data_quality_score': data_quality_score,
        'verified': verified,
        'consent_given': consent_given,
        'consent_date': (datetime.now() - timedelta(days=random.randint(1, 365))).date().isoformat() if consent_given else None,
    }


def main():
    print("🚀 Starting voter data generation...")
    print(f"Target: {TOTAL_VOTERS:,} voters")
    print(f"Batch size: {BATCH_SIZE:,}")
    print()

    # Step 1: Fetch polling booths
    print("📍 Fetching polling booths...")
    response = supabase.table('polling_booths').select('id, organization_id, name, booth_number').execute()
    booths = response.data

    if not booths:
        print("❌ No polling booths found! Please run Phase 2 migration first.")
        sys.exit(1)

    print(f"✅ Found {len(booths)} polling booths")
    print()

    # Step 2: Distribute voters across booths
    voters_per_booth = TOTAL_VOTERS // len(booths)
    remainder = TOTAL_VOTERS % len(booths)

    print(f"📊 Distribution: ~{voters_per_booth} voters per booth")
    print()

    # Step 3: Generate and insert voters
    total_inserted = 0

    for booth_idx, booth in enumerate(booths):
        num_voters = voters_per_booth + (1 if booth_idx < remainder else 0)

        print(f"🏢 Booth {booth_idx + 1}/{len(booths)}: {booth['name']} ({booth['booth_number']})")
        print(f"   Generating {num_voters:,} voters...")

        # Generate voters in batches
        for batch_start in range(0, num_voters, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, num_voters)
            batch_size = batch_end - batch_start

            voters_batch = [
                generate_voter(booth['id'], booth['organization_id'])
                for _ in range(batch_size)
            ]

            # Insert batch
            try:
                supabase.table('voters').insert(voters_batch).execute()
                total_inserted += batch_size
                print(f"   ✓ Inserted {batch_start + batch_size:,}/{num_voters:,} voters ({total_inserted:,} total)")
            except Exception as e:
                print(f"   ❌ Error inserting batch: {e}")
                continue

        print()

    # Step 4: Verify and summarize
    print("=" * 60)
    print("✅ Voter generation complete!")
    print(f"Total voters inserted: {total_inserted:,}")
    print()

    # Fetch statistics
    print("📊 Generating statistics...")
    stats_response = supabase.table('voters').select('gender, sentiment, voter_category', count='exact').execute()

    print(f"Total records in database: {stats_response.count:,}")
    print()

    print("💡 Next steps:")
    print("  1. Verify data in Supabase dashboard")
    print("  2. Run: SELECT * FROM voters LIMIT 10;")
    print("  3. Check constituency stats: SELECT * FROM get_constituency_stats('constituency_id');")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Generation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
