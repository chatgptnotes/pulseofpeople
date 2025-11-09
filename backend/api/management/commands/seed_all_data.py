"""
Management command to seed ALL sample data for the platform
Usage: python manage.py seed_all_data
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Seeds the database with all sample data for the political platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick mode with fewer records',
        )

    def handle(self, *args, **options):
        quick = options['quick']

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Starting comprehensive data seeding...'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Step 1: Seed political data (states, districts, constituencies)
        self.stdout.write(self.style.WARNING('\n1. Seeding political geographic data...'))
        try:
            call_command('seed_political_data')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding political data: {e}'))

        # Step 2: Seed voters
        self.stdout.write(self.style.WARNING('\n2. Seeding voters...'))
        voter_count = 500 if quick else 1000
        try:
            call_command('seed_voters', count=voter_count)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding voters: {e}'))

        # Step 3: Seed campaigns
        self.stdout.write(self.style.WARNING('\n3. Seeding campaigns...'))
        campaign_count = 25 if quick else 50
        try:
            call_command('seed_campaigns', count=campaign_count)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding campaigns: {e}'))

        # Step 4: Seed voter interactions
        self.stdout.write(self.style.WARNING('\n4. Seeding voter interactions...'))
        interaction_count = 250 if quick else 500
        try:
            call_command('seed_interactions', count=interaction_count)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding interactions: {e}'))

        # Step 5: Seed events
        self.stdout.write(self.style.WARNING('\n5. Seeding events...'))
        event_count = 50 if quick else 100
        try:
            call_command('seed_events', count=event_count)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding events: {e}'))

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('Data seeding complete!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write(f'  - Political data: States, Districts, Constituencies')
        self.stdout.write(f'  - Voters: ~{voter_count}')
        self.stdout.write(f'  - Campaigns: ~{campaign_count}')
        self.stdout.write(f'  - Voter Interactions: ~{interaction_count}')
        self.stdout.write(f'  - Events: ~{event_count}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('You can now test the API endpoints!'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
