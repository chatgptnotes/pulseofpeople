# 🚀 Complete Supabase Setup Guide - Step by Step

## Overview
This guide will help you set up the complete RBAC system with your Supabase database.

---

## ✅ Option 1: Using Supabase Dashboard (EASIEST)

### Step 1: Open Supabase Dashboard

Go to: https://supabase.com/dashboard

### Step 2: Select Your Project

Click on your project: `iwtgbseaoztjbnvworyq`

### Step 3: Open SQL Editor

1. Click "**SQL Editor**" in the left sidebar
2. Click "**New Query**"

### Step 4: Run the RBAC Migration

1. Open this file on your computer:
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/supabase/migrations/20251028_add_rbac_system.sql
   ```

2. Copy **ALL** the contents (it's a big file!)

3. Paste into the Supabase SQL Editor

4. Click "**Run**" (or press `Cmd + Enter`)

5. Wait for it to complete. You should see: "Success. No rows returned"

**What this does:**
- Creates 7 new tables for RBAC
- Adds organizations, roles, permissions tables
- Sets up Row Level Security
- Creates 7 default roles
- Creates 33 permissions
- Sets up helper functions

### Step 5: Create Your Super Admin User

In the same SQL Editor, run this:

```sql
-- Create Super Admin User
INSERT INTO users (
  name,
  email,
  role,
  is_super_admin,
  organization_id,
  tenant_id,
  status,
  permissions,
  created_at,
  updated_at
)
VALUES (
  'Super Admin',                    -- Change to your name
  'superadmin@example.com',        -- Change to your email
  'super_admin',
  TRUE,
  NULL,
  NULL,
  'active',
  ARRAY[]::TEXT[],
  NOW(),
  NOW()
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'super_admin',
  is_super_admin = TRUE,
  status = 'active',
  updated_at = NOW();
```

**Make sure to:**
- Replace `'Super Admin'` with your name
- Replace `'superadmin@example.com'` with YOUR email address

Click "**Run**"

### Step 6: Create Auth User

1. In Supabase Dashboard, click "**Authentication**" in left sidebar
2. Click "**Users**"
3. Click "**Add User**" button (green button top-right)
4. Enter the **SAME EMAIL** you used in Step 5
5. Enter a **password** (remember it!)
6. Click "**Create User**"

### Step 7: Test Login!

1. Go to your app: http://localhost:3000/login
2. Enter your email and password
3. Click "Sign In"
4. You should be logged in as Super Admin!

---

## ✅ Option 2: Using Supabase CLI (Advanced)

If you want to use CLI instead:

### Prerequisites

You need:
- Supabase Access Token
- PostgreSQL client (psql)

### Get Supabase Access Token

1. Go to https://supabase.com/dashboard/account/tokens
2. Click "Generate new token"
3. Give it a name (e.g., "CLI Access")
4. Copy the token

### Run Commands

```bash
# Set your access token
export SUPABASE_ACCESS_TOKEN="your-token-here"

# Link your project
cd /Users/apple/Downloads/Pulseofpeoplevoter23oct
supabase link --project-ref iwtgbseaoztjbnvworyq

# Push migration
supabase db push
```

---

## 🎯 Verification

### Check if Migration Worked

In Supabase SQL Editor, run:

```sql
-- Check if new tables exist
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN (
  'organizations',
  'roles',
  'permissions',
  'role_permissions',
  'user_permissions',
  'user_organizations',
  'rbac_audit_log'
);
```

You should see all 7 tables!

### Check Your Super Admin User

```sql
-- Check if your user was created
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
```

You should see your super admin user!

### Check Permissions

```sql
-- See all available permissions
SELECT name, display_name, category
FROM permissions
ORDER BY category, name;
```

You should see 33 permissions!

### Check Roles

```sql
-- See all roles
SELECT name, display_name, level
FROM roles
ORDER BY level;
```

You should see 7 roles!

---

## 🎨 What You Get

After completing the setup:

### 1. Database Tables ✅
- `organizations` - Tenant organizations
- `roles` - Role definitions
- `permissions` - Permission definitions
- `role_permissions` - Role-permission mapping
- `user_permissions` - Custom user permissions
- `user_organizations` - User-org relationships
- `rbac_audit_log` - Audit trail

### 2. Default Roles ✅
- super_admin (Level 1)
- admin (Level 2)
- manager (Level 3)
- analyst (Level 4)
- user (Level 5)
- viewer (Level 6)
- volunteer (Level 7)

### 3. Permissions ✅
33 granular permissions across 6 categories:
- Users (5 permissions)
- Data (7 permissions)
- Voters (3 permissions)
- Field Workers (4 permissions)
- Social Media (2 permissions)
- AI/Analytics (3 permissions)
- Settings (3 permissions)
- Alerts (2 permissions)
- System (4 permissions)

---

## 🔐 Create Additional Users

### Create an Admin User

```sql
INSERT INTO users (
  name,
  email,
  role,
  is_super_admin,
  organization_id,
  status,
  permissions
)
VALUES (
  'John Admin',
  'john@example.com',
  'admin',
  FALSE,
  NULL,  -- Set organization_id if needed
  'active',
  ARRAY[]::TEXT[]
);
```

Then create in Supabase Auth (same as Step 6 above)

### Create a Regular User

```sql
INSERT INTO users (
  name,
  email,
  role,
  status
)
VALUES (
  'Jane User',
  'jane@example.com',
  'user',
  'active'
);
```

### Create a Volunteer

```sql
INSERT INTO users (
  name,
  email,
  role,
  status
)
VALUES (
  'Bob Volunteer',
  'bob@example.com',
  'volunteer',
  'active'
);
```

---

## 🏢 Create an Organization

```sql
INSERT INTO organizations (
  tenant_id,
  name,
  slug,
  description,
  subscription_tier,
  subscription_status,
  status,
  state,
  region
)
VALUES (
  'kerala-bjp',
  'Kerala BJP',
  'kerala-bjp',
  'Kerala State BJP Organization',
  'premium',
  'active',
  'active',
  'Kerala',
  'South India'
);
```

### Assign User to Organization

```sql
-- First, get the organization ID
SELECT id FROM organizations WHERE slug = 'kerala-bjp';

-- Then update user
UPDATE users
SET organization_id = 'organization-id-here'
WHERE email = 'user@example.com';
```

---

## 🐛 Troubleshooting

### Issue: "Relation already exists"

**Solution:** Tables already exist! Just create your user (Step 5)

### Issue: "Permission denied"

**Solution:** Make sure you're logged into Supabase Dashboard with correct account

### Issue: Can't login to app

**Solution:**
1. Make sure you created user in BOTH places:
   - `users` table (Step 5)
   - Supabase Auth (Step 6)
2. Use the SAME email in both places
3. Clear browser cache: `localStorage.clear()` in console

### Issue: Permissions not working

**Solution:**
```sql
-- Check user's permissions
SELECT * FROM get_user_permissions('user-id-here');

-- Or refresh by logging out and back in
```

---

## 📱 Testing Different Roles

### Test Super Admin
```
Email: superadmin@example.com (or what you created)
Password: (what you set)
Should see: ALL features, no restrictions
```

### Test Admin
Create admin user and test:
- Can manage users in their organization
- Can view all analytics
- Can edit settings

### Test Viewer
Create viewer user and test:
- Can only view dashboards
- No edit buttons
- No export buttons

---

## 🎉 Success Checklist

After completing all steps:

- [ ] Ran RBAC migration (Step 4)
- [ ] Created super admin in `users` table (Step 5)
- [ ] Created auth user in Supabase (Step 6)
- [ ] Can login to app (Step 7)
- [ ] Verified tables exist
- [ ] Verified user exists
- [ ] Verified permissions exist
- [ ] Verified roles exist

---

## 📞 Quick Commands Reference

### View All Users
```sql
SELECT id, name, email, role, is_super_admin, status
FROM users
ORDER BY created_at DESC;
```

### View User's Permissions
```sql
SELECT * FROM get_user_permissions('user-id-here');
```

### Check User Role
```sql
SELECT name, email, role, is_super_admin
FROM users
WHERE email = 'your@email.com';
```

### Make User Super Admin
```sql
UPDATE users
SET
  role = 'super_admin',
  is_super_admin = TRUE
WHERE email = 'user@example.com';
```

### View Audit Log
```sql
SELECT
  action,
  actor_id,
  target_user_id,
  created_at
FROM rbac_audit_log
ORDER BY created_at DESC
LIMIT 20;
```

---

## 🚀 You're Ready!

Once you complete Step 1-7, your multi-tenant RBAC system will be fully operational!

**Next Steps:**
1. Complete the setup above
2. Login and test
3. Create more users as needed
4. Build Super Admin Dashboard UI
5. Build User Management interface

---

**Need Help?**
- Check GETTING_STARTED_GUIDE.md for more details
- Check RBAC_IMPLEMENTATION_GUIDE.md for technical docs
- Check browser console (F12) for errors

Good luck! 🎉
