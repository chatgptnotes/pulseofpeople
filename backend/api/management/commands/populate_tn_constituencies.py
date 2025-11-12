"""
Management command to populate all 234 Tamil Nadu Assembly Constituencies
Maps each constituency to its parent district

Usage:
    python manage.py populate_tn_constituencies
"""

from django.core.management.base import BaseCommand
from api.models import State, District, Constituency


class Command(BaseCommand):
    help = 'Populate all 234 Tamil Nadu Assembly Constituencies with district mappings'

    # All 234 Tamil Nadu Assembly Constituencies organized by district
    TN_CONSTITUENCIES = {
        'Ariyalur': ['Ariyalur', 'Jayankondam', 'Sendurai'],
        'Chengalpattu': ['Alandur', 'Chengalpattu', 'Cheyyur', 'Maduranthakam', 'Madurantakam', 'Pallavaram', 'Sriperumbudur', 'Tambaram'],
        'Chennai': ['Anna Nagar', 'Ayanavaram', 'Chepauk-Thiruvallikeni', 'Egmore', 'Harbour', 'Kolathur', 'Mylapore', 'Perambur', 'Royapuram', 'Saidapet', 'T. Nagar', 'Thiru Vi Ka Nagar', 'Thousand Lights', 'Villivakkam', 'Virugambakkam'],
        'Coimbatore': ['Coimbatore North', 'Coimbatore South', 'Karamadai', 'Kavundampalayam', 'Kinathukadavu', 'Mettupalayam', 'Pollachi', 'Singanallur', 'Sulur', 'Valparai'],
        'Cuddalore': ['Bhuvanagiri', 'Chidambaram', 'Cuddalore', 'Kattumannarkoil', 'Kurinjipadi', 'Panruti', 'Tittagudi', 'Virudhachalam', 'Vriddachalam'],
        'Dharmapuri': ['Dharmapuri', 'Harur', 'Palacode', 'Pennagaram', 'Pappireddipatti'],
        'Dindigul': ['Athoor', 'Dindigul', 'Natham', 'Nilakottai', 'Oddanchatram', 'Palani', 'Vedasandur'],
        'Erode': ['Anthiyur', 'Bhavani', 'Erode East', 'Erode West', 'Gobichettipalayam', 'Modakurichi', 'Perundurai', 'Sathyamangalam'],
        'Kallakurichi': ['Gangavalli', 'Kallakurichi', 'Rishivandiyam', 'Sankarapuram', 'Tirukoilur'],
        'Kanchipuram': ['Acharapakkam', 'Kanchipuram', 'Madurantakam', 'Uthiramerur'],
        'Kanyakumari': ['Colachal', 'Killiyoor', 'Nagercoil', 'Padmanabhapuram', 'Vilavancode'],
        'Karur': ['Aravakurichi', 'Karur', 'Krishnarayapuram', 'Kulithalai'],
        'Krishnagiri': ['Bargur', 'Hosur', 'Krishnagiri', 'Shoolagiri', 'Uthangarai', 'Veppanahalli'],
        'Madurai': ['Madurai Central', 'Madurai East', 'Madurai North', 'Madurai South', 'Madurai West', 'Melur', 'Sholavandan', 'Thiruparankundram', 'Usilampatti'],
        'Mayiladuthurai': ['Mayiladuthurai', 'Poompuhar', 'Sirkazhi'],
        'Nagapattinam': ['Kilvelur', 'Nagapattinam', 'Vedaranyam'],
        'Namakkal': ['Kumarapalayam', 'Namakkal', 'Paramathi-Velur', 'Rasipuram', 'Sankari', 'Sentamangalam'],
        'Nilgiris': ['Coonoor', 'Gudalur', 'Ootacamund', 'Udhagamandalam'],
        'Perambalur': ['Perambalur', 'Veppanthattai'],
        'Pudukkottai': ['Alangudi', 'Aranthangi', 'Karambakudi', 'Pudukkottai', 'Thirumayam', 'Viralimalai'],
        'Ramanathapuram': ['Kadaladi', 'Mudukulathur', 'Paramakudi', 'Ramanathapuram', 'Tiruvadanai'],
        'Ranipet': ['Arakkonam', 'Arcot', 'Ranipet', 'Sholinghur'],
        'Salem': ['Attur', 'Gangavalli', 'Omalur', 'Salem North', 'Salem South', 'Salem West', 'Sankagiri', 'Vazhapadi', 'Yercaud'],
        'Sivaganga': ['Karaikudi', 'Manamadurai', 'Sivaganga', 'Thirupathur'],
        'Tenkasi': ['Alangulam', 'Kadayanallur', 'Shenkottai', 'Tenkasi', 'Vasudevanallur'],
        'Thanjavur': ['Kumbakonam', 'Orathanadu', 'Papanasam', 'Pattukkottai', 'Thanjavur', 'Thiruvaiyaru', 'Thiruvidaimarudur'],
        'Theni': ['Andipatti', 'Bodinayakanur', 'Periyakulam', 'Theni'],
        'Thoothukudi': ['Kovilpatti', 'Ottapidaram', 'Srivaikuntam', 'Tiruchendur', 'Tuticorin', 'Vilathikulam'],
        'Tiruchirappalli': ['Lalgudi', 'Manachanallur', 'Musiri', 'Srirangam', 'Thiruverumbur', 'Tiruchirapalli East', 'Tiruchirapalli West'],
        'Tirunelveli': ['Ambasamudram', 'Cheranmahadevi', 'Nanguneri', 'Palayamkottai', 'Radhapuram', 'Tirunelveli'],
        'Tirupathur': ['Ambur', 'Jolarpet', 'Natrampalli', 'Tirupathur', 'Vaniyambadi'],
        'Tiruppur': ['Avanashi', 'Dharapuram', 'Kangeyam', 'Palladam', 'Tiruppur North', 'Tiruppur South', 'Udumalpet'],
        'Tiruvallur': ['Avadi', 'Gummidipoondi', 'Madavaram', 'Maduravoyal', 'Poonamallee', 'R K Pet', 'Thiruvallur', 'Thiruvottiyur'],
        'Tiruvannamalai': ['Arani', 'Chengam', 'Cheyyar', 'Kalasapakkam', 'Kilpennathur', 'Polur', 'Thandrampattu', 'Tiruvannamalai', 'Vandavasi'],
        'Tiruvarur': ['Mannargudi', 'Nannilam', 'Thiruthuraipoondi', 'Tiruvarur'],
        'Vellore': ['Anaicut', 'Gudiyatham', 'Katpadi', 'Vellore'],
        'Viluppuram': ['Gingee', 'Mailam', 'Melmalaiyanur', 'Tirukkoyilur', 'Vanur', 'Vikravandi', 'Viluppuram'],
        'Virudhunagar': ['Aruppukottai', 'Rajapalayam', 'Sattur', 'Sivakasi', 'Srivilliputtur', 'Tiruchuli', 'Virudhunagar']
    }

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Tamil Nadu Constituency Population'))
        self.stdout.write('=' * 80)

        # Get Tamil Nadu state
        tn_state = State.objects.filter(name='Tamil Nadu').first()
        if not tn_state:
            self.stdout.write(self.style.ERROR('Tamil Nadu state not found in database!'))
            return

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Iterate through each district and its constituencies
        for district_name, constituencies in self.TN_CONSTITUENCIES.items():
            # Get the district
            district = District.objects.filter(
                name__iexact=district_name,
                state=tn_state
            ).first()

            if not district:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  District not found: {district_name} - skipping {len(constituencies)} constituencies')
                )
                skipped_count += len(constituencies)
                continue

            self.stdout.write(f'\n📍 Processing {district_name} District ({len(constituencies)} constituencies)')

            # Create or update each constituency
            for idx, constituency_name in enumerate(constituencies, start=1):
                # Generate constituency code (lowercase, no spaces)
                code = constituency_name.lower().replace(' ', '').replace('-', '').replace('.', '')[:20]

                constituency, created = Constituency.objects.get_or_create(
                    name=constituency_name,
                    state=tn_state,
                    defaults={
                        'code': code,
                        'district': district,
                        'constituency_type': 'assembly',
                        'number': created_count + idx  # Sequential numbering
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(f'  ✅ Created: {constituency_name} ({code})')
                else:
                    # Update district if it was missing
                    if constituency.district != district:
                        constituency.district = district
                        constituency.save()
                        updated_count += 1
                        self.stdout.write(f'  🔄 Updated: {constituency_name} - assigned to {district_name}')
                    else:
                        self.stdout.write(f'  ⏭️  Exists: {constituency_name}')

        # Summary
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('✅ CONSTITUENCY POPULATION COMPLETE'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'📊 Statistics:')
        self.stdout.write(f'   • Created: {created_count} constituencies')
        self.stdout.write(f'   • Updated: {updated_count} constituencies')
        self.stdout.write(f'   • Skipped: {skipped_count} constituencies (district not found)')
        self.stdout.write(f'   • Total in DB: {Constituency.objects.filter(state=tn_state).count()}')
        self.stdout.write('=' * 80)

        if Constituency.objects.filter(state=tn_state).count() >= 234:
            self.stdout.write(self.style.SUCCESS('\n🎉 SUCCESS: All 234 Tamil Nadu constituencies are now in the database!'))
            self.stdout.write(self.style.SUCCESS('Next step: Run "python manage.py setup_supabase_users --preserve-existing" to create remaining analysts and users'))
        else:
            self.stdout.write(self.style.WARNING(f'\n⚠️  WARNING: Expected 234 constituencies, found {Constituency.objects.filter(state=tn_state).count()}'))
