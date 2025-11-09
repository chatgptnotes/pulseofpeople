# API Test Suite - Pulse of People Platform

Comprehensive test suite for ward/booth features and political data management.

## Quick Start

```bash
cd backend
source venv/bin/activate

# Run all tests
python manage.py test api.tests

# Run specific test file
python manage.py test api.tests.test_models
python manage.py test api.tests.test_api
python manage.py test api.tests.test_serializers
```

## Test Structure

```
api/tests/
├── __init__.py                 # Test package initialization
├── test_models.py              # Model unit tests (39 tests)
├── test_api.py                 # API integration tests (30 tests)
├── test_serializers.py         # Serializer validation tests (45 tests)
└── README.md                   # This file
```

## Test Categories

### 1. Model Tests (39 tests)

**File:** `test_models.py`

Tests Django models for:
- State (7 tests)
- District (6 tests)
- Constituency (8 tests)
- PollingBooth (10 tests)
- IssueCategory (4 tests)
- VoterSegment (2 tests)
- DirectFeedback (5 tests)
- BoothAgent (2 tests)
- Bulk validation (5 tests)

**Run:** `python manage.py test api.tests.test_models`

### 2. API Integration Tests (30 tests)

**File:** `test_api.py`

Tests REST API endpoints:
- State endpoints (3 tests)
- District endpoints (4 tests)
- Constituency endpoints (5 tests)
- Polling booth endpoints (6 tests)
- Feedback endpoints (3 tests)
- Bulk operations (2 tests)
- Performance tests (5 tests)

**Run:** `python manage.py test api.tests.test_api`

### 3. Serializer Tests (45 tests)

**File:** `test_serializers.py`

Tests data validation:
- State serializer (2 tests)
- District serializer (3 tests)
- Constituency serializer (3 tests)
- Polling booth serializer (4 tests)
- Feedback serializer (7 tests)
- CSV validation (10 tests)

**Run:** `python manage.py test api.tests.test_serializers`

## Coverage Report

Generate coverage report:

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run manage.py test api.tests

# View report
coverage report

# Generate HTML report
coverage html
open htmlcov/index.html
```

## Writing New Tests

### Test Template

```python
from django.test import TestCase
from api.models import YourModel

class YourModelTest(TestCase):
    """Test YourModel functionality"""

    def setUp(self):
        """Set up test data"""
        self.instance = YourModel.objects.create(
            field1='value1',
            field2='value2'
        )

    def test_your_feature(self):
        """Test description"""
        # Arrange
        expected_value = 'expected'

        # Act
        actual_value = self.instance.field1

        # Assert
        self.assertEqual(actual_value, expected_value)
```

### API Test Template

```python
from rest_framework.test import APITestCase
from rest_framework import status

class YourAPITest(APITestCase):
    """Test Your API endpoints"""

    def setUp(self):
        """Set up test data"""
        # Create test objects
        pass

    def test_list_endpoint(self):
        """Test GET /api/your-endpoint/"""
        response = self.client.get('/api/your-endpoint/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Best Practices

1. **Descriptive Names:** Test names should describe what they test
2. **AAA Pattern:** Arrange, Act, Assert
3. **Isolation:** Tests should not depend on each other
4. **Fast:** Keep tests fast by using in-memory database
5. **Coverage:** Aim for 80%+ code coverage
6. **Edge Cases:** Test boundary conditions and error cases

## Debugging Tests

```bash
# Run with verbose output
python manage.py test api.tests --verbosity=2

# Run with timing
python manage.py test api.tests --timing

# Run single test
python manage.py test api.tests.test_models.StateModelTest.test_state_creation

# Keep test database
python manage.py test api.tests --keepdb

# Run with Python debugger
python manage.py test api.tests --pdb
```

## Current Status

⚠️ **BLOCKED:** Tests cannot run due to import errors in application code.

**Fix Required:**
1. Update `/Users/murali/1backup/Pulseofpeople8thNov/pulseofpeople/backend/api/views/legacy.py`
2. Fix import statements for UserSerializer, UserProfileSerializer, etc.

See `QA_REPORT.md` for detailed analysis.

## Test Data

Tests create temporary data in an in-memory SQLite database:
- 3 states
- 5 districts
- 10 constituencies
- Up to 1000 polling booths (for performance tests)
- Sample feedback submissions

All data is automatically cleaned up after tests complete.

## Performance Targets

| Operation | Dataset Size | Target Time |
|-----------|--------------|-------------|
| List booths | 1,000 | < 2.0s |
| Filter booths | 1,000 | < 2.0s |
| Search booths | 1,000 | < 1.0s |
| Bulk create | 100 | < 1.0s |

## Contributing

When adding new features:
1. Write tests first (TDD)
2. Ensure tests pass
3. Check coverage doesn't decrease
4. Update this README if needed

## Resources

- [Django Testing Documentation](https://docs.djangoproject.com/en/5.0/topics/testing/)
- [DRF Testing Documentation](https://www.django-rest-framework.org/api-guide/testing/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
