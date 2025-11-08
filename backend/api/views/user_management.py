"""
User Management Views for Bulk Upload
"""

import csv
import io
import os
import tempfile
from django.http import HttpResponse, FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from api.models import BulkUploadJob, BulkUploadError
from api.services.bulk_user_import import BulkUserImportService, start_bulk_upload_processing


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_upload_users(request):
    """
    Upload CSV file for bulk user creation

    POST /api/users/bulk-upload/
    Headers: Authorization: Bearer <token>
    Body: multipart/form-data with 'file' field

    Returns:
        {
            "job_id": "uuid",
            "message": "Bulk upload started",
            "total_rows": 100
        }
    """
    # Check if user has permission to create users
    user_profile = getattr(request.user, 'profile', None)
    user_role = user_profile.role if user_profile else 'user'

    allowed_roles = ['superadmin', 'admin', 'manager', 'analyst']
    if user_role not in allowed_roles:
        return Response({
            'error': f'Your role ({user_role}) does not have permission to bulk upload users.'
        }, status=status.HTTP_403_FORBIDDEN)

    # Check if file was uploaded
    if 'file' not in request.FILES:
        return Response({
            'error': 'No file uploaded. Please provide a CSV file.'
        }, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES['file']

    # Validate file type
    if not uploaded_file.name.endswith('.csv'):
        return Response({
            'error': 'Invalid file type. Please upload a CSV file.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate file size (max 5MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        return Response({
            'error': 'File too large. Maximum size is 5MB.'
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Read file content
        file_content = uploaded_file.read().decode('utf-8')

        # Create a temporary file to store the uploaded CSV
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        # Create BulkUploadJob
        job = BulkUploadJob.objects.create(
            created_by=request.user,
            file_name=uploaded_file.name,
            file_path=temp_file_path,
            status='pending'
        )

        # Start background processing
        start_bulk_upload_processing(job, file_content, request.user)

        return Response({
            'job_id': str(job.job_id),
            'message': 'Bulk upload started. You will receive an email when processing is complete.',
            'status': 'pending'
        }, status=status.HTTP_202_ACCEPTED)

    except Exception as e:
        return Response({
            'error': f'Failed to process upload: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bulk_upload_status(request, job_id):
    """
    Get status of a bulk upload job

    GET /api/users/bulk-upload/{job_id}/status/

    Returns:
        {
            "job_id": "uuid",
            "status": "processing",
            "total_rows": 100,
            "processed_rows": 50,
            "success_count": 45,
            "failed_count": 5,
            "progress_percentage": 50,
            "started_at": "2025-01-01T12:00:00Z",
            "completed_at": null,
            "validation_errors": []
        }
    """
    try:
        job = BulkUploadJob.objects.get(job_id=job_id, created_by=request.user)

        return Response({
            'job_id': str(job.job_id),
            'status': job.status,
            'file_name': job.file_name,
            'total_rows': job.total_rows,
            'processed_rows': job.processed_rows,
            'success_count': job.success_count,
            'failed_count': job.failed_count,
            'progress_percentage': job.get_progress_percentage(),
            'validation_errors': job.validation_errors,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'created_at': job.created_at.isoformat(),
        })

    except BulkUploadJob.DoesNotExist:
        return Response({
            'error': 'Bulk upload job not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bulk_upload_errors(request, job_id):
    """
    Download error report CSV for a bulk upload job

    GET /api/users/bulk-upload/{job_id}/errors/

    Returns: CSV file with errors
    """
    try:
        job = BulkUploadJob.objects.get(job_id=job_id, created_by=request.user)

        # Get all errors for this job
        errors = BulkUploadError.objects.filter(job=job).order_by('row_number')

        if not errors.exists():
            return Response({
                'message': 'No errors found for this job'
            })

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['Row Number', 'Field', 'Error Message', 'Row Data'])

        # Write error rows
        for error in errors:
            writer.writerow([
                error.row_number,
                error.error_field,
                error.error_message,
                str(error.row_data)
            ])

        # Create HTTP response
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="bulk_upload_errors_{job_id}.csv"'

        return response

    except BulkUploadJob.DoesNotExist:
        return Response({
            'error': 'Bulk upload job not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cancel_bulk_upload(request, job_id):
    """
    Cancel a bulk upload job

    DELETE /api/users/bulk-upload/{job_id}/

    Returns:
        {
            "message": "Bulk upload cancelled"
        }
    """
    try:
        job = BulkUploadJob.objects.get(job_id=job_id, created_by=request.user)

        # Only allow cancellation if job is still pending or processing
        if job.status in ['pending', 'validating', 'processing']:
            job.status = 'cancelled'
            job.completed_at = timezone.now()
            job.save()

            return Response({
                'message': 'Bulk upload cancelled successfully'
            })
        else:
            return Response({
                'error': f'Cannot cancel job with status: {job.status}'
            }, status=status.HTTP_400_BAD_REQUEST)

    except BulkUploadJob.DoesNotExist:
        return Response({
            'error': 'Bulk upload job not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_user_template(request):
    """
    Download CSV template for bulk user upload

    GET /api/users/bulk-upload/template/

    Returns: CSV file with sample data
    """
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(['name', 'email', 'role', 'phone', 'state_id', 'district_id'])

    # Write sample rows
    writer.writerow(['John Doe', 'john@example.com', 'user', '+91 9876543210', '1', '5'])
    writer.writerow(['Jane Smith', 'jane@example.com', 'analyst', '+91 9876543211', '1', '5'])
    writer.writerow(['Bob Johnson', 'bob@example.com', 'manager', '', '', ''])

    # Create HTTP response
    output.seek(0)
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bulk_user_upload_template.csv"'

    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def bulk_upload_jobs_list(request):
    """
    List all bulk upload jobs for the current user

    GET /api/users/bulk-upload/jobs/

    Returns:
        {
            "jobs": [
                {
                    "job_id": "uuid",
                    "status": "completed",
                    "file_name": "users.csv",
                    "total_rows": 100,
                    "success_count": 95,
                    "failed_count": 5,
                    "created_at": "2025-01-01T12:00:00Z"
                }
            ]
        }
    """
    jobs = BulkUploadJob.objects.filter(
        created_by=request.user
    ).order_by('-created_at')[:20]  # Last 20 jobs

    jobs_data = [{
        'job_id': str(job.job_id),
        'status': job.status,
        'file_name': job.file_name,
        'total_rows': job.total_rows,
        'processed_rows': job.processed_rows,
        'success_count': job.success_count,
        'failed_count': job.failed_count,
        'progress_percentage': job.get_progress_percentage(),
        'created_at': job.created_at.isoformat(),
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
    } for job in jobs]

    return Response({
        'jobs': jobs_data
    })
