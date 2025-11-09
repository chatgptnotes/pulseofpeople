"""
Migration for security and performance enhancements
Adds 2FA fields and database indexes
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_district_state_constituency_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
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

        # Create TwoFactorBackupCode model
        migrations.CreateModel(
            name='TwoFactorBackupCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_hash', models.CharField(help_text='Hashed backup code', max_length=255)),
                ('is_used', models.BooleanField(default=False)),
                ('used_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='twofactor_backup_codes', to='auth.user')),
            ],
            options={
                'verbose_name': '2FA Backup Code',
                'verbose_name_plural': '2FA Backup Codes',
                'ordering': ['-created_at'],
            },
        ),

        # Add indexes for TwoFactorBackupCode
        migrations.AddIndex(
            model_name='twofactorbackupcode',
            index=models.Index(fields=['user', 'is_used'], name='api_twofact_user_id_is_used_idx'),
        ),

        # Performance indexes for existing models
        # DirectFeedback indexes
        migrations.AddIndex(
            model_name='directfeedback',
            index=models.Index(fields=['state', 'district'], name='api_directf_state_district_idx'),
        ),
        migrations.AddIndex(
            model_name='directfeedback',
            index=models.Index(fields=['status', '-submitted_at'], name='api_directf_status_date_idx'),
        ),

        # FieldReport indexes
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['state', 'district'], name='api_fieldr_state_district_idx'),
        ),
        migrations.AddIndex(
            model_name='fieldreport',
            index=models.Index(fields=['verification_status', '-timestamp'], name='api_fieldr_verify_date_idx'),
        ),

        # SentimentData indexes
        migrations.AddIndex(
            model_name='sentimentdata',
            index=models.Index(fields=['state', 'district'], name='api_sentim_state_district_idx'),
        ),
        migrations.AddIndex(
            model_name='sentimentdata',
            index=models.Index(fields=['polarity', '-timestamp'], name='api_sentim_polarity_date_idx'),
        ),

        # PollingBooth indexes
        migrations.AddIndex(
            model_name='pollingbooth',
            index=models.Index(fields=['is_active', 'constituency'], name='api_polling_active_const_idx'),
        ),

        # AuditLog indexes (additional)
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['action', '-timestamp'], name='api_auditl_action_date_idx'),
        ),

        # UserProfile indexes
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['role', 'organization'], name='api_userpr_role_org_idx'),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            index=models.Index(fields=['is_2fa_enabled'], name='api_userpr_2fa_enabled_idx'),
        ),
    ]
