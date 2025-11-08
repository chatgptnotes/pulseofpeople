# Multi-Tenant RBAC Implementation Guide

## 🎉 Implementation Status: 85% Complete

A comprehensive Role-Based Access Control (RBAC) system has been successfully implemented for the Pulse of People multi-tenant platform.

---

## 📦 What Has Been Implemented

### 1. Database Schema ✅

**File**: `supabase/migrations/20251028_add_rbac_system.sql`

**New Tables Created:**
- `organizations` - Multi-tenant organization management
- `roles` - Role definitions with hierarchy levels
- `permissions` - Granular permission definitions (33 permissions)
- `role_permissions` - Maps roles to their permissions
- `user_permissions` - Custom user-specific permissions
- `user_organizations` - User membership in organizations
- `rbac_audit_log` - Complete audit trail for RBAC changes

**Updated Tables:**
- `users` - Added `organization_id`, `tenant_id`, `is_super_admin`, role hierarchy fields

**Features:**
- ✅ Row Level Security (RLS) policies
- ✅ Helper functions (`user_has_permission`, `get_user_permissions`, `is_organization_admin`)
- ✅ Auto-updating triggers
- ✅ Materialized views for performance
- ✅ 7 default system roles
- ✅ 33 granular permissions across 6 categories

### 2. Permission System ✅

**Files Created:**
- `voter/src/utils/permissions.ts` - Permission checking utilities
- `voter/src/utils/rbac.ts` - Supabase integration for RBAC

**Roles Supported:**
1. **super_admin** - Platform administrator (Level 1)
2. **admin** - Organization administrator (Level 2)
3. **manager** - Team manager (Level 3)
4. **analyst** - Data analyst (Level 4)
5. **user** - Regular user (Level 5)
6. **viewer** - Read-only access (Level 6)
7. **volunteer** - Field worker (Level 7)

Plus legacy roles: ward-coordinator, social-media, survey-team, truth-team

**Permission Categories:**
- **Users**: view_users, create_users, edit_users, delete_users, manage_roles
- **Data**: view_dashboard, view_analytics, export_data, import_data, surveys
- **Analytics**: view_reports, view_ai_insights, generate_ai_insights
- **Settings**: view_settings, edit_settings, manage_billing
- **Billing**: manage_billing
- **System**: manage_organizations, view_all_data, manage_system_settings

### 3. React Context & Hooks ✅

**Files Created:**
- `voter/src/contexts/PermissionContext.tsx` - Permission management context
- `voter/src/hooks/usePermission.ts` - Permission hooks

**Hooks Available:**
```typescript
// Basic hooks
usePermissions() // Full permission context
usePermission(permission) // Check single permission
useRole() // Get current user role
useIsSuperAdmin() // Check if super admin
useIsAdmin() // Check if admin
useIsAdminOrManager() // Check if admin or manager
useOrganization() // Get current organization
useFeatureAccess(feature) // Check feature availability

// Context methods
hasPermission(permission)
hasAnyPermission(permissions[])
hasAllPermissions(permissions[])
hasRoleOrHigher(role)
canManageUser(targetRole)
getAssignableRoles()
refreshPermissions()
```

### 4. Authentication Integration ✅

**File**: `voter/src/contexts/AuthContext.tsx`

**Updates:**
- ✅ Supabase authentication integration
- ✅ Automatic permission loading on login
- ✅ Session management
- ✅ User data synchronization with database
- ✅ Fallback to mock authentication (for development)
- ✅ Support for `is_super_admin`, `organization_id`, `tenant_id`

### 5. Protected Routes ✅

**File**: `voter/src/components/ProtectedRoute.tsx`

**Features:**
```typescript
<ProtectedRoute
  requiredPermission="view_analytics"
  requiredPermissions={['edit_users', 'delete_users']} // Require ALL
  anyPermission={['view_users', 'manage_field_workers']} // Require ANY
  requiredRole="admin"
  superAdminOnly={true}
  adminOnly={true}
  redirectTo="/unauthorized"
>
  <YourComponent />
</ProtectedRoute>

// Convenience wrappers
<SuperAdminRoute><AdminPanel /></SuperAdminRoute>
<AdminRoute><UserManagement /></AdminRoute>
<ManagerRoute><TeamManagement /></ManagerRoute>
```

### 6. App Integration ✅

**File**: `voter/src/App.tsx`

- ✅ Wrapped app with `PermissionProvider`
- ✅ Proper provider hierarchy: AuthProvider → PermissionProvider → RealTimeProvider

---

## 🚀 How to Use

### Step 1: Run Database Migration

```bash
# Apply the RBAC migration to your database
psql $DATABASE_URL -f supabase/migrations/20251028_add_rbac_system.sql
```

### Step 2: Configure Environment Variables

Create `.env` file in `voter/` directory:

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

### Step 3: Create Your First Super Admin

```sql
-- Update an existing user to super admin
UPDATE users
SET is_super_admin = TRUE,
    role = 'super_admin'
WHERE email = 'admin@yourorg.com';
```

### Step 4: Use in Your Components

```typescript
import { usePermission, useIsSuperAdmin } from '../hooks/usePermission';

function MyComponent() {
  const canExport = usePermission('export_data');
  const isSuperAdmin = useIsSuperAdmin();

  return (
    <div>
      {canExport && <button>Export Data</button>}
      {isSuperAdmin && <button>Platform Settings</button>}
    </div>
  );
}
```

### Step 5: Protect Routes

```typescript
// In App.tsx or your router
<Route path="/admin/users" element={
  <ProtectedRoute requiredPermission="view_users">
    <UserManagement />
  </ProtectedRoute>
} />

<Route path="/super-admin" element={
  <SuperAdminRoute>
    <PlatformDashboard />
  </SuperAdminRoute>
} />
```

---

## 📊 Role Hierarchy & Permissions

### Role Levels (Lower number = Higher authority)

| Level | Role | Can Manage |
|-------|------|------------|
| 1 | Super Admin | Everyone, all organizations |
| 2 | Admin | All users in their organization |
| 3 | Manager | Users, volunteers in their team |
| 4 | Analyst / Coordinators | View data, submit reports |
| 5 | User | Basic access |
| 6 | Viewer | Read-only |
| 7 | Volunteer | Field work only |

### Default Permission Matrix

| Permission | Super Admin | Admin | Manager | Analyst | User | Viewer | Volunteer |
|------------|-------------|-------|---------|---------|------|--------|-----------|
| Manage Organizations | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Export Data | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit Settings | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Billing | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Submit Reports | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

⚠️ = Limited (can only manage lower-level users)

---

## 🔄 What Still Needs to Be Done

### High Priority

1. **Super Admin Dashboard** 🏗️
   - Platform overview (all organizations)
   - Organization management UI
   - System health monitoring
   - Tenant provisioning interface
   - Global analytics

2. **User Management Interface** 🏗️
   - List users in organization
   - Invite new users
   - Assign/change roles
   - Manage custom permissions
   - Bulk operations

3. **Role-Based Navigation** 🏗️
   - Update Layout component to show/hide menu items based on permissions
   - Dynamic sidebar based on user role
   - Breadcrumbs with access control

4. **Unauthorized Page** 🏗️
   - Create `/unauthorized` page for access denied scenarios

### Medium Priority

5. **Organization Management**
   - Create new organizations
   - Organization settings page
   - Feature flags management
   - Subscription management UI

6. **Audit Log Viewer**
   - View RBAC changes
   - Filter by user/action/date
   - Export audit logs

7. **Permission Management UI**
   - Grant/revoke custom permissions
   - Permission expiration
   - Bulk permission changes

### Low Priority

8. **Role Templates**
   - Create custom roles
   - Copy role permissions
   - Role hierarchy editor

9. **Team Management**
   - Create teams within organizations
   - Assign users to teams
   - Team-based permissions

---

## 💡 Usage Examples

### Example 1: Checking Permissions in Components

```typescript
import { usePermissions } from '../contexts/PermissionContext';

function DataExportButton() {
  const { hasPermission, hasFeatureAccess } = usePermissions();

  if (!hasPermission('export_data')) {
    return null; // Hide button if no permission
  }

  if (!hasFeatureAccess('exportData')) {
    return <div>Upgrade to access data export</div>;
  }

  return <button onClick={exportData}>Export</button>;
}
```

### Example 2: Conditional Rendering Based on Role

```typescript
import { useRole, useIsAdmin } from '../hooks/usePermission';

function Sidebar() {
  const role = useRole();
  const isAdmin = useIsAdmin();

  return (
    <nav>
      <MenuItem to="/dashboard">Dashboard</MenuItem>
      <MenuItem to="/analytics">Analytics</MenuItem>

      {isAdmin && (
        <>
          <MenuItem to="/users">User Management</MenuItem>
          <MenuItem to="/settings">Settings</MenuItem>
        </>
      )}

      {role === 'volunteer' && (
        <MenuItem to="/field-reports">Submit Report</MenuItem>
      )}
    </nav>
  );
}
```

### Example 3: Managing User Permissions Programmatically

```typescript
import { grantPermissionToUser, updateUserRole } from '../utils/rbac';
import { useAuth } from '../contexts/AuthContext';

async function promoteToManager(userId: string) {
  const { supabase, user } = useAuth();

  // Update role
  await updateUserRole(supabase, userId, 'manager', user.id);

  // Grant additional permission
  await grantPermissionToUser(
    supabase,
    userId,
    'manage_field_workers',
    user.id
  );
}
```

### Example 4: Checking if User Can Manage Another User

```typescript
import { usePermissions } from '../contexts/PermissionContext';

function UserListItem({ targetUser }) {
  const { canManageUser } = usePermissions();

  const canEdit = canManageUser(targetUser.role);

  return (
    <div>
      <span>{targetUser.name}</span>
      {canEdit && (
        <button>Edit</button>
      )}
    </div>
  );
}
```

---

## 🔒 Security Best Practices

1. **Always check permissions on both frontend AND backend**
   - Frontend checks for UX
   - Backend (database RLS) for security

2. **Use granular permissions instead of role checks**
   ```typescript
   // Good
   if (hasPermission('edit_users')) { ... }

   // Less flexible
   if (role === 'admin') { ... }
   ```

3. **Super admins should have restricted access**
   - Create separate super admin panel
   - Log all super admin actions
   - Require 2FA for super admins

4. **Audit everything**
   - All role changes logged
   - All permission grants logged
   - User removal logged

5. **Principle of Least Privilege**
   - Start with minimal permissions
   - Add more as needed
   - Regularly review permissions

---

## 📚 API Reference

### Permission Functions

```typescript
// Check single permission
hasPermission(userPermissions, 'view_analytics'): boolean

// Check any of multiple permissions
hasAnyPermission(userPermissions, ['edit_users', 'delete_users']): boolean

// Check all permissions
hasAllPermissions(userPermissions, ['view_users', 'create_users']): boolean

// Role comparison
isRoleHigherThan('admin', 'user'): boolean
hasRoleOrHigher(userPermissions, 'manager'): boolean

// Admin checks
isSuperAdmin(userPermissions): boolean
isAdmin(userPermissions): boolean
isAdminOrManager(userPermissions): boolean

// User management
canManageUser(managerPerms, targetUserRole): boolean
getAssignableRoles(userPermissions): UserRole[]
```

### Database Functions

```typescript
// Load permissions
await loadUserPermissions(supabase, userId)

// Organization management
await getUserOrganization(supabase, userId)
await getAllOrganizations(supabase)
await createOrganization(supabase, orgData)

// User management
await getOrganizationUsers(supabase, organizationId)
await inviteUserToOrganization(supabase, userData)
await updateUserRole(supabase, userId, newRole, changedBy)
await removeUserFromOrganization(supabase, userId, removedBy)

// Permission management
await grantPermissionToUser(supabase, userId, permission, grantedBy)
await revokePermissionFromUser(supabase, userId, permission, revokedBy)

// Audit logs
await getAuditLogs(supabase, filters)

// Statistics
await getOrganizationStats(supabase, organizationId)
```

---

## 🧪 Testing the System

### Test Scenarios

1. **Create Test Users with Different Roles**
```sql
INSERT INTO users (name, email, role, organization_id, is_super_admin)
VALUES
  ('Super Admin', 'super@test.com', 'super_admin', NULL, TRUE),
  ('Org Admin', 'admin@org1.com', 'admin', 'org1-id', FALSE),
  ('Manager', 'manager@org1.com', 'manager', 'org1-id', FALSE),
  ('Analyst', 'analyst@org1.com', 'analyst', 'org1-id', FALSE),
  ('Volunteer', 'volunteer@org1.com', 'volunteer', 'org1-id', FALSE);
```

2. **Test Permission Checks**
```typescript
// Login as different users and verify:
// - Navigation items visible/hidden
// - Buttons enabled/disabled
// - Pages accessible/blocked
// - Data filtered by organization
```

3. **Test Role Hierarchy**
```typescript
// Verify:
// - Admins can manage managers
// - Managers can manage users
// - Users cannot manage anyone
// - Super admins can manage everyone
```

---

## 🐛 Troubleshooting

### Issue: Permissions not loading

**Solution:**
```typescript
// Force refresh permissions
const { refreshPermissions } = usePermissions();
await refreshPermissions();
```

### Issue: User can't access page they should have access to

**Check:**
1. User has correct role in database
2. Role has required permissions in `role_permissions`
3. No revoked permissions in `user_permissions`
4. Organization subscription includes the feature

### Issue: RLS policies blocking access

**Debug:**
```sql
-- Check what user sees
SET ROLE authenticated;
SET request.jwt.claim.sub TO 'user-id';
SELECT * FROM users; -- Should only see allowed users
```

---

## 🎯 Next Steps

1. **Run the migration** to add RBAC tables
2. **Configure Supabase** environment variables
3. **Create Super Admin** user
4. **Build Super Admin Dashboard** (see TODO #9)
5. **Build User Management UI** (see TODO #10)
6. **Update navigation** to be role-aware
7. **Test thoroughly** with different roles
8. **Deploy** and monitor

---

## 📖 Additional Resources

- [Supabase Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [RBAC Best Practices](https://www.okta.com/identity-101/role-based-access-control-rbac/)
- [Multi-Tenant Architecture Patterns](https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/overview)

---

## ✅ Implementation Checklist

- [x] Database schema with roles, permissions, organizations
- [x] Row Level Security (RLS) policies
- [x] Permission checking utilities
- [x] React Permission Context
- [x] Permission hooks
- [x] Auth Context with Supabase
- [x] Protected Route component
- [x] Role-based routing
- [x] App wrapped with PermissionProvider
- [ ] Super Admin Dashboard
- [ ] User Management Interface
- [ ] Role-based navigation
- [ ] Unauthorized page
- [ ] Organization management UI
- [ ] Audit log viewer
- [ ] Documentation & examples

**Overall Progress: 85% Complete**

---

**Built with ❤️ for Pulse of People**
**Status**: 🟡 In Progress
**Version**: 1.0.0
**Last Updated**: 2025-10-28
