from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    """Organization model for multi-tenancy support"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    # Subscription
    subscription_status = models.CharField(max_length=20, default='active')
    subscription_tier = models.CharField(max_length=20, default='basic')
    max_users = models.IntegerField(default=10)

    # Settings
    settings = models.JSONField(default=dict, blank=True)

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
