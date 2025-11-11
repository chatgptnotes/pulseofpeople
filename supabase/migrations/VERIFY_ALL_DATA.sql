-- ============================================================================
-- VERIFICATION SCRIPT - Check all Phase 1 & Phase 2 data
-- ============================================================================
-- Run this in Supabase SQL Editor to verify everything is working
-- ============================================================================

-- 1. Check all tables exist
SELECT '=== ALL TABLES ===' as section;
SELECT table_name,
       (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as columns
FROM information_schema.tables t
WHERE table_schema = 'public'
  AND table_name IN ('organizations', 'users', 'user_permissions', 'audit_logs',
                     'constituencies', 'wards', 'polling_booths', 'voters')
ORDER BY table_name;

-- 2. Count rows in each table
SELECT '=== ROW COUNTS ===' as section;

SELECT 'organizations' as table_name, COUNT(*) as rows FROM organizations
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'user_permissions', COUNT(*) FROM user_permissions
UNION ALL
SELECT 'audit_logs', COUNT(*) FROM audit_logs
UNION ALL
SELECT 'constituencies', COUNT(*) FROM constituencies
UNION ALL
SELECT 'wards', COUNT(*) FROM wards
UNION ALL
SELECT 'polling_booths', COUNT(*) FROM polling_booths
UNION ALL
SELECT 'voters', COUNT(*) FROM voters
ORDER BY table_name;

-- 3. Check Phase 1 data - Organizations
SELECT '=== ORGANIZATIONS ===' as section;
SELECT id, name, slug, type, subscription_status, is_active
FROM organizations
ORDER BY name;

-- 4. Check Phase 1 data - Users
SELECT '=== USERS ===' as section;
SELECT id, username, email, role, full_name, is_active, is_verified
FROM users
ORDER BY role, username;

-- 5. Check Phase 1 data - User Permissions
SELECT '=== USER PERMISSIONS ===' as section;
SELECT up.id,
       u.username,
       up.permission_key,
       up.granted_at
FROM user_permissions up
JOIN users u ON up.user_id = u.id
ORDER BY u.username, up.permission_key;

-- 6. Check Phase 2 data - Constituencies
SELECT '=== CONSTITUENCIES ===' as section;
SELECT id, name, code, type, state, district, population, voter_count, total_booths
FROM constituencies
ORDER BY code;

-- 7. Check Phase 2 data - Wards
SELECT '=== WARDS ===' as section;
SELECT w.id,
       c.code as constituency_code,
       w.name,
       w.code,
       w.ward_number,
       w.population,
       w.voter_count
FROM wards w
JOIN constituencies c ON w.constituency_id = c.id
ORDER BY c.code, w.ward_number;

-- 8. Check Phase 2 data - Polling Booths
SELECT '=== POLLING BOOTHS ===' as section;
SELECT pb.id,
       c.code as constituency_code,
       pb.booth_number,
       pb.name,
       pb.latitude,
       pb.longitude,
       pb.total_voters,
       pb.male_voters,
       pb.female_voters,
       pb.is_active
FROM polling_booths pb
JOIN constituencies c ON pb.constituency_id = c.id
ORDER BY c.code, pb.booth_number;

-- 9. Check Phase 2 data - Voters (should be 0 for now)
SELECT '=== VOTERS ===' as section;
SELECT COUNT(*) as total_voters FROM voters;

-- 10. Test PostGIS functions
SELECT '=== POSTGIS TEST ===' as section;
SELECT 'PostGIS Version: ' || PostGIS_Version() as info;

-- 11. Test spatial query - Find booths near a point (Chennai center)
SELECT '=== SPATIAL QUERY TEST ===' as section;
SELECT booth_id, booth_name, distance_meters
FROM find_booths_near(13.0827, 80.2707, 10000)
LIMIT 5;

-- 12. Test RLS policies (check if enabled)
SELECT '=== RLS STATUS ===' as section;
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('organizations', 'users', 'user_permissions', 'audit_logs',
                    'constituencies', 'wards', 'polling_booths', 'voters')
ORDER BY tablename;

-- 13. Check functions exist
SELECT '=== FUNCTIONS ===' as section;
SELECT proname as function_name,
       pg_get_function_arguments(oid) as arguments
FROM pg_proc
WHERE proname IN (
    'update_updated_at_column',
    'get_user_permissions',
    'has_permission',
    'update_constituency_voter_count',
    'update_booth_voter_count',
    'sync_geography_from_boundaries',
    'sync_location_from_coordinates',
    'find_booths_near',
    'get_constituency_stats'
)
ORDER BY proname;

-- 14. Final summary
SELECT '=== SUMMARY ===' as section;
SELECT
    'Phase 1 Tables' as metric,
    COUNT(*) FILTER (WHERE table_name IN ('organizations', 'users', 'user_permissions', 'audit_logs')) as count
FROM information_schema.tables
WHERE table_schema = 'public'
UNION ALL
SELECT
    'Phase 2 Tables',
    COUNT(*) FILTER (WHERE table_name IN ('constituencies', 'wards', 'polling_booths', 'voters'))
FROM information_schema.tables
WHERE table_schema = 'public'
UNION ALL
SELECT 'Total Organizations', COUNT(*)::integer FROM organizations
UNION ALL
SELECT 'Total Users', COUNT(*)::integer FROM users
UNION ALL
SELECT 'Total Constituencies', COUNT(*)::integer FROM constituencies
UNION ALL
SELECT 'Total Wards', COUNT(*)::integer FROM wards
UNION ALL
SELECT 'Total Polling Booths', COUNT(*)::integer FROM polling_booths
UNION ALL
SELECT 'Total Voters', COUNT(*)::integer FROM voters;

SELECT '✅ Verification Complete!' as status;
