"""
Production settings for Pulse of People platform.

This settings file is optimized for production deployment on Railway/Render/AWS.
It includes security hardening, performance optimizations, and proper logging.

Usage:
    Set environment variable: DJANGO_SETTINGS_MODULE=config.settings_production
    Or use: python manage.py runserver --settings=config.settings_production
"""

from .settings import *
import os

# ============================================
# SECURITY SETTINGS
# ============================================

DEBUG = False

# This should be set via environment variable
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")

# Allowed hosts from environment
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['']:
    raise ValueError("ALLOWED_HOSTS must be configured in production")

# Security middleware configuration
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# CSRF security
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ============================================
# DATABASE CONFIGURATION
# ============================================

# Force PostgreSQL in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', '600')),
        'CONN_HEALTH_CHECKS': True,
        'OPTIONS': {
            'sslmode': os.environ.get('DB_SSLMODE', 'require'),
            'connect_timeout': 10,
        },
    }
}

# Validate database configuration
for key in ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']:
    if not os.environ.get(key):
        raise ValueError(f"{key} environment variable must be set in production")

# ============================================
# CACHING (Redis)
# ============================================

REDIS_URL = os.environ.get('REDIS_URL')

if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'PASSWORD': os.environ.get('REDIS_PASSWORD', ''),
                'SOCKET_CONNECT_TIMEOUT': 5,
                'SOCKET_TIMEOUT': 5,
                'RETRY_ON_TIMEOUT': True,
                'MAX_CONNECTIONS': 50,
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
            },
            'KEY_PREFIX': 'pulseofpeople',
            'TIMEOUT': 300,  # 5 minutes default
        }
    }

    # Session backend
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
else:
    # Fallback to database cache if Redis not available
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            'LOCATION': 'cache_table',
        }
    }

# ============================================
# STATIC FILES & MEDIA
# ============================================

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# AWS S3 Configuration (if enabled)
USE_S3 = os.environ.get('USE_S3', 'False') == 'True'

if USE_S3:
    # Add 'storages' to INSTALLED_APPS if using S3
    INSTALLED_APPS += ['storages']

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-south-1')
    AWS_S3_CUSTOM_DOMAIN = os.environ.get('AWS_S3_CUSTOM_DOMAIN', f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com')
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 1 day
    }

    # Static files via S3
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'

    # Media files via S3
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# ============================================
# EMAIL CONFIGURATION
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@pulseofpeople.com')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'alerts@pulseofpeople.com')

# Email timeout
EMAIL_TIMEOUT = 30

# ============================================
# LOGGING CONFIGURATION
# ============================================

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.environ.get('LOG_FILE_PATH', '/var/log/pulseofpeople/django.log'),
            'maxBytes': int(os.environ.get('LOG_MAX_BYTES', '10485760')),  # 10MB
            'backupCount': int(os.environ.get('LOG_BACKUP_COUNT', '10')),
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'api': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
}

# ============================================
# CELERY CONFIGURATION
# ============================================

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)

# Celery settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = os.environ.get('CELERY_TIMEZONE', 'Asia/Kolkata')
CELERY_ENABLE_UTC = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Beat schedule for periodic tasks
CELERY_BEAT_SCHEDULE = {
    'cleanup-expired-tokens': {
        'task': 'api.tasks.cleanup_expired_tokens',
        'schedule': 86400.0,  # Daily
    },
    'generate-daily-reports': {
        'task': 'api.tasks.generate_daily_reports',
        'schedule': 86400.0,  # Daily at midnight
    },
    'sync-social-media-data': {
        'task': 'api.tasks.sync_social_media_data',
        'schedule': 3600.0,  # Hourly
    },
}

# ============================================
# MONITORING (Sentry)
# ============================================

SENTRY_DSN = os.environ.get('SENTRY_DSN')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        environment=os.environ.get('SENTRY_ENVIRONMENT', 'production'),
        traces_sample_rate=float(os.environ.get('SENTRY_TRACES_SAMPLE_RATE', '0.1')),
        profiles_sample_rate=float(os.environ.get('SENTRY_PROFILES_SAMPLE_RATE', '0.1')),
        send_default_pii=False,
        attach_stacktrace=True,
        request_bodies='medium',
    )

# ============================================
# CORS CONFIGURATION
# ============================================

# Parse CORS origins from environment
cors_origins_raw = os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins_raw if origin.strip()]

# Validate CORS configuration
if not CORS_ALLOWED_ORIGINS:
    raise ValueError("CORS_ALLOWED_ORIGINS must be configured in production")

CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = False

# CSRF trusted origins
csrf_origins_raw = os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in csrf_origins_raw if origin.strip()]

# ============================================
# REST FRAMEWORK PRODUCTION SETTINGS
# ============================================

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

# Stricter throttling in production
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': os.environ.get('RATE_LIMIT_ANON', '100/hour'),
    'user': os.environ.get('RATE_LIMIT_USER', '1000/hour'),
    'admin': os.environ.get('RATE_LIMIT_ADMIN', '5000/hour'),
}

# ============================================
# JWT PRODUCTION SETTINGS
# ============================================

SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_LIFETIME', '15')))
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(minutes=int(os.environ.get('JWT_REFRESH_TOKEN_LIFETIME', '10080')))
SIMPLE_JWT['SIGNING_KEY'] = os.environ.get('JWT_SECRET_KEY', SECRET_KEY)

# ============================================
# ADMIN CONFIGURATION
# ============================================

# Disable admin in production if needed
ENABLE_ADMIN_PANEL = os.environ.get('ENABLE_ADMIN_PANEL', 'True') == 'True'

if not ENABLE_ADMIN_PANEL:
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.admin']

# ============================================
# ADDITIONAL SECURITY MEASURES
# ============================================

# Disable browsable API in production
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [
    'rest_framework.renderers.JSONRenderer',
]

# Password validation (stricter in production)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ============================================
# PERFORMANCE OPTIMIZATIONS
# ============================================

# Database query optimization
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Template caching
if not DEBUG:
    TEMPLATES[0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]

# ============================================
# FEATURE FLAGS
# ============================================

ENABLE_NOTIFICATIONS = os.environ.get('ENABLE_NOTIFICATIONS', 'True') == 'True'
ENABLE_EMAIL_NOTIFICATIONS = os.environ.get('ENABLE_EMAIL_NOTIFICATIONS', 'True') == 'True'
ENABLE_SMS_NOTIFICATIONS = os.environ.get('ENABLE_SMS_NOTIFICATIONS', 'True') == 'True'
ENABLE_FILE_UPLOAD = os.environ.get('ENABLE_FILE_UPLOAD', 'True') == 'True'
ENABLE_SENTIMENT_ANALYSIS = os.environ.get('ENABLE_SENTIMENT_ANALYSIS', 'True') == 'True'
ENABLE_AUDIT_LOGGING = os.environ.get('ENABLE_AUDIT_LOGGING', 'True') == 'True'
ENABLE_REALTIME = os.environ.get('ENABLE_REALTIME', 'True') == 'True'
ENABLE_2FA = os.environ.get('ENABLE_2FA', 'True') == 'True'

# ============================================
# DEPLOYMENT METADATA
# ============================================

DEPLOYMENT_PLATFORM = os.environ.get('DEPLOYMENT_PLATFORM', 'railway')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')
VERSION = os.environ.get('VERSION', '1.0.0')
BUILD_NUMBER = os.environ.get('BUILD_NUMBER', 'unknown')
COMMIT_HASH = os.environ.get('COMMIT_HASH', 'unknown')

print(f"""
🚀 Production Settings Loaded
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Environment: {ENVIRONMENT}
Version: {VERSION}
Platform: {DEPLOYMENT_PLATFORM}
Debug: {DEBUG}
Database: {DATABASES['default']['NAME']}@{DATABASES['default']['HOST']}
Cache: {'Redis' if REDIS_URL else 'Database'}
Static: {'S3' if USE_S3 else 'Local'}
Sentry: {'✓' if SENTRY_DSN else '✗'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
