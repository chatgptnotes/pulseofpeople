"""
Management command to seed sample voter interaction data
Usage: python manage.py seed_interactions --count 500
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import VoterInteraction, Voter
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker('en_IN')


class Command(BaseCommand):
    help = 'Seeds the database with sample voter interaction data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=500,
            help='Number of interactions to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} voter interactions...')

        # Get voters and users
        voters = list(Voter.objects.all())
        users = list(User.objects.all())

        if not voters:
            self.stdout.write(self.style.ERROR('No voters found. Please run seed_voters first.'))
            return

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        interactions_created = 0
        for i in range(count):
            try:
                voter = random.choice(voters)
                contacted_by = random.choice(users)

                interaction = VoterInteraction.objects.create(
                    voter=voter,
                    interaction_type=random.choice(['phone_call', 'door_visit', 'event_meeting', 'sms', 'email', 'whatsapp']),
                    contacted_by=contacted_by,
                    duration_minutes=random.randint(5, 60) if random.random() > 0.3 else None,
                    sentiment=random.choice(['positive', 'neutral', 'negative']),
                    issues_discussed=[
                        random.choice(['Education', 'Healthcare', 'Infrastructure', 'Employment', 'Agriculture', 'Water', 'Electricity'])
                        for _ in range(random.randint(1, 4))
                    ],
                    promises_made=fake.sentence() if random.random() > 0.6 else '',
                    follow_up_required=random.random() > 0.7,
                    follow_up_date=fake.date_between(start_date='now', end_date='+30d') if random.random() > 0.5 else None,
                    notes=fake.paragraph(nb_sentences=2) if random.random() > 0.5 else '',
                )

                interactions_created += 1

                if interactions_created % 100 == 0:
                    self.stdout.write(f'Created {interactions_created} interactions...')

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating interaction: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {interactions_created} interactions'))
