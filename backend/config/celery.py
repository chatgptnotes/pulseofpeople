"""
Celery Configuration for Pulse of People Platform
Handles background tasks and scheduled reports
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create Celery app
app = Celery('pulseofpeople')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django app configs
app.autodiscover_tasks()

# Celery Beat Schedule for Automated Reports
app.conf.beat_schedule = {
    # Daily Report - Runs every day at 6 PM
    'daily-activity-report': {
        'task': 'api.tasks.generate_daily_report',
        'schedule': crontab(hour=18, minute=0),
        'options': {
            'expires': 3600,  # Task expires after 1 hour
        }
    },

    # Weekly Report - Runs every Monday at 9 AM
    'weekly-summary-report': {
        'task': 'api.tasks.generate_weekly_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),
        'options': {
            'expires': 7200,
        }
    },

    # Monthly Report - Runs on 1st of every month at 10 AM
    'monthly-comprehensive-report': {
        'task': 'api.tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=10, minute=0),
        'options': {
            'expires': 7200,
        }
    },

    # Cleanup expired reports - Runs daily at midnight
    'cleanup-expired-reports': {
        'task': 'api.tasks.cleanup_expired_reports',
        'schedule': crontab(hour=0, minute=0),
    },

    # Cleanup expired exports - Runs daily at 12:30 AM
    'cleanup-expired-exports': {
        'task': 'api.tasks.cleanup_expired_exports',
        'schedule': crontab(hour=0, minute=30),
    },

    # Aggregate analytics data - Runs hourly
    'aggregate-analytics-hourly': {
        'task': 'api.tasks.aggregate_analytics_task',
        'schedule': crontab(minute=0),  # Every hour at minute 0
        'options': {
            'expires': 3600,
        }
    },
}

# Celery Configuration
app.conf.update(
    # Time zone
    timezone='Asia/Kolkata',
    enable_utc=True,

    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes

    # Result backend
    result_backend='redis://localhost:6379/0',
    result_expires=3600,  # 1 hour

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Broker settings
    broker_connection_retry_on_startup=True,
)


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f'Request: {self.request!r}')
    return 'Celery is working!'
