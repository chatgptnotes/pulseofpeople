"""
Bulk User Import Service
Handles CSV validation, processing, and user creation in background
"""

import csv
import io
import os
import uuid
import string
import secrets
import threading
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from api.models import UserProfile, BulkUploadJob, BulkUploadError, State, District


class BulkUserImportService:
    """Service for handling bulk user imports from CSV"""

    REQUIRED_COLUMNS = ['name', 'email', 'role']
    OPTIONAL_COLUMNS = ['phone', 'state_id', 'district_id']
    ALL_COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS

    VALID_ROLES = ['admin', 'manager', 'analyst', 'user', 'volunteer', 'viewer']

    # Role hierarchy for validation
    ROLE_HIERARCHY = {
        'superadmin': ['admin', 'manager', 'analyst', 'user', 'volunteer', 'viewer'],
        'admin': ['manager', 'analyst', 'user', 'volunteer', 'viewer'],
        'manager': ['analyst', 'user', 'volunteer', 'viewer'],
        'analyst': ['user', 'volunteer', 'viewer'],
    }

    def __init__(self, job: BulkUploadJob, requesting_user: User):
        self.job = job
        self.requesting_user = requesting_user
        self.requesting_role = getattr(requesting_user.profile, 'role', 'user')
        self.allowed_roles = self.ROLE_HIERARCHY.get(self.requesting_role, [])

    def generate_password(self, length: int = 12) -> str:
        """Generate a random secure password"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        while True:
            password = ''.join(secrets.choice(alphabet) for _ in range(length))
            # Ensure password meets requirements
            if (any(c.islower() for c in password)
                    and any(c.isupper() for c in password)
                    and any(c.isdigit() for c in password)
                    and any(c in string.punctuation for c in password)):
                return password

    def validate_csv_structure(self, file_content: str) -> Tuple[bool, List[str], List[Dict]]:
        """
        Validate CSV structure and return parsed rows

        Returns:
            (is_valid, errors, rows)
        """
        errors = []
        rows = []

        try:
            # Parse CSV
            csv_file = io.StringIO(file_content)
            reader = csv.DictReader(csv_file)

            # Check if file has headers
            if not reader.fieldnames:
                errors.append("CSV file is empty or has no headers")
                return False, errors, []

            # Validate required columns
            missing_columns = set(self.REQUIRED_COLUMNS) - set(reader.fieldnames)
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                return False, errors, []

            # Read all rows
            for idx, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                rows.append({
                    'row_number': idx,
                    'data': row
                })

            if not rows:
                errors.append("CSV file contains no data rows")
                return False, errors, []

            if len(rows) > 10000:
                errors.append("CSV file exceeds maximum of 10,000 users")
                return False, errors, []

            return True, errors, rows

        except Exception as e:
            errors.append(f"Failed to parse CSV: {str(e)}")
            return False, errors, []

    def validate_row(self, row: Dict, row_number: int) -> Tuple[bool, List[str]]:
        """
        Validate a single row

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        if not row.get('name', '').strip():
            errors.append('Name is required')

        email = row.get('email', '').strip()
        if not email:
            errors.append('Email is required')
        elif '@' not in email:
            errors.append('Email is invalid')
        elif User.objects.filter(email=email).exists():
            errors.append(f'Email {email} already exists')

        # Validate role
        role = row.get('role', '').strip().lower()
        if not role:
            errors.append('Role is required')
        elif role not in self.VALID_ROLES:
            errors.append(f'Invalid role: {role}. Must be one of: {", ".join(self.VALID_ROLES)}')
        elif role not in self.allowed_roles:
            errors.append(f'You do not have permission to create users with role: {role}')

        # Validate optional state_id
        state_id = row.get('state_id', '').strip()
        if state_id:
            try:
                state_id = int(state_id)
                if not State.objects.filter(id=state_id).exists():
                    errors.append(f'State ID {state_id} does not exist')
            except ValueError:
                errors.append(f'State ID must be a number, got: {state_id}')

        # Validate optional district_id
        district_id = row.get('district_id', '').strip()
        if district_id:
            try:
                district_id = int(district_id)
                if not District.objects.filter(id=district_id).exists():
                    errors.append(f'District ID {district_id} does not exist')
            except ValueError:
                errors.append(f'District ID must be a number, got: {district_id}')

        return len(errors) == 0, errors

    def validate_all_rows(self, rows: List[Dict]) -> List[BulkUploadError]:
        """
        Validate all rows and collect errors

        Returns:
            List of BulkUploadError objects (not yet saved)
        """
        error_objects = []

        for row_info in rows:
            row_number = row_info['row_number']
            row_data = row_info['data']

            is_valid, error_messages = self.validate_row(row_data, row_number)

            if not is_valid:
                for error_msg in error_messages:
                    error_objects.append(BulkUploadError(
                        job=self.job,
                        row_number=row_number,
                        row_data=row_data,
                        error_message=error_msg,
                        error_field=self._extract_field_from_error(error_msg)
                    ))

        return error_objects

    def _extract_field_from_error(self, error_msg: str) -> str:
        """Extract field name from error message"""
        if 'name' in error_msg.lower():
            return 'name'
        elif 'email' in error_msg.lower():
            return 'email'
        elif 'role' in error_msg.lower():
            return 'role'
        elif 'phone' in error_msg.lower():
            return 'phone'
        elif 'state' in error_msg.lower():
            return 'state_id'
        elif 'district' in error_msg.lower():
            return 'district_id'
        return ''

    def create_user_from_row(self, row: Dict) -> Tuple[Optional[User], Optional[str], str]:
        """
        Create a user from a validated row

        Returns:
            (user, password, error_message)
        """
        try:
            name = row.get('name', '').strip()
            email = row.get('email', '').strip()
            role = row.get('role', '').strip().lower()
            phone = row.get('phone', '').strip()
            state_id = row.get('state_id', '').strip()
            district_id = row.get('district_id', '').strip()

            # Generate username from email
            username = email.split('@')[0]
            base_username = username

            # Make username unique if needed
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            # Generate password
            password = self.generate_password()

            # Create user
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=name.split()[0] if name else '',
                    last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else ''
                )

                # Get or create profile
                profile, created = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={'role': role, 'must_change_password': True}
                )

                if not created:
                    profile.role = role
                    profile.must_change_password = True

                # Update optional fields
                if phone:
                    profile.phone = phone
                if state_id:
                    try:
                        profile.assigned_state_id = int(state_id)
                    except (ValueError, TypeError):
                        pass
                if district_id:
                    try:
                        profile.assigned_district_id = int(district_id)
                    except (ValueError, TypeError):
                        pass

                profile.save()

            return user, password, None

        except Exception as e:
            return None, None, str(e)

    def send_welcome_email(self, user: User, password: str):
        """Send welcome email with credentials"""
        try:
            subject = 'Welcome to Pulse of People - Your Account Details'
            message = f"""
Hello {user.first_name or user.username},

Your account has been created successfully!

Login Details:
- Email: {user.email}
- Username: {user.username}
- Temporary Password: {password}

Please login and change your password immediately for security.

Login URL: {settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'http://localhost:5173'}

Best regards,
Pulse of People Team
            """.strip()

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@pulseofpeople.com',
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e}")

    def send_completion_email(self):
        """Send completion email to admin"""
        try:
            subject = f'Bulk User Import Completed - Job {self.job.job_id}'
            message = f"""
Hello {self.requesting_user.first_name or self.requesting_user.username},

Your bulk user import job has been completed.

Summary:
- Total Rows: {self.job.total_rows}
- Successfully Created: {self.job.success_count}
- Failed: {self.job.failed_count}
- Status: {self.job.status}

{f"You can download the error report from the user management page." if self.job.failed_count > 0 else "All users were created successfully!"}

Best regards,
Pulse of People Team
            """.strip()

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@pulseofpeople.com',
                [self.requesting_user.email],
                fail_silently=True,
            )
        except Exception as e:
            print(f"Failed to send completion email: {e}")

    def process_csv(self, file_content: str):
        """
        Main processing function - validates and creates users
        This runs in the background
        """
        try:
            # Update status to validating
            self.job.status = 'validating'
            self.job.started_at = timezone.now()
            self.job.save()

            # Validate CSV structure
            is_valid, structure_errors, rows = self.validate_csv_structure(file_content)
            if not is_valid:
                self.job.status = 'failed'
                self.job.validation_errors = structure_errors
                self.job.completed_at = timezone.now()
                self.job.save()
                return

            self.job.total_rows = len(rows)
            self.job.save()

            # Validate all rows
            validation_errors = self.validate_all_rows(rows)

            if validation_errors:
                # Save validation errors
                BulkUploadError.objects.bulk_create(validation_errors)
                self.job.failed_count = len(validation_errors)
                self.job.validation_errors = [f"{len(validation_errors)} rows have validation errors"]
                self.job.save()

            # Filter out rows with errors
            error_row_numbers = {err.row_number for err in validation_errors}
            valid_rows = [r for r in rows if r['row_number'] not in error_row_numbers]

            if not valid_rows:
                self.job.status = 'failed'
                self.job.validation_errors = ["No valid rows to process"]
                self.job.completed_at = timezone.now()
                self.job.save()
                self.send_completion_email()
                return

            # Update status to processing
            self.job.status = 'processing'
            self.job.save()

            # Process valid rows
            for row_info in valid_rows:
                row_number = row_info['row_number']
                row_data = row_info['data']

                user, password, error = self.create_user_from_row(row_data)

                if user and password:
                    # Success
                    self.job.success_count += 1
                    # Send welcome email
                    self.send_welcome_email(user, password)
                else:
                    # Failed to create user
                    self.job.failed_count += 1
                    BulkUploadError.objects.create(
                        job=self.job,
                        row_number=row_number,
                        row_data=row_data,
                        error_message=error or 'Unknown error',
                        error_field=''
                    )

                # Update progress
                self.job.processed_rows += 1
                self.job.save()

            # Mark as completed
            self.job.status = 'completed'
            self.job.completed_at = timezone.now()
            self.job.save()

            # Send completion email
            self.send_completion_email()

        except Exception as e:
            # Handle unexpected errors
            self.job.status = 'failed'
            self.job.validation_errors = [f"Unexpected error: {str(e)}"]
            self.job.completed_at = timezone.now()
            self.job.save()


def process_bulk_upload_async(job_id: str, file_content: str, requesting_user_id: int):
    """
    Process bulk upload in background thread

    Args:
        job_id: UUID of the BulkUploadJob
        file_content: CSV file content as string
        requesting_user_id: ID of user who initiated the upload
    """
    try:
        job = BulkUploadJob.objects.get(job_id=job_id)
        requesting_user = User.objects.get(id=requesting_user_id)

        service = BulkUserImportService(job, requesting_user)
        service.process_csv(file_content)

    except Exception as e:
        print(f"Background processing failed for job {job_id}: {e}")


def start_bulk_upload_processing(job: BulkUploadJob, file_content: str, requesting_user: User):
    """
    Start background processing of bulk upload

    Args:
        job: BulkUploadJob instance
        file_content: CSV file content as string
        requesting_user: User who initiated the upload
    """
    thread = threading.Thread(
        target=process_bulk_upload_async,
        args=(str(job.job_id), file_content, requesting_user.id)
    )
    thread.daemon = True
    thread.start()
