#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from api.models import District, Constituency, PollingBooth

print('=' * 80)
print('DATABASE STATUS CHECK')
print('=' * 80)

# Check districts
districts = District.objects.all().order_by('code')
print(f'\nTotal districts: {districts.count()}')
print('\nDistrict codes (first 10):')
for d in districts[:10]:
    print(f'  {d.code}: {d.name}')

# Check constituencies
constituencies = Constituency.objects.all()
print(f'\nTotal constituencies: {constituencies.count()}')

# Check for constituencies without districts
no_district = Constituency.objects.filter(district__isnull=True)
print(f'\nConstituencies without districts: {no_district.count()}')
if no_district.exists():
    print('  Examples:')
    for c in no_district[:5]:
        print(f'    - {c.name} (code: {c.code})')

# Check polling booths
booths = PollingBooth.objects.all()
print(f'\nTotal polling booths: {booths.count()}')

# Check for polling booths without districts
booths_no_district = PollingBooth.objects.filter(district__isnull=True)
print(f'Polling booths without districts: {booths_no_district.count()}')
if booths_no_district.exists():
    print('  Examples:')
    for b in booths_no_district[:5]:
        print(f'    - {b.name} (constituency: {b.constituency.name if b.constituency else "None"})')

print('\n' + '=' * 80)
