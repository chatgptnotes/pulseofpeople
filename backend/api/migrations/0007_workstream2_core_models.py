# Generated migration for Workstream 2 core models

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0006_district_state_constituency_and_more'),
    ]

    operations = [
        # Update Organization model with new fields
        migrations.AddField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='org_logos/'),
        ),
        migrations.AddField(
            model_name='organization',
            name='organization_type',
            field=models.CharField(choices=[('party', 'Political Party'), ('campaign', 'Campaign Organization'), ('ngo', 'NGO'), ('other', 'Other')], default='campaign', max_length=20),
        ),
        migrations.AddField(
            model_name='organization',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='organization',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='organization',
            name='address',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='city',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='organization',
            name='state',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='organization',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='social_media_links',
            field=models.JSONField(blank=True, default=dict, help_text='Social media URLs'),
        ),
        migrations.AddField(
            model_name='organization',
            name='subscription_plan',
            field=models.CharField(choices=[('free', 'Free'), ('basic', 'Basic'), ('pro', 'Professional'), ('enterprise', 'Enterprise')], default='free', max_length=20),
        ),
        migrations.AddField(
            model_name='organization',
            name='subscription_expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='subscription_tier',
            new_name='subscription_plan_old',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='subscription_plan_old',
        ),

        # Add 2FA fields to UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='is_2fa_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='totp_secret',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),

        # Create Voter model
        migrations.CreateModel(
            name='Voter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voter_id', models.CharField(db_index=True, help_text='Official voter ID', max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(blank=True, max_length=100)),
                ('middle_name', models.CharField(blank=True, max_length=100)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('age', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(18), django.core.validators.MaxValueValidator(120)])),
                ('gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('phone', models.CharField(blank=True, db_index=True, max_length=20)),
                ('alternate_phone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='voter_photos/')),
                ('address_line1', models.CharField(blank=True, max_length=200)),
                ('address_line2', models.CharField(blank=True, max_length=200)),
                ('landmark', models.CharField(blank=True, max_length=200)),
                ('ward', models.CharField(blank=True, db_index=True, max_length=100)),
                ('pincode', models.CharField(blank=True, max_length=10)),
                ('latitude', models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=8, max_digits=11, null=True)),
                ('party_affiliation', models.CharField(choices=[('bjp', 'BJP'), ('congress', 'Congress'), ('aap', 'AAP'), ('tvk', 'TVK'), ('dmk', 'DMK'), ('aiadmk', 'AIADMK'), ('neutral', 'Neutral'), ('unknown', 'Unknown'), ('other', 'Other')], default='unknown', max_length=20)),
                ('voting_history', models.JSONField(blank=True, default=list, help_text='Last 5 elections voting history')),
                ('sentiment', models.CharField(choices=[('strong_supporter', 'Strong Supporter'), ('supporter', 'Supporter'), ('neutral', 'Neutral'), ('opposition', 'Opposition'), ('strong_opposition', 'Strong Opposition')], default='neutral', max_length=30)),
                ('influence_level', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='low', max_length=20)),
                ('is_opinion_leader', models.BooleanField(default=False)),
                ('last_contacted_at', models.DateTimeField(blank=True, null=True)),
                ('contact_frequency', models.IntegerField(default=0, help_text='Number of times contacted')),
                ('interaction_count', models.IntegerField(default=0)),
                ('positive_interactions', models.IntegerField(default=0)),
                ('negative_interactions', models.IntegerField(default=0)),
                ('preferred_communication', models.CharField(choices=[('phone', 'Phone Call'), ('sms', 'SMS'), ('whatsapp', 'WhatsApp'), ('email', 'Email'), ('door_to_door', 'Door to Door')], default='phone', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('tags', models.JSONField(blank=True, default=list, help_text='Tags for categorization')),
                ('notes', models.TextField(blank=True)),
                ('constituency', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voters', to='api.constituency')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_voters', to=settings.AUTH_USER_MODEL)),
                ('district', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voters', to='api.district')),
                ('state', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voters', to='api.state')),
            ],
            options={
                'verbose_name': 'Voter',
                'verbose_name_plural': 'Voters',
                'ordering': ['-created_at'],
            },
        ),

        # Create VoterInteraction model
        migrations.CreateModel(
            name='VoterInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('phone_call', 'Phone Call'), ('door_visit', 'Door to Door Visit'), ('event_meeting', 'Event Meeting'), ('sms', 'SMS'), ('email', 'Email'), ('whatsapp', 'WhatsApp')], max_length=20)),
                ('interaction_date', models.DateTimeField(auto_now_add=True)),
                ('duration_minutes', models.IntegerField(blank=True, help_text='Duration in minutes', null=True)),
                ('sentiment', models.CharField(choices=[('positive', 'Positive'), ('neutral', 'Neutral'), ('negative', 'Negative')], default='neutral', max_length=10)),
                ('issues_discussed', models.JSONField(blank=True, default=list)),
                ('promises_made', models.TextField(blank=True)),
                ('follow_up_required', models.BooleanField(default=False)),
                ('follow_up_date', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('contacted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='voter_interactions', to=settings.AUTH_USER_MODEL)),
                ('voter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='api.voter')),
            ],
            options={
                'verbose_name': 'Voter Interaction',
                'verbose_name_plural': 'Voter Interactions',
                'ordering': ['-interaction_date'],
            },
        ),

        # Create Campaign model
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_name', models.CharField(max_length=200)),
                ('campaign_type', models.CharField(choices=[('election', 'Election Campaign'), ('awareness', 'Awareness Campaign'), ('issue_based', 'Issue-based Campaign'), ('door_to_door', 'Door to Door Campaign')], max_length=20)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.CharField(choices=[('planning', 'Planning'), ('active', 'Active'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='planning', max_length=20)),
                ('budget', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('spent_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('target_audience', models.TextField(blank=True, help_text='Description of target audience')),
                ('goals', models.JSONField(blank=True, default=dict, help_text='Campaign goals and objectives')),
                ('metrics', models.JSONField(blank=True, default=dict, help_text='Reach, engagement, conversion metrics')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campaign_manager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_campaigns', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_campaigns', to=settings.AUTH_USER_MODEL)),
                ('target_constituency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campaigns', to='api.constituency')),
                ('team_members', models.ManyToManyField(blank=True, related_name='campaigns', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Campaign',
                'verbose_name_plural': 'Campaigns',
                'ordering': ['-start_date'],
            },
        ),

        # Create SocialMediaPost model
        migrations.CreateModel(
            name='SocialMediaPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('facebook', 'Facebook'), ('twitter', 'Twitter/X'), ('instagram', 'Instagram'), ('whatsapp', 'WhatsApp'), ('youtube', 'YouTube')], max_length=20)),
                ('post_content', models.TextField()),
                ('post_url', models.URLField(blank=True)),
                ('post_id', models.CharField(blank=True, help_text='Platform-specific post ID', max_length=200)),
                ('posted_at', models.DateTimeField()),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('reach', models.IntegerField(default=0)),
                ('impressions', models.IntegerField(default=0)),
                ('engagement_count', models.IntegerField(default=0)),
                ('likes', models.IntegerField(default=0)),
                ('shares', models.IntegerField(default=0)),
                ('comments_count', models.IntegerField(default=0)),
                ('sentiment_score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)])),
                ('is_published', models.BooleanField(default=False)),
                ('is_promoted', models.BooleanField(default=False)),
                ('hashtags', models.JSONField(blank=True, default=list)),
                ('mentions', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='social_posts', to='api.campaign')),
                ('posted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='social_posts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Social Media Post',
                'verbose_name_plural': 'Social Media Posts',
                'ordering': ['-posted_at'],
            },
        ),

        # Create Alert model
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alert_type', models.CharField(choices=[('info', 'Information'), ('warning', 'Warning'), ('urgent', 'Urgent'), ('critical', 'Critical')], default='info', max_length=20)),
                ('title', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('target_role', models.CharField(blank=True, choices=[('superadmin', 'Super Admin'), ('admin', 'Admin'), ('manager', 'Manager'), ('analyst', 'Analyst'), ('user', 'User'), ('viewer', 'Viewer'), ('volunteer', 'Volunteer')], help_text='Send to specific role', max_length=20)),
                ('priority', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20)),
                ('is_read', models.BooleanField(default=False)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('action_url', models.URLField(blank=True)),
                ('action_required', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('constituency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alerts', to='api.constituency')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_alerts', to=settings.AUTH_USER_MODEL)),
                ('district', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='alerts', to='api.district')),
                ('target_users', models.ManyToManyField(blank=True, related_name='alerts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Alert',
                'verbose_name_plural': 'Alerts',
                'ordering': ['-created_at'],
            },
        ),

        # Create Event model
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=200)),
                ('event_type', models.CharField(choices=[('rally', 'Rally'), ('meeting', 'Meeting'), ('door_to_door', 'Door to Door'), ('booth_visit', 'Booth Visit'), ('town_hall', 'Town Hall')], max_length=20)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('location', models.CharField(max_length=300)),
                ('ward', models.CharField(blank=True, max_length=100)),
                ('latitude', models.DecimalField(blank=True, decimal_places=8, max_digits=10, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=8, max_digits=11, null=True)),
                ('expected_attendance', models.IntegerField(default=0)),
                ('actual_attendance', models.IntegerField(default=0)),
                ('budget', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('expenses', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(choices=[('planned', 'Planned'), ('ongoing', 'Ongoing'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='planned', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('photos', models.JSONField(blank=True, default=list, help_text='URLs to event photos')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='api.campaign')),
                ('constituency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='events', to='api.constituency')),
                ('organizer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='organized_events', to=settings.AUTH_USER_MODEL)),
                ('volunteers', models.ManyToManyField(blank=True, related_name='volunteer_events', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Event',
                'verbose_name_plural': 'Events',
                'ordering': ['-start_datetime'],
            },
        ),

        # Create VolunteerProfile model
        migrations.CreateModel(
            name='VolunteerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volunteer_id', models.CharField(db_index=True, max_length=50, unique=True)),
                ('skills', models.JSONField(blank=True, default=list, help_text='List of volunteer skills')),
                ('availability', models.JSONField(blank=True, default=dict, help_text='Days and times available')),
                ('assigned_ward', models.CharField(blank=True, max_length=100)),
                ('tasks_completed', models.IntegerField(default=0)),
                ('hours_contributed', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('rating', models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
                ('is_active', models.BooleanField(default=True)),
                ('joined_at', models.DateField(auto_now_add=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_constituency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='volunteers', to='api.constituency')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='volunteer_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Volunteer Profile',
                'verbose_name_plural': 'Volunteer Profiles',
            },
        ),

        # Create Expense model
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expense_type', models.CharField(choices=[('travel', 'Travel'), ('materials', 'Campaign Materials'), ('advertising', 'Advertising'), ('event', 'Event Expenses'), ('salary', 'Salary/Honorarium'), ('other', 'Other')], max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency', models.CharField(default='INR', max_length=3)),
                ('description', models.TextField()),
                ('receipt_image', models.ImageField(blank=True, null=True, upload_to='receipts/')),
                ('status', models.CharField(choices=[('pending', 'Pending Approval'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('paid', 'Paid')], default='pending', max_length=20)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_expenses', to=settings.AUTH_USER_MODEL)),
                ('campaign', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expenses', to='api.campaign')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_expenses', to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='expense_items', to='api.event')),
            ],
            options={
                'verbose_name': 'Expense',
                'verbose_name_plural': 'Expenses',
                'ordering': ['-created_at'],
            },
        ),

        # Add indexes
        migrations.AddIndex(
            model_name='voter',
            index=models.Index(fields=['voter_id'], name='api_voter_voter_i_idx'),
        ),
        migrations.AddIndex(
            model_name='voter',
            index=models.Index(fields=['constituency', 'ward'], name='api_voter_const_ward_idx'),
        ),
        migrations.AddIndex(
            model_name='voter',
            index=models.Index(fields=['party_affiliation'], name='api_voter_party_idx'),
        ),
        migrations.AddIndex(
            model_name='voter',
            index=models.Index(fields=['sentiment'], name='api_voter_sentiment_idx'),
        ),
        migrations.AddIndex(
            model_name='voter',
            index=models.Index(fields=['phone'], name='api_voter_phone_idx'),
        ),
        migrations.AddIndex(
            model_name='voter',
            index=models.Index(fields=['is_active'], name='api_voter_active_idx'),
        ),
        migrations.AddIndex(
            model_name='voter',
            index=models.Index(fields=['-created_at'], name='api_voter_created_idx'),
        ),
    ]
