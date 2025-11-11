"""
Health check endpoints for monitoring and load balancers.

Provides comprehensive health status for:
- Database connectivity
- Redis cache
- Celery workers
- External service dependencies
- System resources
"""

from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import time
import psutil
import os


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint.
    Returns 200 if application is running.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
    }

    return JsonResponse(health_status, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """
    Detailed health check with all dependencies.
    Returns component-level health status.
    """
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
        'components': {}
    }

    overall_healthy = True

    # Check database
    db_status = check_database()
    health_status['components']['database'] = db_status
    if not db_status['healthy']:
        overall_healthy = False

    # Check cache/Redis
    cache_status = check_cache()
    health_status['components']['cache'] = cache_status
    if not cache_status['healthy']:
        overall_healthy = False

    # Check Celery
    celery_status = check_celery()
    health_status['components']['celery'] = celery_status
    # Don't mark overall as unhealthy if only Celery is down
    # It's a warning but not critical

    # Check disk space
    disk_status = check_disk_space()
    health_status['components']['disk'] = disk_status
    if not disk_status['healthy']:
        overall_healthy = False

    # Check memory
    memory_status = check_memory()
    health_status['components']['memory'] = memory_status
    # Memory is informational, don't fail health check

    # Set overall status
    health_status['status'] = 'healthy' if overall_healthy else 'unhealthy'

    # Return appropriate status code
    status_code = 200 if overall_healthy else 503

    return JsonResponse(health_status, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_probe(request):
    """
    Kubernetes liveness probe.
    Simple check to see if the application is running.
    """
    return JsonResponse({'status': 'alive'}, status=200)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_probe(request):
    """
    Kubernetes readiness probe.
    Checks if the application is ready to receive traffic.
    """
    ready = True
    components = {}

    # Check critical components only
    db_status = check_database()
    components['database'] = db_status['healthy']
    if not db_status['healthy']:
        ready = False

    cache_status = check_cache()
    components['cache'] = cache_status['healthy']
    # Cache is not critical for readiness

    readiness_status = {
        'status': 'ready' if ready else 'not_ready',
        'components': components
    }

    status_code = 200 if ready else 503
    return JsonResponse(readiness_status, status=status_code)


def check_database():
    """Check database connectivity and basic operations."""
    try:
        start_time = time.time()

        # Execute a simple query
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        response_time = (time.time() - start_time) * 1000  # Convert to ms

        return {
            'healthy': True,
            'response_time_ms': round(response_time, 2),
            'message': 'Database connection successful'
        }
    except Exception as e:
        return {
            'healthy': False,
            'error': str(e),
            'message': 'Database connection failed'
        }


def check_cache():
    """Check Redis cache connectivity."""
    try:
        start_time = time.time()

        # Test cache operations
        test_key = 'health_check_test'
        test_value = 'ok'

        cache.set(test_key, test_value, 10)
        result = cache.get(test_key)
        cache.delete(test_key)

        response_time = (time.time() - start_time) * 1000

        if result != test_value:
            raise Exception("Cache read/write mismatch")

        return {
            'healthy': True,
            'response_time_ms': round(response_time, 2),
            'message': 'Cache connection successful'
        }
    except Exception as e:
        return {
            'healthy': False,
            'error': str(e),
            'message': 'Cache connection failed'
        }


def check_celery():
    """Check Celery worker status."""
    try:
        from celery import current_app

        # Get worker statistics
        stats = current_app.control.inspect().stats()

        if stats:
            worker_count = len(stats)
            return {
                'healthy': True,
                'workers': worker_count,
                'message': f'{worker_count} worker(s) active'
            }
        else:
            return {
                'healthy': False,
                'workers': 0,
                'message': 'No workers available'
            }
    except Exception as e:
        return {
            'healthy': False,
            'error': str(e),
            'message': 'Celery check failed'
        }


def check_disk_space():
    """Check available disk space."""
    try:
        disk = psutil.disk_usage('/')
        percent_used = disk.percent
        gb_free = disk.free / (1024 ** 3)

        # Consider unhealthy if less than 1GB free or more than 90% used
        healthy = gb_free > 1.0 and percent_used < 90

        status = 'healthy' if healthy else 'low_space'

        return {
            'healthy': healthy,
            'total_gb': round(disk.total / (1024 ** 3), 2),
            'used_gb': round(disk.used / (1024 ** 3), 2),
            'free_gb': round(gb_free, 2),
            'percent_used': percent_used,
            'status': status
        }
    except Exception as e:
        return {
            'healthy': True,  # Don't fail if we can't check
            'error': str(e),
            'message': 'Disk space check unavailable'
        }


def check_memory():
    """Check system memory usage."""
    try:
        memory = psutil.virtual_memory()
        percent_used = memory.percent
        gb_available = memory.available / (1024 ** 3)

        return {
            'healthy': True,  # Informational only
            'total_gb': round(memory.total / (1024 ** 3), 2),
            'used_gb': round(memory.used / (1024 ** 3), 2),
            'available_gb': round(gb_available, 2),
            'percent_used': percent_used,
            'status': 'normal' if percent_used < 90 else 'high_usage'
        }
    except Exception as e:
        return {
            'healthy': True,  # Don't fail if we can't check
            'error': str(e),
            'message': 'Memory check unavailable'
        }


@api_view(['GET'])
@permission_classes([AllowAny])
def version_info(request):
    """
    Return application version and build information.
    """
    version_data = {
        'version': getattr(settings, 'VERSION', '1.0.0'),
        'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
        'build_number': getattr(settings, 'BUILD_NUMBER', 'unknown'),
        'commit_hash': getattr(settings, 'COMMIT_HASH', 'unknown'),
        'deployment_platform': getattr(settings, 'DEPLOYMENT_PLATFORM', 'unknown'),
        'python_version': os.sys.version,
        'django_version': __import__('django').get_version(),
    }

    return JsonResponse(version_data, status=200)
