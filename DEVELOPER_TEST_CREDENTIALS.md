# DEVELOPER TEST CREDENTIALS

**Application**: Pulse of People - Political Sentiment Analysis Platform
**Environment**: Development/Testing
**Last Updated**: 2025-11-10

---

## 🔐 QUICK ACCESS CREDENTIALS

### **Primary Test Accounts** (Start Here)

```
SUPERADMIN (Platform Owner):
  Email:    testadmin@tvk.com
  Password: Admin@2024

ADMIN (Organization Owner):
  Email:    admin1@tvk.com
  Password: Admin@2024

MANAGER (District Manager):
  Email:    manager@tvk.com
  Password: Manager@2024

ANALYST (Constituency Head):
  Email:    analyst@tvk.com
  Password: Analyst@2024

USER (Field Worker):
  Email:    user@tvk.com
  Password: User@2024

VOLUNTEER:
  Email:    volunteer1@tvk.com
  Password: Volunteer@2024

VIEWER (Read-Only):
  Email:    viewer@tvk.com
  Password: Viewer@2024
```

---

## 🎯 ROLE-BASED TEST CREDENTIALS

### **1. SUPERADMIN** (Platform Administrator)

```
Email:    testadmin@tvk.com
Password: Admin@2024
Name:     Test Admin
Role:     superadmin
```

**Permissions**:
- ✅ Full platform access
- ✅ Create/manage organizations
- ✅ Manage all users across organizations
- ✅ View platform-wide analytics
- ✅ System configuration

**Use Cases**:
- Testing platform administration features
- Multi-organization management
- User role assignments
- System-level configurations

---

### **2. ADMIN** (Organization Administrator)

#### Primary Admin:
```
Email:    admin1@tvk.com
Password: Admin@2024
Name:     TVK Admin 1
Role:     admin
```

#### Additional Admin Accounts:
```
admin2@tvk.com    | Admin@2024 | TVK Admin 2
admin3@tvk.com    | Admin@2024 | TVK Admin 3
```

**Permissions**:
- ✅ Full organization access
- ✅ Create/manage managers and analysts
- ✅ View organization analytics
- ✅ Manage campaigns and events
- ✅ Configure organization settings

**Use Cases**:
- Testing admin dashboard
- User management workflows
- Organization-level reporting
- Campaign management

---

### **3. MANAGER** (District Manager)

#### Primary Manager:
```
Email:    manager@tvk.com
Password: Manager@2024
Name:     District Manager
Role:     manager
```

#### District-wise Managers:
```
Chennai District:
  Email:    manager.chennai@tvk.com
  Password: Manager@2024

Virudhunagar District:
  Email:    manager.virudhunagar@tvk.org
  Password: Manager@2024

Viluppuram District:
  Email:    manager.viluppuram@tvk.org
  Password: Manager@2024

Vellore District:
  Email:    manager.vellore@tvk.org
  Password: Manager@2024

Tiruvarur District:
  Email:    manager.tiruvarur@tvk.org
  Password: Manager@2024
```

**Total**: 40 district managers

**Permissions**:
- ✅ District-level operations
- ✅ Manage analysts and field workers
- ✅ View district analytics
- ✅ Coordinate campaigns in district
- ✅ Field reports management

**Use Cases**:
- Testing district-level dashboards
- Analyst coordination
- District reporting
- Field operations management

---

### **4. ANALYST** (Constituency Analyst)

#### Primary Analyst:
```
Email:    analyst@tvk.com
Password: Analyst@2024
Name:     Data Analyst
Role:     analyst
```

#### Constituency-wise Analysts (Sample):
```
Gummidipoondi:
  Email:    analyst.gummidipoondi@tvk.com
  Password: Analyst@2024

Radhapuram:
  Email:    analyst.radhapuram@tvk.org
  Password: Analyst@2024

Palayamkottai:
  Email:    analyst.palayamkottai@tvk.org
  Password: Analyst@2024

Ambur:
  Email:    analyst.ambur@tvk.org
  Password: Analyst@2024

Chennai Central:
  Email:    analyst.chennaicentral@tvk.org
  Password: Analyst@2024

Madurai Central:
  Email:    analyst.maduraicentral@tvk.org
  Password: Analyst@2024
```

**Total**: 446 constituency analysts (one per constituency)

**Email Pattern**: `analyst.<constituency>@tvk.com` or `analyst.<constituency>@tvk.org`

**Permissions**:
- ✅ Constituency-level data access
- ✅ Voter database for constituency
- ✅ Booth-level analytics
- ✅ Sentiment data analysis
- ✅ Field reports submission

**Use Cases**:
- Testing constituency dashboards
- Voter database management
- Booth-level operations
- Sentiment tracking
- Local campaign monitoring

---

### **5. USER** (Field Worker)

#### Primary User:
```
Email:    user@tvk.com
Password: User@2024
Name:     Field Worker
Role:     user
```

#### Additional User Accounts:
```
user1@tvk.com     | User@2024 | Field Worker 1
user2@tvk.com     | User@2024 | Field Worker 2
```

**Total**: 10 field workers

**Permissions**:
- ✅ Data entry and submission
- ✅ Booth-level access
- ✅ Voter interaction logging
- ✅ Field report submission
- ✅ Mobile app features

**Use Cases**:
- Testing field worker workflows
- Data collection forms
- Voter registration
- Booth management
- Mobile responsiveness

---

### **6. VOLUNTEER**

#### Primary Volunteer:
```
Email:    volunteer1@tvk.com
Password: Volunteer@2024
Name:     Volunteer 1
Role:     volunteer
```

#### Additional Volunteers:
```
volunteer@bettroi.com | Volunteer@2024 | Volunteer (External)
```

**Total**: 2 volunteers

**Permissions**:
- ✅ Limited data submission
- ✅ Assigned area access only
- ✅ Basic dashboard view
- ✅ Event participation logging

**Use Cases**:
- Testing volunteer workflows
- Limited access scenarios
- Event participation features
- Basic data collection

---

### **7. VIEWER** (Read-Only Access)

#### Primary Viewer:
```
Email:    viewer@tvk.com
Password: Viewer@2024
Name:     View Only User
Role:     viewer
```

#### Additional Viewers:
```
viewer@bettroi.com | Viewer@2024 | External Viewer
```

**Total**: 2 viewers

**Permissions**:
- ✅ Read-only dashboard access
- ✅ View reports and analytics
- ✅ No edit/create permissions
- ✅ Export functionality only

**Use Cases**:
- Testing read-only features
- Report viewing
- Data export functionality
- Guest access scenarios

---

## 📊 USER STATISTICS

```
Total Users: 507

Role Distribution:
├─ Analyst     : 446 users (87.9%) - Constituency heads
├─ Manager     :  40 users ( 7.9%) - District managers
├─ User        :  10 users ( 2.0%) - Field workers
├─ Admin       :   6 users ( 1.2%) - Organization admins
├─ Volunteer   :   2 users ( 0.4%)
├─ Viewer      :   2 users ( 0.4%)
└─ Superadmin  :   1 user  ( 0.2%) - Platform owner
```

---

## 🌐 APPLICATION URLS

### **Development**:
```
Frontend:  http://localhost:5174
Backend:   http://127.0.0.1:8000
```

### **Production** (if deployed):
```
Frontend:  https://tvk.pulseofpeople.com
Backend:   https://pulseofpeople-production.up.railway.app
```

---

## 🔑 PASSWORD PATTERNS

All test accounts follow consistent password patterns:

```
Superadmin/Admin → Admin@2024
Manager          → Manager@2024
Analyst          → Analyst@2024
User             → User@2024
Volunteer        → Volunteer@2024
Viewer           → Viewer@2024
```

**Security Note**: These are TEST credentials only. Change all passwords before production deployment.

---

## 🧪 TESTING SCENARIOS

### **Scenario 1: Admin Workflow**
1. Login as `admin1@tvk.com`
2. Navigate to User Management
3. Create a new analyst
4. Assign constituency
5. Verify access levels

### **Scenario 2: Manager Workflow**
1. Login as `manager.chennai@tvk.com`
2. View district dashboard
3. Check analyst performance
4. Review field reports
5. Generate district report

### **Scenario 3: Analyst Workflow**
1. Login as `analyst.gummidipoondi@tvk.com`
2. Access constituency dashboard
3. View voter database
4. Submit sentiment data
5. Create field report

### **Scenario 4: Field Worker Workflow**
1. Login as `user@tvk.com`
2. Access mobile interface
3. Submit voter interaction
4. Log booth visit
5. Upload photos/data

### **Scenario 5: Cross-Role Testing**
1. Test role-based access control
2. Verify data isolation
3. Check permission boundaries
4. Test unauthorized access prevention

---

## 🔐 SPECIAL TEST ACCOUNTS

### **VIP Account** (For Demo/Presentation):
```
Email:    vijay@tvk.com
Password: Vijay@2026
Name:     Vijay
Role:     superadmin
Note:     Use for demos and presentations
```

### **External Organization** (Multi-tenancy Testing):
```
Email:    admin@dmk.org
Password: Admin@2024
Name:     DMK Admin
Org:      DMK (Opposition party)
Note:     For testing data isolation
```

---

## 📝 CREDENTIAL USAGE GUIDELINES

### **DO**:
- ✅ Use these credentials for local development
- ✅ Test role-based features
- ✅ Verify permission boundaries
- ✅ Share with team developers
- ✅ Update passwords if needed

### **DON'T**:
- ❌ Use in production environment
- ❌ Share publicly or commit to git
- ❌ Use for actual campaign data
- ❌ Give to external users
- ❌ Keep default passwords in production

---

## 🆘 TROUBLESHOOTING

### **Login Issues**:
1. Verify you're on http://localhost:5174
2. Check email is spelled correctly (no extra spaces)
3. Password is case-sensitive
4. Clear browser cache and cookies
5. Check backend is running (port 8000)

### **Access Denied**:
1. Verify you're using correct role account
2. Check RLS policies are applied
3. Verify user exists in both auth.users and public.users
4. Check organization_id is set

### **Slow Login**:
- Should be <2 seconds after recent fix
- If slow, check RLS functions are updated
- Verify JWT metadata is present
- Check database connection

---

## 🔄 RESETTING CREDENTIALS

If you need to reset any password:

```bash
cd backend
source venv/bin/activate
python update_user_metadata.py
```

Or manually via Supabase Dashboard:
1. Go to Authentication → Users
2. Find user by email
3. Click "..." → Reset Password
4. Set new password

---

## 📞 SUPPORT

For credential issues:
1. Check this document first
2. Verify user exists in database
3. Run sync script if needed: `python sync_all_users.py`
4. Contact system administrator

---

**Last Verified**: 2025-11-10
**Status**: ✅ All credentials active and working
**Database**: Supabase PostgreSQL (507 users synced)

