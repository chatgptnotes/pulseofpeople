"""
Unit tests for validators
Tests all input validation and sanitization functions
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from api.validators import (
    validate_phone_number, validate_email, validate_name,
    validate_address, sanitize_html, sanitize_text_input,
    validate_pincode, validate_voter_id, validate_aadhar_number,
    validate_constituency_code, validate_booth_number,
    validate_latitude, validate_longitude, validate_sentiment_score,
    validate_age, validate_url
)


class PhoneValidatorTest(TestCase):
    """Test phone number validation"""

    def test_valid_indian_phone_10_digits(self):
        """Test valid 10-digit Indian phone"""
        try:
            validate_phone_number('9876543210')
            validate_phone_number('8012345678')
            validate_phone_number('7123456789')
        except ValidationError:
            self.fail('Valid phone number failed validation')

    def test_valid_indian_phone_with_91(self):
        """Test valid phone with country code"""
        try:
            validate_phone_number('919876543210')
            validate_phone_number('+919876543210')
        except ValidationError:
            self.fail('Valid phone number with country code failed validation')

    def test_valid_phone_with_formatting(self):
        """Test phone with spaces and dashes"""
        try:
            validate_phone_number('98765 43210')
            validate_phone_number('9876-543-210')
            validate_phone_number('(987) 654-3210')
        except ValidationError:
            self.fail('Valid formatted phone number failed validation')

    def test_invalid_phone_too_short(self):
        """Test invalid phone - too short"""
        with self.assertRaises(ValidationError):
            validate_phone_number('12345')

    def test_invalid_phone_wrong_start(self):
        """Test invalid phone - doesn't start with 6-9"""
        with self.assertRaises(ValidationError):
            validate_phone_number('1234567890')
        with self.assertRaises(ValidationError):
            validate_phone_number('5234567890')

    def test_invalid_phone_letters(self):
        """Test invalid phone - contains letters"""
        with self.assertRaises(ValidationError):
            validate_phone_number('987654321a')


class EmailValidatorTest(TestCase):
    """Test email validation"""

    def test_valid_emails(self):
        """Test valid email addresses"""
        self.assertTrue(validate_email('test@example.com'))
        self.assertTrue(validate_email('user.name@domain.co.in'))
        self.assertTrue(validate_email('firstname+lastname@company.org'))

    def test_invalid_emails(self):
        """Test invalid email addresses"""
        self.assertFalse(validate_email('notanemail'))
        self.assertFalse(validate_email('@example.com'))
        self.assertFalse(validate_email('user@'))
        self.assertFalse(validate_email(''))


class NameValidatorTest(TestCase):
    """Test name validation"""

    def test_valid_names(self):
        """Test valid names"""
        try:
            validate_name('John Doe')
            validate_name("O'Brien")
            validate_name('Mary-Jane')
            validate_name('Dr. Smith')
        except ValidationError:
            self.fail('Valid name failed validation')

    def test_invalid_name_too_short(self):
        """Test name too short"""
        with self.assertRaises(ValidationError):
            validate_name('A')

    def test_invalid_name_empty(self):
        """Test empty name"""
        with self.assertRaises(ValidationError):
            validate_name('')

    def test_invalid_name_special_chars(self):
        """Test name with invalid special characters"""
        with self.assertRaises(ValidationError):
            validate_name('John@Doe')
        with self.assertRaises(ValidationError):
            validate_name('User<script>')


class AddressValidatorTest(TestCase):
    """Test address validation"""

    def test_valid_address(self):
        """Test valid address"""
        try:
            validate_address('123 Main St, City, State, 600001')
        except ValidationError:
            self.fail('Valid address failed validation')

    def test_address_too_short(self):
        """Test address too short"""
        with self.assertRaises(ValidationError):
            validate_address('123')

    def test_address_with_xss(self):
        """Test address with XSS attempt"""
        with self.assertRaises(ValidationError):
            validate_address('123 Main <script>alert("xss")</script>')
        with self.assertRaises(ValidationError):
            validate_address('Address with javascript:alert(1)')


class HTMLSanitizerTest(TestCase):
    """Test HTML sanitization"""

    def test_sanitize_removes_scripts(self):
        """Test script tags are removed"""
        dirty = '<p>Hello</p><script>alert("xss")</script>'
        clean = sanitize_html(dirty)
        self.assertNotIn('<script>', clean)
        self.assertIn('Hello', clean)

    def test_sanitize_removes_dangerous_attributes(self):
        """Test dangerous attributes are removed"""
        dirty = '<a href="#" onclick="alert(1)">Link</a>'
        clean = sanitize_html(dirty)
        self.assertNotIn('onclick', clean)

    def test_sanitize_allows_safe_tags(self):
        """Test safe tags are preserved"""
        safe = '<p>Hello <strong>world</strong></p>'
        clean = sanitize_html(safe)
        self.assertIn('<strong>', clean)


class TextSanitizerTest(TestCase):
    """Test text sanitization"""

    def test_sanitize_removes_all_html(self):
        """Test all HTML is removed from text"""
        dirty = 'Hello <b>world</b>'
        clean = sanitize_text_input(dirty)
        self.assertEqual(clean, 'Hello world')

    def test_sanitize_removes_excessive_whitespace(self):
        """Test excessive whitespace is normalized"""
        dirty = 'Hello    world\n\n\ntest'
        clean = sanitize_text_input(dirty)
        self.assertEqual(clean, 'Hello world test')


class PincodeValidatorTest(TestCase):
    """Test PIN code validation"""

    def test_valid_pincode(self):
        """Test valid Indian PIN code"""
        try:
            validate_pincode('600001')
            validate_pincode('110001')
        except ValidationError:
            self.fail('Valid PIN code failed validation')

    def test_invalid_pincode_length(self):
        """Test invalid PIN code length"""
        with self.assertRaises(ValidationError):
            validate_pincode('1234')
        with self.assertRaises(ValidationError):
            validate_pincode('1234567')

    def test_invalid_pincode_letters(self):
        """Test PIN code with letters"""
        with self.assertRaises(ValidationError):
            validate_pincode('60000A')


class VoterIDValidatorTest(TestCase):
    """Test Voter ID validation"""

    def test_valid_voter_id(self):
        """Test valid voter ID"""
        try:
            validate_voter_id('ABC1234567')
            validate_voter_id('xyz9876543')  # Should convert to uppercase
        except ValidationError:
            self.fail('Valid voter ID failed validation')

    def test_invalid_voter_id_format(self):
        """Test invalid voter ID format"""
        with self.assertRaises(ValidationError):
            validate_voter_id('12345678')  # No letters
        with self.assertRaises(ValidationError):
            validate_voter_id('ABCD123456')  # Too many letters


class AadharValidatorTest(TestCase):
    """Test Aadhar number validation"""

    def test_valid_aadhar(self):
        """Test valid Aadhar number"""
        try:
            validate_aadhar_number('123456789012')
            validate_aadhar_number('1234 5678 9012')  # With spaces
        except ValidationError:
            self.fail('Valid Aadhar number failed validation')

    def test_invalid_aadhar_length(self):
        """Test invalid Aadhar length"""
        with self.assertRaises(ValidationError):
            validate_aadhar_number('12345')


class ConstituencyCodeValidatorTest(TestCase):
    """Test constituency code validation"""

    def test_valid_constituency_code(self):
        """Test valid constituency code"""
        try:
            validate_constituency_code('TN-001')
            validate_constituency_code('MH-045')
        except ValidationError:
            self.fail('Valid constituency code failed validation')

    def test_invalid_constituency_code_format(self):
        """Test invalid constituency code format"""
        with self.assertRaises(ValidationError):
            validate_constituency_code('TN001')  # Missing dash
        with self.assertRaises(ValidationError):
            validate_constituency_code('TN-1')  # Too few digits


class BoothNumberValidatorTest(TestCase):
    """Test booth number validation"""

    def test_valid_booth_number(self):
        """Test valid booth numbers"""
        try:
            validate_booth_number('001')
            validate_booth_number('123')
            validate_booth_number('45A')
            validate_booth_number('6B')
        except ValidationError:
            self.fail('Valid booth number failed validation')

    def test_invalid_booth_number(self):
        """Test invalid booth numbers"""
        with self.assertRaises(ValidationError):
            validate_booth_number('ABC')  # Only letters
        with self.assertRaises(ValidationError):
            validate_booth_number('1AB')  # Multiple letters


class CoordinateValidatorTest(TestCase):
    """Test latitude/longitude validation"""

    def test_valid_latitude(self):
        """Test valid latitudes"""
        try:
            validate_latitude(13.0827)  # Chennai
            validate_latitude(-90)
            validate_latitude(90)
            validate_latitude(0)
        except ValidationError:
            self.fail('Valid latitude failed validation')

    def test_invalid_latitude(self):
        """Test invalid latitudes"""
        with self.assertRaises(ValidationError):
            validate_latitude(100)
        with self.assertRaises(ValidationError):
            validate_latitude(-100)

    def test_valid_longitude(self):
        """Test valid longitudes"""
        try:
            validate_longitude(80.2707)  # Chennai
            validate_longitude(-180)
            validate_longitude(180)
            validate_longitude(0)
        except ValidationError:
            self.fail('Valid longitude failed validation')

    def test_invalid_longitude(self):
        """Test invalid longitudes"""
        with self.assertRaises(ValidationError):
            validate_longitude(200)
        with self.assertRaises(ValidationError):
            validate_longitude(-200)


class SentimentScoreValidatorTest(TestCase):
    """Test sentiment score validation"""

    def test_valid_sentiment_score(self):
        """Test valid sentiment scores"""
        try:
            validate_sentiment_score(0.0)
            validate_sentiment_score(0.5)
            validate_sentiment_score(1.0)
        except ValidationError:
            self.fail('Valid sentiment score failed validation')

    def test_invalid_sentiment_score(self):
        """Test invalid sentiment scores"""
        with self.assertRaises(ValidationError):
            validate_sentiment_score(-0.1)
        with self.assertRaises(ValidationError):
            validate_sentiment_score(1.1)


class AgeValidatorTest(TestCase):
    """Test age validation"""

    def test_valid_age(self):
        """Test valid ages"""
        try:
            validate_age(18)
            validate_age(50)
            validate_age(120)
        except ValidationError:
            self.fail('Valid age failed validation')

    def test_invalid_age_too_young(self):
        """Test age too young"""
        with self.assertRaises(ValidationError):
            validate_age(17)

    def test_invalid_age_too_old(self):
        """Test age too old"""
        with self.assertRaises(ValidationError):
            validate_age(121)


class URLValidatorTest(TestCase):
    """Test URL validation"""

    def test_valid_urls(self):
        """Test valid URLs"""
        try:
            validate_url('https://example.com')
            validate_url('http://localhost:8000')
            validate_url('https://sub.domain.co.in/path')
        except ValidationError:
            self.fail('Valid URL failed validation')

    def test_invalid_urls(self):
        """Test invalid URLs"""
        with self.assertRaises(ValidationError):
            validate_url('not-a-url')
        with self.assertRaises(ValidationError):
            validate_url('ftp://example.com')  # Wrong protocol
