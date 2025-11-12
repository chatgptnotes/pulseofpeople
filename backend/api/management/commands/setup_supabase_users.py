"""
Management command to set up TVK and DMK organizations with hierarchical users via Supabase Auth.

This command creates:
- 2 Organizations (TVK and DMK)
- 2 Admin accounts (one per organization)
- 38 District Managers for TVK (one per Tamil Nadu district)
- 234 Constituency Analysts for TVK (mapped to districts)
- ~2,340 Users for TVK (10 per analyst)

All users are created via Supabase Auth API for proper authentication.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_save
from api.models import Organization, UserProfile, District, Constituency, State
from supabase import create_client, Client
import os
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Set up TVK and DMK organizations with hierarchical users via Supabase Auth'

    def __init__(self):
        super().__init__()
        # Initialize Supabase Admin client
        supabase_url = os.getenv('SUPABASE_URL', 'https://iwtgbseaoztjbnvworyq.supabase.co')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_key or supabase_key == 'your-service-role-key-if-needed':
            raise ValueError('SUPABASE_SERVICE_ROLE_KEY not set in .env file')

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.tvk_org = None
        self.dmk_org = None

    # Tamil Nadu districts mapped to constituencies
    DISTRICT_CONSTITUENCIES = {
        'Ariyalur': ['Ariyalur', 'Jayankondam', 'Andimadam'],
        'Chengalpattu': ['Chengalpattu', 'Thiruporur', 'Madurantakam', 'Cheyyur', 'Maduranthakam'],
        'Chennai': ['Gummidipoondi', 'Ponneri', 'Tiruvottiyur', 'Chepauk-Thiruvallikeni',
                    'Thousand Lights', 'Anna Nagar', 'Virugambakkam', 'Saidapet', 'T. Nagar',
                    'Mylapore', 'Velachery', 'Sholinganallur', 'Alandur', 'Sriperumbudur', 'Tambaram'],
        'Coimbatore': ['Sulur', 'Kavundampalayam', 'Coimbatore North', 'Coimbatore South', 'Singanallur', 'Kinathukadavu'],
        'Cuddalore': ['Cuddalore', 'Kurinjipadi', 'Panruti', 'Kattumannarkoil', 'Bhuvanagiri'],
        'Dharmapuri': ['Dharmapuri', 'Palacode', 'Pappireddipatti', 'Harur', 'Pennagaram'],
        'Dindigul': ['Palani', 'Oddanchatram', 'Athoor', 'Dindigul', 'Natham', 'Nilakottai', 'Vedasandur'],
        'Erode': ['Anthiyur', 'Bhavani', 'Erode East', 'Erode West', 'Modakkurichi', 'Perundurai'],
        'Kallakurichi': ['Kallakurichi', 'Gangavalli', 'Rishivandiyam', 'Sankarapuram', 'Chinnasalem'],
        'Kanchipuram': ['Kanchipuram', 'Acharapakkam', 'Madurantakam', 'Uthiramerur'],
        'Kanyakumari': ['Kanyakumari', 'Nagercoil', 'Colachel', 'Padmanabhapuram', 'Vilavancode', 'Killiyoor'],
        'Karur': ['Karur', 'Krishnarayapuram', 'Kulithalai', 'Aravakurichi'],
        'Krishnagiri': ['Krishnagiri', 'Veppanahalli', 'Hosur', 'Uthangarai', 'Bargur'],
        'Madurai': ['Melur', 'Madurai East', 'Sholavandan', 'Madurai North', 'Madurai South', 'Madurai Central', 'Madurai West', 'Thiruparankundram'],
        'Mayiladuthurai': ['Mayiladuthurai', 'Sirkazhi', 'Poompuhar'],
        'Nagapattinam': ['Nagapattinam', 'Kilvelur', 'Vedaranyam'],
        'Namakkal': ['Namakkal', 'Paramathi-Velur', 'Tiruchengode', 'Rasipuram', 'Sankari'],
        'Nilgiris': ['Udhagamandalam', 'Gudalur', 'Coonoor'],
        'Perambalur': ['Perambalur', 'Kunnam'],
        'Pudukkottai': ['Pudukkottai', 'Thirumayam', 'Alangudi', 'Aranthangi', 'Karambakudi'],
        'Ramanathapuram': ['Tiruvadanai', 'Paramakudi', 'Rajasingamangalam', 'Mudhukulathur', 'Ramanathapuram'],
        'Ranipet': ['Ranipet', 'Arcot', 'Sholingur', 'Walajah'],
        'Salem': ['Omalur', 'Mettur', 'Edappadi', 'Sankari', 'Salem North', 'Salem South', 'Salem West'],
        'Sivaganga': ['Sivaganga', 'Manamadurai', 'Karaikudi', 'Tiruppattur'],
        'Tenkasi': ['Tenkasi', 'Kadayanallur', 'Sankarankovil', 'Vasudevanallur', 'Alangulam'],
        'Thanjavur': ['Orathanadu', 'Papanasam', 'Thiruvaiyaru', 'Thanjavur', 'Thiruvidaimarudur', 'Kumbakonam', 'Pattukottai'],
        'Theni': ['Bodinayakanur', 'Cumbum', 'Periyakulam', 'Andipatti'],
        'Thoothukudi': ['Thoothukudi', 'Tiruchendur', 'Srivaikuntam', 'Vilathikulam', 'Ottapidaram', 'Kovilpatti'],
        'Tiruchirappalli': ['Manachanallur', 'Musiri', 'Lalgudi', 'Srirangam', 'Tiruchirappalli West', 'Tiruchirappalli East'],
        'Tirunelveli': ['Tirunelveli', 'Palayamkottai', 'Ambasamudram', 'Nanguneri'],
        'Tirupathur': ['Tirupathur', 'Jolarpet', 'Ambur'],
        'Tiruppur': ['Tiruppur North', 'Tiruppur South', 'Kangeyam', 'Dharapuram', 'Palladam', 'Avinashi'],
        'Tiruvallur': ['Tiruvallur', 'Poonamallee', 'Avadi', 'Madhavaram', 'Ambattur', 'Maduravoyal'],
        'Tiruvannamalai': ['Tiruvannamalai', 'Kilpennathur', 'Kalasapakkam', 'Polur', 'Chengam', 'Anakkavoor'],
        'Tiruvarur': ['Tiruvarur', 'Nannilam', 'Thiruthuraipoondi', 'Mannargudi'],
        'Vellore': ['Vellore', 'Anaicut', 'Katpadi', 'Gudiyatham', 'Vaniyambadi'],
        'Viluppuram': ['Viluppuram', 'Vikravandi', 'Tindivanam', 'Vanur', 'Gingee', 'Mailam', 'Rishivandiyam'],
        'Virudhunagar': ['Virudhunagar', 'Sivakasi', 'Srivilliputhur', 'Sattur', 'Aruppukottai'],
    }

    MANAGER_NAMES = [
        'Rajesh Kumar', 'Priya Subramanian', 'Arun Selvam', 'Lakshmi Devi', 'Murugan Thangavel',
        'Divya Ramesh', 'Karthik Shankar', 'Meena Bala', 'Vijay Kannan', 'Sowmya Ravi',
        'Senthil Kumar', 'Kavitha Mohan', 'Prakash Raja', 'Revathi Sundaram', 'Ganesh Venkat',
        'Saranya Krishnan', 'Naveen Balaji', 'Deepa Gopal', 'Ramesh Babu', 'Anjali Nair',
        'Suresh Naidu', 'Vasantha Priya', 'Kumar Raja', 'Malathy Subbu', 'Bala Chandran',
        'Mythili Srinivas', 'Arjun Kumar', 'Geetha Lakshmi', 'Selvam Moorthy', 'Nirmala Devi',
        'Manoj Kumar', 'Padma Vathi', 'Vinoth Raja', 'Shanthi Bala', 'Natarajan Pillai',
        'Shalini Ramesh', 'Raj Kumar', 'Vimala Devi'
    ]

    GENDERS = ['male', 'female', 'other']

    def add_arguments(self, parser):
        parser.add_argument(
            '--preserve-existing',
            action='store_true',
            help='Preserve existing admin@tvk.com account',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('SETTING UP TVK AND DMK ORGANIZATIONS VIA SUPABASE AUTH'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        # CRITICAL FIX: Disconnect auto-profile-creation signal to prevent conflicts
        # The signal would create profiles with default values before we can set proper values
        from api.signals import create_user_profile
        post_save.disconnect(create_user_profile, sender=User)
        self.stdout.write(self.style.WARNING('\n⚠️  Temporarily disabled auto-profile creation signal'))

        try:
            with transaction.atomic():
                # Step 1: Create organizations
                self.stdout.write('\n📦 Step 1: Creating organizations...')
                self.create_organizations()

                # Step 2: Create admin accounts
                self.stdout.write('\n👤 Step 2: Creating admin accounts...')
                self.create_admin_accounts(preserve_existing=options['preserve_existing'])

                # Step 3: Create district managers
                self.stdout.write('\n👥 Step 3: Creating 38 district managers...')
                self.create_managers()

                # Step 4: Create constituency analysts
                self.stdout.write('\n📊 Step 4: Creating constituency analysts...')
                self.create_analysts()

                # Step 5: Create users (10 per analyst)
                self.stdout.write('\n🌐 Step 5: Creating users (10 per analyst)...')
                self.create_users()

            self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
            self.stdout.write(self.style.SUCCESS('✅ Setup completed successfully!'))
            self.stdout.write(self.style.SUCCESS('=' * 80))
            self.print_summary()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            raise

        finally:
            # Reconnect the signal
            post_save.connect(create_user_profile, sender=User)
            self.stdout.write(self.style.WARNING('\n✅ Re-enabled auto-profile creation signal'))

    def create_supabase_user(self, email, password, user_metadata):
        """Create user via Supabase Auth API"""
        try:
            # Create user in Supabase Auth
            response = self.supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirm email
                "user_metadata": user_metadata
            })

            supabase_user_id = response.user.id

            # Create or update Django user (for backend compatibility)
            try:
                user = User.objects.get(email=email)
                created = False
            except User.DoesNotExist:
                # Ensure username is unique
                base_username = email.split('@')[0]
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1

                user = User.objects.create(
                    username=username,
                    email=email,
                    is_active=True
                )
                user.set_password(password)
                user.save()
                created = True

            return user, supabase_user_id

        except Exception as e:
            # Check if user already exists in Supabase
            if 'already been registered' in str(e).lower():
                self.stdout.write(self.style.WARNING(f'  User {email} already exists in Supabase Auth'))

                # CRITICAL FIX: Fetch the existing Supabase user's UUID
                try:
                    # List all users from Supabase Auth (use large per_page to get all users)
                    response = self.supabase.auth.admin.list_users(page=1, per_page=10000)
                    supabase_user_id = None

                    # The response is a list/iterable of user objects
                    # Handle different response types
                    users_list = response if isinstance(response, list) else (response.users if hasattr(response, 'users') else [])

                    # DEBUG: Show first user structure
                    if users_list:
                        first_user = users_list[0]
                        self.stdout.write(self.style.WARNING(f'  DEBUG: First user type: {type(first_user)}'))
                        self.stdout.write(self.style.WARNING(f'  DEBUG: First user attributes: {dir(first_user)[:10]}...'))
                        if hasattr(first_user, 'email'):
                            self.stdout.write(self.style.WARNING(f'  DEBUG: First user email: {first_user.email}'))
                        if hasattr(first_user, '__dict__'):
                            self.stdout.write(self.style.WARNING(f'  DEBUG: First user dict keys: {list(first_user.__dict__.keys())}'))

                    # Find user by email (case-insensitive)
                    for user_data in users_list:
                        user_email = None
                        if hasattr(user_data, 'email'):
                            user_email = user_data.email
                        elif hasattr(user_data, '__dict__') and 'email' in user_data.__dict__:
                            user_email = user_data.__dict__['email']

                        if user_email and user_email.lower() == email.lower():
                            supabase_user_id = user_data.id if hasattr(user_data, 'id') else user_data.__dict__.get('id')
                            self.stdout.write(self.style.SUCCESS(f'  ✅ Found Supabase user: {email} (UUID: {str(supabase_user_id)[:8]}...)'))
                            break

                    if not supabase_user_id:
                        self.stdout.write(self.style.ERROR(f'  ❌ Could not find Supabase UUID for {email}'))
                        self.stdout.write(self.style.ERROR(f'  Searched {len(users_list)} users in Supabase'))
                        # Show some emails for debugging
                        sample_emails = []
                        for u in users_list[:5]:
                            if hasattr(u, 'email'):
                                sample_emails.append(u.email)
                        if sample_emails:
                            self.stdout.write(self.style.ERROR(f'  Sample emails: {sample_emails}'))
                        raise ValueError(f'Could not find Supabase user: {email}')

                except Exception as lookup_error:
                    self.stdout.write(self.style.ERROR(f'  ❌ Failed to fetch Supabase user: {str(lookup_error)}'))
                    raise

                # Get or create Django user for existing Supabase user
                try:
                    user = User.objects.get(email=email)
                    created = False
                except User.DoesNotExist:
                    # Ensure username is unique (same logic as main creation)
                    base_username = email.split('@')[0]
                    username = base_username
                    counter = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{counter}"
                        counter += 1

                    user = User.objects.create(
                        username=username,
                        email=email,
                        is_active=True
                    )
                    created = True
                if created:
                    # Set a random password since they'll use Supabase Auth
                    import secrets
                    import string
                    alphabet = string.ascii_letters + string.digits + string.punctuation
                    random_password = ''.join(secrets.choice(alphabet) for _ in range(32))
                    user.set_password(random_password)
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✅ Synced existing Supabase user to Django: {email}'))

                # CRITICAL: Return the actual Supabase UUID, not None
                return user, supabase_user_id
            else:
                raise

    def create_organizations(self):
        """Create TVK and DMK organizations"""
        self.tvk_org, tvk_created = Organization.objects.get_or_create(
            slug='tvk',
            defaults={
                'name': 'Tamilaga Vettri Kazhagam',
                'organization_type': 'party',
                'subscription_plan': 'enterprise',
                'max_users': 10000,
                'is_active': True,
            }
        )

        if tvk_created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created TVK organization'))
        else:
            self.stdout.write('  ℹ️  TVK organization already exists')

        self.dmk_org, dmk_created = Organization.objects.get_or_create(
            slug='dmk',
            defaults={
                'name': 'Dravida Munnetra Kazhagam',
                'organization_type': 'party',
                'subscription_plan': 'enterprise',
                'max_users': 10000,
                'is_active': True,
            }
        )

        if dmk_created:
            self.stdout.write(self.style.SUCCESS('  ✅ Created DMK organization'))
        else:
            self.stdout.write('  ℹ️  DMK organization already exists')

    def create_admin_accounts(self, preserve_existing=True):
        """Create admin accounts for TVK and DMK"""

        # TVK Admin - preserve existing admin@tvk.com
        if preserve_existing:
            tvk_admin_user = User.objects.filter(email='admin@tvk.com').first()
            if tvk_admin_user:
                self.stdout.write('  ℹ️  Found existing TVK admin: admin@tvk.com (preserving)')
                profile, _ = UserProfile.objects.get_or_create(
                    user=tvk_admin_user,
                    defaults={
                        'organization': self.tvk_org,
                        'role': 'admin',
                        'phone': '+919876543210',
                    }
                )
                if not profile.organization:
                    profile.organization = self.tvk_org
                    profile.role = 'admin'
                    profile.save()
                return

        # Create new TVK admin via Supabase
        user, supabase_id = self.create_supabase_user(
            email='admin@tvk.com',
            password='TvkAdmin@2025',
            user_metadata={
                'name': 'TVK Administrator',
                'role': 'admin',
                'organization_slug': 'tvk',
                'organization_id': str(self.tvk_org.id)
            }
        )

        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'supabase_uid': supabase_id,  # CRITICAL: Link to Supabase Auth
                'organization': self.tvk_org,
                'role': 'admin',
                'phone': '+919876543210',
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✅ Created TVK admin: admin@tvk.com'))

        # DMK Admin
        user, supabase_id = self.create_supabase_user(
            email='admin@dmk.org',
            password='DmkAdmin@2025',
            user_metadata={
                'name': 'DMK Administrator',
                'role': 'admin',
                'organization_slug': 'dmk',
                'organization_id': str(self.dmk_org.id)
            }
        )

        UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'supabase_uid': supabase_id,  # CRITICAL: Link to Supabase Auth
                'organization': self.dmk_org,
                'role': 'admin',
                'phone': '+919876543211',
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✅ Created DMK admin: admin@dmk.org'))

    def create_managers(self):
        """Create 38 district managers for TVK"""
        tn_state = State.objects.filter(name='Tamil Nadu').first()
        if not tn_state:
            self.stdout.write(self.style.ERROR('  ❌ Tamil Nadu state not found in database'))
            return

        districts = District.objects.filter(state=tn_state).order_by('name')

        for idx, district in enumerate(districts):
            manager_name = self.MANAGER_NAMES[idx % len(self.MANAGER_NAMES)]
            email = f'manager.{district.name.lower().replace(" ", "")}@tvk.org'
            username = f'mgr_{district.code.lower()}'
            password = f'Manager@{district.code}2025'

            user, supabase_id = self.create_supabase_user(
                email=email,
                password=password,
                user_metadata={
                    'name': f'{manager_name} - {district.name} Manager',
                    'role': 'manager',
                    'organization_slug': 'tvk',
                    'organization_id': str(self.tvk_org.id),
                    'district': district.name,
                    'district_code': district.code
                }
            )

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'supabase_uid': supabase_id,  # CRITICAL: Link to Supabase Auth
                    'role': 'manager',
                    'organization': self.tvk_org,
                    'assigned_district': district,
                    'phone': f'+91987654{3300 + idx:04d}',
                }
            )

            if (idx + 1) % 10 == 0:
                self.stdout.write(f'  ✅ Created {idx + 1}/38 managers')

        self.stdout.write(self.style.SUCCESS(f'  ✅ Created all 38 district managers'))

    def create_analysts(self):
        """Create analysts for each constituency"""
        tn_state = State.objects.filter(name='Tamil Nadu').first()
        constituencies = Constituency.objects.filter(state=tn_state).select_related('district')

        analyst_count = 0
        for constituency in constituencies:
            email = f'analyst.{constituency.name.lower().replace(" ", "").replace("-", "")}@tvk.org'
            password = f'Analyst@{constituency.code}25'

            user, supabase_id = self.create_supabase_user(
                email=email,
                password=password,
                user_metadata={
                    'name': f'{constituency.name} Analyst',
                    'role': 'analyst',
                    'organization_slug': 'tvk',
                    'organization_id': str(self.tvk_org.id),
                    'district': constituency.district.name if constituency.district else None,
                    'constituency': constituency.name
                }
            )

            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'supabase_uid': supabase_id,  # CRITICAL: Link to Supabase Auth
                    'role': 'analyst',
                    'organization': self.tvk_org,
                    'assigned_district': constituency.district,
                    'constituency': constituency.name,
                    'phone': f'+91987654{4000 + analyst_count:04d}',
                }
            )

            analyst_count += 1
            if analyst_count % 50 == 0:
                self.stdout.write(f'  ✅ Created {analyst_count} analysts')

        self.stdout.write(self.style.SUCCESS(f'  ✅ Created {analyst_count} constituency analysts'))

    def create_users(self):
        """Create 10 users per analyst"""
        analysts = UserProfile.objects.filter(role='analyst', organization=self.tvk_org).select_related('user', 'assigned_district')

        user_count = 0
        for analyst_profile in analysts:
            constituency_name = analyst_profile.constituency or 'unknown'
            const_safe = constituency_name.lower().replace(' ', '').replace('-', '')

            for i in range(1, 11):  # 10 users per analyst
                email = f'user.{const_safe}.{i}@tvk.org'
                password = f'User@{i}{constituency_name[:3]}25'

                user, supabase_id = self.create_supabase_user(
                    email=email,
                    password=password,
                    user_metadata={
                        'name': f'User {i} - {constituency_name}',
                        'role': 'user',
                        'organization_slug': 'tvk',
                        'organization_id': str(self.tvk_org.id),
                        'district': analyst_profile.assigned_district.name if analyst_profile.assigned_district else None,
                        'constituency': constituency_name,
                        'parent_analyst': analyst_profile.user.email
                    }
                )

                UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'supabase_uid': supabase_id,  # CRITICAL: Link to Supabase Auth
                        'role': 'user',
                        'organization': self.tvk_org,
                        'assigned_district': analyst_profile.assigned_district,
                        'constituency': constituency_name,
                        'phone': f'+91987654{5000 + user_count:04d}',
                    }
                )

                user_count += 1
                if user_count % 100 == 0:
                    self.stdout.write(f'  ✅ Created {user_count} users')

        self.stdout.write(self.style.SUCCESS(f'  ✅ Created {user_count} total users'))

    def print_summary(self):
        """Print setup summary"""
        tvk_profiles = UserProfile.objects.filter(organization=self.tvk_org)
        dmk_profiles = UserProfile.objects.filter(organization=self.dmk_org)

        self.stdout.write('\n📊 SUMMARY:')
        self.stdout.write(f'\nTVK Organization:')
        self.stdout.write(f'  Admins: {tvk_profiles.filter(role="admin").count()}')
        self.stdout.write(f'  Managers: {tvk_profiles.filter(role="manager").count()}')
        self.stdout.write(f'  Analysts: {tvk_profiles.filter(role="analyst").count()}')
        self.stdout.write(f'  Users: {tvk_profiles.filter(role="user").count()}')
        self.stdout.write(f'  Total: {tvk_profiles.count()}')

        self.stdout.write(f'\nDMK Organization:')
        self.stdout.write(f'  Admins: {dmk_profiles.filter(role="admin").count()}')
        self.stdout.write(f'  Total: {dmk_profiles.count()}')

        self.stdout.write('\n🔐 ADMIN CREDENTIALS:')
        self.stdout.write('  TVK Admin:')
        self.stdout.write('    Email: admin@tvk.com')
        self.stdout.write('    Password: TvkAdmin@2025')
        self.stdout.write('  DMK Admin:')
        self.stdout.write('    Email: admin@dmk.org')
        self.stdout.write('    Password: DmkAdmin@2025')
