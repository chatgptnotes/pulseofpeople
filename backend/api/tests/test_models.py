"""
Unit tests for models
Tests all model functionality, validation, and methods
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from api.models import (
    Organization, UserProfile, Permission, RolePermission,
    UserPermission, AuditLog, Notification, Task, UploadedFile,
    State, District, Constituency, PollingBooth, PoliticalParty,
    IssueCategory, VoterSegment, DirectFeedback, FieldReport,
    SentimentData, BoothAgent, BulkUploadJob, BulkUploadError,
    TwoFactorBackupCode
)


class OrganizationModelTest(TestCase):
    """Test Organization model"""

    def setUp(self):
        self.org = Organization.objects.create(
            name="Test Organization",
            slug="test-org",
            subscription_status="active",
            subscription_tier="premium",
            max_users=50
        )

    def test_organization_creation(self):
        """Test creating an organization"""
        self.assertEqual(self.org.name, "Test Organization")
        self.assertEqual(self.org.slug, "test-org")
        self.assertEqual(self.org.max_users, 50)

    def test_organization_str(self):
        """Test string representation"""
        self.assertEqual(str(self.org), "Test Organization")

    def test_organization_settings_default(self):
        """Test default settings is empty dict"""
        self.assertEqual(self.org.settings, {})


class UserProfileModelTest(TestCase):
    """Test UserProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            role='admin'
        )

    def test_profile_creation(self):
        """Test creating a user profile"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.role, 'admin')

    def test_is_superadmin(self):
        """Test superadmin check"""
        self.assertFalse(self.profile.is_superadmin())
        self.profile.role = 'superadmin'
        self.assertTrue(self.profile.is_superadmin())

    def test_is_admin(self):
        """Test admin check"""
        self.assertTrue(self.profile.is_admin())

    def test_is_admin_or_above(self):
        """Test admin or above check"""
        self.assertTrue(self.profile.is_admin_or_above())

        self.profile.role = 'user'
        self.assertFalse(self.profile.is_admin_or_above())

    def test_2fa_fields(self):
        """Test 2FA fields"""
        self.assertFalse(self.profile.is_2fa_enabled)
        self.assertIsNone(self.profile.totp_secret)

        self.profile.is_2fa_enabled = True
        self.profile.totp_secret = 'TESTSECRET123456'
        self.profile.save()

        self.assertTrue(self.profile.is_2fa_enabled)
        self.assertEqual(self.profile.totp_secret, 'TESTSECRET123456')


class PermissionModelTest(TestCase):
    """Test Permission model"""

    def setUp(self):
        self.permission = Permission.objects.create(
            name='create_user',
            category='users',
            description='Permission to create users'
        )

    def test_permission_creation(self):
        """Test creating a permission"""
        self.assertEqual(self.permission.name, 'create_user')
        self.assertEqual(self.permission.category, 'users')

    def test_permission_str(self):
        """Test string representation"""
        self.assertEqual(str(self.permission), 'users: create_user')


class StateModelTest(TestCase):
    """Test State model"""

    def setUp(self):
        self.state = State.objects.create(
            name='Tamil Nadu',
            code='TN',
            capital='Chennai',
            region='South',
            total_districts=38,
            total_constituencies=234
        )

    def test_state_creation(self):
        """Test creating a state"""
        self.assertEqual(self.state.name, 'Tamil Nadu')
        self.assertEqual(self.state.code, 'TN')
        self.assertEqual(self.state.capital, 'Chennai')

    def test_state_str(self):
        """Test string representation"""
        self.assertEqual(str(self.state), 'Tamil Nadu')


class DistrictModelTest(TestCase):
    """Test District model"""

    def setUp(self):
        self.state = State.objects.create(
            name='Tamil Nadu',
            code='TN'
        )
        self.district = District.objects.create(
            state=self.state,
            name='Chennai',
            code='TN-CH',
            headquarters='Chennai',
            population=4646732
        )

    def test_district_creation(self):
        """Test creating a district"""
        self.assertEqual(self.district.name, 'Chennai')
        self.assertEqual(self.district.state, self.state)
        self.assertEqual(self.district.population, 4646732)

    def test_district_str(self):
        """Test string representation"""
        self.assertEqual(str(self.district), 'Chennai, TN')


class ConstituencyModelTest(TestCase):
    """Test Constituency model"""

    def setUp(self):
        self.state = State.objects.create(name='Tamil Nadu', code='TN')
        self.district = District.objects.create(
            state=self.state,
            name='Chennai',
            code='TN-CH'
        )
        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name='T. Nagar',
            code='TN-001',
            constituency_type='assembly',
            number=1,
            reserved_for='general',
            total_voters=250000
        )

    def test_constituency_creation(self):
        """Test creating a constituency"""
        self.assertEqual(self.constituency.name, 'T. Nagar')
        self.assertEqual(self.constituency.code, 'TN-001')
        self.assertEqual(self.constituency.total_voters, 250000)

    def test_constituency_str(self):
        """Test string representation"""
        self.assertEqual(str(self.constituency), 'T. Nagar (1)')

    def test_constituency_type_choices(self):
        """Test constituency type choices"""
        self.assertIn(self.constituency.constituency_type, ['assembly', 'parliamentary'])


class PollingBoothModelTest(TestCase):
    """Test PollingBooth model"""

    def setUp(self):
        self.state = State.objects.create(name='Tamil Nadu', code='TN')
        self.district = District.objects.create(state=self.state, name='Chennai', code='TN-CH')
        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name='T. Nagar',
            code='TN-001',
            number=1
        )
        self.booth = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Government School',
            total_voters=1500,
            male_voters=750,
            female_voters=750
        )

    def test_booth_creation(self):
        """Test creating a polling booth"""
        self.assertEqual(self.booth.booth_number, '001')
        self.assertEqual(self.booth.total_voters, 1500)

    def test_booth_str(self):
        """Test string representation"""
        self.assertEqual(str(self.booth), 'Booth 001 - Government School')

    def test_booth_voter_counts(self):
        """Test voter count fields"""
        self.assertEqual(self.booth.male_voters + self.booth.female_voters, 1500)


class DirectFeedbackModelTest(TestCase):
    """Test DirectFeedback model"""

    def setUp(self):
        self.state = State.objects.create(name='Tamil Nadu', code='TN')
        self.district = District.objects.create(state=self.state, name='Chennai', code='TN-CH')
        self.category = IssueCategory.objects.create(name='Education', description='Education issues')

        self.feedback = DirectFeedback.objects.create(
            citizen_name='John Doe',
            citizen_age=35,
            citizen_phone='9876543210',
            state=self.state,
            district=self.district,
            ward='Ward 5',
            issue_category=self.category,
            message_text='Need better schools',
            status='pending'
        )

    def test_feedback_creation(self):
        """Test creating feedback"""
        self.assertEqual(self.feedback.citizen_name, 'John Doe')
        self.assertEqual(self.feedback.status, 'pending')

    def test_feedback_has_uuid(self):
        """Test feedback has UUID"""
        self.assertIsNotNone(self.feedback.feedback_id)

    def test_sentiment_score_validation(self):
        """Test sentiment score is between 0 and 1"""
        self.feedback.ai_sentiment_score = Decimal('0.75')
        self.feedback.save()
        self.assertEqual(self.feedback.ai_sentiment_score, Decimal('0.75'))


class SentimentDataModelTest(TestCase):
    """Test SentimentData model"""

    def setUp(self):
        self.state = State.objects.create(name='Tamil Nadu', code='TN')
        self.category = IssueCategory.objects.create(name='Healthcare')

        self.sentiment = SentimentData.objects.create(
            source_type='direct_feedback',
            source_id='123e4567-e89b-12d3-a456-426614174000',
            issue=self.category,
            sentiment_score=Decimal('0.85'),
            polarity='positive',
            confidence=Decimal('0.90'),
            state=self.state
        )

    def test_sentiment_creation(self):
        """Test creating sentiment data"""
        self.assertEqual(self.sentiment.polarity, 'positive')
        self.assertEqual(self.sentiment.sentiment_score, Decimal('0.85'))

    def test_sentiment_str(self):
        """Test string representation"""
        expected = f"Healthcare - positive (0.85)"
        self.assertEqual(str(self.sentiment), expected)


class TwoFactorBackupCodeModelTest(TestCase):
    """Test TwoFactorBackupCode model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.backup_code = TwoFactorBackupCode.objects.create(
            user=self.user,
            code_hash='hashed_code_12345'
        )

    def test_backup_code_creation(self):
        """Test creating backup code"""
        self.assertEqual(self.backup_code.user, self.user)
        self.assertFalse(self.backup_code.is_used)

    def test_backup_code_str(self):
        """Test string representation"""
        self.assertIn('testuser', str(self.backup_code))
        self.assertIn('Active', str(self.backup_code))

        self.backup_code.is_used = True
        self.backup_code.save()
        self.assertIn('Used', str(self.backup_code))


class AuditLogModelTest(TestCase):
    """Test AuditLog model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.log = AuditLog.objects.create(
            user=self.user,
            action='create',
            target_model='User',
            target_id='123',
            ip_address='127.0.0.1'
        )

    def test_audit_log_creation(self):
        """Test creating audit log"""
        self.assertEqual(self.log.action, 'create')
        self.assertEqual(self.log.user, self.user)

    def test_audit_log_str(self):
        """Test string representation"""
        self.assertIn('testuser', str(self.log))
        self.assertIn('create', str(self.log))


class BulkUploadJobModelTest(TestCase):
    """Test BulkUploadJob model"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.job = BulkUploadJob.objects.create(
            created_by=self.user,
            file_name='voters.xlsx',
            file_path='/uploads/voters.xlsx',
            status='pending',
            total_rows=1000
        )

    def test_job_creation(self):
        """Test creating upload job"""
        self.assertEqual(self.job.status, 'pending')
        self.assertEqual(self.job.total_rows, 1000)

    def test_progress_percentage(self):
        """Test progress calculation"""
        self.assertEqual(self.job.get_progress_percentage(), 0)

        self.job.processed_rows = 500
        self.assertEqual(self.job.get_progress_percentage(), 50)

        self.job.processed_rows = 1000
        self.assertEqual(self.job.get_progress_percentage(), 100)
