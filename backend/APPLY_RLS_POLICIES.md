# How to Apply Row-Level Security (RLS) Policies to Supabase

This guide walks you through applying the RLS policies defined in `supabase_rls_policies.sql` to your Supabase database.

## Prerequisites

- Access to your Supabase Dashboard
- Project: `pulseofpeople` (iwtgbseaoztjbnvworyq)
- Dashboard URL: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq

## Option 1: Supabase Dashboard SQL Editor (Recommended)

### Step 1: Open SQL Editor

1. Go to https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
2. Click **SQL Editor** in the left sidebar
3. Click **New query** button

### Step 2: Copy RLS Policies SQL

1. Open the file: `/Users/murali/Applications/pulseofpeople/backend/supabase_rls_policies.sql`
2. Copy the **entire contents** of the file

### Step 3: Execute the SQL

1. Paste the SQL into the SQL Editor
2. Click **Run** button (or press Cmd+Enter)
3. Wait for execution to complete

### Step 4: Verify RLS is Enabled

Run this verification query in the SQL Editor:

```sql
-- Check which tables have RLS enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND tablename LIKE 'api_%'
ORDER BY tablename;
```

You should see `rowsecurity = true` for these tables:
- api_userprofile
- api_notification
- api_campaign
- api_voter
- api_alert
- api_expense
- api_auditlog
- api_boothagent
- api_uploadedfile
- api_twofactorbackupcode

### Step 5: Verify Policies Created

Run this query to see all policies:

```sql
-- Check all RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;
```

You should see policies like:
- "Users can view profiles in their organization"
- "Users can view own profile"
- "Admins can manage organization profiles"
- etc.

## Option 2: psql Command Line

If you prefer using the command line:

### Step 1: Get Database Connection String

From your `.env` file, the connection details are:
- **Host**: db.iwtgbseaoztjbnvworyq.supabase.co
- **Port**: 5432
- **Database**: postgres
- **User**: postgres
- **Password**: Sx6d9d82FcG3!DT

### Step 2: Apply SQL File

```bash
# Set password as environment variable
export PGPASSWORD='Sx6d9d82FcG3!DT'

# Apply the SQL file
psql -h db.iwtgbseaoztjbnvworyq.supabase.co \
     -p 5432 \
     -U postgres \
     -d postgres \
     -f supabase_rls_policies.sql
```

### Step 3: Verify (same as Option 1 Step 4-5)

## What the RLS Policies Do

### 1. **Organization Isolation**
- Users can only see data from their own organization (TVK or DMK)
- Enforced at database level (cannot be bypassed from frontend)

### 2. **Role-Based Access**
- **Superadmin**: Can see all organizations
- **Admin**: Can manage all data in their organization
- **Manager**: Can manage their district's data
- **Analyst**: Can manage their constituency's data
- **User**: Can see limited data based on their role

### 3. **Helper Functions**
Two PostgreSQL functions are created:
- `auth.get_user_organization_id()`: Extracts org ID from JWT token
- `auth.get_user_role()`: Extracts role from JWT token

### 4. **Automatic JWT Integration**
- When users log in via Supabase Auth, their JWT contains:
  - `user_metadata.organization_id`
  - `user_metadata.role`
  - `user_metadata.organization_slug`
- RLS policies automatically use this metadata to filter queries

## Testing RLS Policies

### Test 1: Login as TVK Manager

```bash
# Login via frontend as manager.chennai@tvk.org
# Password: Manager@CHE2025

# Try to query voters - should only see TVK voters
SELECT * FROM api_voter LIMIT 10;
```

### Test 2: Login as DMK Admin

```bash
# Login as admin@dmk.org
# Password: DmkAdmin@2025

# Should only see DMK data, not TVK data
SELECT organization_id FROM api_userprofile WHERE user_id = auth.uid();
```

### Test 3: Verify Cross-Organization Isolation

```sql
-- As TVK user, this should return 0 rows
SELECT COUNT(*) FROM api_campaign
WHERE created_by_id IN (
  SELECT user_id FROM api_userprofile
  WHERE organization_id != auth.get_user_organization_id()
);
```

## Troubleshooting

### Error: "function auth.jwt() does not exist"

**Solution**: You're not using Supabase Auth properly. Make sure:
1. Users are authenticated via Supabase Auth
2. JWT token is passed in requests
3. You're querying through Supabase client (not direct PostgreSQL)

### Error: "permission denied for table api_userprofile"

**Solution**: Run the GRANT statements at the bottom of `supabase_rls_policies.sql`:

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON api_userprofile TO authenticated;
GRANT SELECT, INSERT, UPDATE ON api_notification TO authenticated;
-- etc.
```

### RLS Blocking All Queries

**Solution**: Check that user metadata is set correctly:

```sql
-- Check current user's JWT metadata
SELECT
  auth.uid() as user_id,
  auth.get_user_organization_id() as org_id,
  auth.get_user_role() as role;
```

If these return NULL, the user's JWT doesn't have proper metadata. Re-create the user with metadata.

## Next Steps

After applying RLS policies:

1. ✅ **Test authentication flow** - Login via frontend
2. ✅ **Verify data isolation** - TVK users can't see DMK data
3. ✅ **Test real-time updates** - Notifications should be filtered by RLS
4. ✅ **Monitor performance** - RLS queries should be fast (indexed properly)

## Security Best Practices

1. **Never bypass RLS** - Don't use service role key from frontend
2. **Always use authenticated role** - Regular users should use `authenticated` role
3. **Test with real users** - Don't just test with service role
4. **Monitor RLS performance** - Add indexes on `organization_id` if queries are slow
5. **Regular audits** - Review policies quarterly to ensure they're still correct

## Additional Resources

- Supabase RLS Documentation: https://supabase.com/docs/guides/auth/row-level-security
- PostgreSQL RLS Reference: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- Your RLS Policies File: `backend/supabase_rls_policies.sql`
