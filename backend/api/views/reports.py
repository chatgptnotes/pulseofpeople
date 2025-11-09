"""
Report Generation Views - PDF and Excel report generation
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import datetime, timedelta
import uuid

from api.models_analytics import ReportTemplate, GeneratedReport


class ExecutiveSummaryReportView(APIView):
    """
    POST /api/reports/executive-summary/
    Generate executive summary report
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Parse request
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to', timezone.now().date())
        export_format = request.data.get('format', 'pdf')  # pdf, excel, both

        # Create report job
        report = GeneratedReport.objects.create(
            report_name=f"Executive Summary - {timezone.now().strftime('%Y-%m-%d')}",
            report_type='executive_summary',
            generated_by=request.user,
            status='pending',
            filters_used={
                'date_from': str(date_from) if date_from else None,
                'date_to': str(date_to),
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # TODO: Queue background task to generate report
        # For now, return job ID

        return Response({
            "report_id": str(report.report_id),
            "status": "pending",
            "message": "Report generation started. You will be notified when ready.",
            "estimated_time": "2-5 minutes"
        }, status=status.HTTP_202_ACCEPTED)


class CampaignPerformanceReportView(APIView):
    """
    POST /api/reports/campaign-performance/
    Generate campaign performance report
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        campaign_ids = request.data.get('campaign_ids', [])
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to', timezone.now().date())
        export_format = request.data.get('format', 'pdf')

        report = GeneratedReport.objects.create(
            report_name=f"Campaign Performance - {timezone.now().strftime('%Y-%m-%d')}",
            report_type='campaign_performance',
            generated_by=request.user,
            status='pending',
            filters_used={
                'campaign_ids': campaign_ids,
                'date_from': str(date_from) if date_from else None,
                'date_to': str(date_to),
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return Response({
            "report_id": str(report.report_id),
            "status": "pending",
            "message": "Report generation started."
        }, status=status.HTTP_202_ACCEPTED)


class ConstituencyReportView(APIView):
    """
    POST /api/reports/constituency/
    Generate detailed constituency report
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        constituency_id = request.data.get('constituency_id')
        if not constituency_id:
            return Response({
                "error": "constituency_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        export_format = request.data.get('format', 'pdf')

        report = GeneratedReport.objects.create(
            report_name=f"Constituency Report - {timezone.now().strftime('%Y-%m-%d')}",
            report_type='constituency',
            generated_by=request.user,
            status='pending',
            filters_used={
                'constituency_id': constituency_id,
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return Response({
            "report_id": str(report.report_id),
            "status": "pending",
            "message": "Report generation started."
        }, status=status.HTTP_202_ACCEPTED)


class DailyActivityReportView(APIView):
    """
    POST /api/reports/daily-activity/
    Generate daily activity report (auto-generated at EOD)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        report_date = request.data.get('date', timezone.now().date())

        report = GeneratedReport.objects.create(
            report_name=f"Daily Activity - {report_date}",
            report_type='daily_activity',
            generated_by=request.user,
            status='pending',
            filters_used={
                'date': str(report_date),
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return Response({
            "report_id": str(report.report_id),
            "status": "pending",
            "message": "Report generation started."
        }, status=status.HTTP_202_ACCEPTED)


class WeeklySummaryReportView(APIView):
    """
    POST /api/reports/weekly-summary/
    Generate weekly summary report
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        week_start = request.data.get('week_start')
        week_end = request.data.get('week_end')

        report = GeneratedReport.objects.create(
            report_name=f"Weekly Summary - {timezone.now().strftime('%Y-%m-%d')}",
            report_type='weekly_summary',
            generated_by=request.user,
            status='pending',
            filters_used={
                'week_start': str(week_start) if week_start else None,
                'week_end': str(week_end) if week_end else None,
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return Response({
            "report_id": str(report.report_id),
            "status": "pending",
            "message": "Report generation started."
        }, status=status.HTTP_202_ACCEPTED)


class VolunteerPerformanceReportView(APIView):
    """
    POST /api/reports/volunteer-performance/
    Generate volunteer performance report
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        date_from = request.data.get('date_from')
        date_to = request.data.get('date_to', timezone.now().date())
        volunteer_ids = request.data.get('volunteer_ids', [])

        report = GeneratedReport.objects.create(
            report_name=f"Volunteer Performance - {timezone.now().strftime('%Y-%m-%d')}",
            report_type='volunteer_performance',
            generated_by=request.user,
            status='pending',
            filters_used={
                'date_from': str(date_from) if date_from else None,
                'date_to': str(date_to),
                'volunteer_ids': volunteer_ids,
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return Response({
            "report_id": str(report.report_id),
            "status": "pending",
            "message": "Report generation started."
        }, status=status.HTTP_202_ACCEPTED)


class CustomReportBuilderView(APIView):
    """
    POST /api/reports/custom/
    Custom report builder - user selects metrics, filters, visualizations
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Report configuration
        metrics = request.data.get('metrics', [])
        filters = request.data.get('filters', {})
        visualizations = request.data.get('visualizations', [])
        export_format = request.data.get('format', 'pdf')

        # Optional: Save as template
        save_as_template = request.data.get('save_as_template', False)
        template_name = request.data.get('template_name')

        if save_as_template and template_name:
            template = ReportTemplate.objects.create(
                name=template_name,
                report_type='custom',
                created_by=request.user,
                metrics=metrics,
                filters=filters,
                visualizations=visualizations,
                export_format=export_format
            )

        # Generate report
        report = GeneratedReport.objects.create(
            report_name=template_name or f"Custom Report - {timezone.now().strftime('%Y-%m-%d')}",
            report_type='custom',
            generated_by=request.user,
            status='pending',
            filters_used=filters,
            metadata={
                'metrics': metrics,
                'visualizations': visualizations,
            },
            expires_at=timezone.now() + timedelta(hours=24)
        )

        return Response({
            "report_id": str(report.report_id),
            "template_id": str(template.template_id) if save_as_template else None,
            "status": "pending",
            "message": "Report generation started."
        }, status=status.HTTP_202_ACCEPTED)


class ReportStatusView(APIView):
    """
    GET /api/reports/{report_id}/status/
    Check report generation status
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = GeneratedReport.objects.get(report_id=report_id)
        except GeneratedReport.DoesNotExist:
            return Response({
                "error": "Report not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if expired
        if report.is_expired():
            return Response({
                "status": "expired",
                "message": "Report download link has expired"
            })

        return Response({
            "report_id": str(report.report_id),
            "status": report.status,
            "pdf_url": report.pdf_file_url if report.status == 'completed' else None,
            "excel_url": report.excel_file_url if report.status == 'completed' else None,
            "error_message": report.error_message if report.status == 'failed' else None,
            "expires_at": report.expires_at.isoformat() if report.expires_at else None,
            "download_count": report.download_count
        })


class ReportDownloadView(APIView):
    """
    GET /api/reports/{report_id}/download/
    Download generated report
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = GeneratedReport.objects.get(report_id=report_id)
        except GeneratedReport.DoesNotExist:
            return Response({
                "error": "Report not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Check if expired
        if report.is_expired():
            return Response({
                "error": "Report download link has expired"
            }, status=status.HTTP_410_GONE)

        if report.status != 'completed':
            return Response({
                "error": f"Report is not ready. Current status: {report.status}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Increment download count
        report.download_count += 1
        report.save()

        # Return download URL
        file_type = request.GET.get('type', 'pdf')
        download_url = report.pdf_file_url if file_type == 'pdf' else report.excel_file_url

        return Response({
            "download_url": download_url,
            "file_name": f"{report.report_name}.{file_type}",
            "expires_at": report.expires_at.isoformat() if report.expires_at else None
        })


class ReportTemplateListView(APIView):
    """
    GET /api/reports/templates/
    List saved report templates
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # User's templates
        templates = ReportTemplate.objects.filter(
            created_by=request.user,
            is_active=True
        ).order_by('-created_at')

        template_list = []
        for template in templates:
            template_list.append({
                "template_id": str(template.template_id),
                "name": template.name,
                "report_type": template.report_type,
                "description": template.description,
                "is_scheduled": template.is_scheduled,
                "schedule_frequency": template.schedule_frequency,
                "last_generated": template.last_generated.isoformat() if template.last_generated else None,
                "created_at": template.created_at.isoformat()
            })

        return Response({
            "templates": template_list,
            "total": len(template_list)
        })

    def post(self, request):
        """Create new report template"""
        name = request.data.get('name')
        report_type = request.data.get('report_type', 'custom')
        description = request.data.get('description', '')
        metrics = request.data.get('metrics', [])
        filters = request.data.get('filters', {})
        visualizations = request.data.get('visualizations', [])

        # Scheduling
        is_scheduled = request.data.get('is_scheduled', False)
        schedule_frequency = request.data.get('schedule_frequency')
        recipients = request.data.get('recipients', [])

        if not name:
            return Response({
                "error": "Template name is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        template = ReportTemplate.objects.create(
            name=name,
            report_type=report_type,
            description=description,
            created_by=request.user,
            metrics=metrics,
            filters=filters,
            visualizations=visualizations,
            is_scheduled=is_scheduled,
            schedule_frequency=schedule_frequency,
            recipients=recipients
        )

        return Response({
            "template_id": str(template.template_id),
            "message": "Template created successfully"
        }, status=status.HTTP_201_CREATED)


class ReportTemplateDetailView(APIView):
    """
    GET/PUT/DELETE /api/reports/templates/{template_id}/
    Manage specific report template
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, template_id):
        try:
            template = ReportTemplate.objects.get(
                template_id=template_id,
                created_by=request.user
            )
        except ReportTemplate.DoesNotExist:
            return Response({
                "error": "Template not found"
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "template_id": str(template.template_id),
            "name": template.name,
            "report_type": template.report_type,
            "description": template.description,
            "metrics": template.metrics,
            "filters": template.filters,
            "visualizations": template.visualizations,
            "is_scheduled": template.is_scheduled,
            "schedule_frequency": template.schedule_frequency,
            "schedule_time": str(template.schedule_time) if template.schedule_time else None,
            "recipients": template.recipients,
            "export_format": template.export_format,
            "created_at": template.created_at.isoformat()
        })

    def put(self, request, template_id):
        try:
            template = ReportTemplate.objects.get(
                template_id=template_id,
                created_by=request.user
            )
        except ReportTemplate.DoesNotExist:
            return Response({
                "error": "Template not found"
            }, status=status.HTTP_404_NOT_FOUND)

        # Update fields
        template.name = request.data.get('name', template.name)
        template.description = request.data.get('description', template.description)
        template.metrics = request.data.get('metrics', template.metrics)
        template.filters = request.data.get('filters', template.filters)
        template.visualizations = request.data.get('visualizations', template.visualizations)
        template.is_scheduled = request.data.get('is_scheduled', template.is_scheduled)
        template.schedule_frequency = request.data.get('schedule_frequency', template.schedule_frequency)
        template.recipients = request.data.get('recipients', template.recipients)
        template.save()

        return Response({
            "message": "Template updated successfully"
        })

    def delete(self, request, template_id):
        try:
            template = ReportTemplate.objects.get(
                template_id=template_id,
                created_by=request.user
            )
        except ReportTemplate.DoesNotExist:
            return Response({
                "error": "Template not found"
            }, status=status.HTTP_404_NOT_FOUND)

        template.is_active = False
        template.save()

        return Response({
            "message": "Template deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)


class ScheduledReportsView(APIView):
    """
    GET /api/reports/scheduled/
    List all scheduled reports
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scheduled_templates = ReportTemplate.objects.filter(
            created_by=request.user,
            is_scheduled=True,
            is_active=True
        )

        scheduled_list = []
        for template in scheduled_templates:
            scheduled_list.append({
                "template_id": str(template.template_id),
                "name": template.name,
                "frequency": template.schedule_frequency,
                "recipients": template.recipients,
                "last_generated": template.last_generated.isoformat() if template.last_generated else None,
                "next_run": None  # Calculate based on schedule
            })

        return Response({
            "scheduled_reports": scheduled_list,
            "total": len(scheduled_list)
        })
