-- ============================================================================
-- CHECK DATABASE STATE
-- ============================================================================
-- Run this in Supabase SQL Editor to see what's already in your database
-- ============================================================================

-- 1. Check which tables exist
SELECT
    table_name,
    (SELECT COUNT(*)
     FROM information_schema.columns
     WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN (
    'organizations', 'users', 'user_permissions', 'audit_logs',
    'constituencies', 'wards', 'polling_booths', 'voters'
  )
ORDER BY table_name;

-- 2. Check data in existing tables
SELECT
    'organizations' as table_name,
    COUNT(*) as row_count
FROM organizations
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'user_permissions', COUNT(*) FROM user_permissions
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs
UNION ALL
SELECT 'constituencies', COUNT(*)
FROM constituencies
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'constituencies')
UNION ALL
SELECT 'wards', COUNT(*)
FROM wards
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'wards')
UNION ALL
SELECT 'polling_booths', COUNT(*)
FROM polling_booths
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'polling_booths')
UNION ALL
SELECT 'voters', COUNT(*)
FROM voters
WHERE EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'voters')
ORDER BY table_name;

-- 3. Check if RLS is enabled
SELECT
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN (
    'organizations', 'users', 'user_permissions', 'audit_logs',
    'constituencies', 'wards', 'polling_booths', 'voters'
  )
ORDER BY tablename;

-- 4. Check if sample data exists (organizations)
SELECT id, name, slug, type, subscription_status
FROM organizations
ORDER BY name;

-- 5. Check if sample data exists (users)
SELECT id, email, role, is_active
FROM users
ORDER BY role, email;
