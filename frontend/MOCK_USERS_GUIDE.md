# 🎭 Mock Users Guide - Test All Roles Without Database!

## ✨ What's This?

You can now test the **complete RBAC system** without setting up Supabase database!

All test users are built-in and ready to use.

---

## 🔐 Available Test Accounts

All accounts use password: **`password`**

### 🟣 Super Admin (Highest Level)
```
Email: superadmin@pulseofpeople.com
Password: password
```

**What this user can do:**
- ✅ Manage ALL organizations
- ✅ Access all tenant data
- ✅ System-wide settings
- ✅ Create/delete organizations
- ✅ Manage all users
- ✅ All permissions enabled

**Use this to:** Test platform management, see everything

---

### 🔵 Admin (Organization Level)
```
Email: admin@bettroi.com
Password: password
```

**What this user can do:**
- ✅ Manage users in their organization
- ✅ Access all org features
- ✅ Edit settings
- ✅ Manage billing
- ✅ View all analytics
- ❌ Cannot see other organizations

**Use this to:** Test organization management

---

### 🟢 Manager (Team Level)
```
Email: manager@bettroi.com
Password: password
```

**What this user can do:**
- ✅ Create/edit users
- ✅ Manage field workers
- ✅ View analytics
- ✅ Export data
- ❌ Cannot manage billing
- ❌ Cannot edit system settings

**Use this to:** Test team management features

---

### 🟡 Analyst (Data Level)
```
Email: analyst@bettroi.com
Password: password
```

**What this user can do:**
- ✅ View all analytics
- ✅ View reports
- ✅ Export data
- ✅ View AI insights
- ❌ Cannot manage users
- ❌ Cannot edit data

**Use this to:** Test analytics features

---

### ⚪ User (Standard Level)
```
Email: user@bettroi.com
Password: password
```

**What this user can do:**
- ✅ View dashboard
- ✅ View analytics
- ✅ View reports
- ✅ View surveys
- ❌ Cannot export
- ❌ Cannot manage anything

**Use this to:** Test standard user experience

---

### 🔘 Viewer (Read-Only)
```
Email: viewer@bettroi.com
Password: password
```

**What this user can do:**
- ✅ View dashboard (read-only)
- ✅ View analytics (read-only)
- ✅ View reports (read-only)
- ❌ Cannot edit anything
- ❌ Cannot export
- ❌ No management access

**Use this to:** Test read-only access

---

### 🟤 Volunteer (Field Worker)
```
Email: volunteer@bettroi.com
Password: password
```

**What this user can do:**
- ✅ View dashboard
- ✅ Submit field reports
- ✅ View surveys
- ❌ Cannot view analytics
- ❌ Cannot export data
- ❌ Limited dashboard access

**Use this to:** Test field worker app

---

### Additional Specialized Roles

#### Ward Coordinator
```
Email: coordinator@bettroi.com
Password: password
```
Can submit data, view ward-specific data, verify local reports

#### Social Media Manager
```
Email: social@bettroi.com
Password: password
```
Can manage social media channels, view social trends

#### Survey Team
```
Email: survey@bettroi.com
Password: password
```
Can create and manage surveys, view results

#### Truth Team
```
Email: truth@bettroi.com
Password: password
```
Can verify submissions, view competitor analysis, manage alerts

---

## 🎯 How to Test

### Step 1: Go to Login
```
http://localhost:3000/login
```

### Step 2: Pick a Role to Test
Choose from the accounts above

### Step 3: Login
```
Email: [pick one from above]
Password: password
```

### Step 4: Explore
Navigate through the app and notice:
- Different menu items visible/hidden
- Different buttons enabled/disabled
- Different features accessible

### Step 5: Test Another Role
1. Logout (or clear: `localStorage.clear()` in console)
2. Login with a different account
3. Compare the differences!

---

## 📊 Permission Comparison

| Feature | Super Admin | Admin | Manager | Analyst | User | Viewer | Volunteer |
|---------|------------|-------|---------|---------|------|--------|-----------|
| Platform Management | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Org Management | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| User Management | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Export Data | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit Settings | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Billing | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Submit Reports | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| View Dashboard | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| AI Insights | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

---

## 💡 Test Scenarios

### Scenario 1: Super Admin Power
1. Login as: `superadmin@pulseofpeople.com`
2. Navigate everywhere
3. Should see: ALL features, NO restrictions

### Scenario 2: Admin vs Manager
1. Login as: `admin@bettroi.com`
2. Note what you can access
3. Logout and login as: `manager@bettroi.com`
4. Compare: Admin has more settings access

### Scenario 3: Viewer Restrictions
1. Login as: `viewer@bettroi.com`
2. Try to find edit buttons
3. Should see: Only view access, no edits

### Scenario 4: Volunteer Experience
1. Login as: `volunteer@bettroi.com`
2. Should see: Limited dashboard, field reports only
3. No analytics or export options

### Scenario 5: Role Progression
Login in this order to see hierarchy:
1. Volunteer (least access)
2. Viewer
3. User
4. Analyst
5. Manager
6. Admin
7. Super Admin (most access)

---

## 🔍 Verify Permissions

After logging in, open browser console (F12) and type:

```javascript
// Check current user
JSON.parse(localStorage.getItem('user'))

// Should show:
// {
//   "email": "...",
//   "role": "super_admin",
//   "is_super_admin": true,
//   "permissions": [...]
// }
```

---

## 🎨 What to Look For

### Navigation Menu
Different roles see different menu items:
- Super Admin: Everything + Platform Settings
- Admin: Everything for their org
- Viewer: Only view pages
- Volunteer: Only field work pages

### Buttons & Actions
- Export buttons (hidden for viewer, volunteer)
- Edit buttons (hidden for viewer)
- Delete buttons (hidden for non-admins)
- Settings buttons (admin+ only)

### Page Access
Try accessing:
- `/dashboard` - All can access
- `/analytics` - Viewer+
- `/settings` - Admin+
- `/admin/users` - Admin+ (coming soon)

---

## 🚀 When You're Ready for Real Supabase

The mock system works exactly like the real one will!

When ready to switch:
1. Run the database migration (QUICK_SETUP_STEPS.md)
2. Create real users in Supabase
3. System automatically uses Supabase instead of mock

**No code changes needed!** The AuthContext handles both.

---

## 🐛 Troubleshooting

### Can't Login
**Try:**
1. Make sure you're using exact email from above
2. Password is always: `password`
3. Check browser console for errors

### Wrong Permissions
**Try:**
```javascript
// Force logout in console
localStorage.clear()
location.reload()
// Then login again
```

### Don't See All Features
**Check:** You might be logged in as a restricted role (viewer, volunteer)
**Solution:** Login as admin or super admin to see everything

---

## ✅ Quick Reference

**Highest Access:**
- `superadmin@pulseofpeople.com` - Platform level

**Organization Level:**
- `admin@bettroi.com` - Full org access
- `manager@bettroi.com` - Team management

**Data Access:**
- `analyst@bettroi.com` - Analytics
- `user@bettroi.com` - Standard

**Limited Access:**
- `viewer@bettroi.com` - Read only
- `volunteer@bettroi.com` - Field work only

**All passwords:** `password`

---

## 🎉 Benefits of Mock Users

✅ **Test immediately** - No database setup needed
✅ **Try all roles** - Switch between accounts easily
✅ **Safe testing** - Nothing permanent
✅ **Fast iteration** - No API delays
✅ **Learn the system** - Understand permissions before deploying

When ready, just connect Supabase and you're production-ready!

---

**Enjoy testing your multi-tenant RBAC system!** 🚀

Server running at: http://localhost:3000/
