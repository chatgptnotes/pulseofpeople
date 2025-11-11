# 🔐 Supabase Authentication Setup Guide

## Quick Setup for Authentication

Follow these steps to set up authentication in your Supabase project:

## Step 1: Create Users Table

1. Go to your Supabase Dashboard
2. Navigate to SQL Editor: https://app.supabase.com/project/iwtgbseaoztjbnvworyq/sql/new
3. Copy and run the SQL from `create_users_table.sql`

## Step 2: Create Test Users in Supabase Auth

1. Go to **Authentication** → **Users** in Supabase Dashboard
2. Click **Add User** → **Create New User**
3. Create these test accounts:

### Admin User
- Email: `admin@bettroi.com`
- Password: `password123!` (or any secure password)
- ✅ Auto Confirm Email

### Regular User
- Email: `user@bettroi.com`
- Password: `password123!`
- ✅ Auto Confirm Email

### Super Admin
- Email: `superadmin@pulseofpeople.com`
- Password: `password123!`
- ✅ Auto Confirm Email

## Step 3: Create User Profiles

After creating auth users, run this SQL to create their profiles:

```sql
-- Insert admin profile
INSERT INTO public.users (id, email, name, role, permissions, is_super_admin)
SELECT
  id,
  email,
  'Admin User',
  'admin',
  ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing'],
  false
FROM auth.users
WHERE email = 'admin@bettroi.com'
ON CONFLICT (email) DO UPDATE
SET
  role = 'admin',
  permissions = ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing'];

-- Insert regular user profile
INSERT INTO public.users (id, email, name, role, permissions, is_super_admin)
SELECT
  id,
  email,
  'Regular User',
  'user',
  ARRAY['view_dashboard', 'view_analytics', 'view_reports', 'view_surveys'],
  false
FROM auth.users
WHERE email = 'user@bettroi.com'
ON CONFLICT (email) DO UPDATE
SET
  role = 'user',
  permissions = ARRAY['view_dashboard', 'view_analytics', 'view_reports', 'view_surveys'];

-- Insert super admin profile
INSERT INTO public.users (id, email, name, role, permissions, is_super_admin)
SELECT
  id,
  email,
  'Super Admin',
  'super_admin',
  ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'manage_organizations', 'view_all_data', 'manage_system_settings', 'view_audit_logs', 'manage_billing'],
  true
FROM auth.users
WHERE email = 'superadmin@pulseofpeople.com'
ON CONFLICT (email) DO UPDATE
SET
  role = 'super_admin',
  is_super_admin = true,
  permissions = ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'manage_organizations', 'view_all_data', 'manage_system_settings', 'view_audit_logs', 'manage_billing'];
```

## Step 4: Test Authentication

1. Restart your development server:
   ```bash
   npm run dev
   ```

2. Open Browser Console (F12) to see debug messages

3. Try logging in with:
   - Email: `admin@bettroi.com`
   - Password: The password you set in Supabase

## Debugging Tips

### Check Console Messages
Open browser console (F12) and look for:
- "🔐 Login attempt for: [email]"
- "Attempting Supabase authentication..."
- "✅ Supabase authentication successful!"

### Common Issues & Solutions

#### 1. "Invalid email or password"
- Verify user exists in Supabase Authentication
- Check password is correct
- Ensure user email is confirmed

#### 2. "Users table not found"
- Run the SQL script to create users table
- Check table exists in Supabase Table Editor

#### 3. Authentication works but no user data
- Make sure user profile exists in users table
- Run the INSERT statements to create profiles

#### 4. Stuck in loading state
- Check browser console for errors
- Verify Supabase URL and Anon Key in .env
- Check network tab for failed requests

## Alternative: Use Mock Authentication

If you want to skip Supabase setup for now, you can use mock authentication:

1. Login with these test accounts (no Supabase needed):
   - `admin@bettroi.com` / `password`
   - `user@bettroi.com` / `password`
   - `superadmin@pulseofpeople.com` / `password`

## Verify Your Setup

Run this SQL to check if users table exists and has data:

```sql
-- Check if table exists
SELECT EXISTS (
   SELECT FROM information_schema.tables
   WHERE table_schema = 'public'
   AND table_name = 'users'
);

-- Check user data
SELECT email, name, role, is_super_admin
FROM public.users;

-- Check auth users
SELECT email, created_at, confirmed_at
FROM auth.users;
```

## Need Help?

If authentication still doesn't work:
1. Check browser console for errors
2. Verify .env has correct Supabase credentials
3. Make sure users exist in both auth.users and public.users tables
4. Try mock authentication as fallback