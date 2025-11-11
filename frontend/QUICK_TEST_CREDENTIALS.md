# 🔑 Quick Test Credentials

## Role Hierarchy: superadmin → admin → manager → analyst → user

---

## 1️⃣ SUPERADMIN
```
Email:    superadmin@pulseofpeople.com
Password: SuperAdmin@123
Badge:    "Superadmin" (Red)
Scope:    All Organizations
```

---

## 2️⃣ ADMIN
```
Email:    admin@tvk.com
Password: Admin@123
Badge:    "Admin" (Red)
Scope:    All Constituencies
```

---

## 3️⃣ MANAGER
```
Email:    manager@tvk.com
Password: Manager@123
Badge:    "Manager" (Yellow)
Scope:    Chennai District
Dashboard: ManagerDistrictDashboard with LineChart
```

---

## 4️⃣ ANALYST
```
Email:    analyst@tvk.com
Password: Analyst@123
Badge:    "Analyst" (Light Red)
Scope:    Perambur Constituency
Dashboard: AnalystConstituencyDashboard with BarChart
```

---

## 5️⃣ USER
```
Email:    user@tvk.com
Password: User@123
Badge:    "User" (Gray)
Scope:    Booth B-456, Ward 15
Dashboard: UserBoothDashboard with PieChart + LineChart
```

---

## ⚡ Quick Setup (Choose ONE method)

### Method 1: SQL Script (Easiest - No coding required)
1. Open Supabase SQL Editor: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/editor
2. Copy and paste: `CREATE_ALL_ROLE_USERS.sql`
3. Click "Run"
4. Follow the instructions to create Auth users manually

### Method 2: Node.js Script (Automated)
```bash
cd frontend

# Get service role key from: https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/settings/api

# Run with environment variable:
SUPABASE_SERVICE_ROLE_KEY=your_key_here node create-all-role-users.cjs
```

---

## ✅ Testing Steps

1. **Start dev server:**
   ```bash
   npm run dev
   ```

2. **Test each role:**
   - Go to http://localhost:5173/login
   - Login with credentials above
   - Click profile icon (bottom left)
   - **Verify badge shows correct role**

3. **Expected Results:**
   - manager@tvk.com → "Manager" badge ✓
   - analyst@tvk.com → "Analyst" badge ✓
   - user@tvk.com → "User" badge ✓

---

## 🐛 If Badge Still Shows Wrong Role

**Clear cache and re-login:**
```javascript
// Open browser console (F12)
localStorage.clear();
location.reload();
```

**Check database:**
```sql
SELECT email, full_name, role FROM users WHERE email = 'manager@tvk.com';
```

---

**Files Created:**
- ✅ `ROLE_HIERARCHY_SETUP.md` - Full documentation
- ✅ `CREATE_ALL_ROLE_USERS.sql` - SQL script (easiest)
- ✅ `create-all-role-users.cjs` - Node script (automated)
- ✅ `QUICK_TEST_CREDENTIALS.md` - This file
