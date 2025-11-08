"""
Audit Logging Decorators

This module provides decorators for automatic audit logging of view functions and methods.
"""

from functools import wraps
from typing import Callable, Optional
from django.http import HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework import status as drf_status
from api.utils.audit import log_action, capture_model_state, get_field_changes
import logging

logger = logging.getLogger(__name__)


def audit_log(
    action: str,
    resource_type: str = '',
    resource_id_param: str = 'pk',
    capture_changes: bool = False,
    async_log: bool = True
):
    """
    Decorator for automatic audit logging of view functions.

    This decorator automatically logs actions when views are called, extracting
    the necessary information from the request and view parameters.

    Args:
        action: Action type to log (e.g., 'user_created', 'user_updated')
        resource_type: Type of resource being acted upon (e.g., 'User', 'PollingBooth')
        resource_id_param: Name of the parameter containing the resource ID (default: 'pk')
        capture_changes: Whether to capture before/after state for updates (default: False)
        async_log: Whether to log asynchronously (default: True)

    Returns:
        Decorated function

    Example:
        @api_view(['POST'])
        @permission_classes([IsAuthenticated])
        @audit_log(action='user_created', resource_type='User')
        def create_user(request):
            # ... create user logic ...
            return Response(data)

        @api_view(['PATCH'])
        @permission_classes([IsAuthenticated])
        @audit_log(action='user_updated', resource_type='User', capture_changes=True)
        def update_user(request, pk):
            # ... update user logic ...
            return Response(data)
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request_or_self, *args, **kwargs):
            # Determine if this is a function-based view or class-based view
            if isinstance(request_or_self, HttpRequest):
                # Function-based view
                request = request_or_self
                user = getattr(request, 'user', None)
            else:
                # Class-based view (ViewSet) - first arg is self, second is request
                request = args[0] if args else None
                user = getattr(request, 'user', None) if request else None

            # Extract resource ID from kwargs
            resource_id = kwargs.get(resource_id_param, '')

            # Capture before state if requested
            before_state = None
            if capture_changes and resource_id:
                try:
                    # This is a placeholder - actual implementation would need
                    # to fetch the model instance before changes
                    # For now, we'll capture changes in the view itself
                    pass
                except Exception as e:
                    logger.error(f"Failed to capture before state: {str(e)}")

            # Execute the view
            response = view_func(request_or_self, *args, **kwargs)

            # Log the action after successful execution
            try:
                # Only log if the response was successful
                should_log = False
                changes = {}

                if isinstance(response, Response):
                    # DRF Response
                    if response.status_code < 400:
                        should_log = True
                        # Try to extract resource_id from response if not in kwargs
                        if not resource_id and hasattr(response, 'data'):
                            if isinstance(response.data, dict):
                                resource_id = response.data.get('id', response.data.get('user_id', ''))
                elif isinstance(response, HttpResponse):
                    # Django HttpResponse
                    if response.status_code < 400:
                        should_log = True

                if should_log and user and user.is_authenticated:
                    # Log the action
                    log_action(
                        user=user,
                        action=action,
                        resource_type=resource_type,
                        resource_id=str(resource_id) if resource_id else '',
                        changes=changes,
                        request=request,
                        async_log=async_log
                    )

            except Exception as e:
                # Never let audit logging break the response
                logger.error(f"Failed to log action in decorator: {str(e)}")

            return response

        return wrapper
    return decorator


def audit_log_method(action: str, resource_type: str = '', capture_changes: bool = False):
    """
    Decorator for audit logging of ViewSet methods.

    This is specifically designed for DRF ViewSet methods (create, update, destroy, etc.)

    Args:
        action: Action type to log
        resource_type: Type of resource being acted upon
        capture_changes: Whether to capture before/after state

    Returns:
        Decorated method

    Example:
        class UserViewSet(viewsets.ModelViewSet):
            @audit_log_method(action='user_created', resource_type='User')
            def create(self, request, *args, **kwargs):
                # ... create logic ...
                return super().create(request, *args, **kwargs)

            @audit_log_method(action='user_updated', resource_type='User', capture_changes=True)
            def update(self, request, *args, **kwargs):
                # ... update logic ...
                return super().update(request, *args, **kwargs)
    """
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self, request, *args, **kwargs):
            user = getattr(request, 'user', None)
            resource_id = kwargs.get('pk', '')

            # Capture before state for updates
            before_state = None
            if capture_changes and resource_id and hasattr(self, 'get_object'):
                try:
                    obj = self.get_object()
                    before_state = capture_model_state(obj)
                except Exception as e:
                    logger.error(f"Failed to capture before state: {str(e)}")

            # Execute the method
            response = method(self, request, *args, **kwargs)

            # Log the action after successful execution
            try:
                if isinstance(response, Response) and response.status_code < 400:
                    changes = {}

                    # Capture after state and calculate changes
                    if capture_changes and before_state and resource_id:
                        try:
                            obj = self.get_object()
                            after_state = capture_model_state(obj)
                            field_changes = get_field_changes(before_state, after_state)
                            if field_changes:
                                changes = {
                                    'fields_changed': field_changes,
                                    'change_count': len(field_changes)
                                }
                        except Exception as e:
                            logger.error(f"Failed to capture after state: {str(e)}")

                    # Extract resource_id from response if not in kwargs
                    if not resource_id and hasattr(response, 'data') and isinstance(response.data, dict):
                        resource_id = response.data.get('id', '')

                    # Log the action
                    if user and user.is_authenticated:
                        log_action(
                            user=user,
                            action=action,
                            resource_type=resource_type,
                            resource_id=str(resource_id) if resource_id else '',
                            changes=changes,
                            request=request
                        )

            except Exception as e:
                logger.error(f"Failed to log action in method decorator: {str(e)}")

            return response

        return wrapper
    return decorator


def audit_login(view_func: Callable) -> Callable:
    """
    Decorator specifically for login views to log both successful and failed attempts.

    Example:
        @api_view(['POST'])
        @audit_login
        def login_view(request):
            # ... login logic ...
            return Response(data)
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Execute the view
        response = view_func(request, *args, **kwargs)

        try:
            # Determine if login was successful based on response
            is_success = False
            user = None
            username = ''

            if isinstance(response, Response):
                if response.status_code == 200 or response.status_code == 201:
                    is_success = True
                    # Try to get user from response or request
                    user = getattr(request, 'user', None)
                    if hasattr(response, 'data') and isinstance(response.data, dict):
                        username = response.data.get('username', response.data.get('email', ''))

            # Get username from request if not from response
            if not username and hasattr(request, 'data'):
                username = request.data.get('username', request.data.get('email', ''))

            # Log the login attempt
            action = 'login_success' if is_success else 'login_failed'
            changes = {'username': username} if username else {}

            log_action(
                user=user if is_success else None,
                action=action,
                resource_type='Authentication',
                resource_id='',
                changes=changes,
                request=request
            )

        except Exception as e:
            logger.error(f"Failed to log login attempt: {str(e)}")

        return response

    return wrapper
