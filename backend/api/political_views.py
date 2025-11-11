"""
API Views for Political Platform
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta

from .models import (
    State, District, Constituency, PollingBooth, PoliticalParty, IssueCategory,
    VoterSegment, DirectFeedback, FieldReport, SentimentData, BoothAgent
)
from .political_serializers import (
    StateSerializer, DistrictSerializer, ConstituencySerializer, ConstituencyListSerializer,
    PollingBoothSerializer, PollingBoothListSerializer,
    PoliticalPartySerializer, IssueCategorySerializer, VoterSegmentSerializer,
    DirectFeedbackSerializer, DirectFeedbackCreateSerializer, DirectFeedbackListSerializer,
    FieldReportSerializer, FieldReportListSerializer,
    SentimentDataSerializer, BoothAgentSerializer
)


# =====================================================
# MASTER DATA VIEWS (Read-Only Reference Data)
# =====================================================

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for States
    GET /api/states/ - List all states
    GET /api/states/{id}/ - Get state details
    """
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [AllowAny]


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Districts
    GET /api/districts/ - List all districts
    GET /api/districts/{id}/ - Get district details
    Filter by: ?state=TN
    """
    queryset = District.objects.select_related('state').all()
    serializer_class = DistrictSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']
    pagination_class = None  # Disable pagination - return all districts

    def get_queryset(self):
        queryset = super().get_queryset()
        state_code = self.request.query_params.get('state', None)
        if state_code:
            queryset = queryset.filter(state__code=state_code)
        return queryset


class ConstituencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Constituencies (234 Assembly + Parliamentary)
    GET /api/constituencies/ - List all (use list serializer for performance)
    GET /api/constituencies/{id}/ - Get constituency details
    Filter by: ?state=TN&type=assembly&district=1
    """
    queryset = Constituency.objects.select_related('state', 'district').all()
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']
    pagination_class = None  # Disable pagination - return all constituencies

    def get_serializer_class(self):
        if self.action == 'list':
            return ConstituencyListSerializer
        return ConstituencySerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by state
        state_code = self.request.query_params.get('state', None)
        if state_code:
            queryset = queryset.filter(state__code=state_code)

        # Filter by type
        const_type = self.request.query_params.get('type', None)
        if const_type:
            queryset = queryset.filter(constituency_type=const_type)

        # Filter by district
        district_id = self.request.query_params.get('district', None)
        if district_id:
            queryset = queryset.filter(district_id=district_id)

        return queryset


class PoliticalPartyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Political Parties
    GET /api/political-parties/ - List all parties
    """
    queryset = PoliticalParty.objects.all()
    serializer_class = PoliticalPartySerializer
    permission_classes = [AllowAny]


class IssueCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Issue Categories (TVK's priorities)
    GET /api/issue-categories/ - List all issues
    """
    queryset = IssueCategory.objects.filter(is_active=True)
    serializer_class = IssueCategorySerializer
    permission_classes = [AllowAny]


class VoterSegmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Voter Segments (Fishermen, Farmers, etc.)
    GET /api/voter-segments/ - List all segments
    """
    queryset = VoterSegment.objects.filter(is_active=True)
    serializer_class = VoterSegmentSerializer
    permission_classes = [AllowAny]


class PollingBoothViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Polling Booths
    GET /api/polling-booths/ - List all booths
    GET /api/polling-booths/{id}/ - Get booth details
    Filter by: ?constituency=<name>&district=<name>&state=TN
    """
    queryset = PollingBooth.objects.select_related('state', 'district', 'constituency').filter(is_active=True)
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'booth_number', 'area', 'building_name']
    pagination_class = None  # Disable pagination - return all booths

    def get_serializer_class(self):
        if self.action == 'list':
            return PollingBoothListSerializer
        return PollingBoothSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by state
        state_code = self.request.query_params.get('state', None)
        if state_code:
            queryset = queryset.filter(state__code=state_code)

        # Filter by district (by name)
        district_name = self.request.query_params.get('district', None)
        if district_name:
            queryset = queryset.filter(district__name=district_name)

        # Filter by constituency (by name)
        constituency_name = self.request.query_params.get('constituency', None)
        if constituency_name:
            queryset = queryset.filter(constituency__name=constituency_name)

        return queryset


# =====================================================
# FEEDBACK COLLECTION VIEWS
# =====================================================

class DirectFeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Direct Citizen Feedback

    POST /api/feedback/ - Submit feedback (public, no auth required)
    GET /api/feedback/ - List feedback (auth required, role-filtered)
    GET /api/feedback/{id}/ - Get feedback details
    PATCH /api/feedback/{id}/ - Update feedback status

    Role-based filtering:
    - Admin3 (Booth Agent): Only their ward/booth
    - Admin2 (District Head): Their entire district
    - Admin1 (State Level): Entire state
    - Superadmin: Everything
    """
    serializer_class = DirectFeedbackSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['citizen_name', 'ward', 'message_text']
    ordering_fields = ['submitted_at', 'status', 'ai_urgency']
    ordering = ['-submitted_at']

    def get_permissions(self):
        # Allow public submission (POST) without authentication
        if self.action == 'create':
            return [AllowAny()]
        # All other actions require authentication
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return DirectFeedbackCreateSerializer
        elif self.action == 'list':
            return DirectFeedbackListSerializer
        return DirectFeedbackSerializer

    def get_queryset(self):
        """
        Role-based filtering of feedback
        """
        user = self.request.user
        queryset = DirectFeedback.objects.select_related(
            'state', 'district', 'constituency', 'issue_category', 'voter_segment'
        ).all()

        # Superadmin sees everything
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'superadmin'):
            return queryset

        # Get user profile
        if not hasattr(user, 'profile'):
            return queryset.none()

        profile = user.profile

        # Admin1 (State level) - sees entire state
        if profile.role == 'admin' and profile.assigned_state:
            return queryset.filter(state=profile.assigned_state)

        # Admin2 (District level) - sees their district
        if profile.role == 'manager' and profile.assigned_district:
            return queryset.filter(district=profile.assigned_district)

        # Admin3 (Booth Agent) - sees their wards/booths
        if hasattr(user, 'booth_agent_profile'):
            agent = user.booth_agent_profile
            return queryset.filter(
                Q(ward__in=agent.assigned_wards) |
                Q(booth_number__in=agent.assigned_booths)
            )

        # Default: user sees only feedback assigned to them
        return queryset.filter(assigned_to=user)

    def perform_create(self, serializer):
        """
        Save feedback submission
        """
        serializer.save()

    @action(detail=True, methods=['post'])
    def mark_reviewed(self, request, pk=None):
        """
        Mark feedback as reviewed
        POST /api/feedback/{id}/mark_reviewed/
        """
        feedback = self.get_object()
        feedback.status = 'reviewed'
        feedback.reviewed_by = request.user
        feedback.reviewed_at = timezone.now()
        feedback.save()
        return Response({'status': 'marked as reviewed'})

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """
        Escalate feedback to higher level
        POST /api/feedback/{id}/escalate/
        """
        feedback = self.get_object()
        feedback.status = 'escalated'
        feedback.save()
        return Response({'status': 'escalated'})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get feedback statistics
        GET /api/feedback/stats/
        """
        queryset = self.get_queryset()

        total = queryset.count()
        by_status = dict(queryset.values('status').annotate(count=Count('id')).values_list('status', 'count'))
        by_urgency = dict(queryset.values('ai_urgency').annotate(count=Count('id')).values_list('ai_urgency', 'count'))

        return Response({
            'total': total,
            'by_status': by_status,
            'by_urgency': by_urgency,
            'pending_count': by_status.get('pending', 0),
            'escalated_count': by_status.get('escalated', 0),
        })


class FieldReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Field Reports (Party Worker Reports)

    POST /api/field-reports/ - Submit report (auto-assigns to logged-in user)
    GET /api/field-reports/ - List reports (role-filtered)
    GET /api/field-reports/{id}/ - Get report details
    PATCH /api/field-reports/{id}/ - Update report
    """
    serializer_class = FieldReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ward', 'booth_number', 'title', 'notes']
    ordering_fields = ['timestamp', 'report_date', 'verification_status']
    ordering = ['-timestamp']

    def get_serializer_class(self):
        if self.action == 'list':
            return FieldReportListSerializer
        return FieldReportSerializer

    def get_queryset(self):
        """
        Role-based filtering of field reports
        """
        user = self.request.user
        queryset = FieldReport.objects.select_related(
            'volunteer', 'state', 'district', 'constituency', 'competitor_party'
        ).prefetch_related('key_issues', 'voter_segments_met').all()

        # Superadmin sees everything
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'superadmin'):
            return queryset

        # Get user profile
        if not hasattr(user, 'profile'):
            return queryset.filter(volunteer=user)

        profile = user.profile

        # Admin1 (State level) - sees entire state
        if profile.role == 'admin' and profile.assigned_state:
            return queryset.filter(state=profile.assigned_state)

        # Admin2 (District level) - sees their district
        if profile.role == 'manager' and profile.assigned_district:
            return queryset.filter(district=profile.assigned_district)

        # Admin3 or regular user - sees only their own reports
        return queryset.filter(volunteer=user)

    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Verify a field report
        POST /api/field-reports/{id}/verify/
        Body: {"verification_notes": "Looks good"}
        """
        report = self.get_object()
        report.verification_status = 'verified'
        report.verified_by = request.user
        report.verified_at = timezone.now()
        report.verification_notes = request.data.get('verification_notes', '')
        report.save()
        return Response({'status': 'verified'})

    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """
        Get current user's reports
        GET /api/field-reports/my_reports/
        """
        queryset = self.get_queryset().filter(volunteer=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# =====================================================
# ANALYTICS VIEWS
# =====================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def constituency_analytics(request, code):
    """
    Get analytics for a specific constituency
    GET /api/analytics/constituency/{code}/
    """
    try:
        constituency = Constituency.objects.get(code=code)
    except Constituency.DoesNotExist:
        return Response({'error': 'Constituency not found'}, status=404)

    # Get all feedback for this constituency
    feedback = DirectFeedback.objects.filter(constituency=constituency)

    # Calculate statistics
    total_feedback = feedback.count()
    by_status = dict(feedback.values('status').annotate(count=Count('id')).values_list('status', 'count'))
    by_urgency = dict(feedback.values('ai_urgency').annotate(count=Count('id')).values_list('ai_urgency', 'count'))

    # Top issues
    top_issues = feedback.values('issue_category__name').annotate(
        count=Count('id'),
        avg_sentiment=Avg('ai_sentiment_score')
    ).order_by('-count')[:5]

    # Voter segments
    segments = feedback.values('voter_segment__name').annotate(
        count=Count('id'),
        avg_sentiment=Avg('ai_sentiment_score')
    ).order_by('-count')[:5]

    return Response({
        'constituency': {
            'code': constituency.code,
            'name': constituency.name,
            'number': constituency.number,
            'district': constituency.district.name if constituency.district else None,
        },
        'total_feedback': total_feedback,
        'by_status': by_status,
        'by_urgency': by_urgency,
        'top_issues': list(top_issues),
        'voter_segments': list(segments),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def district_analytics(request, district_id):
    """
    Get analytics for a specific district
    GET /api/analytics/district/{district_id}/
    """
    try:
        district = District.objects.get(id=district_id)
    except District.DoesNotExist:
        return Response({'error': 'District not found'}, status=404)

    # Get all feedback for this district
    feedback = DirectFeedback.objects.filter(district=district)

    # Calculate statistics
    total_feedback = feedback.count()
    by_status = dict(feedback.values('status').annotate(count=Count('id')).values_list('status', 'count'))

    # Top issues
    top_issues = feedback.values('issue_category__name').annotate(
        count=Count('id'),
        avg_sentiment=Avg('ai_sentiment_score')
    ).order_by('-count')[:10]

    # Constituency breakdown
    by_constituency = feedback.values('constituency__name', 'constituency__code').annotate(
        count=Count('id'),
        avg_sentiment=Avg('ai_sentiment_score')
    ).order_by('-count')[:10]

    return Response({
        'district': {
            'id': district.id,
            'name': district.name,
            'code': district.code,
            'state': district.state.code,
        },
        'total_feedback': total_feedback,
        'by_status': by_status,
        'top_issues': list(top_issues),
        'by_constituency': list(by_constituency),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def state_analytics(request, state_code):
    """
    Get analytics for entire state
    GET /api/analytics/state/{state_code}/
    """
    try:
        state = State.objects.get(code=state_code)
    except State.DoesNotExist:
        return Response({'error': 'State not found'}, status=404)

    # Get all feedback for this state
    feedback = DirectFeedback.objects.filter(state=state)

    # Calculate statistics
    total_feedback = feedback.count()
    by_status = dict(feedback.values('status').annotate(count=Count('id')).values_list('status', 'count'))

    # Top issues
    top_issues = feedback.values('issue_category__name').annotate(
        count=Count('id'),
        avg_sentiment=Avg('ai_sentiment_score')
    ).order_by('-count')[:10]

    # District breakdown
    by_district = feedback.values('district__name', 'district__id').annotate(
        count=Count('id'),
        avg_sentiment=Avg('ai_sentiment_score')
    ).order_by('-count')[:20]

    # Voter segments
    by_segment = feedback.values('voter_segment__name').annotate(
        count=Count('id'),
        avg_sentiment=Avg('ai_sentiment_score')
    ).order_by('-count')[:10]

    return Response({
        'state': {
            'code': state.code,
            'name': state.name,
            'total_districts': state.total_districts,
            'total_constituencies': state.total_constituencies,
        },
        'total_feedback': total_feedback,
        'by_status': by_status,
        'top_issues': list(top_issues),
        'by_district': list(by_district),
        'by_segment': list(by_segment),
    })


@api_view(['GET'])
def dashboard_overview(request):
    """
    Get overall dashboard statistics
    GET /api/analytics/overview/
    """
    # Recent feedback (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_feedback = DirectFeedback.objects.filter(submitted_at__gte=week_ago)

    return Response({
        'total_feedback': DirectFeedback.objects.count(),
        'total_field_reports': FieldReport.objects.count(),
        'pending_feedback': DirectFeedback.objects.filter(status='pending').count(),
        'escalated_feedback': DirectFeedback.objects.filter(status='escalated').count(),
        'recent_feedback_count': recent_feedback.count(),
        'total_constituencies': Constituency.objects.count(),
        'total_districts': District.objects.count(),
    })
