"""
Audit Logging Middleware

This middleware automatically logs all write operations (POST, PUT, PATCH, DELETE)
to the audit log, with configurable exclusions for certain endpoints.
"""

import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest
from api.utils.audit import log_action

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log write operations to audit log.

    This middleware captures:
    - All POST, PUT, PATCH, DELETE requests
    - Request body (for sensitive endpoints)
    - Response status
    - User information

    Excluded endpoints:
    - Health checks
    - Login/logout (handled separately)
    - Static/media files
    - Admin panel
    """

    # Endpoints to exclude from automatic logging
    EXCLUDED_PATHS = [
        '/api/auth/login/',
        '/api/auth/logout/',
        '/api/auth/refresh/',
        '/api/health/',
        '/api/ping/',
        '/admin/',
        '/static/',
        '/media/',
    ]

    # Methods to log
    LOGGED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']

    # Maximum request body size to log (in bytes)
    MAX_BODY_SIZE = 10000  # 10KB

    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Log the request if applicable
        self._log_request(request, response)

        return response

    def _should_log(self, request: HttpRequest) -> bool:
        """
        Determine if this request should be logged.

        Args:
            request: Django HttpRequest object

        Returns:
            True if request should be logged, False otherwise
        """
        # Only log write operations
        if request.method not in self.LOGGED_METHODS:
            return False

        # Check if path is excluded
        path = request.path
        for excluded_path in self.EXCLUDED_PATHS:
            if path.startswith(excluded_path):
                return False

        # Only log authenticated requests
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False

        return True

    def _extract_resource_info(self, request: HttpRequest) -> tuple:
        """
        Extract resource type and ID from the request path.

        Args:
            request: Django HttpRequest object

        Returns:
            Tuple of (resource_type, resource_id)
        """
        path = request.path
        resource_type = ''
        resource_id = ''

        try:
            # Parse the path to extract resource info
            # Example: /api/users/123/ -> ('User', '123')
            parts = [p for p in path.split('/') if p]

            if len(parts) >= 2:
                # Get the resource type from the path
                resource_path = parts[1] if parts[0] == 'api' else parts[0]

                # Convert plural to singular and capitalize
                resource_type = resource_path.rstrip('s').capitalize()

                # Get resource ID if present
                if len(parts) >= 3:
                    potential_id = parts[2]
                    # Check if it looks like an ID (numeric or UUID)
                    if potential_id.isdigit() or '-' in potential_id:
                        resource_id = potential_id

        except Exception as e:
            logger.debug(f"Failed to extract resource info: {str(e)}")

        return resource_type, resource_id

    def _get_action_from_method(self, method: str, path: str) -> str:
        """
        Determine the action type based on HTTP method and path.

        Args:
            method: HTTP method (POST, PUT, PATCH, DELETE)
            path: Request path

        Returns:
            Action type string
        """
        method_action_map = {
            'POST': 'create',
            'PUT': 'update',
            'PATCH': 'update',
            'DELETE': 'delete'
        }

        base_action = method_action_map.get(method, 'unknown')

        # Check for special endpoints
        if 'bulk' in path.lower():
            return f'bulk_{base_action}'
        elif 'upload' in path.lower():
            return 'upload'

        return base_action

    def _get_request_body(self, request: HttpRequest) -> dict:
        """
        Safely extract and parse request body.

        Args:
            request: Django HttpRequest object

        Returns:
            Dictionary containing parsed request body or error message
        """
        try:
            # Check if body is too large
            if hasattr(request, 'body') and len(request.body) > self.MAX_BODY_SIZE:
                return {'_truncated': True, 'size': len(request.body)}

            # Try to parse JSON body
            if hasattr(request, 'data') and request.data:
                # DRF parsed data
                data = dict(request.data)

                # Remove sensitive fields
                sensitive_fields = ['password', 'token', 'secret', 'api_key']
                for field in sensitive_fields:
                    if field in data:
                        data[field] = '***REDACTED***'

                return data

            # Try to parse raw body
            if hasattr(request, 'body') and request.body:
                body = json.loads(request.body.decode('utf-8'))

                # Remove sensitive fields
                sensitive_fields = ['password', 'token', 'secret', 'api_key']
                for field in sensitive_fields:
                    if field in body:
                        body[field] = '***REDACTED***'

                return body

        except Exception as e:
            logger.debug(f"Failed to parse request body: {str(e)}")

        return {}

    def _log_request(self, request: HttpRequest, response):
        """
        Log the request to the audit log.

        Args:
            request: Django HttpRequest object
            response: Django HttpResponse object
        """
        try:
            # Check if we should log this request
            if not self._should_log(request):
                return

            # Only log successful operations (status < 400)
            if hasattr(response, 'status_code') and response.status_code >= 400:
                return

            # Extract resource information
            resource_type, resource_id = self._extract_resource_info(request)

            # Determine action
            action = self._get_action_from_method(request.method, request.path)

            # Get request body for changes
            request_body = self._get_request_body(request)

            # Prepare changes dictionary
            changes = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code if hasattr(response, 'status_code') else None,
            }

            # Include request body if not empty
            if request_body:
                changes['request_data'] = request_body

            # Log the action
            log_action(
                user=request.user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                changes=changes,
                request=request,
                async_log=True
            )

        except Exception as e:
            # Never let audit logging break the request
            logger.error(f"Failed to log request in middleware: {str(e)}")
