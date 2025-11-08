"""
Audit Logging Utility

This module provides utilities for comprehensive audit logging throughout the application.
It handles:
- Extracting request metadata (IP, user agent)
- Asynchronous logging to avoid blocking requests
- Error handling to ensure logging failures don't break requests
- Before/after state capture for updates
"""

import json
import logging
from typing import Dict, Any, Optional
from django.contrib.auth.models import User
from django.http import HttpRequest
from api.models import AuditLog
from threading import Thread

logger = logging.getLogger(__name__)


def get_client_ip(request: HttpRequest) -> str:
    """
    Extract client IP address from request, considering proxy headers.

    Args:
        request: Django HttpRequest object

    Returns:
        Client IP address as string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_user_agent(request: HttpRequest) -> str:
    """
    Extract user agent string from request.

    Args:
        request: Django HttpRequest object

    Returns:
        User agent string, truncated to 500 characters
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    # Truncate to avoid excessively long strings
    return user_agent[:500]


def log_action(
    user: Optional[User],
    action: str,
    resource_type: str = '',
    resource_id: str = '',
    changes: Optional[Dict[str, Any]] = None,
    request: Optional[HttpRequest] = None,
    async_log: bool = True
) -> Optional[AuditLog]:
    """
    Log an action to the audit log.

    This function is safe to call - it will never raise an exception that could
    break the main request flow. Logging is performed asynchronously by default.

    Args:
        user: User performing the action (can be None for anonymous actions)
        action: Action type (e.g., 'user_created', 'login_success')
        resource_type: Type of resource being acted upon (e.g., 'User', 'PollingBooth')
        resource_id: ID of the resource (as string)
        changes: Dictionary containing before/after state or other metadata
        request: Django HttpRequest object (for IP and user agent extraction)
        async_log: Whether to log asynchronously (default: True)

    Returns:
        AuditLog instance if successful (and not async), None otherwise

    Example:
        log_action(
            user=request.user,
            action='user_created',
            resource_type='User',
            resource_id=str(new_user.id),
            changes={'username': new_user.username, 'role': 'analyst'},
            request=request
        )
    """
    try:
        # Extract request metadata
        ip_address = None
        user_agent = None
        if request:
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)

        # Prepare audit log data
        audit_data = {
            'user': user,
            'action': action,
            'target_model': resource_type,
            'target_id': str(resource_id) if resource_id else '',
            'changes': changes or {},
            'ip_address': ip_address,
            'user_agent': user_agent
        }

        if async_log:
            # Log asynchronously to avoid blocking the request
            thread = Thread(target=_create_audit_log, args=(audit_data,))
            thread.daemon = True
            thread.start()
            return None
        else:
            # Log synchronously (useful for testing or critical operations)
            return _create_audit_log(audit_data)

    except Exception as e:
        # Never let audit logging break the main request
        logger.error(f"Failed to log action: {action} for user {user}. Error: {str(e)}")
        return None


def _create_audit_log(audit_data: Dict[str, Any]) -> Optional[AuditLog]:
    """
    Internal function to create the audit log entry.

    Args:
        audit_data: Dictionary containing audit log fields

    Returns:
        Created AuditLog instance or None if failed
    """
    try:
        audit_log = AuditLog.objects.create(**audit_data)
        return audit_log
    except Exception as e:
        logger.error(f"Failed to create audit log entry: {str(e)}")
        return None


def capture_model_state(instance) -> Dict[str, Any]:
    """
    Capture the current state of a model instance for audit logging.

    Args:
        instance: Django model instance

    Returns:
        Dictionary containing field names and their serialized values

    Example:
        before_state = capture_model_state(user)
        user.role = 'admin'
        user.save()
        after_state = capture_model_state(user)
        log_action(user, 'role_changed', 'User', user.id, {
            'before': before_state,
            'after': after_state
        })
    """
    state = {}

    try:
        # Get all fields from the model
        for field in instance._meta.fields:
            field_name = field.name
            field_value = getattr(instance, field_name, None)

            # Serialize the value
            if field_value is None:
                state[field_name] = None
            elif hasattr(field_value, 'pk'):
                # Foreign key - store the ID
                state[field_name] = field_value.pk
            elif isinstance(field_value, (str, int, float, bool)):
                state[field_name] = field_value
            else:
                # For other types, convert to string
                state[field_name] = str(field_value)

    except Exception as e:
        logger.error(f"Failed to capture model state: {str(e)}")

    return state


def get_field_changes(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate the difference between two state dictionaries.

    Args:
        before: State before changes
        after: State after changes

    Returns:
        Dictionary containing only changed fields with before/after values

    Example:
        changes = get_field_changes(
            {'role': 'user', 'name': 'John'},
            {'role': 'admin', 'name': 'John'}
        )
        # Returns: {'role': {'before': 'user', 'after': 'admin'}}
    """
    changes = {}

    try:
        # Find all fields that exist in either dict
        all_fields = set(before.keys()) | set(after.keys())

        for field in all_fields:
            before_value = before.get(field)
            after_value = after.get(field)

            # Check if values are different
            if before_value != after_value:
                changes[field] = {
                    'before': before_value,
                    'after': after_value
                }

    except Exception as e:
        logger.error(f"Failed to calculate field changes: {str(e)}")

    return changes


# Action type constants for consistency
ACTION_USER_CREATED = 'user_created'
ACTION_USER_UPDATED = 'user_updated'
ACTION_USER_DELETED = 'user_deleted'
ACTION_ROLE_CHANGED = 'role_changed'
ACTION_PERMISSION_GRANTED = 'permission_granted'
ACTION_PERMISSION_REVOKED = 'permission_revoked'
ACTION_BOOTH_CREATED = 'booth_created'
ACTION_BOOTH_UPLOADED = 'booth_uploaded'
ACTION_BOOTH_DELETED = 'booth_deleted'
ACTION_REPORT_SUBMITTED = 'report_submitted'
ACTION_REPORT_REVIEWED = 'report_reviewed'
ACTION_LOGIN_SUCCESS = 'login_success'
ACTION_LOGIN_FAILED = 'login_failed'
ACTION_LOGOUT = 'logout'
ACTION_PASSWORD_CHANGED = 'password_changed'
ACTION_SETTINGS_UPDATED = 'settings_updated'
ACTION_ORGANIZATION_CREATED = 'organization_created'
ACTION_ORGANIZATION_UPDATED = 'organization_updated'
ACTION_BULK_UPLOAD_STARTED = 'bulk_upload_started'
ACTION_BULK_UPLOAD_COMPLETED = 'bulk_upload_completed'
