#!/usr/bin/env python
"""
Quick data generation script - bypasses management commands
Generates all master data directly in Supabase
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import (
    State, District, Constituency, PollingBooth,
    IssueCategory, VoterSegment, PoliticalParty, Organization
)
from django.contrib.auth import get_user_model
import random

User = get_user_model()

print("="*80)
print("QUICK DATA GENERATION - SUPABASE")
print("="*80)

# 1. Create Districts for Tamil Nadu
print("\n[1/6] Creating Districts...")
tn_state = State.objects.get(code='TN')
py_state = State.objects.get(code='PY')

tn_districts = [
    'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore',
    'Dharmapuri', 'Dindigul', 'Erode', 'Kallakurichi', 'Kanchipuram',
    'Kanyakumari', 'Karur', 'Krishnagiri', 'Madurai', 'Mayiladuthurai',
    'Nagapattinam', 'Namakkal', 'Nilgiris', 'Perambalur', 'Pudukkottai',
    'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga', 'Tenkasi',
    'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli',
    'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur',
    'Vellore', 'Viluppuram', 'Virudhunagar'
]

py_districts = ['Puducherry', 'Karaikal', 'Mahe', 'Yanam']

tn_district_codes = {
    'Ariyalur': 'ARY', 'Chengalpattu': 'CGP', 'Chennai': 'CHE', 'Coimbatore': 'COI',
    'Cuddalore': 'CUD', 'Dharmapuri': 'DHP', 'Dindigul': 'DIN', 'Erode': 'ERO',
    'Kallakurichi': 'KAL', 'Kanchipuram': 'KAN', 'Kanyakumari': 'KNY', 'Karur': 'KAR',
    'Krishnagiri': 'KRI', 'Madurai': 'MAD', 'Mayiladuthurai': 'MAY', 'Nagapattinam': 'NAG',
    'Namakkal': 'NAM', 'Nilgiris': 'NIL', 'Perambalur': 'PER', 'Pudukkottai': 'PUD',
    'Ramanathapuram': 'RAM', 'Ranipet': 'RAN', 'Salem': 'SAL', 'Sivaganga': 'SIV',
    'Tenkasi': 'TEN', 'Thanjavur': 'THA', 'Theni': 'THE', 'Thoothukudi': 'THO',
    'Tiruchirappalli': 'TRI', 'Tirunelveli': 'TIR', 'Tirupathur': 'TIP', 'Tiruppur': 'TPR',
    'Tiruvallur': 'TIV', 'Tiruvannamalai': 'TIA', 'Tiruvarur': 'TVR', 'Vellore': 'VEL',
    'Viluppuram': 'VIL', 'Virudhunagar': 'VIR'
}

py_district_codes = {'Puducherry': 'PDY', 'Karaikal': 'KRK', 'Mahe': 'MAH', 'Yanam': 'YAN'}

districts = []
for name in tn_districts:
    d, _ = District.objects.get_or_create(
        name=name,
        state=tn_state,
        defaults={'code': tn_district_codes[name]}
    )
    districts.append(d)

for name in py_districts:
    d, _ = District.objects.get_or_create(
        name=name,
        state=py_state,
        defaults={'code': py_district_codes[name]}
    )
    districts.append(d)

print(f"Created {District.objects.count()} districts")

# 2. Create Constituencies
print("\n[2/6] Creating Constituencies...")
constituencies_data = [
    ('Chennai', ['Gummidipoondi', 'Ponneri', 'Tiruvottiyur', 'Chepauk-Thiruvallikeni',
                 'Thousand Lights', 'Anna Nagar', 'Virugambakkam', 'Saidapet', 'T. Nagar']),
    ('Coimbatore', ['Sulur', 'Kavundampalayam', 'Coimbatore North', 'Coimbatore South', 'Singanallur']),
    ('Madurai', ['Melur', 'Madurai East', 'Sholavandan', 'Madurai North', 'Madurai South', 'Madurai Central']),
    ('Salem', ['Omalur', 'Mettur', 'Edappadi', 'Sankari', 'Salem North', 'Salem South', 'Salem West']),
    ('Tiruchirappalli', ['Musiri', 'Lalgudi', 'Manachanallur', 'Srirangam', 'Tiruchirappalli West', 'Tiruchirappalli East']),
]

constituencies = []
const_number = 1
for dist_name, const_list in constituencies_data:
    dist = District.objects.get(name=dist_name)
    for const_name in const_list:
        # Create unique codes to avoid duplicates
        unique_code = f"{dist.code}-{const_number:02d}"
        c, _ = Constituency.objects.get_or_create(
            name=const_name,
            district=dist,
            state=tn_state,
            defaults={
                'code': unique_code,
                'number': const_number,
                'total_voters': random.randint(150000, 300000)
            }
        )
        constituencies.append(c)
        const_number += 1

print(f"Created {Constituency.objects.count()} constituencies")

# 3. Create Polling Booths
print("\n[3/6] Creating Polling Booths...")
booth_count = 0
for const in constituencies[:10]:  # Create booths for first 10 constituencies
    for i in range(1, 51):  # 50 booths per constituency
        PollingBooth.objects.get_or_create(
            booth_number=f"{const.code}-{i:03d}",
            constituency=const,
            defaults={
                'name': f"{const.name} Booth {i}",
                'address': f"{i} Main Road, {const.name}",
                'latitude': 10.0 + random.uniform(-2, 2),
                'longitude': 78.0 + random.uniform(-2, 2),
                'total_voters': random.randint(800, 1200)
            }
        )
        booth_count += 1

print(f"Created {PollingBooth.objects.count()} polling booths")

# 4. Create Issue Categories
print("\n[4/6] Creating Issue Categories...")
issues = [
    ('Water Supply', '#1976D2', 'water-drop'),
    ('Jobs/Employment', '#388E3C', 'work'),
    ('Agriculture', '#689F38', 'agriculture'),
    ('Healthcare', '#D32F2F', 'local-hospital'),
    ('Education', '#7B1FA2', 'school'),
    ('NEET Opposition', '#C2185B', 'school-off'),
    ('Cauvery Dispute', '#0288D1', 'waves'),
    ('Fishermen Rights', '#00796B', 'sailing'),
    ('Cyclone Relief', '#455A64', 'storm'),
    ('Infrastructure', '#F57C00', 'construction'),
]

for name, color, icon in issues:
    IssueCategory.objects.get_or_create(
        name=name,
        defaults={
            'description': f'{name} related issues',
            'color': color,
            'icon': icon,
            'priority': random.randint(1, 5),
            'is_active': True
        }
    )

print(f"Created {IssueCategory.objects.count()} issue categories")

# 5. Create Voter Segments
print("\n[5/6] Creating Voter Segments...")
segments = [
    'Youth (18-25)', 'Young Professionals (26-35)', 'Middle-Aged (36-50)',
    'Senior Citizens (50+)', 'Women Voters', 'First-Time Voters',
    'Urban Educated', 'Rural Farmers', 'IT Professionals', 'Students'
]

for segment_name in segments:
    VoterSegment.objects.get_or_create(
        name=segment_name,
        defaults={
            'description': f'{segment_name} demographic',
            'is_active': True
        }
    )

print(f"Created {VoterSegment.objects.count()} voter segments")

# 6. Create Political Parties
print("\n[6/6] Creating Political Parties...")
parties = [
    ('TVK', 'Tamilaga Vettri Kazhagam', '#FF0000'),
    ('DMK', 'Dravida Munnetra Kazhagam', '#000000'),
    ('AIADMK', 'All India Anna Dravida Munnetra Kazhagam', '#00FF00'),
    ('BJP', 'Bharatiya Janata Party', '#FF9933'),
    ('INC', 'Indian National Congress', '#0000FF'),
]

for code, name, color in parties:
    PoliticalParty.objects.get_or_create(
        code=code,
        defaults={
            'name': name,
            'full_name': name,
            'color': color,
            'symbol': code.lower(),
            'is_active': True
        }
    )

print(f"Created {PoliticalParty.objects.count()} political parties")

# 7. Ensure TVK Organization exists
print("\n[7/7] Creating TVK Organization...")
org, created = Organization.objects.get_or_create(
    name='Tamilaga Vettri Kazhagam',
    defaults={
        'slug': 'tvk',
        'organization_type': 'party',
        'description': 'Tamilaga Vettri Kazhagam - Tamil Nadu Political Party',
        'is_active': True
    }
)
print(f"Organization: {org.name} ({'created' if created else 'already exists'})")

print("\n" + "="*80)
print("DATA GENERATION SUMMARY")
print("="*80)
print(f"States: {State.objects.count()}")
print(f"Districts: {District.objects.count()}")
print(f"Constituencies: {Constituency.objects.count()}")
print(f"Polling Booths: {PollingBooth.objects.count()}")
print(f"Issue Categories: {IssueCategory.objects.count()}")
print(f"Voter Segments: {VoterSegment.objects.count()}")
print(f"Political Parties: {PoliticalParty.objects.count()}")
print(f"Organizations: {Organization.objects.count()}")
print(f"Users: {User.objects.count()}")
print("="*80)
print("✅ MASTER DATA GENERATION COMPLETE!")
print("="*80)
