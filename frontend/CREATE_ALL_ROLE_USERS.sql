-- =====================================================
-- CREATE ALL ROLE HIERARCHY USERS
-- Run this in Supabase SQL Editor
-- =====================================================
--
-- This script creates 5 test users for the role hierarchy:
-- superadmin → admin → manager → analyst → user
--
-- IMPORTANT: After running this SQL, you must ALSO create
-- these users in Supabase Authentication manually.
-- See instructions at the bottom.
-- =====================================================

BEGIN;

-- Delete existing test users if they exist
DELETE FROM users
WHERE email IN (
  'superadmin@pulseofpeople.com',
  'admin@tvk.com',
  'manager@tvk.com',
  'analyst@tvk.com',
  'user@tvk.com'
);

-- =====================================================
-- 1. SUPERADMIN - Platform Owner
-- =====================================================
INSERT INTO users (
  id,
  email,
  full_name,
  role,
  is_super_admin,
  constituency,
  state,
  permissions,
  status,
  created_at,
  updated_at
) VALUES (
  gen_random_uuid(),
  'superadmin@pulseofpeople.com',
  'TVK Super Admin',
  'superadmin',
  true,
  'All Organizations',
  'All States',
  ARRAY['*']::TEXT[],
  'active',
  NOW(),
  NOW()
);

-- =====================================================
-- 2. ADMIN - Organization Admin
-- =====================================================
INSERT INTO users (
  id,
  email,
  full_name,
  role,
  is_super_admin,
  constituency,
  permissions,
  status,
  created_at,
  updated_at
) VALUES (
  gen_random_uuid(),
  'admin@tvk.com',
  'TVK Admin',
  'admin',
  false,
  'All',
  ARRAY['view_all', 'edit_all', 'manage_users', 'export_data']::TEXT[],
  'active',
  NOW(),
  NOW()
);

-- =====================================================
-- 3. MANAGER - District Manager
-- =====================================================
INSERT INTO users (
  id,
  email,
  full_name,
  role,
  is_super_admin,
  constituency,
  permissions,
  status,
  created_at,
  updated_at
) VALUES (
  gen_random_uuid(),
  'manager@tvk.com',
  'TVK Manager',
  'manager',
  false,
  'Chennai District',
  ARRAY['view_users', 'create_users', 'view_analytics', 'export_data']::TEXT[],
  'active',
  NOW(),
  NOW()
);

-- =====================================================
-- 4. ANALYST - Constituency Analyst
-- =====================================================
INSERT INTO users (
  id,
  email,
  full_name,
  role,
  is_super_admin,
  constituency,
  permissions,
  status,
  created_at,
  updated_at
) VALUES (
  gen_random_uuid(),
  'analyst@tvk.com',
  'TVK Analyst',
  'analyst',
  false,
  'Perambur Constituency',
  ARRAY['view_analytics', 'verify_submissions', 'export_data']::TEXT[],
  'active',
  NOW(),
  NOW()
);

-- =====================================================
-- 5. USER - Booth Agent
-- =====================================================
INSERT INTO users (
  id,
  email,
  full_name,
  role,
  is_super_admin,
  constituency,
  ward,
  permissions,
  status,
  created_at,
  updated_at
) VALUES (
  gen_random_uuid(),
  'user@tvk.com',
  'TVK User',
  'user',
  false,
  'Booth B-456',
  'Ward 15',
  ARRAY['view_dashboard', 'submit_data']::TEXT[],
  'active',
  NOW(),
  NOW()
);

COMMIT;

-- =====================================================
-- Verify users were created
-- =====================================================
SELECT
  id,
  email,
  full_name,
  role,
  is_super_admin,
  constituency,
  status
FROM users
WHERE email IN (
  'superadmin@pulseofpeople.com',
  'admin@tvk.com',
  'manager@tvk.com',
  'analyst@tvk.com',
  'user@tvk.com'
)
ORDER BY
  CASE role
    WHEN 'superadmin' THEN 1
    WHEN 'admin' THEN 2
    WHEN 'manager' THEN 3
    WHEN 'analyst' THEN 4
    WHEN 'user' THEN 5
    ELSE 6
  END;

-- =====================================================
-- ✅ SUCCESS! Database records created.
-- =====================================================
--
-- ⚠️  IMPORTANT: Now you MUST create these users in
-- Supabase Authentication (manually)
--
-- 📝 INSTRUCTIONS:
--
-- 1. Go to Supabase Dashboard:
--    https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users
--
-- 2. Click "Add User" button (top right)
--
-- 3. Create each user with these credentials:
--
--    User 1 (Superadmin):
--    - Email: superadmin@pulseofpeople.com
--    - Password: SuperAdmin@123
--    - ✅ CHECK "Auto Confirm User"
--    - Click "Create User"
--
--    User 2 (Admin):
--    - Email: admin@tvk.com
--    - Password: Admin@123
--    - ✅ CHECK "Auto Confirm User"
--    - Click "Create User"
--
--    User 3 (Manager):
--    - Email: manager@tvk.com
--    - Password: Manager@123
--    - ✅ CHECK "Auto Confirm User"
--    - Click "Create User"
--
--    User 4 (Analyst):
--    - Email: analyst@tvk.com
--    - Password: Analyst@123
--    - ✅ CHECK "Auto Confirm User"
--    - Click "Create User"
--
--    User 5 (User):
--    - Email: user@tvk.com
--    - Password: User@123
--    - ✅ CHECK "Auto Confirm User"
--    - Click "Create User"
--
-- 4. After creating all 5 users, test by:
--    - Go to http://localhost:5173/login
--    - Login with each credential
--    - Click profile icon (bottom left)
--    - Verify role badge matches
--
-- =====================================================
-- 🔑 TEST CREDENTIALS SUMMARY
-- =====================================================
--
-- 1. SUPERADMIN: superadmin@pulseofpeople.com / SuperAdmin@123
-- 2. ADMIN:      admin@tvk.com / Admin@123
-- 3. MANAGER:    manager@tvk.com / Manager@123
-- 4. ANALYST:    analyst@tvk.com / Analyst@123
-- 5. USER:       user@tvk.com / User@123
--
-- =====================================================
