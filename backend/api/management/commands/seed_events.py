"""
Management command to seed sample event data
Usage: python manage.py seed_events --count 100
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Event, Campaign, Constituency
from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal

fake = Faker('en_IN')


class Command(BaseCommand):
    help = 'Seeds the database with sample event data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of events to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} events...')

        # Get data
        users = list(User.objects.all())
        campaigns = list(Campaign.objects.all())
        constituencies = list(Constituency.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        events_created = 0
        for i in range(count):
            try:
                organizer = random.choice(users)
                volunteer_count = random.randint(5, 30)
                volunteers = random.sample(users, min(volunteer_count, len(users)))

                # Random dates
                start_datetime = fake.date_time_between(start_date='-3M', end_date='+3M')
                end_datetime = start_datetime + timedelta(hours=random.randint(2, 8))

                # Budget
                budget = Decimal(random.uniform(5000, 500000))
                expenses = Decimal(random.uniform(0, float(budget) * 1.1))  # Can go over budget

                event = Event.objects.create(
                    event_name=f"{fake.catch_phrase()} Event {i+1}",
                    event_type=random.choice(['rally', 'meeting', 'door_to_door', 'booth_visit', 'town_hall']),
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    location=fake.address(),
                    ward=f'Ward {random.randint(1, 50)}',
                    constituency=random.choice(constituencies) if constituencies else None,
                    latitude=fake.latitude(),
                    longitude=fake.longitude(),
                    expected_attendance=random.randint(50, 5000),
                    actual_attendance=random.randint(0, 5000),
                    organizer=organizer,
                    campaign=random.choice(campaigns) if campaigns and random.random() > 0.3 else None,
                    budget=budget,
                    expenses=expenses,
                    status=random.choice(['planned', 'ongoing', 'completed', 'cancelled']),
                    notes=fake.paragraph(nb_sentences=3) if random.random() > 0.5 else '',
                    photos=[
                        f'https://example.com/photos/event{i}_{j}.jpg'
                        for j in range(random.randint(0, 5))
                    ] if random.random() > 0.6 else [],
                )

                # Add volunteers
                event.volunteers.set(volunteers)

                events_created += 1

                if events_created % 20 == 0:
                    self.stdout.write(f'Created {events_created} events...')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating event: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {events_created} events'))
