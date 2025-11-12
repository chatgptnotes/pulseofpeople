"""
Management command to clean up all test user data from Django and Supabase
Keeps master data (organizations, districts, constituencies)

Usage:
    python manage.py cleanup_test_users --confirm
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile, Organization
from supabase import create_client
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Clean up all test user data from Django and Supabase'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all user data',
        )
        parser.add_argument(
            '--keep-admin',
            action='store_true',
            help='Keep admin@tvk.com account',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(self.style.ERROR('⚠️  This will DELETE ALL user data!'))
            self.stdout.write('Run with --confirm flag to proceed')
            self.stdout.write('\nCommand: python manage.py cleanup_test_users --confirm')
            return

        self.stdout.write(self.style.WARNING('=' * 80))
        self.stdout.write(self.style.WARNING('🧹 CLEANING UP TEST USER DATA'))
        self.stdout.write(self.style.WARNING('=' * 80))

        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_service_key:
            self.stdout.write(self.style.ERROR('❌ Supabase credentials not found in environment'))
            return

        self.supabase = create_client(supabase_url, supabase_service_key)
        self.keep_admin = options.get('keep_admin', False)

        # Step 1: Count current data
        self.show_current_counts()

        # Step 2: Clean Django data
        self.clean_django_users()

        # Step 3: Clean Supabase auth.users
        self.clean_supabase_users()

        # Step 4: Show final counts
        self.show_final_counts()

        self.stdout.write(self.style.SUCCESS('\n✅ Cleanup complete!'))

    def show_current_counts(self):
        self.stdout.write('\n📊 Current Data Counts:')
        self.stdout.write('-' * 80)

        # Django counts
        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()

        self.stdout.write(f'Django auth_user: {total_users}')
        self.stdout.write(f'Django api_userprofile: {total_profiles}')

        # Count by role
        for role in ['superadmin', 'admin', 'manager', 'analyst', 'user']:
            count = UserProfile.objects.filter(role=role).count()
            if count > 0:
                self.stdout.write(f'  - {role}: {count}')

        # Supabase count
        try:
            # Get all Supabase users
            result = self.supabase.auth.admin.list_users()
            supabase_count = len(result) if hasattr(result, '__len__') else 0
            self.stdout.write(f'Supabase auth.users: {supabase_count}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Could not count Supabase users: {e}'))

    def clean_django_users(self):
        self.stdout.write('\n🧹 Cleaning Django Database:')
        self.stdout.write('-' * 80)

        if self.keep_admin:
            # Keep admin@tvk.com
            admin_email = 'admin@tvk.com'

            # Delete all profiles except admin
            deleted_profiles = UserProfile.objects.exclude(
                user__email=admin_email
            ).delete()

            # Delete all users except admin
            deleted_users = User.objects.exclude(email=admin_email).delete()

            self.stdout.write(f'✅ Deleted {deleted_profiles[0]} UserProfiles (kept {admin_email})')
            self.stdout.write(f'✅ Deleted {deleted_users[0]} Users (kept {admin_email})')
        else:
            # Delete all profiles
            deleted_profiles = UserProfile.objects.all().delete()

            # Delete all users
            deleted_users = User.objects.all().delete()

            self.stdout.write(f'✅ Deleted {deleted_profiles[0]} UserProfiles')
            self.stdout.write(f'✅ Deleted {deleted_users[0]} Users')

    def clean_supabase_users(self):
        self.stdout.write('\n🧹 Cleaning Supabase Auth:')
        self.stdout.write('-' * 80)

        try:
            # Get all Supabase users
            result = self.supabase.auth.admin.list_users()
            users = result if isinstance(result, list) else []

            deleted_count = 0
            kept_admin = False

            for user in users:
                user_email = user.email if hasattr(user, 'email') else 'unknown'
                user_id = user.id if hasattr(user, 'id') else None

                if not user_id:
                    continue

                # Keep admin@tvk.com if flag is set
                if self.keep_admin and user_email == 'admin@tvk.com':
                    self.stdout.write(f'  ⏭️  Keeping: {user_email}')
                    kept_admin = True
                    continue

                # Delete user from Supabase
                try:
                    self.supabase.auth.admin.delete_user(user_id)
                    deleted_count += 1

                    if deleted_count % 50 == 0:
                        self.stdout.write(f'  ✅ Deleted {deleted_count} users...')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  ⚠️  Failed to delete {user_email}: {e}'))

            self.stdout.write(f'✅ Deleted {deleted_count} Supabase users')
            if kept_admin:
                self.stdout.write('  ✅ Kept admin@tvk.com')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error cleaning Supabase: {e}'))

    def show_final_counts(self):
        self.stdout.write('\n📊 Final Data Counts:')
        self.stdout.write('-' * 80)

        # Django counts
        total_users = User.objects.count()
        total_profiles = UserProfile.objects.count()

        self.stdout.write(f'Django auth_user: {total_users}')
        self.stdout.write(f'Django api_userprofile: {total_profiles}')

        # Organizations (should remain)
        total_orgs = Organization.objects.count()
        self.stdout.write(f'Organizations: {total_orgs} (preserved)')

        # Supabase count
        try:
            result = self.supabase.auth.admin.list_users()
            supabase_count = len(result) if hasattr(result, '__len__') else 0
            self.stdout.write(f'Supabase auth.users: {supabase_count}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Could not count Supabase users: {e}'))

        self.stdout.write('\n✅ Master data preserved:')
        self.stdout.write('  - Organizations')
        self.stdout.write('  - States')
        self.stdout.write('  - Districts')
        self.stdout.write('  - Constituencies (234)')
