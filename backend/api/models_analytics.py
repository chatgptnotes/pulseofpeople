"""
Analytics and Aggregation Models for Pulse of People Platform
Optimized for fast analytics queries and reporting
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class DailyVoterStats(models.Model):
    """Aggregated daily voter statistics for faster queries"""
    date = models.DateField()

    # Geographic filters
    state = models.ForeignKey('api.State', on_delete=models.CASCADE, null=True, blank=True, related_name='daily_stats')
    district = models.ForeignKey('api.District', on_delete=models.CASCADE, null=True, blank=True, related_name='daily_stats')
    constituency = models.ForeignKey('api.Constituency', on_delete=models.CASCADE, null=True, blank=True, related_name='daily_stats')

    # Totals
    total_voters = models.IntegerField(default=0)
    new_voters = models.IntegerField(default=0)

    # Sentiment breakdown
    strong_supporters = models.IntegerField(default=0)
    supporters = models.IntegerField(default=0)
    neutral = models.IntegerField(default=0)
    opposition = models.IntegerField(default=0)
    strong_opposition = models.IntegerField(default=0)

    # Demographics
    male_voters = models.IntegerField(default=0)
    female_voters = models.IntegerField(default=0)
    other_voters = models.IntegerField(default=0)

    # Age groups
    age_18_25 = models.IntegerField(default=0)
    age_26_35 = models.IntegerField(default=0)
    age_36_45 = models.IntegerField(default=0)
    age_46_60 = models.IntegerField(default=0)
    age_60_plus = models.IntegerField(default=0)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['date', 'state', 'district', 'constituency']
        indexes = [
            models.Index(fields=['date', 'state']),
            models.Index(fields=['date', 'district']),
            models.Index(fields=['date', 'constituency']),
            models.Index(fields=['-date']),
        ]
        verbose_name = "Daily Voter Stats"
        verbose_name_plural = "Daily Voter Stats"

    def __str__(self):
        location = self.constituency or self.district or self.state or "All"
        return f"{self.date} - {location}"


class DailyInteractionStats(models.Model):
    """Aggregated daily interaction statistics"""
    date = models.DateField()

    # Geographic filters
    state = models.ForeignKey('api.State', on_delete=models.CASCADE, null=True, blank=True, related_name='interaction_stats')
    district = models.ForeignKey('api.District', on_delete=models.CASCADE, null=True, blank=True, related_name='interaction_stats')
    constituency = models.ForeignKey('api.Constituency', on_delete=models.CASCADE, null=True, blank=True, related_name='interaction_stats')

    # Interaction counts by type
    total_interactions = models.IntegerField(default=0)
    phone_calls = models.IntegerField(default=0)
    door_to_door = models.IntegerField(default=0)
    events = models.IntegerField(default=0)
    social_media = models.IntegerField(default=0)

    # Outcome metrics
    conversions = models.IntegerField(default=0)  # neutral -> supporter
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    # Team performance
    active_volunteers = models.IntegerField(default=0)
    top_volunteer_id = models.IntegerField(null=True, blank=True)
    top_volunteer_count = models.IntegerField(default=0)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['date', 'state', 'district', 'constituency']
        indexes = [
            models.Index(fields=['date', 'state']),
            models.Index(fields=['date', 'district']),
            models.Index(fields=['date', 'constituency']),
            models.Index(fields=['-date']),
        ]
        verbose_name = "Daily Interaction Stats"
        verbose_name_plural = "Daily Interaction Stats"

    def __str__(self):
        location = self.constituency or self.district or self.state or "All"
        return f"{self.date} - {location}"


class DailySentimentStats(models.Model):
    """Aggregated daily sentiment statistics"""
    date = models.DateField()

    # Geographic filters
    state = models.ForeignKey('api.State', on_delete=models.CASCADE, null=True, blank=True, related_name='sentiment_stats')
    district = models.ForeignKey('api.District', on_delete=models.CASCADE, null=True, blank=True, related_name='sentiment_stats')
    constituency = models.ForeignKey('api.Constituency', on_delete=models.CASCADE, null=True, blank=True, related_name='sentiment_stats')

    # Issue category
    issue = models.ForeignKey('api.IssueCategory', on_delete=models.CASCADE, null=True, blank=True, related_name='sentiment_stats')

    # Sentiment metrics
    avg_sentiment_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    sentiment_velocity = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # rate of change

    positive_count = models.IntegerField(default=0)
    negative_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)

    # Source breakdown
    from_feedback = models.IntegerField(default=0)
    from_field_reports = models.IntegerField(default=0)
    from_social_media = models.IntegerField(default=0)
    from_surveys = models.IntegerField(default=0)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date', 'state']),
            models.Index(fields=['date', 'issue']),
            models.Index(fields=['date', 'constituency']),
            models.Index(fields=['-date']),
        ]
        verbose_name = "Daily Sentiment Stats"
        verbose_name_plural = "Daily Sentiment Stats"

    def __str__(self):
        location = self.constituency or self.district or self.state or "All"
        issue_name = self.issue.name if self.issue else "Overall"
        return f"{self.date} - {location} - {issue_name}"


class WeeklyCampaignStats(models.Model):
    """Aggregated weekly campaign statistics"""
    week_start = models.DateField()
    week_end = models.DateField()

    # Geographic filters
    state = models.ForeignKey('api.State', on_delete=models.CASCADE, null=True, blank=True, related_name='campaign_stats')
    district = models.ForeignKey('api.District', on_delete=models.CASCADE, null=True, blank=True, related_name='campaign_stats')

    # Campaign metrics
    total_campaigns = models.IntegerField(default=0)
    active_campaigns = models.IntegerField(default=0)
    completed_campaigns = models.IntegerField(default=0)

    # Performance
    total_reach = models.IntegerField(default=0)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    avg_roi = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    # Engagement
    total_interactions = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-week_start']
        indexes = [
            models.Index(fields=['week_start', 'state']),
            models.Index(fields=['week_start', 'district']),
            models.Index(fields=['-week_start']),
        ]
        verbose_name = "Weekly Campaign Stats"
        verbose_name_plural = "Weekly Campaign Stats"

    def __str__(self):
        location = self.district or self.state or "All"
        return f"Week {self.week_start} - {location}"


class ReportTemplate(models.Model):
    """Saved report templates for custom reports"""
    REPORT_TYPES = [
        ('executive_summary', 'Executive Summary'),
        ('campaign_performance', 'Campaign Performance'),
        ('constituency', 'Constituency Report'),
        ('daily_activity', 'Daily Activity'),
        ('weekly_summary', 'Weekly Summary'),
        ('volunteer_performance', 'Volunteer Performance'),
        ('custom', 'Custom Report'),
    ]

    template_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)

    # Creator
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='report_templates')

    # Template configuration
    metrics = models.JSONField(default=list, help_text="List of metrics to include")
    filters = models.JSONField(default=dict, help_text="Default filters")
    visualizations = models.JSONField(default=list, help_text="Chart configurations")

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=20, blank=True)  # daily, weekly, monthly
    schedule_time = models.TimeField(null=True, blank=True)
    schedule_day = models.IntegerField(null=True, blank=True)  # day of week/month

    # Recipients
    recipients = models.JSONField(default=list, help_text="Email addresses for scheduled reports")

    # Export format
    export_format = models.CharField(max_length=20, default='pdf')  # pdf, excel, both

    # Status
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['report_type']),
            models.Index(fields=['is_scheduled']),
        ]
        verbose_name = "Report Template"
        verbose_name_plural = "Report Templates"

    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class GeneratedReport(models.Model):
    """Track generated reports"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generating', 'Generating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    report_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='generated_reports')

    # Report details
    report_name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50)

    # Generation
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_reports')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Files
    pdf_file_url = models.URLField(max_length=500, blank=True)
    excel_file_url = models.URLField(max_length=500, blank=True)

    # Size and metadata
    file_size = models.BigIntegerField(null=True, blank=True)
    generation_time = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)  # seconds

    # Access
    download_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)  # 24 hours default

    # Error tracking
    error_message = models.TextField(blank=True)

    # Metadata
    filters_used = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['generated_by', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = "Generated Report"
        verbose_name_plural = "Generated Reports"

    def __str__(self):
        return f"{self.report_name} - {self.status}"

    def is_expired(self):
        """Check if report download has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class ExportJob(models.Model):
    """Track data export jobs"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('json', 'JSON'),
        ('pdf', 'PDF'),
    ]

    job_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_jobs')

    # Export configuration
    resource = models.CharField(max_length=50)  # voters, interactions, etc.
    export_format = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    filters = models.JSONField(default=dict)
    fields = models.JSONField(default=list)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    progress = models.IntegerField(default=0)  # 0-100

    # File details
    file_url = models.URLField(max_length=500, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    row_count = models.IntegerField(null=True, blank=True)

    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Error tracking
    error_message = models.TextField(blank=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['job_id']),
        ]
        verbose_name = "Export Job"
        verbose_name_plural = "Export Jobs"

    def __str__(self):
        return f"{self.resource} export - {self.status}"

    def get_progress_display(self):
        """Get human-readable progress"""
        if self.status == 'completed':
            return "100%"
        elif self.status == 'failed':
            return "Failed"
        return f"{self.progress}%"
