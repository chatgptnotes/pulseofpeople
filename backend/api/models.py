from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Organization(models.Model):
    """Organization model for multi-tenancy support (Political parties, campaigns, NGOs)"""
    ORGANIZATION_TYPES = [
        ('party', 'Political Party'),
        ('campaign', 'Campaign Organization'),
        ('ngo', 'NGO'),
        ('other', 'Other'),
    ]
    SUBSCRIPTION_PLANS = [
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('pro', 'Professional'),
        ('enterprise', 'Enterprise'),
    ]

    # Basic Info
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    logo = models.ImageField(upload_to='org_logos/', blank=True, null=True)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES, default='campaign')

    # Contact Info
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, null=True)
    social_media_links = models.JSONField(default=dict, blank=True, help_text="Social media URLs")

    # Subscription
    subscription_plan = models.CharField(max_length=20, choices=SUBSCRIPTION_PLANS, default='free')
    subscription_status = models.CharField(max_length=20, default='active')
    subscription_expires_at = models.DateTimeField(null=True, blank=True)
    max_users = models.IntegerField(default=10)

    # Settings
    settings = models.JSONField(default=dict, blank=True, help_text="Branding colors, email templates, etc.")
    is_active = models.BooleanField(default=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"


class Permission(models.Model):
    """Granular permissions for RBAC"""
    CATEGORIES = [
        ('users', 'User Management'),
        ('data', 'Data Access'),
        ('analytics', 'Analytics'),
        ('settings', 'Settings'),
        ('system', 'System'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}: {self.name}"

    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('analyst', 'Analyst'),
        ('user', 'User'),
        ('viewer', 'Viewer'),
        ('volunteer', 'Volunteer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    # Organization support
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True
    )

    # Profile fields
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)  # Supabase storage URL
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    # Password management
    must_change_password = models.BooleanField(default=False)

    # Two-Factor Authentication
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)

    # Location assignments for political roles
    # Admin1 (State level) - sees entire state
    assigned_state = models.ForeignKey(
        'api.State',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin1_users'
    )
    # Admin2 (District level) - sees their district
    assigned_district = models.ForeignKey(
        'api.District',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin2_users'
    )
    # City and Constituency - free-text fields for user location
    city = models.CharField(max_length=100, blank=True, null=True)
    constituency = models.CharField(max_length=200, blank=True, null=True)
    # Admin3 (Booth level) - managed via BoothAgent model

    # Custom permissions
    custom_permissions = models.ManyToManyField(
        Permission,
        through='UserPermission',
        related_name='users',
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_superadmin(self):
        return self.role == 'superadmin'

    def is_admin(self):
        return self.role == 'admin'

    def is_manager(self):
        return self.role == 'manager'

    def is_user(self):
        return self.role == 'user'

    def is_admin_or_above(self):
        return self.role in ['admin', 'superadmin', 'manager']

    def has_permission(self, permission_name):
        """Check if user has a specific permission"""
        # Superadmin has all permissions
        if self.is_superadmin():
            return True

        # Check role-based permissions
        role_has_perm = RolePermission.objects.filter(
            role=self.role,
            permission__name=permission_name
        ).exists()

        if role_has_perm:
            return True

        # Check user-specific permissions
        user_perm = UserPermission.objects.filter(
            user_profile=self,
            permission__name=permission_name,
            granted=True
        ).exists()

        return user_perm

    def get_permissions(self):
        """Get all permissions for this user"""
        if self.is_superadmin():
            return list(Permission.objects.all().values_list('name', flat=True))

        # Get role permissions
        role_perms = Permission.objects.filter(
            role_permissions__role=self.role
        ).values_list('name', flat=True)

        # Get user-specific permissions
        user_perms = Permission.objects.filter(
            user_permissions__user_profile=self,
            user_permissions__granted=True
        ).values_list('name', flat=True)

        # Combine and remove duplicates
        all_perms = set(list(role_perms) + list(user_perms))
        return list(all_perms)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"


class RolePermission(models.Model):
    """Maps roles to permissions"""
    role = models.CharField(max_length=20, choices=UserProfile.ROLE_CHOICES)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')

    class Meta:
        unique_together = ['role', 'permission']
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"

    def __str__(self):
        return f"{self.role} -> {self.permission.name}"


class UserPermission(models.Model):
    """User-specific permission overrides"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='user_permissions')
    granted = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user_profile', 'permission']
        verbose_name = "User Permission"
        verbose_name_plural = "User Permissions"

    def __str__(self):
        status = "Granted" if self.granted else "Revoked"
        return f"{self.user_profile.user.username} - {self.permission.name} ({status})"


class AuditLog(models.Model):
    """Audit log for tracking all user actions"""
    ACTION_TYPES = [
        ('create', 'Create'),
        ('read', 'Read'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('permission_change', 'Permission Change'),
        ('role_change', 'Role Change'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    target_model = models.CharField(max_length=100, blank=True)
    target_id = models.CharField(max_length=100, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action']),
            models.Index(fields=['target_model', 'target_id']),
        ]
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"{user_str} - {self.action} - {self.timestamp}"


class Notification(models.Model):
    """
    Notification model for real-time user notifications
    Syncs with Supabase for real-time delivery
    """
    TYPE_CHOICES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('task', 'Task'),
        ('user', 'User'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Link to related object (optional)
    related_model = models.CharField(max_length=100, blank=True)
    related_id = models.CharField(max_length=100, blank=True)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Supabase sync
    supabase_id = models.UUIDField(null=True, blank=True, unique=True)
    synced_to_supabase = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_read']),
            models.Index(fields=['notification_type']),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()


class Task(models.Model):
    """Sample Task model for demonstration"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    due_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-created_at']


class UploadedFile(models.Model):
    """
    Uploaded File model for tracking files stored in Supabase Storage
    Stores metadata while actual files are in Supabase Storage buckets
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')

    # File information
    filename = models.CharField(max_length=255, help_text="Stored filename")
    original_filename = models.CharField(max_length=255, help_text="Original uploaded filename")
    file_size = models.BigIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)

    # Storage information
    storage_path = models.CharField(max_length=500, help_text="Path in Supabase Storage")
    storage_url = models.URLField(max_length=500, help_text="Public URL from Supabase")
    bucket_id = models.CharField(max_length=100, default='user-files')

    # File categorization
    file_category = models.CharField(
        max_length=50,
        choices=[
            ('document', 'Document'),
            ('image', 'Image'),
            ('video', 'Video'),
            ('audio', 'Audio'),
            ('archive', 'Archive'),
            ('other', 'Other'),
        ],
        default='document'
    )

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional file metadata")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['file_category']),
            models.Index(fields=['mime_type']),
        ]
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"

    def __str__(self):
        return f"{self.user.username} - {self.original_filename}"

    def get_file_extension(self):
        """Get file extension from original filename"""
        import os
        return os.path.splitext(self.original_filename)[1].lower()

    def is_image(self):
        """Check if file is an image"""
        return self.mime_type.startswith('image/')

    def is_video(self):
        """Check if file is a video"""
        return self.mime_type.startswith('video/')

    def is_audio(self):
        """Check if file is audio"""
        return self.mime_type.startswith('audio/')

    def is_document(self):
        """Check if file is a document"""
        doc_types = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument']
        return any(self.mime_type.startswith(dtype) for dtype in doc_types)

    def get_human_readable_size(self):
        """Convert file size to human readable format"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"


# =====================================================
# POLITICAL PLATFORM MODELS - TVK PARTY
# =====================================================

from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class State(models.Model):
    """States in India"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    capital = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=50, blank=True)
    total_districts = models.IntegerField(default=0)
    total_constituencies = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "State"
        verbose_name_plural = "States"

    def __str__(self):
        return self.name


class District(models.Model):
    """Districts within states"""
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    headquarters = models.CharField(max_length=100, blank=True)
    population = models.IntegerField(null=True, blank=True)
    area_sq_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_wards = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['state', 'name']
        unique_together = ['state', 'name']
        verbose_name = "District"
        verbose_name_plural = "Districts"
        indexes = [
            models.Index(fields=['state', 'name']),
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f"{self.name}, {self.state.code}"


class Constituency(models.Model):
    """Electoral constituencies"""
    CONSTITUENCY_TYPES = [
        ('assembly', 'Assembly'),
        ('parliamentary', 'Parliamentary'),
    ]
    RESERVATION_TYPES = [
        ('general', 'General'),
        ('sc', 'Scheduled Castes'),
        ('st', 'Scheduled Tribes'),
    ]

    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='constituencies')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='constituencies')
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    constituency_type = models.CharField(max_length=20, choices=CONSTITUENCY_TYPES, default='assembly')
    number = models.IntegerField(help_text="Constituency number")
    reserved_for = models.CharField(max_length=20, choices=RESERVATION_TYPES, default='general')
    total_voters = models.IntegerField(null=True, blank=True)
    total_wards = models.IntegerField(default=0)
    total_booths = models.IntegerField(default=0)
    area_sq_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    center_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    center_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    geojson_data = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['state', 'constituency_type', 'number']
        unique_together = ['state', 'code']
        verbose_name = "Constituency"
        verbose_name_plural = "Constituencies"
        indexes = [
            models.Index(fields=['state', 'constituency_type']),
            models.Index(fields=['code']),
            models.Index(fields=['district']),
        ]

    def __str__(self):
        return f"{self.name} ({self.number})"


class PollingBooth(models.Model):
    """Polling Booths/Stations within constituencies"""
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='polling_booths')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='polling_booths')
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='polling_booths')

    booth_number = models.CharField(max_length=20, help_text="Official booth number (e.g., '001', '002A')")
    name = models.CharField(max_length=300, help_text="Polling booth name/location")
    building_name = models.CharField(max_length=200, blank=True, help_text="School/building name")

    # Location details
    address = models.TextField(blank=True)
    area = models.CharField(max_length=200, blank=True, help_text="Locality/area name")
    landmark = models.CharField(max_length=200, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    # Geographic coordinates (optional)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    # Statistics
    total_voters = models.IntegerField(default=0, help_text="Total registered voters")
    male_voters = models.IntegerField(default=0)
    female_voters = models.IntegerField(default=0)
    other_voters = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)
    is_accessible = models.BooleanField(default=True, help_text="Wheelchair accessible")

    # Metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional booth information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['constituency', 'booth_number']
        unique_together = ['constituency', 'booth_number']
        verbose_name = "Polling Booth"
        verbose_name_plural = "Polling Booths"
        indexes = [
            models.Index(fields=['state', 'district']),
            models.Index(fields=['constituency']),
            models.Index(fields=['booth_number']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"Booth {self.booth_number} - {self.name}"


class PoliticalParty(models.Model):
    """Political parties"""
    PARTY_STATUS = [
        ('national', 'National Party'),
        ('state', 'State Party'),
        ('regional', 'Regional Party'),
    ]
    name = models.CharField(max_length=200, unique=True)
    short_name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=100, blank=True)
    symbol_image = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=PARTY_STATUS, default='state')
    headquarters = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True, null=True)
    founded_date = models.DateField(null=True, blank=True)
    active_states = models.ManyToManyField(State, related_name='political_parties', blank=True)
    ideology = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Political Party"
        verbose_name_plural = "Political Parties"

    def __str__(self):
        return f"{self.short_name} - {self.name}"


class IssueCategory(models.Model):
    """Issue categories based on TVK priorities"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    color = models.CharField(max_length=7, default='#3B82F6')
    icon = models.CharField(max_length=50, blank=True)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = "Issue Category"
        verbose_name_plural = "Issue Categories"

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class VoterSegment(models.Model):
    """Voter segments (Fishermen, Farmers, Youth, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    estimated_population = models.IntegerField(null=True, blank=True)
    priority_level = models.IntegerField(default=0)
    key_issues = models.ManyToManyField(IssueCategory, related_name='relevant_segments', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-priority_level', 'name']
        verbose_name = "Voter Segment"
        verbose_name_plural = "Voter Segments"

    def __str__(self):
        return self.name


class DirectFeedback(models.Model):
    """Direct citizen feedback submissions"""
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('analyzing', 'AI Analyzing'),
        ('analyzed', 'Analyzed'),
        ('reviewed', 'Reviewed'),
        ('escalated', 'Escalated'),
        ('resolved', 'Resolved'),
    ]
    URGENCY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    feedback_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    citizen_name = models.CharField(max_length=200)
    citizen_age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(18), MaxValueValidator(120)])
    citizen_phone = models.CharField(max_length=20, blank=True)
    citizen_email = models.EmailField(blank=True, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='feedback')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='feedback')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback')
    ward = models.CharField(max_length=100, blank=True)
    booth_number = models.CharField(max_length=20, blank=True)
    detailed_location = models.TextField(blank=True)
    issue_category = models.ForeignKey(IssueCategory, on_delete=models.SET_NULL, null=True, related_name='feedback')
    message_text = models.TextField()
    expectations = models.TextField(blank=True)
    voter_segment = models.ForeignKey(VoterSegment, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedback')
    audio_file_url = models.URLField(blank=True, null=True, max_length=500)
    video_file_url = models.URLField(blank=True, null=True, max_length=500)
    image_urls = models.JSONField(default=list, blank=True)
    transcription = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    ai_sentiment_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    ai_sentiment_polarity = models.CharField(max_length=20, blank=True, choices=[('positive', 'Positive'), ('negative', 'Negative'), ('neutral', 'Neutral')])
    ai_extracted_issues = models.JSONField(default=list, blank=True)
    ai_urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, blank=True, null=True)
    ai_confidence = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    ai_analysis_metadata = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_feedback')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_feedback')
    review_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    analyzed_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    supabase_id = models.UUIDField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Direct Feedback"
        verbose_name_plural = "Direct Feedback"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['ward']),
            models.Index(fields=['constituency']),
            models.Index(fields=['-submitted_at']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['issue_category']),
            models.Index(fields=['voter_segment']),
        ]

    def __str__(self):
        return f"{self.citizen_name} - {self.ward} ({self.submitted_at.strftime('%Y-%m-%d')})"


class FieldReport(models.Model):
    """Ground-level reports from party workers"""
    REPORT_TYPES = [
        ('daily_summary', 'Daily Summary'),
        ('event_feedback', 'Event Feedback'),
        ('issue_report', 'Issue Report'),
        ('competitor_activity', 'Competitor Activity'),
        ('booth_report', 'Booth Report'),
    ]
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('disputed', 'Disputed'),
    ]
    report_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    volunteer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='field_reports')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='field_reports')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='field_reports')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='field_reports')
    ward = models.CharField(max_length=100)
    booth_number = models.CharField(max_length=20, blank=True)
    location_lat = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    address = models.TextField(blank=True)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    title = models.CharField(max_length=200, blank=True)
    positive_reactions = models.JSONField(default=list, blank=True)
    negative_reactions = models.JSONField(default=list, blank=True)
    key_issues = models.ManyToManyField(IssueCategory, related_name='field_reports', blank=True)
    voter_segments_met = models.ManyToManyField(VoterSegment, related_name='field_reports', blank=True)
    crowd_size = models.IntegerField(null=True, blank=True)
    quotes = models.JSONField(default=list, blank=True)
    notes = models.TextField(blank=True)
    competitor_party = models.ForeignKey(PoliticalParty, on_delete=models.SET_NULL, null=True, blank=True, related_name='competitor_reports')
    competitor_activity_description = models.TextField(blank=True)
    media_urls = models.JSONField(default=list, blank=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_reports')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)
    report_date = models.DateField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    supabase_id = models.UUIDField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Field Report"
        verbose_name_plural = "Field Reports"
        indexes = [
            models.Index(fields=['volunteer', '-timestamp']),
            models.Index(fields=['ward']),
            models.Index(fields=['booth_number']),
            models.Index(fields=['constituency']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['report_type']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['report_date']),
        ]

    def __str__(self):
        return f"{self.get_report_type_display()} - {self.ward} ({self.report_date})"


class SentimentData(models.Model):
    """Core sentiment analysis data"""
    POLARITY_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]
    SOURCE_CHOICES = [
        ('direct_feedback', 'Direct Feedback'),
        ('field_report', 'Field Report'),
        ('social_media', 'Social Media'),
        ('survey', 'Survey'),
    ]
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    source_id = models.UUIDField()
    issue = models.ForeignKey(IssueCategory, on_delete=models.CASCADE, related_name='sentiment_data')
    sentiment_score = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    polarity = models.CharField(max_length=20, choices=POLARITY_CHOICES)
    confidence = models.DecimalField(max_digits=4, decimal_places=2, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='sentiment_data')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='sentiment_data')
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='sentiment_data')
    ward = models.CharField(max_length=100, blank=True)
    voter_segment = models.ForeignKey(VoterSegment, on_delete=models.SET_NULL, null=True, blank=True, related_name='sentiment_data')
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    supabase_id = models.UUIDField(null=True, blank=True, unique=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Sentiment Data"
        verbose_name_plural = "Sentiment Data"
        indexes = [
            models.Index(fields=['issue', '-timestamp']),
            models.Index(fields=['polarity']),
            models.Index(fields=['constituency', '-timestamp']),
            models.Index(fields=['district', '-timestamp']),
            models.Index(fields=['ward']),
            models.Index(fields=['-timestamp']),
            models.Index(fields=['voter_segment']),
        ]

    def __str__(self):
        return f"{self.issue.name} - {self.polarity} ({self.sentiment_score})"


class BoothAgent(models.Model):
    """Extended profile for Admin3 (Booth-level party workers)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='booth_agent_profile')
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='booth_agents')
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='booth_agents')
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='booth_agents')
    assigned_wards = models.JSONField(default=list)
    assigned_booths = models.JSONField(default=list)
    focus_segments = models.ManyToManyField(VoterSegment, related_name='assigned_agents', blank=True)
    total_reports = models.IntegerField(default=0)
    total_feedback_collected = models.IntegerField(default=0)
    last_report_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    joined_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booth Agent"
        verbose_name_plural = "Booth Agents"
        indexes = [
            models.Index(fields=['constituency']),
            models.Index(fields=['district']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.constituency.name}"


# =====================================================
# BULK USER IMPORT MODELS
# =====================================================


class BulkUploadJob(models.Model):
    """Track bulk user upload jobs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('validating', 'Validating'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    job_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_upload_jobs')
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_rows = models.IntegerField(default=0)
    processed_rows = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)

    validation_errors = models.JSONField(default=list)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bulk Upload Job"
        verbose_name_plural = "Bulk Upload Jobs"
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['job_id']),
        ]

    def __str__(self):
        return f"Bulk Upload {self.job_id} - {self.status}"

    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.total_rows == 0:
            return 0
        return int((self.processed_rows / self.total_rows) * 100)


class BulkUploadError(models.Model):
    """Track errors for individual rows in bulk upload"""
    job = models.ForeignKey(BulkUploadJob, on_delete=models.CASCADE, related_name='errors')
    row_number = models.IntegerField()
    row_data = models.JSONField()
    error_message = models.TextField()
    error_field = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['row_number']
        verbose_name = "Bulk Upload Error"
        verbose_name_plural = "Bulk Upload Errors"
        indexes = [
            models.Index(fields=['job', 'row_number']),
        ]

    def __str__(self):
        return f"Row {self.row_number} - {self.error_field}: {self.error_message[:50]}"


# =====================================================
# TWO-FACTOR AUTHENTICATION MODELS
# =====================================================


class TwoFactorBackupCode(models.Model):
    """Backup codes for 2FA recovery"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='twofactor_backup_codes')
    code_hash = models.CharField(max_length=255, help_text="Hashed backup code")
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "2FA Backup Code"
        verbose_name_plural = "2FA Backup Codes"
        indexes = [
            models.Index(fields=['user', 'is_used']),
        ]

    def __str__(self):
        status = 'Used' if self.is_used else 'Active'
        return f'{self.user.username} - Backup Code ({status})'


# =====================================================
# CORE POLITICAL PLATFORM MODELS - WORKSTREAM 2
# =====================================================


class Voter(models.Model):
    """
    Voter database - core voter information and engagement tracking
    """
    PARTY_CHOICES = [
        ('bjp', 'BJP'),
        ('congress', 'Congress'),
        ('aap', 'AAP'),
        ('tvk', 'TVK'),
        ('dmk', 'DMK'),
        ('aiadmk', 'AIADMK'),
        ('neutral', 'Neutral'),
        ('unknown', 'Unknown'),
        ('other', 'Other'),
    ]
    SENTIMENT_CHOICES = [
        ('strong_supporter', 'Strong Supporter'),
        ('supporter', 'Supporter'),
        ('neutral', 'Neutral'),
        ('opposition', 'Opposition'),
        ('strong_opposition', 'Strong Opposition'),
    ]
    INFLUENCE_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    COMMUNICATION_CHOICES = [
        ('phone', 'Phone Call'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('door_to_door', 'Door to Door'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    # Identity
    voter_id = models.CharField(max_length=50, unique=True, db_index=True, help_text="Official voter ID")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(18), MaxValueValidator(120)])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    alternate_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, null=True)
    photo = models.ImageField(upload_to='voter_photos/', blank=True, null=True)

    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    ward = models.CharField(max_length=100, blank=True, db_index=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, related_name='voters')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, related_name='voters')
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, related_name='voters')
    pincode = models.CharField(max_length=10, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)

    # Political Data
    party_affiliation = models.CharField(max_length=20, choices=PARTY_CHOICES, default='unknown')
    voting_history = models.JSONField(default=list, blank=True, help_text="Last 5 elections voting history")
    sentiment = models.CharField(max_length=30, choices=SENTIMENT_CHOICES, default='neutral')
    influence_level = models.CharField(max_length=20, choices=INFLUENCE_CHOICES, default='low')
    is_opinion_leader = models.BooleanField(default=False)

    # Engagement
    last_contacted_at = models.DateTimeField(null=True, blank=True)
    contact_frequency = models.IntegerField(default=0, help_text="Number of times contacted")
    interaction_count = models.IntegerField(default=0)
    positive_interactions = models.IntegerField(default=0)
    negative_interactions = models.IntegerField(default=0)
    preferred_communication = models.CharField(max_length=20, choices=COMMUNICATION_CHOICES, default='phone')

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_voters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    tags = models.JSONField(default=list, blank=True, help_text="Tags for categorization")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Voter"
        verbose_name_plural = "Voters"
        indexes = [
            models.Index(fields=['voter_id']),
            models.Index(fields=['constituency', 'ward']),
            models.Index(fields=['party_affiliation']),
            models.Index(fields=['sentiment']),
            models.Index(fields=['phone']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.voter_id})"


class VoterInteraction(models.Model):
    """
    Track all interactions with voters
    """
    INTERACTION_TYPES = [
        ('phone_call', 'Phone Call'),
        ('door_visit', 'Door to Door Visit'),
        ('event_meeting', 'Event Meeting'),
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
    ]
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    voter = models.ForeignKey(Voter, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    contacted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='voter_interactions')
    interaction_date = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")
    sentiment = models.CharField(max_length=10, choices=SENTIMENT_CHOICES, default='neutral')
    issues_discussed = models.JSONField(default=list, blank=True)
    promises_made = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-interaction_date']
        verbose_name = "Voter Interaction"
        verbose_name_plural = "Voter Interactions"
        indexes = [
            models.Index(fields=['voter', '-interaction_date']),
            models.Index(fields=['contacted_by']),
            models.Index(fields=['interaction_type']),
            models.Index(fields=['sentiment']),
            models.Index(fields=['follow_up_required']),
        ]

    def __str__(self):
        return f"{self.voter.first_name} - {self.get_interaction_type_display()} ({self.interaction_date.date()})"


class Campaign(models.Model):
    """
    Campaign management - elections, awareness, door-to-door campaigns
    """
    CAMPAIGN_TYPES = [
        ('election', 'Election Campaign'),
        ('awareness', 'Awareness Campaign'),
        ('issue_based', 'Issue-based Campaign'),
        ('door_to_door', 'Door to Door Campaign'),
    ]
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    campaign_name = models.CharField(max_length=200)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True, related_name='campaigns')
    target_audience = models.TextField(blank=True, help_text="Description of target audience")
    campaign_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_campaigns')
    team_members = models.ManyToManyField(User, related_name='campaigns', blank=True)
    goals = models.JSONField(default=dict, blank=True, help_text="Campaign goals and objectives")
    metrics = models.JSONField(default=dict, blank=True, help_text="Reach, engagement, conversion metrics")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_campaigns')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = "Campaign"
        verbose_name_plural = "Campaigns"
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['campaign_type']),
            models.Index(fields=['start_date']),
            models.Index(fields=['campaign_manager']),
        ]

    def __str__(self):
        return f"{self.campaign_name} ({self.get_status_display()})"


class SocialMediaPost(models.Model):
    """
    Social media post tracking and engagement
    """
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('whatsapp', 'WhatsApp'),
        ('youtube', 'YouTube'),
    ]

    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    post_content = models.TextField()
    post_url = models.URLField(blank=True)
    post_id = models.CharField(max_length=200, blank=True, help_text="Platform-specific post ID")
    posted_at = models.DateTimeField()
    scheduled_at = models.DateTimeField(null=True, blank=True)
    reach = models.IntegerField(default=0)
    impressions = models.IntegerField(default=0)
    engagement_count = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    sentiment_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='social_posts')
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='social_posts')
    is_published = models.BooleanField(default=False)
    is_promoted = models.BooleanField(default=False)
    hashtags = models.JSONField(default=list, blank=True)
    mentions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-posted_at']
        verbose_name = "Social Media Post"
        verbose_name_plural = "Social Media Posts"
        indexes = [
            models.Index(fields=['platform', '-posted_at']),
            models.Index(fields=['campaign']),
            models.Index(fields=['is_published']),
            models.Index(fields=['-posted_at']),
        ]

    def __str__(self):
        return f"{self.get_platform_display()} - {self.post_content[:50]}"


class Alert(models.Model):
    """
    Alert/Notification system for critical updates
    """
    ALERT_TYPES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('urgent', 'Urgent'),
        ('critical', 'Critical'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='info')
    title = models.CharField(max_length=200)
    message = models.TextField()
    target_role = models.CharField(max_length=20, choices=UserProfile.ROLE_CHOICES, blank=True, help_text="Send to specific role")
    target_users = models.ManyToManyField(User, related_name='alerts', blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    action_url = models.URLField(blank=True)
    action_required = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_alerts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
        indexes = [
            models.Index(fields=['target_role']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_alert_type_display()}: {self.title}"


class Event(models.Model):
    """
    Event management - rallies, meetings, door-to-door events
    """
    EVENT_TYPES = [
        ('rally', 'Rally'),
        ('meeting', 'Meeting'),
        ('door_to_door', 'Door to Door'),
        ('booth_visit', 'Booth Visit'),
        ('town_hall', 'Town Hall'),
    ]
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    event_name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.CharField(max_length=300)
    ward = models.CharField(max_length=100, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    expected_attendance = models.IntegerField(default=0)
    actual_attendance = models.IntegerField(default=0)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='organized_events')
    volunteers = models.ManyToManyField(User, related_name='volunteer_events', blank=True)
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    notes = models.TextField(blank=True)
    photos = models.JSONField(default=list, blank=True, help_text="URLs to event photos")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_datetime']
        verbose_name = "Event"
        verbose_name_plural = "Events"
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['status']),
            models.Index(fields=['start_datetime']),
            models.Index(fields=['constituency']),
        ]

    def __str__(self):
        return f"{self.event_name} - {self.start_datetime.date()}"


class VolunteerProfile(models.Model):
    """
    Extended volunteer profile with skills and assignments
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='volunteer_profile')
    volunteer_id = models.CharField(max_length=50, unique=True, db_index=True)
    skills = models.JSONField(default=list, blank=True, help_text="List of volunteer skills")
    availability = models.JSONField(default=dict, blank=True, help_text="Days and times available")
    assigned_ward = models.CharField(max_length=100, blank=True)
    assigned_constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True, related_name='volunteers')
    tasks_completed = models.IntegerField(default=0)
    hours_contributed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    is_active = models.BooleanField(default=True)
    joined_at = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Volunteer Profile"
        verbose_name_plural = "Volunteer Profiles"
        indexes = [
            models.Index(fields=['volunteer_id']),
            models.Index(fields=['assigned_constituency']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.volunteer_id})"


class Expense(models.Model):
    """
    Expense tracking for campaigns and events
    """
    EXPENSE_TYPES = [
        ('travel', 'Travel'),
        ('materials', 'Campaign Materials'),
        ('advertising', 'Advertising'),
        ('event', 'Event Expenses'),
        ('salary', 'Salary/Honorarium'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
    ]

    expense_type = models.CharField(max_length=20, choices=EXPENSE_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    description = models.TextField()
    campaign = models.ForeignKey(Campaign, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='expense_items')
    receipt_image = models.ImageField(upload_to='receipts/', blank=True, null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_expenses')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Expense"
        verbose_name_plural = "Expenses"
        indexes = [
            models.Index(fields=['expense_type']),
            models.Index(fields=['status']),
            models.Index(fields=['campaign']),
            models.Index(fields=['event']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_expense_type_display()} - {self.amount} {self.currency}"


# =============================================================================
# WHATSAPP AI CHATBOT MODELS
# =============================================================================

class WhatsAppConversation(models.Model):
    """WhatsApp conversation tracking with AI-powered analysis"""

    LANGUAGE_CHOICES = [
        ('ta', 'Tamil'),
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('te', 'Telugu'),
    ]

    CHANNEL_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('web', 'Web'),
        ('telegram', 'Telegram'),
    ]

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]

    CATEGORY_CHOICES = [
        ('feedback', 'Feedback'),
        ('complaint', 'Complaint'),
        ('suggestion', 'Suggestion'),
        ('inquiry', 'Inquiry'),
        ('political', 'Political'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    POLITICAL_LEAN_CHOICES = [
        ('left', 'Left'),
        ('center', 'Center'),
        ('right', 'Right'),
        ('neutral', 'Neutral'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, db_index=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    user_location = models.CharField(max_length=255, blank=True, null=True)

    # Conversation metadata
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    duration_seconds = models.IntegerField(default=0)
    message_count = models.IntegerField(default=0)

    # Language and channel
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='ta')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='whatsapp')

    # Sentiment analysis
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    sentiment_score = models.FloatField(default=0.0)  # -1 to 1

    # Classification
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='inquiry')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Topics and keywords (JSON fields)
    topics = models.JSONField(default=list, blank=True)
    keywords = models.JSONField(default=list, blank=True)
    issues = models.JSONField(default=list, blank=True)

    # User demographics
    demographics = models.JSONField(default=dict, blank=True)
    political_lean = models.CharField(max_length=20, choices=POLITICAL_LEAN_CHOICES, blank=True, null=True)

    # AI processing
    ai_confidence = models.FloatField(default=0.0)
    satisfaction_score = models.IntegerField(default=0)
    resolved = models.BooleanField(default=False)
    human_handoff = models.BooleanField(default=False)

    # Tracking
    session_id = models.UUIDField(default=uuid.uuid4)
    source_campaign = models.CharField(max_length=100, blank=True, null=True)
    referral_code = models.CharField(max_length=50, blank=True, null=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'whatsapp_conversations'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['-started_at']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['sentiment']),
            models.Index(fields=['category']),
            models.Index(fields=['resolved']),
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"

    def calculate_duration(self):
        """Calculate conversation duration"""
        if self.ended_at:
            self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
            self.save(update_fields=['duration_seconds'])


class WhatsAppMessage(models.Model):
    """Individual messages within WhatsApp conversations"""

    SENDER_CHOICES = [
        ('user', 'User'),
        ('bot', 'Bot'),
        ('human', 'Human Agent'),
    ]

    TYPE_CHOICES = [
        ('text', 'Text'),
        ('voice', 'Voice'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('location', 'Location'),
    ]

    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        WhatsAppConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    # Message details
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    content = models.TextField()
    media_url = models.URLField(blank=True, null=True)

    # WhatsApp metadata
    whatsapp_message_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)

    # AI processing
    intent = models.CharField(max_length=100, blank=True, null=True)
    confidence = models.FloatField(default=0.0)
    sentiment = models.CharField(max_length=20, blank=True, null=True)
    entities = models.JSONField(default=dict, blank=True)
    language = models.CharField(max_length=5, blank=True, null=True)

    # Processing status
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)

    # Response metadata
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    model_used = models.CharField(max_length=50, blank=True, null=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'whatsapp_messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation', 'timestamp']),
            models.Index(fields=['whatsapp_message_id']),
            models.Index(fields=['processed']),
        ]

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}"


class VoterProfile(models.Model):
    """Aggregated voter profile from WhatsApp interactions"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)

    # Basic info
    name = models.CharField(max_length=255, blank=True, null=True)
    preferred_language = models.CharField(max_length=5, default='ta')

    # Location data
    location_data = models.JSONField(default=dict, blank=True)

    # Demographics
    demographics = models.JSONField(default=dict, blank=True)
    political_lean = models.CharField(max_length=20, blank=True, null=True)

    # Engagement metrics
    interaction_count = models.IntegerField(default=0)
    total_messages_sent = models.IntegerField(default=0)
    avg_sentiment_score = models.FloatField(default=0.0)
    last_contacted = models.DateTimeField(blank=True, null=True)
    first_contacted = models.DateTimeField(auto_now_add=True)

    # Topics of interest
    topic_interests = models.JSONField(default=dict, blank=True)
    issues_raised = models.JSONField(default=list, blank=True)

    # Sentiment history
    sentiment_history = models.JSONField(default=list, blank=True)

    # Referral tracking
    referral_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    referrals_made = models.IntegerField(default=0)
    referred_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'voter_profiles'
        ordering = ['-last_contacted']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['referral_code']),
            models.Index(fields=['-last_contacted']),
        ]

    def __str__(self):
        return f"{self.name or self.phone_number} - {self.interaction_count} interactions"

    def generate_referral_code(self):
        """Generate unique referral code"""
        if not self.referral_code:
            import hashlib
            hash_input = f"{self.phone_number}{self.id}"
            self.referral_code = hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()
            self.save(update_fields=['referral_code'])
        return self.referral_code


class BotConfiguration(models.Model):
    """Bot personality and behavior configuration"""

    PERSONALITY_CHOICES = [
        ('formal', 'Formal'),
        ('friendly', 'Friendly'),
        ('professional', 'Professional'),
        ('casual', 'Casual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()

    # Configuration
    personality = models.CharField(max_length=20, choices=PERSONALITY_CHOICES, default='friendly')
    languages = models.JSONField(default=list)
    channels = models.JSONField(default=list)

    # AI settings
    ai_model = models.CharField(max_length=50, default='gpt-4')
    system_prompt = models.TextField()
    custom_prompts = models.JSONField(default=dict, blank=True)
    knowledge_base = models.JSONField(default=list, blank=True)

    # Behavior settings
    response_time_target = models.FloatField(default=1.0)
    max_conversation_length = models.IntegerField(default=50)
    auto_handoff_threshold = models.FloatField(default=0.3)

    # Status
    active = models.BooleanField(default=True)

    # Metrics
    total_conversations = models.IntegerField(default=0)
    accuracy_rate = models.FloatField(default=0.0)
    satisfaction_rate = models.FloatField(default=0.0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bot_configurations'
        ordering = ['name']

    def __str__(self):
        return self.name


# =====================================================
# NEWS ARTICLE MODEL - Web Scraping & Sentiment Analysis
# =====================================================

class NewsArticle(models.Model):
    """
    Stores scraped news articles from Tamil Nadu news sources
    with LLM-powered sentiment analysis for TVK/Vijay mentions.

    Scraping Sources:
    - Tamil: Dinamalar, Dinakaran, Maalaimalar
    - English: The Hindu TN, Times of India Chennai, Indian Express TN

    Scheduled: Every 6 hours (12 AM, 6 AM, 12 PM, 6 PM IST)
    """

    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]

    LANGUAGE_CHOICES = [
        ('ta', 'Tamil'),
        ('en', 'English'),
        ('hi', 'Hindi'),
    ]

    CATEGORY_CHOICES = [
        ('politics', 'Politics'),
        ('election', 'Election'),
        ('policy', 'Policy'),
        ('governance', 'Governance'),
        ('social_issue', 'Social Issue'),
        ('economy', 'Economy'),
        ('other', 'Other'),
    ]

    # Primary Key
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Article Metadata
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000, unique=True, db_index=True)
    source = models.CharField(max_length=200)  # "Dinamalar", "The Hindu", etc.
    author = models.CharField(max_length=200, null=True, blank=True)
    published_at = models.DateTimeField(db_index=True)
    scraped_at = models.DateTimeField(auto_now_add=True)

    # Article Content
    article_text = models.TextField()
    excerpt = models.TextField(max_length=500, null=True, blank=True)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    word_count = models.IntegerField(default=0)

    # TVK/Vijay Sentiment Analysis (LLM-powered)
    tvk_sentiment = models.CharField(
        max_length=20,
        choices=SENTIMENT_CHOICES,
        default='neutral',
        db_index=True
    )
    tvk_sentiment_score = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.50,
        help_text="0.00 (very negative) to 1.00 (very positive)"
    )
    vijay_mentions = models.IntegerField(default=0)
    tvk_mentions = models.IntegerField(default=0)
    dmk_mentions = models.IntegerField(default=0)
    opposition_mentions = models.IntegerField(default=0)

    # AI Analysis Results
    ai_summary = models.TextField(null=True, blank=True)
    key_topics = models.JSONField(
        default=list,
        blank=True,
        help_text="['jobs', 'neet', 'water_crisis']"
    )
    sentiment_reasoning = models.TextField(
        null=True,
        blank=True,
        help_text="LLM explanation for sentiment classification"
    )
    entities_mentioned = models.JSONField(
        default=list,
        blank=True,
        help_text="['Vijay', 'Stalin', 'BJP', 'Chennai']"
    )

    # Categorization
    is_relevant = models.BooleanField(
        default=True,
        help_text="Is this article relevant to TN politics/TVK?"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='politics'
    )

    # Processing Status
    ai_processed = models.BooleanField(default=False)
    processing_error = models.TextField(null=True, blank=True)
    processing_attempts = models.IntegerField(default=0)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'news_articles'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at']),
            models.Index(fields=['source', '-published_at']),
            models.Index(fields=['tvk_sentiment', '-published_at']),
            models.Index(fields=['language', '-published_at']),
        ]
        verbose_name = 'News Article'
        verbose_name_plural = 'News Articles'

    def __str__(self):
        return f"{self.source} - {self.title[:50]}"

    def save(self, *args, **kwargs):
        # Calculate word count if not set
        if not self.word_count and self.article_text:
            self.word_count = len(self.article_text.split())

        # Auto-generate excerpt if not set
        if not self.excerpt and self.article_text:
            self.excerpt = self.article_text[:500]

        super().save(*args, **kwargs)
