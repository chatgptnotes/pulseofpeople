"""
Audit Log Views

This module provides API endpoints for viewing audit logs.
Only Superadmin users can view all audit logs.
Admin users can only view logs for their organization.
"""

import csv
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from api.models import AuditLog
from api.serializers import AuditLogSerializer, AuditLogListSerializer
from api.permissions.role_permissions import IsSuperAdmin


class AuditLogPagination(PageNumberPagination):
    """Custom pagination for audit logs"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for audit logs (read-only).

    Audit logs are immutable - they cannot be created, updated, or deleted through the API.

    Permissions:
    - Superadmin: Can view all audit logs
    - Admin: Can view audit logs for their organization (future implementation)
    - Other roles: No access

    Endpoints:
    - GET /api/audit-logs/ - List audit logs with filtering
    - GET /api/audit-logs/{id}/ - Retrieve a single audit log
    - GET /api/audit-logs/export/ - Export logs to CSV
    - GET /api/audit-logs/stats/ - Get audit log statistics
    """

    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = AuditLogPagination

    def get_queryset(self):
        """
        Get queryset with optional filtering.

        Query parameters:
        - user_id: Filter by user ID
        - username: Filter by username (partial match)
        - action: Filter by action type
        - resource_type: Filter by target model
        - resource_id: Filter by target ID
        - date_from: Filter logs from this date (ISO format)
        - date_to: Filter logs to this date (ISO format)
        - search: Search across multiple fields
        """
        queryset = AuditLog.objects.select_related('user').all()

        # Filter by user ID
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        # Filter by username (partial match)
        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.filter(user__username__icontains=username)

        # Filter by action type
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)

        # Filter by resource type
        resource_type = self.request.query_params.get('resource_type')
        if resource_type:
            queryset = queryset.filter(target_model=resource_type)

        # Filter by resource ID
        resource_id = self.request.query_params.get('resource_id')
        if resource_id:
            queryset = queryset.filter(target_id=resource_id)

        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            try:
                date_from = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__gte=date_from)
            except ValueError:
                pass  # Invalid date format, ignore

        date_to = self.request.query_params.get('date_to')
        if date_to:
            try:
                date_to = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                queryset = queryset.filter(timestamp__lte=date_to)
            except ValueError:
                pass  # Invalid date format, ignore

        # Search across multiple fields
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(user__username__icontains=search) |
                Q(user__email__icontains=search) |
                Q(action__icontains=search) |
                Q(target_model__icontains=search) |
                Q(target_id__icontains=search)
            )

        return queryset.order_by('-timestamp')

    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return AuditLogListSerializer
        return AuditLogSerializer

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export audit logs to CSV.

        Applies the same filters as the list view.

        GET /api/audit-logs/export/
        """
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Limit export to 10,000 records
        queryset = queryset[:10000]

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        response['Content-Disposition'] = f'attachment; filename="audit_logs_{timestamp}.csv"'

        writer = csv.writer(response)

        # Write header
        writer.writerow([
            'ID', 'Timestamp', 'User ID', 'Username', 'Email', 'Action',
            'Resource Type', 'Resource ID', 'IP Address', 'User Agent',
            'Changes'
        ])

        # Write data rows
        for log in queryset:
            writer.writerow([
                log.id,
                log.timestamp.isoformat(),
                log.user_id if log.user else '',
                log.user.username if log.user else 'Anonymous',
                log.user.email if log.user else '',
                log.action,
                log.target_model,
                log.target_id,
                log.ip_address or '',
                log.user_agent[:100] if log.user_agent else '',  # Truncate user agent
                str(log.changes) if log.changes else ''
            ])

        return response

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get audit log statistics.

        Returns:
        - Total log count
        - Logs by action type
        - Logs by resource type
        - Recent activity (last 24 hours, 7 days, 30 days)
        - Top users by activity

        GET /api/audit-logs/stats/
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Total count
        total_count = queryset.count()

        # Count by action type
        action_counts = {}
        for action_type, _ in AuditLog.ACTION_TYPES:
            count = queryset.filter(action=action_type).count()
            if count > 0:
                action_counts[action_type] = count

        # Count by resource type
        resource_counts = {}
        resource_types = queryset.values_list('target_model', flat=True).distinct()
        for resource_type in resource_types:
            if resource_type:
                count = queryset.filter(target_model=resource_type).count()
                resource_counts[resource_type] = count

        # Recent activity
        now = timezone.now()
        last_24h = queryset.filter(timestamp__gte=now - timedelta(hours=24)).count()
        last_7d = queryset.filter(timestamp__gte=now - timedelta(days=7)).count()
        last_30d = queryset.filter(timestamp__gte=now - timedelta(days=30)).count()

        # Top users by activity
        top_users = []
        user_ids = queryset.values_list('user_id', flat=True).distinct()
        user_activity = []
        for user_id in user_ids:
            if user_id:
                count = queryset.filter(user_id=user_id).count()
                user = queryset.filter(user_id=user_id).first().user
                if user:
                    user_activity.append({
                        'user_id': user_id,
                        'username': user.username,
                        'email': user.email,
                        'activity_count': count
                    })

        # Sort by activity count and take top 10
        top_users = sorted(user_activity, key=lambda x: x['activity_count'], reverse=True)[:10]

        return Response({
            'total_logs': total_count,
            'action_counts': action_counts,
            'resource_counts': resource_counts,
            'recent_activity': {
                'last_24_hours': last_24h,
                'last_7_days': last_7d,
                'last_30_days': last_30d
            },
            'top_users': top_users
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent audit logs (last 100).

        GET /api/audit-logs/recent/
        """
        queryset = self.get_queryset()[:100]
        serializer = AuditLogListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """
        Get audit logs for a specific user.

        Query parameters:
        - user_id: User ID (required)

        GET /api/audit-logs/user-activity/?user_id=123
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = AuditLog.objects.filter(user_id=user_id).order_by('-timestamp')

        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AuditLogListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AuditLogListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resource_history(self, request):
        """
        Get audit logs for a specific resource.

        Query parameters:
        - resource_type: Resource type (required)
        - resource_id: Resource ID (required)

        GET /api/audit-logs/resource-history/?resource_type=User&resource_id=123
        """
        resource_type = request.query_params.get('resource_type')
        resource_id = request.query_params.get('resource_id')

        if not resource_type or not resource_id:
            return Response(
                {'error': 'resource_type and resource_id parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        queryset = AuditLog.objects.filter(
            target_model=resource_type,
            target_id=resource_id
        ).order_by('-timestamp')

        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AuditLogSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AuditLogSerializer(queryset, many=True)
        return Response(serializer.data)
