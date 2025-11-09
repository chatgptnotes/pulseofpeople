#!/usr/bin/env python
"""
Fix constituencies without districts by deleting them.
These appear to be test/orphaned data that shouldn't exist.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Constituency

print('=' * 80)
print('FIXING CONSTITUENCIES WITHOUT DISTRICTS')
print('=' * 80)

no_district = Constituency.objects.filter(district__isnull=True)
count = no_district.count()

if count == 0:
    print('\nNo constituencies without districts found. Database is clean!')
else:
    print(f'\nFound {count} constituencies without districts:\n')

    for c in no_district:
        print(f'  - {c.name} (code: {c.code})')

    print(f'\nDeleting {count} constituencies...')
    deleted_count, _ = no_district.delete()
    print(f'✓ Deleted {deleted_count} constituencies')

print('\n' + '=' * 80)
