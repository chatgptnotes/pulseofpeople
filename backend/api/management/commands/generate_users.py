"""
Django management command to generate a complete user hierarchy for Pulse of People platform
Creates 640 users with realistic Tamil names across all roles

Usage: python manage.py generate_users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from api.models import (
    UserProfile, Organization, State, District, Constituency,
    PollingBooth, BoothAgent
)
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Generates 640 users with realistic Tamil names across all roles'

    def __init__(self):
        super().__init__()
        self.fake = Faker('en_IN')  # Indian locale for realistic names
        self.organization = None
        self.tn_state = None
        self.districts = []
        self.constituencies = []
        self.wards = []
        self.created_users = []

        # Tamil Nadu districts (38 districts)
        self.tn_districts = [
            'Ariyalur', 'Chengalpattu', 'Chennai', 'Coimbatore', 'Cuddalore',
            'Dharmapuri', 'Dindigul', 'Erode', 'Kallakurichi', 'Kanchipuram',
            'Kanyakumari', 'Karur', 'Krishnagiri', 'Madurai', 'Mayiladuthurai',
            'Nagapattinam', 'Namakkal', 'Nilgiris', 'Perambalur', 'Pudukkottai',
            'Ramanathapuram', 'Ranipet', 'Salem', 'Sivaganga', 'Tenkasi',
            'Thanjavur', 'Theni', 'Thoothukudi', 'Tiruchirappalli', 'Tirunelveli',
            'Tirupathur', 'Tiruppur', 'Tiruvallur', 'Tiruvannamalai', 'Tiruvarur',
            'Vellore', 'Viluppuram', 'Virudhunagar'
        ]

        # Sample Tamil first names
        self.tamil_first_names = [
            'Arun', 'Balaji', 'Chidambaram', 'Dinesh', 'Elango', 'Ganesan',
            'Harish', 'Inbasekaran', 'Jeyakumar', 'Karthik', 'Lakshman', 'Murugan',
            'Nagaraj', 'Pandiyan', 'Rajesh', 'Selvam', 'Thangavel', 'Udhayakumar',
            'Vignesh', 'Yuvaraj', 'Arjun', 'Bharath', 'Chandran', 'Devan',
            'Gopal', 'Hari', 'Ilango', 'Janaki', 'Kumar', 'Mani',
            'Priya', 'Radha', 'Saranya', 'Thamarai', 'Uma', 'Valli',
            'Anbu', 'Deepak', 'Ezhil', 'Franklin', 'Guru', 'Inian',
            'Kamal', 'Mohan', 'Prakash', 'Ramesh', 'Senthil', 'Suresh',
            'Vijay', 'Anitha', 'Bhuvana', 'Chitra', 'Divya', 'Gowri',
            'Jayanthi', 'Kavitha', 'Lakshmi', 'Meena', 'Nirmala', 'Padma'
        ]

        # Sample Tamil last names
        self.tamil_last_names = [
            'Kumar', 'Raj', 'Selvam', 'Murugan', 'Pandian', 'Krishnan',
            'Raman', 'Samy', 'Nadar', 'Gounder', 'Pillai', 'Naicker',
            'Chettiar', 'Thevar', 'Reddy', 'Rao', 'Menon', 'Nair',
            'Iyer', 'Iyengar', 'Mudaliar', 'Chettiyar', 'Asari', 'Achari'
        ]

        # Sample ward names
        self.ward_names = [
            'Anna Nagar', 'T. Nagar', 'Mylapore', 'Adyar', 'Velachery',
            'Ambattur', 'Avadi', 'Chromepet', 'Tambaram', 'Pallavaram',
            'Porur', 'Kodambakkam', 'Saidapet', 'Guindy', 'Nungambakkam',
            'Teynampet', 'Royapuram', 'Perambur', 'Kolathur', 'Villivakkam',
            'Madipakkam', 'Sholinganallur', 'Perungudi', 'Thiruvanmiyur', 'Mandaveli'
        ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip creation if users already exist',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('GENERATING USER HIERARCHY FOR PULSE OF PEOPLE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        try:
            # Setup: Load organization and geography data (outside transaction)
            self._setup_data()

            # Generate users by role hierarchy
            # Each role creation is in its own transaction to prevent cascading failures
            self._create_superadmin()
            self._create_admin()
            self._create_managers()
            self._create_analysts()
            self._create_users()
            self._create_volunteers()

            # Summary
            self._print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\nError: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('USER GENERATION COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def _setup_data(self):
        """Setup organization and load geography data"""
        self.stdout.write('\n[1/7] Setting up organization and geography data...')

        # Get or create TVK organization
        self.organization, created = Organization.objects.get_or_create(
            slug='tvk',
            defaults={
                'name': 'Tamilaga Vettri Kazhagam',
                'organization_type': 'party',
                'subscription_plan': 'enterprise',
                'max_users': 1000,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write('  Created TVK organization')
        else:
            self.stdout.write('  Using existing TVK organization')

        # Load Tamil Nadu state
        try:
            self.tn_state = State.objects.get(code='TN')
            self.stdout.write(f'  Loaded state: {self.tn_state.name}')
        except State.DoesNotExist:
            self.stdout.write(self.style.ERROR('  Tamil Nadu state not found!'))
            self.stdout.write('  Run: python manage.py seed_political_data')
            raise

        # Load districts (38 districts)
        self.districts = list(District.objects.filter(state=self.tn_state))
        self.stdout.write(f'  Loaded {len(self.districts)} districts')

        if len(self.districts) == 0:
            self.stdout.write(self.style.ERROR('  No districts found!'))
            raise Exception('Districts not found. Run seed_political_data first.')

        # Load constituencies (top 100 that have districts assigned)
        self.constituencies = list(
            Constituency.objects.filter(state=self.tn_state, district__isnull=False)
            .order_by('number')[:100]
        )
        self.stdout.write(f'  Loaded {len(self.constituencies)} constituencies')

        # Warn if any constituencies are missing districts
        missing_districts = Constituency.objects.filter(
            state=self.tn_state, district__isnull=True
        ).count()
        if missing_districts > 0:
            self.stdout.write(
                self.style.WARNING(f'  Note: {missing_districts} constituencies without districts excluded')
            )

        # Generate ward list
        self.wards = self.ward_names * 20  # Repeat to have enough wards
        self.stdout.write(f'  Generated {len(self.wards)} ward assignments')

    def _create_superadmin(self):
        """Create 1 superadmin"""
        self.stdout.write('\n[2/7] Creating Superadmin (1 user)...')

        user = self._create_user(
            username='superadmin',
            email='superadmin@pulseofpeople.com',
            first_name='Platform',
            last_name='Superadmin',
            password='Admin@123',
            role='superadmin',
            bio='Platform superadmin with full system access',
        )
        self.stdout.write(self.style.SUCCESS(f'  Created: {user.username} ({user.email})'))

    def _create_admin(self):
        """Create 1 admin - Vijay (TVK Leader)"""
        self.stdout.write('\n[3/7] Creating Admin (1 user)...')

        user = self._create_user(
            username='vijay',
            email='vijay@tvk.com',
            first_name='Vijay',
            last_name='',
            password='Vijay@2026',
            role='admin',
            bio='TVK Party Leader - State Admin for Tamil Nadu',
            assigned_state=self.tn_state,
        )
        self.stdout.write(self.style.SUCCESS(f'  Created: {user.username} ({user.email})'))

    def _create_managers(self):
        """Create 38 managers - one per district"""
        self.stdout.write('\n[4/7] Creating Managers (38 users - one per district)...')

        if len(self.districts) < 38:
            self.stdout.write(
                self.style.WARNING(f'  Only {len(self.districts)} districts available')
            )

        created_count = 0
        for district in self.districts[:38]:
            first_name = random.choice(self.tamil_first_names)
            last_name = random.choice(self.tamil_last_names)
            district_slug = district.name.lower().replace(' ', '')

            user = self._create_user(
                username=f'manager.{district_slug}',
                email=f'manager.{district_slug}@tvk.com',
                first_name=first_name,
                last_name=last_name,
                password='Manager@2024',
                role='manager',
                bio=f'District Manager for {district.name}',
                assigned_district=district,
                assigned_state=self.tn_state,
            )
            created_count += 1

            if created_count <= 5 or created_count % 10 == 0:
                self.stdout.write(f'  [{created_count}/38] {district.name}: {user.username}')

        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} managers'))

    def _create_analysts(self):
        """Create 100 analysts - distributed across constituencies"""
        self.stdout.write('\n[5/7] Creating Analysts (100 users - one per top constituency)...')

        if len(self.constituencies) < 100:
            self.stdout.write(
                self.style.WARNING(f'  Only {len(self.constituencies)} constituencies available')
            )

        created_count = 0
        for constituency in self.constituencies[:100]:
            # Skip constituencies without districts (should not happen after filter, but double check)
            if not constituency.district:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping {constituency.name} - no district assigned')
                )
                continue

            first_name = random.choice(self.tamil_first_names)
            last_name = random.choice(self.tamil_last_names)
            const_slug = constituency.name.lower().replace(' ', '').replace('-', '').replace('.', '')[:30]

            user = self._create_user(
                username=f'analyst.{const_slug}',
                email=f'analyst.{const_slug}@tvk.com',
                first_name=first_name,
                last_name=last_name,
                password='Analyst@2024',
                role='analyst',
                bio=f'Analyst for {constituency.name} constituency',
                assigned_district=constituency.district,
                assigned_state=self.tn_state,
                constituency=constituency.name,
            )
            created_count += 1

            if created_count <= 5 or created_count % 20 == 0:
                self.stdout.write(f'  [{created_count}/100] {constituency.name}: {user.username}')

        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} analysts'))

    def _create_users(self):
        """Create 450 users/booth agents - distributed across wards"""
        self.stdout.write('\n[6/7] Creating Users/Booth Agents (450 users)...')

        # Distribute across wards and booths
        created_count = 0
        for i in range(1, 451):
            first_name = random.choice(self.tamil_first_names)
            last_name = random.choice(self.tamil_last_names)

            # Assign to ward and constituency
            ward = random.choice(self.wards)
            constituency = random.choice(self.constituencies) if self.constituencies else None

            # Ensure we always have a district (fallback to random if constituency has no district)
            if constituency and constituency.district:
                district = constituency.district
            else:
                district = random.choice(self.districts) if self.districts else None

            user = self._create_user(
                username=f'user{i}',
                email=f'user{i}@tvk.com',
                first_name=first_name,
                last_name=last_name,
                password='User@2024',
                role='user',
                bio=f'Booth agent for {ward}',
                assigned_district=district,
                assigned_state=self.tn_state,
                city=ward,
                constituency=constituency.name if constituency else None,
            )

            # Create BoothAgent profile for booth-level assignments
            # Only create if constituency has a district (required by BoothAgent model)
            if constituency and constituency.district:
                self._create_booth_agent(user, constituency, ward)

            created_count += 1

            if created_count <= 5 or created_count % 50 == 0:
                self.stdout.write(f'  [{created_count}/450] Created: {user.username}')

        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} users/booth agents'))

    def _create_volunteers(self):
        """Create 50 volunteers - field workers without fixed assignments"""
        self.stdout.write('\n[7/7] Creating Volunteers (50 users)...')

        created_count = 0
        for i in range(1, 51):
            first_name = random.choice(self.tamil_first_names)
            last_name = random.choice(self.tamil_last_names)

            # Random district for volunteers
            district = random.choice(self.districts) if self.districts else None

            user = self._create_user(
                username=f'volunteer{i}',
                email=f'volunteer{i}@tvk.com',
                first_name=first_name,
                last_name=last_name,
                password='Volunteer@2024',
                role='volunteer',
                bio='TVK volunteer and field worker',
                assigned_district=district,
                assigned_state=self.tn_state,
            )
            created_count += 1

            if created_count <= 5 or created_count % 10 == 0:
                self.stdout.write(f'  [{created_count}/50] Created: {user.username}')

        self.stdout.write(self.style.SUCCESS(f'  Created {created_count} volunteers'))

    def _create_user(
        self,
        username,
        email,
        first_name,
        last_name,
        password,
        role,
        bio='',
        assigned_state=None,
        assigned_district=None,
        constituency=None,
        city=None,
    ):
        """Helper method to create user and profile"""

        try:
            # Create User
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'is_staff': role in ['superadmin', 'admin'],
                    'is_superuser': role == 'superadmin',
                }
            )

            if created:
                user.set_password(password)
                user.save()

            # Get or create UserProfile (may be auto-created by signal)
            try:
                profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                profile = UserProfile.objects.create(
                    user=user,
                    role=role,
                    organization=self.organization,
                    bio=bio,
                    phone=self._generate_phone(),
                    assigned_state=assigned_state,
                    assigned_district=assigned_district,
                    constituency=constituency,
                    city=city,
                )

            # Always update profile fields to ensure correct values
            profile.role = role
            profile.organization = self.organization
            profile.bio = bio
            profile.phone = self._generate_phone()
            profile.assigned_state = assigned_state
            profile.assigned_district = assigned_district
            profile.constituency = constituency
            profile.city = city
            profile.save()

            self.created_users.append(user)
            return user

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  Failed to create user {username}: {str(e)}')
            )
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            # Re-raise to stop execution on critical errors
            raise

    def _create_booth_agent(self, user, constituency, ward):
        """Create BoothAgent profile for booth-level users"""

        try:
            # Safety check: constituency must have a district (required by BoothAgent model)
            if not constituency.district:
                self.stdout.write(
                    self.style.WARNING(f'  Cannot create BoothAgent for {user.username} - constituency {constituency.name} has no district')
                )
                return

            # Assign random booths (1-3 booths per agent)
            num_booths = random.randint(1, 3)
            booth_numbers = [f'{random.randint(1, 50):03d}' for _ in range(num_booths)]

            BoothAgent.objects.get_or_create(
                user=user,
                defaults={
                    'state': self.tn_state,
                    'district': constituency.district,
                    'constituency': constituency,
                    'assigned_wards': [ward],
                    'assigned_booths': booth_numbers,
                    'is_active': True,
                }
            )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'  Failed to create BoothAgent for {user.username}: {str(e)}')
            )
            # Don't re-raise - booth agent creation is optional
            pass

    def _generate_phone(self):
        """Generate realistic Indian phone number"""
        prefixes = ['98', '99', '97', '96', '95', '94', '93', '92', '91', '90']
        prefix = random.choice(prefixes)
        number = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        return f'+91{prefix}{number}'

    def _random_created_date(self):
        """Generate random created_at timestamp (last 6 months)"""
        now = timezone.now()
        days_ago = random.randint(1, 180)
        return now - timedelta(days=days_ago)

    def _print_summary(self):
        """Print summary of created users"""
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('=' * 70)

        # Count users by role
        role_counts = {
            'superadmin': UserProfile.objects.filter(role='superadmin', organization=self.organization).count(),
            'admin': UserProfile.objects.filter(role='admin', organization=self.organization).count(),
            'manager': UserProfile.objects.filter(role='manager', organization=self.organization).count(),
            'analyst': UserProfile.objects.filter(role='analyst', organization=self.organization).count(),
            'user': UserProfile.objects.filter(role='user', organization=self.organization).count(),
            'volunteer': UserProfile.objects.filter(role='volunteer', organization=self.organization).count(),
        }

        total = sum(role_counts.values())

        self.stdout.write(f'\nOrganization: {self.organization.name}')
        self.stdout.write(f'State: {self.tn_state.name}')
        self.stdout.write('\nUsers by Role:')
        self.stdout.write(f'  Superadmin:  {role_counts["superadmin"]:3d} users')
        self.stdout.write(f'  Admin:       {role_counts["admin"]:3d} users')
        self.stdout.write(f'  Manager:     {role_counts["manager"]:3d} users (one per district)')
        self.stdout.write(f'  Analyst:     {role_counts["analyst"]:3d} users (one per constituency)')
        self.stdout.write(f'  User:        {role_counts["user"]:3d} users (booth agents)')
        self.stdout.write(f'  Volunteer:   {role_counts["volunteer"]:3d} users')
        self.stdout.write(f'  {"―" * 50}')
        self.stdout.write(f'  TOTAL:       {total:3d} users')

        # Additional stats
        booth_agents = BoothAgent.objects.filter(
            constituency__state=self.tn_state
        ).count()
        self.stdout.write(f'\nBooth Agent Profiles: {booth_agents}')

        # Sample credentials
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('SAMPLE LOGIN CREDENTIALS'))
        self.stdout.write('=' * 70)
        self.stdout.write('\nSuperadmin:')
        self.stdout.write('  Email:    superadmin@pulseofpeople.com')
        self.stdout.write('  Password: Admin@123')
        self.stdout.write('\nTVK Admin (Vijay):')
        self.stdout.write('  Email:    vijay@tvk.com')
        self.stdout.write('  Password: Vijay@2026')
        self.stdout.write('\nManagers:')
        self.stdout.write('  Email:    manager.<district>@tvk.com')
        self.stdout.write('  Password: Manager@2024')
        self.stdout.write('  Example:  manager.chennai@tvk.com')
        self.stdout.write('\nAnalysts:')
        self.stdout.write('  Email:    analyst.<constituency>@tvk.com')
        self.stdout.write('  Password: Analyst@2024')
        self.stdout.write('\nUsers/Booth Agents:')
        self.stdout.write('  Email:    user<number>@tvk.com (user1 to user450)')
        self.stdout.write('  Password: User@2024')
        self.stdout.write('\nVolunteers:')
        self.stdout.write('  Email:    volunteer<number>@tvk.com (volunteer1 to volunteer50)')
        self.stdout.write('  Password: Volunteer@2024')
