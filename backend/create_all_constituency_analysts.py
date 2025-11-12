#!/usr/bin/env python
"""
Create analyst accounts for ALL constituencies
One analyst per constituency
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
print("CREATING ANALYST ACCOUNTS FOR ALL CONSTITUENCIES")
print("=" * 80)
print()

# Get all constituencies
cursor = connection.cursor()
cursor.execute("""
    SELECT id, name, code, district, state
    FROM constituencies
    ORDER BY name;
""")

constituencies = cursor.fetchall()

print(f"Found {len(constituencies)} constituencies in database")
print()

# Get existing analyst accounts
cursor.execute("""
    SELECT email, full_name
    FROM users
    WHERE role = 'analyst';
""")

existing_analysts = cursor.fetchall()
existing_emails = {email for email, _ in existing_analysts}

print(f"Found {len(existing_analysts)} existing analyst accounts")
print()

# Get organization ID
cursor.execute("SELECT id FROM organizations WHERE slug = 'tvk' LIMIT 1;")
result = cursor.fetchone()
org_id = result[0] if result else '22222222-2222-2222-2222-222222222222'

print("=" * 80)
print("CREATING NEW ANALYST ACCOUNTS")
print("=" * 80)
print()

created_count = 0
already_exists_count = 0
failed_count = 0

for const_id, const_name, const_code, district_name, state in constituencies:
    # Create email from constituency name
    # Remove spaces, special chars, convert to lowercase
    email_name = const_name.lower()
    email_name = email_name.replace(' ', '').replace('-', '').replace('.', '')
    email_name = email_name.replace('(', '').replace(')', '')
    email = f"analyst.{email_name}@tvk.com"

    # Check if already exists
    if email in existing_emails:
        print(f"✓  EXISTS: {email:50} | {const_name}")
        already_exists_count += 1
        continue

    # Create analyst account
    user_data = {
        "email": email,
        "password": "Analyst@2024",
        "email_confirm": True,
        "user_metadata": {
            "role": "analyst",
            "organization_id": str(org_id),
            "full_name": f"{const_name} Analyst",
            "constituency": const_name,
            "district": district_name,
            "state": state
        }
    }

    try:
        response = requests.post(AUTH_URL, json=user_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            auth_user = response.json()
            auth_user_id = auth_user['id']

            # Create in database users table
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
            """, [
                auth_user_id,
                org_id,
                email,
                email.split('@')[0],
                f"{const_name} Analyst",
                'analyst'
            ])
            connection.commit()

            print(f"✅ CREATED: {email:50} | {const_name}")
            created_count += 1
        else:
            error_data = response.json()
            error_msg = error_data.get('msg', error_data.get('message', 'Unknown error'))

            if 'already registered' in error_msg.lower():
                print(f"⚠️  EXISTS: {email:50} | {const_name} (in Supabase Auth)")
                already_exists_count += 1
            else:
                print(f"❌ FAILED: {email:50} | {const_name} - {error_msg}")
                failed_count += 1
    except Exception as e:
        print(f"❌ EXCEPTION: {email:50} | {const_name} - {str(e)}")
        failed_count += 1

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Created: {created_count}")
print(f"✓  Already Existed: {already_exists_count}")
print(f"❌ Failed: {failed_count}")
print(f"📋 Total Constituencies: {len(constituencies)}")
print()

# Get updated count
cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'analyst';")
total_analysts = cursor.fetchone()[0]

print(f"📊 Total Analyst Accounts Now: {total_analysts}")
print()
print("=" * 80)
print("TEST CREDENTIALS")
print("=" * 80)
print()
print("Any analyst account:")
print("  Password: Analyst@2024")
print()
print("Sample logins:")
for const_id, const_name, _, _, _ in constituencies[:5]:
    email_name = const_name.lower().replace(' ', '').replace('-', '').replace('.', '')
    email_name = email_name.replace('(', '').replace(')', '')
    email = f"analyst.{email_name}@tvk.com"
    print(f"  {email}")
print()
print("=" * 80)
print("✅ ALL CONSTITUENCY ANALYSTS CREATED!")
print("=" * 80)
