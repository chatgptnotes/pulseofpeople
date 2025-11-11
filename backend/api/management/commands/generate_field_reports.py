"""
Django management command to generate 3,000 realistic field reports from volunteers/booth agents.
Follows TVK party ground-level reporting patterns with realistic Tamil Nadu scenarios.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from api.models import (
    FieldReport, State, District, Constituency, IssueCategory,
    VoterSegment, PoliticalParty, BoothAgent
)
import random
from datetime import datetime, timedelta
from decimal import Decimal

fake = Faker(['en_IN'])


class Command(BaseCommand):
    help = 'Generate 3,000 realistic field reports from volunteers with TVK-specific patterns'

    def __init__(self):
        super().__init__()
        self.report_count = 0
        self.volunteers = []
        self.constituencies = []
        self.districts = []
        self.state = None
        self.issue_categories = []
        self.voter_segments = []
        self.parties = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=3000,
            help='Number of field reports to generate (default: 3000)'
        )

    def handle(self, *args, **options):
        count = options['count']

        self.stdout.write(self.style.SUCCESS(f'Starting generation of {count} field reports...'))

        # Load reference data
        self._load_reference_data()

        # Generate reports
        self._generate_reports(count)

        # Print statistics
        self._print_statistics()

        self.stdout.write(self.style.SUCCESS(f'Successfully created {self.report_count} field reports!'))

    def _load_reference_data(self):
        """Load all required reference data from database"""
        self.stdout.write('Loading reference data...')

        # Get Tamil Nadu state
        self.state = State.objects.filter(code='TN').first()
        if not self.state:
            self.stdout.write(self.style.ERROR('Tamil Nadu state not found. Please run seed data first.'))
            return

        # Get all volunteers and booth agents
        self.volunteers = list(User.objects.filter(
            profile__role__in=['volunteer', 'user']
        ).select_related('profile')[:500])

        if not self.volunteers:
            self.stdout.write(self.style.ERROR('No volunteers found. Please create users first.'))
            return

        # Get constituencies and districts
        self.constituencies = list(Constituency.objects.filter(state=self.state).select_related('district'))
        self.districts = list(District.objects.filter(state=self.state))

        # Get issue categories
        self.issue_categories = list(IssueCategory.objects.filter(is_active=True))

        # Get voter segments
        self.voter_segments = list(VoterSegment.objects.filter(is_active=True))

        # Get political parties
        self.parties = list(PoliticalParty.objects.all())

        self.stdout.write(self.style.SUCCESS(
            f'Loaded: {len(self.volunteers)} volunteers, {len(self.constituencies)} constituencies, '
            f'{len(self.issue_categories)} issue categories, {len(self.voter_segments)} voter segments'
        ))

    def _generate_reports(self, count):
        """Generate field reports with realistic distribution"""

        # Report type distribution
        report_types = [
            ('daily_summary', 1500),
            ('event_feedback', 750),
            ('issue_report', 450),
            ('competitor_activity', 150),
            ('booth_report', 150),
        ]

        # Verification status distribution
        verification_statuses = [
            ('verified', 0.70),
            ('pending', 0.25),
            ('disputed', 0.05),
        ]

        reports_to_create = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=60)

        self.stdout.write('Generating field reports...')

        for report_type, type_count in report_types:
            for i in range(type_count):
                volunteer = random.choice(self.volunteers)
                constituency = random.choice(self.constituencies) if self.constituencies else None
                district = constituency.district if constituency else random.choice(self.districts) if self.districts else None

                # Generate report timestamp (more recent = more reports)
                # Weight towards recent dates
                days_ago = int(random.triangular(0, 60, 5))
                report_time = end_date - timedelta(
                    days=days_ago,
                    hours=random.randint(18, 21),  # Peak reporting 6-9 PM
                    minutes=random.randint(0, 59)
                )

                # Geographic classification
                is_urban = random.random() < 0.45
                is_semi_urban = random.random() < 0.35

                # Generate ward number
                ward_num = random.randint(1, 60) if constituency else 1
                ward = f"Ward-{ward_num}"

                # Verification status
                verification_status = random.choices(
                    [s[0] for s in verification_statuses],
                    weights=[s[1] for s in verification_statuses]
                )[0]

                # Create report based on type
                report = self._create_report_by_type(
                    report_type=report_type,
                    volunteer=volunteer,
                    constituency=constituency,
                    district=district,
                    ward=ward,
                    report_time=report_time,
                    verification_status=verification_status,
                    is_urban=is_urban
                )

                reports_to_create.append(report)

                # Bulk insert every 500 records
                if len(reports_to_create) >= 500:
                    with transaction.atomic():
                        FieldReport.objects.bulk_create(reports_to_create, ignore_conflicts=True)
                        self.report_count += len(reports_to_create)
                        self.stdout.write(f'Created {self.report_count} reports...')
                        reports_to_create = []

        # Insert remaining reports
        if reports_to_create:
            with transaction.atomic():
                created_reports = FieldReport.objects.bulk_create(reports_to_create, ignore_conflicts=True)
                self.report_count += len(created_reports)

                # Add many-to-many relationships
                self._add_many_to_many_relations(created_reports)

    def _create_report_by_type(self, report_type, volunteer, constituency, district, ward,
                                 report_time, verification_status, is_urban):
        """Create a field report based on type with realistic content"""

        area = self._get_area_name(is_urban, ward)
        booth_num = f"{random.randint(1, 150):03d}" if random.random() < 0.3 else ""

        report = FieldReport(
            volunteer=volunteer,
            state=self.state,
            district=district,
            constituency=constituency,
            ward=ward,
            booth_number=booth_num,
            report_type=report_type,
            verification_status=verification_status,
            report_date=report_time.date(),
            timestamp=report_time,
        )

        if report_type == 'daily_summary':
            report.title, report.notes = self._generate_daily_summary(ward, area, is_urban)
            report.positive_reactions = self._get_positive_reactions()
            report.negative_reactions = self._get_negative_reactions()

        elif report_type == 'event_feedback':
            report.title, report.notes = self._generate_event_feedback(area, is_urban)
            report.crowd_size = random.randint(50, 10000)
            report.positive_reactions = self._get_event_positive_reactions()
            report.quotes = self._get_event_quotes()

        elif report_type == 'issue_report':
            report.title, report.notes = self._generate_issue_report(area, ward, is_urban)
            report.negative_reactions = self._get_issue_negative_reactions()

        elif report_type == 'competitor_activity':
            report.title, report.notes = self._generate_competitor_activity(area)
            if self.parties:
                report.competitor_party = random.choice(self.parties)
            report.competitor_activity_description = report.notes
            report.crowd_size = random.randint(50, 500)

        elif report_type == 'booth_report':
            report.title, report.notes = self._generate_booth_report(ward, booth_num)
            report.positive_reactions = self._get_positive_reactions()

        # Add verification data
        if verification_status == 'verified':
            report.verified_by = random.choice(self.volunteers)
            report.verified_at = report_time + timedelta(hours=random.randint(2, 48))
            report.verification_notes = "Field report verified by supervisor. Data cross-checked."
        elif verification_status == 'disputed':
            report.verification_notes = "Crowd size seems inflated. Needs re-verification."

        return report

    def _add_many_to_many_relations(self, reports):
        """Add many-to-many relationships after bulk creation"""
        for report in reports:
            # Add 1-3 issue categories
            if self.issue_categories:
                issues = random.sample(self.issue_categories, k=min(random.randint(1, 3), len(self.issue_categories)))
                report.key_issues.set(issues)

            # Add voter segments met
            if self.voter_segments:
                segments = random.sample(self.voter_segments, k=min(random.randint(1, 2), len(self.voter_segments)))
                report.voter_segments_met.set(segments)

    def _get_area_name(self, is_urban, ward):
        """Generate realistic area names"""
        if is_urban:
            urban_areas = [
                'T Nagar', 'Adyar', 'Anna Nagar', 'Velachery', 'Tambaram',
                'RS Puram', 'Gandhipuram', 'Saibaba Colony', 'Race Course',
                'Anna Salai', 'Perambur', 'KK Nagar', 'Kodambakkam', 'Mylapore',
                'Ashok Nagar', 'Vadapalani', 'Porur', 'Sholinganallur'
            ]
            return random.choice(urban_areas)
        else:
            return f"{ward} Area"

    # Daily Summary Templates
    def _generate_daily_summary(self, ward, area, is_urban):
        templates = [
            (
                f"Daily Field Visit - {ward}",
                f"{ward} field visit completed. Met 45 families, mostly positive response to TVK vision. Water supply remains top concern in {area}. Residents want immediate action on drinking water crisis."
            ),
            (
                f"Door-to-Door Coverage - {area}",
                f"Booth coverage in {area}: 60% households contacted. Youth showing strong interest in employment programs. Many asked about skill development initiatives and job creation plans."
            ),
            (
                f"Ground Report - {ward}",
                f"Door-to-door in {area}: Mixed reactions. NEET issue resonates strongly with students, parents very concerned about education costs and accessibility for rural students."
            ),
            (
                f"Field Activity Summary - {area}",
                f"Covered {random.randint(30, 80)} households in {area} today. Key concerns: water scarcity, unemployment, agriculture input costs. TVK's anti-corruption stand getting good response."
            ),
            (
                f"Community Engagement - {ward}",
                f"Met with {random.randint(20, 50)} families. Strong support for TVK's stance on social justice. People want change from DMK-AIADMK cycle. Youth very enthusiastic about new political movement."
            ),
        ]
        return random.choice(templates)

    # Event Feedback Templates
    def _generate_event_feedback(self, area, is_urban):
        crowd_descriptor = "massive" if random.random() < 0.3 else "good"
        templates = [
            (
                f"TVK Rally Feedback - {area}",
                f"TVK rally in {area}: Estimated {random.randint(3000, 8000)}+ attendance. Crowd very enthusiastic. Key topics resonated: jobs, water, corruption-free governance. Youth participation exceptional."
            ),
            (
                f"Town Hall Meeting Success - {area}",
                f"Town hall meeting in {area} was highly successful. 200+ participants asked detailed questions about healthcare access, education reforms. Very positive sentiment, people want actionable solutions."
            ),
            (
                f"Public Meeting Report - {area}",
                f"Public meeting had {crowd_descriptor} turnout. Vijay's speech on social justice and equality received standing ovation. Many first-time voters expressing strong support. NEET abolition demand got huge applause."
            ),
            (
                f"Community Gathering - {area}",
                f"Corner meeting in {area} attended by {random.randint(100, 300)} residents. Interactive session on local issues. People appreciate TVK's grassroots approach and listening to ground realities."
            ),
        ]
        return random.choice(templates)

    # Issue Report Templates
    def _generate_issue_report(self, area, ward, is_urban):
        templates = [
            (
                f"URGENT: Water Crisis - {ward}",
                f"URGENT: Water crisis worsening in {ward}. Residents without supply for 3 days. Tanker water expensive at Rs.{random.randint(800, 1500)} per load. Immediate attention needed. Women and children traveling 2km to fetch water."
            ),
            (
                f"Employment Crisis - {area}",
                f"Multiple families in {area} report job loss due to factory closure. Economic distress very high. {random.randint(300, 800)} workers affected. No government response or compensation. Families struggling to make ends meet."
            ),
            (
                f"Fishermen Community Alert - {area}",
                f"Fishermen community raising SL Navy arrest concerns. {random.randint(10, 25)} families affected this month alone. Boats confiscated, livelihoods destroyed. Community demanding government intervention and protection."
            ),
            (
                f"Agriculture Distress - {ward}",
                f"Farmers in {ward} facing severe crisis. No Cauvery water for {random.randint(15, 45)} days. Paddy fields drying up. Input costs doubled but MSP unchanged. Debt burden increasing, many considering quitting farming."
            ),
            (
                f"Healthcare Emergency - {area}",
                f"Primary Health Center in {area} non-functional. No doctors for 2 weeks. Pregnant women forced to travel 30km for basic checkups. Medical emergency cases being turned away. Critical situation needs immediate action."
            ),
            (
                f"Education Infrastructure Crisis - {ward}",
                f"Government school in {ward} has no proper building. {random.randint(200, 400)} students studying under trees. No toilets, no drinking water. Parents demanding infrastructure improvement or school merger."
            ),
        ]
        return random.choice(templates)

    # Competitor Activity Templates
    def _generate_competitor_activity(self, area):
        parties = ['DMK', 'AIADMK', 'BJP', 'Congress']
        party = random.choice(parties)
        templates = [
            (
                f"{party} Activity Observed - {area}",
                f"{party} organized small rally in {area}. Approximately {random.randint(150, 400)} attendees. Focus on existing government schemes and freebies. Crowd response lukewarm."
            ),
            (
                f"Opposition Campaign - {area}",
                f"{party} booth setup observed in {area}. Workers distributing pamphlets about welfare schemes. Minimal public engagement. People asking critical questions about unfulfilled promises."
            ),
            (
                f"Competitor Rally - {area}",
                f"{party} public meeting in {area}. Estimated {random.randint(300, 800)} participants. Many were brought by organizers. Local issues not addressed, only party rhetoric. TVK gaining ground in comparison."
            ),
        ]
        return random.choice(templates)

    # Booth Report Templates
    def _generate_booth_report(self, ward, booth_num):
        templates = [
            (
                f"Booth Assessment - {ward}",
                f"Booth {booth_num} coverage status: {random.randint(50, 85)}% households mapped. Voter database {random.randint(60, 90)}% updated. {random.randint(5, 15)} booth-level volunteers active. Need more volunteers for complete coverage."
            ),
            (
                f"Booth Strength Analysis - {ward}",
                f"Booth {booth_num} has {random.randint(600, 1200)} registered voters. Our estimated support: {random.randint(25, 45)}%. Swing voters: {random.randint(20, 35)}%. Strong opposition: {random.randint(15, 30)}%. Focus needed on undecided voters."
            ),
        ]
        return random.choice(templates)

    def _get_positive_reactions(self):
        reactions = [
            "Strong support for anti-corruption stance",
            "Youth very enthusiastic about new movement",
            "Appreciate grassroots approach",
            "Want alternative to DMK-AIADMK",
            "NEET abolition demand resonates",
            "Jobs creation plans appreciated",
            "Social justice message connects well",
            "Women voters showing strong interest",
        ]
        return random.sample(reactions, k=random.randint(2, 4))

    def _get_negative_reactions(self):
        reactions = [
            "Skeptical about new party effectiveness",
            "Wait and watch approach",
            "Concerned about political experience",
            "Want more concrete policy details",
            "Worried about winnability",
            "Questions about alliance strategy",
        ]
        return random.sample(reactions, k=random.randint(1, 3))

    def _get_event_positive_reactions(self):
        reactions = [
            "Massive crowd turnout exceeded expectations",
            "Standing ovation for key policy points",
            "Youth participation unprecedented",
            "First-time voters very engaged",
            "Social media buzz very positive",
            "Local media coverage extensive",
            "Volunteers highly motivated post-event",
        ]
        return random.sample(reactions, k=random.randint(3, 5))

    def _get_issue_negative_reactions(self):
        reactions = [
            "Community very angry about government inaction",
            "People losing faith in political system",
            "Urgent intervention needed",
            "Families in severe distress",
            "Children's future at stake",
            "Economic hardship increasing",
        ]
        return random.sample(reactions, k=random.randint(2, 4))

    def _get_event_quotes(self):
        quotes = [
            "Finally someone who understands our problems - Auto driver, 42",
            "My son needs a job, not empty promises - Mother of graduate, 48",
            "NEET destroyed my daughter's dreams - Father, 51",
            "We want change, not same old politics - College student, 21",
            "TVK gives us hope for corruption-free governance - Small business owner, 38",
            "Youth needs opportunities in Tamil Nadu - Engineering graduate, 24",
        ]
        return random.sample(quotes, k=random.randint(2, 4))

    def _print_statistics(self):
        """Print comprehensive statistics"""
        self.stdout.write(self.style.SUCCESS('\n=== FIELD REPORTS GENERATION STATISTICS ==='))

        # Count by report type
        for report_type, _ in FieldReport.REPORT_TYPES:
            count = FieldReport.objects.filter(report_type=report_type).count()
            percentage = (count / self.report_count * 100) if self.report_count > 0 else 0
            self.stdout.write(f'{report_type}: {count} ({percentage:.1f}%)')

        # Count by verification status
        self.stdout.write('\nVerification Status:')
        for status, _ in FieldReport.VERIFICATION_STATUS:
            count = FieldReport.objects.filter(verification_status=status).count()
            percentage = (count / self.report_count * 100) if self.report_count > 0 else 0
            self.stdout.write(f'{status}: {count} ({percentage:.1f}%)')

        # Date range
        oldest = FieldReport.objects.order_by('timestamp').first()
        newest = FieldReport.objects.order_by('-timestamp').first()
        if oldest and newest:
            self.stdout.write(f'\nDate Range: {oldest.timestamp.date()} to {newest.timestamp.date()}')

        # Top volunteers
        from django.db.models import Count
        top_reporters = FieldReport.objects.values('volunteer__username').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        self.stdout.write('\nTop 5 Reporters:')
        for reporter in top_reporters:
            self.stdout.write(f"  {reporter['volunteer__username']}: {reporter['count']} reports")

        self.stdout.write(self.style.SUCCESS(f'\nTotal Field Reports: {self.report_count}'))
