from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a default superuser for testing'

    def handle(self, *args, **options):
        # Check if user already exists
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('User "admin" already exists'))
            return

        # Create superuser
        user = User.objects.create_superuser(
            username='admin',
            email='admin@tvk.com',
            password='admin123',
            first_name='Super',
            last_name='Admin'
        )

        # Create or update profile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'role': 'superadmin',
                'phone': '9876543210',
                'organization': None,
            }
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created superuser:'))
        self.stdout.write(f'  Username: admin')
        self.stdout.write(f'  Email: admin@tvk.com')
        self.stdout.write(f'  Password: admin123')
        self.stdout.write(f'  Role: {profile.role}')
