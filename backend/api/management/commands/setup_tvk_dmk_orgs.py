"""
Management command to set up TVK and DMK organizations with complete hierarchical data
Creates: Organizations, Admins, Managers, Analysts, Users with proper relationships
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import (
    Organization, UserProfile, State, District, Constituency
)
from django.db import transaction
import random

User = get_user_model()


# Complete Tamil Nadu Assembly Constituencies mapped to Districts (234 total)
DISTRICT_CONSTITUENCIES = {
    'Ariyalur': ['Ariyalur', 'Jayankondam', 'Andimadam'],
    'Chengalpattu': ['Chengalpattu', 'Thiruporur', 'Madurantakam', 'Cheyyur', 'Maduranthakam'],
    'Chennai': ['Gummidipoondi', 'Ponneri', 'Tiruvottiyur', 'Chepauk-Thiruvallikeni',
                'Thousand Lights', 'Anna Nagar', 'Virugambakkam', 'Saidapet', 'T. Nagar',
                'Mylapore', 'Velachery', 'Sholinganallur', 'Alandur', 'Sriperumbudur', 'Tambaram'],
    'Coimbatore': ['Sulur', 'Kavundampalayam', 'Coimbatore North', 'Coimbatore South',
                   'Singanallur', 'Pollachi', 'Valparai', 'Kinathukadavu', 'Thondamuthur', 'Mettupalayam'],
    'Cuddalore': ['Cuddalore', 'Kurinjipadi', 'Bhuvanagiri', 'Chidambaram', 'Kattumannarkoil', 'Tittakudi'],
    'Dharmapuri': ['Dharmapuri', 'Pappireddipatti', 'Harur', 'Palakodu', 'Pennagaram'],
    'Dindigul': ['Dindigul', 'Athoor', 'Nilakottai', 'Natham', 'Oddanchatram', 'Vedasandur', 'Palani'],
    'Erode': ['Erode East', 'Erode West', 'Modakurichi', 'Perundurai', 'Bhavani', 'Anthiyur', 'Gobichettipalayam', 'Sathyamangalam'],
    'Kallakurichi': ['Kallakurichi', 'Gangavalli', 'Rishivandiyam', 'Sankarapuram', 'Kalvarayan Hills'],
    'Kanchipuram': ['Kanchipuram', 'Acharapakkam', 'Uthiramerur', 'Kancheepuram'],
    'Kanyakumari': ['Kanyakumari', 'Nagercoil', 'Colachel', 'Padmanabhapuram', 'Vilavancode', 'Killiyoor'],
    'Karur': ['Karur', 'Aravakurichi', 'Krishnarayapuram', 'Kulithalai'],
    'Krishnagiri': ['Krishnagiri', 'Veppanahalli', 'Hosur', 'Thalli', 'Uthangarai', 'Bargur'],
    'Madurai': ['Melur', 'Madurai East', 'Sholavandan', 'Madurai North', 'Madurai South',
                'Madurai Central', 'Madurai West', 'Thiruparankundram', 'Usilampatti'],
    'Mayiladuthurai': ['Mayiladuthurai', 'Sirkazhi', 'Poompuhar'],
    'Nagapattinam': ['Nagapattinam', 'Kilvelur', 'Vedaranyam', 'Nannilam'],
    'Namakkal': ['Namakkal', 'Paramathi-Velur', 'Rasipuram', 'Senthamangalam', 'Komarapalayam'],
    'Nilgiris': ['Udhagamandalam', 'Gudalur', 'Coonoor'],
    'Perambalur': ['Perambalur', 'Kunnam', 'Veppanthattai'],
    'Pudukkottai': ['Pudukkottai', 'Thirumayam', 'Alangudi', 'Aranthangi', 'Karambakudi', 'Gandarvakottai'],
    'Ramanathapuram': ['Ramanathapuram', 'Tiruvadanai', 'Paramakudi', 'Rajasingamangalam', 'Mudhukulathur'],
    'Ranipet': ['Ranipet', 'Arcot', 'Sholingur', 'Walajah'],
    'Salem': ['Omalur', 'Mettur', 'Edappadi', 'Sankari', 'Salem North', 'Salem South',
              'Salem West', 'Veerapandi', 'Attur', 'Yercaud'],
    'Sivaganga': ['Sivaganga', 'Manamadurai', 'Karaikudi', 'Tirupathur'],
    'Tenkasi': ['Tenkasi', 'Alangulam', 'Sankarankovil', 'Kadayanallur', 'Vasudevanallur'],
    'Thanjavur': ['Thanjavur', 'Thiruvaiyaru', 'Kumbakonam', 'Papanasam', 'Thiruvidaimarudur', 'Orathanadu', 'Pattukkottai'],
    'Theni': ['Theni', 'Bodinayakanur', 'Cumbum', 'Periyakulam', 'Andipatti'],
    'Thoothukudi': ['Thoothukudi', 'Tiruchendur', 'Srivaikuntam', 'Vilathikulam', 'Ottapidaram', 'Kovilpatti', 'Sathankulam'],
    'Tiruchirappalli': ['Musiri', 'Lalgudi', 'Manachanallur', 'Srirangam', 'Tiruchirappalli West',
                        'Tiruchirappalli East', 'Thiruverumbur', 'Manapparai'],
    'Tirunelveli': ['Tirunelveli', 'Palayamkottai', 'Ambasamudram', 'Nanguneri', 'Radhapuram', 'Cheranmahadevi'],
    'Tirupathur': ['Tirupathur', 'Jolarpet', 'Ambur', 'Natrampalli'],
    'Tiruppur': ['Tiruppur North', 'Tiruppur South', 'Dharapuram', 'Palladam', 'Kangayam', 'Madathukulam', 'Avanashi'],
    'Tiruvallur': ['Tiruvallur', 'Poonamallee', 'Avadi', 'Maduravoyal', 'Ambattur', 'Madhavaram', 'RK Nagar', 'Gummidipoondi'],
    'Tiruvannamalai': ['Tiruvannamalai', 'Kilpennathur', 'Kalasapakkam', 'Polur', 'Arani', 'Cheyyar', 'Vandavasi'],
    'Tiruvarur': ['Tiruvarur', 'Nannilam', 'Thiruthuraipoondi', 'Mannargudi', 'Muthupettai'],
    'Vellore': ['Vellore', 'Katpadi', 'Gudiyatham', 'Vaniyambadi', 'K V Kuppam', 'Jolarpet'],
    'Viluppuram': ['Viluppuram', 'Vikravandi', 'Tindivanam', 'Vanur', 'Gingee', 'Mailam', 'Rishivandiyam'],
    'Virudhunagar': ['Virudhunagar', 'Sivakasi', 'Srivilliputtur', 'Rajapalayam', 'Sattur', 'Aruppukkottai']
}


# Manager names (real Tamil names)
MANAGER_NAMES = [
    'Karthik Kumar', 'Priya Sharma', 'Rajesh Murugan', 'Divya Lakshmi',
    'Suresh Babu', 'Meena Devi', 'Vijay Prakash', 'Lakshmi Priya',
    'Kumar Swamy', 'Anitha Rani', 'Ganesh Kumar', 'Revathi Devi',
    'Senthil Kumar', 'Sudha Rani', 'Prakash Raj', 'Kavitha Devi',
    'Murugan Vel', 'Saranya Devi', 'Ramesh Kumar', 'Manjula Devi',
    'Krishna Moorthy', 'Padma Priya', 'Vignesh Kumar', 'Deepa Lakshmi',
    'Arun Kumar', 'Geetha Rani', 'Babu Raj', 'Kamala Devi',
    'Selvam Kumar', 'Pushpa Rani', 'Dinesh Kumar', 'Radha Devi',
    'Venkat Raman', 'Uma Devi', 'Chandru Kumar', 'Vasanthi Rani',
    'Mohan Raj', 'Selvi Devi'
]

# Analyst name prefixes
ANALYST_PREFIXES = ['Analyst', 'Field Officer', 'Executive', 'Coordinator', 'Officer']

# User name templates
USER_NAME_TEMPLATES = [
    'Booth Agent', 'Field Worker', 'Volunteer', 'Organizer', 'Representative'
]


class Command(BaseCommand):
    help = 'Set up TVK and DMK organizations with complete hierarchical user data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-constituencies',
            action='store_true',
            help='Skip constituency creation (use existing)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*80))
        self.stdout.write(self.style.SUCCESS('SETTING UP TVK & DMK ORGANIZATIONS'))
        self.stdout.write(self.style.SUCCESS('='*80))

        with transaction.atomic():
            # Step 1: Create/Get Organizations
            self.create_organizations()

            # Step 2: Create/Update Admin Accounts
            self.create_admin_accounts()

            # Step 3: Create Constituencies
            if not options['skip_constituencies']:
                self.create_constituencies()

            # Step 4: Create Managers (38 for TVK)
            self.create_managers()

            # Step 5: Create Analysts (per constituency)
            self.create_analysts()

            # Step 6: Create Users (10 per analyst)
            self.create_users()

            # Step 7: Summary
            self.print_summary()

        self.stdout.write(self.style.SUCCESS('\n✅ SETUP COMPLETE!'))

    def create_organizations(self):
        self.stdout.write('\n[1/6] Creating Organizations...')

        # TVK Organization (should already exist)
        tvk_org, tvk_created = Organization.objects.get_or_create(
            slug='tvk',
            defaults={
                'name': 'Tamilaga Vettri Kazhagam',
                'organization_type': 'party',
                'subscription_plan': 'enterprise',
                'subscription_status': 'active',
                'max_users': 10000,
                'is_active': True,
                'contact_email': 'info@tvk.org',
                'contact_phone': '+919876543210'
            }
        )
        self.tvk_org = tvk_org
        self.stdout.write(f'  {"Created" if tvk_created else "Found"} TVK organization')

        # DMK Organization (new)
        dmk_org, dmk_created = Organization.objects.get_or_create(
            slug='dmk',
            defaults={
                'name': 'Dravida Munnetra Kazhagam',
                'organization_type': 'party',
                'subscription_plan': 'enterprise',
                'subscription_status': 'active',
                'max_users': 10000,
                'is_active': True,
                'contact_email': 'info@dmk.org',
                'contact_phone': '+919876543211'
            }
        )
        self.dmk_org = dmk_org
        self.stdout.write(f'  {"Created" if dmk_created else "Found"} DMK organization')

    def create_admin_accounts(self):
        self.stdout.write('\n[2/6] Creating Admin Accounts...')

        # TVK Admin - Keep existing admin@tvk.com (DO NOT MODIFY)
        tvk_admin_user = User.objects.filter(email='admin@tvk.com').first()
        if tvk_admin_user:
            self.stdout.write(f'  ✅ Found existing TVK admin: admin@tvk.com (preserving for other developers)')
            # Ensure profile has organization
            profile, _ = UserProfile.objects.get_or_create(user=tvk_admin_user)
            if not profile.organization:
                profile.organization = self.tvk_org
                profile.role = 'admin'
                profile.save()
                self.stdout.write('    Updated profile with TVK organization')
        else:
            self.stdout.write(self.style.WARNING('  ⚠️  admin@tvk.com not found!'))

        # Create DMK Admin
        dmk_admin_user, dmk_created = User.objects.get_or_create(
            email='admin@dmk.org',
            defaults={
                'username': 'dmk_admin',
                'first_name': 'DMK',
                'last_name': 'Admin',
                'is_staff': False,
                'is_active': True
            }
        )
        if dmk_created:
            dmk_admin_user.set_password('DmkAdmin@2025')
            dmk_admin_user.save()

        dmk_profile, _ = UserProfile.objects.get_or_create(
            user=dmk_admin_user,
            defaults={
                'role': 'admin',
                'organization': self.dmk_org,
                'bio': 'DMK Party State Admin',
                'phone': '+919876543299'
            }
        )
        if not dmk_profile.organization:
            dmk_profile.organization = self.dmk_org
            dmk_profile.role = 'admin'
            dmk_profile.save()

        self.stdout.write(f'  {"✅ Created" if dmk_created else "✅ Found"} DMK admin: admin@dmk.org')
        if dmk_created:
            self.stdout.write(self.style.WARNING(f'     PASSWORD: DmkAdmin@2025'))

    def create_constituencies(self):
        self.stdout.write('\n[3/6] Creating Constituencies...')

        tn_state = State.objects.get(code='TN')
        total_created = 0
        const_number = 1

        for district_name, constituencies in DISTRICT_CONSTITUENCIES.items():
            try:
                district = District.objects.get(name=district_name, state=tn_state)

                for const_name in constituencies:
                    const, created = Constituency.objects.get_or_create(
                        name=const_name,
                        district=district,
                        state=tn_state,
                        defaults={
                            'code': f'{district.code}-{const_number:03d}',
                            'number': const_number,
                            'total_voters': random.randint(150000, 300000)
                        }
                    )
                    if created:
                        total_created += 1
                    const_number += 1

            except District.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'  ⚠️  District {district_name} not found'))

        self.stdout.write(f'  ✅ Created {total_created} new constituencies')
        self.stdout.write(f'  Total constituencies: {Constituency.objects.filter(state=tn_state).count()}')

    def create_managers(self):
        self.stdout.write('\n[4/6] Creating Managers (38 Districts)...')

        tn_state = State.objects.get(code='TN')
        districts = District.objects.filter(state=tn_state).order_by('name')

        created_count = 0
        for idx, district in enumerate(districts):
            manager_name = MANAGER_NAMES[idx % len(MANAGER_NAMES)]
            email = f'manager.{district.name.lower().replace(" ", "")}@tvk.org'
            username = f'mgr_{district.code.lower()}'

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username,
                    'first_name': manager_name.split()[0],
                    'last_name': manager_name.split()[1] if len(manager_name.split()) > 1 else 'Manager',
                    'is_staff': False,
                    'is_active': True
                }
            )

            if created:
                user.set_password(f'Manager@{district.code}2025')
                user.save()
                created_count += 1

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'manager',
                    'organization': self.tvk_org,
                    'assigned_state': tn_state,
                    'assigned_district': district,
                    'bio': f'District Manager for {district.name}',
                    'phone': f'+91987654{3300 + idx:04d}',
                    'city': district.name
                }
            )

            # Ensure manager has correct settings
            if profile.role != 'manager' or profile.organization != self.tvk_org:
                profile.role = 'manager'
                profile.organization = self.tvk_org
                profile.assigned_district = district
                profile.save()

        self.stdout.write(f'  ✅ Created {created_count} new managers')
        self.stdout.write(f'  Total TVK managers: {UserProfile.objects.filter(role="manager", organization=self.tvk_org).count()}')

    def create_analysts(self):
        self.stdout.write('\n[5/6] Creating Analysts (per Constituency)...')

        tn_state = State.objects.get(code='TN')
        constituencies = Constituency.objects.filter(state=tn_state).select_related('district')

        created_count = 0
        for idx, constituency in enumerate(constituencies):
            # Get the manager for this constituency's district
            manager_profile = UserProfile.objects.filter(
                role='manager',
                organization=self.tvk_org,
                assigned_district=constituency.district
            ).first()

            if not manager_profile:
                self.stdout.write(self.style.WARNING(f'  ⚠️  No manager for {constituency.district.name}'))
                continue

            analyst_name = f'{random.choice(ANALYST_PREFIXES)} {constituency.name}'
            email = f'analyst.{constituency.name.lower().replace(" ", "").replace("-", "")}@tvk.org'
            username = f'analyst_{constituency.code.lower().replace("-", "_")}'

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': username[:30],  # Django username limit
                    'first_name': random.choice(['Kumar', 'Devi', 'Raj', 'Priya', 'Murugan', 'Lakshmi']),
                    'last_name': constituency.name.split()[0][:20],
                    'is_staff': False,
                    'is_active': True
                }
            )

            if created:
                user.set_password(f'Analyst@{constituency.code}25')
                user.save()
                created_count += 1

            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'analyst',
                    'organization': self.tvk_org,
                    'assigned_state': tn_state,
                    'assigned_district': constituency.district,
                    'constituency': constituency.name,
                    'bio': f'Constituency Analyst for {constituency.name}',
                    'phone': f'+91987{random.randint(1000000, 9999999):07d}',
                    'city': constituency.district.name
                }
            )

            if profile.role != 'analyst' or profile.organization != self.tvk_org:
                profile.role = 'analyst'
                profile.organization = self.tvk_org
                profile.assigned_district = constituency.district
                profile.constituency = constituency.name
                profile.save()

        self.stdout.write(f'  ✅ Created {created_count} new analysts')
        self.stdout.write(f'  Total TVK analysts: {UserProfile.objects.filter(role="analyst", organization=self.tvk_org).count()}')

    def create_users(self):
        self.stdout.write('\n[6/6] Creating Users (10 per Analyst)...')

        analysts = UserProfile.objects.filter(
            role='analyst',
            organization=self.tvk_org
        ).select_related('user')

        created_count = 0
        genders = ['Male', 'Female', 'Other']

        for analyst_profile in analysts:
            constituency_name = analyst_profile.constituency or 'Unknown'
            const_safe = constituency_name.lower().replace(" ", "").replace("-", "")

            for i in range(1, 11):
                user_type = random.choice(USER_NAME_TEMPLATES)
                email = f'user.{const_safe}.{i}@tvk.org'
                username = f'user_{const_safe}_{i}'[:30]

                user, created = User.objects.get_or_create(
                    email=email,
                    defaults={
                        'username': username,
                        'first_name': f'{user_type} {i}',
                        'last_name': constituency_name.split()[0][:20],
                        'is_staff': False,
                        'is_active': True
                    }
                )

                if created:
                    user.set_password(f'User@{i}{constituency_name[:3]}25')
                    user.save()
                    created_count += 1

                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'role': 'user',
                        'organization': self.tvk_org,
                        'assigned_state': analyst_profile.assigned_state,
                        'assigned_district': analyst_profile.assigned_district,
                        'constituency': constituency_name,
                        'bio': f'{user_type} for {constituency_name}',
                        'phone': f'+91{random.randint(7000000000, 9999999999)}',
                        'city': analyst_profile.city
                    }
                )

                if profile.role != 'user' or profile.organization != self.tvk_org:
                    profile.role = 'user'
                    profile.organization = self.tvk_org
                    profile.assigned_district = analyst_profile.assigned_district
                    profile.constituency = constituency_name
                    profile.save()

        self.stdout.write(f'  ✅ Created {created_count} new users')
        self.stdout.write(f'  Total TVK users: {UserProfile.objects.filter(role="user", organization=self.tvk_org).count()}')

    def print_summary(self):
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('SETUP SUMMARY'))
        self.stdout.write('='*80)

        # Organizations
        self.stdout.write('\n📊 ORGANIZATIONS:')
        self.stdout.write(f'  TVK: {self.tvk_org.members.count()} members')
        self.stdout.write(f'  DMK: {self.dmk_org.members.count()} members')

        # TVK Hierarchy
        self.stdout.write('\n🏛️  TVK HIERARCHY:')
        self.stdout.write(f'  Admins: {UserProfile.objects.filter(role="admin", organization=self.tvk_org).count()}')
        self.stdout.write(f'  Managers: {UserProfile.objects.filter(role="manager", organization=self.tvk_org).count()}')
        self.stdout.write(f'  Analysts: {UserProfile.objects.filter(role="analyst", organization=self.tvk_org).count()}')
        self.stdout.write(f'  Users: {UserProfile.objects.filter(role="user", organization=self.tvk_org).count()}')

        # DMK Hierarchy
        self.stdout.write('\n🏛️  DMK HIERARCHY:')
        self.stdout.write(f'  Admins: {UserProfile.objects.filter(role="admin", organization=self.dmk_org).count()}')
        self.stdout.write(f'  Others: {UserProfile.objects.filter(organization=self.dmk_org).exclude(role="admin").count()}')

        # Geographic Coverage
        tn_state = State.objects.get(code='TN')
        self.stdout.write('\n🗺️  GEOGRAPHIC COVERAGE:')
        self.stdout.write(f'  Districts: {District.objects.filter(state=tn_state).count()}')
        self.stdout.write(f'  Constituencies: {Constituency.objects.filter(state=tn_state).count()}')

        # Login Credentials
        self.stdout.write('\n' + '='*80)
        self.stdout.write(self.style.SUCCESS('🔑 ADMIN LOGIN CREDENTIALS'))
        self.stdout.write('='*80)

        self.stdout.write('\n📌 TVK ADMIN (preserved for other developers):')
        self.stdout.write('  Email: admin@tvk.com')
        self.stdout.write('  Password: [UNCHANGED - use existing password]')

        self.stdout.write('\n📌 DMK ADMIN (new):')
        self.stdout.write('  Email: admin@dmk.org')
        self.stdout.write('  Password: DmkAdmin@2025')

        # Sample Manager Credentials
        sample_manager = UserProfile.objects.filter(
            role='manager',
            organization=self.tvk_org
        ).select_related('user').first()

        if sample_manager:
            district_code = sample_manager.assigned_district.code if sample_manager.assigned_district else 'XXX'
            self.stdout.write(f'\n📌 SAMPLE TVK MANAGER ({sample_manager.assigned_district.name if sample_manager.assigned_district else "Unknown"}):')
            self.stdout.write(f'  Email: {sample_manager.user.email}')
            self.stdout.write(f'  Password: Manager@{district_code}2025')

        self.stdout.write('\n' + '='*80)
