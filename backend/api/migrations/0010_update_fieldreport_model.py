# Generated manually for FieldReport model updates

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0009_pollingbooth'),
    ]

    operations = [
        # Step 0: Remove old indexes first
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_volunte_82454f_idx',
        ),
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_ward_75a8e3_idx',
        ),
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_booth_n_91717d_idx',
        ),
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_constit_f1ae02_idx',
        ),
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_verific_7f2d70_idx',
        ),
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_report__0858bd_idx',
        ),
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_timesta_7a8a66_idx',
        ),
        migrations.RemoveIndex(
            model_name='fieldreport',
            name='api_fieldre_report__c0fcac_idx',
        ),

        # Step 1: Rename fields
        migrations.RenameField(
            model_name='fieldreport',
            old_name='volunteer',
            new_name='submitted_by',
        ),
        migrations.RenameField(
            model_name='fieldreport',
            old_name='location_lat',
            new_name='latitude',
        ),
        migrations.RenameField(
            model_name='fieldreport',
            old_name='location_lng',
            new_name='longitude',
        ),
        migrations.RenameField(
            model_name='fieldreport',
            old_name='verified_at',
            new_name='reviewed_at',
        ),
        migrations.RenameField(
            model_name='fieldreport',
            old_name='verified_by',
            new_name='reviewed_by',
        ),

        # Step 2: Remove old fields
        migrations.RemoveField(
            model_name='fieldreport',
            name='address',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='booth_number',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='competitor_activity_description',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='competitor_party',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='crowd_size',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='key_issues',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='media_urls',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='negative_reactions',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='positive_reactions',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='quotes',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='report_date',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='timestamp',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='verification_notes',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='verification_status',
        ),
        migrations.RemoveField(
            model_name='fieldreport',
            name='voter_segments_met',
        ),

        # Step 3: Alter existing fields
        migrations.AlterField(
            model_name='fieldreport',
            name='report_type',
            field=models.CharField(choices=[
                ('voter_interaction', 'Voter Interaction'),
                ('event_attendance', 'Event Attendance'),
                ('issue_report', 'Issue Report'),
                ('sentiment_feedback', 'Sentiment Feedback')
            ], max_length=50),
        ),
        migrations.AlterField(
            model_name='fieldreport',
            name='title',
            field=models.CharField(max_length=200),
        ),
        migrations.RenameField(
            model_name='fieldreport',
            old_name='notes',
            new_name='review_notes',
        ),

        # Step 4: Add new fields with defaults
        migrations.AddField(
            model_name='fieldreport',
            name='description',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='fieldreport',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('reviewed', 'Reviewed'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected')
                ],
                default='pending',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='fieldreport',
            name='attachments',
            field=models.JSONField(blank=True, default=list, help_text='List of attachment URLs'),
        ),
        migrations.AddField(
            model_name='fieldreport',
            name='voter_sentiment',
            field=models.CharField(
                blank=True,
                choices=[
                    ('positive', 'Positive'),
                    ('neutral', 'Neutral'),
                    ('negative', 'Negative'),
                    ('very_negative', 'Very Negative')
                ],
                max_length=20,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='fieldreport',
            name='priority',
            field=models.CharField(
                choices=[
                    ('low', 'Low'),
                    ('medium', 'Medium'),
                    ('high', 'High'),
                    ('urgent', 'Urgent')
                ],
                default='medium',
                max_length=20
            ),
        ),

        # Step 5: Update Meta options
        migrations.AlterModelOptions(
            name='fieldreport',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Field Report',
                'verbose_name_plural': 'Field Reports'
            },
        ),

        # Step 6: Update indexes
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['submitted_by', '-created_at'], name='api_fieldr_submitt_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['ward'], name='api_fieldr_ward_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['constituency'], name='api_fieldr_constit_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['status'], name='api_fieldr_status_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['report_type'], name='api_fieldr_report_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['priority'], name='api_fieldr_priorit_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['-created_at'], name='api_fieldr_created_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['district'], name='api_fieldr_distric_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['voter_sentiment'], name='api_fieldr_voter_s_idx'),
        ),
    ]
