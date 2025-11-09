"""
Django management command to generate realistic TVK event data

Usage:
    python manage.py generate_events
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from api.models import Event, Campaign, Constituency, UserProfile
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Generate 150 realistic TVK events across different types'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing events before generating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing all existing events...'))
            Event.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Events cleared.'))

        self.stdout.write(self.style.NOTICE('Starting event generation...'))

        # Get required data
        constituencies = list(Constituency.objects.all())
        if not constituencies:
            self.stdout.write(self.style.ERROR('No constituencies found. Please load constituency data first.'))
            return

        # Get campaigns (70% of events will be linked to campaigns)
        campaigns = list(Campaign.objects.all())
        if not campaigns:
            self.stdout.write(self.style.WARNING('No campaigns found. Events will be created without campaign linkage.'))

        # Get organizers (managers and analysts)
        organizers = list(User.objects.filter(profile__role__in=['manager', 'analyst']))
        if not organizers:
            self.stdout.write(self.style.ERROR('No organizers found. Please create users first.'))
            return

        # Get volunteers
        volunteers = list(User.objects.filter(profile__role='volunteer'))
        if not volunteers:
            self.stdout.write(self.style.WARNING('No volunteers found. Events will be created without volunteer assignments.'))

        # Define event counts by type
        event_distribution = {
            'rally': 30,        # 20%
            'meeting': 60,      # 40%
            'door_to_door': 45, # 30%
            'booth_visit': 15,  # 10%
        }

        # Statistics tracking
        stats = {
            'total': 0,
            'by_type': {'rally': 0, 'meeting': 0, 'door_to_door': 0, 'booth_visit': 0},
            'by_status': {'planned': 0, 'ongoing': 0, 'completed': 0, 'cancelled': 0},
            'with_campaign': 0,
            'total_budget': Decimal('0'),
            'total_expenses': Decimal('0'),
            'expected_attendance': 0,
            'actual_attendance': 0,
        }

        # Generate events
        with transaction.atomic():
            events = []

            # Generate rallies
            for i in range(event_distribution['rally']):
                event = self._create_rally(i, constituencies, campaigns, organizers)
                events.append(event)
                self._update_stats(stats, event)

            # Generate meetings
            for i in range(event_distribution['meeting']):
                event = self._create_meeting(i, constituencies, campaigns, organizers)
                events.append(event)
                self._update_stats(stats, event)

            # Generate door-to-door events
            for i in range(event_distribution['door_to_door']):
                event = self._create_door_to_door(i, constituencies, campaigns, organizers)
                events.append(event)
                self._update_stats(stats, event)

            # Generate booth visits
            for i in range(event_distribution['booth_visit']):
                event = self._create_booth_visit(i, constituencies, campaigns, organizers)
                events.append(event)
                self._update_stats(stats, event)

            # Bulk create events
            Event.objects.bulk_create(events)

            # Add many-to-many relationships (volunteers)
            if volunteers:
                self.stdout.write(self.style.NOTICE('Assigning volunteers to events...'))
                for event in Event.objects.all().order_by('-created_at')[:len(events)]:
                    volunteer_count = self._get_volunteer_count(event.event_type)
                    assigned_volunteers = random.sample(volunteers, min(volunteer_count, len(volunteers)))
                    event.volunteers.set(assigned_volunteers)

        # Display statistics
        self._display_statistics(stats)

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully generated {stats["total"]} events!'))

    def _create_rally(self, index, constituencies, campaigns, organizers):
        """Create a rally event"""
        now = timezone.now()

        # Rally templates
        rally_names = [
            ('TVK Mega Rally - Marina Beach, Chennai', 'Chennai Marina Beach', 13.0503, 80.2824),
            ('Youth Employment Rally - Coimbatore RS Puram', 'RS Puram, Coimbatore', 11.0030, 76.9630),
            ('Farmers Rights Rally - Thanjavur', 'Thanjavur Town Hall', 10.7870, 79.1378),
            ('Women Empowerment Rally - Madurai', 'Tamukkam Ground, Madurai', 9.9252, 78.1198),
            ('Save Water Rally - Trichy', 'Trichy Junction', 10.8155, 78.7047),
            ('NEET Opposition Rally - Salem', 'Salem Central', 11.6643, 78.1460),
            ('Tamil Rights Rally - Erode', 'Erode Municipal Stadium', 11.3410, 77.7172),
            ('Healthcare Access Rally - Vellore', 'Vellore Fort Grounds', 12.9165, 79.1325),
            ('Education Rights Rally - Tirunelveli', 'Tirunelveli Junction', 8.7139, 77.7567),
            ('Jobs Rally - Coimbatore Gandhipuram', 'Gandhipuram, Coimbatore', 11.0168, 76.9558),
            ('Anti-Corruption Rally - Chennai T Nagar', 'Panagal Park, T Nagar', 13.0418, 80.2341),
            ('Fisher Rights Rally - Ramanathapuram', 'Ramanathapuram Beach', 9.3623, 78.8379),
            ('Industrial Workers Rally - Hosur', 'Hosur Industrial Area', 12.7409, 77.8253),
            ('TVK Vision Rally - Kanyakumari', 'Vivekananda Rock Area', 8.0883, 77.5385),
            ('Student Unity Rally - Anna University', 'Anna University Chennai', 13.0113, 80.2336),
        ]

        # Select rally details
        rally_data = rally_names[index % len(rally_names)]
        name, location, lat, lng = rally_data

        # Temporal distribution
        status, time_offset = self._get_event_timing('rally')

        # Set datetime
        days_offset = random.randint(*time_offset)
        event_date = now + timedelta(days=days_offset)

        # Rallies typically happen on weekends, 10am-1pm or 5pm-8pm
        if event_date.weekday() > 4:  # Already weekend
            pass
        else:
            # Move to next weekend
            days_to_weekend = 5 - event_date.weekday()
            event_date = event_date + timedelta(days=days_to_weekend)

        # Time slot
        if random.random() < 0.6:  # Morning rally
            start_hour = random.randint(9, 11)
        else:  # Evening rally
            start_hour = random.randint(17, 18)

        start_datetime = event_date.replace(hour=start_hour, minute=0, second=0)
        end_datetime = start_datetime + timedelta(hours=random.randint(2, 4))

        # Attendance
        expected = random.randint(5000, 50000)
        if status == 'completed':
            actual = int(expected * random.uniform(0.80, 1.20))
        elif status == 'ongoing':
            actual = int(expected * random.uniform(0.60, 0.90))
        else:
            actual = 0

        # Budget and expenses
        budget = Decimal(random.randint(200000, 2000000))  # 2L-20L
        if status == 'completed':
            expenses = budget * Decimal(random.uniform(0.85, 1.00))
        elif status == 'ongoing':
            expenses = budget * Decimal(random.uniform(0.40, 0.60))
        else:
            expenses = budget * Decimal(random.uniform(0.00, 0.20))

        # Campaign linkage (70% chance)
        campaign = random.choice(campaigns) if campaigns and random.random() < 0.70 else None

        # Notes for completed rallies
        notes = ''
        if status == 'completed':
            notes = self._get_rally_notes()

        # Photos (3-10 for completed events)
        photos = []
        if status == 'completed':
            photo_count = random.randint(3, 10)
            photos = [f'https://storage.tvk.in/events/rally_{index}_{i}.jpg' for i in range(photo_count)]

        return Event(
            event_name=name,
            event_type='rally',
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location,
            ward=f'Ward {random.randint(1, 200)}',
            constituency=random.choice(constituencies),
            latitude=Decimal(str(lat)),
            longitude=Decimal(str(lng)),
            expected_attendance=expected,
            actual_attendance=actual,
            organizer=random.choice(organizers),
            campaign=campaign,
            budget=budget,
            expenses=expenses,
            status=status,
            notes=notes,
            photos=photos,
        )

    def _create_meeting(self, index, constituencies, campaigns, organizers):
        """Create a meeting event"""
        now = timezone.now()

        # Meeting templates
        meeting_names = [
            ('Town Hall - Water Crisis Solutions - T Nagar', 'T Nagar Community Hall', 13.0418, 80.2341, 'town_hall'),
            ('Youth Connect Meeting - Anna University', 'Anna University Auditorium', 13.0113, 80.2336, 'meeting'),
            ('Women Forum - Coimbatore Gandhipuram', 'Gandhipuram Hall', 11.0168, 76.9558, 'meeting'),
            ('Fisher Community Dialogue - Ramanathapuram', 'Fishermen Community Center', 9.3623, 78.8379, 'meeting'),
            ('Farmers Meet - Thanjavur Delta', 'Agricultural College', 10.7870, 79.1378, 'meeting'),
            ('Student Leaders Forum - Madurai', 'Madurai Kamaraj University', 9.9252, 78.1198, 'meeting'),
            ('Ward Meeting - Mylapore Zone', 'Mylapore Cultural Center', 13.0339, 80.2619, 'meeting'),
            ('Business Community Meet - Coimbatore', 'RS Puram Business Center', 11.0030, 76.9630, 'meeting'),
            ('Auto Drivers Association Meet - Salem', 'Salem Bus Stand', 11.6643, 78.1460, 'meeting'),
            ('Town Hall - Education Reform - Trichy', 'Trichy City Hall', 10.8155, 78.7047, 'town_hall'),
            ('Women Self Help Groups - Vellore', 'Vellore Women Center', 12.9165, 79.1325, 'meeting'),
            ('Youth Employment Forum - Erode', 'Erode IT Park', 11.3410, 77.7172, 'meeting'),
            ('Senior Citizens Meet - Adyar', 'Adyar Club', 13.0067, 80.2577, 'meeting'),
            ('Traders Association - Tirunelveli', 'Tirunelveli Market Complex', 8.7139, 77.7567, 'meeting'),
            ('Industrial Workers Forum - Hosur', 'Hosur Industrial Area', 12.7409, 77.8253, 'meeting'),
        ]

        # Select meeting details
        meeting_data = meeting_names[index % len(meeting_names)]
        name, location, lat, lng, mtype = meeting_data

        # Temporal distribution
        status, time_offset = self._get_event_timing('meeting')

        # Set datetime
        days_offset = random.randint(*time_offset)
        event_date = now + timedelta(days=days_offset)

        # Meetings typically after work hours: 6pm-9pm
        start_hour = random.randint(18, 19)
        start_datetime = event_date.replace(hour=start_hour, minute=0, second=0)
        end_datetime = start_datetime + timedelta(hours=random.randint(2, 3))

        # Attendance
        expected = random.randint(200, 2000)
        if status == 'completed':
            actual = int(expected * random.uniform(0.70, 1.10))
        elif status == 'ongoing':
            actual = int(expected * random.uniform(0.50, 0.80))
        else:
            actual = 0

        # Budget and expenses
        budget = Decimal(random.randint(20000, 200000))  # 20K-2L
        if status == 'completed':
            expenses = budget * Decimal(random.uniform(0.85, 1.00))
        elif status == 'ongoing':
            expenses = budget * Decimal(random.uniform(0.40, 0.60))
        else:
            expenses = budget * Decimal(random.uniform(0.00, 0.20))

        # Campaign linkage (70% chance)
        campaign = random.choice(campaigns) if campaigns and random.random() < 0.70 else None

        # Notes for completed meetings
        notes = ''
        if status == 'completed':
            notes = self._get_meeting_notes()

        # Photos (3-8 for completed events)
        photos = []
        if status == 'completed':
            photo_count = random.randint(3, 8)
            photos = [f'https://storage.tvk.in/events/meeting_{index}_{i}.jpg' for i in range(photo_count)]

        return Event(
            event_name=name,
            event_type=mtype,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=location,
            ward=f'Ward {random.randint(1, 200)}',
            constituency=random.choice(constituencies),
            latitude=Decimal(str(lat)),
            longitude=Decimal(str(lng)),
            expected_attendance=expected,
            actual_attendance=actual,
            organizer=random.choice(organizers),
            campaign=campaign,
            budget=budget,
            expenses=expenses,
            status=status,
            notes=notes,
            photos=photos,
        )

    def _create_door_to_door(self, index, constituencies, campaigns, organizers):
        """Create a door-to-door event"""
        now = timezone.now()

        # Chennai wards
        chennai_wards = [
            'T Nagar', 'Mylapore', 'Adyar', 'Velachery', 'Anna Nagar',
            'Kodambakkam', 'Nungambakkam', 'Egmore', 'Royapettah', 'Guindy',
            'Ashok Nagar', 'KK Nagar', 'Saidapet', 'Teynampet', 'Triplicane'
        ]

        # Coimbatore areas
        coimbatore_areas = [
            'RS Puram', 'Gandhipuram', 'Saibaba Colony', 'Peelamedu', 'Singanallur',
            'Town Hall', 'Race Course', 'Ukkadam', 'Hopes College', 'Podanur'
        ]

        # Other areas
        other_areas = [
            'Thanjavur Main', 'Madurai Central', 'Trichy Fort', 'Salem Steel Plant',
            'Vellore Fort', 'Erode Bazaar', 'Tirunelveli Junction', 'Tiruvannamalai Town',
            'Dindigul Market', 'Karur Main', 'Namakkal Center', 'Cuddalore Port'
        ]

        all_areas = chennai_wards + coimbatore_areas + other_areas
        area = all_areas[index % len(all_areas)]

        # Name
        name = f'Ward-{random.randint(1, 200)} Door Canvassing - {area}'

        # Location coordinates (varied)
        lat = Decimal(str(random.uniform(8.0, 13.5)))
        lng = Decimal(str(random.uniform(76.5, 80.5)))

        # Temporal distribution
        status, time_offset = self._get_event_timing('door_to_door')

        # Set datetime
        days_offset = random.randint(*time_offset)
        event_date = now + timedelta(days=days_offset)

        # Door-to-door typically 4pm-7pm (after work hours)
        start_hour = random.randint(16, 17)
        start_datetime = event_date.replace(hour=start_hour, minute=0, second=0)
        end_datetime = start_datetime + timedelta(hours=3)

        # Attendance (households contacted)
        expected = random.randint(50, 500)
        if status == 'completed':
            actual = int(expected * random.uniform(0.60, 0.90))
        elif status == 'ongoing':
            actual = int(expected * random.uniform(0.30, 0.60))
        else:
            actual = 0

        # Budget and expenses
        budget = Decimal(random.randint(5000, 50000))  # 5K-50K
        if status == 'completed':
            expenses = budget * Decimal(random.uniform(0.85, 1.00))
        elif status == 'ongoing':
            expenses = budget * Decimal(random.uniform(0.40, 0.60))
        else:
            expenses = budget * Decimal(random.uniform(0.00, 0.20))

        # Campaign linkage (70% chance)
        campaign = random.choice(campaigns) if campaigns and random.random() < 0.70 else None

        # Notes for completed door-to-door
        notes = ''
        if status == 'completed':
            notes = self._get_door_to_door_notes(actual)

        # Photos (2-5 for completed events)
        photos = []
        if status == 'completed':
            photo_count = random.randint(2, 5)
            photos = [f'https://storage.tvk.in/events/door_{index}_{i}.jpg' for i in range(photo_count)]

        return Event(
            event_name=name,
            event_type='door_to_door',
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=f'{area} Ward',
            ward=area,
            constituency=random.choice(constituencies),
            latitude=lat,
            longitude=lng,
            expected_attendance=expected,
            actual_attendance=actual,
            organizer=random.choice(organizers),
            campaign=campaign,
            budget=budget,
            expenses=expenses,
            status=status,
            notes=notes,
            photos=photos,
        )

    def _create_booth_visit(self, index, constituencies, campaigns, organizers):
        """Create a booth visit event"""
        now = timezone.now()

        # Booth visit templates
        booth_names = [
            'Booth Monitoring - Booth #042 T Nagar',
            'Booth Agent Training - Multiple Booths Chennai',
            'Booth Inspection - Mylapore Division',
            'Booth Preparedness Check - Adyar Zone',
            'Booth Coverage Drive - Anna Nagar',
            'Booth Agent Meeting - Coimbatore Central',
            'Booth Survey - RS Puram Area',
            'Booth Saturation - Madurai East',
            'Booth Analysis - Trichy Division',
            'Booth Volunteer Training - Salem',
            'Booth Mapping - Thanjavur District',
            'Booth Strength Assessment - Vellore',
            'Booth Agent Coordination - Erode',
            'Booth Data Collection - Tirunelveli',
            'Booth Strategy Meeting - Kanyakumari',
        ]

        # Select booth visit details
        name = booth_names[index % len(booth_names)]

        # Location coordinates
        lat = Decimal(str(random.uniform(8.0, 13.5)))
        lng = Decimal(str(random.uniform(76.5, 80.5)))

        # Temporal distribution
        status, time_offset = self._get_event_timing('booth_visit')

        # Set datetime
        days_offset = random.randint(*time_offset)
        event_date = now + timedelta(days=days_offset)

        # Booth visits can happen anytime
        start_hour = random.randint(9, 16)
        start_datetime = event_date.replace(hour=start_hour, minute=0, second=0)
        end_datetime = start_datetime + timedelta(hours=random.randint(2, 4))

        # Attendance
        expected = random.randint(10, 100)
        if status == 'completed':
            actual = int(expected * random.uniform(0.80, 1.00))
        elif status == 'ongoing':
            actual = int(expected * random.uniform(0.50, 0.80))
        else:
            actual = 0

        # Budget and expenses
        budget = Decimal(random.randint(2000, 20000))  # 2K-20K
        if status == 'completed':
            expenses = budget * Decimal(random.uniform(0.85, 1.00))
        elif status == 'ongoing':
            expenses = budget * Decimal(random.uniform(0.40, 0.60))
        else:
            expenses = budget * Decimal(random.uniform(0.00, 0.20))

        # Campaign linkage (70% chance)
        campaign = random.choice(campaigns) if campaigns and random.random() < 0.70 else None

        # Notes for completed booth visits
        notes = ''
        if status == 'completed':
            notes = self._get_booth_visit_notes()

        # Photos (2-4 for completed events)
        photos = []
        if status == 'completed':
            photo_count = random.randint(2, 4)
            photos = [f'https://storage.tvk.in/events/booth_{index}_{i}.jpg' for i in range(photo_count)]

        return Event(
            event_name=name,
            event_type='booth_visit',
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            location=f'Polling Booth #{random.randint(1, 300):03d}',
            ward=f'Ward {random.randint(1, 200)}',
            constituency=random.choice(constituencies),
            latitude=lat,
            longitude=lng,
            expected_attendance=expected,
            actual_attendance=actual,
            organizer=random.choice(organizers),
            campaign=campaign,
            budget=budget,
            expenses=expenses,
            status=status,
            notes=notes,
            photos=photos,
        )

    def _get_event_timing(self, event_type):
        """Get event timing and status based on distribution"""
        # Status distribution: Completed: 50%, Ongoing: 10%, Planned: 35%, Cancelled: 5%
        rand = random.random()

        if rand < 0.50:  # Completed (50%)
            status = 'completed'
            time_offset = (-90, -1)  # Last 3 months
        elif rand < 0.60:  # Ongoing (10%)
            status = 'ongoing'
            time_offset = (-14, 0)  # Last 2 weeks
        elif rand < 0.95:  # Planned (35%)
            status = 'planned'
            time_offset = (1, 90)  # Next 3 months
        else:  # Cancelled (5%)
            status = 'cancelled'
            time_offset = (-60, 30)  # Past or future

        return status, time_offset

    def _get_volunteer_count(self, event_type):
        """Get volunteer count based on event type"""
        volunteer_ranges = {
            'rally': (20, 50),
            'meeting': (10, 25),
            'town_hall': (15, 30),
            'door_to_door': (5, 15),
            'booth_visit': (5, 12),
        }
        min_vol, max_vol = volunteer_ranges.get(event_type, (5, 20))
        return random.randint(min_vol, max_vol)

    def _get_rally_notes(self):
        """Generate realistic rally notes"""
        notes_templates = [
            "Very successful rally. Crowd response excellent. Key talking points: jobs, water, education. Media coverage good. Over 20 local reporters present.",
            "Massive turnout exceeded expectations. Strong support from youth and women voters. Main issues discussed: NEET opposition, unemployment, corruption. Social media engagement high.",
            "Good rally with enthusiastic participation. Focused on local issues - water crisis and sanitation. Positive feedback from community leaders. Need follow-up meetings.",
            "Excellent rally with energetic crowd. Youth participation exceptional. Key demands: jobs, quality education, healthcare access. Multiple TV channels covered event.",
            "Outstanding response from public. Rally focused on Tamil rights and cultural preservation. Strong emotional connect with audience. Several community organizations pledged support.",
            "Well-organized rally with disciplined crowd management. Main focus: industrial revival and job creation. Business community showed interest. Follow-up meetings scheduled.",
            "Successful rally despite rain. Core message: anti-corruption and transparent governance resonated well. Local media gave extensive coverage.",
            "Large rally with participation from all age groups. Key issues: farmer rights, loan waivers, MSP. Agricultural community very responsive. Need to maintain momentum.",
            "Powerful rally addressing fisher community concerns. Coastal rights and livelihood protection main themes. Strong community mobilization achieved.",
            "Impactful rally with clear messaging on education reform. Students and parents highly engaged. NEET opposition garnered significant support.",
        ]
        return random.choice(notes_templates)

    def _get_meeting_notes(self):
        """Generate realistic meeting notes"""
        notes_templates = [
            "Town hall productive. 25 questions from audience, mostly about NEET and unemployment. Follow-up needed with student groups. Good engagement.",
            "Interactive meeting with strong community participation. Main concerns: water supply, road conditions, sanitation. Ward-level action plan prepared.",
            "Excellent dialogue with women's groups. Safety, healthcare, and economic empowerment main topics. Multiple suggestions for policy positions.",
            "Youth forum very energetic. Jobs, education quality, startup ecosystem discussed extensively. Several young professionals volunteered for campaigns.",
            "Fisher community expressed urgent concerns about coastal erosion and livelihood. Detailed representation submitted. Immediate policy intervention needed.",
            "Farmers meeting identified key pain points: MSP, loan waivers, irrigation. Strong emotional discussions. Commitment to take up issues at state level.",
            "Student leaders forum productive. NEET, fee structure, campus placements discussed. University students willing to organize peer groups.",
            "Business community meeting focused on industrial policy, taxation, ease of doing business. Constructive suggestions received for manifesto.",
            "Auto drivers association highlighted fuel costs, licensing issues, police harassment. Practical solutions discussed. Strong support base identified.",
            "Senior citizens forum raised healthcare, pension, old age security concerns. Detailed note-taking for policy formulation. Very engaged group.",
            "Women self-help groups discussed financial inclusion, skill training, market access. Several successful case studies shared. Partnership opportunities identified.",
            "Traders association concerned about GST, local competition, market infrastructure. Direct dialogue useful for understanding ground realities.",
            "Industrial workers forum productive. Labor rights, workplace safety, wage issues central. Union leaders supportive of party positions.",
            "Ward-level meeting addressed hyperlocal issues - streetlights, garbage collection, drainage. Immediate action items identified for local body pressure.",
        ]
        return random.choice(notes_templates)

    def _get_door_to_door_notes(self, households):
        """Generate realistic door-to-door notes"""
        positive_pct = random.randint(55, 75)
        notes_templates = [
            f"Door campaign covered {households} households. {positive_pct}% positive response. Major concerns: water supply, sanitation, roads. Good voter data collected.",
            f"Productive door-to-door covering {households} households. {positive_pct}% receptive to TVK message. Primary issues: jobs, education costs, healthcare access.",
            f"Ward coverage: {households} households contacted. {positive_pct}% favorable response. Key feedback: appreciate ground connect, want regular followup.",
            f"Door canvassing reached {households} families. {positive_pct}% positive sentiment. Main demands: better schools, clean water, waste management.",
            f"Household visits: {households} completed. {positive_pct}% support indicated. Critical issues: unemployment, rising costs, infrastructure gaps.",
            f"Door campaign productive: {households} households. {positive_pct}% positive reception. Focus areas: youth jobs, women safety, senior citizen welfare.",
            f"Canvassing covered {households} homes. {positive_pct}% favorable response. Issues raised: electricity, water, transportation, healthcare.",
            f"Ward-level connect: {households} households visited. {positive_pct}% good response. Voters appreciate direct engagement. Several volunteers recruited.",
            f"Door-to-door outreach: {households} families met. {positive_pct}% positive interaction. Local issues documented for constituency report.",
            f"Household canvassing: {households} contacts made. {positive_pct}% receptive. Strong interest in party manifesto. Good database building.",
        ]
        return random.choice(notes_templates)

    def _get_booth_visit_notes(self):
        """Generate realistic booth visit notes"""
        notes_templates = [
            "Booth inspection completed. Agent training satisfactory. Voter list verification 80% done. Need more volunteers for booth coverage.",
            "Booth monitoring successful. Identified gaps in voter data. Booth agent committed and well-prepared. Follow-up training needed on EVM procedures.",
            "Multiple booth coverage drive productive. 15 booths visited. Agent morale good. Some booths need additional volunteers for saturation.",
            "Booth strength assessment completed. Strong presence in 60% booths. Weak coverage in remaining booths - action plan prepared.",
            "Booth agent coordination meeting effective. Clear roles assigned. Polling day preparation checklist reviewed. Confidence levels high.",
            "Booth survey completed successfully. Voter sentiment mapping done. Identified swing voter households for focused outreach.",
            "Booth preparedness check satisfactory. All agents briefed on polling procedures. Mock drill conducted. Ready for election day.",
            "Booth data collection productive. Updated voter lists received. Booth-wise issues documented. Need material support for some agents.",
            "Booth saturation drive successful. Covered all assigned booths. Good volunteer turnout. Identified strong supporters for day-of mobilization.",
            "Booth strategy meeting concluded with clear action items. Agent training modules distributed. Next review scheduled in 2 weeks.",
        ]
        return random.choice(notes_templates)

    def _update_stats(self, stats, event):
        """Update statistics dictionary"""
        stats['total'] += 1
        stats['by_type'][event.event_type] += 1
        stats['by_status'][event.status] += 1
        stats['total_budget'] += event.budget
        stats['total_expenses'] += event.expenses
        stats['expected_attendance'] += event.expected_attendance
        stats['actual_attendance'] += event.actual_attendance
        if event.campaign:
            stats['with_campaign'] += 1

    def _display_statistics(self, stats):
        """Display event generation statistics"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('EVENT GENERATION STATISTICS'))
        self.stdout.write('='*70)

        self.stdout.write(f"\nTotal Events Created: {stats['total']}")

        self.stdout.write('\nEvents by Type:')
        for etype, count in stats['by_type'].items():
            pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            self.stdout.write(f"  {etype.replace('_', ' ').title():20s}: {count:3d} ({pct:5.1f}%)")

        self.stdout.write('\nEvents by Status:')
        for status, count in stats['by_status'].items():
            pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            self.stdout.write(f"  {status.title():20s}: {count:3d} ({pct:5.1f}%)")

        self.stdout.write('\nCampaign Linkage:')
        linked_pct = (stats['with_campaign'] / stats['total'] * 100) if stats['total'] > 0 else 0
        self.stdout.write(f"  Events linked to campaigns: {stats['with_campaign']} ({linked_pct:.1f}%)")

        self.stdout.write('\nAttendance Summary:')
        self.stdout.write(f"  Total Expected Attendance:  {stats['expected_attendance']:,}")
        self.stdout.write(f"  Total Actual Attendance:    {stats['actual_attendance']:,}")
        if stats['expected_attendance'] > 0:
            attendance_pct = (stats['actual_attendance'] / stats['expected_attendance'] * 100)
            self.stdout.write(f"  Achievement Rate:           {attendance_pct:.1f}%")

        self.stdout.write('\nBudget Summary:')
        self.stdout.write(f"  Total Budget Allocated: ₹{stats['total_budget']:,.2f}")
        self.stdout.write(f"  Total Expenses:         ₹{stats['total_expenses']:,.2f}")
        if stats['total_budget'] > 0:
            expense_pct = (stats['total_expenses'] / stats['total_budget'] * 100)
            self.stdout.write(f"  Budget Utilization:     {expense_pct:.1f}%")

        avg_budget = stats['total_budget'] / stats['total'] if stats['total'] > 0 else 0
        avg_attendance = stats['expected_attendance'] / stats['total'] if stats['total'] > 0 else 0
        self.stdout.write(f"\n  Average Event Budget:      ₹{avg_budget:,.2f}")
        self.stdout.write(f"  Average Expected Attendance: {avg_attendance:,.0f}")

        self.stdout.write('\n' + '='*70)
