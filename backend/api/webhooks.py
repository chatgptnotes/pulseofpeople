"""
Webhook handlers for Supabase events
Handles user creation, updates, and deletion events from Supabase
"""

import logging
import hmac
import hashlib
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .utils import (
    sync_supabase_user,
    handle_user_email_change,
    handle_user_deletion
)

logger = logging.getLogger(__name__)


def verify_supabase_webhook_signature(request):
    """
    Verify that the webhook request is from Supabase
    Uses HMAC signature verification

    Args:
        request: Django request object

    Returns:
        bool: True if signature is valid, False otherwise
    """
    webhook_secret = getattr(settings, 'SUPABASE_WEBHOOK_SECRET', None)
    if not webhook_secret:
        logger.warning('SUPABASE_WEBHOOK_SECRET not configured - skipping verification')
        return True  # Allow in development

    signature = request.headers.get('X-Supabase-Signature')
    if not signature:
        logger.warning('No X-Supabase-Signature header found')
        return False

    # Calculate expected signature
    expected_signature = hmac.new(
        webhook_secret.encode('utf-8'),
        request.body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)


@csrf_exempt
@require_POST
def supabase_user_webhook(request):
    """
    Handle Supabase user events via webhook
    Supported events:
    - user.created: New user registered
    - user.updated: User information updated
    - user.deleted: User deleted
    - user.email_changed: User email changed

    Expected payload format:
    {
        "type": "user.created",
        "user": {
            "id": "uuid",
            "email": "user@example.com",
            "user_metadata": {...},
            "app_metadata": {...}
        }
    }
    """
    # Verify webhook signature
    if not verify_supabase_webhook_signature(request):
        logger.warning('Invalid webhook signature')
        return JsonResponse({'error': 'Invalid signature'}, status=401)

    import json

    try:
        payload = json.loads(request.body)
        event_type = payload.get('type')
        user_data = payload.get('user', {})

        logger.info(f'Received Supabase webhook: {event_type}')

        if event_type == 'user.created':
            return handle_user_created(user_data)
        elif event_type == 'user.updated':
            return handle_user_updated(user_data)
        elif event_type == 'user.deleted':
            return handle_user_deleted_event(user_data)
        elif event_type == 'user.email_changed':
            return handle_email_changed(payload)
        else:
            logger.warning(f'Unknown event type: {event_type}')
            return JsonResponse({'error': 'Unknown event type'}, status=400)

    except json.JSONDecodeError:
        logger.error('Invalid JSON payload')
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f'Webhook processing failed: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def handle_user_created(user_data):
    """Handle user.created event"""
    try:
        user_id = user_data.get('id')
        email = user_data.get('email')
        user_metadata = user_data.get('user_metadata', {})
        app_metadata = user_data.get('app_metadata', {})

        logger.info(f'Creating user from webhook: {email}')

        user = sync_supabase_user(
            supabase_user_id=user_id,
            email=email,
            user_metadata=user_metadata,
            app_metadata=app_metadata
        )

        return JsonResponse({
            'status': 'success',
            'message': 'User created',
            'user_id': user.id,
            'email': user.email
        })

    except Exception as e:
        logger.error(f'Failed to create user: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def handle_user_updated(user_data):
    """Handle user.updated event"""
    try:
        user_id = user_data.get('id')
        email = user_data.get('email')
        user_metadata = user_data.get('user_metadata', {})
        app_metadata = user_data.get('app_metadata', {})

        logger.info(f'Updating user from webhook: {email}')

        user = sync_supabase_user(
            supabase_user_id=user_id,
            email=email,
            user_metadata=user_metadata,
            app_metadata=app_metadata
        )

        return JsonResponse({
            'status': 'success',
            'message': 'User updated',
            'user_id': user.id,
            'email': user.email
        })

    except Exception as e:
        logger.error(f'Failed to update user: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def handle_user_deleted_event(user_data):
    """Handle user.deleted event"""
    try:
        email = user_data.get('email')
        user_id = user_data.get('id')

        logger.info(f'Deleting user from webhook: {email}')

        success = handle_user_deletion(email=email, supabase_user_id=user_id)

        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'User deactivated',
                'email': email
            })
        else:
            return JsonResponse({
                'status': 'warning',
                'message': 'User not found',
                'email': email
            }, status=404)

    except Exception as e:
        logger.error(f'Failed to delete user: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)


def handle_email_changed(payload):
    """Handle user.email_changed event"""
    try:
        old_email = payload.get('old_email')
        new_email = payload.get('new_email')

        logger.info(f'Changing user email: {old_email} -> {new_email}')

        user = handle_user_email_change(old_email, new_email)

        return JsonResponse({
            'status': 'success',
            'message': 'Email updated',
            'user_id': user.id,
            'old_email': old_email,
            'new_email': new_email
        })

    except ValueError as e:
        logger.error(f'Failed to change email: {str(e)}')
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f'Failed to change email: {str(e)}', exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
