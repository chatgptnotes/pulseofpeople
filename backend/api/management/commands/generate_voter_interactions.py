"""
Django management command to generate comprehensive voter interaction records

Usage:
    python manage.py generate_voter_interactions

This command generates 30,000 voter interaction records with:
- Various interaction types (phone calls, door visits, events, SMS, WhatsApp, email)
- Realistic interaction patterns (focus on high/medium influence voters)
- Sentiment distribution showing TVK improvement
- Issues discussed based on Tamil Nadu priorities
- Contacted by booth agents and volunteers
- Duration, follow-up requirements, and detailed notes
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from api.models import VoterInteraction, Voter
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker with Indian locale
fake = Faker(['ta_IN', 'en_IN'])


class Command(BaseCommand):
    help = 'Generates 30,000 voter interaction records with realistic patterns'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30000,
            help='Number of interactions to generate (default: 30,000)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Batch size for bulk creation (default: 500)'
        )

    def handle(self, *args, **options):
        total_count = options['count']
        batch_size = options['batch_size']

        self.stdout.write(self.style.WARNING(f'Starting voter interaction generation: {total_count:,} interactions'))
        self.stdout.write('=' * 80)

        # Interaction type distribution
        INTERACTION_TYPES = {
            'phone_call': 0.40,     # 40% - 12,000
            'door_visit': 0.30,     # 30% - 9,000
            'event_meeting': 0.15,  # 15% - 4,500
            'sms': 0.08,            # 8% - 2,400
            'whatsapp': 0.05,       # 5% - 1,500
            'email': 0.02,          # 2% - 600
        }

        # Sentiment distribution (showing TVK improvement)
        SENTIMENT_DISTRIBUTION = {
            'positive': 0.55,   # 55% - improving TVK sentiment
            'neutral': 0.30,    # 30%
            'negative': 0.15,   # 15%
        }

        # Issues discussed (Tamil Nadu priorities)
        ISSUES_DISTRIBUTION = {
            'Jobs': 0.25,
            'Water': 0.20,
            'NEET': 0.12,
            'Healthcare': 0.10,
            'Education': 0.08,
            'Agriculture': 0.07,
            'Transportation': 0.05,
            'Electricity': 0.04,
            'Housing': 0.03,
            'Sanitation': 0.03,
            'Law and Order': 0.03,
        }

        # Duration ranges by interaction type (in minutes)
        DURATION_RANGES = {
            'phone_call': (2, 15),
            'door_visit': (5, 30),
            'event_meeting': (15, 60),
            'sms': (0, 0),
            'whatsapp': (0, 0),
            'email': (0, 0),
        }

        # Realistic interaction notes templates
        NOTES_TEMPLATES = {
            'positive': [
                "Discussed {issue} issues in {ward}. Voter {sentiment} about TVK vision. Interested in {interest_area}.",
                "Very enthusiastic conversation about TVK's {policy} policy. {voter_name} appreciates leadership's transparency.",
                "Strong supporter. Discussed {issue} concerns. Promised to help with grassroots mobilization in {area}.",
                "First-time engagement. Youth voter excited about {topic}. Willing to volunteer for upcoming events.",
                "Farmer concerned about {issue}. Explained TVK's {solution}. Positive response, requested follow-up meeting.",
                "Opinion leader in community. Discussed multiple issues: {issues}. Committed to organizing local meeting.",
                "Senior citizen, traditional voter. Impressed by party's {value} values. Requested more information materials.",
                "Business owner worried about {issue}. Detailed discussion about economic policies. Very supportive feedback.",
            ],
            'neutral': [
                "Listened to concerns about {issue}. Voter undecided but open to further dialogue. Scheduled follow-up.",
                "Neutral conversation. Discussed {issue} and {issue2}. Voter wants to see concrete action plans.",
                "First contact. Provided party manifesto. Voter non-committal but took literature for review.",
                "Brief discussion about {issue}. Voter waiting to evaluate all parties before deciding.",
                "Attended community meeting. Asked several questions about {topic}. Neither positive nor negative.",
                "Concerned about {issue}. Explained party stance. Voter wants time to think and compare with others.",
                "Respectful conversation. {voter_name} appreciates outreach but hasn't made up mind yet.",
            ],
            'negative': [
                "Voter skeptical about political promises. Discussed {issue} but remains unconvinced. Will try again later.",
                "Strong supporter of {opponent}. Brief conversation, left materials. Unlikely to change affiliation.",
                "Disappointed with political system overall. Expressed frustration about {issue}. Cordial but not interested.",
                "Critical of new party entry. Believes established parties better. Noted concerns about {issue} for report.",
                "Refused detailed discussion. Stated loyalty to {party}. Maintained respectful interaction throughout.",
                "Concerned about {issue} but distrusts all political parties. Challenging conversation, documented concerns.",
                "Previously contacted, still negative. Needs more time and evidence of concrete action on {issue}.",
            ]
        }

        # Get voters with weighted preference for high/medium influence
        self.stdout.write('Loading voters from database...')
        all_voters = list(Voter.objects.all().select_related('constituency', 'district'))

        if not all_voters:
            self.stdout.write(self.style.ERROR('No voters found. Please run generate_voters first.'))
            return

        # Separate voters by influence level
        high_influence_voters = [v for v in all_voters if v.influence_level == 'high']
        medium_influence_voters = [v for v in all_voters if v.influence_level == 'medium']
        low_influence_voters = [v for v in all_voters if v.influence_level == 'low']

        self.stdout.write(self.style.SUCCESS(
            f'Found {len(all_voters):,} voters: '
            f'{len(high_influence_voters):,} high, '
            f'{len(medium_influence_voters):,} medium, '
            f'{len(low_influence_voters):,} low influence'
        ))

        # Get users (booth agents and volunteers)
        users = list(User.objects.filter(is_active=True).exclude(username='system'))
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create booth agents and volunteers first.'))
            return

        # Simulate different activity levels for volunteers
        active_users = random.sample(users, min(len(users), max(1, len(users) // 2)))
        very_active_users = random.sample(active_users, min(len(active_users), max(1, len(active_users) // 3)))

        self.stdout.write(self.style.SUCCESS(f'Using {len(users)} users for interactions'))
        self.stdout.write('=' * 80)

        # Track statistics
        stats = {
            'total_created': 0,
            'by_type': {},
            'by_sentiment': {},
            'by_issue': {},
            'by_influence': {},
            'require_followup': 0,
            'recent_interactions': 0,  # Last 30 days
            'multiple_interactions': 0,  # Voters with 5+ interactions
        }

        def weighted_random(distribution):
            """Select item based on weighted distribution"""
            items = list(distribution.keys())
            weights = list(distribution.values())
            return random.choices(items, weights=weights, k=1)[0]

        def select_voter():
            """Select voter with bias towards high/medium influence (70% of interactions)"""
            rand = random.random()
            if rand < 0.35 and high_influence_voters:  # 35% high influence
                return random.choice(high_influence_voters)
            elif rand < 0.70 and medium_influence_voters:  # 35% medium influence
                return random.choice(medium_influence_voters)
            else:  # 30% low influence
                return random.choice(low_influence_voters) if low_influence_voters else random.choice(all_voters)

        def select_user():
            """Select user with different activity levels"""
            rand = random.random()
            if rand < 0.50 and very_active_users:  # 50% very active
                return random.choice(very_active_users)
            elif rand < 0.80 and active_users:  # 30% active
                return random.choice(active_users)
            else:  # 20% all users
                return random.choice(users)

        def generate_issues_discussed():
            """Generate 1-4 issues discussed based on distribution"""
            num_issues = random.choices([1, 2, 3, 4], weights=[0.40, 0.35, 0.20, 0.05], k=1)[0]
            all_issues = list(ISSUES_DISTRIBUTION.keys())
            weights = list(ISSUES_DISTRIBUTION.values())
            return random.choices(all_issues, weights=weights, k=num_issues)

        def generate_interaction_notes(sentiment, issues, voter, interaction_type):
            """Generate realistic interaction notes"""
            templates = NOTES_TEMPLATES[sentiment]
            template = random.choice(templates)

            # Replacement values
            replacements = {
                '{issue}': random.choice(issues) if issues else 'general',
                '{issue2}': random.choice(issues) if len(issues) > 1 else 'infrastructure',
                '{issues}': ', '.join(issues[:3]) if len(issues) > 2 else ', '.join(issues),
                '{ward}': voter.ward,
                '{area}': voter.address_line2 or voter.ward,
                '{voter_name}': voter.first_name,
                '{sentiment}': random.choice(['very positive', 'enthusiastic', 'supportive']),
                '{interest_area}': random.choice(['youth programs', 'education policy', 'job creation']),
                '{policy}': random.choice(['education', 'employment', 'agriculture', 'healthcare']),
                '{topic}': random.choice(['youth empowerment', 'job opportunities', 'education reform']),
                '{solution}': random.choice(['detailed plan', 'comprehensive policy', 'immediate action plan']),
                '{value}': random.choice(['integrity', 'transparency', 'accountability']),
                '{opponent}': random.choice(['DMK', 'AIADMK', 'BJP', 'Congress']),
                '{party}': random.choice(['DMK', 'AIADMK', 'BJP', 'Congress']),
            }

            note = template
            for key, value in replacements.items():
                note = note.replace(key, value)

            # Add interaction-specific details
            if interaction_type == 'phone_call':
                note = f"Phone call conducted. {note}"
            elif interaction_type == 'door_visit':
                note = f"Door-to-door visit. {note}"
            elif interaction_type == 'event_meeting':
                note = f"Met at community event. {note}"

            return note

        def get_interaction_date():
            """
            Generate interaction date with focus on recent activity
            Peak campaign activity in last 30 days: 50%
            Last 90 days: 30%
            Older than 90 days: 20%
            """
            rand = random.random()
            if rand < 0.50:  # Last 30 days
                days_ago = random.randint(0, 30)
                return True, timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            elif rand < 0.80:  # 31-90 days
                days_ago = random.randint(31, 90)
                return False, timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
            else:  # 91-180 days
                days_ago = random.randint(91, 180)
                return False, timezone.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

        # Track voter interaction counts for multiple interactions stat
        voter_interaction_counts = {}

        # Generate interactions in batches
        batch = []

        for i in range(total_count):
            try:
                # Select voter and user
                voter = select_voter()
                contacted_by = select_user()

                # Track interactions per voter
                voter_interaction_counts[voter.id] = voter_interaction_counts.get(voter.id, 0) + 1

                # Interaction type
                interaction_type = weighted_random(INTERACTION_TYPES)

                # Sentiment (influenced by voter's party affiliation and sentiment)
                if voter.party_affiliation == 'tvk':
                    # TVK supporters more positive
                    sentiment = random.choices(
                        ['positive', 'neutral', 'negative'],
                        weights=[0.75, 0.20, 0.05],
                        k=1
                    )[0]
                elif voter.sentiment in ['strong_supporter', 'supporter']:
                    sentiment = random.choices(
                        ['positive', 'neutral', 'negative'],
                        weights=[0.65, 0.25, 0.10],
                        k=1
                    )[0]
                else:
                    sentiment = weighted_random(SENTIMENT_DISTRIBUTION)

                # Issues discussed
                issues = generate_issues_discussed()

                # Duration
                duration_range = DURATION_RANGES[interaction_type]
                duration = random.randint(duration_range[0], duration_range[1]) if duration_range[1] > 0 else None

                # Interaction date
                is_recent, interaction_date = get_interaction_date()
                if is_recent:
                    stats['recent_interactions'] += 1

                # Follow-up requirement (40%)
                follow_up_required = random.random() < 0.40
                follow_up_date = None
                if follow_up_required:
                    stats['require_followup'] += 1
                    days_ahead = random.randint(7, 30)
                    follow_up_date = (interaction_date + timedelta(days=days_ahead)).date()

                # Generate realistic notes
                notes = generate_interaction_notes(sentiment, issues, voter, interaction_type)

                # Generate promises/commitments
                promises = ""
                if sentiment == 'positive' and random.random() > 0.60:
                    promise_templates = [
                        f"Promised to escalate {issues[0]} issue to district manager.",
                        f"Committed to organizing community meeting on {issues[0]} within 2 weeks.",
                        f"Will provide detailed information on TVK's {issues[0]} policy via WhatsApp.",
                        f"Promised to connect voter with local {random.choice(['youth', 'farmer', 'business'])} forum.",
                        "Will arrange meeting with constituency in-charge to discuss concerns.",
                        f"Committed to provide regular updates on {issues[0]} developments.",
                    ]
                    promises = random.choice(promise_templates)

                # Create interaction object
                interaction = VoterInteraction(
                    voter=voter,
                    interaction_type=interaction_type,
                    contacted_by=contacted_by,
                    interaction_date=interaction_date,
                    duration_minutes=duration,
                    sentiment=sentiment,
                    issues_discussed=issues,
                    promises_made=promises,
                    follow_up_required=follow_up_required,
                    follow_up_date=follow_up_date,
                    notes=notes,
                )

                batch.append(interaction)

                # Update statistics
                stats['by_type'][interaction_type] = stats['by_type'].get(interaction_type, 0) + 1
                stats['by_sentiment'][sentiment] = stats['by_sentiment'].get(sentiment, 0) + 1
                stats['by_influence'][voter.influence_level] = stats['by_influence'].get(voter.influence_level, 0) + 1
                for issue in issues:
                    stats['by_issue'][issue] = stats['by_issue'].get(issue, 0) + 1

                # Bulk create when batch is full
                if len(batch) >= batch_size:
                    with transaction.atomic():
                        VoterInteraction.objects.bulk_create(batch)
                    stats['total_created'] += len(batch)
                    self.stdout.write(
                        f"Progress: {stats['total_created']:,} / {total_count:,} interactions created "
                        f"({(stats['total_created']/total_count*100):.1f}%)"
                    )
                    batch = []

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error generating interaction {i+1}: {str(e)}"))
                continue

        # Create remaining interactions
        if batch:
            with transaction.atomic():
                VoterInteraction.objects.bulk_create(batch)
            stats['total_created'] += len(batch)

        # Calculate voters with multiple interactions (5+)
        stats['multiple_interactions'] = len([v for v in voter_interaction_counts.values() if v >= 5])

        # Update voter engagement statistics
        self.stdout.write('\nUpdating voter engagement statistics...')
        with transaction.atomic():
            for voter_id, count in voter_interaction_counts.items():
                voter = Voter.objects.get(id=voter_id)
                voter.interaction_count += count
                voter.contact_frequency += 1

                # Update last contacted
                last_interaction = VoterInteraction.objects.filter(voter=voter).order_by('-interaction_date').first()
                if last_interaction:
                    voter.last_contacted_at = last_interaction.interaction_date

                    # Update positive/negative interactions
                    positive = VoterInteraction.objects.filter(voter=voter, sentiment='positive').count()
                    negative = VoterInteraction.objects.filter(voter=voter, sentiment='negative').count()
                    voter.positive_interactions = positive
                    voter.negative_interactions = negative

                voter.save()

        # Display comprehensive statistics
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('VOTER INTERACTION GENERATION COMPLETE'))
        self.stdout.write('=' * 80)
        self.stdout.write(f"\nTotal Interactions Created: {stats['total_created']:,}\n")

        self.stdout.write(self.style.WARNING('INTERACTION TYPES:'))
        for itype, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_created']) * 100
            type_display = itype.replace('_', ' ').title()
            self.stdout.write(f"  {type_display:20s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nSENTIMENT DISTRIBUTION:'))
        for sentiment, count in sorted(stats['by_sentiment'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {sentiment.capitalize():15s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nTOP 10 ISSUES DISCUSSED:'))
        for issue, count in sorted(stats['by_issue'].items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {issue:20s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nINTERACTIONS BY VOTER INFLUENCE:'))
        for influence, count in sorted(stats['by_influence'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / stats['total_created']) * 100
            self.stdout.write(f"  {influence.capitalize():15s}: {count:6,} ({percentage:5.2f}%)")

        self.stdout.write(self.style.WARNING('\nCAMPAIGN ACTIVITY PATTERNS:'))
        recent_pct = (stats['recent_interactions'] / stats['total_created']) * 100
        followup_pct = (stats['require_followup'] / stats['total_created']) * 100
        self.stdout.write(f"  Recent (Last 30 days):        {stats['recent_interactions']:6,} ({recent_pct:5.2f}%)")
        self.stdout.write(f"  Require Follow-up:            {stats['require_followup']:6,} ({followup_pct:5.2f}%)")
        self.stdout.write(f"  Voters with 5+ Interactions:  {stats['multiple_interactions']:6,}")

        self.stdout.write(self.style.WARNING('\nVOTER ENGAGEMENT:'))
        unique_voters = len(voter_interaction_counts)
        avg_interactions = sum(voter_interaction_counts.values()) / len(voter_interaction_counts)
        self.stdout.write(f"  Unique Voters Contacted:      {unique_voters:6,}")
        self.stdout.write(f"  Avg Interactions per Voter:   {avg_interactions:6.2f}")

        # Top contacted voters
        top_voters = sorted(voter_interaction_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        self.stdout.write(self.style.WARNING('\nTOP 5 CONTACTED VOTERS:'))
        for voter_id, count in top_voters:
            voter = Voter.objects.get(id=voter_id)
            self.stdout.write(
                f"  {voter.voter_id} - {voter.first_name} {voter.last_name} "
                f"({voter.influence_level}): {count} interactions"
            )

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS('Sample verification queries:'))
        self.stdout.write('  VoterInteraction.objects.filter(sentiment="positive").count()')
        self.stdout.write('  VoterInteraction.objects.filter(interaction_type="phone_call").count()')
        self.stdout.write('  VoterInteraction.objects.filter(follow_up_required=True).count()')
        self.stdout.write('  VoterInteraction.objects.filter(interaction_date__gte=timezone.now()-timedelta(days=30)).count()')
        self.stdout.write('  Voter.objects.filter(interaction_count__gte=5).count()')
        self.stdout.write('=' * 80)
