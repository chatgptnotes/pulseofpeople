"""
Polling Booth Management Views with Bulk Upload Support
"""
import io
import csv
import pandas as pd
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.models import PollingBooth, State, District, Constituency
from api.political_serializers import (
    PollingBoothSerializer,
    PollingBoothListSerializer
)
from api.permissions.role_permissions import CanManagePollingBooths


class PollingBoothViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Polling Booth management with bulk upload support

    Endpoints:
    - GET    /api/polling-booths/             - List all booths (with data isolation)
    - GET    /api/polling-booths/{id}/        - Retrieve single booth
    - POST   /api/polling-booths/             - Create single booth (Admin+)
    - PUT    /api/polling-booths/{id}/        - Update booth (Manager+)
    - PATCH  /api/polling-booths/{id}/        - Partial update (Manager+)
    - DELETE /api/polling-booths/{id}/        - Delete booth (Manager+)
    - POST   /api/polling-booths/bulk-upload/ - Bulk upload CSV/Excel (Admin+)
    - GET    /api/polling-booths/template/    - Download CSV template

    Data Isolation Rules:
    - Superadmin: sees all booths
    - Admin: sees booths in their assigned state
    - Manager: sees booths in their assigned district
    - Analyst: sees booths in their assigned constituency
    - User: sees booths in their assigned ward (via constituency)
    """
    queryset = PollingBooth.objects.select_related(
        'state', 'district', 'constituency'
    ).all()
    permission_classes = [IsAuthenticated, CanManagePollingBooths]

    def get_serializer_class(self):
        """Use lightweight serializer for lists"""
        if self.action == 'list':
            return PollingBoothListSerializer
        return PollingBoothSerializer

    def get_queryset(self):
        """
        Apply role-based data isolation
        Filter booths based on user's role and assigned location
        """
        queryset = super().get_queryset()
        user = self.request.user

        try:
            profile = user.profile
            role = profile.role

            # Superadmin sees everything
            if role == 'superadmin':
                return queryset

            # Admin sees their assigned state
            elif role == 'admin':
                if profile.assigned_state:
                    return queryset.filter(state=profile.assigned_state)
                else:
                    # If no state assigned, return empty
                    return queryset.none()

            # Manager sees their assigned district
            elif role == 'manager':
                if profile.assigned_district:
                    return queryset.filter(district=profile.assigned_district)
                else:
                    # Fall back to state if only state is assigned
                    if profile.assigned_state:
                        return queryset.filter(state=profile.assigned_state)
                    return queryset.none()

            # Analyst sees their assigned constituency
            elif role == 'analyst':
                # Analysts see booths in their constituency (from text field)
                if profile.constituency:
                    return queryset.filter(
                        constituency__name__icontains=profile.constituency
                    )
                # Fall back to district
                elif profile.assigned_district:
                    return queryset.filter(district=profile.assigned_district)
                return queryset.none()

            # User sees booths in their ward/constituency area
            elif role == 'user':
                if profile.constituency:
                    return queryset.filter(
                        constituency__name__icontains=profile.constituency
                    )
                # Fall back to city-based filtering
                elif profile.city:
                    return queryset.filter(
                        district__name__icontains=profile.city
                    )
                return queryset.none()

            # Other roles (viewer, volunteer) see limited data
            else:
                if profile.assigned_district:
                    return queryset.filter(district=profile.assigned_district)
                return queryset.none()

        except Exception as e:
            # If no profile exists or error, return empty queryset
            return queryset.none()

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, CanManagePollingBooths])
    def bulk_upload(self, request):
        """
        Bulk upload polling booths from CSV or Excel file

        POST /api/polling-booths/bulk-upload/
        Content-Type: multipart/form-data
        Body: file (CSV or Excel)

        Required CSV columns:
        - booth_number: Official booth number (e.g., '001', '002A')
        - name: Polling booth name/location
        - state_code: State code (e.g., 'TN' for Tamil Nadu)
        - district_code: District code
        - constituency_code: Constituency code
        - address: Full address (optional)
        - area: Locality/area name (optional)
        - building_name: School/building name (optional)
        - landmark: Nearby landmark (optional)
        - pincode: PIN code (optional)
        - latitude: Geographic latitude (optional)
        - longitude: Geographic longitude (optional)
        - total_voters: Total registered voters (default: 0)
        - male_voters: Male voters (default: 0)
        - female_voters: Female voters (default: 0)
        - other_voters: Other gender voters (default: 0)
        - is_active: Active status (default: True)
        - is_accessible: Wheelchair accessible (default: True)

        Returns:
        {
            "success": true,
            "message": "Successfully uploaded 95 booths. 5 failed.",
            "total_rows": 100,
            "success_count": 95,
            "failed_count": 5,
            "errors": [
                {"row": 12, "error": "State 'XY' not found", "data": {...}},
                ...
            ]
        }
        """
        # Check role permission for bulk upload (Admin and above)
        try:
            if request.user.profile.role not in ['admin', 'superadmin']:
                return Response({
                    'success': False,
                    'error': 'Only admins and superadmins can bulk upload polling booths.'
                }, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({
                'success': False,
                'error': 'User profile not found.'
            }, status=status.HTTP_403_FORBIDDEN)

        # Check if file was uploaded
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No file uploaded. Please provide a CSV or Excel file.'
            }, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()

        # Validate file type
        if file_extension not in ['csv', 'xlsx', 'xls']:
            return Response({
                'success': False,
                'error': 'Invalid file type. Please upload a CSV or Excel file (.csv, .xlsx, .xls).'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validate file size (max 10MB)
        if uploaded_file.size > 10 * 1024 * 1024:
            return Response({
                'success': False,
                'error': 'File too large. Maximum size is 10MB.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read file into pandas DataFrame
            if file_extension == 'csv':
                df = pd.read_csv(io.BytesIO(uploaded_file.read()))
            else:
                df = pd.read_excel(io.BytesIO(uploaded_file.read()))

            # Validate required columns
            required_columns = ['booth_number', 'name', 'state_code', 'district_code', 'constituency_code']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                return Response({
                    'success': False,
                    'error': f'Missing required columns: {", ".join(missing_columns)}',
                    'required_columns': required_columns,
                    'found_columns': list(df.columns)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validate row count
            if len(df) == 0:
                return Response({
                    'success': False,
                    'error': 'File is empty. No rows to process.'
                }, status=status.HTTP_400_BAD_REQUEST)

            if len(df) > 10000:
                return Response({
                    'success': False,
                    'error': f'Too many rows ({len(df)}). Maximum is 10,000 rows per upload.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Process upload
            result = self._process_bulk_upload(df, request.user)

            return Response(result, status=status.HTTP_200_OK)

        except pd.errors.EmptyDataError:
            return Response({
                'success': False,
                'error': 'File is empty or has no data.'
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'success': False,
                'error': f'Failed to process file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_bulk_upload(self, df, user):
        """
        Process the bulk upload DataFrame
        Returns dict with upload results
        """
        success_count = 0
        failed_count = 0
        errors = []

        # Cache lookups for performance
        state_cache = {s.code: s for s in State.objects.all()}
        district_cache = {d.code: d for d in District.objects.select_related('state').all()}
        constituency_cache = {c.code: c for c in Constituency.objects.select_related('state', 'district').all()}

        # Process each row
        for idx, row in df.iterrows():
            row_number = idx + 2  # +2 for header row and 0-based index

            try:
                # Validate and get foreign key objects
                state_code = str(row.get('state_code', '')).strip()
                district_code = str(row.get('district_code', '')).strip()
                constituency_code = str(row.get('constituency_code', '')).strip()

                if not state_code or state_code not in state_cache:
                    errors.append({
                        'row': row_number,
                        'error': f'Invalid or missing state_code: {state_code}',
                        'data': row.to_dict()
                    })
                    failed_count += 1
                    continue

                if not district_code or district_code not in district_cache:
                    errors.append({
                        'row': row_number,
                        'error': f'Invalid or missing district_code: {district_code}',
                        'data': row.to_dict()
                    })
                    failed_count += 1
                    continue

                if not constituency_code or constituency_code not in constituency_cache:
                    errors.append({
                        'row': row_number,
                        'error': f'Invalid or missing constituency_code: {constituency_code}',
                        'data': row.to_dict()
                    })
                    failed_count += 1
                    continue

                state = state_cache[state_code]
                district = district_cache[district_code]
                constituency = constituency_cache[constituency_code]

                # Validate booth_number and name
                booth_number = str(row.get('booth_number', '')).strip()
                name = str(row.get('name', '')).strip()

                if not booth_number:
                    errors.append({
                        'row': row_number,
                        'error': 'booth_number is required',
                        'data': row.to_dict()
                    })
                    failed_count += 1
                    continue

                if not name:
                    errors.append({
                        'row': row_number,
                        'error': 'name is required',
                        'data': row.to_dict()
                    })
                    failed_count += 1
                    continue

                # Prepare booth data
                booth_data = {
                    'state': state,
                    'district': district,
                    'constituency': constituency,
                    'booth_number': booth_number,
                    'name': name,
                    'building_name': str(row.get('building_name', '')).strip(),
                    'address': str(row.get('address', '')).strip(),
                    'area': str(row.get('area', '')).strip(),
                    'landmark': str(row.get('landmark', '')).strip(),
                    'pincode': str(row.get('pincode', '')).strip(),
                    'total_voters': int(row.get('total_voters', 0)) if pd.notna(row.get('total_voters')) else 0,
                    'male_voters': int(row.get('male_voters', 0)) if pd.notna(row.get('male_voters')) else 0,
                    'female_voters': int(row.get('female_voters', 0)) if pd.notna(row.get('female_voters')) else 0,
                    'other_voters': int(row.get('other_voters', 0)) if pd.notna(row.get('other_voters')) else 0,
                    'is_active': bool(row.get('is_active', True)) if pd.notna(row.get('is_active')) else True,
                    'is_accessible': bool(row.get('is_accessible', True)) if pd.notna(row.get('is_accessible')) else True,
                }

                # Add coordinates if provided
                if pd.notna(row.get('latitude')):
                    try:
                        booth_data['latitude'] = float(row.get('latitude'))
                    except (ValueError, TypeError):
                        pass

                if pd.notna(row.get('longitude')):
                    try:
                        booth_data['longitude'] = float(row.get('longitude'))
                    except (ValueError, TypeError):
                        pass

                # Check for duplicate booth_number in constituency
                existing = PollingBooth.objects.filter(
                    constituency=constituency,
                    booth_number=booth_number
                ).first()

                if existing:
                    # Update existing booth
                    for key, value in booth_data.items():
                        setattr(existing, key, value)
                    existing.save()
                    success_count += 1
                else:
                    # Create new booth
                    PollingBooth.objects.create(**booth_data)
                    success_count += 1

            except Exception as e:
                errors.append({
                    'row': row_number,
                    'error': str(e),
                    'data': row.to_dict() if hasattr(row, 'to_dict') else {}
                })
                failed_count += 1

        # Prepare response
        total_rows = len(df)

        return {
            'success': True,
            'message': f'Successfully processed {success_count} booths. {failed_count} failed.',
            'total_rows': total_rows,
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors[:100]  # Limit errors to first 100 for performance
        }

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def template(self, request):
        """
        Download CSV template for bulk upload

        GET /api/polling-booths/template/

        Returns: CSV file with headers and sample data
        """
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'booth_number', 'name', 'state_code', 'district_code', 'constituency_code',
            'building_name', 'address', 'area', 'landmark', 'pincode',
            'latitude', 'longitude',
            'total_voters', 'male_voters', 'female_voters', 'other_voters',
            'is_active', 'is_accessible'
        ])

        # Write sample rows
        writer.writerow([
            '001', 'Government High School, Main Road', 'TN', 'TN001', 'TN001',
            'Government High School', '123 Main Road, Chennai', 'Anna Nagar', 'Near Bus Stand', '600001',
            '13.082680', '80.270718',
            '1200', '600', '580', '20',
            'True', 'True'
        ])
        writer.writerow([
            '002', 'Corporation Primary School, West Street', 'TN', 'TN001', 'TN001',
            'Corporation Primary School', '456 West Street, Chennai', 'Anna Nagar West', 'Near Park', '600001',
            '13.082123', '80.271234',
            '1500', '750', '730', '20',
            'True', 'True'
        ])
        writer.writerow([
            '003A', 'Community Hall, East Avenue', 'TN', 'TN001', 'TN001',
            'Community Hall', '789 East Avenue, Chennai', 'Anna Nagar East', 'Near Temple', '600001',
            '', '',
            '800', '400', '390', '10',
            'True', 'False'
        ])

        # Create HTTP response
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="polling_booth_upload_template.csv"'

        return response

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        """
        Get statistics about polling booths

        GET /api/polling-booths/stats/

        Returns booth counts and totals filtered by user's role
        """
        queryset = self.get_queryset()

        total_booths = queryset.count()
        total_voters = sum(queryset.values_list('total_voters', flat=True))
        active_booths = queryset.filter(is_active=True).count()
        accessible_booths = queryset.filter(is_accessible=True).count()

        # Group by constituency
        by_constituency = {}
        for booth in queryset.values('constituency__name').annotate(
            count=Count('id'),
            voters=Sum('total_voters')
        ):
            by_constituency[booth['constituency__name']] = {
                'booths': booth['count'],
                'voters': booth['voters'] or 0
            }

        return Response({
            'total_booths': total_booths,
            'active_booths': active_booths,
            'accessible_booths': accessible_booths,
            'total_voters': total_voters,
            'by_constituency': by_constituency
        })
