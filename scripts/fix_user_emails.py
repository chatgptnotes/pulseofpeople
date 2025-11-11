#!/usr/bin/env python3
"""
Fix user emails to match TVK branding and Supabase Auth users
"""

import os
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://iwtgbseaoztjbnvworyq.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("FIXING USER EMAILS FOR TVK")
print("=" * 60)
print()

# Mapping of old emails to new emails
email_mappings = [
    ('super@dap.org', 'admin@tvk.com', 'TVK Super Admin'),
    ('admin@dap.org', 'admin1@tvk.com', 'TVK Admin 1'),
    ('manager@dap.org', 'manager@tvk.com', 'District Manager'),
    ('analyst@dap.org', 'analyst@tvk.com', 'Data Analyst'),
    ('user@dap.org', 'user@tvk.com', 'Field Worker'),
    ('viewer@dap.org', 'viewer@tvk.com', 'View Only User'),
    ('admin@pc.org', 'admin2@tvk.com', 'TVK Admin 2'),
    ('admin@cf.org', 'admin3@tvk.com', 'TVK Admin 3'),
]

for old_email, new_email, new_name in email_mappings:
    try:
        print(f"Updating: {old_email} → {new_email}")

        # Update the user in the database
        result = supabase.table('users').update({
            'email': new_email,
            'full_name': new_name
        }).eq('email', old_email).execute()

        if result.data:
            print(f"  ✅ Updated successfully")
        else:
            print(f"  ⚠️  User not found with email: {old_email}")

    except Exception as e:
        print(f"  ❌ Error: {e}")

print()
print("=" * 60)
print("EMAIL UPDATE COMPLETE")
print("=" * 60)
print()
print("Now run create_test_users.py to create matching Supabase Auth users")
print()
