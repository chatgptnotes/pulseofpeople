"""
Management command to seed sample campaign data
Usage: python manage.py seed_campaigns --count 50
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import Campaign, Constituency
from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal

fake = Faker('en_IN')


class Command(BaseCommand):
    help = 'Seeds the database with sample campaign data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of campaigns to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        self.stdout.write(f'Creating {count} campaigns...')

        # Get users and constituencies
        users = list(User.objects.all())
        constituencies = list(Constituency.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create users first.'))
            return

        if not constituencies:
            self.stdout.write(self.style.ERROR('No constituencies found. Please run seed_political_data first.'))
            return

        campaigns_created = 0
        for i in range(count):
            try:
                campaign_manager = random.choice(users)
                team_size = random.randint(3, 15)
                team_members = random.sample(users, min(team_size, len(users)))

                # Random dates
                start_date = fake.date_between(start_date='-6M', end_date='+3M')
                end_date = start_date + timedelta(days=random.randint(30, 180))

                # Budget
                budget = Decimal(random.uniform(100000, 10000000))
                spent = Decimal(random.uniform(0, float(budget) * 0.8))

                campaign = Campaign.objects.create(
                    campaign_name=f"{fake.catch_phrase()} Campaign {i+1}",
                    campaign_type=random.choice(['election', 'awareness', 'issue_based', 'door_to_door']),
                    start_date=start_date,
                    end_date=end_date,
                    status=random.choice(['planning', 'active', 'completed', 'cancelled']),
                    budget=budget,
                    spent_amount=spent,
                    target_constituency=random.choice(constituencies) if random.random() > 0.5 else None,
                    target_audience=fake.paragraph(nb_sentences=2),
                    campaign_manager=campaign_manager,
                    goals={
                        'voter_outreach': random.randint(1000, 50000),
                        'events': random.randint(5, 50),
                        'social_media_reach': random.randint(10000, 500000),
                    },
                    metrics={
                        'voters_contacted': random.randint(0, 30000),
                        'events_held': random.randint(0, 30),
                        'social_reach': random.randint(0, 300000),
                        'engagement_rate': round(random.uniform(0.1, 0.5), 2),
                    },
                    created_by=campaign_manager,
                )

                # Add team members
                campaign.team_members.set(team_members)

                campaigns_created += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error creating campaign: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {campaigns_created} campaigns'))
