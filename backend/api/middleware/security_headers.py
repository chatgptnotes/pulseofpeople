"""
Security headers middleware
Adds comprehensive security headers to all HTTP responses
"""


class SecurityHeadersMiddleware:
    """
    Middleware to add security headers to all responses
    Protects against common web vulnerabilities
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking attacks
        response['X-Frame-Options'] = 'DENY'

        # Enable XSS protection (legacy browsers)
        response['X-XSS-Protection'] = '1; mode=block'

        # Strict Transport Security (HSTS) - Force HTTPS
        # Only set in production (when not in DEBUG mode)
        if not request.META.get('DEBUG', False):
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'

        # Content Security Policy (CSP)
        # Restricts resource loading to prevent XSS
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
            "font-src 'self' https://fonts.gstatic.com data:",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https://*.supabase.co wss://*.supabase.co https://api.mapbox.com",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'",
        ]
        response['Content-Security-Policy'] = '; '.join(csp_directives)

        # Referrer Policy - Control referrer information
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Permissions Policy (formerly Feature Policy)
        # Restrict access to browser features
        permissions = [
            "geolocation=(self)",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
        ]
        response['Permissions-Policy'] = ', '.join(permissions)

        # Remove server information disclosure
        if 'Server' in response:
            del response['Server']
        if 'X-Powered-By' in response:
            del response['X-Powered-By']

        # Cross-Origin policies
        response['Cross-Origin-Opener-Policy'] = 'same-origin'
        response['Cross-Origin-Resource-Policy'] = 'same-origin'
        response['Cross-Origin-Embedder-Policy'] = 'require-corp'

        return response


class RequestSizeMiddleware:
    """
    Middleware to limit request body size
    Prevents DoS attacks via large payloads
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.max_body_size = 10 * 1024 * 1024  # 10MB default

    def __call__(self, request):
        # Check content length
        content_length = request.META.get('CONTENT_LENGTH')

        if content_length:
            try:
                content_length = int(content_length)
                if content_length > self.max_body_size:
                    from django.http import JsonResponse
                    return JsonResponse(
                        {
                            'error': 'Request too large',
                            'message': f'Request body exceeds maximum size of {self.max_body_size / (1024*1024)}MB',
                            'max_size_mb': self.max_body_size / (1024*1024),
                            'your_size_mb': content_length / (1024*1024)
                        },
                        status=413
                    )
            except ValueError:
                pass

        return self.get_response(request)


class IPWhitelistMiddleware:
    """
    Optional middleware to restrict access to specific IP addresses
    Useful for admin panels or internal APIs
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Add your whitelisted IPs here
        self.whitelisted_ips = [
            '127.0.0.1',
            '::1',  # IPv6 localhost
        ]
        # Paths that require IP whitelisting
        self.protected_paths = [
            '/api/admin/system/',
            '/api/superadmin/critical/',
        ]

    def __call__(self, request):
        # Check if path requires IP whitelisting
        path = request.path
        requires_whitelist = any(path.startswith(protected) for protected in self.protected_paths)

        if requires_whitelist:
            # Get client IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                client_ip = x_forwarded_for.split(',')[0].strip()
            else:
                client_ip = request.META.get('REMOTE_ADDR')

            # Check if IP is whitelisted
            if client_ip not in self.whitelisted_ips:
                from django.http import JsonResponse
                return JsonResponse(
                    {
                        'error': 'Access denied',
                        'message': 'Your IP address is not authorized to access this resource'
                    },
                    status=403
                )

        return self.get_response(request)
