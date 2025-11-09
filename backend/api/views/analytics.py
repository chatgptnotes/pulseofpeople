"""
Analytics Views - Comprehensive analytics endpoints for Pulse of People Platform
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Sum, Q, F, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from api.models import (
    DirectFeedback, FieldReport, SentimentData, PollingBooth,
    State, District, Constituency, IssueCategory, VoterSegment
)
from api.models_analytics import (
    DailyVoterStats, DailyInteractionStats, DailySentimentStats,
    WeeklyCampaignStats
)


class VoterAnalyticsView(APIView):
    """
    GET /api/analytics/voters/
    Comprehensive voter analytics with filters
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Parse filters
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to', timezone.now().date())
        state_id = request.GET.get('state')
        district_id = request.GET.get('district')
        constituency_id = request.GET.get('constituency')
        aggregation = request.GET.get('aggregation', 'daily')  # daily, weekly, monthly

        # Base query
        stats_query = DailyVoterStats.objects.all()

        # Apply filters
        if date_from:
            stats_query = stats_query.filter(date__gte=date_from)
        if date_to:
            stats_query = stats_query.filter(date__lte=date_to)
        if state_id:
            stats_query = stats_query.filter(state_id=state_id)
        if district_id:
            stats_query = stats_query.filter(district_id=district_id)
        if constituency_id:
            stats_query = stats_query.filter(constituency_id=constituency_id)

        # Aggregate data
        totals = stats_query.aggregate(
            total_voters=Sum('total_voters'),
            new_voters=Sum('new_voters'),
            strong_supporters=Sum('strong_supporters'),
            supporters=Sum('supporters'),
            neutral=Sum('neutral'),
            opposition=Sum('opposition'),
            strong_opposition=Sum('strong_opposition'),
            male_voters=Sum('male_voters'),
            female_voters=Sum('female_voters'),
            other_voters=Sum('other_voters'),
            age_18_25=Sum('age_18_25'),
            age_26_35=Sum('age_26_35'),
            age_36_45=Sum('age_36_45'),
            age_46_60=Sum('age_46_60'),
            age_60_plus=Sum('age_60_plus'),
        )

        # Sentiment breakdown
        by_sentiment = {
            "strong_supporter": totals.get('strong_supporters', 0) or 0,
            "supporter": totals.get('supporters', 0) or 0,
            "neutral": totals.get('neutral', 0) or 0,
            "opposition": totals.get('opposition', 0) or 0,
            "strong_opposition": totals.get('strong_opposition', 0) or 0,
        }

        # Gender breakdown
        by_gender = {
            "male": totals.get('male_voters', 0) or 0,
            "female": totals.get('female_voters', 0) or 0,
            "other": totals.get('other_voters', 0) or 0,
        }

        # Age group breakdown
        by_age_group = {
            "18-25": totals.get('age_18_25', 0) or 0,
            "26-35": totals.get('age_26_35', 0) or 0,
            "36-45": totals.get('age_36_45', 0) or 0,
            "46-60": totals.get('age_46_60', 0) or 0,
            "60+": totals.get('age_60_plus', 0) or 0,
        }

        # Growth trend
        growth_trend = []
        trend_data = stats_query.values('date').annotate(
            count=Sum('total_voters'),
            new=Sum('new_voters')
        ).order_by('date')
        for item in trend_data:
            growth_trend.append({
                "date": str(item['date']),
                "count": item['count'],
                "new": item['new']
            })

        # Constituency breakdown
        by_constituency = []
        if not constituency_id:
            constituency_stats = stats_query.values(
                'constituency__name'
            ).annotate(
                total=Sum('total_voters'),
                supporters=Sum('strong_supporters') + Sum('supporters')
            ).order_by('-total')[:10]

            for item in constituency_stats:
                by_constituency.append({
                    "constituency": item['constituency__name'] or "Unknown",
                    "total": item['total'],
                    "supporters": item['supporters']
                })

        # Influence distribution (mock data - implement based on voter model)
        influence_distribution = {
            "high": 0,
            "medium": 0,
            "low": 0
        }

        return Response({
            "total_voters": totals.get('total_voters', 0) or 0,
            "by_sentiment": by_sentiment,
            "by_gender": by_gender,
            "by_age_group": by_age_group,
            "by_constituency": by_constituency,
            "growth_trend": growth_trend,
            "influence_distribution": influence_distribution,
            "filters_applied": {
                "date_from": date_from,
                "date_to": date_to,
                "state": state_id,
                "district": district_id,
                "constituency": constituency_id,
            }
        })


class CampaignAnalyticsView(APIView):
    """
    GET /api/analytics/campaigns/
    Campaign performance metrics
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to', timezone.now().date())
        state_id = request.GET.get('state')
        district_id = request.GET.get('district')

        # Base query
        stats_query = WeeklyCampaignStats.objects.all()

        # Apply filters
        if date_from:
            stats_query = stats_query.filter(week_start__gte=date_from)
        if date_to:
            stats_query = stats_query.filter(week_end__lte=date_to)
        if state_id:
            stats_query = stats_query.filter(state_id=state_id)
        if district_id:
            stats_query = stats_query.filter(district_id=district_id)

        # Aggregate
        totals = stats_query.aggregate(
            total_campaigns=Sum('total_campaigns'),
            active_campaigns=Sum('active_campaigns'),
            completed_campaigns=Sum('completed_campaigns'),
            total_reach=Sum('total_reach'),
            total_budget=Sum('total_budget'),
            total_spent=Sum('total_spent'),
            avg_roi=Avg('avg_roi'),
            total_interactions=Sum('total_interactions'),
            total_conversions=Sum('total_conversions'),
        )

        # Weekly trend
        weekly_trend = []
        for week_stat in stats_query.order_by('week_start'):
            weekly_trend.append({
                "week_start": str(week_stat.week_start),
                "campaigns": week_stat.total_campaigns,
                "reach": week_stat.total_reach,
                "conversions": week_stat.total_conversions,
                "roi": float(week_stat.avg_roi)
            })

        return Response({
            "total_campaigns": totals.get('total_campaigns', 0) or 0,
            "active_campaigns": totals.get('active_campaigns', 0) or 0,
            "completed_campaigns": totals.get('completed_campaigns', 0) or 0,
            "total_reach": totals.get('total_reach', 0) or 0,
            "total_budget": float(totals.get('total_budget', 0) or 0),
            "total_spent": float(totals.get('total_spent', 0) or 0),
            "avg_roi": float(totals.get('avg_roi', 0) or 0),
            "total_interactions": totals.get('total_interactions', 0) or 0,
            "total_conversions": totals.get('total_conversions', 0) or 0,
            "conversion_rate": round((totals.get('total_conversions', 0) or 0) / max(totals.get('total_interactions', 1), 1) * 100, 2),
            "weekly_trend": weekly_trend,
        })


class InteractionAnalyticsView(APIView):
    """
    GET /api/analytics/interactions/
    Interaction analytics and performance metrics
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to', timezone.now().date())
        state_id = request.GET.get('state')
        district_id = request.GET.get('district')
        constituency_id = request.GET.get('constituency')

        # Base query
        stats_query = DailyInteractionStats.objects.all()

        # Apply filters
        if date_from:
            stats_query = stats_query.filter(date__gte=date_from)
        if date_to:
            stats_query = stats_query.filter(date__lte=date_to)
        if state_id:
            stats_query = stats_query.filter(state_id=state_id)
        if district_id:
            stats_query = stats_query.filter(district_id=district_id)
        if constituency_id:
            stats_query = stats_query.filter(constituency_id=constituency_id)

        # Aggregate
        totals = stats_query.aggregate(
            total_interactions=Sum('total_interactions'),
            phone_calls=Sum('phone_calls'),
            door_to_door=Sum('door_to_door'),
            events=Sum('events'),
            social_media=Sum('social_media'),
            conversions=Sum('conversions'),
            avg_response_rate=Avg('response_rate'),
            unique_volunteers=Sum('active_volunteers'),
        )

        # By type
        by_type = {
            "phone_calls": totals.get('phone_calls', 0) or 0,
            "door_to_door": totals.get('door_to_door', 0) or 0,
            "events": totals.get('events', 0) or 0,
            "social_media": totals.get('social_media', 0) or 0,
        }

        # Daily trend
        daily_trend = []
        for day_stat in stats_query.order_by('date'):
            daily_trend.append({
                "date": str(day_stat.date),
                "interactions": day_stat.total_interactions,
                "conversions": day_stat.conversions,
                "response_rate": float(day_stat.response_rate)
            })

        total_int = totals.get('total_interactions', 0) or 0
        total_conv = totals.get('conversions', 0) or 0

        return Response({
            "total_interactions": total_int,
            "by_type": by_type,
            "total_conversions": total_conv,
            "conversion_rate": round(total_conv / max(total_int, 1) * 100, 2),
            "avg_response_rate": float(totals.get('avg_response_rate', 0) or 0),
            "active_volunteers": totals.get('unique_volunteers', 0) or 0,
            "daily_trend": daily_trend,
        })


class GeographicAnalyticsView(APIView):
    """
    GET /api/analytics/geographic/
    Geographic breakdown and heatmap data
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to', timezone.now().date())

        # State-wise breakdown
        state_query = DailyVoterStats.objects.filter(
            state__isnull=False,
            district__isnull=True,
            constituency__isnull=True
        )
        if date_from:
            state_query = state_query.filter(date__gte=date_from)
        if date_to:
            state_query = state_query.filter(date__lte=date_to)

        state_breakdown = []
        state_stats = state_query.values('state__name').annotate(
            total=Sum('total_voters'),
            supporters=Sum('strong_supporters') + Sum('supporters')
        )
        for item in state_stats:
            state_breakdown.append({
                "state": item['state__name'],
                "total_voters": item['total'],
                "supporters": item['supporters']
            })

        # District-wise breakdown
        district_query = DailyVoterStats.objects.filter(
            district__isnull=False,
            constituency__isnull=True
        )
        if date_from:
            district_query = district_query.filter(date__gte=date_from)
        if date_to:
            district_query = district_query.filter(date__lte=date_to)

        district_breakdown = []
        district_stats = district_query.values('district__name', 'state__name').annotate(
            total=Sum('total_voters')
        ).order_by('-total')[:20]
        for item in district_stats:
            district_breakdown.append({
                "district": item['district__name'],
                "state": item['state__name'],
                "total_voters": item['total']
            })

        # Constituency-wise breakdown
        constituency_query = DailyVoterStats.objects.filter(
            constituency__isnull=False
        )
        if date_from:
            constituency_query = constituency_query.filter(date__gte=date_from)
        if date_to:
            constituency_query = constituency_query.filter(date__lte=date_to)

        constituency_breakdown = []
        constituency_stats = constituency_query.values('constituency__name').annotate(
            total=Sum('total_voters')
        ).order_by('-total')[:20]
        for item in constituency_stats:
            constituency_breakdown.append({
                "constituency": item['constituency__name'],
                "total_voters": item['total']
            })

        # Heatmap data (polling booths with coordinates)
        heatmap_data = []
        booths_with_coords = PollingBooth.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            is_active=True
        )[:500]  # Limit for performance

        for booth in booths_with_coords:
            heatmap_data.append({
                "lat": float(booth.latitude),
                "lng": float(booth.longitude),
                "value": booth.total_voters,
                "name": booth.name
            })

        return Response({
            "state_breakdown": state_breakdown,
            "district_breakdown": district_breakdown,
            "constituency_breakdown": constituency_breakdown,
            "heatmap_data": heatmap_data,
            "coverage_summary": {
                "total_states": len(state_breakdown),
                "total_districts": len(district_breakdown),
                "total_constituencies": len(constituency_breakdown),
                "mapped_booths": len(heatmap_data)
            }
        })


class SentimentAnalyticsView(APIView):
    """
    GET /api/analytics/sentiment/
    Sentiment analysis and trends
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to', timezone.now().date())
        state_id = request.GET.get('state')
        district_id = request.GET.get('district')
        constituency_id = request.GET.get('constituency')

        # Base query
        stats_query = DailySentimentStats.objects.all()

        # Apply filters
        if date_from:
            stats_query = stats_query.filter(date__gte=date_from)
        if date_to:
            stats_query = stats_query.filter(date__lte=date_to)
        if state_id:
            stats_query = stats_query.filter(state_id=state_id)
        if district_id:
            stats_query = stats_query.filter(district_id=district_id)
        if constituency_id:
            stats_query = stats_query.filter(constituency_id=constituency_id)

        # Overall sentiment
        overall = stats_query.aggregate(
            avg_score=Avg('avg_sentiment_score'),
            avg_velocity=Avg('sentiment_velocity'),
            positive=Sum('positive_count'),
            negative=Sum('negative_count'),
            neutral=Sum('neutral_count'),
        )

        # Convert to -100 to +100 scale
        avg_score = float(overall.get('avg_score', 0) or 0)
        overall_sentiment_score = round((avg_score - 0.5) * 200, 2)

        # Trend over time
        sentiment_trend = []
        for day_stat in stats_query.filter(issue__isnull=True).order_by('date'):
            sentiment_trend.append({
                "date": str(day_stat.date),
                "score": float(day_stat.avg_sentiment_score),
                "velocity": float(day_stat.sentiment_velocity)
            })

        # By issue
        by_issue = []
        issue_stats = stats_query.filter(issue__isnull=False).values(
            'issue__name'
        ).annotate(
            avg_score=Avg('avg_sentiment_score'),
            total=Sum('positive_count') + Sum('negative_count') + Sum('neutral_count')
        ).order_by('-total')[:10]

        for item in issue_stats:
            by_issue.append({
                "issue": item['issue__name'],
                "score": float(item['avg_score'] or 0),
                "mentions": item['total']
            })

        # By location
        by_location = []
        if not constituency_id:
            location_stats = stats_query.values('constituency__name').annotate(
                avg_score=Avg('avg_sentiment_score')
            ).order_by('-avg_score')[:10]

            for item in location_stats:
                by_location.append({
                    "location": item['constituency__name'] or "Unknown",
                    "score": float(item['avg_score'] or 0)
                })

        return Response({
            "overall_sentiment_score": overall_sentiment_score,
            "sentiment_distribution": {
                "positive": overall.get('positive', 0) or 0,
                "negative": overall.get('negative', 0) or 0,
                "neutral": overall.get('neutral', 0) or 0,
            },
            "sentiment_velocity": float(overall.get('avg_velocity', 0) or 0),
            "sentiment_trend": sentiment_trend,
            "by_issue": by_issue,
            "by_location": by_location,
        })


class SocialMediaAnalyticsView(APIView):
    """
    GET /api/analytics/social-media/
    Social media performance metrics (mock implementation)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Mock data - implement with actual social media integration
        return Response({
            "platforms": {
                "facebook": {
                    "followers": 150000,
                    "reach": 450000,
                    "engagement_rate": 4.5,
                    "post_count": 125
                },
                "twitter": {
                    "followers": 85000,
                    "reach": 320000,
                    "engagement_rate": 3.8,
                    "post_count": 210
                },
                "instagram": {
                    "followers": 120000,
                    "reach": 380000,
                    "engagement_rate": 5.2,
                    "post_count": 95
                }
            },
            "top_posts": [
                {"platform": "facebook", "content": "Campaign announcement", "reach": 25000, "engagement": 1200},
                {"platform": "instagram", "content": "Event photos", "reach": 18000, "engagement": 950},
            ],
            "best_posting_times": ["09:00", "13:00", "19:00"],
            "trending_hashtags": ["#TVK", "#PeopleFirst", "#Progress"],
            "follower_growth": [
                {"date": "2025-11-01", "followers": 145000},
                {"date": "2025-11-08", "followers": 155000},
            ]
        })


class FieldReportAnalyticsView(APIView):
    """
    GET /api/analytics/field-reports/
    Field report analytics
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to', timezone.now().date())

        # Base query
        reports_query = FieldReport.objects.all()

        # Apply filters
        if date_from:
            reports_query = reports_query.filter(report_date__gte=date_from)
        if date_to:
            reports_query = reports_query.filter(report_date__lte=date_to)

        # By type
        by_type = reports_query.values('report_type').annotate(
            count=Count('id')
        )
        reports_by_type = {item['report_type']: item['count'] for item in by_type}

        # By status
        by_status = reports_query.values('verification_status').annotate(
            count=Count('id')
        )
        reports_by_status = {item['verification_status']: item['count'] for item in by_status}

        # Top reporters
        top_reporters = reports_query.values(
            'volunteer__username', 'volunteer__first_name', 'volunteer__last_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        top_volunteers = []
        for item in top_reporters:
            name = f"{item['volunteer__first_name']} {item['volunteer__last_name']}".strip()
            top_volunteers.append({
                "name": name or item['volunteer__username'],
                "report_count": item['count']
            })

        # Geographic distribution
        geographic = reports_query.values('constituency__name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        geographic_dist = [
            {"location": item['constituency__name'] or "Unknown", "count": item['count']}
            for item in geographic
        ]

        return Response({
            "total_reports": reports_query.count(),
            "by_type": reports_by_type,
            "by_status": reports_by_status,
            "top_volunteers": top_volunteers,
            "geographic_distribution": geographic_dist,
            "avg_response_time": "4.5 hours",  # Mock - calculate from verified_at - timestamp
        })


class BoothAnalyticsView(APIView):
    """
    GET /api/analytics/polling-booths/
    Polling booth coverage and statistics
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state_id = request.GET.get('state')
        district_id = request.GET.get('district')
        constituency_id = request.GET.get('constituency')

        # Base query
        booths_query = PollingBooth.objects.all()

        # Apply filters
        if state_id:
            booths_query = booths_query.filter(state_id=state_id)
        if district_id:
            booths_query = booths_query.filter(district_id=district_id)
        if constituency_id:
            booths_query = booths_query.filter(constituency_id=constituency_id)

        # Statistics
        stats = booths_query.aggregate(
            total_booths=Count('id'),
            total_voters=Sum('total_voters'),
            avg_voters_per_booth=Avg('total_voters'),
            mapped_booths=Count('id', filter=Q(latitude__isnull=False, longitude__isnull=False)),
            accessible_booths=Count('id', filter=Q(is_accessible=True)),
        )

        # By constituency
        by_constituency = booths_query.values('constituency__name').annotate(
            booth_count=Count('id'),
            voter_count=Sum('total_voters')
        ).order_by('-voter_count')[:10]

        constituency_breakdown = [
            {
                "constituency": item['constituency__name'],
                "booths": item['booth_count'],
                "voters": item['voter_count']
            }
            for item in by_constituency
        ]

        # Coverage analysis
        total = stats['total_booths']
        mapped = stats['mapped_booths']
        coverage_percentage = round(mapped / max(total, 1) * 100, 2)

        return Response({
            "total_booths": total,
            "total_voters": stats['total_voters'] or 0,
            "avg_voters_per_booth": round(float(stats['avg_voters_per_booth'] or 0), 2),
            "mapped_booths": mapped,
            "unmapped_booths": total - mapped,
            "coverage_percentage": coverage_percentage,
            "accessible_booths": stats['accessible_booths'],
            "by_constituency": constituency_breakdown,
        })


class ComparativeAnalyticsView(APIView):
    """
    GET /api/analytics/compare/
    Comparative analytics between locations or time periods
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        compare_type = request.GET.get('type', 'constituencies')  # constituencies, districts, time_periods
        item1_id = request.GET.get('item1')
        item2_id = request.GET.get('item2')

        if compare_type == 'constituencies' and item1_id and item2_id:
            # Compare two constituencies
            const1_stats = DailyVoterStats.objects.filter(constituency_id=item1_id).aggregate(
                total=Sum('total_voters'),
                supporters=Sum('strong_supporters') + Sum('supporters')
            )
            const2_stats = DailyVoterStats.objects.filter(constituency_id=item2_id).aggregate(
                total=Sum('total_voters'),
                supporters=Sum('strong_supporters') + Sum('supporters')
            )

            try:
                const1 = Constituency.objects.get(id=item1_id)
                const2 = Constituency.objects.get(id=item2_id)
            except Constituency.DoesNotExist:
                return Response({"error": "Constituency not found"}, status=status.HTTP_404_NOT_FOUND)

            return Response({
                "comparison_type": "constituencies",
                "item1": {
                    "name": const1.name,
                    "total_voters": const1_stats['total'] or 0,
                    "supporters": const1_stats['supporters'] or 0,
                },
                "item2": {
                    "name": const2.name,
                    "total_voters": const2_stats['total'] or 0,
                    "supporters": const2_stats['supporters'] or 0,
                }
            })

        elif compare_type == 'time_periods':
            # Compare this month vs last month
            today = timezone.now().date()
            this_month_start = today.replace(day=1)
            last_month_end = this_month_start - timedelta(days=1)
            last_month_start = last_month_end.replace(day=1)

            this_month = DailyVoterStats.objects.filter(
                date__gte=this_month_start,
                date__lte=today
            ).aggregate(
                total=Sum('total_voters'),
                new=Sum('new_voters')
            )

            last_month = DailyVoterStats.objects.filter(
                date__gte=last_month_start,
                date__lte=last_month_end
            ).aggregate(
                total=Sum('total_voters'),
                new=Sum('new_voters')
            )

            return Response({
                "comparison_type": "time_periods",
                "this_month": {
                    "total_voters": this_month['total'] or 0,
                    "new_voters": this_month['new'] or 0,
                },
                "last_month": {
                    "total_voters": last_month['total'] or 0,
                    "new_voters": last_month['new'] or 0,
                },
                "change": {
                    "total": (this_month['total'] or 0) - (last_month['total'] or 0),
                    "new": (this_month['new'] or 0) - (last_month['new'] or 0),
                }
            })

        return Response({"error": "Invalid comparison parameters"}, status=status.HTTP_400_BAD_REQUEST)


class PredictiveAnalyticsView(APIView):
    """
    GET /api/analytics/predictions/
    Predictive analytics (mock implementation - integrate ML models later)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Mock predictive data - implement with ML models
        return Response({
            "voter_turnout_prediction": {
                "estimated_turnout": 68.5,
                "confidence": 0.82,
                "factors": ["Historical data", "Current sentiment", "Campaign intensity"]
            },
            "sentiment_forecast": {
                "next_7_days": [
                    {"date": "2025-11-10", "predicted_score": 0.65},
                    {"date": "2025-11-11", "predicted_score": 0.67},
                    {"date": "2025-11-12", "predicted_score": 0.68},
                ],
                "trend": "improving"
            },
            "risk_areas": [
                {"constituency": "Constituency A", "risk_level": "high", "reason": "Declining sentiment"},
                {"constituency": "Constituency B", "risk_level": "medium", "reason": "Low volunteer activity"},
            ],
            "opportunities": [
                {"constituency": "Constituency C", "opportunity": "High undecided voters", "potential": "high"},
                {"segment": "Youth voters", "opportunity": "Growing positive sentiment", "potential": "medium"},
            ]
        })
