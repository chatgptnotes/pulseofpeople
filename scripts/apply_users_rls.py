#!/usr/bin/env python3
"""
Apply RLS policies to the users table to enable authenticated access
"""

import os
import sys
from supabase import create_client, Client

# Load environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://iwtgbseaoztjbnvworyq.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_KEY:
    print("❌ SUPABASE_SERVICE_KEY not set!")
    print("Please run:")
    print("export SUPABASE_SERVICE_KEY='your-service-key'")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("APPLYING RLS POLICIES TO USERS TABLE")
print("=" * 60)
print()

# Read the migration file
migration_file = 'supabase/migrations/20251109_enable_users_rls.sql'

try:
    with open(migration_file, 'r') as f:
        sql = f.read()

    print(f"📄 Reading migration: {migration_file}")
    print()

    # Execute the SQL
    print("⚙️  Applying RLS policies...")
    result = supabase.rpc('exec_sql', {'sql': sql}).execute()

    print("✅ RLS policies applied successfully!")
    print()

except FileNotFoundError:
    print(f"❌ Migration file not found: {migration_file}")
    print()
    print("Manual steps:")
    print("1. Go to Supabase Dashboard → SQL Editor")
    print("2. Run the following SQL:")
    print()
    print("-- Enable RLS")
    print("ALTER TABLE users ENABLE ROW LEVEL SECURITY;")
    print()
    print("-- Allow users to view their own data")
    print("CREATE POLICY \"Users can view their own data\"")
    print("ON users FOR SELECT")
    print("USING (auth.email() = email);")
    print()
    print("-- Grant permissions")
    print("GRANT SELECT, UPDATE ON users TO authenticated;")
    print()
    sys.exit(1)

except Exception as e:
    print(f"⚠️  Could not apply via RPC (this is normal)")
    print(f"Error: {e}")
    print()
    print("=" * 60)
    print("MANUAL SETUP REQUIRED")
    print("=" * 60)
    print()
    print("Please apply the RLS policies manually:")
    print()
    print("1. Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq")
    print("2. Navigate to: SQL Editor")
    print("3. Copy and paste this SQL:")
    print()
    print("-" * 60)

    with open(migration_file, 'r') as f:
        print(f.read())

    print("-" * 60)
    print()
    print("4. Click 'Run' to execute the SQL")
    print()

print("=" * 60)
print("NEXT STEPS")
print("=" * 60)
print()
print("After applying RLS policies:")
print("1. Refresh the login page: http://localhost:5174/")
print("2. Try logging in again with: admin@tvk.com / admin123456")
print("3. The user profile should now load successfully")
print()
