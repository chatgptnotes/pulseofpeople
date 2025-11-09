"""
Serializers for Core Political Platform Models - Workstream 2
Includes: Voter, VoterInteraction, Campaign, SocialMediaPost, Alert, Event, Volunteer, Expense, Enhanced Organization
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Voter, VoterInteraction, Campaign, SocialMediaPost, Alert, Event,
    VolunteerProfile, Expense, Organization,
    Constituency, District, State
)


# ==================== ORGANIZATION SERIALIZERS ====================

class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for organization listing"""
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'organization_type', 'subscription_plan', 'is_active', 'created_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """Full organization serializer"""
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'logo', 'organization_type', 'contact_email', 'contact_phone',
            'address', 'city', 'state', 'website', 'social_media_links', 'subscription_plan',
            'subscription_status', 'subscription_expires_at', 'max_users', 'settings',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== VOTER SERIALIZERS ====================

class VoterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for voter listing"""
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)

    class Meta:
        model = Voter
        fields = [
            'id', 'voter_id', 'first_name', 'last_name', 'age', 'gender', 'phone',
            'ward', 'constituency_name', 'district_name', 'party_affiliation',
            'sentiment', 'influence_level', 'is_active', 'created_at'
        ]


class VoterDetailSerializer(serializers.ModelSerializer):
    """Detailed voter serializer with all fields"""
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    state_name = serializers.CharField(source='state.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    recent_interactions = serializers.SerializerMethodField()

    class Meta:
        model = Voter
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'interaction_count',
                           'positive_interactions', 'negative_interactions']

    def get_recent_interactions(self, obj):
        """Get last 5 interactions"""
        interactions = obj.interactions.all()[:5]
        return VoterInteractionListSerializer(interactions, many=True).data


class VoterCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating voters with validation"""
    class Meta:
        model = Voter
        exclude = ['created_by', 'created_at', 'updated_at', 'interaction_count',
                  'positive_interactions', 'negative_interactions']

    def validate_voter_id(self, value):
        """Ensure voter ID is unique"""
        if Voter.objects.filter(voter_id=value).exists():
            raise serializers.ValidationError("A voter with this ID already exists.")
        return value

    def create(self, validated_data):
        """Auto-assign created_by from request user"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class VoterUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating voters (partial updates allowed)"""
    class Meta:
        model = Voter
        exclude = ['voter_id', 'created_by', 'created_at', 'updated_at']


# ==================== VOTER INTERACTION SERIALIZERS ====================

class VoterInteractionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for interaction listing"""
    voter_name = serializers.SerializerMethodField()
    contacted_by_name = serializers.CharField(source='contacted_by.get_full_name', read_only=True)

    class Meta:
        model = VoterInteraction
        fields = [
            'id', 'voter', 'voter_name', 'interaction_type', 'contacted_by_name',
            'interaction_date', 'sentiment', 'follow_up_required', 'follow_up_date'
        ]

    def get_voter_name(self, obj):
        return f"{obj.voter.first_name} {obj.voter.last_name}"


class VoterInteractionDetailSerializer(serializers.ModelSerializer):
    """Detailed interaction serializer"""
    voter_name = serializers.SerializerMethodField()
    contacted_by_name = serializers.CharField(source='contacted_by.get_full_name', read_only=True)

    class Meta:
        model = VoterInteraction
        fields = '__all__'
        read_only_fields = ['id', 'interaction_date', 'created_at']

    def get_voter_name(self, obj):
        return f"{obj.voter.first_name} {obj.voter.last_name}"


class VoterInteractionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating interactions"""
    class Meta:
        model = VoterInteraction
        exclude = ['contacted_by', 'interaction_date', 'created_at']

    def create(self, validated_data):
        """Auto-assign contacted_by from request user and update voter stats"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['contacted_by'] = request.user

        # Create interaction
        interaction = super().create(validated_data)

        # Update voter interaction counts
        voter = interaction.voter
        voter.interaction_count += 1
        voter.last_contacted_at = interaction.interaction_date
        if interaction.sentiment == 'positive':
            voter.positive_interactions += 1
        elif interaction.sentiment == 'negative':
            voter.negative_interactions += 1
        voter.save()

        return interaction


# ==================== CAMPAIGN SERIALIZERS ====================

class CampaignListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for campaign listing"""
    manager_name = serializers.CharField(source='campaign_manager.get_full_name', read_only=True)
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'campaign_name', 'campaign_type', 'start_date', 'end_date', 'status',
            'budget', 'spent_amount', 'manager_name', 'team_count', 'created_at'
        ]

    def get_team_count(self, obj):
        return obj.team_members.count()


class CampaignDetailSerializer(serializers.ModelSerializer):
    """Detailed campaign serializer"""
    manager_name = serializers.CharField(source='campaign_manager.get_full_name', read_only=True)
    target_constituency_name = serializers.CharField(source='target_constituency.name', read_only=True)
    team_members_details = serializers.SerializerMethodField()
    budget_spent_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_team_members_details(self, obj):
        """Get team member names"""
        return [{'id': u.id, 'name': u.get_full_name() or u.username, 'email': u.email}
                for u in obj.team_members.all()]

    def get_budget_spent_percentage(self, obj):
        """Calculate budget spent percentage"""
        if obj.budget > 0:
            return round((float(obj.spent_amount) / float(obj.budget)) * 100, 2)
        return 0


class CampaignCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating campaigns"""
    class Meta:
        model = Campaign
        exclude = ['created_by', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate start date is before end date"""
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("Start date must be before end date")
        return data

    def create(self, validated_data):
        """Auto-assign created_by"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user

        # Extract team_members before creating
        team_members = validated_data.pop('team_members', [])
        campaign = super().create(validated_data)
        campaign.team_members.set(team_members)
        return campaign


# ==================== SOCIAL MEDIA POST SERIALIZERS ====================

class SocialMediaPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for social post listing"""
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)

    class Meta:
        model = SocialMediaPost
        fields = [
            'id', 'platform', 'post_content', 'posted_at', 'reach', 'engagement_count',
            'likes', 'shares', 'sentiment_score', 'posted_by_name', 'campaign_name',
            'is_published', 'created_at'
        ]


class SocialMediaPostDetailSerializer(serializers.ModelSerializer):
    """Detailed social post serializer"""
    posted_by_name = serializers.CharField(source='posted_by.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    engagement_rate = serializers.SerializerMethodField()

    class Meta:
        model = SocialMediaPost
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_engagement_rate(self, obj):
        """Calculate engagement rate (engagement / reach)"""
        if obj.reach > 0:
            return round((obj.engagement_count / obj.reach) * 100, 2)
        return 0


class SocialMediaPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating social posts"""
    class Meta:
        model = SocialMediaPost
        exclude = ['posted_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Auto-assign posted_by"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['posted_by'] = request.user
        return super().create(validated_data)


# ==================== ALERT SERIALIZERS ====================

class AlertListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for alert listing"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'title', 'message', 'priority', 'is_read',
            'target_role', 'created_by_name', 'created_at', 'expires_at'
        ]


class AlertDetailSerializer(serializers.ModelSerializer):
    """Detailed alert serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    target_users_details = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def get_target_users_details(self, obj):
        """Get target user names"""
        return [{'id': u.id, 'name': u.get_full_name() or u.username, 'email': u.email}
                for u in obj.target_users.all()]


class AlertCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating alerts"""
    class Meta:
        model = Alert
        exclude = ['created_by', 'created_at', 'is_read', 'read_at']

    def create(self, validated_data):
        """Auto-assign created_by"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user

        # Extract target_users before creating
        target_users = validated_data.pop('target_users', [])
        alert = super().create(validated_data)
        alert.target_users.set(target_users)
        return alert


# ==================== EVENT SERIALIZERS ====================

class EventListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for event listing"""
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    volunteer_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'event_name', 'event_type', 'start_datetime', 'end_datetime', 'location',
            'status', 'expected_attendance', 'actual_attendance', 'organizer_name',
            'campaign_name', 'volunteer_count', 'created_at'
        ]

    def get_volunteer_count(self, obj):
        return obj.volunteers.count()


class EventDetailSerializer(serializers.ModelSerializer):
    """Detailed event serializer"""
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    constituency_name = serializers.CharField(source='constituency.name', read_only=True)
    volunteers_details = serializers.SerializerMethodField()
    budget_expenses_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_volunteers_details(self, obj):
        """Get volunteer names"""
        return [{'id': u.id, 'name': u.get_full_name() or u.username, 'email': u.email}
                for u in obj.volunteers.all()]

    def get_budget_expenses_percentage(self, obj):
        """Calculate budget spent percentage"""
        if obj.budget > 0:
            return round((float(obj.expenses) / float(obj.budget)) * 100, 2)
        return 0


class EventCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating events"""
    class Meta:
        model = Event
        exclude = ['created_at', 'updated_at']

    def validate(self, data):
        """Validate start datetime is before end datetime"""
        if data.get('start_datetime') and data.get('end_datetime'):
            if data['start_datetime'] >= data['end_datetime']:
                raise serializers.ValidationError("Start datetime must be before end datetime")
        return data

    def create(self, validated_data):
        """Extract volunteers before creating"""
        volunteers = validated_data.pop('volunteers', [])
        event = super().create(validated_data)
        event.volunteers.set(volunteers)
        return event


# ==================== VOLUNTEER SERIALIZERS ====================

class VolunteerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for volunteer listing"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    constituency_name = serializers.CharField(source='assigned_constituency.name', read_only=True)

    class Meta:
        model = VolunteerProfile
        fields = [
            'id', 'volunteer_id', 'user', 'user_name', 'user_email', 'assigned_ward',
            'constituency_name', 'tasks_completed', 'hours_contributed', 'rating',
            'is_active', 'joined_at'
        ]


class VolunteerDetailSerializer(serializers.ModelSerializer):
    """Detailed volunteer serializer"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    constituency_name = serializers.CharField(source='assigned_constituency.name', read_only=True)

    class Meta:
        model = VolunteerProfile
        fields = '__all__'
        read_only_fields = ['id', 'joined_at', 'created_at', 'updated_at']


class VolunteerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating volunteer profiles"""
    class Meta:
        model = VolunteerProfile
        exclude = ['joined_at', 'created_at', 'updated_at']

    def validate_volunteer_id(self, value):
        """Ensure volunteer ID is unique"""
        if VolunteerProfile.objects.filter(volunteer_id=value).exists():
            raise serializers.ValidationError("A volunteer with this ID already exists.")
        return value


# ==================== EXPENSE SERIALIZERS ====================

class ExpenseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for expense listing"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)

    class Meta:
        model = Expense
        fields = [
            'id', 'expense_type', 'amount', 'currency', 'description', 'status',
            'created_by_name', 'approved_by_name', 'campaign_name', 'created_at'
        ]


class ExpenseDetailSerializer(serializers.ModelSerializer):
    """Detailed expense serializer"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.campaign_name', read_only=True)
    event_name = serializers.CharField(source='event.event_name', read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating expenses"""
    class Meta:
        model = Expense
        exclude = ['created_by', 'approved_by', 'paid_at', 'created_at', 'updated_at']

    def create(self, validated_data):
        """Auto-assign created_by"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)
