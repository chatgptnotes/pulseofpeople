#!/usr/bin/env python3
"""
Check what users exist in the database
"""

import os
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://iwtgbseaoztjbnvworyq.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("CHECKING USERS IN DATABASE")
print("=" * 60)
print()

try:
    # Get all users
    result = supabase.table('users').select('id, email, full_name, role').execute()

    if result.data:
        print(f"Found {len(result.data)} users in the database:")
        print()
        for user in result.data:
            print(f"  Email: {user.get('email', 'N/A')}")
            print(f"  Name: {user.get('full_name', 'N/A')}")
            print(f"  Role: {user.get('role', 'N/A')}")
            print(f"  ID: {user.get('id', 'N/A')}")
            print()
    else:
        print("❌ No users found in the database!")
        print()
        print("This is the problem - users exist in Supabase Auth")
        print("but not in the users table.")
        print()
        print("We need to create users in the database that match")
        print("the Supabase Auth users.")

except Exception as e:
    print(f"❌ Error querying users: {e}")
