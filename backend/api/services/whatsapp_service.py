"""
WhatsApp Service
Handles all WhatsApp Cloud API interactions using PyWa
"""
import os
import logging
from typing import Optional, Dict, Any
from pywa import WhatsApp
from pywa.types import Message, Button, CallbackButton
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service class for WhatsApp Cloud API integration
    """

    def __init__(self):
        """Initialize WhatsApp client with credentials"""
        self.phone_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.token = os.getenv('WHATSAPP_ACCESS_TOKEN')

        if not self.phone_id or not self.token:
            logger.warning("WhatsApp credentials not configured. Running in test mode.")
            self.client = None
        else:
            try:
                self.client = WhatsApp(
                    phone_id=self.phone_id,
                    token=self.token
                )
                logger.info(f"WhatsApp Service initialized with phone_id: {self.phone_id}")
            except Exception as e:
                logger.error(f"Failed to initialize WhatsApp client: {str(e)}")
                self.client = None

    def send_text_message(
        self,
        to: str,
        message: str,
        preview_url: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Send text message to a WhatsApp number

        Args:
            to: Phone number with country code (e.g., "919876543210")
            message: Text message to send
            preview_url: Whether to show URL preview

        Returns:
            Message ID if successful, None otherwise
        """
        if not self.client:
            logger.warning(f"Test mode: Would send message to {to}: {message}")
            return {"message_id": "test_message_id", "status": "test_mode"}

        try:
            response = self.client.send_message(
                to=to,
                text=message,
                preview_url=preview_url
            )
            logger.info(f"Message sent to {to}, ID: {response.message_id}")
            return {
                "message_id": response.message_id,
                "status": "sent"
            }
        except Exception as e:
            logger.error(f"Failed to send message to {to}: {str(e)}")
            return None

    def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en",
        components: Optional[list] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send pre-approved template message

        Args:
            to: Phone number
            template_name: Name of approved template
            language_code: Template language
            components: Template components/variables

        Returns:
            Message ID if successful
        """
        if not self.client:
            logger.warning(f"Test mode: Would send template {template_name} to {to}")
            return {"message_id": "test_template_id", "status": "test_mode"}

        try:
            response = self.client.send_template(
                to=to,
                template=template_name,
                lang=language_code,
                components=components or []
            )
            logger.info(f"Template sent to {to}, ID: {response.message_id}")
            return {
                "message_id": response.message_id,
                "status": "sent"
            }
        except Exception as e:
            logger.error(f"Failed to send template to {to}: {str(e)}")
            return None

    def send_interactive_buttons(
        self,
        to: str,
        body_text: str,
        buttons: list,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send interactive message with buttons

        Args:
            to: Phone number
            body_text: Main message text
            buttons: List of button dictionaries [{"id": "1", "title": "Option 1"}]
            header_text: Optional header
            footer_text: Optional footer

        Returns:
            Message ID if successful
        """
        if not self.client:
            logger.warning(f"Test mode: Would send buttons to {to}")
            return {"message_id": "test_button_id", "status": "test_mode"}

        try:
            button_objects = [
                Button(
                    button_id=btn['id'],
                    title=btn['title']
                )
                for btn in buttons
            ]

            response = self.client.send_message(
                to=to,
                text=body_text,
                buttons=button_objects,
                header=header_text,
                footer=footer_text
            )
            logger.info(f"Interactive buttons sent to {to}")
            return {
                "message_id": response.message_id,
                "status": "sent"
            }
        except Exception as e:
            logger.error(f"Failed to send buttons to {to}: {str(e)}")
            return None

    def send_media_message(
        self,
        to: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send media message (image, video, document)

        Args:
            to: Phone number
            media_type: Type of media (image, video, document)
            media_url: Public URL of media file
            caption: Optional caption

        Returns:
            Message ID if successful
        """
        if not self.client:
            logger.warning(f"Test mode: Would send {media_type} to {to}")
            return {"message_id": "test_media_id", "status": "test_mode"}

        try:
            if media_type == 'image':
                response = self.client.send_image(
                    to=to,
                    image=media_url,
                    caption=caption
                )
            elif media_type == 'video':
                response = self.client.send_video(
                    to=to,
                    video=media_url,
                    caption=caption
                )
            elif media_type == 'document':
                response = self.client.send_document(
                    to=to,
                    document=media_url,
                    caption=caption
                )
            else:
                raise ValueError(f"Unsupported media type: {media_type}")

            logger.info(f"{media_type} sent to {to}")
            return {
                "message_id": response.message_id,
                "status": "sent"
            }
        except Exception as e:
            logger.error(f"Failed to send {media_type} to {to}: {str(e)}")
            return None

    def mark_as_read(self, message_id: str) -> bool:
        """
        Mark message as read

        Args:
            message_id: WhatsApp message ID

        Returns:
            True if successful
        """
        if not self.client:
            return True

        try:
            self.client.mark_message_as_read(message_id)
            return True
        except Exception as e:
            logger.error(f"Failed to mark message {message_id} as read: {str(e)}")
            return False

    def generate_qr_code(self, message: str = "Hi") -> str:
        """
        Generate wa.me link with pre-filled message

        Args:
            message: Pre-filled message text

        Returns:
            WhatsApp link
        """
        # Use configured phone number or test number
        phone = self.phone_id or "919876543210"

        # Remove + from phone number if present
        phone = phone.replace('+', '')

        # URL encode the message
        from urllib.parse import quote
        encoded_message = quote(message)

        return f"https://wa.me/{phone}?text={encoded_message}"

    def generate_click_to_chat_link(
        self,
        message: str = "Hi",
        source: str = "",
        campaign: str = ""
    ) -> str:
        """
        Generate tracked WhatsApp link

        Args:
            message: Pre-filled message
            source: Traffic source (e.g., "facebook", "qr_code")
            campaign: Campaign identifier

        Returns:
            Tracked WhatsApp link
        """
        # Build tracking parameters into message
        tracking_suffix = ""
        if source:
            tracking_suffix += f" [src:{source}]"
        if campaign:
            tracking_suffix += f" [cmp:{campaign}]"

        full_message = message + tracking_suffix
        return self.generate_qr_code(full_message)


# Singleton instance
_whatsapp_service = None

def get_whatsapp_service() -> WhatsAppService:
    """Get or create WhatsApp service instance"""
    global _whatsapp_service
    if _whatsapp_service is None:
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service
