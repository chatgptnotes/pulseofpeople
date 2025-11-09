"""
Serializers for Geography Models (Wards and Polling Booths)
These work with Supabase data (not Django ORM)
"""

from rest_framework import serializers
from decimal import Decimal
from typing import Dict, Any


class WardSerializer(serializers.Serializer):
    """Serializer for Ward data from Supabase"""

    id = serializers.UUIDField(read_only=True)
    organization_id = serializers.UUIDField(required=True)
    constituency_id = serializers.UUIDField(required=True)

    # Basic Info
    name = serializers.CharField(max_length=255, required=True)
    code = serializers.CharField(max_length=50, required=True)
    ward_number = serializers.IntegerField(required=False, allow_null=True)

    # Geographic Info
    boundaries = serializers.JSONField(required=False, allow_null=True)

    # Demographics
    population = serializers.IntegerField(required=False, allow_null=True, min_value=0)
    voter_count = serializers.IntegerField(default=0, min_value=0)
    total_booths = serializers.IntegerField(default=0, min_value=0)
    demographics = serializers.JSONField(default=dict, required=False)

    # Socioeconomic Data
    income_level = serializers.ChoiceField(
        choices=['low', 'middle', 'high'],
        required=False,
        allow_null=True
    )
    urbanization = serializers.ChoiceField(
        choices=['urban', 'semi_urban', 'rural'],
        required=False,
        allow_null=True
    )
    literacy_rate = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True,
        min_value=Decimal('0'),
        max_value=Decimal('100')
    )

    # Metadata
    metadata = serializers.JSONField(default=dict, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_code(self, value):
        """Validate ward code format"""
        import re
        pattern = r'^[A-Z]{2}-AC-\d{3}-W-\d{3}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Ward code must be in format: XX-AC-XXX-W-XXX (e.g., TN-AC-001-W-001)"
            )
        return value

    def validate(self, data):
        """Cross-field validation"""
        # Voter count should not exceed population
        if data.get('population') and data.get('voter_count'):
            if data['voter_count'] > data['population']:
                raise serializers.ValidationError({
                    'voter_count': 'Voter count cannot exceed population'
                })
        return data


class PollingBoothSerializer(serializers.Serializer):
    """Serializer for Polling Booth data from Supabase"""

    id = serializers.UUIDField(read_only=True)
    organization_id = serializers.UUIDField(required=True)
    constituency_id = serializers.UUIDField(required=True)
    ward_id = serializers.UUIDField(required=False, allow_null=True)

    # Booth Identity
    booth_number = serializers.CharField(max_length=50, required=True)
    name = serializers.CharField(max_length=255, required=True)

    # Location
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    latitude = serializers.DecimalField(
        max_digits=10,
        decimal_places=8,
        required=False,
        allow_null=True,
        min_value=Decimal('-90'),
        max_value=Decimal('90')
    )
    longitude = serializers.DecimalField(
        max_digits=11,
        decimal_places=8,
        required=False,
        allow_null=True,
        min_value=Decimal('-180'),
        max_value=Decimal('180')
    )
    landmark = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    # Voter Stats
    total_voters = serializers.IntegerField(default=0, min_value=0)
    male_voters = serializers.IntegerField(default=0, min_value=0)
    female_voters = serializers.IntegerField(default=0, min_value=0)
    transgender_voters = serializers.IntegerField(default=0, min_value=0)

    # Booth Details
    booth_type = serializers.ChoiceField(
        choices=['regular', 'auxiliary', 'special'],
        default='regular',
        required=False
    )
    is_accessible = serializers.BooleanField(default=True)
    facilities = serializers.JSONField(default=list, required=False)

    # Building Info
    building_name = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    building_type = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    floor_number = serializers.IntegerField(required=False, allow_null=True)
    room_number = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)

    # Operational Info
    is_active = serializers.BooleanField(default=True)
    last_used_election = serializers.DateField(required=False, allow_null=True)
    booth_level_officer = serializers.CharField(max_length=255, required=False, allow_blank=True, allow_null=True)
    contact_number = serializers.CharField(max_length=20, required=False, allow_blank=True, allow_null=True)

    # Sentiment & Strategy
    party_strength = serializers.JSONField(required=False, allow_null=True)
    swing_potential = serializers.ChoiceField(
        choices=['high', 'medium', 'low'],
        required=False,
        allow_null=True
    )
    priority_level = serializers.IntegerField(
        default=3,
        min_value=1,
        max_value=5,
        required=False
    )

    # Metadata
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.JSONField(default=dict, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate(self, data):
        """Cross-field validation"""
        # Sum of gender voters should not exceed total
        total = data.get('total_voters', 0)
        male = data.get('male_voters', 0)
        female = data.get('female_voters', 0)
        transgender = data.get('transgender_voters', 0)

        gender_sum = male + female + transgender
        if gender_sum > total:
            raise serializers.ValidationError({
                'total_voters': f'Sum of gender voters ({gender_sum}) exceeds total_voters ({total})'
            })

        # Both latitude and longitude must be provided together or not at all
        lat = data.get('latitude')
        lon = data.get('longitude')
        if (lat is not None and lon is None) or (lat is None and lon is not None):
            raise serializers.ValidationError({
                'latitude': 'Both latitude and longitude must be provided together',
                'longitude': 'Both latitude and longitude must be provided together'
            })

        return data


class BulkImportResponseSerializer(serializers.Serializer):
    """Serializer for bulk import response"""
    job_id = serializers.UUIDField(read_only=True)
    status = serializers.ChoiceField(
        choices=['pending', 'validating', 'processing', 'completed', 'failed'],
        read_only=True
    )
    total_rows = serializers.IntegerField(read_only=True)
    processed_rows = serializers.IntegerField(read_only=True)
    success_count = serializers.IntegerField(read_only=True)
    failed_count = serializers.IntegerField(read_only=True)
    validation_errors = serializers.JSONField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    completed_at = serializers.DateTimeField(read_only=True, allow_null=True)


class WardBulkImportSerializer(serializers.Serializer):
    """Serializer for ward bulk import request"""
    file = serializers.FileField(required=True)
    organization_id = serializers.UUIDField(required=True)
    update_existing = serializers.BooleanField(default=False)

    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_ext = value.name.lower()[value.name.lower().rfind('.'):]

        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File too large. Maximum size: 10MB. Your file: {value.size / (1024*1024):.2f}MB"
            )

        return value


class PollingBoothBulkImportSerializer(serializers.Serializer):
    """Serializer for polling booth bulk import request"""
    file = serializers.FileField(required=True)
    organization_id = serializers.UUIDField(required=True)
    update_existing = serializers.BooleanField(default=False)

    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file extension
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_ext = value.name.lower()[value.name.lower().rfind('.'):]

        if file_ext not in allowed_extensions:
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File too large. Maximum size: 10MB. Your file: {value.size / (1024*1024):.2f}MB"
            )

        return value
