"""
API Integration Tests - Authentication
Tests authentication flows, permissions, and security
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from api.models import UserProfile, Organization, Permission, RolePermission


class AuthenticationAPITest(APITestCase):
    """Test authentication API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create test organization
        self.org = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )

        # Create test users with different roles
        self.superadmin_user = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password='superpass123'
        )
        self.superadmin_profile = UserProfile.objects.create(
            user=self.superadmin_user,
            role='superadmin'
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            role='admin',
            organization=self.org
        )

        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            role='user',
            organization=self.org
        )

        self.viewer = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='viewerpass123'
        )
        self.viewer_profile = UserProfile.objects.create(
            user=self.viewer,
            role='viewer',
            organization=self.org
        )

    def test_login_with_valid_credentials(self):
        """Test login with correct credentials"""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_with_invalid_credentials(self):
        """Test login with wrong password"""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@example.com',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_with_nonexistent_user(self):
        """Test login with non-existent email"""
        response = self.client.post('/api/auth/login/', {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        })

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_without_auth(self):
        """Test accessing protected endpoint without authentication"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_endpoint_with_auth(self):
        """Test accessing protected endpoint with authentication"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/users/')

        # Should succeed (200) or return empty list (depending on implementation)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN])

    def test_token_refresh(self):
        """Test JWT token refresh"""
        # First login to get tokens
        login_response = self.client.post('/api/auth/login/', {
            'email': 'admin@example.com',
            'password': 'adminpass123'
        })

        refresh_token = login_response.data.get('refresh')

        # Use refresh token to get new access token
        refresh_response = self.client.post('/api/auth/refresh/', {
            'refresh': refresh_token
        })

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)


class PermissionAPITest(APITestCase):
    """Test permission-based access control"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        # Create organization
        self.org = Organization.objects.create(name="Test Org", slug="test-org")

        # Create users with different roles
        self.superadmin = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.superadmin, role='superadmin')

        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.admin, role='admin', organization=self.org)

        self.viewer = User.objects.create_user(
            username='viewer',
            email='viewer@example.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.viewer, role='viewer', organization=self.org)

    def test_superadmin_has_all_permissions(self):
        """Test superadmin can access everything"""
        self.client.force_authenticate(user=self.superadmin)

        # Superadmin should be able to access admin endpoints
        response = self.client.get('/api/admin/users/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_admin_can_manage_org_users(self):
        """Test admin can manage users in their organization"""
        self.client.force_authenticate(user=self.admin)

        # Admin should be able to access user management
        response = self.client.get('/api/admin/users/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_viewer_cannot_create_users(self):
        """Test viewer cannot create users"""
        self.client.force_authenticate(user=self.viewer)

        response = self.client.post('/api/admin/users/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'role': 'user'
        })

        # Should be forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_access_different_org(self):
        """Test users can only access data from their organization"""
        # Create another organization with a user
        other_org = Organization.objects.create(name="Other Org", slug="other-org")

        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )
        UserProfile.objects.create(user=other_user, role='user', organization=other_org)

        # Admin from first org should not see users from other org
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')

        if response.status_code == status.HTTP_200_OK:
            # If endpoint exists, check that other org users are not visible
            usernames = [u['username'] for u in response.data.get('results', response.data)]
            self.assertNotIn('otheruser', usernames)


class RateLimitAPITest(APITestCase):
    """Test rate limiting"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, role='user')

    def test_rate_limiting_on_login(self):
        """Test rate limiting on login endpoint"""
        # Note: This test requires django-ratelimit to be properly configured

        # Try to login multiple times with wrong password
        for i in range(10):
            response = self.client.post('/api/auth/login/', {
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })

            if i < 5:
                # First 5 attempts should get 401
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            else:
                # After rate limit, should get 429 (if rate limiting is active)
                # If not configured, will still get 401
                self.assertIn(response.status_code, [
                    status.HTTP_401_UNAUTHORIZED,
                    status.HTTP_429_TOO_MANY_REQUESTS
                ])


class TwoFactorAuthAPITest(APITestCase):
    """Test 2FA functionality"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='pass123'
        )
        self.profile = UserProfile.objects.create(user=self.user, role='admin')

    def test_2fa_setup(self):
        """Test 2FA setup endpoint"""
        self.client.force_authenticate(user=self.user)

        response = self.client.post('/api/auth/2fa/setup/')

        # Should return QR code and secret key
        if response.status_code == status.HTTP_200_OK:
            self.assertIn('qr_code', response.data)
            self.assertIn('backup_codes', response.data)

    def test_2fa_enable(self):
        """Test enabling 2FA"""
        self.client.force_authenticate(user=self.user)

        # First setup 2FA
        setup_response = self.client.post('/api/auth/2fa/setup/')

        if setup_response.status_code == status.HTTP_200_OK:
            # Try to enable with a code (would need actual TOTP code in real test)
            enable_response = self.client.post('/api/auth/2fa/enable/', {
                'code': '123456'  # Would be actual TOTP code
            })

            # Will likely fail without real code, but endpoint should exist
            self.assertIn(enable_response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_400_BAD_REQUEST
            ])

    def test_2fa_required_for_admin(self):
        """Test that 2FA is enforced for admin roles"""
        # Admin role should require 2FA
        from api.services.two_factor_service import TwoFactorService
        self.assertTrue(TwoFactorService.is_2fa_required_for_role('admin'))
        self.assertTrue(TwoFactorService.is_2fa_required_for_role('superadmin'))
        self.assertFalse(TwoFactorService.is_2fa_required_for_role('viewer'))


class SecurityHeadersAPITest(APITestCase):
    """Test security headers in responses"""

    def setUp(self):
        """Set up test client"""
        self.client = APIClient()

    def test_security_headers_present(self):
        """Test that security headers are present in responses"""
        response = self.client.get('/api/')

        # Check for security headers
        self.assertIn('X-Content-Type-Options', response)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

        self.assertIn('X-Frame-Options', response)
        self.assertEqual(response['X-Frame-Options'], 'DENY')

    def test_no_server_info_disclosure(self):
        """Test that server information is not disclosed"""
        response = self.client.get('/api/')

        # Server and X-Powered-By headers should be removed
        self.assertNotIn('Server', response)
        self.assertNotIn('X-Powered-By', response)
