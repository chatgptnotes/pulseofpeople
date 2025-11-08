"""
Django management command to seed political platform data
Usage: python manage.py seed_political_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import (
    State, District, Constituency, PoliticalParty, IssueCategory,
    VoterSegment, DirectFeedback, UserProfile
)


class Command(BaseCommand):
    help = 'Seeds political platform with Tamil Nadu data and TVK priorities'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🌱 Starting seed process...'))

        # 1. Create States
        self.seed_states()

        # 2. Create Districts
        self.seed_districts()

        # 3. Create Political Parties
        self.seed_parties()

        # 4. Create Issue Categories (TVK's 9 priorities)
        self.seed_issues()

        # 5. Create Voter Segments
        self.seed_voter_segments()

        # 6. Create sample constituencies (first 10)
        self.seed_constituencies()

        self.stdout.write(self.style.SUCCESS('✅ Seed process completed!'))

    def seed_states(self):
        self.stdout.write('📍 Seeding states...')

        states_data = [
            {'name': 'Tamil Nadu', 'code': 'TN', 'capital': 'Chennai', 'region': 'South', 'total_districts': 38, 'total_constituencies': 234},
            {'name': 'Puducherry', 'code': 'PY', 'capital': 'Puducherry', 'region': 'South', 'total_districts': 4, 'total_constituencies': 30},
        ]

        for data in states_data:
            state, created = State.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✓ Created state: {state.name}')
            else:
                self.stdout.write(f'  - State exists: {state.name}')

    def seed_districts(self):
        self.stdout.write('📍 Seeding districts...')

        tn = State.objects.get(code='TN')

        # Tamil Nadu's 38 districts
        districts_data = [
            'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore',
            'Dharmapuri', 'Dindigul', 'Erode', 'Kallakurichi', 'Kanchipuram',
            'Kanyakumari', 'Karur', 'Krishnagiri', 'Madurai', 'Mayiladuthurai',
            'Nagapattinam', 'Namakkal', 'Nilgiris', 'Perambalur', 'Pudukkottai',
            'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga', 'Tenkasi',
            'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli',
            'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur',
            'Vellore', 'Viluppuram', 'Virudhunagar'
        ]

        for idx, name in enumerate(districts_data, 1):
            district, created = District.objects.get_or_create(
                code=f'TN{idx:02d}',
                defaults={
                    'state': tn,
                    'name': name,
                    'headquarters': name,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created district: {name}')

        self.stdout.write(f'  Total: {len(districts_data)} districts')

    def seed_parties(self):
        self.stdout.write('🏛️  Seeding political parties...')

        tn = State.objects.get(code='TN')

        parties_data = [
            {
                'name': 'Tamilaga Vettri Kazhagam',
                'short_name': 'TVK',
                'status': 'state',
                'ideology': 'Secular Social Justice',
                'founded_date': '2024-02-02',
                'headquarters': 'Chennai, Tamil Nadu',
                'website': 'https://tvk.org',
                'description': 'Founded by actor Vijay, focused on social justice, anti-casteism, and Tamil pride.'
            },
            {
                'name': 'Dravida Munnetra Kazhagam',
                'short_name': 'DMK',
                'status': 'state',
                'ideology': 'Dravidian, Social Democracy',
                'headquarters': 'Chennai, Tamil Nadu',
                'description': 'Major Dravidian party, currently ruling Tamil Nadu.'
            },
            {
                'name': 'All India Anna Dravida Munnetra Kazhagam',
                'short_name': 'AIADMK',
                'status': 'state',
                'ideology': 'Dravidian, Social Conservatism',
                'headquarters': 'Chennai, Tamil Nadu',
                'description': 'Major opposition party in Tamil Nadu.'
            },
            {
                'name': 'Bharatiya Janata Party',
                'short_name': 'BJP',
                'status': 'national',
                'ideology': 'Hindu Nationalism, Right-wing',
                'headquarters': 'New Delhi',
                'description': 'National party, currently ruling at the centre.'
            },
        ]

        for data in parties_data:
            party, created = PoliticalParty.objects.get_or_create(
                short_name=data['short_name'],
                defaults=data
            )
            if created:
                party.active_states.add(tn)
                self.stdout.write(f'  ✓ Created party: {party.short_name}')
            else:
                self.stdout.write(f'  - Party exists: {party.short_name}')

    def seed_issues(self):
        self.stdout.write('📋 Seeding issue categories (TVK priorities)...')

        # TVK's 9 Key Issues
        issues_data = [
            {'name': 'Social Justice & Caste Issues', 'priority': 9, 'color': '#E74C3C', 'icon': 'balance'},
            {'name': "Women's Safety & Empowerment", 'priority': 8, 'color': '#9B59B6', 'icon': 'female'},
            {'name': "Fishermen's Rights & Livelihood", 'priority': 7, 'color': '#3498DB', 'icon': 'sailing'},
            {'name': 'Farmers Welfare & Agriculture', 'priority': 6, 'color': '#27AE60', 'icon': 'agriculture'},
            {'name': 'Youth Employment & Education', 'priority': 5, 'color': '#F39C12', 'icon': 'school'},
            {'name': 'Healthcare Access', 'priority': 4, 'color': '#E67E22', 'icon': 'local_hospital'},
            {'name': 'Environmental Protection', 'priority': 3, 'color': '#16A085', 'icon': 'eco'},
            {'name': 'Language & Cultural Rights', 'priority': 2, 'color': '#D35400', 'icon': 'language'},
            {'name': 'Law & Order', 'priority': 1, 'color': '#C0392B', 'icon': 'gavel'},
        ]

        for data in issues_data:
            issue, created = IssueCategory.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✓ Created issue: {issue.name}')
            else:
                self.stdout.write(f'  - Issue exists: {issue.name}')

    def seed_voter_segments(self):
        self.stdout.write('👥 Seeding voter segments...')

        segments_data = [
            {'name': 'Fishermen Community', 'priority_level': 9, 'estimated_population': 500000},
            {'name': 'Farmers', 'priority_level': 8, 'estimated_population': 10000000},
            {'name': 'Youth (18-25)', 'priority_level': 7, 'estimated_population': 8000000},
            {'name': 'Women', 'priority_level': 6, 'estimated_population': 35000000},
            {'name': 'Laborers & Workers', 'priority_level': 5, 'estimated_population': 15000000},
            {'name': 'Weavers', 'priority_level': 4, 'estimated_population': 200000},
            {'name': 'Students', 'priority_level': 3, 'estimated_population': 12000000},
            {'name': 'Elderly (60+)', 'priority_level': 2, 'estimated_population': 7000000},
            {'name': 'SC/ST Communities', 'priority_level': 1, 'estimated_population': 15000000},
        ]

        for data in segments_data:
            segment, created = VoterSegment.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                self.stdout.write(f'  ✓ Created segment: {segment.name}')
            else:
                self.stdout.write(f'  - Segment exists: {segment.name}')

    def seed_constituencies(self):
        self.stdout.write('🏛️  Seeding sample constituencies...')

        tn = State.objects.get(code='TN')
        chennai = District.objects.get(code='TN03')

        # First 10 Chennai constituencies
        constituencies_data = [
            {'code': 'TN001', 'number': 1, 'name': 'Gummidipoondi', 'reserved_for': 'sc'},
            {'code': 'TN002', 'number': 2, 'name': 'Ponneri', 'reserved_for': 'sc'},
            {'code': 'TN003', 'number': 3, 'name': 'Tiruvottiyur', 'reserved_for': 'general'},
            {'code': 'TN004', 'number': 4, 'name': 'Radhakrishnan Nagar', 'reserved_for': 'general'},
            {'code': 'TN005', 'number': 5, 'name': 'Perambur', 'reserved_for': 'general'},
            {'code': 'TN006', 'number': 6, 'name': 'Kolathur', 'reserved_for': 'general'},
            {'code': 'TN007', 'number': 7, 'name': 'Thiru-Vi-Ka-Nagar', 'reserved_for': 'general'},
            {'code': 'TN008', 'number': 8, 'name': 'Royapuram', 'reserved_for': 'general'},
            {'code': 'TN009', 'number': 9, 'name': 'Harbour', 'reserved_for': 'sc'},
            {'code': 'TN010', 'number': 10, 'name': 'Dr. Radhakrishnan Nagar', 'reserved_for': 'general'},
        ]

        for data in constituencies_data:
            constituency, created = Constituency.objects.get_or_create(
                code=data['code'],
                defaults={
                    'state': tn,
                    'district': chennai,
                    'name': data['name'],
                    'number': data['number'],
                    'constituency_type': 'assembly',
                    'reserved_for': data['reserved_for'],
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created constituency: {constituency.name}')

        self.stdout.write(f'  Total: {len(constituencies_data)} constituencies')
