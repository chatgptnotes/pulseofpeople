"""
Django management command to create a superadmin user

Usage:
    python manage.py createsuperadmin --email=vijay@tvk.com --name="Vijay TVK" --password=secure123

    Or use interactive mode:
    python manage.py createsuperadmin
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from api.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a superadmin user with UserProfile'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the superadmin',
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Full name of the superadmin',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superadmin',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number (optional)',
            default='',
        )

    def handle(self, *args, **options):
        # Get values from arguments or prompt
        email = options.get('email')
        name = options.get('name')
        password = options.get('password')
        phone = options.get('phone', '')

        # Interactive mode if arguments not provided
        if not email:
            email = input('Email address: ')

        if not email:
            raise CommandError('Email address is required')

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email {email} already exists!')

        if not name:
            name = input('Full name: ')

        if not name:
            name = email.split('@')[0]  # Default to email username

        if not password:
            from getpass import getpass
            password = getpass('Password: ')
            password_confirm = getpass('Password (again): ')

            if password != password_confirm:
                raise CommandError('Passwords do not match!')

        if not password or len(password) < 6:
            raise CommandError('Password must be at least 6 characters long')

        # Split name into first and last
        name_parts = name.split(' ', 1)
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Create username from email
        username = email.split('@')[0]

        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        try:
            # Create Django user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,  # Can access Django admin
                is_superuser=True  # Has all permissions
            )

            # Create UserProfile with superadmin role
            profile = UserProfile.objects.create(
                user=user,
                role='superadmin',
                phone=phone
            )

            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Superadmin created successfully!\n'
                f'   Email: {email}\n'
                f'   Username: {username}\n'
                f'   Name: {name}\n'
                f'   Role: superadmin\n'
                f'\nYou can now login with these credentials.'
            ))

        except Exception as e:
            raise CommandError(f'Failed to create superadmin: {str(e)}')
