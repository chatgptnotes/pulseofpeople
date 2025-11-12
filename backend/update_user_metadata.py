#!/usr/bin/env python
"""
Update Supabase Auth user metadata with role and organization_id
This allows RLS policies to read from JWT instead of querying database
"""
import os
import requests
from dotenv import load_dotenv
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://iwtgbseaoztjbnvworyq.supabase.co')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

if not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: SUPABASE_SERVICE_ROLE_KEY not found in .env file!")
    exit(1)

# Supabase Admin API endpoint
AUTH_URL = f"{SUPABASE_URL}/auth/v1/admin/users"

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("UPDATING SUPABASE AUTH USER METADATA")
print("=" * 80)
print()

# Get all users from database
cursor = connection.cursor()
cursor.execute("""
    SELECT id, email, role, organization_id, full_name
    FROM users
    WHERE email IS NOT NULL
    ORDER BY email;
""")

db_users = cursor.fetchall()

print(f"Found {len(db_users)} users in database")
print()

# Get all Supabase Auth users
response = requests.get(AUTH_URL, headers=headers)
if response.status_code != 200:
    print(f"❌ Failed to fetch Auth users: {response.text}")
    exit(1)

auth_users = response.json().get('users', [])
auth_users_by_email = {user['email']: user for user in auth_users}

print(f"Found {len(auth_users)} users in Supabase Auth")
print()

print("=" * 80)
print("UPDATING USER METADATA")
print("=" * 80)
print()

updated_count = 0
skipped_count = 0
failed_count = 0

for user_id, email, role, org_id, full_name in db_users:
    # Check if user exists in Auth
    auth_user = auth_users_by_email.get(email)

    if not auth_user:
        print(f"⚠️  SKIP: {email:45} - Not found in Supabase Auth")
        skipped_count += 1
        continue

    auth_user_id = auth_user['id']

    # Check if metadata already up to date
    current_metadata = auth_user.get('user_metadata', {})
    if (current_metadata.get('role') == role and
        current_metadata.get('organization_id') == str(org_id) and
        current_metadata.get('full_name') == full_name):
        print(f"✓  OK: {email:45} - Metadata already up to date")
        skipped_count += 1
        continue

    # Update user metadata
    update_data = {
        "user_metadata": {
            "role": role,
            "organization_id": str(org_id),
            "full_name": full_name
        }
    }

    try:
        update_url = f"{AUTH_URL}/{auth_user_id}"
        response = requests.put(update_url, json=update_data, headers=headers)

        if response.status_code == 200:
            print(f"✅ UPDATED: {email:45} - Role: {role:15} - Org: {str(org_id)[:8]}...")
            updated_count += 1
        else:
            error_data = response.json()
            error_msg = error_data.get('msg', error_data.get('message', 'Unknown error'))
            print(f"❌ FAILED: {email:45} - {error_msg}")
            failed_count += 1
    except Exception as e:
        print(f"❌ EXCEPTION: {email:45} - {str(e)}")
        failed_count += 1

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Updated: {updated_count}")
print(f"✓  Already OK: {skipped_count}")
print(f"❌ Failed: {failed_count}")
print(f"📋 Total: {len(db_users)}")
print()
print("=" * 80)
print("NEXT STEPS")
print("=" * 80)
print()
print("1. Run the SQL fix to update RLS functions:")
print("   psql $DATABASE_URL -f backend/fix_slow_login.sql")
print()
print("2. Or execute in Supabase SQL Editor:")
print("   - Open Supabase Dashboard")
print("   - Go to SQL Editor")
print("   - Copy contents of backend/fix_slow_login.sql")
print("   - Execute")
print()
print("3. Test login - should be much faster now!")
print()
print("=" * 80)
