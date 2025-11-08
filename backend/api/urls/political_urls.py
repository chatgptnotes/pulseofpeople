"""
URL routing for Political Platform APIs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.political_views import (
    StateViewSet, DistrictViewSet, ConstituencyViewSet, PollingBoothViewSet,
    PoliticalPartyViewSet, IssueCategoryViewSet, VoterSegmentViewSet,
    DirectFeedbackViewSet, FieldReportViewSet,
    constituency_analytics, district_analytics, state_analytics, dashboard_overview
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'states', StateViewSet, basename='state')
router.register(r'districts', DistrictViewSet, basename='district')
router.register(r'constituencies', ConstituencyViewSet, basename='constituency')
router.register(r'polling-booths', PollingBoothViewSet, basename='polling-booth')
router.register(r'political-parties', PoliticalPartyViewSet, basename='political-party')
router.register(r'issue-categories', IssueCategoryViewSet, basename='issue-category')
router.register(r'voter-segments', VoterSegmentViewSet, basename='voter-segment')
router.register(r'feedback', DirectFeedbackViewSet, basename='feedback')
router.register(r'field-reports', FieldReportViewSet, basename='field-report')

urlpatterns = [
    # Analytics endpoints
    path('analytics/overview/', dashboard_overview, name='analytics-overview'),
    path('analytics/constituency/<str:code>/', constituency_analytics, name='constituency-analytics'),
    path('analytics/district/<int:district_id>/', district_analytics, name='district-analytics'),
    path('analytics/state/<str:state_code>/', state_analytics, name='state-analytics'),

    # Include all router URLs
    path('', include(router.urls)),
]
