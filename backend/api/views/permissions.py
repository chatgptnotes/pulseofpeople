"""
Permission Management Views

API endpoints for managing user permissions programmatically.
Supports grant, revoke, list, and sync operations.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from api.models import Permission, UserPermission, RolePermission, UserProfile
from api.serializers.permission_serializers import (
    PermissionSerializer,
    UserPermissionsListSerializer,
    GrantPermissionSerializer,
    RevokePermissionSerializer,
    SyncRolePermissionsSerializer,
    UserPermissionDetailSerializer,
    RolePermissionSerializer
)
from api.permissions.role_permissions import IsAdminOrAbove
from api.utils.audit import (
    log_action,
    ACTION_PERMISSION_GRANTED,
    ACTION_PERMISSION_REVOKED,
)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing available permissions.

    GET /api/permissions/ - List all permissions
    GET /api/permissions/{id}/ - Get permission details
    GET /api/permissions/roles/{role}/ - Get default permissions for a role
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrAbove]

    @action(detail=False, methods=['get'], url_path='roles/(?P<role>[^/.]+)')
    def role_permissions(self, request, role=None):
        """
        Get default permissions for a specific role.

        GET /api/permissions/roles/analyst/

        Response:
        {
            "role": "analyst",
            "permissions": ["view_analytics", "view_reports", ...]
        }
        """
        # Validate role
        valid_roles = ['superadmin', 'admin', 'manager', 'analyst', 'user', 'viewer', 'volunteer']
        if role not in valid_roles:
            return Response(
                {'error': f"Invalid role. Must be one of: {', '.join(valid_roles)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get permissions for this role
        role_perms = Permission.objects.filter(
            role_permissions__role=role
        ).values_list('name', flat=True)

        serializer = RolePermissionSerializer({
            'role': role,
            'permissions': list(role_perms)
        })

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Get all permission categories with counts.

        GET /api/permissions/categories/

        Response:
        {
            "categories": [
                {"name": "users", "label": "User Management", "count": 15},
                ...
            ]
        }
        """
        categories = Permission.objects.values('category').distinct()
        category_data = []

        for cat in categories:
            category_name = cat['category']
            count = Permission.objects.filter(category=category_name).count()
            category_label = dict(Permission.CATEGORIES).get(category_name, category_name)

            category_data.append({
                'name': category_name,
                'label': category_label,
                'count': count
            })

        return Response({'categories': category_data})


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrAbove])
def user_permissions_list(request, user_id):
    """
    List all permissions for a specific user.

    GET /api/users/{user_id}/permissions/

    Response:
    {
        "user_id": 123,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "analyst",
        "role_permissions": ["view_analytics", "view_reports", ...],
        "custom_grants": ["create_users"],
        "custom_revocations": ["export_data"],
        "effective_permissions": ["view_analytics", "view_reports", "create_users"]
    }
    """
    # Get target user
    try:
        target_user = User.objects.get(id=user_id)
        target_profile = target_user.profile
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except UserProfile.DoesNotExist:
        return Response(
            {'error': 'User profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check organization isolation (admins can only see users in their org)
    requesting_role = request.user.profile.role if hasattr(request.user, 'profile') else 'user'
    if requesting_role == 'admin':
        # Admins can only see users in their organization
        if hasattr(request.user.profile, 'organization') and hasattr(target_profile, 'organization'):
            if request.user.profile.organization != target_profile.organization:
                return Response(
                    {'error': 'You can only view permissions for users in your organization'},
                    status=status.HTTP_403_FORBIDDEN
                )

    # Get role-based permissions
    role_perms = list(Permission.objects.filter(
        role_permissions__role=target_profile.role
    ).values_list('name', flat=True))

    # Get custom grants
    custom_grants = list(UserPermission.objects.filter(
        user_profile=target_profile,
        granted=True
    ).select_related('permission').values_list('permission__name', flat=True))

    # Get custom revocations
    custom_revocations = list(UserPermission.objects.filter(
        user_profile=target_profile,
        granted=False
    ).select_related('permission').values_list('permission__name', flat=True))

    # Calculate effective permissions
    # Start with role permissions
    effective_perms = set(role_perms)
    # Add custom grants
    effective_perms.update(custom_grants)
    # Remove custom revocations
    effective_perms.difference_update(custom_revocations)

    # Prepare response data
    data = {
        'user_id': target_user.id,
        'username': target_user.username,
        'email': target_user.email,
        'role': target_profile.role,
        'role_permissions': sorted(role_perms),
        'custom_grants': sorted(custom_grants),
        'custom_revocations': sorted(custom_revocations),
        'effective_permissions': sorted(list(effective_perms))
    }

    serializer = UserPermissionsListSerializer(data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrAbove])
def grant_permission(request, user_id):
    """
    Grant a permission to a user.

    POST /api/users/{user_id}/permissions/grant/

    Request:
    {
        "permission": "create_users",
        "reason": "Promoted to team lead"
    }

    Response:
    {
        "success": true,
        "user_id": 123,
        "permission": "create_users",
        "granted_by": "admin@example.com",
        "granted_at": "2025-11-08T20:30:00Z",
        "message": "Permission granted successfully"
    }
    """
    serializer = GrantPermissionSerializer(
        data=request.data,
        context={'request': request, 'target_user_id': user_id}
    )

    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get validated data
    validated_data = serializer.validated_data
    target_user = validated_data['_target_user']
    permission = validated_data['_permission']
    requesting_user = validated_data['_requesting_user']
    reason = validated_data.get('reason', '')

    try:
        with transaction.atomic():
            # Check if there's an existing revocation to update
            existing_revocation = UserPermission.objects.filter(
                user_profile=target_user.profile,
                permission=permission,
                granted=False
            ).first()

            if existing_revocation:
                # Update existing revocation to grant
                existing_revocation.granted = True
                existing_revocation.save()
                user_permission = existing_revocation
            else:
                # Create new grant
                user_permission = UserPermission.objects.create(
                    user_profile=target_user.profile,
                    permission=permission,
                    granted=True
                )

            # Log the action
            log_action(
                user=requesting_user,
                action=ACTION_PERMISSION_GRANTED,
                resource_type='UserPermission',
                resource_id=str(user_permission.id),
                changes={
                    'target_user_id': target_user.id,
                    'target_user_email': target_user.email,
                    'permission': permission.name,
                    'reason': reason,
                    'granted_by': requesting_user.email
                },
                request=request
            )

            return Response({
                'success': True,
                'user_id': target_user.id,
                'username': target_user.username,
                'permission': permission.name,
                'granted_by': requesting_user.email,
                'granted_at': user_permission.created_at.isoformat(),
                'message': f"Permission '{permission.name}' granted successfully"
            }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {'error': f"Failed to grant permission: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrAbove])
def revoke_permission(request, user_id):
    """
    Revoke a permission from a user.

    POST /api/users/{user_id}/permissions/revoke/

    Request:
    {
        "permission": "create_users",
        "reason": "Role changed"
    }

    Response:
    {
        "success": true,
        "user_id": 123,
        "permission": "create_users",
        "revoked_by": "admin@example.com",
        "revoked_at": "2025-11-08T20:30:00Z",
        "message": "Permission revoked successfully"
    }
    """
    serializer = RevokePermissionSerializer(
        data=request.data,
        context={'request': request, 'target_user_id': user_id}
    )

    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get validated data
    validated_data = serializer.validated_data
    target_user = validated_data['_target_user']
    permission = validated_data['_permission']
    requesting_user = validated_data['_requesting_user']
    reason = validated_data.get('reason', '')

    try:
        with transaction.atomic():
            # Check if there's an existing grant to update
            existing_grant = UserPermission.objects.filter(
                user_profile=target_user.profile,
                permission=permission,
                granted=True
            ).first()

            if existing_grant:
                # Update existing grant to revoke
                existing_grant.granted = False
                existing_grant.save()
                user_permission = existing_grant
            else:
                # Create new revocation (to override role permission)
                user_permission = UserPermission.objects.create(
                    user_profile=target_user.profile,
                    permission=permission,
                    granted=False
                )

            # Log the action
            log_action(
                user=requesting_user,
                action=ACTION_PERMISSION_REVOKED,
                resource_type='UserPermission',
                resource_id=str(user_permission.id),
                changes={
                    'target_user_id': target_user.id,
                    'target_user_email': target_user.email,
                    'permission': permission.name,
                    'reason': reason,
                    'revoked_by': requesting_user.email
                },
                request=request
            )

            return Response({
                'success': True,
                'user_id': target_user.id,
                'username': target_user.username,
                'permission': permission.name,
                'revoked_by': requesting_user.email,
                'revoked_at': user_permission.created_at.isoformat(),
                'message': f"Permission '{permission.name}' revoked successfully"
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f"Failed to revoke permission: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminOrAbove])
def sync_role_permissions(request, user_id):
    """
    Reset user permissions to role defaults (removes all custom grants/revocations).

    POST /api/users/{user_id}/permissions/sync-role/

    Request:
    {
        "confirm": true
    }

    Response:
    {
        "success": true,
        "user_id": 123,
        "role": "analyst",
        "removed_grants": ["create_users"],
        "removed_revocations": [],
        "current_permissions": ["view_analytics", "view_reports", ...],
        "message": "Permissions synced to role defaults"
    }
    """
    serializer = SyncRolePermissionsSerializer(
        data=request.data,
        context={'request': request, 'target_user_id': user_id}
    )

    if not serializer.is_valid():
        return Response(
            {'error': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get validated data
    validated_data = serializer.validated_data
    target_user = validated_data['_target_user']
    requesting_user = validated_data['_requesting_user']

    try:
        with transaction.atomic():
            # Get current custom permissions
            custom_perms = UserPermission.objects.filter(
                user_profile=target_user.profile
            )

            removed_grants = list(custom_perms.filter(granted=True).values_list('permission__name', flat=True))
            removed_revocations = list(custom_perms.filter(granted=False).values_list('permission__name', flat=True))

            # Delete all custom permissions
            deleted_count = custom_perms.delete()[0]

            # Get current role permissions
            role_perms = list(Permission.objects.filter(
                role_permissions__role=target_user.profile.role
            ).values_list('name', flat=True))

            # Log the action
            log_action(
                user=requesting_user,
                action='permission_sync',
                resource_type='UserProfile',
                resource_id=str(target_user.profile.id),
                changes={
                    'target_user_id': target_user.id,
                    'target_user_email': target_user.email,
                    'role': target_user.profile.role,
                    'removed_grants': removed_grants,
                    'removed_revocations': removed_revocations,
                    'removed_count': deleted_count,
                    'synced_by': requesting_user.email
                },
                request=request
            )

            return Response({
                'success': True,
                'user_id': target_user.id,
                'username': target_user.username,
                'role': target_user.profile.role,
                'removed_grants': sorted(removed_grants),
                'removed_revocations': sorted(removed_revocations),
                'current_permissions': sorted(role_perms),
                'message': f"Permissions synced to role defaults. Removed {deleted_count} custom permissions."
            }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f"Failed to sync permissions: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminOrAbove])
def user_permission_history(request, user_id):
    """
    Get permission change history for a user.

    GET /api/users/{user_id}/permissions/history/

    Response:
    {
        "user_id": 123,
        "history": [
            {
                "action": "permission_granted",
                "permission": "create_users",
                "changed_by": "admin@example.com",
                "timestamp": "2025-11-08T20:30:00Z",
                "reason": "Promoted to team lead"
            },
            ...
        ]
    }
    """
    # Get target user
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Import AuditLog here to avoid circular imports
    from api.models import AuditLog

    # Get permission-related audit logs for this user
    audit_logs = AuditLog.objects.filter(
        target_model='UserPermission',
        changes__target_user_id=user_id
    ).order_by('-timestamp')[:50]  # Last 50 changes

    history = []
    for log in audit_logs:
        history.append({
            'action': log.action,
            'permission': log.changes.get('permission', 'Unknown'),
            'changed_by': log.user.email if log.user else 'System',
            'timestamp': log.timestamp.isoformat(),
            'reason': log.changes.get('reason', ''),
            'details': log.changes
        })

    return Response({
        'user_id': user_id,
        'username': target_user.username,
        'history': history,
        'total_changes': len(history)
    })
