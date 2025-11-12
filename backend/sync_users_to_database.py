#!/usr/bin/env python
"""
Sync Supabase Auth users to the users table
This script fetches users from Supabase Auth and creates corresponding records in the users table
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
print("SYNCING SUPABASE AUTH USERS TO USERS TABLE")
print("=" * 80)
print()

# Get all Supabase Auth users
print("Fetching users from Supabase Auth...")
response = requests.get(AUTH_URL, headers=headers)

if response.status_code != 200:
    print(f"❌ Failed to fetch users: {response.text}")
    exit(1)

auth_users = response.json().get('users', [])
print(f"Found {len(auth_users)} users in Supabase Auth")
print()

# Get organization ID (we'll use the first one we find, or create one)
cursor = connection.cursor()
cursor.execute("SELECT id FROM organizations LIMIT 1;")
result = cursor.fetchone()

if result:
    org_id = result[0]
    print(f"✅ Using existing organization: {org_id}")
else:
    # Create a default organization
    print("Creating TVK organization...")
    cursor.execute("""
        INSERT INTO organizations (name, slug, organization_type, subscription_plan, subscription_status, max_users, is_active, created_at, updated_at)
        VALUES ('Tamilaga Vettri Kazhagam', 'tvk', 'party', 'enterprise', 'active', 1000, true, NOW(), NOW())
        RETURNING id;
    """)
    org_id = cursor.fetchone()[0]
    connection.commit()
    print(f"✅ Created organization: {org_id}")

print()
print("=" * 80)
print("SYNCING USERS")
print("=" * 80)
print()

synced_count = 0
skipped_count = 0
failed_count = 0

for auth_user in auth_users:
    email = auth_user['email']
    user_id = auth_user['id']
    user_metadata = auth_user.get('user_metadata', {})
    role = user_metadata.get('role', 'user')
    full_name = user_metadata.get('full_name', email.split('@')[0])

    # Check if user already exists in users table
    cursor.execute("SELECT id FROM users WHERE email = %s;", [email])
    if cursor.fetchone():
        print(f"⚠️  SKIP: {email:45} - Already exists in users table")
        skipped_count += 1
        continue

    # Create username from email
    username = email.split('@')[0].replace('.', '_')

    try:
        # Insert into users table
        cursor.execute("""
            INSERT INTO users (
                id, organization_id, email, username, full_name, role,
                is_active, is_verified, email_verified_at,
                created_at, updated_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s,
                true, true, NOW(),
                NOW(), NOW()
            );
        """, [user_id, org_id, email, username, full_name, role])

        connection.commit()
        print(f"✅ SYNCED: {email:45} - Role: {role:15}")
        synced_count += 1

    except Exception as e:
        print(f"❌ FAILED: {email:45} - Error: {str(e)}")
        failed_count += 1
        connection.rollback()

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Synced: {synced_count}")
print(f"⚠️  Skipped: {skipped_count}")
print(f"❌ Failed: {failed_count}")
print(f"📋 Total: {len(auth_users)}")
print()
print("=" * 80)
print("✅ DONE! Users are now ready for login")
print("=" * 80)
