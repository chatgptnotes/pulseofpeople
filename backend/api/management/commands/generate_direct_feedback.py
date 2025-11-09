"""
Django management command to generate 5,000 realistic direct citizen feedback submissions.
Follows real Tamil Nadu citizen concerns with realistic AI analysis patterns.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from faker import Faker
from api.models import (
    DirectFeedback, State, District, Constituency, IssueCategory,
    VoterSegment
)
import random
from datetime import datetime, timedelta
from decimal import Decimal

fake = Faker(['en_IN'])


class Command(BaseCommand):
    help = 'Generate 5,000 realistic direct citizen feedback submissions with AI analysis'

    def __init__(self):
        super().__init__()
        self.feedback_count = 0
        self.state = None
        self.districts = []
        self.constituencies = []
        self.issue_categories = {}
        self.voter_segments = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5000,
            help='Number of feedback submissions to generate (default: 5000)'
        )

    def handle(self, *args, **options):
        count = options['count']

        self.stdout.write(self.style.SUCCESS(f'Starting generation of {count} direct feedback submissions...'))

        # Load reference data
        self._load_reference_data()

        # Generate feedback
        self._generate_feedback(count)

        # Print statistics
        self._print_statistics()

        self.stdout.write(self.style.SUCCESS(f'Successfully created {self.feedback_count} feedback submissions!'))

    def _load_reference_data(self):
        """Load all required reference data from database"""
        self.stdout.write('Loading reference data...')

        # Get Tamil Nadu state
        self.state = State.objects.filter(code='TN').first()
        if not self.state:
            self.stdout.write(self.style.ERROR('Tamil Nadu state not found. Please run seed data first.'))
            return

        # Get districts and constituencies
        self.districts = list(District.objects.filter(state=self.state))
        self.constituencies = list(Constituency.objects.filter(state=self.state).select_related('district'))

        # Get issue categories by name for easy lookup
        for issue in IssueCategory.objects.filter(is_active=True):
            self.issue_categories[issue.name] = issue

        # Get voter segments
        self.voter_segments = list(VoterSegment.objects.filter(is_active=True))

        self.stdout.write(self.style.SUCCESS(
            f'Loaded: {len(self.districts)} districts, {len(self.constituencies)} constituencies, '
            f'{len(self.issue_categories)} issue categories, {len(self.voter_segments)} voter segments'
        ))

    def _generate_feedback(self, count):
        """Generate direct feedback with realistic distribution"""

        # Issue distribution matching real TN priorities
        issue_distribution = [
            ('Water Supply', 1100, 'water'),
            ('Jobs/Employment', 900, 'jobs'),
            ('Agriculture/Farmers', 600, 'agriculture'),
            ('NEET Opposition', 500, 'neet'),
            ('Healthcare', 450, 'healthcare'),
            ('Education', 400, 'education'),
            ('Fishermen Rights', 300, 'fishermen'),
            ('Cauvery Water', 250, 'cauvery'),
            ('Others', 500, 'other'),
        ]

        # Status distribution
        status_distribution = [
            ('analyzed', 0.60),
            ('reviewed', 0.20),
            ('pending', 0.15),
            ('escalated', 0.05),
        ]

        feedback_to_create = []
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)

        self.stdout.write('Generating direct feedback submissions...')

        for issue_name, issue_count, issue_key in issue_distribution:
            for i in range(issue_count):
                # Get random location
                constituency = random.choice(self.constituencies) if self.constituencies else None
                district = constituency.district if constituency else random.choice(self.districts) if self.districts else None

                # Generate submission timestamp (event-driven spikes)
                days_ago = self._get_weighted_days_ago()
                submission_time = end_date - timedelta(
                    days=days_ago,
                    hours=random.randint(8, 22),
                    minutes=random.randint(0, 59)
                )

                # Generate citizen details
                gender = random.choices(['male', 'female', 'other'], weights=[0.60, 0.35, 0.05])[0]
                citizen_name = fake.name_male() if gender == 'male' else fake.name_female()
                citizen_age = int(random.triangular(18, 75, 35))
                citizen_phone = f"+91{random.randint(7000000000, 9999999999)}"
                citizen_email = fake.email() if random.random() < 0.30 else ""

                # Urban/rural distribution
                is_urban = random.random() < 0.55

                # Ward and location
                ward_num = random.randint(1, 60) if constituency else 1
                ward = f"Ward-{ward_num}"

                # Status
                status = random.choices(
                    [s[0] for s in status_distribution],
                    weights=[s[1] for s in status_distribution]
                )[0]

                # Create feedback based on issue type
                feedback = self._create_feedback_by_issue(
                    issue_key=issue_key,
                    citizen_name=citizen_name,
                    citizen_age=citizen_age,
                    citizen_phone=citizen_phone,
                    citizen_email=citizen_email,
                    gender=gender,
                    constituency=constituency,
                    district=district,
                    ward=ward,
                    submission_time=submission_time,
                    status=status,
                    is_urban=is_urban
                )

                feedback_to_create.append(feedback)

                # Bulk insert every 500 records
                if len(feedback_to_create) >= 500:
                    with transaction.atomic():
                        DirectFeedback.objects.bulk_create(feedback_to_create, ignore_conflicts=True)
                        self.feedback_count += len(feedback_to_create)
                        self.stdout.write(f'Created {self.feedback_count} feedback submissions...')
                        feedback_to_create = []

        # Insert remaining feedback
        if feedback_to_create:
            with transaction.atomic():
                DirectFeedback.objects.bulk_create(feedback_to_create, ignore_conflicts=True)
                self.feedback_count += len(feedback_to_create)

    def _get_weighted_days_ago(self):
        """Generate timestamp with more recent entries (event-driven spikes)"""
        # 40% in last 15 days, 30% in 16-45 days, 30% in 46-90 days
        rand = random.random()
        if rand < 0.40:
            return random.randint(0, 15)
        elif rand < 0.70:
            return random.randint(16, 45)
        else:
            return random.randint(46, 90)

    def _create_feedback_by_issue(self, issue_key, citizen_name, citizen_age, citizen_phone,
                                    citizen_email, gender, constituency, district, ward,
                                    submission_time, status, is_urban):
        """Create feedback based on issue type with realistic citizen messages"""

        # Get issue category
        issue_category = self._get_issue_category(issue_key)
        voter_segment = self._get_voter_segment(issue_key)

        # Generate message based on issue
        message_text, expectations = self._generate_message_by_issue(issue_key, ward, is_urban, gender)

        # Generate AI analysis
        ai_analysis = self._generate_ai_analysis(issue_key, message_text, status)

        feedback = DirectFeedback(
            citizen_name=citizen_name,
            citizen_age=citizen_age,
            citizen_phone=citizen_phone,
            citizen_email=citizen_email,
            state=self.state,
            district=district,
            constituency=constituency,
            ward=ward,
            detailed_location=f"{ward}, {district.name if district else 'Tamil Nadu'}",
            issue_category=issue_category,
            message_text=message_text,
            expectations=expectations,
            voter_segment=voter_segment,
            status=status,
            submitted_at=submission_time,
            **ai_analysis
        )

        # Set analyzed_at and reviewed_at based on status
        if status in ['analyzed', 'reviewed', 'escalated']:
            feedback.analyzed_at = submission_time + timedelta(hours=random.randint(1, 24))

        if status in ['reviewed', 'escalated']:
            feedback.reviewed_at = feedback.analyzed_at + timedelta(hours=random.randint(2, 48))

        return feedback

    def _get_issue_category(self, issue_key):
        """Map issue key to issue category"""
        issue_mapping = {
            'water': 'Water Supply',
            'jobs': 'Employment',
            'agriculture': 'Agriculture',
            'neet': 'Education',
            'healthcare': 'Healthcare',
            'education': 'Education',
            'fishermen': 'Fishermen Rights',
            'cauvery': 'Agriculture',
            'other': 'Infrastructure',
        }
        category_name = issue_mapping.get(issue_key, 'Others')

        # Try to find exact match first
        if category_name in self.issue_categories:
            return self.issue_categories[category_name]

        # Try partial match
        for cat_name, cat_obj in self.issue_categories.items():
            if category_name.lower() in cat_name.lower():
                return cat_obj

        # Return any category if nothing matches
        return list(self.issue_categories.values())[0] if self.issue_categories else None

    def _get_voter_segment(self, issue_key):
        """Map issue to relevant voter segment"""
        segment_mapping = {
            'fishermen': 'Fishermen',
            'agriculture': 'Farmers',
            'cauvery': 'Farmers',
            'jobs': 'Youth',
            'neet': 'Students',
            'education': 'Students',
        }

        segment_name = segment_mapping.get(issue_key)
        if segment_name and self.voter_segments:
            for segment in self.voter_segments:
                if segment_name.lower() in segment.name.lower():
                    return segment

        return random.choice(self.voter_segments) if self.voter_segments else None

    # Message generation by issue type
    def _generate_message_by_issue(self, issue_key, ward, is_urban, gender):
        """Generate realistic citizen message based on issue"""

        message_generators = {
            'water': self._generate_water_message,
            'jobs': self._generate_jobs_message,
            'agriculture': self._generate_agriculture_message,
            'neet': self._generate_neet_message,
            'healthcare': self._generate_healthcare_message,
            'education': self._generate_education_message,
            'fishermen': self._generate_fishermen_message,
            'cauvery': self._generate_cauvery_message,
            'other': self._generate_other_message,
        }

        generator = message_generators.get(issue_key, self._generate_other_message)
        return generator(ward, is_urban, gender)

    def _generate_water_message(self, ward, is_urban, gender):
        templates = [
            (
                f"No water supply for {random.randint(3, 7)} days in our {ward} area. Tanker water very expensive at Rs.{random.randint(800, 1500)} per load. Children missing school to fetch water from far away. How will we survive summer?",
                "Immediate restoration of regular water supply. Permanent solution for water crisis."
            ),
            (
                f"Groundwater completely dried up in {ward}. Even bore wells not working after {random.randint(300, 600)} feet. Spending Rs.{random.randint(3000, 8000)} monthly on tanker water. Cannot afford this.",
                "Government should provide free water supply or subsidize tanker water costs."
            ),
            (
                f"Metro water not coming for weeks. {ward} has {random.randint(500, 2000)} families suffering. Women waiting in long queues for public tap water. Please help us.",
                "Regular water supply schedule and new water connections for all households."
            ),
            (
                f"Our {ward} locality completely neglected. Rich areas getting daily water, we get once in {random.randint(7, 15)} days. This is injustice. Poor people also need water.",
                "Equal water distribution across all areas regardless of economic status."
            ),
        ]
        return random.choice(templates)

    def _generate_jobs_message(self, ward, is_urban, gender):
        pronoun = "my son" if gender == 'female' else "I"
        degree = random.choice(['Engineering', 'MBA', 'B.Com', 'B.Sc', 'M.Sc'])
        templates = [
            (
                f"{pronoun} completed {degree} {random.randint(1, 5)} years ago, still searching for proper job. Only call center offers with Rs.{random.randint(12000, 18000)} salary. Need good manufacturing jobs in Tamil Nadu.",
                "Government should create quality jobs with decent salary and job security."
            ),
            (
                f"Factory in {ward} closed {random.randint(3, 12)} months ago. {random.randint(300, 800)} workers became jobless. No government help, no compensation, no answers. How will we feed our families?",
                "Immediate relief for unemployed workers and help in finding new employment."
            ),
            (
                f"Youth unemployment crisis very serious. Every house in {ward} has unemployed graduate. Educated youth driving autos and doing manual labor. What is future for our children?",
                "Large scale job creation programs and support for local industries and startups."
            ),
            (
                f"Private companies exploiting workers. Working {random.randint(10, 14)} hours daily for Rs.{random.randint(8000, 15000)} monthly. No ESI, no PF, no job security. Where to complain?",
                "Strict labor law enforcement and minimum wage implementation across all sectors."
            ),
        ]
        return random.choice(templates)

    def _generate_agriculture_message(self, ward, is_urban, gender):
        templates = [
            (
                f"Cauvery water not reaching our {ward} fields for {random.randint(20, 60)} days. Paddy fields completely drying up. Entire season will be lost. We will be in more debt.",
                "Ensure fair water distribution to all farmers and crop loss compensation."
            ),
            (
                f"Farming not profitable anymore. Input costs doubled - fertilizer Rs.{random.randint(1500, 2500)}, seeds Rs.{random.randint(800, 1500)}, labor Rs.{random.randint(500, 800)} per day. But paddy price same for {random.randint(5, 10)} years. How to survive?",
                "Increase MSP to cover production costs and provide subsidized inputs."
            ),
            (
                f"Our {random.randint(2, 10)} acres land lying unused. No water, no profit, only debt. Young people leaving villages. If farmers stop farming, where will food come from?",
                "Complete farm loan waiver and guaranteed minimum income for farmers."
            ),
            (
                f"Monsoon failed, bore wells dry, Cauvery water not coming. Crops dying. Already {random.randint(50000, 500000)} rupees in debt. Moneylenders threatening us. Desperate situation.",
                "Emergency drought relief and protection from moneylenders exploitation."
            ),
        ]
        return random.choice(templates)

    def _generate_neet_message(self, ward, is_urban, gender):
        relation = random.choice(['daughter', 'son', 'child'])
        templates = [
            (
                f"My {relation} scored {random.randint(92, 98)}% in 12th standard but couldn't clear NEET. Dreams of becoming doctor completely shattered. Please remove NEET for Tamil Nadu students.",
                "Abolish NEET and restore state board based medical admissions in Tamil Nadu."
            ),
            (
                f"Rural students cannot afford NEET coaching costing Rs.{random.randint(80000, 200000)} per year. NEET is only for rich urban families. This is injustice to poor and rural students.",
                "Either remove NEET or provide free coaching for economically backward students."
            ),
            (
                f"My {relation} attempted NEET {random.randint(2, 3)} times, failed each time despite scoring 95%+ in state board. Lost {random.randint(2, 3)} years of life. NEET destroying Tamil students future.",
                "Bring back state quota system where marks in 12th standard matter for admissions."
            ),
            (
                f"Poor students with talent being denied medical education because of NEET. Rich students with average marks getting seats through coaching. This is not meritocracy, this is injustice.",
                "Supreme Court should understand ground reality and allow states to decide admission policy."
            ),
        ]
        return random.choice(templates)

    def _generate_healthcare_message(self, ward, is_urban, gender):
        templates = [
            (
                f"Primary Health Center in {ward} has no doctor for {random.randint(15, 60)} days. Pregnant women forced to travel {random.randint(25, 50)}km for basic checkups. Medical emergencies turned away.",
                "Immediately appoint doctors and ensure 24x7 PHC services in all areas."
            ),
            (
                f"Government hospital has {random.randint(1, 3)} doctors for {random.randint(500, 2000)} patients daily. Waiting time {random.randint(3, 8)} hours. Medicines not available. People dying without treatment.",
                "Increase doctors in government hospitals and ensure free medicines availability."
            ),
            (
                f"Cannot afford private hospital charges. Simple treatment costs Rs.{random.randint(20000, 100000)}. Poor people forced to borrow money even for basic medical care. Where is government healthcare?",
                "Strengthen government hospitals with proper facilities and make healthcare truly free."
            ),
            (
                f"My family member needs urgent surgery. Government hospital has {random.randint(3, 6)} months waiting. Private hospital demanding Rs.{random.randint(200000, 500000)} upfront. What should poor people do?",
                "Expand government hospital capacity and provide health insurance for all."
            ),
        ]
        return random.choice(templates)

    def _generate_education_message(self, ward, is_urban, gender):
        templates = [
            (
                f"Government school in {ward} has no proper building. {random.randint(150, 400)} students studying under trees. No toilets, no drinking water. How can children study in such conditions?",
                "Build proper school buildings with basic facilities in all government schools."
            ),
            (
                f"Our school has only {random.randint(2, 5)} teachers for {random.randint(8, 12)} classes. One teacher teaching multiple subjects and classes. Children not learning properly.",
                "Appoint adequate teachers in all government schools as per student strength."
            ),
            (
                f"Private school fees increased to Rs.{random.randint(30000, 80000)} per year. Uniforms, books, transport extra Rs.{random.randint(15000, 30000)}. Cannot afford quality education for children.",
                "Control private school fee hikes and improve government schools so people don't need private schools."
            ),
            (
                f"Mid-day meal quality very poor. Sometimes spoiled food given to children. Several students fell sick. Government should ensure food quality and quantity.",
                "Proper monitoring of mid-day meal scheme and strict action against quality issues."
            ),
        ]
        return random.choice(templates)

    def _generate_fishermen_message(self, ward, is_urban, gender):
        relation = random.choice(['husband', 'brother', 'father', 'son'])
        templates = [
            (
                f"My {relation} arrested by Sri Lankan Navy {random.randint(2, 5)}th time this year. Family starving. We just want to fish in our traditional waters peacefully.",
                "Protect Indian fishermen from Sri Lankan Navy and secure our fishing rights."
            ),
            (
                f"Boat damaged by SL Navy, equipment worth Rs.{random.randint(200000, 800000)} lost. No compensation from government. How will we feed our children? Fishermen need protection.",
                "Immediate compensation for damaged boats and strong diplomatic action against SL Navy."
            ),
            (
                f"Cannot go fishing due to fear of arrest. {random.randint(50, 200)} fishing families in {ward} without income for {random.randint(20, 60)} days. Government must take action.",
                "Navy escort for fishing boats and permanent solution to fishing boundary dispute."
            ),
            (
                f"{random.randint(10, 30)} fishermen from our area in Sri Lankan jails. Government not doing enough to bring them back. Families suffering without earning members.",
                "Immediate diplomatic efforts to release all arrested fishermen and prevent future arrests."
            ),
        ]
        return random.choice(templates)

    def _generate_cauvery_message(self, ward, is_urban, gender):
        templates = [
            (
                f"Karnataka not releasing Cauvery water as per Supreme Court order. Delta farmers suffering badly. Our {random.randint(3, 20)} acres completely dry. Crops failing.",
                "Tamil Nadu government should take strong action to get our Cauvery water share."
            ),
            (
                f"Cauvery water dispute affecting {random.randint(10000, 50000)} farmers in our region. Kuruvai season completely lost. Samba season also in danger. This is our survival issue.",
                "Supreme Court should ensure strict compliance of water sharing formula."
            ),
            (
                f"Every year same problem. Karnataka releases water late, Tamil Nadu farmers suffer. We need permanent solution, not temporary relief. Our agriculture depends on Cauvery.",
                "Establish Cauvery Management Board with full powers to ensure water justice."
            ),
        ]
        return random.choice(templates)

    def _generate_other_message(self, ward, is_urban, gender):
        templates = [
            (
                f"Roads in {ward} completely damaged. Potholes everywhere. Two-wheeler accidents happening daily. Monsoon season will be nightmare. Please repair roads urgently.",
                "Immediate road repairs with proper quality materials and regular maintenance."
            ),
            (
                f"Electricity outage {random.randint(4, 10)} hours daily in {ward}. No notice, no schedule. Students cannot study, businesses suffering losses. This is unbearable.",
                "Ensure 24x7 electricity supply or at least provide fixed power cut schedule."
            ),
            (
                f"Garbage not collected for {random.randint(7, 20)} days in {ward}. Waste piling up on streets. Bad smell, mosquitoes, health hazard. Where is corporation?",
                "Daily garbage collection and proper waste management system for all areas."
            ),
        ]
        return random.choice(templates)

    def _generate_ai_analysis(self, issue_key, message_text, status):
        """Generate realistic AI analysis fields"""

        # Sentiment score based on issue (crisis issues = lower scores)
        crisis_issues = ['water', 'jobs', 'agriculture', 'fishermen', 'cauvery']
        if issue_key in crisis_issues:
            sentiment_score = Decimal(str(round(random.uniform(0.10, 0.35), 2)))
            polarity = 'negative'
        elif issue_key == 'neet':
            sentiment_score = Decimal(str(round(random.uniform(0.15, 0.40), 2)))
            polarity = 'negative'
        else:
            sentiment_score = Decimal(str(round(random.uniform(0.20, 0.50), 2)))
            polarity = random.choice(['negative', 'neutral'])

        # Urgency distribution
        urgency_weights = {'low': 0.05, 'medium': 0.15, 'high': 0.60, 'urgent': 0.20}
        urgency = random.choices(
            list(urgency_weights.keys()),
            weights=list(urgency_weights.values())
        )[0]

        # AI confidence
        confidence = Decimal(str(round(random.uniform(0.70, 0.95), 2)))

        # Extracted issues
        extracted_issues = self._extract_issues(issue_key, message_text)

        # AI summary
        summary = self._generate_summary(issue_key, message_text)

        analysis = {
            'ai_sentiment_score': sentiment_score,
            'ai_sentiment_polarity': polarity,
            'ai_urgency': urgency,
            'ai_confidence': confidence,
            'ai_extracted_issues': extracted_issues,
            'ai_summary': summary,
            'ai_analysis_metadata': {
                'model': 'sentiment-analyzer-v2.1',
                'processing_time_ms': random.randint(150, 800),
                'language_detected': 'en',
                'keywords': self._extract_keywords(message_text),
            }
        }

        return analysis

    def _extract_issues(self, issue_key, message_text):
        """Extract issues from message"""
        issue_keywords = {
            'water': ['Water shortage', 'Tanker water costs', 'Irregular supply'],
            'jobs': ['Unemployment', 'Low wages', 'Job security', 'Factory closure'],
            'agriculture': ['Irrigation failure', 'Input costs', 'MSP', 'Farm debt'],
            'neet': ['NEET exam', 'Medical admissions', 'Education accessibility'],
            'healthcare': ['Doctor shortage', 'Hospital infrastructure', 'Medicine availability'],
            'education': ['School infrastructure', 'Teacher shortage', 'Education costs'],
            'fishermen': ['SL Navy arrests', 'Fishing rights', 'Livelihood loss'],
            'cauvery': ['Cauvery water', 'Interstate dispute', 'Agriculture water'],
            'other': ['Infrastructure', 'Public services', 'Civic issues'],
        }

        return issue_keywords.get(issue_key, ['General issues'])

    def _generate_summary(self, issue_key, message_text):
        """Generate AI summary"""
        summaries = {
            'water': f"Citizen reporting severe water crisis affecting daily life. Issue requires immediate administrative attention.",
            'jobs': f"Unemployment and job security concerns raised. Economic distress evident in feedback.",
            'agriculture': f"Farmer facing agricultural crisis due to water shortage and economic pressures. Urgent intervention needed.",
            'neet': f"Student/parent expressing strong opposition to NEET exam impact on medical education accessibility.",
            'healthcare': f"Critical healthcare access issues reported. Public health infrastructure concerns raised.",
            'education': f"Educational infrastructure and quality concerns affecting children's learning outcomes.",
            'fishermen': f"Fishermen community facing livelihood threats and security concerns. Government intervention required.",
            'cauvery': f"Cauvery water dispute impact on agriculture reported. Interstate water sharing concerns.",
            'other': f"Civic infrastructure and public service delivery issues affecting quality of life.",
        }

        return summaries.get(issue_key, "Citizen feedback requiring review and appropriate action.")

    def _extract_keywords(self, message_text):
        """Extract keywords from message"""
        words = message_text.lower().split()
        keywords = []

        keyword_list = [
            'water', 'job', 'employment', 'farmer', 'agriculture', 'neet', 'medical',
            'education', 'hospital', 'doctor', 'fishermen', 'cauvery', 'crisis',
            'urgent', 'help', 'government', 'poor', 'family', 'children'
        ]

        for word in words:
            for keyword in keyword_list:
                if keyword in word:
                    keywords.append(keyword)
                    break

        return list(set(keywords))[:8]  # Unique keywords, max 8

    def _print_statistics(self):
        """Print comprehensive statistics"""
        self.stdout.write(self.style.SUCCESS('\n=== DIRECT FEEDBACK GENERATION STATISTICS ==='))

        # Count by issue (approximate from categories)
        self.stdout.write('\nFeedback by Status:')
        for status, _ in DirectFeedback.STATUS_CHOICES:
            count = DirectFeedback.objects.filter(status=status).count()
            percentage = (count / self.feedback_count * 100) if self.feedback_count > 0 else 0
            self.stdout.write(f'{status}: {count} ({percentage:.1f}%)')

        # Sentiment distribution
        self.stdout.write('\nSentiment Polarity:')
        for polarity in ['positive', 'negative', 'neutral']:
            count = DirectFeedback.objects.filter(ai_sentiment_polarity=polarity).count()
            percentage = (count / self.feedback_count * 100) if self.feedback_count > 0 else 0
            self.stdout.write(f'{polarity}: {count} ({percentage:.1f}%)')

        # Urgency distribution
        self.stdout.write('\nUrgency Levels:')
        for urgency, _ in DirectFeedback.URGENCY_CHOICES:
            count = DirectFeedback.objects.filter(ai_urgency=urgency).count()
            percentage = (count / self.feedback_count * 100) if self.feedback_count > 0 else 0
            self.stdout.write(f'{urgency}: {count} ({percentage:.1f}%)')

        # Date range
        oldest = DirectFeedback.objects.order_by('submitted_at').first()
        newest = DirectFeedback.objects.order_by('-submitted_at').first()
        if oldest and newest:
            self.stdout.write(f'\nDate Range: {oldest.submitted_at.date()} to {newest.submitted_at.date()}')

        # Top districts
        from django.db.models import Count
        top_districts = DirectFeedback.objects.values('district__name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        self.stdout.write('\nTop 5 Districts:')
        for dist in top_districts:
            if dist['district__name']:
                self.stdout.write(f"  {dist['district__name']}: {dist['count']} submissions")

        # Age demographics
        avg_age = DirectFeedback.objects.filter(citizen_age__isnull=False).aggregate(
            models.Avg('citizen_age')
        )
        if avg_age['citizen_age__avg']:
            self.stdout.write(f'\nAverage Citizen Age: {avg_age["citizen_age__avg"]:.1f} years')

        self.stdout.write(self.style.SUCCESS(f'\nTotal Direct Feedback: {self.feedback_count}'))


# Import for aggregate functions
from django.db import models
