#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import Constituency, PollingBooth

print('=' * 80)
print('CONSTITUENCIES WITHOUT DISTRICTS')
print('=' * 80)

no_district = Constituency.objects.filter(district__isnull=True)
print(f'\nFound {no_district.count()} constituencies without districts:\n')

for c in no_district:
    print(f'ID: {c.id}')
    print(f'Code: {c.code}')
    print(f'Name: {c.name}')
    print(f'State: {c.state.name if c.state else "None"}')
    print(f'District: {c.district}')

    # Check how many polling booths reference this constituency
    booth_count = PollingBooth.objects.filter(constituency=c).count()
    print(f'Polling booths: {booth_count}')
    print('-' * 80)

print('\n' + '=' * 80)
