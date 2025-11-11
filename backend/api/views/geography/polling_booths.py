"""
Polling Booth CRUD API Views
Handles polling booth listing, creation, retrieval, update, and deletion
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from supabase import create_client

from api.serializers.geography_serializers import (
    PollingBoothSerializer,
    PollingBoothBulkImportSerializer,
    BulkImportResponseSerializer
)
from api.services.bulk_geography_import import PollingBoothBulkImportService
from api.decorators.permissions import require_role


def get_supabase_client():
    """Get Supabase client instance"""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def polling_booth_list_create(request):
    """
    GET: List all polling booths with pagination and filtering
    POST: Create a new polling booth
    """

    supabase = get_supabase_client()
    organization_id = str(request.user.profile.organization_id)

    if request.method == 'GET':
        # Query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        search = request.GET.get('search', '')
        constituency_id = request.GET.get('constituency_id')
        ward_id = request.GET.get('ward_id')
        is_active = request.GET.get('is_active')
        is_accessible = request.GET.get('is_accessible')
        priority_level = request.GET.get('priority_level')

        # Build query
        query = supabase.table('polling_booths').select('*').eq('organization_id', organization_id)

        # Apply filters
        if constituency_id:
            query = query.eq('constituency_id', constituency_id)

        if ward_id:
            query = query.eq('ward_id', ward_id)

        if is_active is not None:
            query = query.eq('is_active', is_active.lower() == 'true')

        if is_accessible is not None:
            query = query.eq('is_accessible', is_accessible.lower() == 'true')

        if priority_level:
            query = query.eq('priority_level', int(priority_level))

        if search:
            query = query.or_(f'name.ilike.%{search}%,booth_number.ilike.%{search}%,address.ilike.%{search}%')

        # Calculate pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)

        # Execute query
        response = query.order('created_at', desc=True).execute()

        # Get total count
        count_response = supabase.table('polling_booths').select('id', count='exact').eq(
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
        # Require manager role or above
        if not request.user.profile.is_admin_or_above():
            return Response(
                {'error': 'Only managers and admins can create polling booths'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = PollingBoothSerializer(data=request.data)
        if serializer.is_valid():
            # Insert into Supabase
            try:
                booth_data = serializer.validated_data
                booth_data['organization_id'] = organization_id

                response = supabase.table('polling_booths').insert(booth_data).execute()

                return Response(response.data[0], status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def polling_booth_detail(request, booth_id):
    """
    GET: Retrieve a polling booth
    PUT/PATCH: Update a polling booth
    DELETE: Delete a polling booth
    """

    supabase = get_supabase_client()
    organization_id = str(request.user.profile.organization_id)

    # Check if booth exists and belongs to organization
    booth_response = supabase.table('polling_booths').select('*').eq('id', booth_id).eq(
        'organization_id', organization_id
    ).execute()

    if not booth_response.data:
        return Response(
            {'error': 'Polling booth not found'},
            status=status.HTTP_404_NOT_FOUND
        )

    booth = booth_response.data[0]

    if request.method == 'GET':
        return Response(booth)

    elif request.method in ['PUT', 'PATCH']:
        # Require manager role or above
        if not request.user.profile.is_admin_or_above():
            return Response(
                {'error': 'Only managers and admins can update polling booths'},
                status=status.HTTP_403_FORBIDDEN
            )

        partial = request.method == 'PATCH'
        serializer = PollingBoothSerializer(data=request.data, partial=partial)

        if serializer.is_valid():
            try:
                update_data = serializer.validated_data
                response = supabase.table('polling_booths').update(update_data).eq('id', booth_id).execute()

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
                {'error': 'Only admins can delete polling booths'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            supabase.table('polling_booths').delete().eq('id', booth_id).execute()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@require_role(['admin', 'manager', 'superadmin'])
def polling_booth_bulk_import(request):
    """
    Bulk import polling booths from CSV or Excel file

    Expected file format:
    - CSV or Excel (.csv, .xlsx, .xls)
    - Headers: constituency_code, ward_code (optional), booth_number, name, address,
               latitude, longitude, total_voters, male_voters, female_voters, transgender_voters,
               booth_type, is_accessible, building_name, priority_level, etc.

    Request body:
    - file: File upload
    - update_existing: Boolean (optional, default=False)
    """

    serializer = PollingBoothBulkImportSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get organization from user
    organization_id = str(request.user.profile.organization_id)

    # Process file
    service = PollingBoothBulkImportService(request.user, organization_id)
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
def polling_booth_import_status(request, job_id):
    """Get status of a bulk import job"""

    from api.models import BulkUploadJob, BulkUploadError

    try:
        job = BulkUploadJob.objects.get(job_id=job_id, created_by=request.user)

        # Get error details if exists
        errors = []
        if job.status == 'failed':
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
def polling_booth_statistics(request):
    """Get polling booth statistics for organization"""

    supabase = get_supabase_client()
    organization_id = str(request.user.profile.organization_id)

    # Get total counts
    total_booths_response = supabase.table('polling_booths').select('id', count='exact').eq(
        'organization_id', organization_id
    ).execute()
    total_booths = total_booths_response.count

    # Get active booths count
    active_booths_response = supabase.table('polling_booths').select('id', count='exact').eq(
        'organization_id', organization_id
    ).eq('is_active', True).execute()
    active_booths = active_booths_response.count

    # Get accessible booths count
    accessible_booths_response = supabase.table('polling_booths').select('id', count='exact').eq(
        'organization_id', organization_id
    ).eq('is_accessible', True).execute()
    accessible_booths = accessible_booths_response.count

    # Get total voters
    voters_response = supabase.table('polling_booths').select('total_voters').eq(
        'organization_id', organization_id
    ).execute()

    total_voters = sum(booth.get('total_voters', 0) for booth in voters_response.data)

    return Response({
        'total_booths': total_booths,
        'active_booths': active_booths,
        'inactive_booths': total_booths - active_booths,
        'accessible_booths': accessible_booths,
        'total_voters': total_voters,
        'average_voters_per_booth': total_voters // total_booths if total_booths > 0 else 0
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def polling_booths_near(request):
    """
    Find polling booths near a location

    Query parameters:
    - latitude: float (required)
    - longitude: float (required)
    - radius_meters: int (optional, default=5000)
    """

    latitude = request.GET.get('latitude')
    longitude = request.GET.get('longitude')
    radius_meters = int(request.GET.get('radius_meters', 5000))

    if not latitude or not longitude:
        return Response(
            {'error': 'Both latitude and longitude are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return Response(
            {'error': 'Invalid latitude or longitude values'},
            status=status.HTTP_400_BAD_REQUEST
        )

    supabase = get_supabase_client()
    organization_id = str(request.user.profile.organization_id)

    # Use PostGIS function to find nearby booths
    try:
        response = supabase.rpc('find_booths_near', {
            'p_latitude': latitude,
            'p_longitude': longitude,
            'p_radius_meters': radius_meters
        }).eq('organization_id', organization_id).execute()

        return Response({
            'latitude': latitude,
            'longitude': longitude,
            'radius_meters': radius_meters,
            'booths_found': len(response.data),
            'booths': response.data
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
