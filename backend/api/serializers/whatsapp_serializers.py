"""
WhatsApp Serializers
For API endpoints to serve frontend
"""
from rest_framework import serializers
from api.models import (
    WhatsAppConversation,
    WhatsAppMessage,
    VoterProfile,
    BotConfiguration
)


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    """Serializer for WhatsApp messages"""

    class Meta:
        model = WhatsAppMessage
        fields = [
            'id',
            'sender',
            'message_type',
            'content',
            'media_url',
            'timestamp',
            'intent',
            'confidence',
            'sentiment',
            'entities',
            'language',
            'processed',
            'model_used',
        ]


class WhatsAppConversationListSerializer(serializers.ModelSerializer):
    """Serializer for conversation list (summary view)"""

    message_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = WhatsAppConversation
        fields = [
            'id',
            'phone_number',
            'user_name',
            'user_location',
            'started_at',
            'duration_seconds',
            'message_count',
            'language',
            'channel',
            'sentiment',
            'sentiment_score',
            'category',
            'priority',
            'topics',
            'keywords',
            'issues',
            'satisfaction_score',
            'demographics',
            'political_lean',
            'ai_confidence',
            'resolved',
            'human_handoff',
        ]


class WhatsAppConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer for conversation detail (with messages)"""

    messages = WhatsAppMessageSerializer(many=True, read_only=True)

    class Meta:
        model = WhatsAppConversation
        fields = [
            'id',
            'phone_number',
            'user_name',
            'user_location',
            'started_at',
            'ended_at',
            'duration_seconds',
            'message_count',
            'language',
            'channel',
            'sentiment',
            'sentiment_score',
            'category',
            'priority',
            'topics',
            'keywords',
            'issues',
            'satisfaction_score',
            'demographics',
            'political_lean',
            'ai_confidence',
            'resolved',
            'human_handoff',
            'source_campaign',
            'referral_code',
            'messages',
            'created_at',
            'updated_at',
        ]


class VoterProfileSerializer(serializers.ModelSerializer):
    """Serializer for voter profiles"""

    class Meta:
        model = VoterProfile
        fields = [
            'id',
            'phone_number',
            'name',
            'preferred_language',
            'location_data',
            'demographics',
            'political_lean',
            'interaction_count',
            'total_messages_sent',
            'avg_sentiment_score',
            'last_contacted',
            'first_contacted',
            'topic_interests',
            'issues_raised',
            'sentiment_history',
            'referral_code',
            'referrals_made',
        ]


class BotConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for bot configurations"""

    class Meta:
        model = BotConfiguration
        fields = [
            'id',
            'name',
            'description',
            'personality',
            'languages',
            'channels',
            'ai_model',
            'system_prompt',
            'custom_prompts',
            'knowledge_base',
            'response_time_target',
            'max_conversation_length',
            'auto_handoff_threshold',
            'active',
            'total_conversations',
            'accuracy_rate',
            'satisfaction_rate',
        ]


class ConversationAnalyticsSerializer(serializers.Serializer):
    """Serializer for analytics data"""

    total_conversations = serializers.IntegerField()
    active_chats = serializers.IntegerField()
    avg_response_time = serializers.FloatField()
    satisfaction_rate = serializers.FloatField()
    human_handoffs = serializers.IntegerField()
    resolved_today = serializers.IntegerField()
    language_breakdown = serializers.DictField()
    sentiment_breakdown = serializers.DictField()
    category_breakdown = serializers.DictField()
    top_topics = serializers.ListField()
    top_issues = serializers.ListField()


class ClickToWhatsAppLinkSerializer(serializers.Serializer):
    """Serializer for generating click-to-chat links"""

    message = serializers.CharField(
        default="Hi, I want to share feedback",
        max_length=500
    )
    source = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Traffic source (e.g., facebook, qr_code, website)"
    )
    campaign = serializers.CharField(
        required=False,
        max_length=100,
        help_text="Campaign identifier"
    )
