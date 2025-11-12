#!/usr/bin/env python
"""
Sync ALL Supabase Auth users to the users table (with pagination support)
This script fetches ALL users from Supabase Auth and creates corresponding records in the users table
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

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("SYNCING ALL SUPABASE AUTH USERS TO USERS TABLE")
print("=" * 80)
print()

# Fetch ALL users from Supabase Auth (with pagination)
print("Fetching ALL users from Supabase Auth (with pagination)...")
all_auth_users = []
page = 1
per_page = 1000

while True:
    url = f"{SUPABASE_URL}/auth/v1/admin/users?page={page}&per_page={per_page}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Error fetching page {page}: {response.text}")
        break

    data = response.json()
    users = data.get('users', [])

    if not users:
        break

    all_auth_users.extend(users)
    print(f"  Page {page}: Fetched {len(users)} users (Total: {len(all_auth_users)})")

    if len(users) < per_page:
        break

    page += 1

print(f"\n✅ Found {len(all_auth_users)} users in Supabase Auth")
print()

# Get organization ID
cursor = connection.cursor()
cursor.execute("SELECT id FROM organizations WHERE slug = 'tvk' LIMIT 1;")
result = cursor.fetchone()

if result:
    org_id = result[0]
    print(f"✅ Using organization: {org_id}")
else:
    print("Creating TVK organization...")
    cursor.execute("""
        INSERT INTO organizations (name, slug, organization_type, subscription_plan, subscription_status, max_users, is_active, created_at, updated_at)
        VALUES ('Tamilaga Vettri Kazhagam', 'tvk', 'party', 'enterprise', 'active', 10000, true, NOW(), NOW())
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

for auth_user in all_auth_users:
    email = auth_user['email']
    user_id = auth_user['id']
    user_metadata = auth_user.get('user_metadata', {})
    role = user_metadata.get('role', 'user')
    full_name = user_metadata.get('full_name', email.split('@')[0])

    # Check if user already exists in users table
    cursor.execute("SELECT id FROM users WHERE id = %s;", [user_id])
    if cursor.fetchone():
        skipped_count += 1
        if skipped_count <= 10:  # Only show first 10 skips
            print(f"⚠️  SKIP: {email:45} - Already exists")
        elif skipped_count == 11:
            print(f"⚠️  ... (hiding remaining skipped users for brevity)")
        continue

    # Create username from email
    username = email.split('@')[0].replace('.', '_').replace('-', '_')

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
        print(f"❌ FAILED: {email:45} - Error: {str(e)[:50]}")
        failed_count += 1
        connection.rollback()

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Synced: {synced_count}")
print(f"⚠️  Skipped: {skipped_count}")
print(f"❌ Failed: {failed_count}")
print(f"📋 Total in Auth: {len(all_auth_users)}")
print()

# Get final count in users table
cursor.execute("SELECT COUNT(*) FROM users;")
total_users = cursor.fetchone()[0]
print(f"📊 Total users in public.users table: {total_users}")
print()
print("=" * 80)
print("✅ DONE! All users are now synced")
print("=" * 80)
