-- =====================================================
-- QUICK SETUP: Create Super Admin User
-- Run this in Supabase SQL Editor after running the main migration
-- =====================================================

-- Step 1: Create Super Admin User in users table
INSERT INTO users (
  name,
  email,
  role,
  is_super_admin,
  organization_id,
  tenant_id,
  status,
  permissions,
  ward,
  constituency,
  state,
  district,
  created_at,
  updated_at
)
VALUES (
  'Super Admin',                    -- ⚠️ CHANGE THIS to your name
  'superadmin@yourdomain.com',     -- ⚠️ CHANGE THIS to your email
  'super_admin',
  TRUE,
  NULL,
  NULL,
  'active',
  ARRAY[]::TEXT[],
  NULL,
  'All',
  'All States',
  NULL,
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'super_admin',
  is_super_admin = TRUE,
  status = 'active',
  updated_at = NOW();

-- Step 2: Verify the user was created
SELECT
  id,
  name,
  email,
  role,
  is_super_admin,
  status,
  created_at
FROM users
WHERE is_super_admin = TRUE;

-- =====================================================
-- IMPORTANT: After running this SQL
-- =====================================================
-- 1. Go to Supabase Dashboard → Authentication → Users
-- 2. Click "Add User"
-- 3. Use the SAME EMAIL as above
-- 4. Set a password
-- 5. Click "Create User"
--
-- Then you can login to your app with:
-- Email: superadmin@yourdomain.com (or what you set)
-- Password: (what you created in Auth)
-- =====================================================

-- =====================================================
-- BONUS: Create Additional Test Users
-- =====================================================

-- Create an Admin user
INSERT INTO users (name, email, role, is_super_admin, status, constituency)
VALUES ('Test Admin', 'admin@test.com', 'admin', FALSE, 'active', 'Test District')
ON CONFLICT (email) DO NOTHING;

-- Create a Manager user
INSERT INTO users (name, email, role, status, constituency)
VALUES ('Test Manager', 'manager@test.com', 'manager', 'active', 'Test District')
ON CONFLICT (email) DO NOTHING;

-- Create an Analyst user
INSERT INTO users (name, email, role, status, constituency)
VALUES ('Test Analyst', 'analyst@test.com', 'analyst', 'active', 'Test District')
ON CONFLICT (email) DO NOTHING;

-- Create a Viewer user
INSERT INTO users (name, email, role, status, constituency)
VALUES ('Test Viewer', 'viewer@test.com', 'viewer', 'active', 'Test District')
ON CONFLICT (email) DO NOTHING;

-- Create a Volunteer user
INSERT INTO users (name, email, role, status, ward)
VALUES ('Test Volunteer', 'volunteer@test.com', 'volunteer', 'active', 'Ward 1')
ON CONFLICT (email) DO NOTHING;

-- Verify all users
SELECT
  id,
  name,
  email,
  role,
  is_super_admin,
  status
FROM users
ORDER BY
  CASE role
    WHEN 'super_admin' THEN 1
    WHEN 'admin' THEN 2
    WHEN 'manager' THEN 3
    WHEN 'analyst' THEN 4
    WHEN 'user' THEN 5
    WHEN 'viewer' THEN 6
    WHEN 'volunteer' THEN 7
    ELSE 8
  END;

-- =====================================================
-- REMEMBER: Create these users in Supabase Auth too!
-- =====================================================
