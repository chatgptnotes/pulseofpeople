#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile

print(f'✅ Total users in database: {User.objects.count()}\n')
print('Users List:')
print('-' * 80)

for user in User.objects.all():
    profile = getattr(user, 'profile', None)
    role = profile.role if profile else 'No profile'
    superuser_status = '🔑 SUPERUSER' if user.is_superuser else ''

    print(f'ID: {user.id:2d} | {user.username:15s} | {user.email:30s} | {role:12s} {superuser_status}')

print('-' * 80)
print(f'\n✅ Database: Supabase PostgreSQL')
print(f'✅ Host: aws-1-ap-south-1.pooler.supabase.com:6543')
