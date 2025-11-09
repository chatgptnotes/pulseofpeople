"""
API URL Configuration for Pulse of People platform.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import health

# Create router for ViewSets
router = DefaultRouter()

# Add ViewSet routes here
# router.register(r'users', UserViewSet)
# router.register(r'organizations', OrganizationViewSet)
# etc.

urlpatterns = [
    # Health check endpoints (no authentication required)
    path('health/', health.health_check, name='health-check'),
    path('health/detailed/', health.health_check_detailed, name='health-check-detailed'),
    path('health/liveness/', health.liveness_probe, name='liveness-probe'),
    path('health/readiness/', health.readiness_probe, name='readiness-probe'),
    path('version/', health.version_info, name='version-info'),

    # Core API endpoints
    path('', include('api.core_views')),  # If you have a separate core views module
    path('political/', include('api.political_views')),  # If you have political views

    # ViewSet routes
    path('', include(router.urls)),

    # Authentication endpoints (if using DRF's built-in)
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
]
