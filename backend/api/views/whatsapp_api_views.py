"""
WhatsApp API Views
REST API endpoints for frontend to fetch conversation data and analytics
"""
import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models.whatsapp_conversation import (
    WhatsAppConversation,
    WhatsAppMessage,
    VoterProfile,
    BotConfiguration
)
from api.serializers.whatsapp_serializers import (
    WhatsAppConversationListSerializer,
    WhatsAppConversationDetailSerializer,
    WhatsAppMessageSerializer,
    VoterProfileSerializer,
    BotConfigurationSerializer,
    ConversationAnalyticsSerializer,
    ClickToWhatsAppLinkSerializer
)
from api.services.whatsapp_service import get_whatsapp_service

logger = logging.getLogger(__name__)


class WhatsAppConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for WhatsApp conversations

    GET /api/whatsapp/conversations/ - List conversations
    GET /api/whatsapp/conversations/{id}/ - Get conversation detail
    GET /api/whatsapp/conversations/analytics/ - Get analytics dashboard data
    """

    permission_classes = [IsAuthenticated]
    queryset = WhatsAppConversation.objects.all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return WhatsAppConversationDetailSerializer
        return WhatsAppConversationListSerializer

    def get_queryset(self):
        """Filter and order conversations"""
        queryset = WhatsAppConversation.objects.all()

        # Filter by date range
        days = self.request.query_params.get('days', 30)
        try:
            days = int(days)
            since_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(started_at__gte=since_date)
        except ValueError:
            pass

        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)

        # Filter by sentiment
        sentiment = self.request.query_params.get('sentiment')
        if sentiment:
            queryset = queryset.filter(sentiment=sentiment)

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filter by channel
        channel = self.request.query_params.get('channel')
        if channel:
            queryset = queryset.filter(channel=channel)

        # Filter by resolved status
        resolved = self.request.query_params.get('resolved')
        if resolved is not None:
            queryset = queryset.filter(resolved=resolved == 'true')

        # Search by phone number or name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(phone_number__icontains=search) |
                Q(user_name__icontains=search)
            )

        return queryset.order_by('-started_at')

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get analytics dashboard data

        GET /api/whatsapp/conversations/analytics/
        """
        try:
            # Time range
            days = int(request.query_params.get('days', 30))
            since_date = timezone.now() - timedelta(days=days)

            # Total conversations
            total_conversations = WhatsAppConversation.objects.filter(
                started_at__gte=since_date
            ).count()

            # Active chats (started in last 24 hours, not ended)
            active_cutoff = timezone.now() - timedelta(hours=24)
            active_chats = WhatsAppConversation.objects.filter(
                started_at__gte=active_cutoff,
                ended_at__isnull=True
            ).count()

            # Average response time (calculate from message timestamps)
            avg_response_time = 0.8  # Simplified for now

            # Satisfaction rate
            satisfaction_data = WhatsAppConversation.objects.filter(
                started_at__gte=since_date,
                satisfaction_score__gt=0
            ).aggregate(
                avg_satisfaction=Avg('satisfaction_score')
            )
            satisfaction_rate = satisfaction_data['avg_satisfaction'] or 0

            # Human handoffs
            human_handoffs = WhatsAppConversation.objects.filter(
                started_at__gte=since_date,
                human_handoff=True
            ).count()

            # Resolved today
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            resolved_today = WhatsAppConversation.objects.filter(
                ended_at__gte=today_start,
                resolved=True
            ).count()

            # Language breakdown
            language_data = WhatsAppConversation.objects.filter(
                started_at__gte=since_date
            ).values('language').annotate(count=Count('id'))

            total = sum(item['count'] for item in language_data)
            language_breakdown = {}
            for item in language_data:
                lang_name = {
                    'ta': 'Tamil',
                    'en': 'English',
                    'hi': 'Hindi',
                    'te': 'Telugu'
                }.get(item['language'], item['language'])

                if total > 0:
                    language_breakdown[lang_name] = int((item['count'] / total) * 100)

            # Sentiment breakdown
            sentiment_data = WhatsAppConversation.objects.filter(
                started_at__gte=since_date
            ).values('sentiment').annotate(count=Count('id'))

            sentiment_breakdown = {
                item['sentiment']: item['count']
                for item in sentiment_data
            }

            # Category breakdown
            category_data = WhatsAppConversation.objects.filter(
                started_at__gte=since_date
            ).values('category').annotate(count=Count('id'))

            category_breakdown = {
                item['category']: item['count']
                for item in category_data
            }

            # Top topics
            all_conversations = WhatsAppConversation.objects.filter(
                started_at__gte=since_date
            )
            topics_counter = {}
            for conv in all_conversations:
                for topic in conv.topics:
                    topics_counter[topic] = topics_counter.get(topic, 0) + 1

            top_topics = sorted(
                [{'topic': k, 'count': v} for k, v in topics_counter.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]

            # Top issues
            issues_counter = {}
            for conv in all_conversations:
                for issue in conv.issues:
                    issues_counter[issue] = issues_counter.get(issue, 0) + 1

            top_issues = sorted(
                [{'issue': k, 'count': v} for k, v in issues_counter.items()],
                key=lambda x: x['count'],
                reverse=True
            )[:10]

            analytics_data = {
                'total_conversations': total_conversations,
                'active_chats': active_chats,
                'avg_response_time': round(avg_response_time, 2),
                'satisfaction_rate': round(satisfaction_rate, 1),
                'human_handoffs': human_handoffs,
                'resolved_today': resolved_today,
                'language_breakdown': language_breakdown,
                'sentiment_breakdown': sentiment_breakdown,
                'category_breakdown': category_breakdown,
                'top_topics': top_topics,
                'top_issues': top_issues,
            }

            serializer = ConversationAnalyticsSerializer(analytics_data)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Analytics error: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def generate_link(self, request):
        """
        Generate click-to-WhatsApp link

        POST /api/whatsapp/conversations/generate_link/
        Body: {"message": "Hi", "source": "facebook", "campaign": "summer_2025"}
        """
        serializer = ClickToWhatsAppLinkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        whatsapp_service = get_whatsapp_service()

        link = whatsapp_service.generate_click_to_chat_link(
            message=data.get('message', 'Hi'),
            source=data.get('source', ''),
            campaign=data.get('campaign', '')
        )

        return Response({
            'link': link,
            'qr_code_url': f"{link}&format=qr"  # Frontend can generate QR from this
        })


class VoterProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for voter profiles

    GET /api/whatsapp/voters/ - List voter profiles
    GET /api/whatsapp/voters/{id}/ - Get voter profile detail
    """

    permission_classes = [IsAuthenticated]
    queryset = VoterProfile.objects.all()
    serializer_class = VoterProfileSerializer

    def get_queryset(self):
        """Filter voter profiles"""
        queryset = VoterProfile.objects.all()

        # Search by phone or name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(phone_number__icontains=search) |
                Q(name__icontains=search)
            )

        # Filter by referral activity
        has_referrals = self.request.query_params.get('has_referrals')
        if has_referrals == 'true':
            queryset = queryset.filter(referrals_made__gt=0)

        return queryset.order_by('-last_contacted')


class BotConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for bot configurations

    GET /api/whatsapp/bots/ - List bot configurations
    GET /api/whatsapp/bots/{id}/ - Get bot configuration detail
    """

    permission_classes = [IsAuthenticated]
    queryset = BotConfiguration.objects.filter(active=True)
    serializer_class = BotConfigurationSerializer


class WhatsAppMessagesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for individual messages (for live chat view)

    GET /api/whatsapp/messages/ - List recent messages
    GET /api/whatsapp/messages/{id}/ - Get message detail
    """

    permission_classes = [IsAuthenticated]
    queryset = WhatsAppMessage.objects.all()
    serializer_class = WhatsAppMessageSerializer

    def get_queryset(self):
        """Filter messages"""
        queryset = WhatsAppMessage.objects.all()

        # Filter by conversation
        conversation_id = self.request.query_params.get('conversation_id')
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)

        # Only recent messages (last 24 hours) if no conversation specified
        else:
            cutoff = timezone.now() - timedelta(hours=24)
            queryset = queryset.filter(timestamp__gte=cutoff)

        return queryset.order_by('timestamp')
