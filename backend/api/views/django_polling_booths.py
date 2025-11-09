"""
Django Polling Booth API Views
Fetches polling booths from Django database (not Supabase)
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db import models
from api.models import PollingBooth, State, District, Constituency


@api_view(['GET'])
@permission_classes([AllowAny])  # Allow public access for map visualization
def django_polling_booths_list(request):
    """
    List all polling booths from Django database with pagination and filtering

    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Results per page (default: 100, max: 1000)
    - state: Filter by state code
    - district: Filter by district code
    - constituency: Filter by constituency code
    - has_gps: Filter booths with GPS coordinates (default: true for maps)
    """

    # Query parameters
    page = int(request.GET.get('page', 1))
    page_size = min(int(request.GET.get('page_size', 100)), 1000)  # Max 1000 per page
    state_code = request.GET.get('state')
    district_code = request.GET.get('district')
    constituency_code = request.GET.get('constituency')
    has_gps = request.GET.get('has_gps', 'true').lower() == 'true'

    # Build query
    queryset = PollingBooth.objects.select_related('state', 'district', 'constituency').all()

    # Apply filters
    if has_gps:
        queryset = queryset.exclude(latitude__isnull=True).exclude(longitude__isnull=True)

    if state_code:
        queryset = queryset.filter(state__code=state_code)

    if district_code:
        queryset = queryset.filter(district__code=district_code)

    if constituency_code:
        queryset = queryset.filter(constituency__code=constituency_code)

    # Order by constituency and booth number
    queryset = queryset.order_by('constituency__code', 'booth_number')

    # Paginate
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)

    # Serialize data
    booths_data = []
    for booth in page_obj:
        booths_data.append({
            'id': booth.id,
            'booth_number': booth.booth_number,
            'name': booth.name,
            'building_name': booth.building_name,
            'address': booth.address,
            'area': booth.area,
            'landmark': booth.landmark,
            'pincode': booth.pincode,
            'latitude': str(booth.latitude) if booth.latitude else None,
            'longitude': str(booth.longitude) if booth.longitude else None,
            'total_voters': booth.total_voters,
            'male_voters': booth.male_voters,
            'female_voters': booth.female_voters,
            'other_voters': booth.other_voters,
            'is_active': booth.is_active,
            'is_accessible': booth.is_accessible,
            'state': {
                'code': booth.state.code,
                'name': booth.state.name,
            },
            'district': {
                'code': booth.district.code,
                'name': booth.district.name,
            },
            'constituency': {
                'code': booth.constituency.code,
                'name': booth.constituency.name,
                'type': booth.constituency.constituency_type,
            },
        })

    # Return paginated response
    return Response({
        'count': paginator.count,
        'total_pages': paginator.num_pages,
        'current_page': page,
        'page_size': page_size,
        'results': booths_data,
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def django_polling_booths_statistics(request):
    """
    Get polling booth statistics from Django database
    """
    total_booths = PollingBooth.objects.count()
    booths_with_gps = PollingBooth.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True).count()
    total_voters = PollingBooth.objects.aggregate(total=models.Sum('total_voters'))['total'] or 0

    states = State.objects.all()
    districts = District.objects.all()
    constituencies = Constituency.objects.all()

    return Response({
        'total_booths': total_booths,
        'booths_with_gps': booths_with_gps,
        'gps_coverage_percent': round((booths_with_gps / total_booths * 100), 2) if total_booths > 0 else 0,
        'total_voters': total_voters,
        'states_count': states.count(),
        'districts_count': districts.count(),
        'constituencies_count': constituencies.count(),
        'states': [{'code': s.code, 'name': s.name} for s in states],
        'districts': [{'code': d.code, 'name': d.name, 'state': d.state.code} for d in districts],
        'constituencies': [{'code': c.code, 'name': c.name, 'state': c.state.code} for c in constituencies],
    })
