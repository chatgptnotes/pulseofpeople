"""
Message Processor
Orchestrates the complete message handling pipeline:
1. Receive WhatsApp message
2. Process with AI
3. Store in database
4. Send response
"""
import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from django.core.cache import cache
from api.models.whatsapp_conversation import (
    WhatsAppConversation,
    WhatsAppMessage,
    VoterProfile
)
from .whatsapp_service import get_whatsapp_service
from .ai_service import get_ai_service

logger = logging.getLogger(__name__)


class MessageProcessor:
    """
    Process incoming WhatsApp messages and generate AI responses
    """

    def __init__(self):
        self.whatsapp_service = get_whatsapp_service()
        self.ai_service = get_ai_service()

    def process_incoming_message(
        self,
        phone_number: str,
        message_text: str,
        message_type: str = 'text',
        whatsapp_message_id: Optional[str] = None,
        media_url: Optional[str] = None,
        source_campaign: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing incoming messages

        Args:
            phone_number: User's phone number
            message_text: Message content
            message_type: Type of message (text, voice, image, etc.)
            whatsapp_message_id: WhatsApp's message ID
            media_url: URL for media messages
            source_campaign: Campaign tracking parameter

        Returns:
            Dictionary with processing results
        """
        try:
            # 1. Get or create voter profile
            voter_profile = self._get_or_create_voter_profile(phone_number)

            # 2. Get or create active conversation
            conversation = self._get_or_create_conversation(
                phone_number,
                source_campaign
            )

            # 3. Detect language
            language = self.ai_service.detect_language(message_text)
            conversation.language = language
            conversation.save(update_fields=['language'])

            # 4. Store incoming message
            user_message = self._store_message(
                conversation=conversation,
                sender='user',
                content=message_text,
                message_type=message_type,
                whatsapp_message_id=whatsapp_message_id,
                media_url=media_url,
                language=language
            )

            # 5. Process message with AI (async)
            self._process_message_with_ai(user_message)

            # 6. Get conversation history
            conversation_history = self._get_conversation_history(conversation)

            # 7. Generate AI response
            bot_personality = self._get_bot_personality(conversation)
            ai_response = self.ai_service.generate_conversation_response(
                user_message=message_text,
                conversation_history=conversation_history,
                language=language,
                bot_personality=bot_personality
            )

            # 8. Store bot response
            bot_message = self._store_message(
                conversation=conversation,
                sender='bot',
                content=ai_response['response'],
                message_type='text',
                model_used=ai_response['model'],
                prompt_tokens=ai_response['tokens']['prompt'],
                completion_tokens=ai_response['tokens']['completion']
            )

            # 9. Send response via WhatsApp
            sent_result = self.whatsapp_service.send_text_message(
                to=phone_number,
                message=ai_response['response']
            )

            if sent_result:
                bot_message.whatsapp_message_id = sent_result.get('message_id')
                bot_message.save(update_fields=['whatsapp_message_id'])

            # 10. Update conversation metrics
            conversation.message_count = conversation.messages.count()
            conversation.save(update_fields=['message_count'])

            # 11. Update voter profile
            voter_profile.interaction_count += 1
            voter_profile.total_messages_sent += 1
            voter_profile.last_contacted = timezone.now()
            voter_profile.save(update_fields=[
                'interaction_count',
                'total_messages_sent',
                'last_contacted'
            ])

            # 12. Check if should send referral prompt
            if self._should_prompt_referral(voter_profile, conversation):
                self._send_referral_prompt(phone_number, voter_profile)

            logger.info(f"Processed message from {phone_number}")

            return {
                "status": "success",
                "conversation_id": str(conversation.id),
                "message_id": str(bot_message.id),
                "response": ai_response['response']
            }

        except Exception as e:
            logger.error(f"Failed to process message: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }

    def _get_or_create_voter_profile(self, phone_number: str) -> VoterProfile:
        """Get or create voter profile"""
        profile, created = VoterProfile.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'preferred_language': 'ta',
                'interaction_count': 0,
                'total_messages_sent': 0
            }
        )

        if created:
            # Generate referral code for new users
            profile.generate_referral_code()
            logger.info(f"Created new voter profile: {phone_number}")

        return profile

    def _get_or_create_conversation(
        self,
        phone_number: str,
        source_campaign: Optional[str] = None
    ) -> WhatsAppConversation:
        """Get active conversation or create new one"""

        # Check for active conversation in last 24 hours
        cutoff_time = timezone.now() - timezone.timedelta(hours=24)
        active_conversation = WhatsAppConversation.objects.filter(
            phone_number=phone_number,
            started_at__gte=cutoff_time,
            ended_at__isnull=True
        ).first()

        if active_conversation:
            return active_conversation

        # Close old conversations
        WhatsAppConversation.objects.filter(
            phone_number=phone_number,
            ended_at__isnull=True
        ).update(ended_at=timezone.now())

        # Create new conversation
        conversation = WhatsAppConversation.objects.create(
            phone_number=phone_number,
            source_campaign=source_campaign,
            channel='whatsapp',
            language='ta',  # Default, will be updated
            sentiment='neutral',
            category='inquiry',
            priority='medium'
        )

        logger.info(f"Created new conversation: {conversation.id}")
        return conversation

    def _store_message(
        self,
        conversation: WhatsAppConversation,
        sender: str,
        content: str,
        message_type: str = 'text',
        **kwargs
    ) -> WhatsAppMessage:
        """Store message in database"""
        message = WhatsAppMessage.objects.create(
            conversation=conversation,
            sender=sender,
            content=content,
            message_type=message_type,
            timestamp=timezone.now(),
            **kwargs
        )
        return message

    def _get_conversation_history(
        self,
        conversation: WhatsAppConversation,
        limit: int = 20
    ) -> list:
        """Get conversation history formatted for AI"""
        messages = conversation.messages.order_by('timestamp')[:limit]

        history = []
        for msg in messages:
            role = 'user' if msg.sender == 'user' else 'assistant'
            history.append({
                'role': role,
                'content': msg.content
            })

        return history

    def _get_bot_personality(self, conversation: WhatsAppConversation) -> str:
        """Determine bot personality based on conversation context"""
        # For now, return default. Can be customized based on user profile later
        return 'friendly'

    def _process_message_with_ai(self, message: WhatsAppMessage):
        """
        Process message with AI for classification, sentiment, etc.
        This runs async after response is sent
        """
        try:
            # Classify intent
            intent_result = self.ai_service.classify_intent(message.content)
            message.intent = intent_result.get('intent')
            message.confidence = intent_result.get('confidence', 0) * 100

            # Analyze sentiment
            sentiment_result = self.ai_service.analyze_sentiment(message.content)
            message.sentiment = sentiment_result.get('sentiment')

            # Extract topics and keywords
            extraction = self.ai_service.extract_topics_and_keywords(message.content)
            message.entities = {
                'topics': extraction.get('topics', []),
                'keywords': extraction.get('keywords', []),
                'issues': extraction.get('issues', [])
            }

            message.processed = True
            message.save()

            # Update conversation with extracted data
            conversation = message.conversation
            conversation.sentiment = sentiment_result.get('sentiment', 'neutral')
            conversation.sentiment_score = sentiment_result.get('score', 0.0)
            conversation.category = intent_result.get('category', 'inquiry')

            # Merge topics and keywords
            conversation.topics = list(set(
                conversation.topics + extraction.get('topics', [])
            ))
            conversation.keywords = list(set(
                conversation.keywords + extraction.get('keywords', [])
            ))
            conversation.issues = list(set(
                conversation.issues + extraction.get('issues', [])
            ))

            conversation.save(update_fields=[
                'sentiment',
                'sentiment_score',
                'category',
                'topics',
                'keywords',
                'issues'
            ])

            logger.info(f"Processed message {message.id} with AI")

        except Exception as e:
            logger.error(f"Failed to process message with AI: {str(e)}")
            message.processing_error = str(e)
            message.save(update_fields=['processing_error'])

    def _should_prompt_referral(
        self,
        voter_profile: VoterProfile,
        conversation: WhatsAppConversation
    ) -> bool:
        """Determine if should send referral prompt"""

        # Check cache to avoid spamming
        cache_key = f"referral_prompt_{voter_profile.phone_number}"
        if cache.get(cache_key):
            return False

        # Conditions for sending referral prompt:
        # 1. User has completed at least 5 messages in conversation
        # 2. User has not referred anyone yet
        # 3. Conversation sentiment is positive or neutral

        if conversation.message_count >= 5 and \
           voter_profile.referrals_made == 0 and \
           conversation.sentiment in ['positive', 'neutral']:
            # Set cache for 24 hours
            cache.set(cache_key, True, 86400)
            return True

        return False

    def _send_referral_prompt(
        self,
        phone_number: str,
        voter_profile: VoterProfile
    ):
        """Send referral invitation message"""
        referral_code = voter_profile.referral_code
        referral_link = self.whatsapp_service.generate_click_to_chat_link(
            message=f"Hi, I'm sharing feedback via this bot [ref:{referral_code}]",
            source="referral",
            campaign=referral_code
        )

        referral_message = f"""🎁 Thank you for sharing your feedback!

Help us reach more people:
Share this link with 5 friends: {referral_link}

When 5 friends join, you'll get early updates on policy changes!

Current referrals: {voter_profile.referrals_made}/5"""

        self.whatsapp_service.send_text_message(
            to=phone_number,
            message=referral_message
        )

        logger.info(f"Sent referral prompt to {phone_number}")

    def end_conversation(self, conversation_id: str):
        """End conversation and calculate metrics"""
        try:
            conversation = WhatsAppConversation.objects.get(id=conversation_id)

            if not conversation.ended_at:
                conversation.ended_at = timezone.now()
                conversation.calculate_duration()

                # Generate conversation summary
                history = self._get_conversation_history(conversation, limit=100)
                summary = self.ai_service.summarize_conversation(history)

                # Extract demographics
                demographics = self.ai_service.extract_demographics(history)
                if demographics:
                    conversation.demographics = demographics

                # Calculate satisfaction score (simplified)
                if conversation.sentiment == 'positive':
                    conversation.satisfaction_score = 85
                elif conversation.sentiment == 'neutral':
                    conversation.satisfaction_score = 60
                else:
                    conversation.satisfaction_score = 40

                conversation.resolved = True
                conversation.save()

                # Update voter profile
                voter_profile = VoterProfile.objects.get(
                    phone_number=conversation.phone_number
                )

                # Update sentiment history
                voter_profile.sentiment_history.append({
                    'date': conversation.started_at.isoformat(),
                    'score': conversation.sentiment_score
                })

                # Update topic interests
                for topic in conversation.topics:
                    voter_profile.topic_interests[topic] = \
                        voter_profile.topic_interests.get(topic, 0) + 1

                # Update demographics
                voter_profile.demographics.update(conversation.demographics)

                voter_profile.save()

                logger.info(f"Ended conversation {conversation_id}")

        except Exception as e:
            logger.error(f"Failed to end conversation: {str(e)}")


# Singleton instance
_message_processor = None

def get_message_processor() -> MessageProcessor:
    """Get or create message processor instance"""
    global _message_processor
    if _message_processor is None:
        _message_processor = MessageProcessor()
    return _message_processor
