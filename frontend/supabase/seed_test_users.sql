-- =====================================================
-- SEED TEST USERS - Create 11 Test Accounts
-- Run this AFTER running the RBAC migration
-- =====================================================

-- Super Admin - Platform Administrator
INSERT INTO users (
  id,
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
  '00000000-0000-0000-0000-000000000000',
  'Super Admin',
  'superadmin@pulseofpeople.com',
  'super_admin',
  TRUE,
  NULL,
  NULL,
  'active',
  ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions',
        'manage_organizations', 'view_all_data', 'manage_system_settings', 'view_audit_logs',
        'manage_billing', 'create_surveys', 'view_voters', 'edit_voters', 'delete_voters',
        'manage_field_workers', 'manage_social_channels', 'generate_ai_insights']::TEXT[],
  NULL,
  'All Organizations',
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

-- Admin - Organization Administrator
INSERT INTO users (
  id,
  name,
  email,
  role,
  is_super_admin,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'John Doe',
  'admin@bettroi.com',
  'admin',
  FALSE,
  'active',
  ARRAY['view_all', 'edit_all', 'manage_users', 'export_data', 'verify_submissions', 'edit_settings', 'manage_billing']::TEXT[],
  'All',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'admin',
  status = 'active',
  updated_at = NOW();

-- Manager - Team Manager
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000008',
  'Mike Manager',
  'manager@bettroi.com',
  'manager',
  'active',
  ARRAY['view_users', 'create_users', 'edit_users', 'view_analytics', 'view_reports', 'export_data', 'manage_field_workers']::TEXT[],
  'Central District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'manager',
  status = 'active',
  updated_at = NOW();

-- Analyst - Data Analyst
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000002',
  'Jane Smith',
  'analyst@bettroi.com',
  'analyst',
  'active',
  ARRAY['view_analytics', 'verify_submissions', 'export_data', 'view_reports', 'view_ai_insights']::TEXT[],
  'Central District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'analyst',
  status = 'active',
  updated_at = NOW();

-- User - Regular User
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000009',
  'Sam User',
  'user@bettroi.com',
  'user',
  'active',
  ARRAY['view_dashboard', 'view_analytics', 'view_reports', 'view_surveys']::TEXT[],
  'South District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'user',
  status = 'active',
  updated_at = NOW();

-- Viewer - Read-only
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000003',
  'Bob Wilson',
  'viewer@bettroi.com',
  'viewer',
  'active',
  ARRAY['view_dashboard', 'view_analytics', 'view_reports']::TEXT[],
  'South District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'viewer',
  status = 'active',
  updated_at = NOW();

-- Ward Coordinator
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  ward,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000004',
  'Priya Sharma',
  'coordinator@bettroi.com',
  'ward-coordinator',
  'active',
  ARRAY['submit_data', 'view_ward_data', 'verify_local', 'view_dashboard', 'submit_field_reports']::TEXT[],
  'Ward 15',
  'North District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'ward-coordinator',
  status = 'active',
  updated_at = NOW();

-- Social Media Manager
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000005',
  'Rahul Kumar',
  'social@bettroi.com',
  'social-media',
  'active',
  ARRAY['submit_data', 'view_social_trends', 'view_social_media', 'manage_social_channels']::TEXT[],
  'East District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'social-media',
  status = 'active',
  updated_at = NOW();

-- Survey Team
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000006',
  'Anjali Patel',
  'survey@bettroi.com',
  'survey-team',
  'active',
  ARRAY['submit_data', 'view_survey_results', 'create_surveys', 'view_surveys']::TEXT[],
  'West District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'survey-team',
  status = 'active',
  updated_at = NOW();

-- Truth Team
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000007',
  'Vikram Singh',
  'truth@bettroi.com',
  'truth-team',
  'active',
  ARRAY['submit_data', 'verify_submissions', 'view_alerts', 'view_competitor_analysis']::TEXT[],
  'Central District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'truth-team',
  status = 'active',
  updated_at = NOW();

-- Volunteer - Field Worker
INSERT INTO users (
  id,
  name,
  email,
  role,
  status,
  permissions,
  ward,
  constituency,
  created_at,
  updated_at
)
VALUES (
  '00000000-0000-0000-0000-000000000010',
  'Rita Volunteer',
  'volunteer@bettroi.com',
  'volunteer',
  'active',
  ARRAY['view_dashboard', 'submit_field_reports', 'view_surveys']::TEXT[],
  'Ward 8',
  'West District',
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'volunteer',
  status = 'active',
  updated_at = NOW();

-- Verify all users were created
SELECT
  id,
  name,
  email,
  role,
  is_super_admin,
  status,
  constituency
FROM users
WHERE email IN (
  'superadmin@pulseofpeople.com',
  'admin@bettroi.com',
  'manager@bettroi.com',
  'analyst@bettroi.com',
  'user@bettroi.com',
  'viewer@bettroi.com',
  'coordinator@bettroi.com',
  'social@bettroi.com',
  'survey@bettroi.com',
  'truth@bettroi.com',
  'volunteer@bettroi.com'
)
ORDER BY
  CASE role
    WHEN 'super_admin' THEN 1
    WHEN 'admin' THEN 2
    WHEN 'manager' THEN 3
    WHEN 'analyst' THEN 4
    WHEN 'user' THEN 5
    WHEN 'viewer' THEN 6
    WHEN 'ward-coordinator' THEN 7
    WHEN 'social-media' THEN 8
    WHEN 'survey-team' THEN 9
    WHEN 'truth-team' THEN 10
    WHEN 'volunteer' THEN 11
    ELSE 12
  END;

-- =====================================================
-- SUCCESS!
-- =====================================================
-- All 11 test users have been created in the database.
--
-- NEXT STEP: Create these users in Supabase Authentication
-- Go to: Supabase Dashboard → Authentication → Users → Add User
--
-- Create each user with:
-- - Email: (from above)
-- - Password: password
-- - Auto Confirm User: ✅ Check this
-- =====================================================
