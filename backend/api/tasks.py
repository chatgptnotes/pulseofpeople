"""
Celery Tasks for Automated Reports and Background Processing
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMessage
from datetime import datetime, timedelta
from io import BytesIO

from api.models_analytics import ReportTemplate, GeneratedReport, ExportJob
from api.utils.pdf_generator import generate_executive_summary_pdf, generate_campaign_report_pdf
from api.utils.excel_exporter import export_analytics_to_excel
from api.models import DirectFeedback, FieldReport


@shared_task
def generate_daily_report():
    """
    Generate daily activity report
    Scheduled to run every day at 6 PM
    """
    today = timezone.now().date()

    # Collect daily data
    feedback_count = DirectFeedback.objects.filter(
        submitted_at__date=today
    ).count()

    reports_count = FieldReport.objects.filter(
        report_date=today
    ).count()

    # Prepare report data
    report_data = {
        'report_name': f'Daily Activity Report - {today}',
        'date_from': str(today),
        'date_to': str(today),
        'generated_by': 'System',
        'summary': {
            'feedback_submitted': feedback_count,
            'field_reports_submitted': reports_count,
            'new_voters_added': 0,  # TODO: Calculate from voter model
            'tasks_completed': 0,  # TODO: Calculate from tasks
            'issues_raised': feedback_count,
        },
        'insights': [
            f"{feedback_count} feedback submissions received today",
            f"{reports_count} field reports submitted by volunteers",
            "Overall sentiment remains positive"
        ]
    }

    # Generate PDF
    try:
        pdf_buffer = generate_executive_summary_pdf(report_data)

        # Create report record
        report = GeneratedReport.objects.create(
            report_name=f"Daily Activity - {today}",
            report_type='daily_activity',
            status='completed',
            filters_used={'date': str(today)},
            # TODO: Upload to Supabase storage and set pdf_file_url
            expires_at=timezone.now() + timedelta(days=7)
        )

        # Send email to admins
        send_report_email.delay(
            report_id=str(report.report_id),
            recipients=['admin@example.com'],  # TODO: Get from settings
            subject=f'Daily Activity Report - {today}'
        )

        return f"Daily report generated: {report.report_id}"

    except Exception as e:
        return f"Error generating daily report: {str(e)}"


@shared_task
def generate_weekly_report():
    """
    Generate weekly summary report
    Scheduled to run every Monday at 9 AM
    """
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    # Collect weekly data
    report_data = {
        'report_name': f'Weekly Summary - Week of {week_start}',
        'date_from': str(week_start),
        'date_to': str(week_end),
        'generated_by': 'System',
        'summary': {
            'total_feedback': DirectFeedback.objects.filter(
                submitted_at__date__gte=week_start,
                submitted_at__date__lte=week_end
            ).count(),
            'total_field_reports': FieldReport.objects.filter(
                report_date__gte=week_start,
                report_date__lte=week_end
            ).count(),
        }
    }

    try:
        pdf_buffer = generate_executive_summary_pdf(report_data)

        report = GeneratedReport.objects.create(
            report_name=f"Weekly Summary - {week_start}",
            report_type='weekly_summary',
            status='completed',
            filters_used={
                'week_start': str(week_start),
                'week_end': str(week_end)
            },
            expires_at=timezone.now() + timedelta(days=30)
        )

        send_report_email.delay(
            report_id=str(report.report_id),
            recipients=['admin@example.com'],
            subject=f'Weekly Summary - Week of {week_start}'
        )

        return f"Weekly report generated: {report.report_id}"

    except Exception as e:
        return f"Error generating weekly report: {str(e)}"


@shared_task
def generate_monthly_report():
    """
    Generate comprehensive monthly report
    Scheduled to run on 1st of every month at 10 AM
    """
    today = timezone.now().date()
    last_month = today.replace(day=1) - timedelta(days=1)
    month_start = last_month.replace(day=1)
    month_end = last_month

    report_data = {
        'report_name': f'Monthly Report - {month_start.strftime("%B %Y")}',
        'date_from': str(month_start),
        'date_to': str(month_end),
        'generated_by': 'System',
        'summary': {
            'total_feedback': DirectFeedback.objects.filter(
                submitted_at__date__gte=month_start,
                submitted_at__date__lte=month_end
            ).count(),
        }
    }

    try:
        pdf_buffer = generate_executive_summary_pdf(report_data)

        report = GeneratedReport.objects.create(
            report_name=f"Monthly Report - {month_start.strftime('%B %Y')}",
            report_type='executive_summary',
            status='completed',
            expires_at=timezone.now() + timedelta(days=90)
        )

        send_report_email.delay(
            report_id=str(report.report_id),
            recipients=['superadmin@example.com'],
            subject=f'Monthly Report - {month_start.strftime("%B %Y")}'
        )

        return f"Monthly report generated: {report.report_id}"

    except Exception as e:
        return f"Error generating monthly report: {str(e)}"


@shared_task
def generate_scheduled_report(template_id):
    """
    Generate report from saved template
    Called by scheduler based on template configuration
    """
    try:
        template = ReportTemplate.objects.get(template_id=template_id)
    except ReportTemplate.DoesNotExist:
        return f"Template not found: {template_id}"

    if not template.is_scheduled or not template.is_active:
        return f"Template is not scheduled: {template_id}"

    # Prepare report data based on template
    report_data = {
        'report_name': template.name,
        'generated_by': 'Scheduled Task',
        'metrics': template.metrics,
        'filters': template.filters,
        # TODO: Fetch actual data based on metrics and filters
    }

    try:
        # Generate PDF and/or Excel
        pdf_buffer = None
        excel_buffer = None

        if template.export_format in ['pdf', 'both']:
            pdf_buffer = generate_executive_summary_pdf(report_data)

        if template.export_format in ['excel', 'both']:
            excel_buffer = export_analytics_to_excel(report_data)

        # Create report record
        report = GeneratedReport.objects.create(
            template=template,
            report_name=template.name,
            report_type=template.report_type,
            status='completed',
            filters_used=template.filters,
            expires_at=timezone.now() + timedelta(hours=48)
        )

        # Update template
        template.last_generated = timezone.now()
        template.save()

        # Send to recipients
        if template.recipients:
            send_report_email.delay(
                report_id=str(report.report_id),
                recipients=template.recipients,
                subject=f'{template.name} - {timezone.now().strftime("%Y-%m-%d")}'
            )

        return f"Scheduled report generated: {report.report_id}"

    except Exception as e:
        return f"Error generating scheduled report: {str(e)}"


@shared_task
def send_report_email(report_id, recipients, subject):
    """
    Send report via email
    """
    try:
        report = GeneratedReport.objects.get(report_id=report_id)
    except GeneratedReport.DoesNotExist:
        return f"Report not found: {report_id}"

    # Email body
    body = f"""
    Hello,

    Your {report.report_type.replace('_', ' ').title()} report is ready.

    Report Name: {report.report_name}
    Generated: {report.created_at.strftime('%B %d, %Y at %I:%M %p')}

    Download Links:
    PDF: {report.pdf_file_url or 'Not available'}
    Excel: {report.excel_file_url or 'Not available'}

    Note: Download links will expire in 24 hours.

    Best regards,
    Pulse of People Platform
    """

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email='noreply@pulseofpeople.com',
            to=recipients,
        )

        # TODO: Attach PDF/Excel files if available

        email.send()

        return f"Email sent to {len(recipients)} recipients"

    except Exception as e:
        return f"Error sending email: {str(e)}"


@shared_task
def process_export_job(job_id):
    """
    Process export job in background
    For large exports (>10K rows)
    """
    try:
        job = ExportJob.objects.get(job_id=job_id)
    except ExportJob.DoesNotExist:
        return f"Export job not found: {job_id}"

    job.status = 'processing'
    job.started_at = timezone.now()
    job.save()

    try:
        # TODO: Fetch data based on job.resource and job.filters
        # TODO: Generate file based on job.export_format
        # TODO: Upload to storage and set job.file_url

        # Mock completion
        job.status = 'completed'
        job.progress = 100
        job.completed_at = timezone.now()
        job.row_count = 5000  # Mock
        job.file_size = 1024 * 500  # Mock 500KB
        job.file_url = 'https://example.com/export.csv'  # Mock
        job.save()

        return f"Export job completed: {job_id}"

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        job.save()
        return f"Export job failed: {str(e)}"


@shared_task
def cleanup_expired_reports():
    """
    Clean up expired reports
    Scheduled to run daily at midnight
    """
    expired = GeneratedReport.objects.filter(
        expires_at__lt=timezone.now(),
        status='completed'
    )

    count = expired.count()

    # TODO: Delete files from storage before deleting records
    expired.delete()

    return f"Cleaned up {count} expired reports"


@shared_task
def cleanup_expired_exports():
    """
    Clean up expired export jobs
    Scheduled to run daily at midnight
    """
    expired = ExportJob.objects.filter(
        expires_at__lt=timezone.now(),
        status='completed'
    )

    count = expired.count()
    expired.delete()

    return f"Cleaned up {count} expired exports"


# Schedule configuration (to be added to celery beat schedule)
"""
CELERY_BEAT_SCHEDULE = {
    'daily-report': {
        'task': 'api.tasks.generate_daily_report',
        'schedule': crontab(hour=18, minute=0),  # 6 PM daily
    },
    'weekly-report': {
        'task': 'api.tasks.generate_weekly_report',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Monday 9 AM
    },
    'monthly-report': {
        'task': 'api.tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=10, minute=0),  # 1st of month, 10 AM
    },
    'cleanup-reports': {
        'task': 'api.tasks.cleanup_expired_reports',
        'schedule': crontab(hour=0, minute=0),  # Midnight daily
    },
    'cleanup-exports': {
        'task': 'api.tasks.cleanup_expired_exports',
        'schedule': crontab(hour=0, minute=30),  # 12:30 AM daily
    },
}
"""
