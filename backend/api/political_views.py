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
from .permissions.role_permissions import ReadOnlyOrAdmin, IsAdminOrAbove, IsUser, IsAnalystOrAbove, IsManagerOrAbove


# =====================================================
# MASTER DATA VIEWS (Read-Only Reference Data)
# =====================================================

class StateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for States
    GET /api/states/ - List all states
    GET /api/states/{id}/ - Get state details

    Permissions: Read-only, authenticated users only
    """
    queryset = State.objects.all()
    serializer_class = StateSerializer
    permission_classes = [IsAuthenticated]


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Districts
    GET /api/districts/ - List all districts
    GET /api/districts/{id}/ - Get district details
    Filter by: ?state=TN

    Permissions: Read-only, authenticated users only
    """
    queryset = District.objects.select_related('state').all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated]
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

    Permissions: Read-only, authenticated users only
    """
    queryset = Constituency.objects.select_related('state', 'district').all()
    permission_classes = [IsAuthenticated]
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

    Permissions: Read-only, authenticated users only
    """
    queryset = PoliticalParty.objects.all()
    serializer_class = PoliticalPartySerializer
    permission_classes = [IsAuthenticated]


class IssueCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Issue Categories (TVK's priorities)
    GET /api/issue-categories/ - List all issues

    Permissions: Read-only, authenticated users only
    """
    queryset = IssueCategory.objects.filter(is_active=True)
    serializer_class = IssueCategorySerializer
    permission_classes = [IsAuthenticated]


class VoterSegmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Voter Segments (Fishermen, Farmers, etc.)
    GET /api/voter-segments/ - List all segments

    Permissions: Read-only, authenticated users only
    """
    queryset = VoterSegment.objects.filter(is_active=True)
    serializer_class = VoterSegmentSerializer
    permission_classes = [IsAuthenticated]


class PollingBoothViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Polling Booths
    GET /api/polling-booths/ - List all booths
    GET /api/polling-booths/{id}/ - Get booth details
    Filter by: ?constituency=<name>&district=<name>&state=TN

    Permissions: Read-only, authenticated users only
    """
    queryset = PollingBooth.objects.select_related('state', 'district', 'constituency').filter(is_active=True)
    permission_classes = [IsAuthenticated]
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

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def mark_reviewed(self, request, pk=None):
        """
        Mark feedback as reviewed
        POST /api/feedback/{id}/mark_reviewed/

        Permissions: Manager and above
        """
        feedback = self.get_object()
        feedback.status = 'reviewed'
        feedback.reviewed_by = request.user
        feedback.reviewed_at = timezone.now()
        feedback.save()
        return Response({'status': 'marked as reviewed'})

    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrAbove])
    def escalate(self, request, pk=None):
        """
        Escalate feedback to higher level
        POST /api/feedback/{id}/escalate/

        Permissions: Manager and above
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
    API endpoint for Field Reports with role-based access control

    POST /api/field-reports/ - Submit new report (Volunteer+)
    GET /api/field-reports/ - List reports (User+, filtered by role)
    GET /api/field-reports/{id}/ - Get report details (User+)
    PATCH /api/field-reports/{id}/ - Update report (Owner or Manager+)
    DELETE /api/field-reports/{id}/ - Delete report (Admin+)
    POST /api/field-reports/{id}/review/ - Review/approve report (Manager+)
    GET /api/field-reports/stats/ - Get statistics (Analyst+)
    """
    serializer_class = FieldReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'ward']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return FieldReportListSerializer
        return FieldReportSerializer

    def get_permissions(self):
        """
        Apply different permissions based on action
        """
        from api.decorators.permissions import (
            CanSubmitFieldReports, CanViewFieldReports, CanReviewFieldReports,
            CanDeleteFieldReports, CanViewStatistics
        )

        if self.action == 'create':
            return [CanSubmitFieldReports()]
        elif self.action in ['list', 'retrieve']:
            return [CanViewFieldReports()]
        elif self.action == 'review':
            return [CanReviewFieldReports()]
        elif self.action == 'destroy':
            return [CanDeleteFieldReports()]
        elif self.action == 'stats':
            return [CanViewStatistics()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        """
        Role-based filtering of field reports with data isolation
        - Volunteers/Users: Only see their own reports
        - Analysts: See reports in their constituency
        - Managers: See reports in their district
        - Admins: See reports in their state
        - Superadmins: See all reports
        """
        user = self.request.user
        queryset = FieldReport.objects.select_related(
            'submitted_by', 'submitted_by__profile', 'state', 'district', 'constituency',
            'reviewed_by'
        ).all()

        # Superadmin sees everything
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'superadmin'):
            queryset = self._apply_filters(queryset)
            return queryset

        # Get user profile
        if not hasattr(user, 'profile'):
            return queryset.filter(submitted_by=user)

        profile = user.profile

        # Admin - sees reports in their state
        if profile.role == 'admin':
            if profile.assigned_state:
                queryset = queryset.filter(state=profile.assigned_state)
            queryset = self._apply_filters(queryset)
            return queryset

        # Manager - sees reports in their district
        if profile.role == 'manager':
            if profile.assigned_district:
                queryset = queryset.filter(district=profile.assigned_district)
            queryset = self._apply_filters(queryset)
            return queryset

        # Analyst - sees reports in their constituency
        if profile.role == 'analyst':
            if profile.constituency:
                queryset = queryset.filter(constituency__name=profile.constituency)
            queryset = self._apply_filters(queryset)
            return queryset

        # Volunteers and Users - see only their own reports
        queryset = queryset.filter(submitted_by=user)
        queryset = self._apply_filters(queryset)
        return queryset

    def _apply_filters(self, queryset):
        """Apply query parameter filters"""
        # Filter by report type
        report_type = self.request.query_params.get('report_type')
        if report_type:
            queryset = queryset.filter(report_type=report_type)

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by voter sentiment
        sentiment = self.request.query_params.get('voter_sentiment')
        if sentiment:
            queryset = queryset.filter(voter_sentiment=sentiment)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Filter by district
        district_id = self.request.query_params.get('district')
        if district_id:
            queryset = queryset.filter(district_id=district_id)

        # Filter by constituency
        constituency_id = self.request.query_params.get('constituency')
        if constituency_id:
            queryset = queryset.filter(constituency_id=constituency_id)

        return queryset

    def perform_create(self, serializer):
        """Save field report with submitted_by set to current user"""
        serializer.save(submitted_by=self.request.user)

    def perform_update(self, serializer):
        """Update field report (only owner or manager+ can update)"""
        instance = self.get_object()
        user = self.request.user

        # Check if user can update
        if instance.submitted_by != user:
            # Only managers and above can update others' reports
            if hasattr(user, 'profile'):
                if user.profile.role not in ['manager', 'admin', 'superadmin']:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("You can only update your own reports")

        serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def review(self, request, pk=None):
        """
        Review and approve/reject a field report (Manager+ only)
        POST /api/field-reports/{id}/review/

        Body:
        {
            "status": "approved",  // or "rejected"
            "review_notes": "Verified with local sources"
        }
        """
        from api.decorators.permissions import CanReviewFieldReports

        # Check permission
        if not CanReviewFieldReports().has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to review reports'},
                status=status.HTTP_403_FORBIDDEN
            )

        report = self.get_object()
        new_status = request.data.get('status')
        review_notes = request.data.get('review_notes', '')

        # Validate status
        if new_status not in ['approved', 'rejected', 'reviewed']:
            return Response(
                {'error': 'Invalid status. Must be "approved", "rejected", or "reviewed"'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update report
        report.status = new_status
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.review_notes = review_notes
        report.save()

        serializer = self.get_serializer(report)
        return Response({
            'message': f'Report {new_status} successfully',
            'report': serializer.data
        })

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """
        Get field report statistics (Analyst+ only)
        GET /api/field-reports/stats/

        Returns aggregated statistics based on user's access level
        """
        from api.decorators.permissions import CanViewStatistics

        # Check permission
        if not CanViewStatistics().has_permission(request, self):
            return Response(
                {'error': 'You do not have permission to view statistics'},
                status=status.HTTP_403_FORBIDDEN
            )

        queryset = self.get_queryset()

        # Total count
        total = queryset.count()

        # Count by report type
        by_type = dict(
            queryset.values('report_type')
            .annotate(count=Count('id'))
            .values_list('report_type', 'count')
        )

        # Count by status
        by_status = dict(
            queryset.values('status')
            .annotate(count=Count('id'))
            .values_list('status', 'count')
        )

        # Count by priority
        by_priority = dict(
            queryset.values('priority')
            .annotate(count=Count('id'))
            .values_list('priority', 'count')
        )

        # Count by voter sentiment
        by_sentiment = dict(
            queryset.values('voter_sentiment')
            .annotate(count=Count('id'))
            .values_list('voter_sentiment', 'count')
        )

        # Recent activity (last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_count = queryset.filter(created_at__gte=seven_days_ago).count()

        # Pending reports
        pending_count = queryset.filter(status='pending').count()

        # Urgent reports
        urgent_count = queryset.filter(priority='urgent').count()

        return Response({
            'total': total,
            'by_type': by_type,
            'by_status': by_status,
            'by_priority': by_priority,
            'by_sentiment': by_sentiment,
            'recent_count': recent_count,
            'pending_count': pending_count,
            'urgent_count': urgent_count,
            'last_updated': timezone.now()
        })

    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        """
        Get current user's reports
        GET /api/field-reports/my_reports/
        """
        queryset = self.get_queryset().filter(submitted_by=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def upload_attachment(self, request, pk=None):
        """
        Upload attachment to a field report
        POST /api/field-reports/{id}/upload_attachment/

        Supports: multipart/form-data with 'file' field
        Multiple files can be uploaded sequentially
        """
        report = self.get_object()

        # Check if user can upload (owner or manager+)
        if report.submitted_by != request.user:
            if hasattr(request.user, 'profile'):
                if request.user.profile.role not in ['manager', 'admin', 'superadmin']:
                    return Response(
                        {'error': 'You can only upload attachments to your own reports'},
                        status=status.HTTP_403_FORBIDDEN
                    )

        # Get uploaded file
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            return Response(
                {'error': 'File size exceeds 10MB limit'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate file type
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif', 'image/webp',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'video/mp4', 'video/quicktime'
        ]
        if uploaded_file.content_type not in allowed_types:
            return Response(
                {'error': f'File type {uploaded_file.content_type} not allowed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save file to media directory
        import os
        from django.conf import settings
        from django.core.files.storage import default_storage

        # Create unique filename
        import uuid
        file_extension = os.path.splitext(uploaded_file.name)[1]
        unique_filename = f"field_reports/{report.id}/{uuid.uuid4()}{file_extension}"

        # Save file
        file_path = default_storage.save(unique_filename, uploaded_file)
        file_url = request.build_absolute_uri(settings.MEDIA_URL + file_path)

        # Add to report attachments
        if not report.attachments:
            report.attachments = []

        report.attachments.append({
            'url': file_url,
            'filename': uploaded_file.name,
            'size': uploaded_file.size,
            'content_type': uploaded_file.content_type,
            'uploaded_at': timezone.now().isoformat(),
            'uploaded_by': request.user.username
        })
        report.save()

        return Response({
            'message': 'File uploaded successfully',
            'file': {
                'url': file_url,
                'filename': uploaded_file.name,
                'size': uploaded_file.size
            }
        })


# =====================================================
# ANALYTICS VIEWS
# =====================================================

@api_view(['GET'])
@permission_classes([IsAnalystOrAbove])
def constituency_analytics(request, code):
    """
    Get analytics for a specific constituency
    GET /api/analytics/constituency/{code}/

    Permissions: Analyst and above
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
@permission_classes([IsAnalystOrAbove])
def district_analytics(request, district_id):
    """
    Get analytics for a specific district
    GET /api/analytics/district/{district_id}/

    Permissions: Analyst and above
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
@permission_classes([IsAnalystOrAbove])
def state_analytics(request, state_code):
    """
    Get analytics for entire state
    GET /api/analytics/state/{state_code}/

    Permissions: Analyst and above
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
@permission_classes([IsAnalystOrAbove])
def dashboard_overview(request):
    """
    Get overall dashboard statistics
    GET /api/analytics/overview/

    Permissions: Analyst and above
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
