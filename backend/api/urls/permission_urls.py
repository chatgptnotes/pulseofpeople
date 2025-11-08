"""
Permission Management URL Configuration

Routes for permission management endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.permissions import (
    PermissionViewSet,
    user_permissions_list,
    grant_permission,
    revoke_permission,
    sync_role_permissions,
    user_permission_history,
)

# Create router for PermissionViewSet
router = DefaultRouter()
router.register(r'permissions', PermissionViewSet, basename='permission')

urlpatterns = [
    # ViewSet routes (permissions listing)
    path('', include(router.urls)),

    # User permission management routes (nested under users)
    path('users/<int:user_id>/permissions/', user_permissions_list, name='user-permissions-list'),
    path('users/<int:user_id>/permissions/grant/', grant_permission, name='grant-permission'),
    path('users/<int:user_id>/permissions/revoke/', revoke_permission, name='revoke-permission'),
    path('users/<int:user_id>/permissions/sync-role/', sync_role_permissions, name='sync-role-permissions'),
    path('users/<int:user_id>/permissions/history/', user_permission_history, name='user-permission-history'),
]
