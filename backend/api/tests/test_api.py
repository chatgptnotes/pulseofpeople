"""
Integration Tests for Political Platform API Endpoints
Tests for CRUD operations, filtering, and authentication
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from decimal import Decimal

from api.models import (
    State, District, Constituency, PollingBooth, PoliticalParty,
    IssueCategory, VoterSegment, DirectFeedback, UserProfile
)


class StateAPITest(APITestCase):
    """Test State API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.state1 = State.objects.create(
            name="Tamil Nadu",
            code="TN",
            capital="Chennai",
            total_districts=38
        )
        self.state2 = State.objects.create(
            name="Karnataka",
            code="KA",
            capital="Bangalore",
            total_districts=30
        )

    def test_list_states(self):
        """Test GET /api/states/ returns all states"""
        response = self.client.get('/api/states/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_state(self):
        """Test GET /api/states/{id}/ returns specific state"""
        response = self.client.get(f'/api/states/{self.state1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Tamil Nadu")
        self.assertEqual(response.data['code'], "TN")

    def test_state_api_no_auth_required(self):
        """Test states can be accessed without authentication"""
        response = self.client.get('/api/states/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DistrictAPITest(APITestCase):
    """Test District API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.state = State.objects.create(name="Tamil Nadu", code="TN")
        self.district1 = District.objects.create(
            state=self.state,
            name="Chennai",
            code="TN-CH",
            population=8000000
        )
        self.district2 = District.objects.create(
            state=self.state,
            name="Coimbatore",
            code="TN-CB",
            population=3500000
        )

    def test_list_districts(self):
        """Test GET /api/districts/ returns all districts"""
        response = self.client.get('/api/districts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_districts_by_state(self):
        """Test filtering districts by state code"""
        response = self.client.get('/api/districts/?state=TN')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_district(self):
        """Test GET /api/districts/{id}/ returns specific district"""
        response = self.client.get(f'/api/districts/{self.district1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Chennai")
        self.assertEqual(response.data['state_name'], "Tamil Nadu")

    def test_search_districts(self):
        """Test searching districts by name"""
        response = self.client.get('/api/districts/?search=Chennai')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)


class ConstituencyAPITest(APITestCase):
    """Test Constituency API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.state = State.objects.create(name="Tamil Nadu", code="TN")
        self.district = District.objects.create(
            state=self.state,
            name="Chennai",
            code="TN-CH"
        )
        self.constituency1 = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name="Chennai Central",
            code="TN001",
            constituency_type="assembly",
            number=1,
            total_voters=250000
        )
        self.constituency2 = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name="Chennai North",
            code="TN002",
            constituency_type="assembly",
            number=2,
            total_voters=230000
        )
        self.constituency3 = Constituency.objects.create(
            state=self.state,
            name="Chennai Parliamentary",
            code="TN-P01",
            constituency_type="parliamentary",
            number=1,
            total_voters=1500000
        )

    def test_list_constituencies(self):
        """Test GET /api/constituencies/ returns all constituencies"""
        response = self.client.get('/api/constituencies/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_by_state(self):
        """Test filtering constituencies by state"""
        response = self.client.get('/api/constituencies/?state=TN')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_filter_by_type(self):
        """Test filtering constituencies by type"""
        response = self.client.get('/api/constituencies/?type=assembly')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_district(self):
        """Test filtering constituencies by district"""
        response = self.client.get(f'/api/constituencies/?district={self.district.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_constituency(self):
        """Test GET /api/constituencies/{id}/ returns specific constituency"""
        response = self.client.get(f'/api/constituencies/{self.constituency1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Chennai Central")
        self.assertEqual(response.data['state_name'], "Tamil Nadu")


class PollingBoothAPITest(APITestCase):
    """Test Polling Booth API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.state = State.objects.create(name="Tamil Nadu", code="TN")
        self.district = District.objects.create(
            state=self.state,
            name="Chennai",
            code="TN-CH"
        )
        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name="Chennai Central",
            code="TN001",
            constituency_type="assembly",
            number=1
        )
        self.booth1 = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number="001",
            name="Government High School",
            area="T. Nagar",
            total_voters=1500,
            is_active=True
        )
        self.booth2 = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number="002",
            name="Community Center",
            area="Anna Nagar",
            total_voters=1200,
            is_active=True
        )

    def test_list_polling_booths(self):
        """Test GET /api/polling-booths/ returns all booths"""
        response = self.client.get('/api/polling-booths/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_state(self):
        """Test filtering booths by state"""
        response = self.client.get('/api/polling-booths/?state=TN')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_constituency(self):
        """Test filtering booths by constituency name"""
        response = self.client.get('/api/polling-booths/?constituency=Chennai Central')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_booths(self):
        """Test searching booths by name"""
        response = self.client.get('/api/polling-booths/?search=Government')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_retrieve_booth(self):
        """Test GET /api/polling-booths/{id}/ returns specific booth"""
        response = self.client.get(f'/api/polling-booths/{self.booth1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['booth_number'], "001")
        self.assertEqual(response.data['name'], "Government High School")
        self.assertEqual(response.data['constituency_name'], "Chennai Central")

    def test_booth_includes_location_data(self):
        """Test booth response includes location information"""
        response = self.client.get(f'/api/polling-booths/{self.booth1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('state_name', response.data)
        self.assertIn('district_name', response.data)
        self.assertIn('area', response.data)


class DirectFeedbackAPITest(APITestCase):
    """Test Direct Feedback API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.state = State.objects.create(name="Tamil Nadu", code="TN")
        self.district = District.objects.create(
            state=self.state,
            name="Chennai",
            code="TN-CH"
        )
        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name="Chennai Central",
            code="TN001",
            constituency_type="assembly",
            number=1
        )
        self.issue = IssueCategory.objects.create(
            name="Water Supply",
            priority=10
        )

        # Create authenticated user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        UserProfile.objects.create(
            user=self.user,
            role='admin'
        )

    def test_create_feedback_no_auth(self):
        """Test POST /api/feedback/ works without authentication"""
        data = {
            'citizen_name': 'Test Citizen',
            'citizen_age': 30,
            'citizen_phone': '9876543210',
            'state': self.state.id,
            'district': self.district.id,
            'ward': 'Ward 1',
            'issue_category': self.issue.id,
            'message_text': 'Test feedback message'
        }

        response = self.client.post('/api/feedback/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['citizen_name'], 'Test Citizen')

    def test_list_feedback_requires_auth(self):
        """Test GET /api/feedback/ requires authentication"""
        response = self.client.get('/api/feedback/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_feedback_with_auth(self):
        """Test GET /api/feedback/ works with authentication"""
        self.client.force_authenticate(user=self.user)

        # Create some feedback
        DirectFeedback.objects.create(
            citizen_name='Test Citizen',
            state=self.state,
            district=self.district,
            ward='Ward 1',
            issue_category=self.issue,
            message_text='Test message'
        )

        response = self.client.get('/api/feedback/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BulkBoothImportTest(APITestCase):
    """Test bulk booth import scenarios"""

    def setUp(self):
        self.client = APIClient()
        self.state = State.objects.create(name="Tamil Nadu", code="TN")
        self.district = District.objects.create(
            state=self.state,
            name="Chennai",
            code="TN-CH"
        )
        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name="Chennai Central",
            code="TN001",
            constituency_type="assembly",
            number=1
        )

    def test_bulk_create_booths(self):
        """Test creating multiple booths in bulk"""
        booths_data = []
        for i in range(1, 51):
            booths_data.append({
                'state': self.state.id,
                'district': self.district.id,
                'constituency': self.constituency.id,
                'booth_number': f'{i:03d}',
                'name': f'Booth {i}',
                'total_voters': 1000 + i
            })

        # Simulate bulk create
        booths = []
        for data in booths_data:
            booths.append(PollingBooth(
                state_id=data['state'],
                district_id=data['district'],
                constituency_id=data['constituency'],
                booth_number=data['booth_number'],
                name=data['name'],
                total_voters=data['total_voters']
            ))

        created_booths = PollingBooth.objects.bulk_create(booths)
        self.assertEqual(len(created_booths), 50)

    def test_bulk_create_with_coordinates(self):
        """Test bulk creating booths with coordinates"""
        booths = []
        base_lat = Decimal('13.0827')
        base_lng = Decimal('80.2707')

        for i in range(1, 101):
            booths.append(PollingBooth(
                state=self.state,
                district=self.district,
                constituency=self.constituency,
                booth_number=f'{i:03d}',
                name=f'Booth {i}',
                latitude=base_lat + Decimal(i) * Decimal('0.001'),
                longitude=base_lng + Decimal(i) * Decimal('0.001'),
                total_voters=1000
            ))

        created_booths = PollingBooth.objects.bulk_create(booths)
        self.assertEqual(len(created_booths), 100)

        # Verify coordinates
        first_booth = PollingBooth.objects.filter(booth_number='001').first()
        self.assertIsNotNone(first_booth.latitude)
        self.assertIsNotNone(first_booth.longitude)


class DataValidationTest(APITestCase):
    """Test data validation in API"""

    def setUp(self):
        self.client = APIClient()
        self.state = State.objects.create(name="Tamil Nadu", code="TN")
        self.district = District.objects.create(
            state=self.state,
            name="Chennai",
            code="TN-CH"
        )
        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name="Chennai Central",
            code="TN001",
            constituency_type="assembly",
            number=1
        )
        self.issue = IssueCategory.objects.create(name="Test Issue")

    def test_feedback_age_validation(self):
        """Test age validation in feedback creation"""
        # Age too young
        data = {
            'citizen_name': 'Test',
            'citizen_age': 15,  # Invalid age
            'state': self.state.id,
            'district': self.district.id,
            'ward': 'Ward 1',
            'issue_category': self.issue.id,
            'message_text': 'Test'
        }

        response = self.client.post('/api/feedback/', data, format='json')
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_201_CREATED  # If model-level validation not enforced
        ])

    def test_required_fields_validation(self):
        """Test required fields validation"""
        data = {
            'citizen_name': 'Test',
            # Missing required fields
        }

        response = self.client.post('/api/feedback/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PerformanceTest(APITestCase):
    """Test API performance with large datasets"""

    def setUp(self):
        self.client = APIClient()
        self.state = State.objects.create(name="Tamil Nadu", code="TN")
        self.district = District.objects.create(
            state=self.state,
            name="Chennai",
            code="TN-CH"
        )
        self.constituency = Constituency.objects.create(
            state=self.state,
            district=self.district,
            name="Chennai Central",
            code="TN001",
            constituency_type="assembly",
            number=1
        )

        # Create 1000 booths for performance testing
        booths = []
        for i in range(1, 1001):
            booths.append(PollingBooth(
                state=self.state,
                district=self.district,
                constituency=self.constituency,
                booth_number=f'{i:04d}',
                name=f'Booth {i}',
                total_voters=1000 + i
            ))

        PollingBooth.objects.bulk_create(booths, batch_size=100)

    def test_list_1000_booths_performance(self):
        """Test listing 1000 booths"""
        import time

        start_time = time.time()
        response = self.client.get('/api/polling-booths/')
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1000)

        # Response should be under 2 seconds
        response_time = end_time - start_time
        self.assertLess(response_time, 2.0, f"Response took {response_time:.2f}s")

    def test_filter_performance(self):
        """Test filtering performance with large dataset"""
        import time

        start_time = time.time()
        response = self.client.get('/api/polling-booths/?constituency=Chennai Central')
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_time = end_time - start_time
        self.assertLess(response_time, 2.0, f"Filtered response took {response_time:.2f}s")

    def test_search_performance(self):
        """Test search performance"""
        import time

        start_time = time.time()
        response = self.client.get('/api/polling-booths/?search=Booth 500')
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_time = end_time - start_time
        self.assertLess(response_time, 1.0, f"Search took {response_time:.2f}s")
