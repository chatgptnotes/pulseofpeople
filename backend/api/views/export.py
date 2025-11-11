"""
Export API - CSV, Excel, JSON, PDF exports for all resources
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
import csv
import json
from io import StringIO, BytesIO

from api.models import DirectFeedback, FieldReport, PollingBooth
from api.models_analytics import ExportJob


class ExportView(APIView):
    """
    POST /api/export/
    Generic export API for all resources
    """
    permission_classes = [IsAuthenticated]

    SUPPORTED_RESOURCES = [
        'voters', 'interactions', 'feedback', 'field_reports',
        'polling_booths', 'sentiment_data', 'campaigns'
    ]

    SUPPORTED_FORMATS = ['csv', 'excel', 'json', 'pdf']

    def post(self, request):
        # Parse request
        resource = request.data.get('resource')
        export_format = request.data.get('format', 'csv')
        filters = request.data.get('filters', {})
        fields = request.data.get('fields', [])
        date_range = request.data.get('date_range', {})

        # Validate
        if resource not in self.SUPPORTED_RESOURCES:
            return Response({
                "error": f"Unsupported resource. Supported: {', '.join(self.SUPPORTED_RESOURCES)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        if export_format not in self.SUPPORTED_FORMATS:
            return Response({
                "error": f"Unsupported format. Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create export job
        job = ExportJob.objects.create(
            created_by=request.user,
            resource=resource,
            export_format=export_format,
            filters=filters,
            fields=fields,
            status='pending',
            expires_at=timezone.now() + timedelta(hours=24)
        )

        # For small exports, process immediately
        # For large exports (>10K rows), queue background task

        # TODO: Queue background task with Celery
        # For now, return job ID

        return Response({
            "job_id": str(job.job_id),
            "status": "pending",
            "message": "Export job created. Processing...",
            "estimated_time": "1-3 minutes"
        }, status=status.HTTP_202_ACCEPTED)


class ExportStatusView(APIView):
    """
    GET /api/export/{job_id}/status/
    Check export job status
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = ExportJob.objects.get(job_id=job_id, created_by=request.user)
        except ExportJob.DoesNotExist:
            return Response({
                "error": "Export job not found"
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "job_id": str(job.job_id),
            "status": job.status,
            "progress": job.progress,
            "file_url": job.file_url if job.status == 'completed' else None,
            "file_size": job.file_size,
            "row_count": job.row_count,
            "error_message": job.error_message if job.status == 'failed' else None,
            "expires_at": job.expires_at.isoformat() if job.expires_at else None,
        })


class ExportDownloadView(APIView):
    """
    GET /api/export/{job_id}/download/
    Download exported file
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        try:
            job = ExportJob.objects.get(job_id=job_id, created_by=request.user)
        except ExportJob.DoesNotExist:
            return Response({
                "error": "Export job not found"
            }, status=status.HTTP_404_NOT_FOUND)

        if job.status != 'completed':
            return Response({
                "error": f"Export not ready. Status: {job.status}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check expiration
        if job.expires_at and timezone.now() > job.expires_at:
            return Response({
                "error": "Export has expired"
            }, status=status.HTTP_410_GONE)

        return Response({
            "download_url": job.file_url,
            "file_name": f"{job.resource}_export_{job.created_at.strftime('%Y%m%d')}.{job.export_format}",
            "file_size": job.file_size,
            "row_count": job.row_count,
        })


class QuickExportCSVView(APIView):
    """
    GET /api/export/quick/csv/{resource}/
    Quick CSV export (synchronous, max 1000 rows)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, resource):
        # Query parameters for filters
        limit = min(int(request.GET.get('limit', 1000)), 1000)

        # Build queryset based on resource
        if resource == 'feedback':
            queryset = DirectFeedback.objects.all()[:limit]
            fieldnames = [
                'feedback_id', 'citizen_name', 'citizen_phone', 'ward',
                'issue_category', 'message_text', 'status', 'submitted_at'
            ]

            # Generate CSV
            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for feedback in queryset:
                writer.writerow({
                    'feedback_id': str(feedback.feedback_id),
                    'citizen_name': feedback.citizen_name,
                    'citizen_phone': feedback.citizen_phone,
                    'ward': feedback.ward,
                    'issue_category': feedback.issue_category.name if feedback.issue_category else '',
                    'message_text': feedback.message_text[:100],
                    'status': feedback.status,
                    'submitted_at': feedback.submitted_at.isoformat(),
                })

            csv_data = output.getvalue()
            output.close()

            from django.http import HttpResponse
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{resource}_export.csv"'
            return response

        elif resource == 'field_reports':
            queryset = FieldReport.objects.all()[:limit]
            fieldnames = [
                'report_id', 'volunteer', 'ward', 'report_type',
                'title', 'verification_status', 'report_date'
            ]

            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for report in queryset:
                writer.writerow({
                    'report_id': str(report.report_id),
                    'volunteer': report.volunteer.username,
                    'ward': report.ward,
                    'report_type': report.report_type,
                    'title': report.title,
                    'verification_status': report.verification_status,
                    'report_date': report.report_date.isoformat(),
                })

            csv_data = output.getvalue()
            output.close()

            from django.http import HttpResponse
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{resource}_export.csv"'
            return response

        elif resource == 'polling_booths':
            queryset = PollingBooth.objects.all()[:limit]
            fieldnames = [
                'booth_number', 'name', 'constituency', 'district',
                'total_voters', 'address', 'is_active'
            ]

            output = StringIO()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()

            for booth in queryset:
                writer.writerow({
                    'booth_number': booth.booth_number,
                    'name': booth.name,
                    'constituency': booth.constituency.name,
                    'district': booth.district.name,
                    'total_voters': booth.total_voters,
                    'address': booth.address,
                    'is_active': booth.is_active,
                })

            csv_data = output.getvalue()
            output.close()

            from django.http import HttpResponse
            response = HttpResponse(csv_data, content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{resource}_export.csv"'
            return response

        return Response({
            "error": "Resource not supported for quick export"
        }, status=status.HTTP_400_BAD_REQUEST)


class QuickExportJSONView(APIView):
    """
    GET /api/export/quick/json/{resource}/
    Quick JSON export (synchronous, max 1000 rows)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, resource):
        limit = min(int(request.GET.get('limit', 1000)), 1000)

        if resource == 'feedback':
            queryset = DirectFeedback.objects.all()[:limit]
            data = []

            for feedback in queryset:
                data.append({
                    'feedback_id': str(feedback.feedback_id),
                    'citizen_name': feedback.citizen_name,
                    'citizen_phone': feedback.citizen_phone,
                    'ward': feedback.ward,
                    'issue_category': feedback.issue_category.name if feedback.issue_category else None,
                    'message_text': feedback.message_text,
                    'status': feedback.status,
                    'submitted_at': feedback.submitted_at.isoformat(),
                })

            from django.http import JsonResponse
            response = JsonResponse(data, safe=False)
            response['Content-Disposition'] = f'attachment; filename="{resource}_export.json"'
            return response

        return Response({
            "error": "Resource not supported for quick export"
        }, status=status.HTTP_400_BAD_REQUEST)


class ExportTemplateView(APIView):
    """
    GET /api/export/template/{resource}/
    Download CSV template for bulk upload
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, resource):
        if resource == 'voters':
            fieldnames = [
                'name', 'phone', 'email', 'age', 'gender',
                'constituency', 'ward', 'booth_number', 'sentiment'
            ]
        elif resource == 'polling_booths':
            fieldnames = [
                'booth_number', 'name', 'constituency', 'district',
                'address', 'total_voters', 'latitude', 'longitude'
            ]
        else:
            return Response({
                "error": "Template not available for this resource"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Generate CSV template
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        # Add sample row
        sample_data = {field: f"sample_{field}" for field in fieldnames}
        writer.writerow(sample_data)

        csv_data = output.getvalue()
        output.close()

        from django.http import HttpResponse
        response = HttpResponse(csv_data, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{resource}_template.csv"'
        return response
