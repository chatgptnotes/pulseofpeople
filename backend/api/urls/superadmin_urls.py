"""
URL configuration for superadmin routes
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.superadmin.user_management import SuperAdminUserManagementViewSet
from api.views.audit_logs import AuditLogViewSet

router = DefaultRouter()
router.register(r'users', SuperAdminUserManagementViewSet, basename='superadmin-users')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    path('', include(router.urls)),
]
