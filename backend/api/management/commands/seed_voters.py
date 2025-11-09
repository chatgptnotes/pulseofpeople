"""
Management command to seed sample voter data
Usage: python manage.py seed_voters --count 1000
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Voter, State, District, Constituency
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('en_IN')  # Indian locale for realistic data


class Command(BaseCommand):
    help = 'Seeds the database with sample voter data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=1000,
            help='Number of voters to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} voters...')

        # Get or create a default user for created_by
        default_user, _ = User.objects.get_or_create(
            username='system',
            defaults={'email': 'system@pulseofpeople.com'}
        )

        # Get constituencies, districts, states
        states = list(State.objects.all())
        districts = list(District.objects.all())
        constituencies = list(Constituency.objects.all())

        if not constituencies:
            self.stdout.write(self.style.ERROR('No constituencies found. Please run seed_political_data first.'))
            return

        voters_created = 0
        for i in range(count):
            try:
                # Random location
                constituency = random.choice(constituencies)
                district = constituency.district or random.choice(districts)
                state = constituency.state or random.choice(states)

                # Generate voter
                voter = Voter.objects.create(
                    voter_id=fake.unique.bothify(text='VOTER######'),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    middle_name=fake.first_name() if random.random() > 0.5 else '',
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=90),
                    age=random.randint(18, 90),
                    gender=random.choice(['male', 'female', 'other']),
                    phone=fake.phone_number()[:20],
                    alternate_phone=fake.phone_number()[:20] if random.random() > 0.7 else '',
                    email=fake.email() if random.random() > 0.6 else None,

                    # Address
                    address_line1=fake.street_address(),
                    address_line2=fake.secondary_address() if random.random() > 0.5 else '',
                    landmark=fake.street_name() if random.random() > 0.5 else '',
                    ward=f'Ward {random.randint(1, 50)}',
                    constituency=constituency,
                    district=district,
                    state=state,
                    pincode=fake.postcode(),
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),

                    # Political Data
                    party_affiliation=random.choice(['bjp', 'congress', 'aap', 'tvk', 'dmk', 'aiadmk', 'neutral', 'unknown', 'other']),
                    voting_history=[
                        {'year': year, 'voted': random.choice([True, False])}
                        for year in [2024, 2023, 2022, 2021, 2020]
                    ],
                    sentiment=random.choice(['strong_supporter', 'supporter', 'neutral', 'opposition', 'strong_opposition']),
                    influence_level=random.choice(['high', 'medium', 'low']),
                    is_opinion_leader=random.random() > 0.9,

                    # Engagement
                    last_contacted_at=fake.date_time_between(start_date='-1y', end_date='now') if random.random() > 0.5 else None,
                    contact_frequency=random.randint(0, 10),
                    interaction_count=random.randint(0, 20),
                    positive_interactions=random.randint(0, 10),
                    negative_interactions=random.randint(0, 5),
                    preferred_communication=random.choice(['phone', 'sms', 'whatsapp', 'email', 'door_to_door']),

                    # Metadata
                    created_by=default_user,
                    is_active=random.random() > 0.1,
                    is_verified=random.random() > 0.3,
                    tags=[fake.word(), fake.word()] if random.random() > 0.7 else [],
                    notes=fake.sentence() if random.random() > 0.8 else '',
                )

                voters_created += 1
                if voters_created % 100 == 0:
                    self.stdout.write(f'Created {voters_created} voters...')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating voter: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {voters_created} voters'))
