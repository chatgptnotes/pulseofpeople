# Supabase Setup Guide - Phase 1: Core Entities
## Pulse of People Platform

**Created**: 2025-11-09
**Phase**: 1 - Foundation (Core Entities)
**Status**: Ready for Implementation

---

## 📋 Overview

This guide will help you set up the Supabase database with the Phase 1 schema (organizations, users, permissions, audit logs) and configure your application to use real data instead of hard-coded mock data.

---

## ✅ Prerequisites

Before you begin, ensure you have:

- [x] Supabase project created at https://app.supabase.com
- [x] Supabase credentials already configured in `frontend/.env`:
  - `VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co`
  - `VITE_SUPABASE_ANON_KEY=eyJhbGci...` (your key)
- [x] PostgreSQL client (psql) installed OR Supabase SQL Editor access
- [x] Basic understanding of SQL and TypeScript

---

## 🚀 Step-by-Step Setup

### Step 1: Access Supabase SQL Editor

1. Go to https://app.supabase.com
2. Select your project: `iwtgbseaoztjbnvworyq`
3. Click **SQL Editor** in the left sidebar
4. Click **+ New Query**

### Step 2: Apply Database Schema

1. Open the migration file: `supabase/migrations/20251109_phase1_core_entities.sql`
2. **Copy the entire contents** of this file
3. **Paste into the Supabase SQL Editor**
4. Click **Run** (or press Ctrl/Cmd + Enter)

**Expected Output:**
```
CREATE EXTENSION
CREATE EXTENSION
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
... (many more CREATE statements)
INSERT 0 3  (organizations)
INSERT 0 8  (users)
INSERT 0 7  (permissions)
```

### Step 3: Verify Schema Installation

Run this verification query in the SQL Editor:

```sql
-- Check all tables were created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('organizations', 'users', 'user_permissions', 'audit_logs')
ORDER BY table_name;
```

**Expected Output:**
```
audit_logs
organizations
user_permissions
users
```

### Step 4: Verify Sample Data

Check that sample data was inserted:

```sql
-- Check organizations
SELECT name, slug, type, subscription_status FROM organizations;

-- Check users
SELECT full_name, email, role FROM users ORDER BY role;

-- Check permissions
SELECT up.permission_key, u.full_name
FROM user_permissions up
JOIN users u ON up.user_id = u.id;
```

**Expected Results:**
- **3 organizations**: Democratic Alliance Party, Progressive Coalition, Citizens Forum
- **8 users**: 1 superadmin, 3 admins, 1 manager, 1 analyst, 1 user, 1 viewer
- **7 permissions**: Manager and analyst permissions

### Step 5: Configure Row Level Security (RLS)

RLS policies are already included in the migration and will be active automatically. To verify:

```sql
-- Check RLS is enabled
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN ('organizations', 'users', 'user_permissions', 'audit_logs');
```

All tables should show `rowsecurity = true`.

### Step 6: Test API Connection

Create a test file to verify the frontend can connect:

**Create: `frontend/src/test-supabase.ts`**

```typescript
import { supabase } from './services/supabase';

async function testConnection() {
  console.log('Testing Supabase connection...');

  try {
    // Test 1: Fetch organizations
    const { data: orgs, error: orgsError } = await supabase
      .from('organizations')
      .select('*');

    if (orgsError) throw orgsError;

    console.log('✅ Organizations fetched:', orgs?.length);
    console.log(orgs);

    // Test 2: Fetch users
    const { data: users, error: usersError } = await supabase
      .from('users')
      .select('*');

    if (usersError) throw usersError;

    console.log('✅ Users fetched:', users?.length);
    console.log(users);

    // Test 3: Call custom function
    const { data: permissions, error: permError } = await supabase
      .rpc('get_user_permissions', {
        p_user_id: 'cccccccc-cccc-cccc-cccc-cccccccccccc' // Manager user
      });

    if (permError) throw permError;

    console.log('✅ Permissions fetched:', permissions);

    console.log('\n🎉 All tests passed! Supabase is connected.');
  } catch (error) {
    console.error('❌ Connection failed:', error);
  }
}

testConnection();
```

Run the test:

```bash
cd frontend
npx tsx src/test-supabase.ts
```

**Expected Output:**
```
Testing Supabase connection...
✅ Organizations fetched: 3
[ { id: '...', name: 'Democratic Alliance Party', ... }, ... ]
✅ Users fetched: 8
[ { id: '...', full_name: 'Super Admin', role: 'superadmin', ... }, ... ]
✅ Permissions fetched: [ { permission_key: 'users.view' }, ... ]

🎉 All tests passed! Supabase is connected.
```

---

## 🔧 Troubleshooting

### Issue 1: "relation does not exist"

**Cause**: Migration hasn't been applied
**Fix**: Re-run Step 2 to apply the schema

### Issue 2: "permission denied for table"

**Cause**: RLS policies preventing access
**Fix**: Check that you're using the correct auth credentials

### Issue 3: "JWT expired" or "Invalid API key"

**Cause**: Environment variable misconfiguration
**Fix**: Verify `VITE_SUPABASE_ANON_KEY` in `.env` matches your project's anon key from Supabase dashboard

### Issue 4: "duplicate key value violates unique constraint"

**Cause**: Trying to run migration twice
**Fix**: Either:
- Run the rollback script at the bottom of the migration file, OR
- Drop and recreate tables manually

---

## 📊 Understanding the Schema

### Organizations Table
Stores top-level tenants/organizations using the platform.

**Key Fields:**
- `id`: UUID primary key
- `slug`: URL-safe identifier (e.g., "dap")
- `subscription_status`: trial, active, suspended, cancelled
- `is_active`: Boolean flag for account status

### Users Table
Stores all platform users with role-based access control.

**Roles (Hierarchy):**
1. **superadmin** - Platform owner, all permissions
2. **admin** - Organization owner, manage organization
3. **manager** - Manage teams and campaigns
4. **analyst** - View analytics, generate reports
5. **user** - Standard user, manage assigned tasks
6. **viewer** - Read-only access
7. **volunteer** - Field operations only

**Key Fields:**
- `organization_id`: Links to organization (multi-tenancy)
- `role`: User's role (enum)
- `is_active`: Can user log in?
- `is_verified`: Email verified?

### User Permissions Table
Granular permissions beyond role-based access.

**Permission Format:** `{category}.{action}`
**Examples:**
- `users.create` - Can create users
- `voters.view` - Can view voter database
- `reports.generate` - Can generate reports

### Audit Logs Table
Complete activity tracking for compliance and security.

**Captures:**
- Who performed the action
- What action was performed
- When it happened
- What changed (before/after values)
- IP address and user agent

---

## 🧪 Testing RLS Policies

### Test 1: Cross-Organization Isolation

```sql
-- Set auth context to user from Org 1
SET request.jwt.claim.sub = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';

-- Try to fetch users (should only see Org 1 users)
SELECT COUNT(*) FROM users; -- Should be 6 (Org 1 users only)

-- Try to access Org 2 data (should fail or return empty)
SELECT * FROM users WHERE organization_id = '22222222-2222-2222-2222-222222222222';
-- Should return 0 rows due to RLS
```

### Test 2: Role-Based Permissions

```sql
-- Set auth context to viewer (read-only role)
SET request.jwt.claim.sub = 'ffffffff-ffff-ffff-ffff-ffffffffffff';

-- Try to insert (should fail)
INSERT INTO users (organization_id, email, username, full_name, role)
VALUES ('11111111-1111-1111-1111-111111111111', 'test@dap.org', 'test', 'Test User', 'user');
-- Should error: permission denied
```

---

## 📖 Using the Services in Your App

### Example 1: Fetch All Users

```typescript
import { userService } from './services/supabase/users.service';

async function loadUsers() {
  const users = await userService.getUsersByOrganization(organizationId);
  console.log('Users:', users);
}
```

### Example 2: Create a New User

```typescript
import { useMutation } from './hooks/useSupabaseQuery';
import { userService } from './services/supabase/users.service';

function CreateUserButton() {
  const { mutate: createUser, loading } = useMutation(
    (userData) => userService.createUser(userData),
    {
      onSuccess: () => {
        alert('User created successfully!');
      }
    }
  );

  const handleCreate = () => {
    createUser({
      organization_id: 'your-org-id',
      email: 'newuser@example.com',
      username: 'newuser',
      full_name: 'New User',
      role: 'user',
      is_active: true,
    });
  };

  return (
    <button onClick={handleCreate} disabled={loading}>
      {loading ? 'Creating...' : 'Create User'}
    </button>
  );
}
```

### Example 3: Use React Hook for Querying

```typescript
import { useSupabaseQuery } from './hooks/useSupabaseQuery';
import { userService } from './services/supabase/users.service';

function UserList({ organizationId }: { organizationId: string }) {
  const { data: users, loading, error } = useSupabaseQuery(userService, {
    filters: { organization_id: organizationId, is_active: true },
    pagination: { page: 1, pageSize: 20 },
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{user.full_name} - {user.role}</li>
      ))}
    </ul>
  );
}
```

### Example 4: Real-time Subscriptions

```typescript
import { useSubscription } from './hooks/useSupabaseQuery';
import { userService } from './services/supabase/users.service';

function UserMonitor({ organizationId }: { organizationId: string }) {
  const [users, setUsers] = useState<User[]>([]);

  // Subscribe to new user creations
  useSubscription(userService, {
    filter: { column: 'organization_id', value: organizationId },
    onInsert: (newUser) => {
      setUsers(prev => [...prev, newUser]);
      alert(`New user joined: ${newUser.full_name}`);
    }
  });

  return <div>Monitoring {users.length} users...</div>;
}
```

---

## 🔒 Security Best Practices

1. **Never expose service role key**: Only use `VITE_SUPABASE_ANON_KEY` in frontend
2. **Rely on RLS**: All data access is controlled by Row Level Security policies
3. **Validate on backend**: Use Django for complex business logic and validation
4. **Audit everything**: Audit logs automatically track all write operations
5. **Rotate keys regularly**: Update Supabase keys every 90 days

---

## 📈 Next Steps

Now that Phase 1 is complete, you can:

1. ✅ **Migrate components** to use real Supabase data instead of hard-coded arrays
2. ✅ **Test multi-tenancy** by creating users in different organizations
3. ✅ **Set up authentication** using Supabase Auth
4. ⏭️ **Phase 2**: Add geography & territory tables (constituencies, booths, voters)
5. ⏭️ **Phase 3**: Add social media monitoring tables

---

## 🆘 Need Help?

- **Supabase Docs**: https://supabase.com/docs
- **RLS Guide**: https://supabase.com/docs/guides/auth/row-level-security
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

---

**Document Version**: 1.0
**Last Updated**: 2025-11-09
**Next Review**: After completing Phase 2
