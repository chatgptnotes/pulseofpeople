"""
Tests for Political Platform Serializers
Tests data validation, serialization, and edge cases
"""
from django.test import TestCase
from rest_framework.exceptions import ValidationError
from decimal import Decimal

from api.models import (
    State, District, Constituency, PollingBooth, IssueCategory,
    VoterSegment, DirectFeedback
)
from api.political_serializers import (
    StateSerializer, DistrictSerializer, ConstituencySerializer,
    PollingBoothSerializer, DirectFeedbackCreateSerializer,
    IssueCategorySerializer, VoterSegmentSerializer
)


class StateSerializerTest(TestCase):
    """Test StateSerializer"""

    def setUp(self):
        self.state_data = {
            'name': 'Tamil Nadu',
            'code': 'TN',
            'capital': 'Chennai',
            'region': 'South',
            'total_districts': 38,
            'total_constituencies': 234
        }

    def test_serialize_state(self):
        """Test serializing a state object"""
        state = State.objects.create(**self.state_data)
        serializer = StateSerializer(state)

        self.assertEqual(serializer.data['name'], 'Tamil Nadu')
        self.assertEqual(serializer.data['code'], 'TN')
        self.assertEqual(serializer.data['capital'], 'Chennai')

    def test_deserialize_state(self):
        """Test deserializing state data"""
        serializer = StateSerializer(data=self.state_data)
        self.assertTrue(serializer.is_valid())

        state = serializer.save()
        self.assertEqual(state.name, 'Tamil Nadu')
        self.assertEqual(state.code, 'TN')


class DistrictSerializerTest(TestCase):
    """Test DistrictSerializer"""

    def setUp(self):
        self.state = State.objects.create(name='Tamil Nadu', code='TN')
        self.district_data = {
            'state': self.state.id,
            'name': 'Chennai',
            'code': 'TN-CH',
            'headquarters': 'Chennai',
            'population': 8000000,
            'area_sq_km': '426.00',
            'total_wards': 200
        }

    def test_serialize_district(self):
        """Test serializing a district object"""
        district = District.objects.create(
            state=self.state,
            name='Chennai',
            code='TN-CH',
            population=8000000
        )
        serializer = DistrictSerializer(district)

        self.assertEqual(serializer.data['name'], 'Chennai')
        self.assertEqual(serializer.data['state_name'], 'Tamil Nadu')
        self.assertEqual(serializer.data['state_code'], 'TN')

    def test_deserialize_district(self):
        """Test deserializing district data"""
        serializer = DistrictSerializer(data=self.district_data)
        self.assertTrue(serializer.is_valid())

        district = serializer.save()
        self.assertEqual(district.name, 'Chennai')
        self.assertEqual(district.state, self.state)

    def test_district_includes_state_info(self):
        """Test that serialized district includes state information"""
        district = District.objects.create(
            state=self.state,
            name='Chennai',
            code='TN-CH'
        )
        serializer = DistrictSerializer(district)

        self.assertIn('state_name', serializer.data)
        self.assertIn('state_code', serializer.data)


class ConstituencySerializerTest(TestCase):
    """Test ConstituencySerializer"""

    def setUp(self):
        self.state = State.objects.create(name='Tamil Nadu', code='TN')
        self.district = District.objects.create(
            state=self.state,
            name='Chennai',
            code='TN-CH'
        )
        self.constituency_data = {
            'state': self.state.id,
            'district': self.district.id,
            'name': 'Chennai Central',
            'code': 'TN001',
            'constituency_type': 'assembly',
            'number': 1,
            'reserved_for': 'general',
            'total_voters': 250000,
            'total_wards': 50,
            'total_booths': 300
        }

    def test_serialize_constituency(self):
        """Test serializing a constituency object"""
        constituency = Constituency.objects.create(**{
            'state': self.state,
            'district': self.district,
            'name': 'Chennai Central',
            'code': 'TN001',
            'constituency_type': 'assembly',
            'number': 1
        })
        serializer = ConstituencySerializer(constituency)

        self.assertEqual(serializer.data['name'], 'Chennai Central')
        self.assertEqual(serializer.data['state_name'], 'Tamil Nadu')
        self.assertEqual(serializer.data['district_name'], 'Chennai')

    def test_deserialize_constituency(self):
        """Test deserializing constituency data"""
        serializer = ConstituencySerializer(data=self.constituency_data)
        self.assertTrue(serializer.is_valid())

        constituency = serializer.save()
        self.assertEqual(constituency.name, 'Chennai Central')
        self.assertEqual(constituency.number, 1)

    def test_constituency_type_validation(self):
        """Test constituency type must be valid"""
        invalid_data = self.constituency_data.copy()
        invalid_data['constituency_type'] = 'invalid_type'

        serializer = ConstituencySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())


class PollingBoothSerializerTest(TestCase):
    """Test PollingBoothSerializer"""

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
            name='Chennai Central',
            code='TN001',
            constituency_type='assembly',
            number=1
        )
        self.booth_data = {
            'state': self.state.id,
            'district': self.district.id,
            'constituency': self.constituency.id,
            'booth_number': '001',
            'name': 'Government High School',
            'building_name': 'Chennai Central Govt School',
            'address': '123 Main Street',
            'area': 'T. Nagar',
            'pincode': '600017',
            'latitude': '13.0827',
            'longitude': '80.2707',
            'total_voters': 1500,
            'male_voters': 750,
            'female_voters': 700,
            'other_voters': 50,
            'is_active': True,
            'is_accessible': True
        }

    def test_serialize_polling_booth(self):
        """Test serializing a polling booth object"""
        booth = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Government High School',
            total_voters=1500
        )
        serializer = PollingBoothSerializer(booth)

        self.assertEqual(serializer.data['booth_number'], '001')
        self.assertEqual(serializer.data['state_name'], 'Tamil Nadu')
        self.assertEqual(serializer.data['district_name'], 'Chennai')
        self.assertEqual(serializer.data['constituency_name'], 'Chennai Central')

    def test_deserialize_polling_booth(self):
        """Test deserializing polling booth data"""
        serializer = PollingBoothSerializer(data=self.booth_data)
        self.assertTrue(serializer.is_valid())

        booth = serializer.save()
        self.assertEqual(booth.booth_number, '001')
        self.assertEqual(booth.total_voters, 1500)

    def test_booth_with_coordinates(self):
        """Test booth serialization with coordinates"""
        booth = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Test Booth',
            latitude=Decimal('13.0827'),
            longitude=Decimal('80.2707')
        )
        serializer = PollingBoothSerializer(booth)

        self.assertEqual(str(serializer.data['latitude']), '13.08270000')
        self.assertEqual(str(serializer.data['longitude']), '80.27070000')

    def test_booth_metadata_field(self):
        """Test booth metadata field serialization"""
        booth = PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Test Booth',
            metadata={'facilities': ['wheelchair', 'parking']}
        )
        serializer = PollingBoothSerializer(booth)

        self.assertIn('facilities', serializer.data['metadata'])
        self.assertIn('wheelchair', serializer.data['metadata']['facilities'])


class DirectFeedbackSerializerTest(TestCase):
    """Test DirectFeedbackCreateSerializer"""

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
            name='Chennai Central',
            code='TN001',
            constituency_type='assembly',
            number=1
        )
        self.issue = IssueCategory.objects.create(
            name='Water Supply',
            priority=10
        )
        self.feedback_data = {
            'citizen_name': 'Rajesh Kumar',
            'citizen_age': 35,
            'citizen_phone': '9876543210',
            'citizen_email': 'rajesh@example.com',
            'state': self.state.id,
            'district': self.district.id,
            'constituency': self.constituency.id,
            'ward': 'Ward 42',
            'booth_number': '125',
            'detailed_location': 'Near Temple Street',
            'issue_category': self.issue.id,
            'message_text': 'Water supply is irregular',
            'expectations': 'Regular water supply twice a day'
        }

    def test_serialize_feedback(self):
        """Test serializing feedback data"""
        serializer = DirectFeedbackCreateSerializer(data=self.feedback_data)
        self.assertTrue(serializer.is_valid())

        feedback = serializer.save()
        self.assertEqual(feedback.citizen_name, 'Rajesh Kumar')
        self.assertEqual(feedback.citizen_age, 35)

    def test_age_validation_too_young(self):
        """Test age validation rejects age < 18"""
        invalid_data = self.feedback_data.copy()
        invalid_data['citizen_age'] = 15

        serializer = DirectFeedbackCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('citizen_age', serializer.errors)

    def test_age_validation_too_old(self):
        """Test age validation rejects age > 120"""
        invalid_data = self.feedback_data.copy()
        invalid_data['citizen_age'] = 125

        serializer = DirectFeedbackCreateSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('citizen_age', serializer.errors)

    def test_age_validation_valid_range(self):
        """Test age validation accepts valid ages"""
        valid_ages = [18, 25, 50, 75, 100, 120]

        for age in valid_ages:
            data = self.feedback_data.copy()
            data['citizen_age'] = age
            serializer = DirectFeedbackCreateSerializer(data=data)
            self.assertTrue(serializer.is_valid(), f"Age {age} should be valid")

    def test_required_fields(self):
        """Test required fields validation"""
        required_fields = ['citizen_name', 'state', 'district', 'ward',
                          'issue_category', 'message_text']

        for field in required_fields:
            data = self.feedback_data.copy()
            del data[field]

            serializer = DirectFeedbackCreateSerializer(data=data)
            self.assertFalse(serializer.is_valid())
            self.assertIn(field, serializer.errors)

    def test_optional_fields(self):
        """Test optional fields can be omitted"""
        minimal_data = {
            'citizen_name': 'Test Citizen',
            'state': self.state.id,
            'district': self.district.id,
            'ward': 'Ward 1',
            'issue_category': self.issue.id,
            'message_text': 'Test message'
        }

        serializer = DirectFeedbackCreateSerializer(data=minimal_data)
        self.assertTrue(serializer.is_valid())


class IssueCategorySerializerTest(TestCase):
    """Test IssueCategorySerializer"""

    def setUp(self):
        self.parent = IssueCategory.objects.create(
            name='Agriculture',
            description='Agricultural issues',
            priority=10
        )

    def test_serialize_category_with_subcategories(self):
        """Test serializing category with subcategories count"""
        child1 = IssueCategory.objects.create(
            name='Irrigation',
            parent=self.parent
        )
        child2 = IssueCategory.objects.create(
            name='Fertilizers',
            parent=self.parent
        )

        serializer = IssueCategorySerializer(self.parent)
        self.assertEqual(serializer.data['subcategories_count'], 2)

    def test_serialize_category_without_parent(self):
        """Test serializing top-level category"""
        serializer = IssueCategorySerializer(self.parent)
        self.assertIsNone(serializer.data['parent'])
        self.assertIsNone(serializer.data['parent_name'])


class CSVDataValidationTest(TestCase):
    """Test CSV data parsing and validation"""

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
            name='Chennai Central',
            code='TN001',
            constituency_type='assembly',
            number=1
        )

    def test_parse_booth_csv_row(self):
        """Test parsing a valid booth CSV row"""
        csv_row = {
            'booth_number': '001',
            'name': 'Government School',
            'area': 'T. Nagar',
            'latitude': '13.0827',
            'longitude': '80.2707',
            'total_voters': '1500'
        }

        booth = PollingBooth(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number=csv_row['booth_number'],
            name=csv_row['name'],
            area=csv_row['area'],
            latitude=Decimal(csv_row['latitude']),
            longitude=Decimal(csv_row['longitude']),
            total_voters=int(csv_row['total_voters'])
        )

        booth.save()
        self.assertEqual(booth.booth_number, '001')
        self.assertEqual(booth.total_voters, 1500)

    def test_handle_empty_coordinates(self):
        """Test handling empty coordinate values"""
        csv_row = {
            'booth_number': '001',
            'name': 'Test Booth',
            'latitude': '',
            'longitude': ''
        }

        booth = PollingBooth(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number=csv_row['booth_number'],
            name=csv_row['name'],
            latitude=None if csv_row['latitude'] == '' else Decimal(csv_row['latitude']),
            longitude=None if csv_row['longitude'] == '' else Decimal(csv_row['longitude'])
        )

        booth.save()
        self.assertIsNone(booth.latitude)
        self.assertIsNone(booth.longitude)

    def test_handle_invalid_number_format(self):
        """Test handling invalid number formats"""
        csv_row = {
            'total_voters': 'invalid'
        }

        with self.assertRaises(ValueError):
            int(csv_row['total_voters'])

    def test_coordinate_range_validation(self):
        """Test coordinate range validation"""
        # Valid coordinates
        valid_booth = PollingBooth(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='Valid Booth',
            latitude=Decimal('13.0827'),  # Valid for India
            longitude=Decimal('80.2707')
        )
        valid_booth.save()

        # Coordinates should be within valid ranges
        self.assertGreaterEqual(valid_booth.latitude, Decimal('-90'))
        self.assertLessEqual(valid_booth.latitude, Decimal('90'))
        self.assertGreaterEqual(valid_booth.longitude, Decimal('-180'))
        self.assertLessEqual(valid_booth.longitude, Decimal('180'))

    def test_duplicate_booth_number_detection(self):
        """Test detecting duplicate booth numbers in same constituency"""
        PollingBooth.objects.create(
            state=self.state,
            district=self.district,
            constituency=self.constituency,
            booth_number='001',
            name='First Booth'
        )

        # Try to create duplicate
        with self.assertRaises(Exception):  # IntegrityError
            PollingBooth.objects.create(
                state=self.state,
                district=self.district,
                constituency=self.constituency,
                booth_number='001',
                name='Duplicate Booth'
            )

    def test_batch_validation(self):
        """Test validating a batch of booth records"""
        batch_data = [
            {'booth_number': '001', 'name': 'Booth 1', 'total_voters': '1000'},
            {'booth_number': '002', 'name': 'Booth 2', 'total_voters': '1500'},
            {'booth_number': '003', 'name': 'Booth 3', 'total_voters': '1200'},
        ]

        errors = []
        valid_records = []

        for row in batch_data:
            try:
                # Validate required fields
                if not row.get('booth_number'):
                    errors.append({'row': row, 'error': 'Missing booth_number'})
                    continue

                if not row.get('name'):
                    errors.append({'row': row, 'error': 'Missing name'})
                    continue

                # Validate number format
                if row.get('total_voters'):
                    try:
                        int(row['total_voters'])
                    except ValueError:
                        errors.append({'row': row, 'error': 'Invalid total_voters format'})
                        continue

                valid_records.append(row)

            except Exception as e:
                errors.append({'row': row, 'error': str(e)})

        self.assertEqual(len(valid_records), 3)
        self.assertEqual(len(errors), 0)
