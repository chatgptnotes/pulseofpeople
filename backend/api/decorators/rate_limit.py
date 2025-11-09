"""
Rate limiting decorators with role-based limits
Prevents API abuse and ensures fair resource usage
"""
from functools import wraps
from django_ratelimit.decorators import ratelimit
from django.http import JsonResponse
from rest_framework import status


# Role-based rate limits (requests per hour)
ROLE_RATE_LIMITS = {
    'superadmin': '10000/h',  # Unlimited for practical purposes
    'admin': '1000/h',
    'manager': '500/h',
    'analyst': '300/h',
    'user': '100/h',
    'volunteer': '50/h',
    'viewer': '200/h',
    'anonymous': '20/h',  # Unauthenticated users
}


def get_user_rate_limit(request):
    """Determine rate limit based on user role"""
    if not request.user.is_authenticated:
        return ROLE_RATE_LIMITS['anonymous']

    try:
        user_role = request.user.profile.role
        return ROLE_RATE_LIMITS.get(user_role, ROLE_RATE_LIMITS['user'])
    except AttributeError:
        return ROLE_RATE_LIMITS['user']


def role_based_ratelimit(group='', key='user', method='ALL'):
    """
    Rate limit decorator that varies by user role

    Usage:
        @role_based_ratelimit(group='api')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            # Get rate limit for user
            rate = get_user_rate_limit(request)

            # Apply rate limit
            @ratelimit(
                group=group or view_func.__name__,
                key=key,
                rate=rate,
                method=method
            )
            def limited_view(req):
                return view_func(req, *args, **kwargs)

            # Check if rate limited
            response = limited_view(request)

            # If rate limited, return 429 error
            if getattr(request, 'limited', False):
                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'message': f'You have exceeded your rate limit of {rate}',
                        'detail': 'Please try again later or contact support for higher limits'
                    },
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            return response

        return wrapped
    return decorator


def login_ratelimit(view_func):
    """
    Rate limit for login attempts: 5 per 15 minutes
    Prevents brute force attacks
    """
    @wraps(view_func)
    @ratelimit(
        key='ip',
        rate='5/15m',
        method='POST',
        block=True
    )
    def wrapped(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return JsonResponse(
                {
                    'error': 'Too many login attempts',
                    'message': 'You have made too many failed login attempts',
                    'detail': 'Please wait 15 minutes before trying again'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return view_func(request, *args, **kwargs)

    return wrapped


def password_reset_ratelimit(view_func):
    """
    Rate limit for password reset: 3 per hour
    Prevents email spam and abuse
    """
    @wraps(view_func)
    @ratelimit(
        key='ip',
        rate='3/h',
        method='POST',
        block=True
    )
    def wrapped(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return JsonResponse(
                {
                    'error': 'Too many password reset attempts',
                    'message': 'You have requested too many password resets',
                    'detail': 'Please wait 1 hour before trying again'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return view_func(request, *args, **kwargs)

    return wrapped


def file_upload_ratelimit(view_func):
    """
    Rate limit for file uploads: 10 per hour
    Prevents storage abuse
    """
    @wraps(view_func)
    @ratelimit(
        key='user',
        rate='10/h',
        method='POST',
        block=True
    )
    def wrapped(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return JsonResponse(
                {
                    'error': 'Too many file uploads',
                    'message': 'You have uploaded too many files',
                    'detail': 'Maximum 10 uploads per hour. Please try again later.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return view_func(request, *args, **kwargs)

    return wrapped


def bulk_operation_ratelimit(view_func):
    """
    Rate limit for bulk operations: 5 per hour
    Prevents database overload
    """
    @wraps(view_func)
    @ratelimit(
        key='user',
        rate='5/h',
        method='POST',
        block=True
    )
    def wrapped(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return JsonResponse(
                {
                    'error': 'Too many bulk operations',
                    'message': 'You have performed too many bulk operations',
                    'detail': 'Maximum 5 bulk operations per hour. Please try again later.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return view_func(request, *args, **kwargs)

    return wrapped


def api_call_ratelimit(view_func):
    """
    General API rate limit: role-based
    Applied to standard API endpoints
    """
    return role_based_ratelimit(group='api')(view_func)


def search_ratelimit(view_func):
    """
    Rate limit for search operations: 30 per minute
    Prevents search abuse
    """
    @wraps(view_func)
    @ratelimit(
        key='user',
        rate='30/m',
        method='GET',
        block=True
    )
    def wrapped(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return JsonResponse(
                {
                    'error': 'Too many search requests',
                    'message': 'You are searching too frequently',
                    'detail': 'Maximum 30 searches per minute. Please slow down.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return view_func(request, *args, **kwargs)

    return wrapped


def analytics_ratelimit(view_func):
    """
    Rate limit for analytics endpoints: 20 per minute
    These are computationally expensive
    """
    @wraps(view_func)
    @ratelimit(
        key='user',
        rate='20/m',
        method='GET',
        block=True
    )
    def wrapped(request, *args, **kwargs):
        if getattr(request, 'limited', False):
            return JsonResponse(
                {
                    'error': 'Too many analytics requests',
                    'message': 'You are requesting analytics too frequently',
                    'detail': 'Maximum 20 analytics requests per minute. Please wait.'
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        return view_func(request, *args, **kwargs)

    return wrapped
