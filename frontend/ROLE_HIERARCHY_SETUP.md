# Role Hierarchy Setup - Pulse of People

## ✅ Role Hierarchy Structure

```
superadmin (Platform Owner)
    ↓
  admin (Organization Admin)
    ↓
 manager (District Manager)
    ↓
 analyst (Constituency Analyst)
    ↓
   user (Booth Agent/Field Worker)
```

---

## 🔑 Test Credentials (All Verified)

### 1. SUPER ADMIN
- **Email**: `superadmin@pulseofpeople.com`
- **Password**: `SuperAdmin@123`
- **Full Name**: TVK Super Admin
- **Role**: `superadmin`
- **Scope**: All Organizations / All States
- **Permissions**: Full platform access (*)
- **Badge Color**: Red

**What you can do:**
- Manage all organizations
- View all data across all tenants
- Manage system settings
- View audit logs
- Manage billing

---

### 2. ADMIN
- **Email**: `admin@tvk.com`
- **Password**: `Admin@123`
- **Full Name**: TVK Admin
- **Role**: `admin`
- **Scope**: All constituencies
- **Permissions**: View all, Edit all, Manage users, Export data
- **Badge Color**: Red

**What you can do:**
- Manage organization users
- View all organization data
- Export reports
- Manage field workers
- Access admin panel

---

### 3. MANAGER
- **Email**: `manager@tvk.com`
- **Password**: `Manager@123`
- **Full Name**: TVK Manager
- **Role**: `manager`
- **Scope**: Chennai District (6-16 constituencies)
- **Permissions**: View users, Create users, View analytics, Export data
- **Badge Color**: Yellow

**What you can do:**
- View district sentiment overview
- Manage constituency analysts
- District-wide social media monitoring
- Field operations in district
- **Dashboard**: ManagerDistrictDashboard with LineChart

---

### 4. ANALYST
- **Email**: `analyst@tvk.com`
- **Password**: `Analyst@123`
- **Full Name**: TVK Analyst
- **Role**: `analyst`
- **Scope**: Perambur Constituency (200-300 booths)
- **Permissions**: View analytics, Verify submissions, Export data
- **Badge Color**: Light Red

**What you can do:**
- View constituency sentiment
- Manage booth agents
- Track booth performance
- Issue tracking for constituency
- Field reports from booths
- **Dashboard**: AnalystConstituencyDashboard with BarChart

---

### 5. USER (Booth Agent)
- **Email**: `user@tvk.com`
- **Password**: `User@123`
- **Full Name**: TVK User
- **Role**: `user`
- **Scope**: Booth B-456, Ward 15
- **Permissions**: View dashboard, Submit data
- **Badge Color**: Gray

**What you can do:**
- Collect voter feedback
- Submit daily field reports
- Track assigned voters
- View booth metrics
- **Dashboard**: UserBoothDashboard with PieChart & LineChart

---

## 🚀 Setup Instructions

### Step 1: Run the User Creation Script

```bash
cd frontend
node create-all-role-users.cjs
```

This script will:
1. Create users in Supabase Authentication (auto-confirmed)
2. Create users in the `users` database table
3. Link auth users to database records
4. Verify all users are created correctly

---

### Step 2: Verify Role Display

1. **Start the development server:**
   ```bash
   npm run dev
   ```

2. **Test each role:**
   - Go to http://localhost:5173/login
   - Login with each credential above
   - Click the profile icon (bottom left sidebar)
   - **Verify the badge shows the correct role**

   Expected results:
   - `superadmin@pulseofpeople.com` → Badge: "Superadmin" (Red)
   - `admin@tvk.com` → Badge: "Admin" (Red)
   - `manager@tvk.com` → Badge: "Manager" (Yellow)
   - `analyst@tvk.com` → Badge: "Analyst" (Light Red)
   - `user@tvk.com` → Badge: "User" (Gray)

---

## 🐛 Troubleshooting

### Issue: Profile shows "Superadmin" for all roles

**Cause:** Database `users` table doesn't have the correct role for the logged-in user.

**Solution:**
```bash
# Re-run the user creation script
node create-all-role-users.cjs
```

---

### Issue: Login fails with "Invalid credentials"

**Cause:** User doesn't exist in Supabase Auth, or password is wrong.

**Solution:**
1. Check the script output for any errors
2. Manually verify in Supabase Dashboard:
   - Go to: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users
   - Look for the user email
   - If missing, click "Add User" and create manually with credentials above
   - ✅ Check "Auto Confirm User"

---

### Issue: Role badge doesn't update after login

**Cause:** Frontend is using cached auth data, or `users` table data is stale.

**Solution:**
1. **Clear browser cache and localStorage:**
   ```javascript
   // In browser console (F12)
   localStorage.clear();
   location.reload();
   ```

2. **Verify database has correct role:**
   ```sql
   -- Run in Supabase SQL Editor
   SELECT id, full_name, email, role, is_super_admin, status
   FROM users
   WHERE email IN (
     'superadmin@pulseofpeople.com',
     'admin@tvk.com',
     'manager@tvk.com',
     'analyst@tvk.com',
     'user@tvk.com'
   );
   ```

3. **Check AuthContext is fetching correctly:**
   - Open browser DevTools → Console
   - Look for `[AuthContext]` logs
   - Should show: `✅ User data loaded from database: TVK Manager, manager`

---

## 📊 Role Comparison Table

| Role | Dashboard | Charts | Geographic Scope | Key Features |
|------|-----------|--------|------------------|--------------|
| **Superadmin** | SuperAdminDashboard | Platform-wide stats | All Organizations | Tenant management, billing, audit logs |
| **Admin** | AdminDashboard | Organization overview | All Constituencies | User management, org settings |
| **Manager** | ManagerDistrictDashboard | LineChart (sentiment trend) | District (6-16 constituencies) | District analytics, constituency comparison |
| **Analyst** | AnalystConstituencyDashboard | BarChart (booth performance) | Constituency (200-300 booths) | Booth tracking, issue analysis |
| **User** | UserBoothDashboard | PieChart + LineChart | Single Booth | Feedback collection, daily reports |

---

## 🔒 Security Notes

1. **Development Credentials Only:**
   - These credentials are for testing/development only
   - **DO NOT use in production**
   - Production passwords should be:
     - Minimum 12 characters
     - Auto-generated and securely stored
     - Rotated every 90 days

2. **Service Role Key:**
   - The `create-all-role-users.cjs` script uses the service role key
   - This bypasses Row Level Security (RLS)
   - **NEVER commit service role keys to git**
   - Keep in `.env` files only

3. **Role-Based Access Control (RBAC):**
   - All permissions are enforced in the `users` table
   - Frontend checks permissions via `AuthContext.hasPermission()`
   - Backend enforces via RLS policies

---

## ✅ Success Checklist

- [ ] Ran `node create-all-role-users.cjs` successfully
- [ ] All 5 users created (superadmin, admin, manager, analyst, user)
- [ ] Logged in as `manager@tvk.com` → Badge shows "Manager" ✓
- [ ] Logged in as `analyst@tvk.com` → Badge shows "Analyst" ✓
- [ ] Logged in as `user@tvk.com` → Badge shows "User" ✓
- [ ] Manager dashboard shows LineChart ✓
- [ ] Analyst dashboard shows BarChart ✓
- [ ] User dashboard shows PieChart ✓

---

## 📝 Next Steps

Once all roles are verified:

1. **Test Role-Based Features:**
   - SuperAdmin → Can access Admin Panel
   - Admin → Can manage users
   - Manager → Can view district map
   - Analyst → Can view constituency booths
   - User → Can submit feedback

2. **Test Role Restrictions:**
   - User should NOT see Admin Panel button
   - Analyst should NOT see district-wide data
   - Manager should NOT see other districts

3. **Production Deployment:**
   - Create real users via admin panel
   - Assign proper roles based on organization hierarchy
   - Monitor audit logs for role changes

---

**Status:** ✅ Ready for Testing
**Last Updated:** 2025-11-10
**Version:** 1.0
