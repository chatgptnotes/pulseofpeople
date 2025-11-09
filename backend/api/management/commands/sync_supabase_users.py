"""
Django management command to manually sync Supabase users
Usage: python manage.py sync_supabase_users [--email EMAIL]
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.utils import sync_supabase_user, ensure_user_profile_exists
from api.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Synchronize Supabase users with Django database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Sync specific user by email',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Ensure all existing users have profiles',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        email = options.get('email')
        sync_all = options.get('all')
        dry_run = options.get('dry_run')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        if email:
            # Sync specific user
            self.sync_user_by_email(email, dry_run)
        elif sync_all:
            # Ensure all users have profiles
            self.ensure_all_profiles(dry_run)
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Please specify --email or --all. '
                    'Use --help for more information.'
                )
            )

    def sync_user_by_email(self, email, dry_run=False):
        """Sync a specific user by email"""
        try:
            user = User.objects.get(email=email)
            self.stdout.write(f'Found user: {email}')

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f'Would sync user: {email}')
                )
                return

            # Check if profile exists
            try:
                profile = user.profile
                self.stdout.write(
                    f'  Profile exists: Role={profile.role}, '
                    f'Org={profile.organization.name if profile.organization else "None"}'
                )
            except UserProfile.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING('  No profile found - creating default profile')
                )
                from api.signals import ensure_user_profile_exists
                profile = ensure_user_profile_exists(user)
                self.stdout.write(
                    self.style.SUCCESS(f'  Created profile with role: {profile.role}')
                )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User not found: {email}')
            )

    def ensure_all_profiles(self, dry_run=False):
        """Ensure all users have profiles"""
        users = User.objects.all()
        total = users.count()
        missing_profiles = 0
        existing_profiles = 0

        self.stdout.write(f'Processing {total} users...')

        for user in users:
            try:
                profile = user.profile
                existing_profiles += 1
                if dry_run:
                    self.stdout.write(f'  {user.email}: Profile exists (role={profile.role})')
            except UserProfile.DoesNotExist:
                missing_profiles += 1
                if dry_run:
                    self.stdout.write(
                        self.style.WARNING(f'  {user.email}: Would create profile')
                    )
                else:
                    from api.signals import ensure_user_profile_exists
                    profile = ensure_user_profile_exists(user)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  {user.email}: Created profile (role={profile.role})'
                        )
                    )

        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(f'Total users: {total}')
        self.stdout.write(f'Existing profiles: {existing_profiles}')
        self.stdout.write(f'Missing profiles: {missing_profiles}')

        if missing_profiles > 0:
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f'\nWould create {missing_profiles} profiles. '
                        'Run without --dry-run to apply changes.'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'\nCreated {missing_profiles} profiles')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nAll users have profiles!')
            )
