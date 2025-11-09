"""
Input validation and sanitization utilities
Comprehensive validators for all user inputs
"""
import re
import os
import magic
import bleach
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.translation import gettext_lazy as _


class IndianPhoneValidator:
    """Validator for Indian phone numbers"""

    def __call__(self, value):
        if not value:
            return

        # Remove spaces, dashes, and other formatting
        cleaned = re.sub(r'[\s\-\(\)]', '', str(value))

        # Check if it starts with +91 or 91 or is 10 digits
        patterns = [
            r'^\+91[6-9]\d{9}$',  # +91 followed by 10 digits starting with 6-9
            r'^91[6-9]\d{9}$',     # 91 followed by 10 digits
            r'^[6-9]\d{9}$',       # 10 digits starting with 6-9
        ]

        if not any(re.match(pattern, cleaned) for pattern in patterns):
            raise ValidationError(
                _('Enter a valid Indian phone number (10 digits starting with 6-9)'),
                code='invalid_phone'
            )


def validate_phone_number(phone):
    """Validate Indian phone number format"""
    validator = IndianPhoneValidator()
    validator(phone)
    return True


def validate_email(email):
    """Validate email format"""
    if not email:
        return False

    validator = EmailValidator()
    try:
        validator(email)
        return True
    except ValidationError:
        return False


def validate_name(name):
    """Validate name fields - only letters, spaces, hyphens, and apostrophes"""
    if not name:
        raise ValidationError(_('Name cannot be empty'))

    if len(name) < 2:
        raise ValidationError(_('Name must be at least 2 characters'))

    if len(name) > 200:
        raise ValidationError(_('Name cannot exceed 200 characters'))

    # Allow only letters, spaces, hyphens, apostrophes, and dots (for middle initials)
    if not re.match(r"^[a-zA-Z\s\-\'\.]+$", name):
        raise ValidationError(
            _('Name can only contain letters, spaces, hyphens, apostrophes, and dots')
        )

    return True


def validate_address(address):
    """Validate address fields"""
    if not address:
        return True  # Address is optional in most cases

    if len(address) < 5:
        raise ValidationError(_('Address must be at least 5 characters'))

    if len(address) > 1000:
        raise ValidationError(_('Address cannot exceed 1000 characters'))

    # Check for potentially malicious content
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onclick=',
        r'<iframe',
    ]

    address_lower = address.lower()
    for pattern in dangerous_patterns:
        if re.search(pattern, address_lower):
            raise ValidationError(_('Address contains invalid content'))

    return True


def sanitize_html(text):
    """Remove dangerous HTML/JavaScript from text"""
    if not text:
        return text

    # Allow only safe HTML tags
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'ul', 'ol', 'li']
    allowed_attributes = {'a': ['href', 'title']}

    # Clean the HTML
    cleaned = bleach.clean(
        text,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )

    return cleaned


def sanitize_text_input(text):
    """Sanitize plain text input - remove all HTML"""
    if not text:
        return text

    # Remove all HTML tags
    cleaned = bleach.clean(text, tags=[], strip=True)

    # Remove excessive whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    return cleaned


def validate_file_upload(file):
    """
    Comprehensive file upload validation
    Checks: file type, size, content, malware
    """
    if not file:
        raise ValidationError(_('No file provided'))

    # 1. Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_size:
        raise ValidationError(
            _('File too large. Maximum size is 10MB. Your file is %(size)s MB'),
            params={'size': round(file.size / (1024 * 1024), 2)},
            code='file_too_large'
        )

    # 2. Check file extension
    allowed_extensions = {
        '.jpg', '.jpeg', '.png', '.gif',  # Images
        '.pdf',  # Documents
        '.doc', '.docx',  # Word
        '.xls', '.xlsx',  # Excel
        '.csv',  # Data
    }

    ext = os.path.splitext(file.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            _('File type not allowed. Allowed types: %(types)s'),
            params={'types': ', '.join(allowed_extensions)},
            code='invalid_file_type'
        )

    # 3. Check MIME type (actual file content)
    allowed_mime_types = {
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
    }

    # Read file content to check MIME type
    file.seek(0)  # Reset file pointer
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)  # Reset again for later use

    if mime not in allowed_mime_types:
        raise ValidationError(
            _('Invalid file content. Detected type: %(mime)s'),
            params={'mime': mime},
            code='invalid_mime_type'
        )

    # 4. Check for executable files and scripts
    dangerous_extensions = {
        '.exe', '.bat', '.cmd', '.sh', '.php', '.py', '.js',
        '.vbs', '.app', '.deb', '.rpm', '.dmg', '.pkg'
    }

    if ext in dangerous_extensions:
        raise ValidationError(
            _('Executable files are not allowed'),
            code='executable_not_allowed'
        )

    # 5. Check filename for dangerous patterns
    filename_lower = file.name.lower()
    dangerous_patterns = ['../', '..\\', '<', '>', '|', ':', '*', '?', '"']

    if any(pattern in filename_lower for pattern in dangerous_patterns):
        raise ValidationError(
            _('Filename contains invalid characters'),
            code='invalid_filename'
        )

    return True


def validate_json_field(data, required_fields=None):
    """Validate JSON field data"""
    if not isinstance(data, dict):
        raise ValidationError(_('Invalid JSON data format'))

    if required_fields:
        missing_fields = set(required_fields) - set(data.keys())
        if missing_fields:
            raise ValidationError(
                _('Missing required fields: %(fields)s'),
                params={'fields': ', '.join(missing_fields)}
            )

    return True


def validate_pincode(pincode):
    """Validate Indian PIN code"""
    if not pincode:
        return True  # Optional field

    # Indian PIN codes are 6 digits
    if not re.match(r'^\d{6}$', str(pincode)):
        raise ValidationError(
            _('Enter a valid 6-digit PIN code'),
            code='invalid_pincode'
        )

    return True


def validate_voter_id(voter_id):
    """Validate Indian Voter ID format"""
    if not voter_id:
        return True  # Optional field

    # Indian Voter ID: 3 letters + 7 digits
    if not re.match(r'^[A-Z]{3}\d{7}$', voter_id.upper()):
        raise ValidationError(
            _('Enter a valid Voter ID (e.g., ABC1234567)'),
            code='invalid_voter_id'
        )

    return True


def validate_aadhar_number(aadhar):
    """Validate Indian Aadhar number"""
    if not aadhar:
        return True  # Optional field

    # Remove spaces
    cleaned = re.sub(r'\s', '', str(aadhar))

    # Aadhar is 12 digits
    if not re.match(r'^\d{12}$', cleaned):
        raise ValidationError(
            _('Enter a valid 12-digit Aadhar number'),
            code='invalid_aadhar'
        )

    return True


def validate_constituency_code(code):
    """Validate constituency code format"""
    if not code:
        raise ValidationError(_('Constituency code cannot be empty'))

    # Format: STATE_CODE-NUMBER (e.g., TN-001, MH-045)
    if not re.match(r'^[A-Z]{2}-\d{3}$', code):
        raise ValidationError(
            _('Enter a valid constituency code (e.g., TN-001)'),
            code='invalid_constituency_code'
        )

    return True


def validate_booth_number(booth_number):
    """Validate polling booth number"""
    if not booth_number:
        raise ValidationError(_('Booth number cannot be empty'))

    # Booth numbers can be: 001, 002A, 123B, etc.
    if not re.match(r'^\d{1,4}[A-Z]?$', str(booth_number)):
        raise ValidationError(
            _('Enter a valid booth number (e.g., 001, 123A)'),
            code='invalid_booth_number'
        )

    return True


def validate_latitude(lat):
    """Validate latitude coordinate"""
    if lat is None:
        return True  # Optional

    try:
        lat_float = float(lat)
        if not (-90 <= lat_float <= 90):
            raise ValidationError(
                _('Latitude must be between -90 and 90 degrees'),
                code='invalid_latitude'
            )
    except (ValueError, TypeError):
        raise ValidationError(_('Invalid latitude format'))

    return True


def validate_longitude(lng):
    """Validate longitude coordinate"""
    if lng is None:
        return True  # Optional

    try:
        lng_float = float(lng)
        if not (-180 <= lng_float <= 180):
            raise ValidationError(
                _('Longitude must be between -180 and 180 degrees'),
                code='invalid_longitude'
            )
    except (ValueError, TypeError):
        raise ValidationError(_('Invalid longitude format'))

    return True


def validate_url(url):
    """Validate URL format"""
    if not url:
        return True  # Optional

    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    if not url_pattern.match(url):
        raise ValidationError(
            _('Enter a valid URL'),
            code='invalid_url'
        )

    return True


def validate_sentiment_score(score):
    """Validate sentiment score (0.0 to 1.0)"""
    if score is None:
        return True  # Optional

    try:
        score_float = float(score)
        if not (0.0 <= score_float <= 1.0):
            raise ValidationError(
                _('Sentiment score must be between 0.0 and 1.0'),
                code='invalid_sentiment_score'
            )
    except (ValueError, TypeError):
        raise ValidationError(_('Invalid sentiment score format'))

    return True


def validate_age(age):
    """Validate age (18 to 120)"""
    if age is None:
        return True  # Optional

    try:
        age_int = int(age)
        if not (18 <= age_int <= 120):
            raise ValidationError(
                _('Age must be between 18 and 120'),
                code='invalid_age'
            )
    except (ValueError, TypeError):
        raise ValidationError(_('Invalid age format'))

    return True
