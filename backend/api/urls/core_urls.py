"""
URL routing for Core Political Platform APIs - Workstream 2
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.core_views import (
    OrganizationViewSet,
    VoterViewSet,
    VoterInteractionViewSet,
    CampaignViewSet,
    SocialMediaPostViewSet,
    AlertViewSet,
    EventViewSet,
    VolunteerViewSet,
    ExpenseViewSet,
)

# Create router
router = DefaultRouter()

# Register all viewsets
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'voters', VoterViewSet, basename='voter')
router.register(r'voter-interactions', VoterInteractionViewSet, basename='voter-interaction')
router.register(r'campaigns', CampaignViewSet, basename='campaign')
router.register(r'social-posts', SocialMediaPostViewSet, basename='social-post')
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'events', EventViewSet, basename='event')
router.register(r'volunteers', VolunteerViewSet, basename='volunteer')
router.register(r'expenses', ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]
