# 🔐 Login Setup Instructions

## Problem Diagnosis

Your login is failing because:
1. ❌ **Users table missing columns** (`is_super_admin`, `full_name`, etc.)
2. ❌ **Email not confirmed** in Supabase Auth
3. ⚠️ **Wrong password displayed** on login page (shows `Admin@123` but should be `Admin@123456`)

---

## ✅ Solution: 3-Step Fix

### Step 1: Run SQL Migration (2 minutes)

1. **Open Supabase SQL Editor:**
   - Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/sql
   - Or: Supabase Dashboard → SQL Editor → New Query

2. **Copy and paste this SQL:**
   ```sql
   -- Paste entire contents of fix-users-table.sql file
   ```
   (See `fix-users-table.sql` in frontend folder)

3. **Click "RUN"** at the bottom right

4. **Verify success:** You should see:
   ```
   ✅ Added is_super_admin column
   ✅ Added full_name column
   ... (more success messages)
   ```

---

### Step 2: Confirm User Email (1 minute)

1. **Open Supabase Authentication:**
   - Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users
   - Or: Supabase Dashboard → Authentication → Users

2. **Find the user:**
   - Look for: `admin@tvk.com`

3. **Confirm email:**
   - Click the **"..."** menu (3 dots) next to the user
   - Select **"Confirm Email"**
   - ✅ You should see a green checkmark appear

4. **Optional:** If `admin@tvk.com` doesn't exist:
   - Click **"Add User"** → **"Create new user"**
   - Email: `admin@tvk.com`
   - Password: `Admin@123456`
   - ✅ Check **"Auto Confirm User"**
   - Click **"Create User"**

---

### Step 3: Test Login (30 seconds)

1. **Open your app:** http://localhost:5174

2. **Login with:**
   - **Email:** `admin@tvk.com`
   - **Password:** `Admin@123456` ← **Note the "456" at the end!**

3. **Success!** You should be redirected to the dashboard

---

## 🔑 All Available Credentials

| Email | Password | Role |
|-------|----------|------|
| `admin@tvk.com` | `Admin@123456` | Superadmin |
| `user@tvk.com` | `User@123456` | User |
| `test@pulseofpeople.com` | `TestPassword123!` | Admin |

---

## 🚨 Troubleshooting

### Error: "Invalid login credentials"
- ✅ **Fix:** Confirm email in Supabase Auth (Step 2 above)
- ✅ **Check:** Password is `Admin@123456` (with "456")

### Error: "Failed to fetch" / Network error
- ✅ **Check:** Dev server is running on http://localhost:5174
- ✅ **Restart:** Stop and restart the dev server
  ```bash
  cd frontend
  npm run dev
  ```

### Error: "column users.is_super_admin does not exist"
- ✅ **Fix:** Run the SQL migration (Step 1 above)

### Login successful but shows wrong role
- ✅ **Fix:** Make sure user record exists in `users` table with correct role
- ✅ **Run:** Check in Supabase SQL Editor:
  ```sql
  SELECT * FROM users WHERE email = 'admin@tvk.com';
  ```

---

## 📋 Quick Command Reference

```bash
# Restart dev server
cd frontend
npm run dev

# Create test users in Auth (if needed)
node create-auth-users.cjs

# Test login connection
node test-login.cjs
```

---

## ✅ Success Checklist

- [ ] SQL migration executed (all columns added)
- [ ] User email confirmed in Supabase Auth
- [ ] Can login with admin@tvk.com / Admin@123456
- [ ] Redirected to dashboard after login
- [ ] User role shows as "superadmin"

---

## 🎯 What's Next?

After successful login, you can:
- 👥 Manage users
- 📊 View analytics dashboard
- 🗺️ Access map features
- ⚙️ Configure settings

---

**Status:** Frontend running on **http://localhost:5174**
**Supabase Project:** https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq
