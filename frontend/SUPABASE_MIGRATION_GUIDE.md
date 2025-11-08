# Supabase Migration Guide - Connect Real Database

## Overview
This guide will help you migrate from mock authentication to real Supabase database with full RBAC system and 11 test users.

**Time Required:** ~15 minutes

---

## Step 1: Open Supabase Dashboard

1. Go to: **https://supabase.com/dashboard**
2. Login to your account
3. Select your project: **`iwtgbseaoztjbnvworyq`**

---

## Step 2: Run RBAC Migration

This creates all the database tables, roles, permissions, and security policies.

### Instructions:

1. In Supabase Dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New Query"** button
3. Open this file on your computer:
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/supabase/migrations/20251028_add_rbac_system.sql
   ```
4. **Copy ALL contents** (Cmd+A, Cmd+C)
5. **Paste** into Supabase SQL Editor
6. Click **"Run"** (or press Cmd+Enter)
7. Wait for **"Success. No rows returned"** message

### What This Creates:
- ✅ 7 new tables (organizations, roles, permissions, etc.)
- ✅ 7 default roles (super_admin → volunteer)
- ✅ 33 granular permissions
- ✅ Row Level Security (RLS) policies
- ✅ Helper functions for RBAC

---

## Step 3: Seed Test Users

This creates 11 test user accounts in the database.

### Instructions:

1. In SQL Editor, click **"New Query"**
2. Open this file:
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/supabase/seed_test_users.sql
   ```
3. **Copy ALL contents**
4. **Paste** into SQL Editor
5. Click **"Run"**
6. You should see a table with 11 users displayed

### Users Created:
- Super Admin: `superadmin@pulseofpeople.com`
- Admin: `admin@bettroi.com`
- Manager: `manager@bettroi.com`
- Analyst: `analyst@bettroi.com`
- User: `user@bettroi.com`
- Viewer: `viewer@bettroi.com`
- Ward Coordinator: `coordinator@bettroi.com`
- Social Media: `social@bettroi.com`
- Survey Team: `survey@bettroi.com`
- Truth Team: `truth@bettroi.com`
- Volunteer: `volunteer@bettroi.com`

---

## Step 4: Create Authentication Users

Now create login credentials for each user.

### Instructions:

1. In Supabase Dashboard, click **"Authentication"** (left sidebar)
2. Click **"Users"** tab
3. For **EACH** of the 11 emails below, do this:
   - Click **"Add User"** button (green, top-right)
   - **Email:** (copy from list below)
   - **Password:** `password`
   - **Auto Confirm User:** ✅ **Check this box**
   - Click **"Create User"**

### List of Emails to Create:

```
superadmin@pulseofpeople.com
admin@bettroi.com
manager@bettroi.com
analyst@bettroi.com
user@bettroi.com
viewer@bettroi.com
coordinator@bettroi.com
social@bettroi.com
survey@bettroi.com
truth@bettroi.com
volunteer@bettroi.com
```

**Password for all:** `password`

**Tip:** This is the tedious part - creating 11 users. Take your time and make sure each email is exactly correct!

---

## Step 5: Verify Setup

Let's make sure everything is connected properly.

### Check 1: Database Users

Run this in SQL Editor:

```sql
SELECT COUNT(*) as user_count FROM users;
```

Should return: **11 users**

### Check 2: Auth Users

Go to: **Authentication → Users**

Should see: **11 users in the list**

### Check 3: Application Connection

1. Go to your app: **http://localhost:3000/login**
2. Try logging in with: `superadmin@pulseofpeople.com` / `password`
3. Should redirect to dashboard
4. Open browser console (F12)
5. Type:
   ```javascript
   JSON.parse(localStorage.getItem('user'))
   ```
6. Should see your user object with `is_super_admin: true`

---

## Step 6: Test All Roles

Try logging in with different accounts to test permissions:

### Super Admin
```
Email: superadmin@pulseofpeople.com
Password: password
```
**Expected:** See ALL features, no restrictions

### Admin
```
Email: admin@bettroi.com
Password: password
```
**Expected:** Full organization access, but no platform settings

### Manager
```
Email: manager@bettroi.com
Password: password
```
**Expected:** User management, team features

### Viewer
```
Email: viewer@bettroi.com
Password: password
```
**Expected:** Read-only access, no edit buttons

### Volunteer
```
Email: volunteer@bettroi.com
Password: password
```
**Expected:** Limited dashboard, field reports only

---

## Troubleshooting

### "Cannot find user" error when logging in

**Problem:** User exists in Auth but not in `users` table

**Solution:**
1. Check if user exists: `SELECT * FROM users WHERE email = 'your@email.com';`
2. If missing, re-run the seed script (Step 3)

---

### "Invalid credentials" error

**Problem:** User doesn't exist in Supabase Auth

**Solution:**
1. Go to Authentication → Users
2. Check if email exists
3. If missing, create the user (Step 4)
4. Make sure "Auto Confirm User" was checked

---

### "No permissions" or blank dashboard

**Problem:** User has no role or permissions

**Solution:**
```sql
-- Check user permissions
SELECT email, role, is_super_admin, permissions
FROM users
WHERE email = 'your@email.com';

-- If permissions are empty, re-run seed script
```

---

### Dev server shows Supabase errors

**Problem:** Environment variables not loaded

**Solution:**
```bash
# Make sure .env file exists (not .env.backup)
ls -la /Users/apple/Downloads/Pulseofpeoplevoter23oct/voter/.env

# Restart dev server
# Kill the running server and run:
npm run dev
```

---

### RLS Policy errors when accessing data

**Problem:** Row Level Security blocking access

**Solution:**
1. Make sure migration ran successfully
2. Check if user has `is_super_admin = true` for super admin
3. Verify `organization_id` matches for non-super-admin users

---

## What's Next?

After successfully migrating to Supabase:

1. ✅ **Create Your Own Super Admin**
   - Use your personal email
   - Update the seed script or create manually

2. ✅ **Create Organizations**
   - Add real political parties/campaigns
   - Assign users to organizations

3. ✅ **Build Management UIs**
   - Super Admin Dashboard
   - User Management Interface
   - Organization Settings Page

4. ✅ **Customize Permissions**
   - Adjust role permissions as needed
   - Grant/revoke custom permissions

5. ✅ **Deploy to Production**
   - Use production Supabase project
   - Update environment variables
   - Create real user accounts

---

## Files Reference

All files mentioned in this guide:

```
/Users/apple/Downloads/Pulseofpeoplevoter23oct/
├── supabase/
│   ├── migrations/
│   │   └── 20251028_add_rbac_system.sql      # RBAC migration
│   └── seed_test_users.sql                   # Test users seed
├── voter/
│   ├── .env                                   # Supabase credentials
│   └── src/
│       └── contexts/
│           └── AuthContext.tsx                # Authentication logic
└── SUPABASE_MIGRATION_GUIDE.md               # This file
```

---

## Success Checklist

- [ ] Ran RBAC migration (Step 2)
- [ ] Seeded 11 test users (Step 3)
- [ ] Created 11 auth users (Step 4)
- [ ] Logged in as Super Admin successfully
- [ ] Tested at least 3 different roles
- [ ] Verified permissions work correctly

---

## Support

If you encounter issues not covered here:

1. Check browser console for errors
2. Check Supabase Dashboard → Logs
3. Review the migration SQL for syntax errors
4. Verify environment variables are correct

---

**You're now running on real Supabase with full RBAC! 🎉**

Mock authentication has been completely removed and you're using production-ready authentication.
