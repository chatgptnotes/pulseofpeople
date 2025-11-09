"""
WhatsApp Webhook Views
Handles incoming webhooks from Meta WhatsApp Cloud API
"""
import os
import logging
import json
import hashlib
import hmac
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from api.services.message_processor import get_message_processor

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(APIView):
    """
    Webhook endpoint for WhatsApp Cloud API
    Handles verification and incoming messages
    """

    # No authentication required for webhooks (uses verify_token)
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """
        Handle webhook verification from Meta

        Meta sends GET request with:
        - hub.mode: 'subscribe'
        - hub.verify_token: our verify token
        - hub.challenge: challenge string to echo back
        """
        try:
            mode = request.GET.get('hub.mode')
            token = request.GET.get('hub.verify_token')
            challenge = request.GET.get('hub.challenge')

            verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'pulse_of_people_2025')

            if mode == 'subscribe' and token == verify_token:
                logger.info("WhatsApp webhook verified successfully")
                return Response(int(challenge), status=status.HTTP_200_OK)
            else:
                logger.warning(f"WhatsApp webhook verification failed: mode={mode}, token={token}")
                return Response(
                    {"error": "Verification failed"},
                    status=status.HTTP_403_FORBIDDEN
                )

        except Exception as e:
            logger.error(f"Webhook verification error: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        Handle incoming WhatsApp messages

        Meta sends POST with message data in request body
        """
        try:
            # Verify signature (optional but recommended for production)
            if not self._verify_signature(request):
                logger.warning("Invalid webhook signature")
                return Response(
                    {"error": "Invalid signature"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Parse webhook payload
            body = request.data
            logger.info(f"Received webhook: {json.dumps(body, indent=2)}")

            # Extract message data
            if body.get('object') != 'whatsapp_business_account':
                return Response({"status": "ignored"}, status=status.HTTP_200_OK)

            entries = body.get('entry', [])
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    if change.get('field') != 'messages':
                        continue

                    value = change.get('value', {})
                    messages = value.get('messages', [])

                    for message in messages:
                        self._process_webhook_message(message, value)

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}", exc_info=True)
            # Return 200 to prevent Meta from retrying
            return Response({"status": "error"}, status=status.HTTP_200_OK)

    def _verify_signature(self, request):
        """
        Verify webhook signature from Meta

        Meta signs requests with app secret
        """
        app_secret = os.getenv('WHATSAPP_APP_SECRET')
        if not app_secret:
            # Skip verification if no secret configured (for testing)
            logger.warning("No app secret configured, skipping signature verification")
            return True

        signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')
        if not signature:
            return False

        # Calculate expected signature
        expected_signature = 'sha256=' + hmac.new(
            app_secret.encode('utf-8'),
            request.body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def _process_webhook_message(self, message: dict, value: dict):
        """
        Process individual message from webhook

        Args:
            message: Message object from webhook
            value: Parent value object containing metadata
        """
        try:
            # Extract message details
            message_id = message.get('id')
            message_type = message.get('type')
            from_number = message.get('from')
            timestamp = message.get('timestamp')

            # Extract message content based on type
            if message_type == 'text':
                message_text = message.get('text', {}).get('body', '')
            elif message_type == 'image':
                message_text = message.get('image', {}).get('caption', '[Image]')
            elif message_type == 'video':
                message_text = message.get('video', {}).get('caption', '[Video]')
            elif message_type == 'audio':
                message_text = '[Audio message]'
            elif message_type == 'document':
                message_text = message.get('document', {}).get('caption', '[Document]')
            elif message_type == 'location':
                location = message.get('location', {})
                message_text = f"[Location: {location.get('latitude')}, {location.get('longitude')}]"
            elif message_type == 'button':
                message_text = message.get('button', {}).get('text', '[Button click]')
            else:
                message_text = f'[{message_type} message]'
                logger.info(f"Received unsupported message type: {message_type}")

            # Extract media URL if present
            media_url = None
            if message_type in ['image', 'video', 'audio', 'document']:
                media_data = message.get(message_type, {})
                media_url = media_data.get('url')

            # Extract campaign tracking from message (if present)
            source_campaign = self._extract_campaign_tracking(message_text)

            # Get message processor
            processor = get_message_processor()

            # Process message
            result = processor.process_incoming_message(
                phone_number=from_number,
                message_text=message_text,
                message_type=message_type,
                whatsapp_message_id=message_id,
                media_url=media_url,
                source_campaign=source_campaign
            )

            logger.info(f"Processed message {message_id}: {result['status']}")

        except Exception as e:
            logger.error(f"Failed to process webhook message: {str(e)}", exc_info=True)

    def _extract_campaign_tracking(self, message_text: str) -> str:
        """
        Extract campaign tracking from message

        Messages from click-to-chat links may include:
        [src:facebook] [cmp:campaign_001]
        """
        import re

        # Extract campaign ID
        campaign_match = re.search(r'\[cmp:([^\]]+)\]', message_text)
        if campaign_match:
            return campaign_match.group(1)

        # Extract source
        source_match = re.search(r'\[src:([^\]]+)\]', message_text)
        if source_match:
            return source_match.group(1)

        # Extract referral code
        ref_match = re.search(r'\[ref:([^\]]+)\]', message_text)
        if ref_match:
            return f"referral_{ref_match.group(1)}"

        return None


@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppStatusWebhookView(APIView):
    """
    Webhook endpoint for WhatsApp message status updates
    Handles delivery receipts, read receipts, etc.
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Handle status updates"""
        try:
            body = request.data
            logger.debug(f"Received status webhook: {json.dumps(body, indent=2)}")

            # Extract status updates
            entries = body.get('entry', [])
            for entry in entries:
                changes = entry.get('changes', [])
                for change in changes:
                    value = change.get('value', {})
                    statuses = value.get('statuses', [])

                    for status_update in statuses:
                        self._process_status_update(status_update)

            return Response({"status": "success"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Status webhook error: {str(e)}")
            return Response({"status": "error"}, status=status.HTTP_200_OK)

    def _process_status_update(self, status_update: dict):
        """Process message status update"""
        try:
            from api.models.whatsapp_conversation import WhatsAppMessage

            message_id = status_update.get('id')
            status_value = status_update.get('status')
            timestamp = status_update.get('timestamp')

            # Update message in database
            message = WhatsAppMessage.objects.filter(
                whatsapp_message_id=message_id
            ).first()

            if message:
                if not message.metadata:
                    message.metadata = {}

                message.metadata['delivery_status'] = status_value
                message.metadata['status_timestamp'] = timestamp
                message.save(update_fields=['metadata'])

                logger.debug(f"Updated message {message_id} status to {status_value}")
            else:
                logger.warning(f"Message {message_id} not found in database")

        except Exception as e:
            logger.error(f"Failed to process status update: {str(e)}")
