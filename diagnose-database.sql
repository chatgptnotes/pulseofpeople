-- ============================================================================
-- DIAGNOSTIC SCRIPT - Run this first to see your database state
-- ============================================================================
-- Copy and paste this into Supabase SQL Editor to see what you have
-- ============================================================================

-- 1. What tables exist?
SELECT 'EXISTING TABLES:' as info;
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 2. What columns does organizations have?
SELECT '---' as separator;
SELECT 'ORGANIZATIONS TABLE COLUMNS:' as info;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'organizations'
ORDER BY ordinal_position;

-- 3. What data is in organizations?
SELECT '---' as separator;
SELECT 'ORGANIZATIONS DATA:' as info;
SELECT * FROM organizations;

-- 4. Check if other expected tables exist
SELECT '---' as separator;
SELECT 'OTHER TABLES CHECK:' as info;
SELECT
    'users' as table_name,
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users')
         THEN 'EXISTS' ELSE 'MISSING' END as status
UNION ALL
SELECT 'user_permissions',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_permissions')
         THEN 'EXISTS' ELSE 'MISSING' END
UNION ALL
SELECT 'audit_logs',
    CASE WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_logs')
         THEN 'EXISTS' ELSE 'MISSING' END;
