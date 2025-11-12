#!/usr/bin/env python
"""
Create users in Supabase Auth (not Django auth)
This script creates users directly in Supabase using the Admin API
"""
import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://iwtgbseaoztjbnvworyq.supabase.co')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

if not SUPABASE_SERVICE_KEY:
    print("❌ ERROR: SUPABASE_SERVICE_ROLE_KEY not found in .env file!")
    print("   Please add your service role key to backend/.env")
    exit(1)

# Supabase Admin API endpoint
AUTH_URL = f"{SUPABASE_URL}/auth/v1/admin/users"

headers = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("CREATING USERS IN SUPABASE AUTH")
print("=" * 80)
print()

# Test users to create
users_to_create = [
    {
        "email": "superadmin@pulseofpeople.com",
        "password": "Admin@123",
        "email_confirm": True,
        "user_metadata": {
            "role": "superadmin",
            "full_name": "Super Administrator"
        }
    },
    {
        "email": "vijay@tvk.com",
        "password": "Vijay@2026",
        "email_confirm": True,
        "user_metadata": {
            "role": "admin",
            "full_name": "Vijay",
            "organization": "TVK"
        }
    },
    {
        "email": "manager.chennai@tvk.com",
        "password": "Manager@2024",
        "email_confirm": True,
        "user_metadata": {
            "role": "manager",
            "full_name": "Chennai Manager",
            "district": "Chennai",
            "organization": "TVK"
        }
    },
    {
        "email": "analyst.gummidipoondi@tvk.com",
        "password": "Analyst@2024",
        "email_confirm": True,
        "user_metadata": {
            "role": "analyst",
            "full_name": "Gummidipoondi Analyst",
            "constituency": "Gummidipoondi",
            "organization": "TVK"
        }
    },
    {
        "email": "user1@tvk.com",
        "password": "User@2024",
        "email_confirm": True,
        "user_metadata": {
            "role": "user",
            "full_name": "User 1",
            "organization": "TVK"
        }
    },
    {
        "email": "volunteer1@tvk.com",
        "password": "Volunteer@2024",
        "email_confirm": True,
        "user_metadata": {
            "role": "volunteer",
            "full_name": "Volunteer 1",
            "organization": "TVK"
        }
    }
]

created_count = 0
failed_count = 0

for user_data in users_to_create:
    email = user_data["email"]
    role = user_data["user_metadata"]["role"]

    print(f"Creating {role}: {email}...", end=" ")

    try:
        response = requests.post(AUTH_URL, json=user_data, headers=headers)

        if response.status_code == 200 or response.status_code == 201:
            print("✅ SUCCESS")
            created_count += 1
        else:
            error_data = response.json()
            error_msg = error_data.get('msg', error_data.get('message', 'Unknown error'))

            # Check if user already exists
            if 'already registered' in error_msg.lower() or 'already exists' in error_msg.lower():
                print(f"⚠️  ALREADY EXISTS")
            else:
                print(f"❌ FAILED: {error_msg}")
                failed_count += 1
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        failed_count += 1

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"✅ Created: {created_count}")
print(f"❌ Failed: {failed_count}")
print(f"📋 Total: {len(users_to_create)}")
print()
print("=" * 80)
print("TEST CREDENTIALS")
print("=" * 80)
print()
print("Superadmin:")
print("  Email:    superadmin@pulseofpeople.com")
print("  Password: Admin@123")
print()
print("TVK Admin (Vijay):")
print("  Email:    vijay@tvk.com")
print("  Password: Vijay@2026")
print()
print("Manager:")
print("  Email:    manager.chennai@tvk.com")
print("  Password: Manager@2024")
print()
print("Analyst:")
print("  Email:    analyst.gummidipoondi@tvk.com")
print("  Password: Analyst@2024")
print()
print("User:")
print("  Email:    user1@tvk.com")
print("  Password: User@2024")
print()
print("Volunteer:")
print("  Email:    volunteer1@tvk.com")
print("  Password: Volunteer@2024")
print()
print("=" * 80)
print("✅ DONE! You can now login at http://localhost:5174")
print("=" * 80)
