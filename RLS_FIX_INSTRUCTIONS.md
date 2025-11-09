# 🔧 FIX RLS INFINITE RECURSION ERROR

## Problem
Your Supabase database has an infinite recursion error in RLS (Row Level Security) policies that prevents API queries from working.

## Solution Options

### ✅ **Option 1: Execute SQL in Supabase Dashboard (RECOMMENDED)**

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
   - Navigate to: SQL Editor (left sidebar)

2. **Copy and Paste the SQL**
   - Open: `supabase/migrations/20251109120000_fix_rls_final.sql`
   - Copy all the SQL code
   - Paste into the SQL Editor
   - Click "RUN" button

3. **Verify the Fix**
   - Run this query in SQL Editor:
   ```sql
   SELECT * FROM organizations;
   ```
   - You should see 3 organizations without errors

---

### 🔄 **Option 2: Use Service Role Key (Quick Workaround)**

If you need immediate access while fixing RLS, update your frontend to use the **service role key** for backend queries:

**⚠️ WARNING: Service role key bypasses RLS. Only use server-side, NEVER expose in frontend code.**

```typescript
// Create a separate server-side Supabase client
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://iwtgbseaoztjbnvworyq.supabase.co';
const supabaseServiceKey = 'YOUR_SERVICE_ROLE_KEY_HERE'; // Get from Supabase dashboard

// Server-side only client (bypasses RLS)
export const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false
  }
});

// Use for admin operations
const { data: organizations } = await supabaseAdmin
  .from('organizations')
  .select('*');
```

**To get your Service Role Key:**
1. Go to: Settings → API
2. Find: `service_role` secret (not `anon` public)
3. Click "Reveal" and copy

---

### 🛠️ **Option 3: Temporarily Disable RLS (Development Only)**

**⚠️ WARNING: This removes all security. Only use in development/local testing.**

Run in SQL Editor:
```sql
ALTER TABLE organizations DISABLE ROW LEVEL SECURITY;
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE constituencies DISABLE ROW LEVEL SECURITY;
ALTER TABLE wards DISABLE ROW LEVEL SECURITY;
ALTER TABLE polling_booths DISABLE ROW LEVEL SECURITY;
ALTER TABLE voters DISABLE ROW LEVEL SECURITY;
```

To re-enable later:
```sql
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
-- ... (repeat for all tables)
```

---

## What Caused the Error?

The original RLS policies had **circular references**:

```sql
-- ❌ BAD: This creates infinite recursion
CREATE POLICY "Users can view their organization"
    ON organizations FOR SELECT
    USING (id IN (
        SELECT organization_id FROM users WHERE id = auth.uid()
    ));
```

When you query `organizations`, it checks `users` table.
But `users` also has a policy that checks `organizations`.
This creates an infinite loop!

## How the Fix Works

The new policies use **helper functions** that break the recursion:

```sql
-- ✅ GOOD: Helper function with SECURITY DEFINER
CREATE FUNCTION get_user_organization_id() RETURNS UUID AS $$
BEGIN
    RETURN (SELECT organization_id FROM users WHERE id = auth.uid() LIMIT 1);
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Now policies use the helper function
CREATE POLICY "org_select_policy"
    ON organizations FOR SELECT
    USING (id = get_user_organization_id());
```

The `SECURITY DEFINER` flag makes the function execute with elevated privileges, bypassing RLS when querying users table.

---

## Testing After Fix

Run these queries in SQL Editor to verify:

```sql
-- Test 1: Organizations
SELECT id, name, slug FROM organizations;

-- Test 2: Wards
SELECT id, name, code, voter_count FROM wards;

-- Test 3: Constituencies
SELECT id, name, code, voter_count FROM constituencies;

-- Test 4: Check policies
SELECT schemaname, tablename, policyname
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename;
```

All should return data without recursion errors.

---

## Next Steps

After applying the fix:

1. ✅ Test API queries from your frontend
2. ✅ Verify authentication still works
3. ✅ Test data access for different user roles
4. ✅ Monitor for any other policy issues

---

## Need Help?

If you still see errors, check:
- Are you using the correct Supabase project URL?
- Did all SQL statements execute successfully?
- Are there any error messages in the SQL Editor?

Common issues:
- **"relation does not exist"** → Table wasn't created yet, run Phase 1 & 2 migrations first
- **"permission denied"** → Use service role key or check user authentication
- **"policy still recursive"** → Some old policies weren't dropped, re-run the fix SQL
