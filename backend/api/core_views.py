"""
ViewSets for Core Political Platform Models - Workstream 2
Complete CRUD operations with filtering, search, pagination, and custom actions
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Voter, VoterInteraction, Campaign, SocialMediaPost, Alert, Event,
    VolunteerProfile, Expense, Organization
)
from .core_serializers import (
    VoterListSerializer, VoterDetailSerializer, VoterCreateSerializer, VoterUpdateSerializer,
    VoterInteractionListSerializer, VoterInteractionDetailSerializer, VoterInteractionCreateSerializer,
    CampaignListSerializer, CampaignDetailSerializer, CampaignCreateSerializer,
    SocialMediaPostListSerializer, SocialMediaPostDetailSerializer, SocialMediaPostCreateSerializer,
    AlertListSerializer, AlertDetailSerializer, AlertCreateSerializer,
    EventListSerializer, EventDetailSerializer, EventCreateSerializer,
    VolunteerListSerializer, VolunteerDetailSerializer, VolunteerCreateSerializer,
    ExpenseListSerializer, ExpenseDetailSerializer, ExpenseCreateSerializer,
    OrganizationListSerializer, OrganizationSerializer
)


# ==================== ORGANIZATION VIEWSET ====================

class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Organizations

    GET /api/organizations/ - List all organizations
    POST /api/organizations/ - Create organization
    GET /api/organizations/{id}/ - Get organization details
    PUT/PATCH /api/organizations/{id}/ - Update organization
    DELETE /api/organizations/{id}/ - Delete organization
    """
    queryset = Organization.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'slug', 'contact_email', 'city']
    filterset_fields = ['organization_type', 'subscription_plan', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganizationListSerializer
        return OrganizationSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get organization statistics"""
        queryset = self.get_queryset()
        return Response({
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'by_type': dict(queryset.values('organization_type').annotate(count=Count('id')).values_list('organization_type', 'count')),
            'by_plan': dict(queryset.values('subscription_plan').annotate(count=Count('id')).values_list('subscription_plan', 'count')),
        })


# ==================== VOTER VIEWSET ====================

class VoterViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Voters

    GET /api/voters/ - List all voters (role-filtered)
    POST /api/voters/ - Create voter
    GET /api/voters/{id}/ - Get voter details
    PUT/PATCH /api/voters/{id}/ - Update voter
    DELETE /api/voters/{id}/ - Delete voter

    Custom actions:
    GET /api/voters/stats/ - Get voter statistics
    GET /api/voters/by_sentiment/ - Group by sentiment
    POST /api/voters/bulk_import/ - Bulk import voters
    GET /api/voters/export/ - Export voters to CSV
    """
    queryset = Voter.objects.select_related('constituency', 'district', 'state', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['voter_id', 'first_name', 'last_name', 'phone', 'email']
    filterset_fields = ['party_affiliation', 'sentiment', 'influence_level', 'is_active', 'gender', 'ward']
    ordering_fields = ['created_at', 'first_name', 'age', 'last_contacted_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return VoterListSerializer
        elif self.action == 'create':
            return VoterCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VoterUpdateSerializer
        return VoterDetailSerializer

    def get_queryset(self):
        """
        Role-based filtering of voters
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Superadmin sees everything
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'superadmin'):
            return queryset

        # Get user profile
        if not hasattr(user, 'profile'):
            return queryset.none()

        profile = user.profile

        # Admin (State level) - sees entire state
        if profile.role == 'admin' and profile.assigned_state:
            return queryset.filter(state=profile.assigned_state)

        # Manager (District level) - sees their district
        if profile.role == 'manager' and profile.assigned_district:
            return queryset.filter(district=profile.assigned_district)

        # Analyst or below - sees only voters they created
        return queryset.filter(created_by=user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get voter statistics"""
        queryset = self.get_queryset()

        return Response({
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'by_party': dict(queryset.values('party_affiliation').annotate(count=Count('id')).values_list('party_affiliation', 'count')),
            'by_sentiment': dict(queryset.values('sentiment').annotate(count=Count('id')).values_list('sentiment', 'count')),
            'by_influence': dict(queryset.values('influence_level').annotate(count=Count('id')).values_list('influence_level', 'count')),
            'opinion_leaders': queryset.filter(is_opinion_leader=True).count(),
            'avg_age': queryset.aggregate(Avg('age'))['age__avg'],
        })

    @action(detail=False, methods=['get'])
    def by_sentiment(self, request):
        """Get voters grouped by sentiment"""
        queryset = self.get_queryset()
        sentiment_data = {}

        for sentiment_choice in Voter.SENTIMENT_CHOICES:
            sentiment_key = sentiment_choice[0]
            voters = queryset.filter(sentiment=sentiment_key)
            sentiment_data[sentiment_key] = {
                'count': voters.count(),
                'percentage': round((voters.count() / queryset.count() * 100), 2) if queryset.count() > 0 else 0,
            }

        return Response(sentiment_data)

    @action(detail=True, methods=['post'])
    def mark_contacted(self, request, pk=None):
        """Mark voter as contacted"""
        voter = self.get_object()
        voter.last_contacted_at = timezone.now()
        voter.contact_frequency += 1
        voter.save()
        return Response({'status': 'marked as contacted', 'contact_frequency': voter.contact_frequency})


# ==================== VOTER INTERACTION VIEWSET ====================

class VoterInteractionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Voter Interactions

    GET /api/voter-interactions/ - List all interactions (role-filtered)
    POST /api/voter-interactions/ - Create interaction
    GET /api/voter-interactions/{id}/ - Get interaction details
    PUT/PATCH /api/voter-interactions/{id}/ - Update interaction
    DELETE /api/voter-interactions/{id}/ - Delete interaction
    """
    queryset = VoterInteraction.objects.select_related('voter', 'contacted_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['voter__first_name', 'voter__last_name', 'voter__voter_id', 'notes']
    filterset_fields = ['interaction_type', 'sentiment', 'follow_up_required', 'voter']
    ordering_fields = ['interaction_date', 'duration_minutes']
    ordering = ['-interaction_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return VoterInteractionListSerializer
        elif self.action == 'create':
            return VoterInteractionCreateSerializer
        return VoterInteractionDetailSerializer

    def get_queryset(self):
        """Role-based filtering of interactions"""
        user = self.request.user
        queryset = super().get_queryset()

        # Superadmin sees everything
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'superadmin'):
            return queryset

        # Get user profile
        if not hasattr(user, 'profile'):
            return queryset.filter(contacted_by=user)

        profile = user.profile

        # Admin (State level) - sees entire state
        if profile.role == 'admin' and profile.assigned_state:
            return queryset.filter(voter__state=profile.assigned_state)

        # Manager (District level) - sees their district
        if profile.role == 'manager' and profile.assigned_district:
            return queryset.filter(voter__district=profile.assigned_district)

        # Default: user sees only interactions they created
        return queryset.filter(contacted_by=user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get interaction statistics"""
        queryset = self.get_queryset()

        return Response({
            'total': queryset.count(),
            'by_type': dict(queryset.values('interaction_type').annotate(count=Count('id')).values_list('interaction_type', 'count')),
            'by_sentiment': dict(queryset.values('sentiment').annotate(count=Count('id')).values_list('sentiment', 'count')),
            'follow_ups_pending': queryset.filter(follow_up_required=True, follow_up_date__gte=timezone.now().date()).count(),
            'avg_duration': queryset.aggregate(Avg('duration_minutes'))['duration_minutes__avg'],
        })

    @action(detail=False, methods=['get'])
    def pending_followups(self, request):
        """Get interactions requiring follow-up"""
        queryset = self.get_queryset().filter(
            follow_up_required=True,
            follow_up_date__lte=timezone.now().date() + timedelta(days=7)
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ==================== CAMPAIGN VIEWSET ====================

class CampaignViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Campaigns

    GET /api/campaigns/ - List all campaigns
    POST /api/campaigns/ - Create campaign
    GET /api/campaigns/{id}/ - Get campaign details
    PUT/PATCH /api/campaigns/{id}/ - Update campaign
    DELETE /api/campaigns/{id}/ - Delete campaign
    """
    queryset = Campaign.objects.select_related('campaign_manager', 'target_constituency', 'created_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['campaign_name', 'target_audience']
    filterset_fields = ['campaign_type', 'status', 'campaign_manager']
    ordering_fields = ['start_date', 'created_at', 'budget']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        elif self.action == 'create':
            return CampaignCreateSerializer
        return CampaignDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get campaign statistics"""
        queryset = self.get_queryset()

        return Response({
            'total': queryset.count(),
            'active': queryset.filter(status='active').count(),
            'by_type': dict(queryset.values('campaign_type').annotate(count=Count('id')).values_list('campaign_type', 'count')),
            'by_status': dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'total_budget': queryset.aggregate(Sum('budget'))['budget__sum'],
            'total_spent': queryset.aggregate(Sum('spent_amount'))['spent_amount__sum'],
        })

    @action(detail=True, methods=['post'])
    def update_metrics(self, request, pk=None):
        """Update campaign metrics"""
        campaign = self.get_object()
        metrics = request.data.get('metrics', {})
        campaign.metrics.update(metrics)
        campaign.save()
        return Response({'status': 'metrics updated', 'metrics': campaign.metrics})

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        """Get campaign performance metrics"""
        campaign = self.get_object()

        return Response({
            'budget_utilization': round((float(campaign.spent_amount) / float(campaign.budget) * 100), 2) if campaign.budget > 0 else 0,
            'team_size': campaign.team_members.count(),
            'events_count': campaign.events.count(),
            'social_posts_count': campaign.social_posts.count(),
            'metrics': campaign.metrics,
        })


# ==================== SOCIAL MEDIA POST VIEWSET ====================

class SocialMediaPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Social Media Posts

    GET /api/social-posts/ - List all posts
    POST /api/social-posts/ - Create post
    GET /api/social-posts/{id}/ - Get post details
    PUT/PATCH /api/social-posts/{id}/ - Update post
    DELETE /api/social-posts/{id}/ - Delete post
    """
    queryset = SocialMediaPost.objects.select_related('campaign', 'posted_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['post_content']
    filterset_fields = ['platform', 'campaign', 'is_published', 'is_promoted']
    ordering_fields = ['posted_at', 'reach', 'engagement_count']
    ordering = ['-posted_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return SocialMediaPostListSerializer
        elif self.action == 'create':
            return SocialMediaPostCreateSerializer
        return SocialMediaPostDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get social media statistics"""
        queryset = self.get_queryset()

        return Response({
            'total_posts': queryset.count(),
            'published': queryset.filter(is_published=True).count(),
            'by_platform': dict(queryset.values('platform').annotate(count=Count('id')).values_list('platform', 'count')),
            'total_reach': queryset.aggregate(Sum('reach'))['reach__sum'],
            'total_engagement': queryset.aggregate(Sum('engagement_count'))['engagement_count__sum'],
            'total_likes': queryset.aggregate(Sum('likes'))['likes__sum'],
            'total_shares': queryset.aggregate(Sum('shares'))['shares__sum'],
            'avg_engagement_rate': queryset.aggregate(Avg('sentiment_score'))['sentiment_score__avg'],
        })

    @action(detail=False, methods=['get'])
    def top_performing(self, request):
        """Get top performing posts"""
        queryset = self.get_queryset().order_by('-engagement_count')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ==================== ALERT VIEWSET ====================

class AlertViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Alerts

    GET /api/alerts/ - List all alerts (role-filtered)
    POST /api/alerts/ - Create alert
    GET /api/alerts/{id}/ - Get alert details
    PUT/PATCH /api/alerts/{id}/ - Update alert
    DELETE /api/alerts/{id}/ - Delete alert
    """
    queryset = Alert.objects.select_related('created_by', 'constituency', 'district').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'message']
    filterset_fields = ['alert_type', 'priority', 'is_read', 'target_role']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return AlertListSerializer
        elif self.action == 'create':
            return AlertCreateSerializer
        return AlertDetailSerializer

    def get_queryset(self):
        """Filter alerts by target role or target users"""
        user = self.request.user
        queryset = super().get_queryset()

        # Superadmin sees all alerts
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'superadmin'):
            return queryset

        # Filter by target role or target users
        if hasattr(user, 'profile'):
            queryset = queryset.filter(
                Q(target_role=user.profile.role) |
                Q(target_users=user) |
                Q(created_by=user)
            ).distinct()

        return queryset

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark alert as read"""
        alert = self.get_object()
        alert.is_read = True
        alert.read_at = timezone.now()
        alert.save()
        return Response({'status': 'marked as read'})

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread alerts"""
        queryset = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ==================== EVENT VIEWSET ====================

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Events

    GET /api/events/ - List all events
    POST /api/events/ - Create event
    GET /api/events/{id}/ - Get event details
    PUT/PATCH /api/events/{id}/ - Update event
    DELETE /api/events/{id}/ - Delete event
    """
    queryset = Event.objects.select_related('organizer', 'campaign', 'constituency').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['event_name', 'location', 'notes']
    filterset_fields = ['event_type', 'status', 'organizer', 'campaign']
    ordering_fields = ['start_datetime', 'created_at']
    ordering = ['-start_datetime']

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        elif self.action == 'create':
            return EventCreateSerializer
        return EventDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get event statistics"""
        queryset = self.get_queryset()

        return Response({
            'total': queryset.count(),
            'by_type': dict(queryset.values('event_type').annotate(count=Count('id')).values_list('event_type', 'count')),
            'by_status': dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'total_budget': queryset.aggregate(Sum('budget'))['budget__sum'],
            'total_expenses': queryset.aggregate(Sum('expenses'))['expenses__sum'],
            'total_attendance': queryset.aggregate(Sum('actual_attendance'))['actual_attendance__sum'],
        })

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming events"""
        queryset = self.get_queryset().filter(
            start_datetime__gte=timezone.now(),
            status='planned'
        ).order_by('start_datetime')[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark event as completed and record attendance"""
        event = self.get_object()
        event.status = 'completed'
        event.actual_attendance = request.data.get('actual_attendance', 0)
        event.save()
        return Response({'status': 'marked as completed'})


# ==================== VOLUNTEER VIEWSET ====================

class VolunteerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Volunteers

    GET /api/volunteers/ - List all volunteers
    POST /api/volunteers/ - Create volunteer profile
    GET /api/volunteers/{id}/ - Get volunteer details
    PUT/PATCH /api/volunteers/{id}/ - Update volunteer
    DELETE /api/volunteers/{id}/ - Delete volunteer
    """
    queryset = VolunteerProfile.objects.select_related('user', 'assigned_constituency').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['volunteer_id', 'user__first_name', 'user__last_name', 'user__email']
    filterset_fields = ['is_active', 'assigned_constituency', 'assigned_ward']
    ordering_fields = ['joined_at', 'tasks_completed', 'rating']
    ordering = ['-joined_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return VolunteerListSerializer
        elif self.action == 'create':
            return VolunteerCreateSerializer
        return VolunteerDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get volunteer statistics"""
        queryset = self.get_queryset()

        return Response({
            'total': queryset.count(),
            'active': queryset.filter(is_active=True).count(),
            'total_hours': queryset.aggregate(Sum('hours_contributed'))['hours_contributed__sum'],
            'total_tasks': queryset.aggregate(Sum('tasks_completed'))['tasks_completed__sum'],
            'avg_rating': queryset.aggregate(Avg('rating'))['rating__avg'],
        })

    @action(detail=True, methods=['post'])
    def log_hours(self, request, pk=None):
        """Log volunteer hours"""
        volunteer = self.get_object()
        hours = float(request.data.get('hours', 0))
        volunteer.hours_contributed += hours
        volunteer.save()
        return Response({'status': 'hours logged', 'total_hours': float(volunteer.hours_contributed)})


# ==================== EXPENSE VIEWSET ====================

class ExpenseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Expenses

    GET /api/expenses/ - List all expenses
    POST /api/expenses/ - Create expense
    GET /api/expenses/{id}/ - Get expense details
    PUT/PATCH /api/expenses/{id}/ - Update expense
    DELETE /api/expenses/{id}/ - Delete expense
    """
    queryset = Expense.objects.select_related('campaign', 'event', 'created_by', 'approved_by').all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description']
    filterset_fields = ['expense_type', 'status', 'campaign', 'event']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return ExpenseListSerializer
        elif self.action == 'create':
            return ExpenseCreateSerializer
        return ExpenseDetailSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get expense statistics"""
        queryset = self.get_queryset()

        return Response({
            'total_expenses': queryset.count(),
            'by_type': dict(queryset.values('expense_type').annotate(count=Count('id')).values_list('expense_type', 'count')),
            'by_status': dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count')),
            'total_amount': queryset.aggregate(Sum('amount'))['amount__sum'],
            'pending_amount': queryset.filter(status='pending').aggregate(Sum('amount'))['amount__sum'],
            'approved_amount': queryset.filter(status='approved').aggregate(Sum('amount'))['amount__sum'],
        })

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve expense"""
        expense = self.get_object()
        expense.status = 'approved'
        expense.approved_by = request.user
        expense.save()
        return Response({'status': 'expense approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject expense"""
        expense = self.get_object()
        expense.status = 'rejected'
        expense.approved_by = request.user
        expense.save()
        return Response({'status': 'expense rejected'})

    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get expenses pending approval"""
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
