"""
Management Command: Aggregate Analytics Data
Run hourly to aggregate data for faster analytics queries

Usage:
    python manage.py aggregate_analytics
    python manage.py aggregate_analytics --date 2025-11-09
    python manage.py aggregate_analytics --backfill 30  # Backfill last 30 days
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q
from datetime import datetime, timedelta

from api.models import DirectFeedback, FieldReport, SentimentData
from api.models_analytics import (
    DailyVoterStats, DailyInteractionStats, DailySentimentStats,
    WeeklyCampaignStats
)


class Command(BaseCommand):
    help = 'Aggregate analytics data for faster queries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Specific date to aggregate (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--backfill',
            type=int,
            help='Backfill last N days',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-aggregation even if data exists',
        )

    def handle(self, *args, **options):
        specific_date = options.get('date')
        backfill_days = options.get('backfill')
        force = options.get('force')

        if specific_date:
            # Aggregate specific date
            target_date = datetime.strptime(specific_date, '%Y-%m-%d').date()
            self.aggregate_date(target_date, force)

        elif backfill_days:
            # Backfill multiple days
            self.stdout.write(f"Backfilling last {backfill_days} days...")
            for i in range(backfill_days):
                target_date = timezone.now().date() - timedelta(days=i)
                self.aggregate_date(target_date, force)

        else:
            # Default: aggregate yesterday's data
            yesterday = timezone.now().date() - timedelta(days=1)
            self.aggregate_date(yesterday, force)

        self.stdout.write(self.style.SUCCESS('Analytics aggregation completed'))

    def aggregate_date(self, target_date, force=False):
        """Aggregate data for a specific date"""
        self.stdout.write(f"Aggregating data for {target_date}...")

        # Aggregate voter stats
        self.aggregate_voter_stats(target_date, force)

        # Aggregate interaction stats
        self.aggregate_interaction_stats(target_date, force)

        # Aggregate sentiment stats
        self.aggregate_sentiment_stats(target_date, force)

        # Aggregate weekly campaign stats
        if target_date.weekday() == 6:  # Sunday - end of week
            self.aggregate_weekly_campaign_stats(target_date, force)

    def aggregate_voter_stats(self, target_date, force=False):
        """Aggregate daily voter statistics"""
        # TODO: Implement when Voter model is available
        # For now, create sample aggregation structure

        # Overall stats (no geographic filter)
        stats, created = DailyVoterStats.objects.get_or_create(
            date=target_date,
            state=None,
            district=None,
            constituency=None,
            defaults={
                'total_voters': 0,
                'new_voters': 0,
                'strong_supporters': 0,
                'supporters': 0,
                'neutral': 0,
                'opposition': 0,
                'strong_opposition': 0,
            }
        )

        if created or force:
            # Calculate metrics from voter model
            # stats.total_voters = Voter.objects.filter(...).count()
            # stats.new_voters = Voter.objects.filter(created_at__date=target_date).count()
            # stats.save()
            self.stdout.write(f"  Voter stats: Created/Updated")

    def aggregate_interaction_stats(self, target_date, force=False):
        """Aggregate daily interaction statistics"""
        # Count field reports as interactions
        reports_count = FieldReport.objects.filter(
            report_date=target_date
        ).count()

        # Overall stats
        stats, created = DailyInteractionStats.objects.get_or_create(
            date=target_date,
            state=None,
            district=None,
            constituency=None,
            defaults={
                'total_interactions': reports_count,
                'phone_calls': 0,
                'door_to_door': 0,
                'events': 0,
                'social_media': 0,
                'conversions': 0,
                'response_rate': 0.0,
                'active_volunteers': 0,
            }
        )

        if created or force:
            # Count interactions by type
            event_reports = FieldReport.objects.filter(
                report_date=target_date,
                report_type='event_feedback'
            ).count()

            stats.total_interactions = reports_count
            stats.events = event_reports

            # Count unique volunteers
            unique_volunteers = FieldReport.objects.filter(
                report_date=target_date
            ).values('volunteer').distinct().count()
            stats.active_volunteers = unique_volunteers

            stats.save()
            self.stdout.write(f"  Interaction stats: {reports_count} interactions")

    def aggregate_sentiment_stats(self, target_date, force=False):
        """Aggregate daily sentiment statistics"""
        # Overall sentiment
        sentiment_data = SentimentData.objects.filter(
            timestamp__date=target_date
        )

        if sentiment_data.exists():
            aggregates = sentiment_data.aggregate(
                avg_score=Avg('sentiment_score'),
                positive=Count('id', filter=Q(polarity='positive')),
                negative=Count('id', filter=Q(polarity='negative')),
                neutral=Count('id', filter=Q(polarity='neutral')),
            )

            # Count by source
            from_feedback = sentiment_data.filter(source_type='direct_feedback').count()
            from_reports = sentiment_data.filter(source_type='field_report').count()
            from_social = sentiment_data.filter(source_type='social_media').count()
            from_survey = sentiment_data.filter(source_type='survey').count()

            stats, created = DailySentimentStats.objects.get_or_create(
                date=target_date,
                state=None,
                district=None,
                constituency=None,
                issue=None,
                defaults={
                    'avg_sentiment_score': aggregates['avg_score'] or 0.0,
                    'positive_count': aggregates['positive'],
                    'negative_count': aggregates['negative'],
                    'neutral_count': aggregates['neutral'],
                    'from_feedback': from_feedback,
                    'from_field_reports': from_reports,
                    'from_social_media': from_social,
                    'from_surveys': from_survey,
                }
            )

            if not created and force:
                stats.avg_sentiment_score = aggregates['avg_score'] or 0.0
                stats.positive_count = aggregates['positive']
                stats.negative_count = aggregates['negative']
                stats.neutral_count = aggregates['neutral']
                stats.from_feedback = from_feedback
                stats.from_field_reports = from_reports
                stats.from_social_media = from_social
                stats.from_surveys = from_survey
                stats.save()

            self.stdout.write(f"  Sentiment stats: Avg score {aggregates['avg_score']:.2f}")

            # Aggregate by issue category
            for issue_id in sentiment_data.values_list('issue', flat=True).distinct():
                if issue_id:
                    issue_sentiment = sentiment_data.filter(issue_id=issue_id)
                    issue_aggregates = issue_sentiment.aggregate(
                        avg_score=Avg('sentiment_score'),
                        positive=Count('id', filter=Q(polarity='positive')),
                        negative=Count('id', filter=Q(polarity='negative')),
                        neutral=Count('id', filter=Q(polarity='neutral')),
                    )

                    DailySentimentStats.objects.update_or_create(
                        date=target_date,
                        issue_id=issue_id,
                        state=None,
                        district=None,
                        constituency=None,
                        defaults={
                            'avg_sentiment_score': issue_aggregates['avg_score'] or 0.0,
                            'positive_count': issue_aggregates['positive'],
                            'negative_count': issue_aggregates['negative'],
                            'neutral_count': issue_aggregates['neutral'],
                        }
                    )

    def aggregate_weekly_campaign_stats(self, week_end_date, force=False):
        """Aggregate weekly campaign statistics"""
        week_start = week_end_date - timedelta(days=6)

        self.stdout.write(f"  Aggregating weekly stats for week {week_start} to {week_end_date}")

        # TODO: Implement when Campaign model is available
        stats, created = WeeklyCampaignStats.objects.get_or_create(
            week_start=week_start,
            week_end=week_end_date,
            state=None,
            district=None,
            defaults={
                'total_campaigns': 0,
                'active_campaigns': 0,
                'completed_campaigns': 0,
                'total_reach': 0,
                'total_budget': 0.0,
                'total_spent': 0.0,
                'avg_roi': 0.0,
                'total_interactions': 0,
                'total_conversions': 0,
            }
        )

        if created or force:
            # Calculate weekly interaction totals
            weekly_interactions = DailyInteractionStats.objects.filter(
                date__gte=week_start,
                date__lte=week_end_date
            ).aggregate(
                total=Sum('total_interactions'),
                conversions=Sum('conversions')
            )

            stats.total_interactions = weekly_interactions['total'] or 0
            stats.total_conversions = weekly_interactions['conversions'] or 0
            stats.save()

            self.stdout.write(f"  Weekly campaign stats: {stats.total_interactions} interactions")
