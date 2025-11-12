# SLOW LOGIN ISSUE - ROOT CAUSE & SOLUTION

**Date**: 2025-11-10
**Severity**: 🔴 **CRITICAL** - Performance Issue
**Impact**: Login takes 10-30 seconds and frequently fails

---

## 🔍 ROOT CAUSE IDENTIFIED

### The Problem: **Circular Reference in RLS Policies**

The login slowness is caused by a **circular dependency** in Row Level Security (RLS) policies:

```
User logs in
   ↓
Frontend queries: SELECT * FROM users WHERE email = 'user@example.com'
   ↓
Supabase RLS Policy activates
   ↓
Policy calls: get_user_role() and get_user_organization_id()
   ↓
These functions execute: SELECT role FROM users WHERE id = auth.uid()
   ↓
This triggers RLS policy AGAIN (nested query on same table!)
   ↓
CIRCULAR REFERENCE → Slow performance or timeout
```

---

## 📊 TECHNICAL DETAILS

### Current RLS Policies (Problematic)

**Policy: `users_select_policy`**
```sql
-- Applied to authenticated users
USING (
    (organization_id = get_user_organization_id())
    OR
    ((get_user_role())::text = 'superadmin'::text)
)
```

**Problem Functions:**

```sql
CREATE FUNCTION get_user_role() RETURNS VARCHAR AS $$
BEGIN
    RETURN (
        SELECT role
        FROM users  -- ❌ Queries same table RLS is protecting!
        WHERE id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE FUNCTION get_user_organization_id() RETURNS UUID AS $$
BEGIN
    RETURN (
        SELECT organization_id
        FROM users  -- ❌ Queries same table RLS is protecting!
        WHERE id = auth.uid()
        LIMIT 1
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

### Why This Causes Slowness

1. **Infinite Recursion Risk**: PostgreSQL has to evaluate RLS policies on every query, including the nested ones
2. **Multiple Policy Evaluations**: With 8 RLS policies on the users table, each nested query evaluates all policies
3. **Function Overhead**: SECURITY DEFINER functions add extra overhead
4. **Lock Contention**: Nested queries on the same table can cause lock contention

---

## 🔥 CONTRIBUTING FACTORS

### 1. Excessive Timeout (30 seconds)

**Location**: `frontend/src/contexts/AuthContext.tsx:187-188`

```typescript
const timeoutPromise = new Promise((_, reject) => {
  setTimeout(() => reject(new Error('User data fetch timeout after 30 seconds')), 30000);
});
```

**Issue**: 30-second timeout is excessively long. Should be 3-5 seconds max.

### 2. Duplicate Query in Login Flow

The login function queries the users table TWICE:
1. In `fetchUserData()` during auth state change
2. Again in `login()` function (lines 298-302)

### 3. Complex RLS Policy Stack

8 different RLS policies on the users table, each evaluated on every query:
- Anon can read all users
- Authenticated users can read own data
- Authenticated users can update own data
- Service role full access
- users_insert_policy
- users_select_policy (← **This one causes the circular reference**)
- users_update_own_policy
- users_update_policy

---

## ✅ SOLUTION

### Option 1: Use JWT Claims (Recommended - Fastest)

Store user metadata in JWT claims instead of querying the database:

**Step 1: Modify Supabase Auth User Creation**

```python
# create_supabase_users.py - Add metadata
{
    "email": "user@example.com",
    "password": "password",
    "email_confirm": True,
    "user_metadata": {
        "role": "admin",
        "organization_id": "uuid-here",  # ← Add this
        "full_name": "User Name"
    }
}
```

**Step 2: Update RLS Policy Functions**

```sql
-- Replace get_user_role() with JWT claim lookup
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS VARCHAR AS $$
BEGIN
    -- Read from JWT instead of querying users table
    RETURN COALESCE(
        (auth.jwt() -> 'user_metadata' ->> 'role')::VARCHAR,
        'user'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;

-- Replace get_user_organization_id() with JWT claim lookup
CREATE OR REPLACE FUNCTION get_user_organization_id()
RETURNS UUID AS $$
BEGIN
    -- Read from JWT instead of querying users table
    RETURN (auth.jwt() -> 'user_metadata' ->> 'organization_id')::UUID;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER STABLE;
```

**Benefits**:
- ✅ No database query needed
- ✅ No circular reference
- ✅ Instant policy evaluation
- ✅ Scales to millions of users

---

### Option 2: Bypass RLS for Login Query (Quick Fix)

Simplify the RLS policy to allow users to read their own data without function calls:

```sql
-- Replace users_select_policy with simpler version
DROP POLICY IF EXISTS users_select_policy ON users;

CREATE POLICY users_select_simple ON users
    FOR SELECT
    TO authenticated
    USING (
        -- Allow reading own data (no function call needed)
        id = auth.uid()
        OR
        -- Allow reading if same organization (use direct comparison)
        organization_id IN (
            SELECT organization_id
            FROM users
            WHERE id = auth.uid()
        )
    );
```

**Note**: This still has a nested query but it's simpler and PostgreSQL can optimize it better.

---

### Option 3: Disable RLS for Initial Login Query (Nuclear Option)

Create a special policy that allows authenticated users to read by email without restrictions:

```sql
-- Add permissive policy for email-based lookup
CREATE POLICY users_select_by_email ON users
    FOR SELECT
    TO authenticated
    USING (
        -- Allow any authenticated user to read users by email
        -- This is safe because you're already authenticated
        true
    );
```

Then rely on application-level authorization instead of RLS.

**Pros**: Fast, simple
**Cons**: Less secure, removes database-level security

---

## 🚀 IMMEDIATE FIXES (Do This Now)

### Fix 1: Reduce Timeout to 5 Seconds

**File**: `frontend/src/contexts/AuthContext.tsx`

**Line 187-188**:
```typescript
// BEFORE (30 seconds):
setTimeout(() => reject(new Error('User data fetch timeout after 30 seconds')), 30000);

// AFTER (5 seconds):
setTimeout(() => reject(new Error('User data fetch timeout after 5 seconds')), 5000);
```

**Line 294-296** (duplicate timeout in login function):
```typescript
// BEFORE:
setTimeout(() => reject(new Error('User data fetch timeout after 30 seconds')), 30000);

// AFTER:
setTimeout(() => reject(new Error('User data fetch timeout after 5 seconds')), 5000);
```

### Fix 2: Use Service Role Key for Login Query

Modify the Supabase client to use service role key for the initial user data fetch:

**File**: `frontend/src/contexts/AuthContext.tsx`

Add at the top:
```typescript
import { createClient } from '@supabase/supabase-js';

// Create service role client (bypasses RLS)
const supabaseServiceRole = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_SERVICE_ROLE_KEY
);
```

Then in the login function (line 298):
```typescript
// BEFORE:
const userDataPromise = supabase
  .from('users')
  .select('*')
  .eq('email', email)
  .single();

// AFTER (bypasses RLS):
const userDataPromise = supabaseServiceRole
  .from('users')
  .select('*')
  .eq('email', email)
  .single();
```

**Important**: Add to `.env`:
```env
VITE_SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

---

## 📈 EXPECTED IMPROVEMENTS

### Before Fix:
- 🐌 Login time: 10-30 seconds
- ❌ Frequent timeouts
- 🔴 Poor user experience

### After Fix:
- ⚡ Login time: < 2 seconds
- ✅ No timeouts
- 🟢 Excellent user experience

---

## 🧪 TESTING PROCEDURE

### Test 1: Verify Query Performance

```bash
# In browser console after applying fixes:
console.time('login');
// Attempt login
console.timeEnd('login');

# Should show: login: 1500ms (or less)
```

### Test 2: Check RLS Function Usage

```sql
-- Run in Supabase SQL Editor
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'test@example.com';

-- Look for:
-- "Execution Time" should be < 100ms
-- No recursive calls to RLS functions
```

### Test 3: Stress Test

```javascript
// Test multiple logins in sequence
for (let i = 0; i < 5; i++) {
  await login('user@example.com', 'password');
  await logout();
}
// All should complete in < 10 seconds total
```

---

## 🛠️ IMPLEMENTATION PRIORITY

### Immediate (Do Today):
1. ✅ Reduce timeout from 30s to 5s
2. ✅ Use service role key for login query
3. ✅ Test login performance

### Short-term (This Week):
1. ⚠️ Update RLS policy functions to use JWT claims
2. ⚠️ Update user creation to include metadata in JWT
3. ⚠️ Test with all user roles

### Long-term (Next Sprint):
1. 📝 Simplify RLS policy stack
2. 📝 Add performance monitoring
3. 📝 Implement connection pooling
4. 📝 Add caching layer

---

## 📝 FILES TO MODIFY

### Critical Files:
1. **`frontend/src/contexts/AuthContext.tsx`** (Lines 187, 294, 298)
   - Reduce timeouts
   - Use service role client

2. **`backend/.env`**
   - Add `VITE_SUPABASE_SERVICE_ROLE_KEY`

3. **`frontend/.env`**
   - Add `VITE_SUPABASE_SERVICE_ROLE_KEY`

### Optional (Long-term):
4. **Supabase SQL Editor** - Execute:
   - Update `get_user_role()` function
   - Update `get_user_organization_id()` function
   - Simplify `users_select_policy`

---

## ⚠️ WARNINGS

### Security Considerations:

1. **Service Role Key Exposure**:
   - ⚠️ Service role key should NEVER be exposed in client code
   - ✅ Alternative: Create a serverless function that uses service role
   - ✅ Or use JWT claims approach (no service role needed)

2. **RLS Bypass Risk**:
   - Using service role bypasses ALL RLS policies
   - Only use for initial user data fetch during login
   - All other queries should use regular client

3. **JWT Claims Consistency**:
   - Must update JWT claims when user role/org changes
   - Implement refresh mechanism

---

## 🎯 RECOMMENDED APPROACH

**Best Solution**: **Use JWT Claims** (Option 1)

**Why**:
- ✅ Secure (no service role key needed)
- ✅ Fast (no database query)
- ✅ Scalable
- ✅ No circular reference
- ✅ Industry standard approach

**Implementation**:
1. Update user creation to include role + org_id in JWT
2. Update RLS functions to read from JWT
3. Reduce timeouts
4. Test thoroughly

**Timeline**: 2-3 hours of development + testing

---

## 📞 SUPPORT

If issues persist after applying fixes:

1. Check browser console for errors
2. Check Supabase logs for slow queries
3. Run `EXPLAIN ANALYZE` on user queries
4. Monitor for RLS policy evaluation time
5. Check network tab for request/response times

---

**Status**: 🟡 **IDENTIFIED** - Ready for Implementation
**Priority**: 🔴 **P0** - Critical User Experience Issue
**Estimated Fix Time**: 2-3 hours

