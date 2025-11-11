"""
Bulk Import Service for Wards and Polling Booths
Handles CSV/Excel parsing, validation, and batch insertion to Supabase
"""

import csv
import io
import uuid
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from decimal import Decimal
import openpyxl
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from supabase import create_client, Client

from api.models import BulkUploadJob, BulkUploadError, User, Constituency
from api.utils.validators import WardValidator, PollingBoothValidator, DuplicateDetector


class SupabaseService:
    """Wrapper for Supabase client operations"""

    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY
        )

    def get_constituencies(self, organization_id: str) -> Dict[str, str]:
        """Get constituency code -> id mapping"""
        response = self.client.table('constituencies').select('id, code').eq(
            'organization_id', organization_id
        ).execute()

        return {row['code']: row['id'] for row in response.data}

    def get_wards(self, organization_id: str) -> Dict[str, str]:
        """Get ward code -> id mapping"""
        response = self.client.table('wards').select('id, code').eq(
            'organization_id', organization_id
        ).execute()

        return {row['code']: row['id'] for row in response.data}

    def bulk_insert_wards(self, wards: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, Any]:
        """
        Bulk insert wards in batches

        Args:
            wards: List of ward dictionaries
            batch_size: Number of records per batch

        Returns:
            Dict with insert statistics
        """
        total_inserted = 0
        total_failed = 0
        errors = []

        # Insert in batches
        for i in range(0, len(wards), batch_size):
            batch = wards[i:i + batch_size]
            try:
                response = self.client.table('wards').insert(batch).execute()
                total_inserted += len(response.data)
            except Exception as e:
                total_failed += len(batch)
                errors.append({
                    'batch_start': i,
                    'batch_end': min(i + batch_size, len(wards)),
                    'error': str(e)
                })

        return {
            'total_inserted': total_inserted,
            'total_failed': total_failed,
            'errors': errors
        }

    def bulk_upsert_wards(self, wards: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, Any]:
        """
        Bulk upsert wards (insert or update if exists)

        Uses ON CONFLICT (organization_id, code) DO UPDATE
        """
        total_upserted = 0
        total_failed = 0
        errors = []

        for i in range(0, len(wards), batch_size):
            batch = wards[i:i + batch_size]
            try:
                response = self.client.table('wards').upsert(
                    batch,
                    on_conflict='organization_id,code'
                ).execute()
                total_upserted += len(response.data)
            except Exception as e:
                total_failed += len(batch)
                errors.append({
                    'batch_start': i,
                    'batch_end': min(i + batch_size, len(wards)),
                    'error': str(e)
                })

        return {
            'total_upserted': total_upserted,
            'total_failed': total_failed,
            'errors': errors
        }

    def bulk_insert_booths(self, booths: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, Any]:
        """Bulk insert polling booths in batches"""
        total_inserted = 0
        total_failed = 0
        errors = []

        for i in range(0, len(booths), batch_size):
            batch = booths[i:i + batch_size]
            try:
                response = self.client.table('polling_booths').insert(batch).execute()
                total_inserted += len(response.data)
            except Exception as e:
                total_failed += len(batch)
                errors.append({
                    'batch_start': i,
                    'batch_end': min(i + batch_size, len(booths)),
                    'error': str(e)
                })

        return {
            'total_inserted': total_inserted,
            'total_failed': total_failed,
            'errors': errors
        }

    def bulk_upsert_booths(self, booths: List[Dict[str, Any]], batch_size: int = 100) -> Dict[str, Any]:
        """Bulk upsert polling booths"""
        total_upserted = 0
        total_failed = 0
        errors = []

        for i in range(0, len(booths), batch_size):
            batch = booths[i:i + batch_size]
            try:
                response = self.client.table('polling_booths').upsert(
                    batch,
                    on_conflict='organization_id,constituency_id,booth_number'
                ).execute()
                total_upserted += len(response.data)
            except Exception as e:
                total_failed += len(batch)
                errors.append({
                    'batch_start': i,
                    'batch_end': min(i + batch_size, len(booths)),
                    'error': str(e)
                })

        return {
            'total_upserted': total_upserted,
            'total_failed': total_failed,
            'errors': errors
        }


class FileParser:
    """Parse CSV and Excel files"""

    @staticmethod
    def parse_csv(file: UploadedFile) -> List[Dict[str, Any]]:
        """Parse CSV file into list of dictionaries"""
        # Read file content
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8-sig')  # Handle BOM

        # Parse CSV
        reader = csv.DictReader(io.StringIO(content))
        rows = [dict(row) for row in reader]

        return rows

    @staticmethod
    def parse_excel(file: UploadedFile) -> List[Dict[str, Any]]:
        """Parse Excel file into list of dictionaries"""
        workbook = openpyxl.load_workbook(file, read_only=True)
        sheet = workbook.active

        # Get headers from first row
        headers = [cell.value for cell in sheet[1]]

        # Parse data rows
        rows = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            row_dict = {headers[i]: row[i] for i in range(len(headers)) if i < len(row)}
            rows.append(row_dict)

        workbook.close()
        return rows


class WardBulkImportService:
    """Service for bulk importing wards"""

    def __init__(self, user: User, organization_id: str):
        self.user = user
        self.organization_id = organization_id
        self.supabase = SupabaseService()

    def process_file(self, file: UploadedFile, update_existing: bool = False) -> BulkUploadJob:
        """
        Process uploaded file and import wards

        Args:
            file: Uploaded CSV or Excel file
            update_existing: If True, update existing wards. If False, skip duplicates.

        Returns:
            BulkUploadJob instance with import results
        """
        # Create job record
        job = BulkUploadJob.objects.create(
            created_by=self.user,
            file_name=file.name,
            file_path=f"uploads/{uuid.uuid4()}_{file.name}",
            status='validating'
        )

        try:
            # Parse file
            if file.name.lower().endswith('.csv'):
                rows = FileParser.parse_csv(file)
            else:
                rows = FileParser.parse_excel(file)

            job.total_rows = len(rows)
            job.save()

            # Get constituency mapping
            constituency_map = self.supabase.get_constituencies(self.organization_id)
            constituency_codes = set(constituency_map.keys())

            # Validate data
            job.status = 'validating'
            job.save()

            validation_result = WardValidator.validate_batch(rows, constituency_codes)

            if not validation_result['is_valid']:
                # Store validation errors
                for error in validation_result['errors']:
                    BulkUploadError.objects.create(
                        job=job,
                        row_number=error['row_number'],
                        row_data=error['row_data'],
                        error_message='; '.join(error['errors']),
                        error_field='validation'
                    )

                job.status = 'failed'
                job.failed_count = validation_result['invalid_rows']
                job.validation_errors = validation_result['errors']
                job.save()
                return job

            # Check for duplicates in the file
            duplicates = DuplicateDetector.find_duplicate_ward_codes(rows)
            if duplicates:
                job.status = 'failed'
                job.validation_errors = {
                    'duplicates': duplicates,
                    'message': f"Found {len(duplicates)} duplicate ward codes in file"
                }
                job.save()
                return job

            # Transform data for Supabase
            job.status = 'processing'
            job.started_at = datetime.now()
            job.save()

            wards_data = self._transform_rows(
                validation_result['valid_data'],
                constituency_map
            )

            # Insert or upsert to Supabase
            if update_existing:
                result = self.supabase.bulk_upsert_wards(wards_data, batch_size=100)
                job.success_count = result['total_upserted']
            else:
                result = self.supabase.bulk_insert_wards(wards_data, batch_size=100)
                job.success_count = result['total_inserted']

            job.failed_count = result['total_failed']
            job.processed_rows = job.total_rows

            if result['errors']:
                job.validation_errors = {'insert_errors': result['errors']}

            # Update job status
            job.status = 'completed' if job.failed_count == 0 else 'failed'
            job.completed_at = datetime.now()
            job.save()

            return job

        except Exception as e:
            job.status = 'failed'
            job.validation_errors = {'error': str(e)}
            job.save()
            raise

    def _transform_rows(self, rows: List[Dict[str, Any]], constituency_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Transform validated rows into Supabase format"""
        wards = []

        for row in rows:
            ward = {
                'organization_id': self.organization_id,
                'constituency_id': constituency_map[row['constituency_code']],
                'name': row['name'],
                'code': row['code'],
            }

            # Optional fields
            if row.get('ward_number'):
                ward['ward_number'] = int(row['ward_number'])

            if row.get('population'):
                ward['population'] = int(row['population'])

            if row.get('voter_count'):
                ward['voter_count'] = int(row['voter_count'])

            if row.get('total_booths'):
                ward['total_booths'] = int(row['total_booths'])

            if row.get('urbanization'):
                ward['urbanization'] = row['urbanization'].lower()

            if row.get('income_level'):
                ward['income_level'] = row['income_level'].lower()

            if row.get('literacy_rate'):
                ward['literacy_rate'] = float(row['literacy_rate'])

            wards.append(ward)

        return wards


class PollingBoothBulkImportService:
    """Service for bulk importing polling booths"""

    def __init__(self, user: User, organization_id: str):
        self.user = user
        self.organization_id = organization_id
        self.supabase = SupabaseService()

    def process_file(self, file: UploadedFile, update_existing: bool = False) -> BulkUploadJob:
        """Process uploaded file and import polling booths"""

        # Create job record
        job = BulkUploadJob.objects.create(
            created_by=self.user,
            file_name=file.name,
            file_path=f"uploads/{uuid.uuid4()}_{file.name}",
            status='validating'
        )

        try:
            # Parse file
            if file.name.lower().endswith('.csv'):
                rows = FileParser.parse_csv(file)
            else:
                rows = FileParser.parse_excel(file)

            job.total_rows = len(rows)
            job.save()

            # Get constituency and ward mappings
            constituency_map = self.supabase.get_constituencies(self.organization_id)
            constituency_codes = set(constituency_map.keys())

            ward_map = self.supabase.get_wards(self.organization_id)
            ward_codes = set(ward_map.keys())

            # Validate data
            job.status = 'validating'
            job.save()

            validation_result = PollingBoothValidator.validate_batch(
                rows, constituency_codes, ward_codes
            )

            if not validation_result['is_valid']:
                for error in validation_result['errors']:
                    BulkUploadError.objects.create(
                        job=job,
                        row_number=error['row_number'],
                        row_data=error['row_data'],
                        error_message='; '.join(error['errors']),
                        error_field='validation'
                    )

                job.status = 'failed'
                job.failed_count = validation_result['invalid_rows']
                job.validation_errors = validation_result['errors']
                job.save()
                return job

            # Check for duplicates
            duplicates = DuplicateDetector.find_duplicate_booth_numbers(rows)
            if duplicates:
                job.status = 'failed'
                job.validation_errors = {
                    'duplicates': duplicates,
                    'message': f"Found {len(duplicates)} duplicate booth numbers in file"
                }
                job.save()
                return job

            # Transform and insert
            job.status = 'processing'
            job.started_at = datetime.now()
            job.save()

            booths_data = self._transform_rows(rows, constituency_map, ward_map)

            if update_existing:
                result = self.supabase.bulk_upsert_booths(booths_data, batch_size=100)
                job.success_count = result['total_upserted']
            else:
                result = self.supabase.bulk_insert_booths(booths_data, batch_size=100)
                job.success_count = result['total_inserted']

            job.failed_count = result['total_failed']
            job.processed_rows = job.total_rows

            if result['errors']:
                job.validation_errors = {'insert_errors': result['errors']}

            job.status = 'completed' if job.failed_count == 0 else 'failed'
            job.completed_at = datetime.now()
            job.save()

            return job

        except Exception as e:
            job.status = 'failed'
            job.validation_errors = {'error': str(e)}
            job.save()
            raise

    def _transform_rows(self, rows: List[Dict[str, Any]],
                       constituency_map: Dict[str, str],
                       ward_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Transform validated rows into Supabase format"""
        booths = []

        for row in rows:
            booth = {
                'organization_id': self.organization_id,
                'constituency_id': constituency_map[row['constituency_code']],
                'booth_number': str(row['booth_number']).strip(),
                'name': row['name'],
            }

            # Optional fields
            if row.get('ward_code') and row['ward_code'] in ward_map:
                booth['ward_id'] = ward_map[row['ward_code']]

            if row.get('address'):
                booth['address'] = row['address']

            if row.get('latitude'):
                booth['latitude'] = float(row['latitude'])

            if row.get('longitude'):
                booth['longitude'] = float(row['longitude'])

            if row.get('landmark'):
                booth['landmark'] = row['landmark']

            if row.get('total_voters'):
                booth['total_voters'] = int(row['total_voters'])

            if row.get('male_voters'):
                booth['male_voters'] = int(row['male_voters'])

            if row.get('female_voters'):
                booth['female_voters'] = int(row['female_voters'])

            if row.get('transgender_voters'):
                booth['transgender_voters'] = int(row['transgender_voters'])

            if row.get('booth_type'):
                booth['booth_type'] = row['booth_type'].lower()

            if row.get('is_accessible') is not None:
                booth['is_accessible'] = self._parse_boolean(row['is_accessible'])

            if row.get('is_active') is not None:
                booth['is_active'] = self._parse_boolean(row['is_active'])

            if row.get('building_name'):
                booth['building_name'] = row['building_name']

            if row.get('building_type'):
                booth['building_type'] = row['building_type']

            if row.get('priority_level'):
                booth['priority_level'] = int(row['priority_level'])

            booths.append(booth)

        return booths

    @staticmethod
    def _parse_boolean(value: Any) -> bool:
        """Parse various boolean representations"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', 'yes', '1', 't', 'y']
        if isinstance(value, int):
            return value == 1
        return False
