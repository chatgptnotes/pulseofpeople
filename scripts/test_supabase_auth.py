#!/usr/bin/env python3
"""
Test Supabase authentication to verify API keys and login functionality
"""

import os
import sys
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://iwtgbseaoztjbnvworyq.supabase.co')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3dGdic2Vhb3p0amJudndvcnlxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjExNjAzOTksImV4cCI6MjA3NjczNjM5OX0.xA4B0XZJE_4MdjFCkw2yVsf4vlHmHfpeV6Bk5tG2T94')

print("=" * 60)
print("TESTING SUPABASE AUTHENTICATION")
print("=" * 60)
print()

# Test connection
print("1. Testing Supabase connection...")
print(f"   URL: {SUPABASE_URL}")
print(f"   Anon Key: {SUPABASE_ANON_KEY[:20]}...")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("   ✅ Supabase client created successfully")
except Exception as e:
    print(f"   ❌ Failed to create Supabase client: {e}")
    sys.exit(1)

# Test authentication with a test user
print("\n2. Testing authentication with test user...")
print("   Email: admin@tvk.com")
print("   Password: admin123456")

try:
    response = supabase.auth.sign_in_with_password({
        "email": "admin@tvk.com",
        "password": "admin123456"
    })

    if response.user:
        print(f"   ✅ Login successful!")
        print(f"   User ID: {response.user.id}")
        print(f"   Email: {response.user.email}")
        print(f"   Email confirmed: {response.user.email_confirmed_at is not None}")
    else:
        print("   ❌ Login failed - no user returned")

except Exception as e:
    print(f"   ❌ Login error: {e}")
    print("\n   Possible issues:")
    print("   - User doesn't exist in Supabase Auth")
    print("   - Password is incorrect")
    print("   - Email confirmation required")
    print("   - API keys are incorrect")
    sys.exit(1)

# Test fetching user data from database
print("\n3. Testing user data from database...")
try:
    user_data = supabase.table('users').select('*').eq('email', 'admin@tvk.com').execute()

    if user_data.data and len(user_data.data) > 0:
        user = user_data.data[0]
        print(f"   ✅ User found in database!")
        print(f"   Name: {user.get('full_name', 'N/A')}")
        print(f"   Role: {user.get('role', 'N/A')}")
        print(f"   Organization ID: {user.get('organization_id', 'N/A')}")
    else:
        print("   ⚠️  User not found in database")
        print("   Note: User exists in Auth but not in users table")

except Exception as e:
    print(f"   ❌ Database query error: {e}")

# Sign out
print("\n4. Testing sign out...")
try:
    supabase.auth.sign_out()
    print("   ✅ Sign out successful")
except Exception as e:
    print(f"   ❌ Sign out error: {e}")

print()
print("=" * 60)
print("AUTHENTICATION TEST COMPLETE")
print("=" * 60)
print()
print("If all tests passed, your Supabase authentication is working correctly!")
print()
