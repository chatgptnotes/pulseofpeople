"""
Serializers for Political Platform Models
"""
from rest_framework import serializers
from .models import (
    State, District, Constituency, PollingBooth, PoliticalParty, IssueCategory,
    VoterSegment, DirectFeedback, FieldReport, SentimentData, BoothAgent
)
from django.contrib.auth.models import User


# =====================================================
# LOCATION & GEOGRAPHY SERIALIZERS
# =====================================================

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'name', 'code', 'capital', 'region', 'total_districts', 'total_constituencies', 'created_at']
        read_only_fields = ['id', 'created_at']


class DistrictSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)
    state_code = serializers.CharField(source='state.code', read_only=True)

    class Meta:
        model = District
        fields = [
            'id', 'name', 'code', 'state', 'state_name', 'state_code',
            'headquarters', 'population', 'area_sq_km', 'total_wards', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConstituencySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = Constituency
        fields = [
            'id', 'code', 'name', 'number', 'constituency_type', 'reserved_for',
            'state', 'state_name', 'district', 'district_name',
            'total_voters', 'total_wards', 'total_booths', 'area_sq_km',
            'center_lat', 'center_lng', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConstituencyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists"""
    state_code = serializers.CharField(source='state.code', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = Constituency
        fields = ['id', 'code', 'name', 'number', 'state_code', 'district_name']


class PollingBoothSerializer(serializers.ModelSerializer):
    """Serializer for Polling Booths"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)

    class Meta:
        model = PollingBooth
        fields = [
            'id', 'booth_number', 'name', 'building_name',
            'state', 'state_name', 'district', 'district_name',
            'constituency', 'constituency_name',
            'address', 'area', 'landmark', 'pincode',
            'latitude', 'longitude',
            'total_voters', 'male_voters', 'female_voters', 'other_voters',
            'is_active', 'is_accessible', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PollingBoothListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for polling booth lists"""
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)

    class Meta:
        model = PollingBooth
        fields = ['id', 'booth_number', 'name', 'area', 'constituency_name', 'total_voters']


# =====================================================
# POLITICAL DATA SERIALIZERS
# =====================================================

class PoliticalPartySerializer(serializers.ModelSerializer):
    active_states_list = StateSerializer(source='active_states', many=True, read_only=True)

    class Meta:
        model = PoliticalParty
        fields = [
            'id', 'name', 'short_name', 'symbol', 'symbol_image', 'status',
            'headquarters', 'website', 'founded_date', 'ideology', 'description',
            'active_states', 'active_states_list', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class IssueCategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    subcategories_count = serializers.SerializerMethodField()

    class Meta:
        model = IssueCategory
        fields = [
            'id', 'name', 'description', 'parent', 'parent_name',
            'color', 'icon', 'priority', 'is_active',
            'subcategories_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_subcategories_count(self, obj):
        return obj.subcategories.count()


class VoterSegmentSerializer(serializers.ModelSerializer):
    key_issues_list = IssueCategorySerializer(source='key_issues', many=True, read_only=True)

    class Meta:
        model = VoterSegment
        fields = [
            'id', 'name', 'description', 'estimated_population', 'priority_level',
            'key_issues', 'key_issues_list', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# =====================================================
# FEEDBACK SERIALIZERS
# =====================================================

class DirectFeedbackSerializer(serializers.ModelSerializer):
    """Full serializer for DirectFeedback with all details"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    issue_name = serializers.CharField(source='issue_category.name', read_only=True)
    voter_segment_name = serializers.CharField(source='voter_segment.name', read_only=True, allow_null=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True, allow_null=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = DirectFeedback
        fields = [
            'id', 'feedback_id', 'citizen_name', 'citizen_age', 'citizen_phone', 'citizen_email',
            'state', 'state_name', 'district', 'district_name',
            'constituency', 'constituency_name', 'ward', 'booth_number', 'detailed_location',
            'issue_category', 'issue_name', 'message_text', 'expectations',
            'voter_segment', 'voter_segment_name',
            'audio_file_url', 'video_file_url', 'image_urls',
            'transcription', 'ai_summary', 'ai_sentiment_score', 'ai_sentiment_polarity',
            'ai_extracted_issues', 'ai_urgency', 'ai_confidence', 'ai_analysis_metadata',
            'status', 'assigned_to', 'assigned_to_name', 'reviewed_by', 'reviewed_by_name',
            'review_notes', 'submitted_at', 'analyzed_at', 'reviewed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'feedback_id', 'submitted_at', 'analyzed_at', 'reviewed_at',
            'created_at', 'updated_at'
        ]


class DirectFeedbackCreateSerializer(serializers.ModelSerializer):
    """Serializer for public feedback submission (no auth required)"""

    class Meta:
        model = DirectFeedback
        fields = [
            'citizen_name', 'citizen_age', 'citizen_phone', 'citizen_email',
            'state', 'district', 'constituency', 'ward', 'booth_number', 'detailed_location',
            'issue_category', 'message_text', 'expectations', 'voter_segment',
            'audio_file_url', 'video_file_url', 'image_urls'
        ]

    def validate_citizen_age(self, value):
        if value and (value < 18 or value > 120):
            raise serializers.ValidationError("Age must be between 18 and 120")
        return value


class DirectFeedbackListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for feedback lists"""
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    issue_name = serializers.CharField(source='issue_category.name', read_only=True)

    class Meta:
        model = DirectFeedback
        fields = [
            'id', 'feedback_id', 'citizen_name', 'ward', 'booth_number',
            'state_name', 'district_name', 'constituency_name',
            'issue_name', 'status', 'ai_sentiment_polarity', 'ai_urgency',
            'submitted_at'
        ]


# =====================================================
# FIELD REPORT SERIALIZERS
# =====================================================

class FieldReportSerializer(serializers.ModelSerializer):
    """Full serializer for FieldReport with nested user info"""
    # Submitted by user info
    submitted_by_username = serializers.CharField(source='submitted_by.username', read_only=True)
    submitted_by_name = serializers.SerializerMethodField()
    submitted_by_email = serializers.CharField(source='submitted_by.email', read_only=True)
    submitted_by_role = serializers.SerializerMethodField()

    # Reviewed by user info
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True, allow_null=True)
    reviewed_by_name = serializers.SerializerMethodField()

    # Location info
    state_name = serializers.CharField(source='state.name', read_only=True, allow_null=True)
    district_name = serializers.CharField(source='district.name', read_only=True, allow_null=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True, allow_null=True)

    class Meta:
        model = FieldReport
        fields = [
            'id', 'report_id',
            # Basic info
            'report_type', 'title', 'description',
            # Location
            'state', 'state_name', 'district', 'district_name',
            'constituency', 'constituency_name', 'ward', 'latitude', 'longitude',
            # Submission
            'submitted_by', 'submitted_by_username', 'submitted_by_name',
            'submitted_by_email', 'submitted_by_role',
            'status', 'attachments',
            # Sentiment and priority
            'voter_sentiment', 'priority',
            # Review
            'reviewed_by', 'reviewed_by_username', 'reviewed_by_name',
            'review_notes', 'reviewed_at',
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'report_id', 'submitted_by', 'reviewed_by', 'reviewed_at',
            'created_at', 'updated_at'
        ]

    def get_submitted_by_name(self, obj):
        """Get full name of submitter"""
        if obj.submitted_by:
            return f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}".strip() or obj.submitted_by.username
        return None

    def get_submitted_by_role(self, obj):
        """Get role of submitter"""
        if obj.submitted_by and hasattr(obj.submitted_by, 'profile'):
            return obj.submitted_by.profile.role
        return None

    def get_reviewed_by_name(self, obj):
        """Get full name of reviewer"""
        if obj.reviewed_by:
            return f"{obj.reviewed_by.first_name} {obj.reviewed_by.last_name}".strip() or obj.reviewed_by.username
        return None

    def validate(self, attrs):
        """Validate field report data"""
        # Ensure title is provided
        if not attrs.get('title', '').strip():
            raise serializers.ValidationError({'title': 'Title is required'})

        # Ensure description is provided
        if not attrs.get('description', '').strip():
            raise serializers.ValidationError({'description': 'Description is required'})

        # Ensure ward is provided
        if not attrs.get('ward', '').strip():
            raise serializers.ValidationError({'ward': 'Ward is required'})

        # Validate coordinates if provided
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        if latitude is not None and (latitude < -90 or latitude > 90):
            raise serializers.ValidationError({'latitude': 'Latitude must be between -90 and 90'})
        if longitude is not None and (longitude < -180 or longitude > 180):
            raise serializers.ValidationError({'longitude': 'Longitude must be between -180 and 180'})

        return attrs

    def create(self, validated_data):
        """Auto-assign submitted_by from request user"""
        validated_data['submitted_by'] = self.context['request'].user
        return super().create(validated_data)


class FieldReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for report lists"""
    submitted_by_name = serializers.SerializerMethodField()
    constituency_name = serializers.CharField(source='constituency.name', read_only=True, allow_null=True)
    district_name = serializers.CharField(source='district.name', read_only=True, allow_null=True)

    class Meta:
        model = FieldReport
        fields = [
            'id', 'report_id', 'report_type', 'title', 'ward',
            'submitted_by_name', 'constituency_name', 'district_name',
            'status', 'priority', 'voter_sentiment', 'created_at'
        ]

    def get_submitted_by_name(self, obj):
        """Get full name of submitter"""
        if obj.submitted_by:
            return f"{obj.submitted_by.first_name} {obj.submitted_by.last_name}".strip() or obj.submitted_by.username
        return None


# =====================================================
# SENTIMENT DATA SERIALIZERS
# =====================================================

class SentimentDataSerializer(serializers.ModelSerializer):
    """Serializer for sentiment analytics data"""
    issue_name = serializers.CharField(source='issue.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    voter_segment_name = serializers.CharField(source='voter_segment.name', read_only=True, allow_null=True)

    class Meta:
        model = SentimentData
        fields = [
            'id', 'source_type', 'source_id', 'issue', 'issue_name',
            'sentiment_score', 'polarity', 'confidence',
            'state', 'state_name', 'district', 'district_name',
            'constituency', 'constituency_name', 'ward',
            'voter_segment', 'voter_segment_name', 'timestamp', 'created_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at']


# =====================================================
# BOOTH AGENT SERIALIZERS
# =====================================================

class BoothAgentSerializer(serializers.ModelSerializer):
    """Serializer for booth agent profiles (Admin3)"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    focus_segments_list = VoterSegmentSerializer(source='focus_segments', many=True, read_only=True)

    class Meta:
        model = BoothAgent
        fields = [
            'id', 'user', 'user_name', 'username', 'email',
            'state', 'state_name', 'district', 'district_name',
            'constituency', 'constituency_name', 'assigned_wards', 'assigned_booths',
            'focus_segments', 'focus_segments_list', 'total_reports',
            'total_feedback_collected', 'last_report_date', 'phone',
            'is_active', 'joined_date', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_reports', 'total_feedback_collected', 'last_report_date',
            'joined_date', 'created_at', 'updated_at'
        ]
