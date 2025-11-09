"""
Supabase JWT Authentication for Django REST Framework
Validates Supabase JWT tokens and syncs with Django User model
"""

import jwt
import logging
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import UserProfile
from .utils import get_user_from_supabase_payload

User = get_user_model()
logger = logging.getLogger('api.authentication')


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests using Supabase JWT tokens
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token)
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            logger.debug('No Bearer token found in Authorization header')
            return None

        token = auth_header.split(' ')[1]

        logger.info(f'Attempting Supabase JWT authentication with token: {token[:20]}...')

        try:
            # Decode and verify the Supabase JWT token
            payload = self.verify_supabase_token(token)
            logger.info(f'Token verified successfully. User ID: {payload.get("sub")}, Email: {payload.get("email")}')

            # Get or create Django user from Supabase user data
            user = self.get_or_create_user(payload)
            logger.info(f'User authenticated: {user.email} (ID: {user.id})')

            return (user, token)

        except jwt.ExpiredSignatureError as e:
            logger.warning(f'Token expired: {str(e)}')
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            logger.warning(f'Invalid token: {str(e)}')
            raise exceptions.AuthenticationFailed('Invalid token')
        except Exception as e:
            logger.error(f'Authentication failed with unexpected error: {str(e)}', exc_info=True)
            raise exceptions.AuthenticationFailed(f'Authentication failed: {str(e)}')

    def verify_supabase_token(self, token):
        """
        Verify the Supabase JWT token using the JWT secret
        """
        supabase_jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)

        if not supabase_jwt_secret:
            logger.error('SUPABASE_JWT_SECRET not configured in settings')
            raise exceptions.AuthenticationFailed('Supabase JWT secret not configured')

        logger.debug(f'Using JWT secret: {supabase_jwt_secret[:10]}...')

        try:
            # Decode the JWT token
            # Note: Supabase uses 'authenticated' as the audience for authenticated users
            payload = jwt.decode(
                token,
                supabase_jwt_secret,
                algorithms=['HS256'],
                audience='authenticated',
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_aud': True,
                }
            )

            logger.debug(f'Token payload: sub={payload.get("sub")}, email={payload.get("email")}, role={payload.get("role")}')
            return payload

        except jwt.ExpiredSignatureError as e:
            logger.warning(f'Token signature expired: {str(e)}')
            raise
        except jwt.InvalidTokenError as e:
            logger.warning(f'Invalid token error: {str(e)}')
            raise
        except Exception as e:
            logger.error(f'Token verification failed with unexpected error: {str(e)}', exc_info=True)
            raise exceptions.AuthenticationFailed(f'Token verification failed: {str(e)}')

    def get_or_create_user(self, payload):
        """
        Get or create Django user from Supabase JWT payload
        Uses the centralized sync utility function for consistency
        """
        try:
            user = get_user_from_supabase_payload(payload)
            return user
        except ValueError as e:
            logger.error(f'User sync failed: {str(e)}')
            raise exceptions.AuthenticationFailed(str(e))
        except Exception as e:
            logger.error(f'Unexpected error during user sync: {str(e)}', exc_info=True)
            raise exceptions.AuthenticationFailed(f'User sync failed: {str(e)}')

    def authenticate_header(self, request):
        """
        Return WWW-Authenticate header for 401 responses
        """
        return 'Bearer realm="api"'


class HybridAuthentication(authentication.BaseAuthentication):
    """
    Try Supabase authentication first, fall back to Django JWT if needed
    This allows both auth methods to work during migration period
    """

    def authenticate(self, request):
        """
        Try Supabase auth first, then fall back to Django JWT
        """
        # Only try Supabase if JWT secret is configured
        supabase_jwt_secret = getattr(settings, 'SUPABASE_JWT_SECRET', None)

        if supabase_jwt_secret:
            # Try Supabase authentication
            try:
                logger.debug('HybridAuth: Attempting Supabase authentication')
                supabase_auth = SupabaseJWTAuthentication()
                result = supabase_auth.authenticate(request)
                if result is not None:
                    logger.info('HybridAuth: Supabase authentication successful')
                    return result
                logger.debug('HybridAuth: Supabase authentication returned None (no Bearer token)')
            except exceptions.AuthenticationFailed as e:
                # If Supabase auth fails with authentication error, log and try Django JWT
                logger.info(f'HybridAuth: Supabase authentication failed: {str(e)}, trying Django JWT fallback')
            except Exception as e:
                # Log unexpected errors
                logger.warning(f'HybridAuth: Supabase authentication error: {str(e)}, trying Django JWT fallback', exc_info=True)

        # Fall back to Django JWT
        from rest_framework_simplejwt.authentication import JWTAuthentication
        django_jwt_auth = JWTAuthentication()

        try:
            logger.debug('HybridAuth: Attempting Django JWT authentication')
            result = django_jwt_auth.authenticate(request)
            if result is not None:
                logger.info('HybridAuth: Django JWT authentication successful')
            else:
                logger.debug('HybridAuth: Django JWT authentication returned None')
            return result
        except Exception as e:
            logger.debug(f'HybridAuth: Django JWT authentication failed: {str(e)}')
            return None

    def authenticate_header(self, request):
        return 'Bearer realm="api"'
