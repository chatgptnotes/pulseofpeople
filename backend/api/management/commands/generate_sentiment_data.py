"""
Django management command to generate 50,000 realistic sentiment data records
based on REAL Tamil Nadu issues from November 2024.

Usage: python manage.py generate_sentiment_data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import random
import numpy as np
from tqdm import tqdm

from api.models import (
    SentimentData, IssueCategory, District, Constituency,
    VoterSegment, State
)


class Command(BaseCommand):
    help = 'Generates 50,000 realistic sentiment data records based on real TN issues (Nov 2024)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50000,
            help='Number of records to generate (default: 50000)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for bulk create (default: 1000)',
        )

    def handle(self, *args, **options):
        total_records = options['count']
        batch_size = options['batch_size']

        self.stdout.write(self.style.SUCCESS(
            f'\n{"="*80}\n'
            f'SENTIMENT DATA GENERATOR - Tamil Nadu Real Crisis Scenarios (Nov 2024)\n'
            f'{"="*80}\n'
        ))

        # Verify required data exists
        if not self.verify_data():
            return

        # Initialize data structures
        self.load_data()

        # Generate sentiment data
        self.stdout.write('\nGenerating sentiment data records...\n')
        stats = self.generate_sentiment_data(total_records, batch_size)

        # Display statistics
        self.display_statistics(stats)

    def verify_data(self):
        """Verify that required data exists in the database"""
        self.stdout.write('Verifying database...')

        state_count = State.objects.filter(code='TN').count()
        district_count = District.objects.filter(state__code='TN').count()
        constituency_count = Constituency.objects.filter(state__code='TN').count()
        issue_count = IssueCategory.objects.count()
        segment_count = VoterSegment.objects.count()

        self.stdout.write(f'  States (TN): {state_count}')
        self.stdout.write(f'  Districts: {district_count}')
        self.stdout.write(f'  Constituencies: {constituency_count}')
        self.stdout.write(f'  Issue Categories: {issue_count}')
        self.stdout.write(f'  Voter Segments: {segment_count}')

        if state_count == 0:
            self.stdout.write(self.style.ERROR('\nERROR: Tamil Nadu state not found!'))
            self.stdout.write('Please run: python manage.py seed_political_data')
            return False

        if district_count == 0:
            self.stdout.write(self.style.ERROR('\nERROR: No districts found!'))
            self.stdout.write('Please run: python manage.py seed_political_data')
            return False

        if issue_count == 0:
            self.stdout.write(self.style.ERROR('\nERROR: No issue categories found!'))
            self.stdout.write('Please run: python manage.py seed_political_data')
            return False

        self.stdout.write(self.style.SUCCESS('  Database verified!\n'))
        return True

    def load_data(self):
        """Load all required data from database"""
        self.stdout.write('Loading data structures...')

        self.tn_state = State.objects.get(code='TN')
        self.all_districts = list(District.objects.filter(state=self.tn_state))
        self.all_constituencies = list(Constituency.objects.filter(state=self.tn_state))
        self.all_issues = list(IssueCategory.objects.all())
        self.all_segments = list(VoterSegment.objects.all())

        # Create issue name to object mapping
        self.issue_map = {issue.name: issue for issue in self.all_issues}

        # Create district name to object mapping
        self.district_map = {district.name: district for district in self.all_districts}

        # Define real crisis scenarios (Nov 2024)
        self.define_crisis_scenarios()

        self.stdout.write(self.style.SUCCESS('  Data loaded!\n'))

    def define_crisis_scenarios(self):
        """Define real Tamil Nadu crisis scenarios from November 2024"""

        # Water Crisis Districts (26 districts affected)
        water_crisis_districts = [
            'Coimbatore', 'Chennai', 'Tiruchirappalli', 'Salem', 'Erode',
            'Madurai', 'Tiruppur', 'Vellore', 'Dindigul', 'Karur'
        ]

        # Cauvery Dispute Districts (Delta region)
        cauvery_districts = [
            'Thanjavur', 'Tiruvarur', 'Nagapattinam', 'Cuddalore',
            'Mayiladuthurai', 'Ariyalur'
        ]

        # Cyclone Fengal affected (Nov 2024)
        cyclone_districts = [
            'Cuddalore', 'Viluppuram', 'Tiruvannamalai', 'Chengalpattu',
            'Kallakurichi', 'Ranipet'
        ]

        # Fishermen issues (Coastal districts)
        fishermen_districts = [
            'Ramanathapuram', 'Nagapattinam', 'Pudukkottai', 'Thanjavur',
            'Thoothukudi', 'Kanyakumari', 'Chennai'
        ]

        # Urban centers (higher volume)
        urban_districts = [
            'Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli',
            'Salem', 'Tiruppur', 'Erode'
        ]

        # Map issues to affected districts
        self.issue_district_map = {
            'Water Supply': water_crisis_districts,
            'Cauvery Dispute': cauvery_districts,
            'Cyclone Relief': cyclone_districts,
            'Fishermen Rights': fishermen_districts,
            'Jobs/Employment': urban_districts,
            'Agriculture': cauvery_districts + ['Salem', 'Erode', 'Namakkal'],
            'NEET Opposition': urban_districts,
            'Healthcare': urban_districts,
            'Education': urban_districts,
        }

        # Issue distribution (percentages must sum to 100)
        self.issue_distribution = {
            'Water Supply': 20.0,
            'Jobs/Employment': 18.0,
            'Agriculture': 12.0,
            'NEET Opposition': 10.0,
            'Cauvery Dispute': 8.0,
            'Healthcare': 8.0,
            'Education': 7.0,
            'Fishermen Rights': 5.0,
            'Infrastructure': 5.0,
            'Cyclone Relief': 4.0,
            'Other': 3.0,
        }

        # Source distribution
        self.source_distribution = {
            'direct_feedback': 40.0,
            'social_media': 35.0,
            'field_report': 20.0,
            'survey': 5.0,
        }

        # Sentiment patterns by issue
        self.issue_sentiment_patterns = {
            'Water Supply': {'positive': 15, 'neutral': 25, 'negative': 60},
            'Cauvery Dispute': {'positive': 10, 'neutral': 20, 'negative': 70},
            'Cyclone Relief': {'positive': 20, 'neutral': 30, 'negative': 50},
            'Fishermen Rights': {'positive': 15, 'neutral': 25, 'negative': 60},
            'NEET Opposition': {'positive': 45, 'neutral': 30, 'negative': 25},
            'Jobs/Employment': {'positive': 25, 'neutral': 30, 'negative': 45},
            'Agriculture': {'positive': 20, 'neutral': 25, 'negative': 55},
            'Healthcare': {'positive': 30, 'neutral': 35, 'negative': 35},
            'Education': {'positive': 35, 'neutral': 35, 'negative': 30},
            'Infrastructure': {'positive': 30, 'neutral': 40, 'negative': 30},
            'Other': {'positive': 40, 'neutral': 35, 'negative': 25},
        }

        # District urbanization levels (affects volume)
        self.district_weights = {}
        for district in self.all_districts:
            if district.name in urban_districts:
                self.district_weights[district.name] = 3.0  # Urban: 3x weight
            elif district.name in (water_crisis_districts + cauvery_districts):
                self.district_weights[district.name] = 2.0  # Semi-urban/affected: 2x
            else:
                self.district_weights[district.name] = 1.0  # Rural: 1x

    def get_random_timestamp(self, start_date, end_date):
        """Generate random timestamp with realistic distribution"""
        # More recent = more volume (exponential distribution)
        days_range = (end_date - start_date).days

        # Exponential distribution favoring recent dates
        random_days = int(np.random.exponential(scale=days_range / 3))
        random_days = min(random_days, days_range)  # Cap at max range

        date = end_date - timedelta(days=random_days)

        # Peak hours: 7-9am, 12-2pm, 6-9pm IST
        hour_weights = [1, 1, 1, 1, 1, 1, 3, 3, 2, 1, 1, 3, 3, 1, 1, 1, 1, 3, 3, 3, 2, 1, 1, 1]
        hour = random.choices(range(24), weights=hour_weights)[0]

        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        timestamp = datetime.combine(date, datetime.min.time()) + timedelta(
            hours=hour, minutes=minute, seconds=second
        )

        # Weekday volume 30% higher than weekend
        if timestamp.weekday() >= 5:  # Weekend
            if random.random() > 0.7:  # 30% chance to skip
                return self.get_random_timestamp(start_date, end_date)

        return timezone.make_aware(timestamp, timezone.get_current_timezone())

    def select_issue_by_distribution(self):
        """Select issue based on defined distribution"""
        issue_names = list(self.issue_distribution.keys())
        weights = list(self.issue_distribution.values())
        selected_issue_name = random.choices(issue_names, weights=weights)[0]

        # Map to actual IssueCategory or create generic mapping
        issue_mapping = {
            'Water Supply': 'Healthcare Access',  # Use existing category
            'Jobs/Employment': 'Youth Employment & Education',
            'Agriculture': 'Farmers Welfare & Agriculture',
            'NEET Opposition': 'Youth Employment & Education',
            'Cauvery Dispute': 'Farmers Welfare & Agriculture',
            'Healthcare': 'Healthcare Access',
            'Education': 'Youth Employment & Education',
            'Fishermen Rights': "Fishermen's Rights & Livelihood",
            'Infrastructure': 'Environmental Protection',
            'Cyclone Relief': 'Farmers Welfare & Agriculture',
            'Other': 'Social Justice & Caste Issues',
        }

        mapped_issue_name = issue_mapping.get(selected_issue_name, selected_issue_name)

        # Get the issue object
        if mapped_issue_name in self.issue_map:
            return self.issue_map[mapped_issue_name], selected_issue_name
        else:
            # Fallback to random issue if not found
            return random.choice(self.all_issues), selected_issue_name

    def select_district_for_issue(self, issue_name):
        """Select district based on issue relevance"""
        if issue_name in self.issue_district_map:
            relevant_districts = self.issue_district_map[issue_name]
            available_districts = [d for d in self.all_districts if d.name in relevant_districts]

            if available_districts:
                # Weight by district urbanization
                weights = [self.district_weights.get(d.name, 1.0) for d in available_districts]
                return random.choices(available_districts, weights=weights)[0]

        # Fallback: random district weighted by urbanization
        weights = [self.district_weights.get(d.name, 1.0) for d in self.all_districts]
        return random.choices(self.all_districts, weights=weights)[0]

    def select_constituency(self, district):
        """Select constituency within district"""
        district_constituencies = [c for c in self.all_constituencies if c.district_id == district.id]
        if district_constituencies:
            return random.choice(district_constituencies)
        # Fallback to any constituency
        return random.choice(self.all_constituencies) if self.all_constituencies else None

    def generate_sentiment_score(self, issue_name):
        """Generate sentiment score based on issue patterns"""
        pattern = self.issue_sentiment_patterns.get(
            issue_name,
            {'positive': 40, 'neutral': 35, 'negative': 25}
        )

        # Select polarity based on pattern
        polarity = random.choices(
            ['positive', 'neutral', 'negative'],
            weights=[pattern['positive'], pattern['neutral'], pattern['negative']]
        )[0]

        # Generate sentiment score based on polarity
        if polarity == 'positive':
            # Positive: 0.6 - 1.0
            score = np.random.beta(5, 2) * 0.4 + 0.6
        elif polarity == 'neutral':
            # Neutral: 0.4 - 0.6
            score = np.random.beta(2, 2) * 0.2 + 0.4
        else:
            # Negative: 0.0 - 0.4
            score = np.random.beta(2, 5) * 0.4

        return float(min(max(score, 0.0), 1.0)), polarity

    def generate_confidence_score(self):
        """Generate realistic confidence score"""
        # Normal distribution: mean=0.75, std=0.15
        confidence = np.random.normal(0.75, 0.15)
        return float(min(max(confidence, 0.0), 1.0))

    def select_source(self):
        """Select source based on distribution"""
        sources = list(self.source_distribution.keys())
        weights = list(self.source_distribution.values())
        return random.choices(sources, weights=weights)[0]

    def select_ward(self):
        """Generate realistic ward identifier"""
        ward_types = ['Ward', 'Division', 'Zone']
        ward_type = random.choice(ward_types)
        ward_number = random.randint(1, 100)
        return f'{ward_type} {ward_number}'

    def generate_sentiment_data(self, total_records, batch_size):
        """Generate sentiment data records in batches"""
        # Date range: Sept 1 - Nov 30, 2024 (90 days)
        end_date = datetime(2024, 11, 30)
        start_date = datetime(2024, 9, 1)

        records = []
        stats = {
            'total': 0,
            'by_issue': {},
            'by_district': {},
            'by_polarity': {'positive': 0, 'neutral': 0, 'negative': 0},
            'by_source': {},
            'date_range': {'start': None, 'end': None},
        }

        # Use tqdm for progress bar
        with tqdm(total=total_records, desc='Generating records', unit='record') as pbar:
            for i in range(total_records):
                # Select issue
                issue, issue_name = self.select_issue_by_distribution()

                # Select district based on issue
                district = self.select_district_for_issue(issue_name)

                # Select constituency
                constituency = self.select_constituency(district)

                # Generate sentiment score
                sentiment_score, polarity = self.generate_sentiment_score(issue_name)

                # Generate confidence
                confidence = self.generate_confidence_score()

                # Select source
                source = self.select_source()

                # Generate timestamp
                timestamp = self.get_random_timestamp(start_date, end_date)

                # Select ward
                ward = self.select_ward()

                # Select voter segment (optional, 50% chance)
                voter_segment = random.choice(self.all_segments) if random.random() > 0.5 and self.all_segments else None

                # Create sentiment data record
                record = SentimentData(
                    source_type=source,
                    source_id=uuid.uuid4(),
                    issue=issue,
                    sentiment_score=Decimal(str(round(sentiment_score, 2))),
                    polarity=polarity,
                    confidence=Decimal(str(round(confidence, 2))),
                    state=self.tn_state,
                    district=district,
                    constituency=constituency,
                    ward=ward,
                    voter_segment=voter_segment,
                    timestamp=timestamp,
                )

                records.append(record)

                # Update statistics
                stats['by_issue'][issue_name] = stats['by_issue'].get(issue_name, 0) + 1
                stats['by_district'][district.name] = stats['by_district'].get(district.name, 0) + 1
                stats['by_polarity'][polarity] += 1
                stats['by_source'][source] = stats['by_source'].get(source, 0) + 1

                if stats['date_range']['start'] is None or timestamp < stats['date_range']['start']:
                    stats['date_range']['start'] = timestamp
                if stats['date_range']['end'] is None or timestamp > stats['date_range']['end']:
                    stats['date_range']['end'] = timestamp

                # Bulk create in batches
                if len(records) >= batch_size:
                    SentimentData.objects.bulk_create(records, batch_size=batch_size)
                    stats['total'] += len(records)
                    pbar.update(len(records))
                    records = []

            # Create remaining records
            if records:
                SentimentData.objects.bulk_create(records, batch_size=batch_size)
                stats['total'] += len(records)
                pbar.update(len(records))

        return stats

    def display_statistics(self, stats):
        """Display generation statistics"""
        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(self.style.SUCCESS(f'GENERATION COMPLETE'))
        self.stdout.write(f'{"="*80}\n')

        self.stdout.write(f'Total Records Created: {stats["total"]:,}\n')

        # Date range
        if stats['date_range']['start'] and stats['date_range']['end']:
            self.stdout.write(f'Date Range:')
            self.stdout.write(f'  Start: {stats["date_range"]["start"].strftime("%Y-%m-%d %H:%M:%S")}')
            self.stdout.write(f'  End:   {stats["date_range"]["end"].strftime("%Y-%m-%d %H:%M:%S")}\n')

        # Issue breakdown
        self.stdout.write('Breakdown by Issue:')
        sorted_issues = sorted(stats['by_issue'].items(), key=lambda x: x[1], reverse=True)
        for issue, count in sorted_issues:
            percentage = (count / stats['total']) * 100
            self.stdout.write(f'  {issue:.<40} {count:>6,} ({percentage:>5.1f}%)')

        # Polarity breakdown
        self.stdout.write('\nBreakdown by Polarity:')
        for polarity, count in sorted(stats['by_polarity'].items()):
            percentage = (count / stats['total']) * 100
            self.stdout.write(f'  {polarity.capitalize():.<40} {count:>6,} ({percentage:>5.1f}%)')

        # Source breakdown
        self.stdout.write('\nBreakdown by Source:')
        for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total']) * 100
            self.stdout.write(f'  {source.replace("_", " ").title():.<40} {count:>6,} ({percentage:>5.1f}%)')

        # Top 10 districts
        self.stdout.write('\nTop 10 Districts by Volume:')
        sorted_districts = sorted(stats['by_district'].items(), key=lambda x: x[1], reverse=True)[:10]
        for district, count in sorted_districts:
            percentage = (count / stats['total']) * 100
            self.stdout.write(f'  {district:.<40} {count:>6,} ({percentage:>5.1f}%)')

        # Geographic coverage
        total_districts = len(stats['by_district'])
        self.stdout.write(f'\nGeographic Coverage:')
        self.stdout.write(f'  Districts covered: {total_districts} / {len(self.all_districts)}')

        self.stdout.write(f'\n{"="*80}')
        self.stdout.write(self.style.SUCCESS('Sentiment data generation completed successfully!'))
        self.stdout.write(f'{"="*80}\n')
