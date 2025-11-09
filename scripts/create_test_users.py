#!/usr/bin/env python3
"""
Create test users in Supabase for authentication testing

This script creates Supabase Auth users and links them to existing users in the database.
"""

import os
import sys
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing environment variables!")
    print("Please set SUPABASE_URL and SUPABASE_SERVICE_KEY")
    sys.exit(1)

# Initialize Supabase client with service key (admin access)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test users to create (matching the 8 users in the database)
TEST_USERS = [
    {
        'email': 'admin@tvk.com',
        'password': 'admin123456',  # Minimum 6 characters for Supabase
        'role': 'superadmin',
        'name': 'TVK Super Admin'
    },
    {
        'email': 'admin1@tvk.com',
        'password': 'admin123456',
        'role': 'admin',
        'name': 'TVK Admin 1'
    },
    {
        'email': 'admin2@tvk.com',
        'password': 'admin123456',
        'role': 'admin',
        'name': 'TVK Admin 2'
    },
    {
        'email': 'admin3@tvk.com',
        'password': 'admin123456',
        'role': 'admin',
        'name': 'TVK Admin 3'
    },
    {
        'email': 'manager@tvk.com',
        'password': 'manager123456',
        'role': 'manager',
        'name': 'District Manager'
    },
    {
        'email': 'analyst@tvk.com',
        'password': 'analyst123456',
        'role': 'analyst',
        'name': 'Data Analyst'
    },
    {
        'email': 'user@tvk.com',
        'password': 'user123456',
        'role': 'user',
        'name': 'Field Worker'
    },
    {
        'email': 'viewer@tvk.com',
        'password': 'viewer123456',
        'role': 'viewer',
        'name': 'View Only User'
    },
]

print("=" * 60)
print("CREATING TEST USERS IN SUPABASE AUTH")
print("=" * 60)
print()

created_count = 0
already_exists_count = 0
error_count = 0

for test_user in TEST_USERS:
    try:
        print(f"📝 Creating auth user: {test_user['email']}...", end=" ")

        # Create user in Supabase Auth using Admin API
        # Note: Using admin.create_user to bypass email confirmation
        response = supabase.auth.admin.create_user({
            "email": test_user['email'],
            "password": test_user['password'],
            "email_confirm": True,  # Auto-confirm email
        })

        if response.user:
            print(f"✅ Created (ID: {response.user.id})")
            created_count += 1

            # Update the corresponding user record in the database with auth_user_id
            try:
                supabase.table('users').update({
                    'auth_user_id': response.user.id
                }).eq('email', test_user['email']).execute()
                print(f"   ✅ Linked to database user")
            except Exception as db_error:
                print(f"   ⚠️  Warning: Could not link to database: {db_error}")

        else:
            print(f"❌ Failed to create")
            error_count += 1

    except Exception as e:
        error_msg = str(e)
        if 'already been registered' in error_msg or 'User already registered' in error_msg:
            print(f"⚠️  Already exists")
            already_exists_count += 1
        else:
            print(f"❌ Error: {error_msg}")
            error_count += 1

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"✅ Created: {created_count}")
print(f"⚠️  Already existed: {already_exists_count}")
print(f"❌ Errors: {error_count}")
print()
print("=" * 60)
print("TEST CREDENTIALS")
print("=" * 60)
print()
print("You can now log in with any of these credentials:")
print()
for user in TEST_USERS:
    print(f"  {user['role'].upper():12s} - {user['email']:20s} / {user['password']}")
print()
print("=" * 60)
print("✅ SETUP COMPLETE!")
print("=" * 60)
print()
print("Next steps:")
print("1. Start the frontend: cd frontend && npm run dev")
print("2. Open http://localhost:5173")
print("3. Log in with any of the credentials above")
print()
