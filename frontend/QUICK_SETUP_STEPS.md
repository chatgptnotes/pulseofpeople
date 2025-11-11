# ⚡ Quick Setup - 7 Easy Steps

## 🎯 What You Need to Do

Follow these steps **in order** to set up your Super Admin account:

---

## ✅ Step 1: Open Supabase Dashboard

Go to: **https://supabase.com/dashboard**

Click on your project: **`iwtgbseaoztjbnvworyq`**

---

## ✅ Step 2: Open SQL Editor

1. Click "**SQL Editor**" in the left sidebar
2. Click "**New Query**" button

---

## ✅ Step 3: Run Main RBAC Migration

1. **Open this file** on your computer:
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/supabase/migrations/20251028_add_rbac_system.sql
   ```

2. **Copy ALL the contents** (Cmd+A, Cmd+C)

3. **Paste** into Supabase SQL Editor

4. **Click "Run"** (or press Cmd+Enter)

5. **Wait** for "Success. No rows returned"

✅ **This creates all RBAC tables, roles, and permissions**

---

## ✅ Step 4: Create Your Super Admin

1. In the same SQL Editor, click "**New Query**"

2. **Open this file**:
   ```
   /Users/apple/Downloads/Pulseofpeoplevoter23oct/create_super_admin.sql
   ```

3. **IMPORTANT:** Edit these lines (near the top):
   ```sql
   'Super Admin',                    -- Change to YOUR name
   'superadmin@yourdomain.com',     -- Change to YOUR email
   ```

4. **Copy** the file contents

5. **Paste** into SQL Editor

6. **Click "Run"**

7. You should see your new user in the results!

✅ **Your super admin is now in the database**

---

## ✅ Step 5: Create Auth User

1. In Supabase Dashboard, click "**Authentication**" (left sidebar)

2. Click "**Users**"

3. Click "**Add User**" (green button top-right)

4. Enter:
   - **Email**: The SAME email you used in Step 4
   - **Password**: Create a strong password (remember it!)
   - **Auto Confirm User**: ✅ Check this

5. Click "**Create User**"

✅ **Now you can login with this email and password**

---

## ✅ Step 6: Test Login

1. Go to your app: **http://localhost:3000/login**

2. Enter:
   - **Email**: Your email from Step 4
   - **Password**: Your password from Step 5

3. Click "**Sign In**"

4. You should be redirected to the dashboard!

✅ **You're now logged in as Super Admin!**

---

## ✅ Step 7: Verify Your Setup

Open browser console (F12) and type:

```javascript
JSON.parse(localStorage.getItem('user'))
```

You should see:
```json
{
  "role": "super_admin",
  "is_super_admin": true,
  "email": "your-email@domain.com"
}
```

✅ **Setup complete!**

---

## 🎉 What You Have Now

After completing all 7 steps:

✅ **Database with RBAC system**
- 7 new tables
- 7 roles (super_admin → volunteer)
- 33 permissions
- Row Level Security

✅ **Your Super Admin Account**
- Full platform access
- Can manage all organizations
- Can create/manage users
- All permissions enabled

✅ **Working Authentication**
- Login with Supabase Auth
- Automatic permission loading
- Role-based access control

---

## 🚀 What's Next?

### Test Your Permissions

Try accessing different pages:
- Dashboard (/dashboard)
- Analytics (/analytics)
- Settings (/settings)
- User Management (coming soon)

Everything should work!

### Create More Users

Want to create more test users? Use this in SQL Editor:

```sql
-- Create an Admin
INSERT INTO users (name, email, role, status)
VALUES ('Test Admin', 'admin@test.com', 'admin', 'active');

-- Create a Viewer
INSERT INTO users (name, email, role, status)
VALUES ('Test Viewer', 'viewer@test.com', 'viewer', 'active');
```

Then create them in Authentication → Users (Step 5)

### Build Management UIs

Next priorities:
1. Super Admin Dashboard
2. User Management Interface
3. Organization Settings

---

## 🐛 Troubleshooting

### "Table already exists" error
✅ **Good!** Skip to Step 4

### Can't login
❌ Make sure you created user in BOTH:
1. `users` table (Step 4)
2. Supabase Auth (Step 5)

Use the SAME email in both places!

### "Invalid credentials"
❌ Check:
- Email matches exactly
- Password is correct
- User status is 'active'

### Permissions not working
❌ Try:
```javascript
// In browser console
localStorage.clear()
location.reload()
```

Then login again.

---

## 📁 Files You Need

All in: `/Users/apple/Downloads/Pulseofpeoplevoter23oct/`

1. **`supabase/migrations/20251028_add_rbac_system.sql`**
   - Main migration (Step 3)

2. **`create_super_admin.sql`**
   - Create super admin (Step 4)

3. **`SUPABASE_SETUP_GUIDE.md`**
   - Detailed guide with troubleshooting

4. **`QUICK_START.md`**
   - Quick reference for using RBAC

---

## ⏱️ Estimated Time

- **Step 1-2**: 1 minute
- **Step 3**: 2 minutes (migration runs)
- **Step 4**: 2 minutes (edit & run)
- **Step 5**: 1 minute (create auth user)
- **Step 6**: 1 minute (test login)
- **Step 7**: 1 minute (verify)

**Total: ~10 minutes**

---

## 🎓 Remember

- **Step 3** creates the database structure
- **Step 4** creates your user record
- **Step 5** creates authentication
- **Step 6** tests everything works

You need ALL steps for it to work!

---

## ✅ Checklist

- [ ] Opened Supabase Dashboard
- [ ] Opened SQL Editor
- [ ] Ran main RBAC migration (Step 3)
- [ ] Edited create_super_admin.sql with MY email
- [ ] Ran create_super_admin.sql (Step 4)
- [ ] Created Auth user with SAME email (Step 5)
- [ ] Tested login successfully (Step 6)
- [ ] Verified user in console (Step 7)

**All done? Congratulations! 🎉**

Your multi-tenant RBAC system is now fully operational!

---

**Questions?** Check SUPABASE_SETUP_GUIDE.md for detailed help!
