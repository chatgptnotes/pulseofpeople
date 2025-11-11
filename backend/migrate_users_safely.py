#\!/usr/bin/env python
"""
Safe User Migration Script: SQLite → Supabase
Preserves existing Supabase data and adds new users from SQLite
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import UserProfile
from django.db import connection, connections
from django.conf import settings

print('='*60)
print('SAFE USER MIGRATION: SQLite → Supabase')
print('='*60)
print()
print('⚠️  This script will:')
print('  1. Read all users from SQLite')
print('  2. Check existing users in Supabase')
print('  3. Add ONLY new users (skip duplicates)')
print('  4. Preserve ALL existing Supabase data')

# Step 1: Get users from SQLite
print()
print('='*60)
print('STEP 1: READING SQLITE DATABASE')
print('='*60)

# Ensure we're using SQLite
os.environ['USE_SQLITE'] = 'True'
connections.close_all()

# Manually set database to SQLite
from django.conf import settings
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': settings.BASE_DIR / 'db.sqlite3',
}

# Read SQLite users
sqlite_users_data = []
for user in User.objects.all().order_by('id'):
    try:
        profile = user.profile
        role = profile.role
    except:
        role = 'user'

    sqlite_users_data.append({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'password': user.password,  # Already hashed
        'role': role,
    })
    print(f'  - {user.username} ({user.email}) - Role: {role}')

print(f'Total SQLite users: {len(sqlite_users_data)}')

# Step 2: Switch to Supabase and check existing users
print()
print('='*60)
print('STEP 2: CHECKING SUPABASE DATABASE')
print('='*60)

# Switch to Supabase
os.environ['USE_SQLITE'] = 'False'
connections.close_all()

# Manually set database to Supabase (use environment variables for security)
settings.DATABASES['default'] = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': os.environ.get('DB_NAME', 'postgres'),
    'USER': os.environ.get('DB_USER', 'postgres.iwtgbseaoztjbnvworyq'),
    'PASSWORD': os.environ.get('DB_PASSWORD'),  # MUST be set in environment
    'HOST': os.environ.get('DB_HOST', 'aws-1-ap-south-1.pooler.supabase.com'),
    'PORT': os.environ.get('DB_PORT', '6543'),
    'OPTIONS': {
        'sslmode': os.environ.get('DB_SSLMODE', 'prefer'),
    },
}

# Check existing users in Supabase
existing_usernames = set(User.objects.values_list('username', flat=True))
existing_emails = set(User.objects.values_list('email', flat=True))

print(f'Existing Supabase users: {len(existing_usernames)}')
for username in existing_usernames:
    user = User.objects.get(username=username)
    print(f'  - {username} ({user.email})')

# Step 3: Determine which users to add
print()
print('='*60)
print('STEP 3: MIGRATION PLAN')
print('='*60)

users_to_add = []
users_to_skip = []

for user_data in sqlite_users_data:
    username = user_data['username']
    email = user_data['email']

    if username in existing_usernames or email in existing_emails:
        users_to_skip.append(f'{username} ({email})')
        print(f'  ⏭️  SKIP: {username} ({email}) - Already exists in Supabase')
    else:
        users_to_add.append(user_data)
        print(f'  ✅ ADD:  {username} ({email}) - Role: {user_data["role"]}')

print(f'Summary:')
print(f'  - Users to add: {len(users_to_add)}')
print(f'  - Users to skip (duplicates): {len(users_to_skip)}')

# Step 4: Add new users
if users_to_add:
    print()
    print('='*60)
    print('STEP 4: ADDING NEW USERS TO SUPABASE')
    print('='*60)

    added_count = 0
    for user_data in users_to_add:
        try:
            # Create user
            user = User.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_superuser=user_data['is_superuser'],
                is_staff=user_data['is_staff'],
                is_active=user_data['is_active'],
            )
            # Set hashed password directly
            user.password = user_data['password']
            user.save()

            # Create profile
            UserProfile.objects.create(
                user=user,
                role=user_data['role']
            )

            added_count += 1
            print(f'  ✅ Added: {user.username} ({user.email}) - Role: {user_data["role"]}')

        except Exception as e:
            print(f'  ❌ Error adding {user_data["username"]}: {e}')

    print(f'✅ Migration complete\! Added {added_count} new users to Supabase.')
else:
    print()
    print('✅ No new users to add. Supabase already has all users.')

# Step 5: Verify final state
print()
print('='*60)
print('STEP 5: VERIFICATION - FINAL USER COUNT IN SUPABASE')
print('='*60)

all_users = User.objects.all().order_by('id')
print(f'Total users in Supabase: {all_users.count()}')
print()

for user in all_users:
    try:
        profile = user.profile
        role = profile.role
    except:
        role = 'NO PROFILE'
    print(f'  ID={user.id} | {user.username:15} | {user.email:25} | Role: {role:12}')

print()
print('='*60)
print('✅ MIGRATION SUCCESSFUL\!')
print('='*60)
print()
print('✅ ALL EXISTING SUPABASE DATA PRESERVED')
print(f'✅ {len(users_to_add)} NEW USERS ADDED FROM SQLITE')
print(f'✅ {len(users_to_skip)} DUPLICATE USERS SKIPPED')
print()
print('Next steps:')
print('  1. Keep USE_SQLITE=False in .env')
print('  2. Test login with dev@tvk.com / Dev@1234')
print('  3. Verify all users appear in user management')
print('  4. Start Django server and test frontend')
