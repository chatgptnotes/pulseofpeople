# Setup Instructions - Supabase Migration Complete!

## Current Status

✅ **Code Migration Complete!**
- All mock authentication code has been removed
- Supabase is now the only authentication method
- Environment variables are configured
- Dev server is running

## What You Need to Do Now

Before you can login, you must set up the Supabase database. Follow these steps:

---

## Quick Setup (3 Main Steps)

### Step 1: Run RBAC Migration (Creates Tables)

1. Go to: **https://supabase.com/dashboard**
2. Open your project: **`iwtgbseaoztjbnvworyq`**
3. Click **"SQL Editor"** → **"New Query"**
4. Open and copy ALL contents from:
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/supabase/migrations/20251028_add_rbac_system.sql
   ```
5. Paste in SQL Editor and click **"Run"**
6. Wait for success message

**What this does:** Creates 7 tables, roles, permissions, and security policies

---

### Step 2: Seed Test Users (Creates User Records)

1. In SQL Editor, click **"New Query"**
2. Open and copy ALL contents from:
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/supabase/seed_test_users.sql
   ```
3. Paste and click **"Run"**
4. You should see 11 users listed in the results

**What this does:** Creates 11 test user records in the database

---

### Step 3: Create Auth Users (Creates Login Credentials)

For **EACH** of these 11 emails, do the following:

1. In Supabase Dashboard → **Authentication** → **Users**
2. Click **"Add User"** (green button)
3. Enter email and password below
4. **✅ Check "Auto Confirm User"**
5. Click **"Create User"**

**List of users to create:**

| Email | Password | Role |
|-------|----------|------|
| superadmin@pulseofpeople.com | password | Super Admin |
| admin@bettroi.com | password | Admin |
| manager@bettroi.com | password | Manager |
| analyst@bettroi.com | password | Analyst |
| user@bettroi.com | password | User |
| viewer@bettroi.com | password | Viewer |
| coordinator@bettroi.com | password | Ward Coordinator |
| social@bettroi.com | password | Social Media |
| survey@bettroi.com | password | Survey Team |
| truth@bettroi.com | password | Truth Team |
| volunteer@bettroi.com | password | Volunteer |

**Note:** This is the tedious part - you need to create each user manually. Take your time!

---

## Step 4: Test Login

1. Go to: **http://localhost:3000/login**
2. Try logging in with:
   ```
   Email: superadmin@pulseofpeople.com
   Password: password
   ```
3. Should redirect to dashboard
4. Open browser console (F12) and verify user:
   ```javascript
   JSON.parse(localStorage.getItem('user'))
   ```

---

## Detailed Guide

For more detailed instructions, troubleshooting, and explanations, see:

📖 **SUPABASE_MIGRATION_GUIDE.md**

---

## Files Created

All necessary files are ready:

- ✅ `supabase/migrations/20251028_add_rbac_system.sql` - Database schema
- ✅ `supabase/seed_test_users.sql` - Test user data
- ✅ `SUPABASE_MIGRATION_GUIDE.md` - Detailed guide
- ✅ `SETUP_INSTRUCTIONS.md` - This file
- ✅ `.env` - Supabase credentials (restored)

---

## Quick Checklist

Before testing login:

- [ ] Ran RBAC migration (Step 1)
- [ ] Seeded test users (Step 2)
- [ ] Created all 11 auth users (Step 3)
- [ ] Dev server is running (http://localhost:3000)

---

## Why This is Necessary

The application now uses **real Supabase authentication** which requires:

1. **Database tables** - Where user data is stored (Step 1)
2. **User records** - The actual user data (Step 2)
3. **Auth credentials** - Login email/password (Step 3)

Without all three, login will fail with "Invalid credentials" or "User not found".

---

## What Changed

**Before (Mock Mode):**
- Users were hardcoded in AuthContext.tsx
- No database needed
- Worked offline

**Now (Supabase Mode):**
- Users are in Supabase database
- Requires internet connection
- Production-ready authentication
- Full RBAC with permissions

---

## Estimate Time

- Step 1: 2 minutes
- Step 2: 1 minute
- Step 3: 10 minutes (creating 11 users)

**Total: ~15 minutes**

---

## After Setup

Once you've completed all steps, you can:

✅ Login with any of the 11 test accounts
✅ Test different role permissions
✅ See role-based UI changes
✅ Use real database features
✅ Deploy to production

---

## Need Help?

Check the detailed guide: **SUPABASE_MIGRATION_GUIDE.md**

It includes:
- Step-by-step screenshots
- Troubleshooting section
- Error solutions
- Verification steps

---

**Ready? Start with Step 1!** 🚀
