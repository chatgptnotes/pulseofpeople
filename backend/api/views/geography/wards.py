"""
Ward CRUD API Views
Handles ward listing, creation, retrieval, update, and deletion
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from supabase import create_client

from api.serializers.geography_serializers import (
    WardSerializer,
    WardBulkImportSerializer,
    BulkImportResponseSerializer
)
from api.services.bulk_geography_import import WardBulkImportService
from api.decorators.permissions import require_role


def get_supabase_client():
    """Get Supabase client instance"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


class WardPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 500


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def ward_list_create(request):
    """
    GET: List all wards with pagination and filtering
    POST: Create a new ward
    """

    supabase = get_supabase_client()
    organization_id = str(request.user.profile.organization_id)

    if request.method == 'GET':
        # Query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        search = request.GET.get('search', '')
        constituency_id = request.GET.get('constituency_id')
        urbanization = request.GET.get('urbanization')
        income_level = request.GET.get('income_level')

        # Build query
        query = supabase.table('wards').select('*').eq('organization_id', organization_id)

        # Apply filters
        if constituency_id:
            query = query.eq('constituency_id', constituency_id)

        if urbanization:
            query = query.eq('urbanization', urbanization)

        if income_level:
            query = query.eq('income_level', income_level)

        if search:
            query = query.or_(f'name.ilike.%{search}%,code.ilike.%{search}%')

        # Calculate pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        # Execute query
        response = query.order('created_at', desc=True).execute()

        # Get total count
        count_response = supabase.table('wards').select('id', count='exact').eq(
            'organization_id', organization_id
        ).execute()

        total_count = count_response.count

        return Response({
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'results': response.data
        })

    elif request.method == 'POST':
        # Require admin role
        if not request.user.profile.is_admin_or_above():
            return Response(
                {'error': 'Only admins can create wards'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = WardSerializer(data=request.data)
        if serializer.is_valid():
            # Insert into Supabase
            try:
                ward_data = serializer.validated_data
                ward_data['organization_id'] = organization_id

                response = supabase.table('wards').insert(ward_data).execute()

                return Response(response.data[0], status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def ward_detail(request, ward_id):
    """
    GET: Retrieve a ward
    PUT/PATCH: Update a ward
    DELETE: Delete a ward
    """

    supabase = get_supabase_client()
    organization_id = str(request.user.profile.organization_id)

    # Check if ward exists and belongs to organization
    ward_response = supabase.table('wards').select('*').eq('id', ward_id).eq(
        'organization_id', organization_id
    ).execute()

    if not ward_response.data:
        return Response(
            {'error': 'Ward not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    ward = ward_response.data[0]

    if request.method == 'GET':
        return Response(ward)

    elif request.method in ['PUT', 'PATCH']:
        # Require admin role
        if not request.user.profile.is_admin_or_above():
            return Response(
                {'error': 'Only admins can update wards'},
                status=status.HTTP_403_FORBIDDEN
            )

        partial = request.method == 'PATCH'
        serializer = WardSerializer(data=request.data, partial=partial)

        if serializer.is_valid():
            try:
                update_data = serializer.validated_data
                response = supabase.table('wards').update(update_data).eq('id', ward_id).execute()

                return Response(response.data[0])
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Require admin role
        if not request.user.profile.role in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can delete wards'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            supabase.table('wards').delete().eq('id', ward_id).execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_role(['admin', 'superadmin'])
def ward_bulk_import(request):
    """
    Bulk import wards from CSV or Excel file

    Expected file format:
    - CSV or Excel (.csv, .xlsx, .xls)
    - Headers: constituency_code, name, code, ward_number, population, voter_count,
               total_booths, urbanization, income_level, literacy_rate

    Request body:
    - file: File upload
    - update_existing: Boolean (optional, default=False)
    """

    serializer = WardBulkImportSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get organization from user
    organization_id = str(request.user.profile.organization_id)

    # Process file
    service = WardBulkImportService(request.user, organization_id)
    update_existing = serializer.validated_data.get('update_existing', False)

    try:
        job = service.process_file(
            serializer.validated_data['file'],
            update_existing=update_existing
        )

        response_serializer = BulkImportResponseSerializer({
            'job_id': job.job_id,
            'status': job.status,
            'total_rows': job.total_rows,
            'processed_rows': job.processed_rows,
            'success_count': job.success_count,
            'failed_count': job.failed_count,
            'validation_errors': job.validation_errors,
            'created_at': job.created_at,
            'completed_at': job.completed_at
        })

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK if job.status == 'completed' else status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {'error': f'Import failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ward_import_status(request, job_id):
    """Get status of a bulk import job"""

    from api.models import BulkUploadJob

    try:
        job = BulkUploadJob.objects.get(job_id=job_id, created_by=request.user)

        # Get error details if exists
        errors = []
        if job.status == 'failed':
            from api.models import BulkUploadError
            error_records = BulkUploadError.objects.filter(job=job)[:100]  # Limit to 100 errors
            errors = [{
                'row_number': err.row_number,
                'error_message': err.error_message,
                'error_field': err.error_field
            } for err in error_records]

        return Response({
            'job_id': job.job_id,
            'status': job.status,
            'total_rows': job.total_rows,
            'processed_rows': job.processed_rows,
            'success_count': job.success_count,
            'failed_count': job.failed_count,
            'progress_percentage': job.get_progress_percentage(),
            'validation_errors': job.validation_errors,
            'errors': errors,
            'created_at': job.created_at,
            'started_at': job.started_at,
            'completed_at': job.completed_at
        })

    except BulkUploadJob.DoesNotExist:
        return Response(
            {'error': 'Import job not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ward_statistics(request):
    """Get ward statistics for organization"""

    supabase = get_supabase_client()
    organization_id = str(request.user.profile.organization_id)

    # Get total counts
    total_wards = supabase.table('wards').select('id', count='exact').eq(
        'organization_id', organization_id
    ).execute().count

    # Get breakdown by urbanization
    urbanization_query = supabase.rpc('get_ward_urbanization_stats', {
        'org_id': organization_id
    }).execute()

    # Get breakdown by income level
    income_query = supabase.rpc('get_ward_income_stats', {
        'org_id': organization_id
    }).execute()

    return Response({
        'total_wards': total_wards,
        'by_urbanization': urbanization_query.data if urbanization_query.data else [],
        'by_income_level': income_query.data if income_query.data else []
    })
