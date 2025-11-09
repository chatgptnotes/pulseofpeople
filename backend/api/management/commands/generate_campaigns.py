"""
Django management command to generate realistic TVK campaign data

Usage:
    python manage.py generate_campaigns
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from api.models import Campaign, Constituency, UserProfile
from decimal import Decimal
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Generate 30 realistic TVK campaigns with diverse types and statuses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing campaigns before generating new ones',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing all existing campaigns...'))
            Campaign.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Campaigns cleared.'))

        self.stdout.write(self.style.NOTICE('Starting campaign generation...'))

        # Get required data
        constituencies = list(Constituency.objects.all())
        if not constituencies:
            self.stdout.write(self.style.ERROR('No constituencies found. Please load constituency data first.'))
            return

        # Get managers and analysts for campaign managers
        managers = list(User.objects.filter(profile__role__in=['manager', 'analyst']))
        if not managers:
            self.stdout.write(self.style.ERROR('No managers/analysts found. Please create users first.'))
            return

        # Get users for team members
        team_pool = list(User.objects.filter(profile__role__in=['user', 'volunteer', 'analyst']))
        if not team_pool:
            self.stdout.write(self.style.ERROR('No team members found. Please create users first.'))
            return

        # Define campaign templates
        campaign_templates = self._get_campaign_templates()

        # Statistics tracking
        stats = {
            'total': 0,
            'by_type': {'election': 0, 'awareness': 0, 'issue_based': 0, 'door_to_door': 0},
            'by_status': {'planning': 0, 'active': 0, 'completed': 0, 'cancelled': 0},
            'total_budget': Decimal('0'),
            'total_spent': Decimal('0'),
        }

        # Generate campaigns
        with transaction.atomic():
            campaigns = []

            for template in campaign_templates:
                campaign = self._create_campaign(
                    template,
                    constituencies,
                    managers,
                    team_pool
                )
                campaigns.append(campaign)

                # Update stats
                stats['total'] += 1
                stats['by_type'][campaign.campaign_type] += 1
                stats['by_status'][campaign.status] += 1
                stats['total_budget'] += campaign.budget
                stats['total_spent'] += campaign.spent_amount

            # Bulk create
            Campaign.objects.bulk_create(campaigns)

            # Add many-to-many relationships (team members)
            self.stdout.write(self.style.NOTICE('Assigning team members...'))
            for i, campaign in enumerate(Campaign.objects.all().order_by('-created_at')[:len(campaigns)]):
                team_size = random.randint(5, 20)
                team = random.sample(team_pool, min(team_size, len(team_pool)))
                campaign.team_members.set(team)

        # Display statistics
        self._display_statistics(stats)

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully generated {stats["total"]} campaigns!'))

    def _get_campaign_templates(self):
        """Define campaign templates with realistic data"""
        now = timezone.now()

        return [
            # ELECTION CAMPAIGNS (35% - 10-11 campaigns)
            {
                'name': '2026 Assembly Election - Chennai Region',
                'type': 'election',
                'status': 'planning',
                'budget_range': (30000000, 50000000),  # 3-5 Cr
                'duration_days': (150, 180),
                'start_offset_days': (60, 120),  # Future
                'spent_pct_range': (0, 5),
                'goals': {
                    'voter_contacts': 500000,
                    'events_planned': 50,
                    'volunteers_mobilized': 2000,
                    'social_media_reach': 5000000,
                    'booth_coverage': '100%'
                },
            },
            {
                'name': '2026 Assembly Election - Coimbatore Zone',
                'type': 'election',
                'status': 'planning',
                'budget_range': (25000000, 40000000),
                'duration_days': (150, 180),
                'start_offset_days': (60, 120),
                'spent_pct_range': (0, 8),
                'goals': {
                    'voter_contacts': 400000,
                    'events_planned': 45,
                    'volunteers_mobilized': 1500,
                    'social_media_reach': 4000000,
                    'booth_coverage': '95%'
                },
            },
            {
                'name': '2026 Assembly Election - Madurai Division',
                'type': 'election',
                'status': 'active',
                'budget_range': (20000000, 35000000),
                'duration_days': (120, 150),
                'start_offset_days': (-30, 0),  # Recently started
                'spent_pct_range': (15, 35),
                'goals': {
                    'voter_contacts': 350000,
                    'events_planned': 40,
                    'volunteers_mobilized': 1200,
                    'social_media_reach': 3500000,
                    'booth_coverage': '90%'
                },
            },
            {
                'name': 'Parliamentary Constituency Campaign - Central Chennai',
                'type': 'election',
                'status': 'planning',
                'budget_range': (15000000, 25000000),
                'duration_days': (120, 150),
                'start_offset_days': (90, 150),
                'spent_pct_range': (0, 10),
                'goals': {
                    'voter_contacts': 200000,
                    'events_planned': 30,
                    'volunteers_mobilized': 800,
                    'social_media_reach': 2000000,
                    'booth_coverage': '100%'
                },
            },
            {
                'name': 'Parliamentary Constituency Campaign - South Coimbatore',
                'type': 'election',
                'status': 'planning',
                'budget_range': (12000000, 20000000),
                'duration_days': (120, 150),
                'start_offset_days': (90, 150),
                'spent_pct_range': (0, 5),
                'goals': {
                    'voter_contacts': 180000,
                    'events_planned': 28,
                    'volunteers_mobilized': 700,
                    'social_media_reach': 1800000,
                    'booth_coverage': '95%'
                },
            },
            {
                'name': 'Assembly Constituency Pre-Campaign - T Nagar',
                'type': 'election',
                'status': 'active',
                'budget_range': (8000000, 15000000),
                'duration_days': (90, 120),
                'start_offset_days': (-45, -15),
                'spent_pct_range': (40, 60),
                'goals': {
                    'voter_contacts': 100000,
                    'events_planned': 25,
                    'volunteers_mobilized': 500,
                    'social_media_reach': 1000000,
                    'booth_coverage': '100%'
                },
            },
            {
                'name': 'Assembly Constituency Pre-Campaign - Mylapore',
                'type': 'election',
                'status': 'active',
                'budget_range': (8000000, 15000000),
                'duration_days': (90, 120),
                'start_offset_days': (-45, -15),
                'spent_pct_range': (35, 55),
                'goals': {
                    'voter_contacts': 95000,
                    'events_planned': 22,
                    'volunteers_mobilized': 450,
                    'social_media_reach': 950000,
                    'booth_coverage': '95%'
                },
            },
            {
                'name': 'By-Election Preparedness - Delta Districts',
                'type': 'election',
                'status': 'completed',
                'budget_range': (5000000, 10000000),
                'duration_days': (60, 90),
                'start_offset_days': (-120, -90),
                'spent_pct_range': (85, 100),
                'goals': {
                    'voter_contacts': 80000,
                    'events_planned': 20,
                    'volunteers_mobilized': 400,
                    'social_media_reach': 800000,
                    'booth_coverage': '85%'
                },
            },
            {
                'name': 'Assembly Seat Consolidation - Trichy Zone',
                'type': 'election',
                'status': 'active',
                'budget_range': (10000000, 18000000),
                'duration_days': (90, 120),
                'start_offset_days': (-30, 0),
                'spent_pct_range': (25, 45),
                'goals': {
                    'voter_contacts': 150000,
                    'events_planned': 30,
                    'volunteers_mobilized': 600,
                    'social_media_reach': 1500000,
                    'booth_coverage': '90%'
                },
            },
            {
                'name': 'Urban Seats Strategy - Metro Chennai',
                'type': 'election',
                'status': 'planning',
                'budget_range': (20000000, 35000000),
                'duration_days': (120, 150),
                'start_offset_days': (45, 90),
                'spent_pct_range': (0, 8),
                'goals': {
                    'voter_contacts': 300000,
                    'events_planned': 40,
                    'volunteers_mobilized': 1000,
                    'social_media_reach': 3000000,
                    'booth_coverage': '100%'
                },
            },

            # AWARENESS CAMPAIGNS (30% - 9 campaigns)
            {
                'name': 'TVK Vision 2026 - Statewide Awareness',
                'type': 'awareness',
                'status': 'active',
                'budget_range': (3000000, 5000000),  # 30-50L
                'duration_days': (60, 90),
                'start_offset_days': (-30, 0),
                'spent_pct_range': (40, 60),
                'goals': {
                    'voter_contacts': 200000,
                    'events_planned': 15,
                    'volunteers_mobilized': 500,
                    'social_media_reach': 2000000,
                    'booth_coverage': '50%'
                },
            },
            {
                'name': 'Corruption-Free Tamil Nadu Campaign',
                'type': 'awareness',
                'status': 'active',
                'budget_range': (2000000, 4000000),
                'duration_days': (60, 90),
                'start_offset_days': (-20, 0),
                'spent_pct_range': (35, 55),
                'goals': {
                    'voter_contacts': 150000,
                    'events_planned': 12,
                    'volunteers_mobilized': 400,
                    'social_media_reach': 1500000,
                    'booth_coverage': '40%'
                },
            },
            {
                'name': 'Youth Empowerment Initiative',
                'type': 'awareness',
                'status': 'active',
                'budget_range': (1500000, 3000000),
                'duration_days': (45, 75),
                'start_offset_days': (-25, -5),
                'spent_pct_range': (45, 65),
                'goals': {
                    'voter_contacts': 100000,
                    'events_planned': 20,
                    'volunteers_mobilized': 800,
                    'social_media_reach': 2500000,
                    'booth_coverage': '30%'
                },
            },
            {
                'name': 'Women Safety & Rights Campaign',
                'type': 'awareness',
                'status': 'completed',
                'budget_range': (1000000, 2000000),
                'duration_days': (30, 60),
                'start_offset_days': (-90, -60),
                'spent_pct_range': (90, 100),
                'goals': {
                    'voter_contacts': 80000,
                    'events_planned': 15,
                    'volunteers_mobilized': 300,
                    'social_media_reach': 1000000,
                    'booth_coverage': '25%'
                },
            },
            {
                'name': 'Education Rights Awareness - NEET Impact',
                'type': 'awareness',
                'status': 'planning',
                'budget_range': (2000000, 3500000),
                'duration_days': (45, 75),
                'start_offset_days': (15, 45),
                'spent_pct_range': (0, 10),
                'goals': {
                    'voter_contacts': 120000,
                    'events_planned': 18,
                    'volunteers_mobilized': 600,
                    'social_media_reach': 1800000,
                    'booth_coverage': '35%'
                },
            },
            {
                'name': 'Tamil Language & Culture Promotion',
                'type': 'awareness',
                'status': 'active',
                'budget_range': (1500000, 2500000),
                'duration_days': (60, 90),
                'start_offset_days': (-40, -10),
                'spent_pct_range': (50, 70),
                'goals': {
                    'voter_contacts': 100000,
                    'events_planned': 25,
                    'volunteers_mobilized': 500,
                    'social_media_reach': 1200000,
                    'booth_coverage': '30%'
                },
            },
            {
                'name': 'Environmental Conservation Drive',
                'type': 'awareness',
                'status': 'completed',
                'budget_range': (1000000, 1800000),
                'duration_days': (30, 45),
                'start_offset_days': (-75, -50),
                'spent_pct_range': (88, 98),
                'goals': {
                    'voter_contacts': 60000,
                    'events_planned': 10,
                    'volunteers_mobilized': 250,
                    'social_media_reach': 800000,
                    'booth_coverage': '20%'
                },
            },
            {
                'name': 'Digital Literacy for Rural Areas',
                'type': 'awareness',
                'status': 'planning',
                'budget_range': (1200000, 2200000),
                'duration_days': (45, 60),
                'start_offset_days': (30, 60),
                'spent_pct_range': (0, 5),
                'goals': {
                    'voter_contacts': 70000,
                    'events_planned': 15,
                    'volunteers_mobilized': 350,
                    'social_media_reach': 500000,
                    'booth_coverage': '25%'
                },
            },
            {
                'name': 'Healthcare Access Awareness',
                'type': 'awareness',
                'status': 'planning',
                'budget_range': (1800000, 3000000),
                'duration_days': (45, 75),
                'start_offset_days': (20, 50),
                'spent_pct_range': (0, 8),
                'goals': {
                    'voter_contacts': 90000,
                    'events_planned': 12,
                    'volunteers_mobilized': 400,
                    'social_media_reach': 1100000,
                    'booth_coverage': '30%'
                },
            },

            # ISSUE-BASED CAMPAIGNS (25% - 7-8 campaigns)
            {
                'name': 'Save TN Water - Community Mobilization',
                'type': 'issue_based',
                'status': 'active',
                'budget_range': (1500000, 3000000),  # 15-30L
                'duration_days': (60, 120),
                'start_offset_days': (-50, -20),
                'spent_pct_range': (50, 70),
                'goals': {
                    'voter_contacts': 120000,
                    'events_planned': 18,
                    'volunteers_mobilized': 600,
                    'social_media_reach': 1500000,
                    'booth_coverage': '40%'
                },
            },
            {
                'name': 'NEET Opposition - Students United',
                'type': 'issue_based',
                'status': 'active',
                'budget_range': (2000000, 3500000),
                'duration_days': (90, 150),
                'start_offset_days': (-60, -30),
                'spent_pct_range': (45, 65),
                'goals': {
                    'voter_contacts': 150000,
                    'events_planned': 25,
                    'volunteers_mobilized': 1000,
                    'social_media_reach': 2500000,
                    'booth_coverage': '35%'
                },
            },
            {
                'name': 'Jobs for Tamil Youth - Industrial Revival',
                'type': 'issue_based',
                'status': 'active',
                'budget_range': (2500000, 4000000),
                'duration_days': (90, 150),
                'start_offset_days': (-45, -15),
                'spent_pct_range': (40, 60),
                'goals': {
                    'voter_contacts': 180000,
                    'events_planned': 22,
                    'volunteers_mobilized': 800,
                    'social_media_reach': 2000000,
                    'booth_coverage': '45%'
                },
            },
            {
                'name': 'Fisher Community Rights Campaign',
                'type': 'issue_based',
                'status': 'completed',
                'budget_range': (800000, 1500000),
                'duration_days': (45, 75),
                'start_offset_days': (-90, -60),
                'spent_pct_range': (85, 100),
                'goals': {
                    'voter_contacts': 50000,
                    'events_planned': 12,
                    'volunteers_mobilized': 300,
                    'social_media_reach': 600000,
                    'booth_coverage': '30%'
                },
            },
            {
                'name': 'Cauvery Water Rights Movement',
                'type': 'issue_based',
                'status': 'active',
                'budget_range': (1800000, 2800000),
                'duration_days': (75, 120),
                'start_offset_days': (-40, -10),
                'spent_pct_range': (50, 70),
                'goals': {
                    'voter_contacts': 100000,
                    'events_planned': 16,
                    'volunteers_mobilized': 500,
                    'social_media_reach': 1200000,
                    'booth_coverage': '40%'
                },
            },
            {
                'name': 'Farmer Loan Waiver Advocacy',
                'type': 'issue_based',
                'status': 'planning',
                'budget_range': (1500000, 2500000),
                'duration_days': (60, 90),
                'start_offset_days': (20, 50),
                'spent_pct_range': (0, 10),
                'goals': {
                    'voter_contacts': 80000,
                    'events_planned': 14,
                    'volunteers_mobilized': 450,
                    'social_media_reach': 1000000,
                    'booth_coverage': '35%'
                },
            },
            {
                'name': 'Transport Workers Rights Initiative',
                'type': 'issue_based',
                'status': 'planning',
                'budget_range': (1000000, 2000000),
                'duration_days': (45, 75),
                'start_offset_days': (15, 45),
                'spent_pct_range': (0, 5),
                'goals': {
                    'voter_contacts': 60000,
                    'events_planned': 10,
                    'volunteers_mobilized': 350,
                    'social_media_reach': 800000,
                    'booth_coverage': '25%'
                },
            },
            {
                'name': 'Land Rights for Marginalized Communities',
                'type': 'issue_based',
                'status': 'cancelled',
                'budget_range': (1200000, 2000000),
                'duration_days': (60, 90),
                'start_offset_days': (-30, 0),
                'spent_pct_range': (15, 25),
                'goals': {
                    'voter_contacts': 70000,
                    'events_planned': 12,
                    'volunteers_mobilized': 400,
                    'social_media_reach': 700000,
                    'booth_coverage': '30%'
                },
            },

            # DOOR-TO-DOOR CAMPAIGNS (10% - 3 campaigns)
            {
                'name': 'Ward-wise Voter Connect - Phase 1',
                'type': 'door_to_door',
                'status': 'active',
                'budget_range': (800000, 1500000),  # 8-15L
                'duration_days': (45, 60),
                'start_offset_days': (-25, -5),
                'spent_pct_range': (50, 70),
                'goals': {
                    'voter_contacts': 80000,
                    'events_planned': 50,
                    'volunteers_mobilized': 400,
                    'social_media_reach': 200000,
                    'booth_coverage': '80%'
                },
            },
            {
                'name': 'Booth Saturation - Chennai Metro',
                'type': 'door_to_door',
                'status': 'completed',
                'budget_range': (1000000, 1800000),
                'duration_days': (30, 45),
                'start_offset_days': (-75, -50),
                'spent_pct_range': (90, 100),
                'goals': {
                    'voter_contacts': 100000,
                    'events_planned': 60,
                    'volunteers_mobilized': 500,
                    'social_media_reach': 300000,
                    'booth_coverage': '100%'
                },
            },
            {
                'name': 'Rural Outreach - Delta Districts',
                'type': 'door_to_door',
                'status': 'planning',
                'budget_range': (600000, 1200000),
                'duration_days': (45, 60),
                'start_offset_days': (20, 45),
                'spent_pct_range': (0, 5),
                'goals': {
                    'voter_contacts': 60000,
                    'events_planned': 40,
                    'volunteers_mobilized': 300,
                    'social_media_reach': 150000,
                    'booth_coverage': '70%'
                },
            },
        ]

    def _create_campaign(self, template, constituencies, managers, team_pool):
        """Create a campaign from template"""
        now = timezone.now()

        # Calculate dates
        start_offset = random.randint(*template['start_offset_days'])
        start_date = (now + timedelta(days=start_offset)).date()

        duration = random.randint(*template['duration_days'])
        end_date = start_date + timedelta(days=duration)

        # Calculate budget
        budget = Decimal(random.randint(*template['budget_range']))
        spent_pct = random.uniform(*template['spent_pct_range']) / 100
        spent_amount = budget * Decimal(str(spent_pct))

        # Calculate metrics based on status
        goals = template['goals'].copy()
        metrics = {}

        if template['status'] == 'completed':
            # Completed campaigns: 80-120% of goals achieved
            metrics = {
                'voters_contacted': int(goals['voter_contacts'] * random.uniform(0.80, 1.20)),
                'events_completed': int(goals['events_planned'] * random.uniform(0.85, 1.15)),
                'volunteers_active': int(goals['volunteers_mobilized'] * random.uniform(0.75, 1.10)),
                'social_media_impressions': int(goals['social_media_reach'] * random.uniform(0.70, 1.50)),
                'booths_covered': int(float(goals['booth_coverage'].rstrip('%')) * random.uniform(0.85, 1.05))
            }
        elif template['status'] == 'active':
            # Active campaigns: 30-70% progress
            progress = random.uniform(0.30, 0.70)
            metrics = {
                'voters_contacted': int(goals['voter_contacts'] * progress),
                'events_completed': int(goals['events_planned'] * progress),
                'volunteers_active': int(goals['volunteers_mobilized'] * random.uniform(0.70, 0.95)),
                'social_media_impressions': int(goals['social_media_reach'] * progress * random.uniform(0.80, 1.20)),
                'booths_covered': int(float(goals['booth_coverage'].rstrip('%')) * progress)
            }
        elif template['status'] == 'planning':
            # Planning campaigns: 0-15% progress
            progress = random.uniform(0.0, 0.15)
            metrics = {
                'voters_contacted': int(goals['voter_contacts'] * progress),
                'events_completed': int(goals['events_planned'] * progress),
                'volunteers_active': int(goals['volunteers_mobilized'] * progress),
                'social_media_impressions': int(goals['social_media_reach'] * progress),
                'booths_covered': int(float(goals['booth_coverage'].rstrip('%')) * progress)
            }
        else:  # cancelled
            # Cancelled campaigns: 10-30% progress
            progress = random.uniform(0.10, 0.30)
            metrics = {
                'voters_contacted': int(goals['voter_contacts'] * progress),
                'events_completed': int(goals['events_planned'] * progress),
                'volunteers_active': int(goals['volunteers_mobilized'] * progress),
                'social_media_impressions': int(goals['social_media_reach'] * progress),
                'booths_covered': int(float(goals['booth_coverage'].rstrip('%')) * progress)
            }

        # Create campaign
        campaign = Campaign(
            campaign_name=template['name'],
            campaign_type=template['type'],
            start_date=start_date,
            end_date=end_date,
            status=template['status'],
            budget=budget,
            spent_amount=spent_amount,
            target_constituency=random.choice(constituencies),
            target_audience=self._get_target_audience(template['type']),
            campaign_manager=random.choice(managers),
            goals=goals,
            metrics=metrics,
            created_by=random.choice(managers),
        )

        return campaign

    def _get_target_audience(self, campaign_type):
        """Get target audience description based on campaign type"""
        audiences = {
            'election': 'All registered voters in the constituency, with focus on swing voters and youth voters (18-35 age group)',
            'awareness': 'General public across all age groups, with emphasis on social media engagement and community leaders',
            'issue_based': 'Affected communities and stakeholders, opinion leaders, activists, and concerned citizens',
            'door_to_door': 'Ward-level registered voters, booth-level contacts, household decision makers',
        }
        return audiences.get(campaign_type, 'General public')

    def _display_statistics(self, stats):
        """Display campaign generation statistics"""
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('CAMPAIGN GENERATION STATISTICS'))
        self.stdout.write('='*70)

        self.stdout.write(f"\nTotal Campaigns Created: {stats['total']}")

        self.stdout.write('\nCampaigns by Type:')
        for ctype, count in stats['by_type'].items():
            pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            self.stdout.write(f"  {ctype.replace('_', ' ').title():20s}: {count:2d} ({pct:5.1f}%)")

        self.stdout.write('\nCampaigns by Status:')
        for status, count in stats['by_status'].items():
            pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            self.stdout.write(f"  {status.title():20s}: {count:2d} ({pct:5.1f}%)")

        self.stdout.write('\nBudget Summary:')
        self.stdout.write(f"  Total Budget Allocated: ₹{stats['total_budget']:,.2f}")
        self.stdout.write(f"  Total Amount Spent:     ₹{stats['total_spent']:,.2f}")
        spent_pct = (stats['total_spent'] / stats['total_budget'] * 100) if stats['total_budget'] > 0 else 0
        self.stdout.write(f"  Overall Spent:          {spent_pct:.1f}%")

        # Additional insights
        avg_budget = stats['total_budget'] / stats['total'] if stats['total'] > 0 else 0
        self.stdout.write(f"\n  Average Campaign Budget: ₹{avg_budget:,.2f}")

        self.stdout.write('\n' + '='*70)
