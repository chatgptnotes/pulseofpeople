# ⚡ Quick Start - RBAC System

## 🎉 YOUR SERVER IS RUNNING!

### Access Your App:
- **Local**: http://localhost:3000/
- **Network**: http://192.168.1.16:3000/

---

## 🔐 Test Login Credentials (Mock Users)

### Admin (Full Access)
```
Email: admin@bettroi.com
Password: password
```

### Analyst (Data Access)
```
Email: analyst@bettroi.com
Password: password
```

### Viewer (Read-Only)
```
Email: viewer@bettroi.com
Password: password
```

### Volunteer (Field Worker)
```
Email: volunteer@bettroi.com
Password: password
```

---

## 📋 What You Have Now

### ✅ Working Features:
- Multi-tenant RBAC system
- 7 user roles (Super Admin → Volunteer)
- 33 granular permissions
- Role-based authentication
- Protected routes
- Permission checking hooks

### 🏗️ To Be Built:
- Super Admin Dashboard UI
- User Management Interface
- Organization Settings Page
- Role-based navigation menu

---

## 🚀 3-Step Setup (Required Once)

### Step 1: Run Database Migration
Go to https://supabase.com/dashboard → SQL Editor → Paste this file:
```
supabase/migrations/20251028_add_rbac_system.sql
```

### Step 2: Create Super Admin
In Supabase SQL Editor:
```sql
INSERT INTO users (name, email, role, is_super_admin, status)
VALUES ('Admin', 'admin@yourorg.com', 'super_admin', TRUE, 'active')
ON CONFLICT (email) DO UPDATE SET role = 'super_admin', is_super_admin = TRUE;
```

### Step 3: Test It!
Login at http://localhost:3000/login with mock credentials above

---

## 💡 Quick Code Examples

### Check Permission in Component
```typescript
import { usePermission } from '../hooks/usePermission';

function MyComponent() {
  const canExport = usePermission('export_data');

  return canExport ? <ExportButton /> : null;
}
```

### Check User Role
```typescript
import { useIsAdmin, useRole } from '../hooks/usePermission';

function Dashboard() {
  const isAdmin = useIsAdmin();
  const role = useRole();

  return (
    <div>
      {isAdmin && <AdminPanel />}
      {role === 'volunteer' && <FieldReports />}
    </div>
  );
}
```

### Protect a Route
```typescript
<Route path="/admin" element={
  <ProtectedRoute requiredPermission="manage_users">
    <AdminPage />
  </ProtectedRoute>
} />
```

---

## 🎭 Role Comparison

| Feature | Super Admin | Admin | Manager | Analyst | User | Viewer | Volunteer |
|---------|------------|-------|---------|---------|------|--------|-----------|
| Manage All Orgs | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Manage Users | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| View Analytics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Export Data | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Edit Settings | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Submit Reports | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

⚠️ = Limited access

---

## 🔍 Available Permissions (33 Total)

### Users (5)
- view_users, create_users, edit_users, delete_users, manage_roles

### Data (7)
- view_dashboard, view_analytics, view_reports, export_data, import_data, create_surveys, view_surveys

### Voters (3)
- view_voters, edit_voters, delete_voters

### Field Workers (4)
- view_field_workers, manage_field_workers, view_field_reports, submit_field_reports

### Social Media (2)
- view_social_media, manage_social_channels

### AI/Analytics (3)
- view_competitor_analysis, view_ai_insights, generate_ai_insights

### Settings (3)
- view_settings, edit_settings, manage_billing

### Alerts (2)
- view_alerts, manage_alerts

### System (4)
- manage_organizations, view_all_data, manage_system_settings, view_audit_logs

---

## 📁 Important Files

```
voter/src/
├── utils/
│   ├── permissions.ts       ← Permission functions
│   └── rbac.ts             ← Database operations
├── contexts/
│   ├── AuthContext.tsx     ← Authentication
│   └── PermissionContext.tsx ← Permissions
├── hooks/
│   └── usePermission.ts    ← Permission hooks
└── components/
    └── ProtectedRoute.tsx  ← Route protection

supabase/migrations/
└── 20251028_add_rbac_system.sql ← Database schema

Documentation/
├── RBAC_IMPLEMENTATION_GUIDE.md  ← Full technical guide
└── GETTING_STARTED_GUIDE.md      ← Detailed tutorial
```

---

## 🐛 Quick Troubleshooting

**Can't Login?**
- Use mock credentials (see top of this file)
- Check browser console for errors

**Permission Not Working?**
- Refresh the page
- Check user role in database
- Console: `localStorage.getItem('user')`

**Need to Logout?**
- Console: `localStorage.clear(); location.reload()`

---

## 🎯 What To Do Next

### Immediate (Test Current System):
1. ✅ Open http://localhost:3000/
2. ✅ Login with different users
3. ✅ Check which pages you can access
4. ✅ Test permissions

### Today (Set Up Database):
1. Run the migration in Supabase
2. Create your super admin user
3. Test with real authentication

### This Week (Build UIs):
1. Super Admin Dashboard
2. User Management Interface
3. Role-based navigation

---

## 📖 More Information

- **Full Guide**: `GETTING_STARTED_GUIDE.md`
- **Technical Docs**: `RBAC_IMPLEMENTATION_GUIDE.md`
- **Server Logs**: Check your terminal

---

## ⌨️ Useful Commands

```bash
# Start server (if not running)
cd voter && npm run dev

# Reinstall dependencies (if issues)
rm -rf node_modules package-lock.json && npm install

# Check server status
curl http://localhost:3000/
```

---

**🎉 Happy Coding!**

Your multi-tenant RBAC system is ready. Start testing with the mock users above, then set up your database when ready!

**Questions?** Check `GETTING_STARTED_GUIDE.md` for detailed explanations.
