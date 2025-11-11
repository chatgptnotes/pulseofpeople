"""
Django management command to generate comprehensive voter database with realistic Tamil Nadu demographics

Usage:
    python manage.py generate_voters

This command generates 100,000 anonymized voter records with:
- Proportional geographic distribution across 38 Tamil Nadu districts
- Realistic age, gender, education demographics
- Party affiliation reflecting pre-TVK and post-TVK landscape
- Sentiment distribution and influence levels
- Contact history and voter attributes
- Ward and constituency assignments
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from api.models import Voter, State, District, Constituency
from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize Faker with Indian locale for realistic Tamil names
fake = Faker(['ta_IN', 'en_IN'])


class Command(BaseCommand):
    help = 'Generates 100,000 anonymized voter records with realistic Tamil Nadu demographics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100000,
            help='Number of voters to generate (default: 100,000)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk creation (default: 1,000)'
        )

    def handle(self, *args, **options):
        total_count = options['count']
        batch_size = options['batch_size']

        self.stdout.write(self.style.WARNING(f'Starting voter generation: {total_count:,} voters'))
        self.stdout.write('=' * 80)

        # Tamil Nadu district distribution (38 districts)
        TN_DISTRICT_DISTRIBUTION = {
            'Chennai': 0.15,          # 15%
            'Coimbatore': 0.08,       # 8%
            'Madurai': 0.06,          # 6%
            'Tiruchirappalli': 0.05,  # 5%
            'Salem': 0.05,            # 5%
            'Tirunelveli': 0.04,      # 4%
            'Erode': 0.035,
            'Vellore': 0.035,
            'Tiruppur': 0.035,
            'Thoothukudi': 0.03,
            'Thanjavur': 0.03,
            'Kancheepuram': 0.03,
            'Dindigul': 0.028,
            'Cuddalore': 0.027,
            'Namakkal': 0.025,
            'Krishnagiri': 0.025,
            'Virudhunagar': 0.024,
            'Karur': 0.022,
            'Sivaganga': 0.022,
            'Ramanathapuram': 0.021,
            'Pudukkottai': 0.02,
            'Villupuram': 0.02,
            'Tiruvannamalai': 0.019,
            'Dharmapuri': 0.018,
            'Nagapattinam': 0.018,
            'Theni': 0.017,
            'Kanniyakumari': 0.016,
            'Tiruvallur': 0.016,
            'Ariyalur': 0.014,
            'Perambalur': 0.013,
            'Nilgiris': 0.013,
            'Tiruvarur': 0.012,
            'Ranipet': 0.011,
            'Tirupathur': 0.011,
            'Tenkasi': 0.01,
            'Kallakurichi': 0.01,
            'Chengalpattu': 0.009,
            'Mayiladuthurai': 0.008,
        }

        # Age distribution
        AGE_DISTRIBUTION = {
            (18, 25): 0.20,   # Youth: 20%
            (26, 35): 0.25,   # Young adults: 25%
            (36, 50): 0.30,   # Middle age: 30%
            (51, 65): 0.18,   # Senior: 18%
            (66, 90): 0.07,   # Elderly: 7%
        }

        # Gender distribution
        GENDER_DISTRIBUTION = {
            'male': 0.51,
            'female': 0.48,
            'other': 0.01,
        }

        # Education distribution (TN literacy patterns)
        EDUCATION_LEVELS = {
            'Illiterate': 0.10,
            'Primary': 0.15,
            'Secondary': 0.25,
            'Higher Secondary': 0.20,
            'Graduate': 0.20,
            'Postgraduate': 0.10,
        }

        # Party affiliation (simulated pre-TVK + TVK gain)
        PARTY_AFFILIATION = {
            'tvk': 0.22,        # TVK: 22% - Growing support
            'dmk': 0.20,        # DMK: 20% - Current ruling
            'aiadmk': 0.18,     # AIADMK: 18% - Major opposition
            'bjp': 0.08,        # BJP: 8%
            'congress': 0.05,   # Congress: 5%
            'neutral': 0.20,    # Neutral/Undecided: 20%
            'other': 0.07,      # Other parties: 7%
        }

        # Sentiment distribution
        SENTIMENT_DISTRIBUTION = {
            'strong_supporter': 0.15,
            'supporter': 0.25,
            'neutral': 0.35,
            'opposition': 0.20,
            'strong_opposition': 0.05,
        }

        # Influence level
        INFLUENCE_DISTRIBUTION = {
            'high': 0.05,    # Opinion leaders: 5%
            'medium': 0.20,  # Active community: 20%
            'low': 0.75,     # General voters: 75%
        }

        # Realistic Tamil names
        TAMIL_FIRST_NAMES_MALE = [
            'Arun', 'Balaji', 'Chandran', 'Dhanush', 'Ezhil', 'Gokul', 'Hari', 'Ilango',
            'Jagan', 'Karthik', 'Kumar', 'Manoj', 'Murugan', 'Naren', 'Pandi', 'Prakash',
            'Raj', 'Ravi', 'Sakthi', 'Senthil', 'Surya', 'Tamil', 'Vasan', 'Vijay', 'Vinoth'
        ]
        TAMIL_FIRST_NAMES_FEMALE = [
            'Anitha', 'Bharathi', 'Chitra', 'Deepa', 'Gayatri', 'Geetha', 'Janaki', 'Kavitha',
            'Lakshmi', 'Malathi', 'Meena', 'Nila', 'Priya', 'Radha', 'Sangeetha', 'Saranya',
            'Selvi', 'Shanthi', 'Sudha', 'Sumathi', 'Thenmozhi', 'Vasanthi', 'Valli', 'Yamini'
        ]
        TAMIL_LAST_NAMES = [
            'Kumar', 'Raj', 'Selvam', 'Moorthy', 'Pandian', 'Kannan', 'Rajan', 'Subramanian',
            'Venkatesh', 'Sundaram', 'Murugan', 'Anand', 'Krishnan', 'Ramesh', 'Saravanan'
        ]

        # Tamil Nadu localities/areas
        TN_AREAS = [
            'Anna Nagar', 'T Nagar', 'Adyar', 'Velachery', 'Tambaram', 'Pallavaram',
            'Gandhipuram', 'RS Puram', 'Saibaba Colony', 'Peelamedu', 'Singanallur',
            'SS Colony', 'Anna Nagar West', 'Vilangudi', 'Tallakulam', 'K Pudur',
            'Woraiyur', 'Srirangam', 'Thillai Nagar', 'Cantonment', 'Town Hall Area',
            'Junction', 'Fairlands', 'New Bus Stand', 'Collectorate', 'Market Area'
        ]

        # Voter tags
        VOTER_TAGS = [
            ['youth', 'first_time'], ['farmer'], ['tech_worker'], ['business_owner'],
            ['teacher'], ['healthcare_worker'], ['student'], ['retired'],
            ['daily_wage'], ['fisherman'], ['auto_driver'], ['small_business']
        ]

        # Get Tamil Nadu state and districts
        try:
            tn_state = State.objects.get(code='TN')
        except State.DoesNotExist:
            self.stdout.write(self.style.ERROR('Tamil Nadu state not found. Please run seed_political_data first.'))
            return

        districts = list(District.objects.filter(state=tn_state))
        if not districts:
            self.stdout.write(self.style.ERROR('No districts found for Tamil Nadu.'))
            return

        constituencies = list(Constituency.objects.filter(state=tn_state))
        if not constituencies:
            self.stdout.write(self.style.ERROR('No constituencies found for Tamil Nadu.'))
            return

        # Get system user for created_by
        system_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@pulseofpeople.com', 'first_name': 'System', 'last_name': 'Admin'}
        )

        self.stdout.write(self.style.SUCCESS(f'Found {len(districts)} districts and {len(constituencies)} constituencies'))
        self.stdout.write('=' * 80)

        # Track statistics
        stats = {
            'total_created': 0,
            'by_district': {},
            'by_age_group': {},
            'by_gender': {},
            'by_party': {},
            'by_sentiment': {},
            'by_influence': {},
            'by_education': {},
            'with_phone': 0,
            'with_email': 0,
            'opinion_leaders': 0,
        }

        def weighted_random(distribution):
            """Select item based on weighted distribution"""
            items = list(distribution.keys())
            weights = list(distribution.values())
            return random.choices(items, weights=weights, k=1)[0]

        def generate_voter_id(district_code, sequence):
            """Generate unique voter ID: TN{district_code}{6_digits}"""
            return f"TN{district_code}{sequence:06d}"

        def get_age_from_distribution():
            """Get age based on distribution"""
            age_range = weighted_random(AGE_DISTRIBUTION)
            return random.randint(age_range[0], age_range[1])

        def get_voting_history(age):
            """Generate realistic voting history based on age"""
            elections = [
                {'year': 2021, 'election': 'Assembly', 'voted': False},
                {'year': 2019, 'election': 'Lok Sabha', 'voted': False},
                {'year': 2016, 'election': 'Assembly', 'voted': False},
                {'year': 2014, 'election': 'Lok Sabha', 'voted': False},
            ]

            history = []
            current_year = 2024
            for election in elections:
                if current_year - election['year'] <= (age - 18):
                    # Eligible to vote in this election
                    voted = random.random() > 0.25  # 75% voting participation
                    history.append({**election, 'voted': voted})

            return history

        def generate_tamil_name(gender):
            """Generate realistic Tamil name"""
            if gender == 'male':
                first_name = random.choice(TAMIL_FIRST_NAMES_MALE)
            elif gender == 'female':
                first_name = random.choice(TAMIL_FIRST_NAMES_FEMALE)
            else:
                first_name = random.choice(TAMIL_FIRST_NAMES_MALE + TAMIL_FIRST_NAMES_FEMALE)

            last_name = random.choice(TAMIL_LAST_NAMES)
            middle_name = random.choice(TAMIL_LAST_NAMES) if random.random() > 0.6 else ''

            return first_name, middle_name, last_name

        # Create district mapping
        district_map = {}
        for district in districts:
            district_name = district.name
            for key in TN_DISTRICT_DISTRIBUTION.keys():
                if key.lower() in district_name.lower() or district_name.lower() in key.lower():
                    district_map[key] = district
                    break

        # Generate voters in batches
        batch = []
        voter_sequence = {}

        for i in range(total_count):
            try:
                # Select district based on distribution
                district_key = weighted_random(TN_DISTRICT_DISTRIBUTION)
                district = district_map.get(district_key, random.choice(districts))

                # Initialize sequence counter for district
                if district.code not in voter_sequence:
                    voter_sequence[district.code] = 1
                else:
                    voter_sequence[district.code] += 1

                # Select constituency from same district
                district_constituencies = [c for c in constituencies if c.district_id == district.id]
                constituency = random.choice(district_constituencies) if district_constituencies else random.choice(constituencies)

                # Generate demographics
                gender = weighted_random(GENDER_DISTRIBUTION)
                age = get_age_from_distribution()
                first_name, middle_name, last_name = generate_tamil_name(gender)

                # Generate voter ID
                voter_id = generate_voter_id(district.code, voter_sequence[district.code])

                # Phone/Email based on demographics (young/educated more likely to have)
                has_phone = random.random() < 0.70
                has_email = random.random() < 0.25
                if age <= 35:
                    has_email = random.random() < 0.40  # Young people more likely to have email

                # Party affiliation
                party = weighted_random(PARTY_AFFILIATION)

                # Sentiment (TVK supporters more positive)
                if party == 'tvk':
                    sentiment = random.choices(
                        ['strong_supporter', 'supporter', 'neutral'],
                        weights=[0.40, 0.50, 0.10],
                        k=1
                    )[0]
                else:
                    sentiment = weighted_random(SENTIMENT_DISTRIBUTION)

                # Influence level
                influence = weighted_random(INFLUENCE_DISTRIBUTION)
                is_opinion_leader = influence == 'high'

                # Contact history
                last_contacted_days = random.randint(0, 180)
                last_contacted = timezone.now() - timedelta(days=last_contacted_days) if random.random() > 0.40 else None
                contact_frequency = random.randint(0, 20)
                interaction_count = random.randint(0, 50)
                positive_ratio = 0.60 if sentiment in ['strong_supporter', 'supporter'] else 0.40
                positive_interactions = int(interaction_count * positive_ratio)
                negative_interactions = interaction_count - positive_interactions

                # Ward assignment (simulated)
                ward_number = random.randint(1, 50)
                ward = f"Ward-{ward_number}"

                # Generate address
                area = random.choice(TN_AREAS)
                address_line1 = f"{random.randint(1, 500)}, {fake.street_name()}"

                # Education
                education = weighted_random(EDUCATION_LEVELS)

                # Tags
                tags = random.choice(VOTER_TAGS) if random.random() > 0.60 else []
                if age <= 25:
                    tags.append('youth')
                if age <= 21:
                    tags.append('first_time')
                if is_opinion_leader:
                    tags.append('influencer')

                # Generate date of birth
                dob = datetime.now().date() - timedelta(days=age*365 + random.randint(0, 364))

                # Create voter object
                voter = Voter(
                    voter_id=voter_id,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    date_of_birth=dob,
                    age=age,
                    gender=gender,
                    phone=fake.phone_number()[:20] if has_phone else '',
                    alternate_phone=fake.phone_number()[:20] if has_phone and random.random() > 0.7 else '',
                    email=fake.email() if has_email else None,

                    # Address
                    address_line1=address_line1,
                    address_line2=area,
                    landmark=fake.street_name() if random.random() > 0.5 else '',
                    ward=ward,
                    constituency=constituency,
                    district=district,
                    state=tn_state,
                    pincode=f"{random.randint(600000, 643999)}",
                    latitude=Decimal(str(round(random.uniform(8.0, 13.5), 6))),
                    longitude=Decimal(str(round(random.uniform(76.0, 80.5), 6))),

                    # Political data
                    party_affiliation=party,
                    voting_history=get_voting_history(age),
                    sentiment=sentiment,
                    influence_level=influence,
                    is_opinion_leader=is_opinion_leader,

                    # Engagement
                    last_contacted_at=last_contacted,
                    contact_frequency=contact_frequency,
                    interaction_count=interaction_count,
                    positive_interactions=positive_interactions,
                    negative_interactions=negative_interactions,
                    preferred_communication=random.choice(['phone', 'sms', 'whatsapp', 'email', 'door_to_door']),

                    # Metadata
                    created_by=system_user,
                    is_active=True,
                    is_verified=random.random() > 0.30,
                    tags=tags,
                    notes=f"Education: {education}, Area: {area}"
                )

                batch.append(voter)

                # Update statistics
                stats['by_district'][district.name] = stats['by_district'].get(district.name, 0) + 1
                age_group = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
                stats['by_age_group'][age_group] = stats['by_age_group'].get(age_group, 0) + 1
                stats['by_gender'][gender] = stats['by_gender'].get(gender, 0) + 1
                stats['by_party'][party] = stats['by_party'].get(party, 0) + 1
                stats['by_sentiment'][sentiment] = stats['by_sentiment'].get(sentiment, 0) + 1
                stats['by_influence'][influence] = stats['by_influence'].get(influence, 0) + 1
                stats['by_education'][education] = stats['by_education'].get(education, 0) + 1
                if has_phone:
                    stats['with_phone'] += 1
                if has_email:
                    stats['with_email'] += 1
                if is_opinion_leader:
                    stats['opinion_leaders'] += 1

                # Bulk create when batch is full
                if len(batch) >= batch_size:
                    with transaction.atomic():
                        Voter.objects.bulk_create(batch, ignore_conflicts=True)
                    stats['total_created'] += len(batch)
                    self.stdout.write(f"Progress: {stats['total_created']:,} / {total_count:,} voters created ({(stats['total_created']/total_count*100):.1f}%)")
                    batch = []

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error generating voter {i+1}: {str(e)}"))
                continue

        # Create remaining voters
        if batch:
            with transaction.atomic():
                Voter.objects.bulk_create(batch, ignore_conflicts=True)
            stats['total_created'] += len(batch)

        # Display comprehensive statistics
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS(f'VOTER GENERATION COMPLETE'))
        self.stdout.write('=' * 80)
        self.stdout.write(f"\nTotal Voters Created: {stats['total_created']:,}\n")

        self.stdout.write(self.style.WARNING('\nDISTRICT DISTRIBUTION:'))
        for district, count in sorted(stats['by_district'].items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {district:25s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nAGE GROUP DISTRIBUTION:'))
        for age_group, count in sorted(stats['by_age_group'].items()):
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {age_group:15s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nGENDER DISTRIBUTION:'))
        for gender, count in stats['by_gender'].items():
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {gender.capitalize():15s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nPARTY AFFILIATION:'))
        for party, count in sorted(stats['by_party'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {party.upper():15s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nSENTIMENT DISTRIBUTION:'))
        for sentiment, count in sorted(stats['by_sentiment'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {sentiment:20s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nINFLUENCE LEVEL:'))
        for influence, count in stats['by_influence'].items():
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {influence.capitalize():15s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nEDUCATION DISTRIBUTION:'))
        for education, count in sorted(stats['by_education'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {education:20s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nCONTACT INFORMATION:'))
        phone_pct = (stats['with_phone'] / stats['total_created']) * 100
        email_pct = (stats['with_email'] / stats['total_created']) * 100
        self.stdout.write(f"  With Phone:        {stats['with_phone']:6,} ({phone_pct:5.2f}%)")
        self.stdout.write(f"  With Email:        {stats['with_email']:6,} ({email_pct:5.2f}%)")
        self.stdout.write(f"  Opinion Leaders:   {stats['opinion_leaders']:6,}")

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('Sample verification queries:'))
        self.stdout.write('  Voter.objects.filter(party_affiliation="tvk").count()')
        self.stdout.write('  Voter.objects.filter(age__lt=26).count()')
        self.stdout.write('  Voter.objects.filter(district__name="Chennai").count()')
        self.stdout.write('  Voter.objects.filter(is_opinion_leader=True).count()')
        self.stdout.write('=' * 80)
