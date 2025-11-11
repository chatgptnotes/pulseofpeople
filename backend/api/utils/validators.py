"""
Data Validation Utilities for Ward and Polling Booth Import
Validates CSV/Excel data before bulk insertion into database
"""

from typing import Dict, List, Tuple, Optional, Any
import re
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, field: str, message: str, row_number: Optional[int] = None):
        self.field = field
        self.message = message
        self.row_number = row_number
        super().__init__(f"Row {row_number}: {field} - {message}" if row_number else f"{field} - {message}")


class WardValidator:
    """Validator for ward data"""

    REQUIRED_FIELDS = ['name', 'code', 'constituency_code']
    URBANIZATION_TYPES = ['urban', 'semi_urban', 'rural']
    INCOME_LEVELS = ['low', 'medium', 'high']

    @classmethod
    def validate_row(cls, row: Dict[str, Any], row_number: int, constituency_codes: set) -> Tuple[bool, List[str]]:
        """
        Validate a single ward row

        Args:
            row: Dictionary containing ward data
            row_number: Row number in the file (for error reporting)
            constituency_codes: Set of valid constituency codes

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if not row.get(field) or str(row[field]).strip() == '':
                errors.append(f"Missing required field: {field}")

        # Validate constituency code exists
        if row.get('constituency_code') and row['constituency_code'] not in constituency_codes:
            errors.append(f"Invalid constituency_code: {row['constituency_code']} not found")

        # Validate ward code format (e.g., TN-AC-001-W-001)
        if row.get('code'):
            if not cls.validate_ward_code(row['code']):
                errors.append(f"Invalid ward code format: {row['code']}. Expected format: XX-AC-XXX-W-XXX")

        # Validate ward number (must be positive integer)
        if row.get('ward_number'):
            try:
                ward_num = int(row['ward_number'])
                if ward_num <= 0:
                    errors.append("ward_number must be a positive integer")
            except (ValueError, TypeError):
                errors.append(f"Invalid ward_number: {row['ward_number']} (must be an integer)")

        # Validate population (if provided)
        if row.get('population'):
            try:
                pop = int(row['population'])
                if pop < 0:
                    errors.append("population cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid population: {row['population']} (must be an integer)")

        # Validate voter_count (must be non-negative)
        if row.get('voter_count'):
            try:
                voters = int(row['voter_count'])
                if voters < 0:
                    errors.append("voter_count cannot be negative")
                # Sanity check: voter_count should not exceed population
                if row.get('population') and voters > int(row['population']):
                    errors.append("voter_count cannot exceed population")
            except (ValueError, TypeError):
                errors.append(f"Invalid voter_count: {row['voter_count']} (must be an integer)")

        # Validate total_booths
        if row.get('total_booths'):
            try:
                booths = int(row['total_booths'])
                if booths < 0:
                    errors.append("total_booths cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid total_booths: {row['total_booths']} (must be an integer)")

        # Validate urbanization
        if row.get('urbanization'):
            if row['urbanization'].lower() not in cls.URBANIZATION_TYPES:
                errors.append(f"Invalid urbanization: {row['urbanization']}. Must be one of {cls.URBANIZATION_TYPES}")

        # Validate income_level
        if row.get('income_level'):
            if row['income_level'].lower() not in cls.INCOME_LEVELS:
                errors.append(f"Invalid income_level: {row['income_level']}. Must be one of {cls.INCOME_LEVELS}")

        # Validate literacy_rate (0-100)
        if row.get('literacy_rate'):
            try:
                rate = float(row['literacy_rate'])
                if rate < 0 or rate > 100:
                    errors.append("literacy_rate must be between 0 and 100")
            except (ValueError, TypeError):
                errors.append(f"Invalid literacy_rate: {row['literacy_rate']} (must be a number)")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_ward_code(code: str) -> bool:
        """Validate ward code format: XX-AC-XXX-W-XXX"""
        pattern = r'^[A-Z]{2}-AC-\d{3}-W-\d{3}$'
        return bool(re.match(pattern, code))

    @classmethod
    def validate_batch(cls, rows: List[Dict[str, Any]], constituency_codes: set) -> Dict[str, Any]:
        """
        Validate a batch of ward rows

        Returns:
            Dictionary with validation results:
            {
                'is_valid': bool,
                'total_rows': int,
                'valid_rows': int,
                'invalid_rows': int,
                'errors': List[Dict],
                'valid_data': List[Dict]
            }
        """
        errors = []
        valid_data = []

        for idx, row in enumerate(rows, start=1):
            is_valid, row_errors = cls.validate_row(row, idx, constituency_codes)
            if is_valid:
                valid_data.append(row)
            else:
                errors.append({
                    'row_number': idx,
                    'row_data': row,
                    'errors': row_errors
                })

        return {
            'is_valid': len(errors) == 0,
            'total_rows': len(rows),
            'valid_rows': len(valid_data),
            'invalid_rows': len(errors),
            'errors': errors,
            'valid_data': valid_data
        }


class PollingBoothValidator:
    """Validator for polling booth data"""

    REQUIRED_FIELDS = ['constituency_code', 'booth_number', 'name']
    BOOTH_TYPES = ['regular', 'auxiliary', 'special']

    @classmethod
    def validate_row(cls, row: Dict[str, Any], row_number: int,
                    constituency_codes: set, ward_codes: set = None) -> Tuple[bool, List[str]]:
        """
        Validate a single polling booth row

        Args:
            row: Dictionary containing booth data
            row_number: Row number in the file
            constituency_codes: Set of valid constituency codes
            ward_codes: Set of valid ward codes (optional)

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if not row.get(field) or str(row[field]).strip() == '':
                errors.append(f"Missing required field: {field}")

        # Validate constituency code
        if row.get('constituency_code') and row['constituency_code'] not in constituency_codes:
            errors.append(f"Invalid constituency_code: {row['constituency_code']} not found")

        # Validate ward code (if provided)
        if row.get('ward_code') and ward_codes:
            if row['ward_code'] not in ward_codes:
                errors.append(f"Invalid ward_code: {row['ward_code']} not found")

        # Validate booth number format (alphanumeric, max 50 chars)
        if row.get('booth_number'):
            booth_num = str(row['booth_number']).strip()
            if len(booth_num) > 50:
                errors.append(f"booth_number too long (max 50 characters): {booth_num}")
            if not booth_num:
                errors.append("booth_number cannot be empty")

        # Validate GPS coordinates
        if row.get('latitude'):
            try:
                lat = float(row['latitude'])
                if lat < -90 or lat > 90:
                    errors.append(f"Invalid latitude: {lat} (must be between -90 and 90)")
            except (ValueError, TypeError):
                errors.append(f"Invalid latitude: {row['latitude']} (must be a number)")

        if row.get('longitude'):
            try:
                lon = float(row['longitude'])
                if lon < -180 or lon > 180:
                    errors.append(f"Invalid longitude: {lon} (must be between -180 and 180)")
            except (ValueError, TypeError):
                errors.append(f"Invalid longitude: {row['longitude']} (must be a number)")

        # Validate voter counts
        total_voters = 0
        if row.get('total_voters'):
            try:
                total_voters = int(row['total_voters'])
                if total_voters < 0:
                    errors.append("total_voters cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid total_voters: {row['total_voters']} (must be an integer)")

        # Validate male voters
        male_voters = 0
        if row.get('male_voters'):
            try:
                male_voters = int(row['male_voters'])
                if male_voters < 0:
                    errors.append("male_voters cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid male_voters: {row['male_voters']} (must be an integer)")

        # Validate female voters
        female_voters = 0
        if row.get('female_voters'):
            try:
                female_voters = int(row['female_voters'])
                if female_voters < 0:
                    errors.append("female_voters cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid female_voters: {row['female_voters']} (must be an integer)")

        # Validate transgender voters
        transgender_voters = 0
        if row.get('transgender_voters'):
            try:
                transgender_voters = int(row['transgender_voters'])
                if transgender_voters < 0:
                    errors.append("transgender_voters cannot be negative")
            except (ValueError, TypeError):
                errors.append(f"Invalid transgender_voters: {row['transgender_voters']} (must be an integer)")

        # Check: sum of gender voters should not exceed total
        if total_voters > 0:
            gender_sum = male_voters + female_voters + transgender_voters
            if gender_sum > total_voters:
                errors.append(f"Sum of gender voters ({gender_sum}) exceeds total_voters ({total_voters})")

        # Validate booth type
        if row.get('booth_type'):
            if row['booth_type'].lower() not in cls.BOOTH_TYPES:
                errors.append(f"Invalid booth_type: {row['booth_type']}. Must be one of {cls.BOOTH_TYPES}")

        # Validate priority level (1-5)
        if row.get('priority_level'):
            try:
                priority = int(row['priority_level'])
                if priority < 1 or priority > 5:
                    errors.append("priority_level must be between 1 and 5")
            except (ValueError, TypeError):
                errors.append(f"Invalid priority_level: {row['priority_level']} (must be an integer)")

        # Validate boolean fields
        for bool_field in ['is_accessible', 'is_active']:
            if row.get(bool_field):
                val = str(row[bool_field]).lower()
                if val not in ['true', 'false', '1', '0', 'yes', 'no', 't', 'f']:
                    errors.append(f"Invalid {bool_field}: {row[bool_field]} (must be boolean)")

        return (len(errors) == 0, errors)

    @classmethod
    def validate_batch(cls, rows: List[Dict[str, Any]],
                      constituency_codes: set,
                      ward_codes: set = None) -> Dict[str, Any]:
        """
        Validate a batch of polling booth rows

        Returns:
            Dictionary with validation results
        """
        errors = []
        valid_data = []

        for idx, row in enumerate(rows, start=1):
            is_valid, row_errors = cls.validate_row(row, idx, constituency_codes, ward_codes)
            if is_valid:
                valid_data.append(row)
            else:
                errors.append({
                    'row_number': idx,
                    'row_data': row,
                    'errors': row_errors
                })

        return {
            'is_valid': len(errors) == 0,
            'total_rows': len(rows),
            'valid_rows': len(valid_data),
            'invalid_rows': len(errors),
            'errors': errors,
            'valid_data': valid_data
        }


class DuplicateDetector:
    """Detect duplicates in import data"""

    @staticmethod
    def find_duplicate_ward_codes(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find duplicate ward codes in the batch"""
        code_counts = {}
        duplicates = []

        for idx, row in enumerate(rows, start=1):
            code = row.get('code')
            if code:
                if code in code_counts:
                    code_counts[code].append(idx)
                else:
                    code_counts[code] = [idx]

        for code, row_numbers in code_counts.items():
            if len(row_numbers) > 1:
                duplicates.append({
                    'code': code,
                    'row_numbers': row_numbers,
                    'count': len(row_numbers)
                })

        return duplicates

    @staticmethod
    def find_duplicate_booth_numbers(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find duplicate booth numbers within same constituency"""
        booth_map = {}
        duplicates = []

        for idx, row in enumerate(rows, start=1):
            constituency_code = row.get('constituency_code')
            booth_number = row.get('booth_number')

            if constituency_code and booth_number:
                key = f"{constituency_code}:{booth_number}"
                if key in booth_map:
                    booth_map[key].append(idx)
                else:
                    booth_map[key] = [idx]

        for key, row_numbers in booth_map.items():
            if len(row_numbers) > 1:
                constituency_code, booth_number = key.split(':')
                duplicates.append({
                    'constituency_code': constituency_code,
                    'booth_number': booth_number,
                    'row_numbers': row_numbers,
                    'count': len(row_numbers)
                })

        return duplicates
