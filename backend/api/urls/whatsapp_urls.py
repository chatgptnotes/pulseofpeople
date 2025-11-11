"""
WhatsApp API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.whatsapp_webhook import (
    WhatsAppWebhookView,
    WhatsAppStatusWebhookView
)
from api.views.whatsapp_api_views import (
    WhatsAppConversationViewSet,
    VoterProfileViewSet,
    BotConfigurationViewSet,
    WhatsAppMessagesViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'conversations', WhatsAppConversationViewSet, basename='conversation')
router.register(r'voters', VoterProfileViewSet, basename='voter')
router.register(r'bots', BotConfigurationViewSet, basename='bot')
router.register(r'messages', WhatsAppMessagesViewSet, basename='message')

urlpatterns = [
    # Webhook endpoints (no authentication required)
    path('webhook/', WhatsAppWebhookView.as_view(), name='whatsapp-webhook'),
    path('webhook/status/', WhatsAppStatusWebhookView.as_view(), name='whatsapp-status-webhook'),

    # API endpoints (authentication required)
    path('', include(router.urls)),
]
