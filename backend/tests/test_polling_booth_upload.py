"""
Tests for Polling Booth Bulk Upload API
"""
import io
import csv
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from api.models import (
    UserProfile, State, District, Constituency, PollingBooth
)


class PollingBoothBulkUploadTestCase(TestCase):
    """Test cases for polling booth bulk upload functionality"""

    def setUp(self):
        """Set up test data"""
        # Create test state, district, constituency
        self.state = State.objects.create(
            name='Tamil Nadu',
            code='TN',
            capital='Chennai'
        )

        self.district = District.objects.create(
            state=self.state,
            name='Chennai',
            code='TN001'
        )

        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name='Chennai Central',
            code='TN001',
            number=1,
            constituency_type='assembly'
        )

        # Create test users with different roles
        self.superadmin_user = User.objects.create_user(
            username='superadmin',
            email='superadmin@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(
            user=self.superadmin_user,
            role='superadmin'
        )

        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(
            user=self.admin_user,
            role='admin',
            assigned_state=self.state
        )

        self.manager_user = User.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(
            user=self.manager_user,
            role='manager',
            assigned_district=self.district
        )

        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )
        UserProfile.objects.create(
            user=self.regular_user,
            role='user'
        )

        self.client = APIClient()

    def create_csv_file(self, rows):
        """Helper to create CSV file in memory"""
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'booth_number', 'name', 'state_code', 'district_code',
            'constituency_code', 'building_name', 'address', 'area',
            'landmark', 'pincode', 'latitude', 'longitude',
            'total_voters', 'male_voters', 'female_voters', 'other_voters',
            'is_active', 'is_accessible'
        ])

        # Write data rows
        for row in rows:
            writer.writerow(row)

        # Create in-memory file
        output.seek(0)
        csv_file = io.BytesIO(output.getvalue().encode('utf-8'))
        csv_file.name = 'test_booths.csv'
        return csv_file

    def test_bulk_upload_success(self):
        """Test successful bulk upload"""
        self.client.force_authenticate(user=self.admin_user)

        # Create CSV with valid data
        csv_file = self.create_csv_file([
            ['001', 'Test Booth 1', 'TN', 'TN001', 'TN001', 'School 1',
             '123 Main St', 'Area 1', 'Near Park', '600001', '13.0', '80.0',
             '1200', '600', '580', '20', 'True', 'True'],
            ['002', 'Test Booth 2', 'TN', 'TN001', 'TN001', 'School 2',
             '456 West St', 'Area 2', 'Near Temple', '600002', '13.1', '80.1',
             '1500', '750', '730', '20', 'True', 'False']
        ])

        response = self.client.post(
            '/api/polling-booths/bulk-upload/',
            {'file': csv_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['success_count'], 2)
        self.assertEqual(response.data['failed_count'], 0)

        # Verify booths were created
        self.assertEqual(PollingBooth.objects.count(), 2)

    def test_bulk_upload_permission_denied_for_regular_user(self):
        """Test that regular users cannot bulk upload"""
        self.client.force_authenticate(user=self.regular_user)

        csv_file = self.create_csv_file([
            ['001', 'Test Booth', 'TN', 'TN001', 'TN001', 'School',
             '123 Main St', 'Area 1', 'Near Park', '600001', '', '',
             '1200', '600', '580', '20', 'True', 'True']
        ])

        response = self.client.post(
            '/api/polling-booths/bulk-upload/',
            {'file': csv_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_upload_with_invalid_state_code(self):
        """Test upload with invalid state code"""
        self.client.force_authenticate(user=self.admin_user)

        csv_file = self.create_csv_file([
            ['001', 'Test Booth', 'XX', 'TN001', 'TN001', 'School',
             '123 Main St', 'Area 1', '', '', '', '',
             '1000', '500', '490', '10', 'True', 'True']
        ])

        response = self.client.post(
            '/api/polling-booths/bulk-upload/',
            {'file': csv_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['failed_count'], 1)
        self.assertGreater(len(response.data['errors']), 0)
        self.assertIn('state_code', response.data['errors'][0]['error'])

    def test_bulk_upload_missing_required_columns(self):
        """Test upload with missing required columns"""
        self.client.force_authenticate(user=self.admin_user)

        # Create CSV with missing columns
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['booth_number', 'name'])  # Missing required columns
        writer.writerow(['001', 'Test Booth'])

        output.seek(0)
        csv_file = io.BytesIO(output.getvalue().encode('utf-8'))
        csv_file.name = 'test.csv'

        response = self.client.post(
            '/api/polling-booths/bulk-upload/',
            {'file': csv_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required columns', response.data['error'])

    def test_download_template(self):
        """Test template download"""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get('/api/polling-booths/template/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])

    def test_data_isolation_for_admin(self):
        """Test data isolation - admin sees only their state"""
        # Create booths in different states
        other_state = State.objects.create(name='Kerala', code='KL')
        other_district = District.objects.create(
            state=other_state,
            name='Kochi',
            code='KL001'
        )
        other_constituency = Constituency.objects.create(
            state=other_state,
            district=other_district,
            name='Kochi',
            code='KL001',
            number=1
        )

        # Booth in admin's state
        PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Booth in TN'
        )

        # Booth in other state
        PollingBooth.objects.create(
            state=other_state,
            district=other_district,
            constituency=other_constituency,
            booth_number='001',
            name='Booth in Kerala'
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/polling-booths/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin should only see booth in their state
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Booth in TN')

    def test_update_booth_permission(self):
        """Test that managers can update booths"""
        booth = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Original Name',
            total_voters=1000
        )

        self.client.force_authenticate(user=self.manager_user)
        response = self.client.patch(
            f'/api/polling-booths/{booth.id}/',
            {'total_voters': 1200},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booth.refresh_from_db()
        self.assertEqual(booth.total_voters, 1200)

    def test_delete_booth_permission(self):
        """Test that managers can delete booths"""
        booth = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Test Booth'
        )

        self.client.force_authenticate(user=self.manager_user)
        response = self.client.delete(f'/api/polling-booths/{booth.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PollingBooth.objects.count(), 0)

    def test_get_booth_stats(self):
        """Test booth statistics endpoint"""
        # Create test booths
        PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Booth 1',
            total_voters=1000,
            is_active=True,
            is_accessible=True
        )
        PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='002',
            name='Booth 2',
            total_voters=1500,
            is_active=True,
            is_accessible=False
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get('/api/polling-booths/stats/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_booths'], 2)
        self.assertEqual(response.data['active_booths'], 2)
        self.assertEqual(response.data['accessible_booths'], 1)
        self.assertEqual(response.data['total_voters'], 2500)
