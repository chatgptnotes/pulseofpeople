# 🚀 Getting Started with Pulse of People - Multi-Tenant RBAC System

## ✅ Your Server is Running!

**Local URL**: http://localhost:3000/
**Network URL**: http://192.168.1.16:3000/

---

## 📋 Quick Overview

Your project now has a **complete multi-tenant Role-Based Access Control (RBAC) system** with:
- ✅ 7 user roles (Super Admin → Volunteer)
- ✅ 33 granular permissions
- ✅ Organization isolation
- ✅ Supabase authentication
- ✅ Protected routes

---

## 🎯 Step-by-Step Guide

### Step 1: Set Up the Database

You need to run the RBAC migration on your Supabase database:

#### Option A: Using Supabase Dashboard (Easiest)

1. Go to https://supabase.com/dashboard
2. Select your project: `iwtgbseaoztjbnvworyq`
3. Click "SQL Editor" in the left sidebar
4. Click "New Query"
5. Copy the contents of this file:
   ```
   supabase/migrations/20251028_add_rbac_system.sql
   ```
6. Paste into the SQL editor
7. Click "Run" (or press Cmd+Enter)

#### Option B: Using Command Line

```bash
cd /Users/apple/Downloads/Pulseofpeoplevoter23oct

# Set your database URL
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.iwtgbseaoztjbnvworyq.supabase.co:5432/postgres"

# Run the migration
psql $DATABASE_URL -f supabase/migrations/20251028_add_rbac_system.sql
```

**This will create:**
- 7 new tables (organizations, roles, permissions, etc.)
- Update the users table with RBAC fields
- Create 7 default roles
- Create 33 permissions
- Set up Row Level Security

---

### Step 2: Create Your First Super Admin

After running the migration, create a super admin user:

#### Using Supabase SQL Editor:

```sql
-- Create a super admin user (or update existing user)
INSERT INTO users (
  name,
  email,
  role,
  is_super_admin,
  status,
  permissions
)
VALUES (
  'Super Admin',
  'admin@pulseofpeople.com',
  'super_admin',
  TRUE,
  'active',
  ARRAY[]::TEXT[]
)
ON CONFLICT (email) DO UPDATE
SET
  role = 'super_admin',
  is_super_admin = TRUE;
```

---

### Step 3: Test Login

#### Mock Login (Without Supabase - For Testing)

Your app includes mock users for testing:

1. Open http://localhost:3000/
2. Click "Login" or go to http://localhost:3000/login
3. Use these credentials:

**Mock Users:**
```
Admin User:
Email: admin@bettroi.com
Password: password

Analyst:
Email: analyst@bettroi.com
Password: password

Viewer:
Email: viewer@bettroi.com
Password: password

Ward Coordinator:
Email: coordinator@bettroi.com
Password: password

Volunteer:
Email: volunteer@bettroi.com
Password: password
```

#### Real Login (With Supabase)

Once you've created users in Supabase:

1. Users need to be created through Supabase Auth
2. Then their details added to the `users` table
3. Login with their Supabase credentials

---

## 🎭 Understanding Roles

### Role Hierarchy (Level 1 = Highest)

```
Level 1: Super Admin
├── Can manage ALL organizations
├── Access all tenant data
└── System-wide settings

Level 2: Admin
├── Manage their organization
├── User management
└── Settings & billing

Level 3: Manager
├── Team management
├── User invitations
└── Field worker management

Level 4: Analyst / Coordinators
├── View analytics
├── Export data
└── Create reports

Level 5: User
├── View dashboards
├── View reports
└── Basic features

Level 6: Viewer
├── Read-only access
└── View dashboards only

Level 7: Volunteer
├── Field work
└── Submit reports
```

---

## 💡 Using the RBAC System in Your App

### Example 1: Check Permission in a Component

```typescript
import { usePermission } from '../hooks/usePermission';

function ExportButton() {
  const canExport = usePermission('export_data');

  if (!canExport) {
    return null; // Hide button
  }

  return <button onClick={handleExport}>Export Data</button>;
}
```

### Example 2: Check User Role

```typescript
import { useRole, useIsAdmin } from '../hooks/usePermission';

function Sidebar() {
  const role = useRole();
  const isAdmin = useIsAdmin();

  return (
    <nav>
      <MenuItem to="/dashboard">Dashboard</MenuItem>

      {isAdmin && (
        <MenuItem to="/admin/users">User Management</MenuItem>
      )}

      {role === 'volunteer' && (
        <MenuItem to="/field-reports">Submit Report</MenuItem>
      )}
    </nav>
  );
}
```

### Example 3: Protect a Route

```typescript
import ProtectedRoute from '../components/ProtectedRoute';

// In App.tsx or your router
<Route path="/admin/users" element={
  <ProtectedRoute requiredPermission="view_users">
    <UserManagement />
  </ProtectedRoute>
} />

// Super Admin only
<Route path="/super-admin" element={
  <ProtectedRoute superAdminOnly>
    <PlatformDashboard />
  </ProtectedRoute>
} />

// Require multiple permissions
<Route path="/analytics" element={
  <ProtectedRoute requiredPermissions={['view_analytics', 'export_data']}>
    <Analytics />
  </ProtectedRoute>
} />
```

### Example 4: Check Multiple Permissions

```typescript
import { usePermissions } from '../contexts/PermissionContext';

function DataControls() {
  const { hasAnyPermission, hasAllPermissions } = usePermissions();

  // User needs ANY of these permissions
  const canAccessData = hasAnyPermission([
    'view_analytics',
    'view_reports',
    'export_data'
  ]);

  // User needs ALL of these permissions
  const canManageData = hasAllPermissions([
    'edit_voters',
    'delete_voters'
  ]);

  return (
    <div>
      {canAccessData && <DataViewer />}
      {canManageData && <DataEditor />}
    </div>
  );
}
```

---

## 🔍 Testing Different Roles

### Test Scenario 1: Admin Features

1. Login as `admin@bettroi.com` / `password`
2. Navigate to different pages
3. You should see:
   - ✅ All dashboard features
   - ✅ Analytics and reports
   - ✅ User management (if UI exists)
   - ✅ Settings
   - ✅ Export buttons

### Test Scenario 2: Viewer (Read-Only)

1. Login as `viewer@bettroi.com` / `password`
2. You should see:
   - ✅ Dashboard (view only)
   - ✅ Reports (view only)
   - ❌ No edit buttons
   - ❌ No export buttons
   - ❌ No user management

### Test Scenario 3: Volunteer (Field Worker)

1. Login as `volunteer@bettroi.com` / `password`
2. You should see:
   - ✅ Dashboard
   - ✅ Submit field reports
   - ✅ View surveys
   - ❌ No analytics
   - ❌ No user management

---

## 📊 Available Permissions

Your system has 33 permissions across 6 categories:

### Users (5 permissions)
- `view_users` - View list of users
- `create_users` - Invite new users
- `edit_users` - Edit user information
- `delete_users` - Remove users
- `manage_roles` - Assign roles

### Data (7 permissions)
- `view_dashboard` - Access main dashboard
- `view_analytics` - View analytics
- `view_reports` - View reports
- `export_data` - Export data to CSV/Excel
- `import_data` - Import data
- `create_surveys` - Create surveys
- `view_surveys` - View survey results

### Voters (3 permissions)
- `view_voters` - Access voter database
- `edit_voters` - Edit voter info
- `delete_voters` - Remove voters

### Field Workers (4 permissions)
- `view_field_workers` - View field workers
- `manage_field_workers` - Manage field workers
- `view_field_reports` - View reports
- `submit_field_reports` - Submit reports

### Social Media (2 permissions)
- `view_social_media` - Social media monitoring
- `manage_social_channels` - Manage channels

### Analytics (3 permissions)
- `view_competitor_analysis` - Competitor data
- `view_ai_insights` - AI insights
- `generate_ai_insights` - Trigger AI analysis

### Settings (3 permissions)
- `view_settings` - View settings
- `edit_settings` - Edit settings
- `manage_billing` - Billing access

### Alerts (2 permissions)
- `view_alerts` - View alerts
- `manage_alerts` - Configure alerts

### System (4 permissions - Super Admin only)
- `manage_organizations` - Manage orgs
- `view_all_data` - Cross-org data
- `manage_system_settings` - System config
- `view_audit_logs` - Audit logs

---

## 🛠️ Common Tasks

### Task 1: Create a New User

#### Via SQL (Quick Method)

```sql
-- Add to Supabase SQL Editor
INSERT INTO users (
  name,
  email,
  role,
  organization_id,
  status
) VALUES (
  'John Manager',
  'john@example.com',
  'manager',
  NULL, -- Set organization_id if you have one
  'active'
);
```

#### Via UI (To Be Built)

The User Management interface is coming soon. For now, use SQL.

### Task 2: Change User Role

```sql
UPDATE users
SET role = 'admin',
    last_role_change = NOW()
WHERE email = 'user@example.com';
```

### Task 3: Grant Custom Permission

```sql
-- First get the permission ID
SELECT id FROM permissions WHERE name = 'export_data';

-- Then grant to user
INSERT INTO user_permissions (user_id, permission_id, granted)
SELECT
  u.id,
  p.id,
  TRUE
FROM users u, permissions p
WHERE u.email = 'user@example.com'
AND p.name = 'export_data';
```

### Task 4: Create an Organization

```sql
INSERT INTO organizations (
  tenant_id,
  name,
  slug,
  subscription_tier,
  status
) VALUES (
  'kerala-bjp',
  'Kerala BJP',
  'kerala-bjp',
  'premium',
  'active'
);
```

---

## 🎨 What You Can Do Now

### ✅ Already Working:

1. **Login System** - Mock login working, Supabase auth ready
2. **Role-Based Access** - All roles and permissions configured
3. **Permission Checking** - Use hooks anywhere in your app
4. **Protected Routes** - Restrict pages by role/permission
5. **Authentication Context** - Full user state management
6. **Permission Context** - Easy permission checking

### 🏗️ To Be Built (Next Steps):

1. **Super Admin Dashboard** - Manage all organizations
2. **User Management UI** - Invite/manage users visually
3. **Role-Based Navigation** - Dynamic menu based on role
4. **Organization Settings** - Manage org details
5. **Audit Log Viewer** - See all RBAC changes
6. **Permission Manager** - Grant/revoke permissions

---

## 🐛 Troubleshooting

### Issue: Can't Login

**Solution:**
- Make sure you're using the correct mock credentials
- Check browser console for errors
- Verify `.env` file has Supabase credentials

### Issue: Getting "Unauthorized" Error

**Solution:**
- Check your user's role in the database
- Verify the page requires a permission you have
- Try logging out and back in
- Check browser console for permission errors

### Issue: Permissions Not Loading

**Solution:**
```typescript
// Force refresh permissions
import { usePermissions } from '../contexts/PermissionContext';

const { refreshPermissions } = usePermissions();
await refreshPermissions();
```

### Issue: Database Migration Failed

**Solution:**
- Check your database connection
- Make sure tables don't already exist
- Try running sections of the migration separately
- Check Supabase logs for errors

---

## 📱 Browser Console Commands (For Testing)

Open browser console (F12) on your app and try:

```javascript
// Check current user
localStorage.getItem('user')

// Clear session (logout)
localStorage.clear()
location.reload()

// View auth token
localStorage.getItem('auth_token')
```

---

## 🎯 Next Steps for Development

### Priority 1: Test the Current System

1. ✅ Login with different mock users
2. ✅ Navigate through the app
3. ✅ Check which pages each role can access
4. ✅ Verify permissions are working

### Priority 2: Run the Database Migration

1. Run `supabase/migrations/20251028_add_rbac_system.sql`
2. Create your first super admin
3. Test with real Supabase authentication

### Priority 3: Build Management UIs

1. Super Admin Dashboard - `/super-admin`
2. User Management - `/admin/users`
3. Organization Settings - `/settings/organization`

### Priority 4: Update Navigation

1. Make sidebar dynamic based on role
2. Hide/show menu items by permission
3. Add role indicator in header

---

## 📖 Key Files to Know

```
Project Structure:
├── voter/src/
│   ├── utils/
│   │   ├── permissions.ts          # Permission checking functions
│   │   └── rbac.ts                 # Database operations
│   │
│   ├── contexts/
│   │   ├── AuthContext.tsx         # Authentication
│   │   └── PermissionContext.tsx   # Permissions
│   │
│   ├── hooks/
│   │   └── usePermission.ts        # Permission hooks
│   │
│   ├── components/
│   │   └── ProtectedRoute.tsx      # Route protection
│   │
│   └── App.tsx                     # Main app with providers
│
├── supabase/migrations/
│   └── 20251028_add_rbac_system.sql  # RBAC database schema
│
└── RBAC_IMPLEMENTATION_GUIDE.md      # Complete technical guide
```

---

## 💬 Need Help?

### Common Questions:

**Q: How do I add a new permission?**
A: Add it to the `permissions` table in the database, then add to `DEFAULT_ROLE_PERMISSIONS` in `permissions.ts`

**Q: Can I create custom roles?**
A: Yes! Insert into the `roles` table and assign permissions via `role_permissions`

**Q: How do I check if user is admin?**
A: Use `useIsAdmin()` hook or check `user.role === 'admin'`

**Q: Where are passwords stored?**
A: In Supabase Auth (secure). The `users` table only has profile data.

**Q: How do I invite users?**
A: Use Supabase Auth API or the inviteUserToOrganization() function in rbac.ts

---

## 🎉 You're All Set!

Your multi-tenant RBAC system is ready to use! Start by:

1. ✅ Testing with mock users (already working)
2. 📊 Running the database migration
3. 👤 Creating your first super admin
4. 🏗️ Building the management UIs

Happy coding! 🚀

---

**Quick Reference Card:**

```typescript
// Import hooks
import { usePermission, useIsAdmin, useRole } from '../hooks/usePermission';

// Check permission
const canEdit = usePermission('edit_users');

// Check role
const isAdmin = useIsAdmin();
const role = useRole();

// In components
{canEdit && <EditButton />}
{isAdmin && <AdminPanel />}

// Protect routes
<ProtectedRoute requiredPermission="view_analytics">
  <Analytics />
</ProtectedRoute>
```

**Server Running At:** http://localhost:3000/
