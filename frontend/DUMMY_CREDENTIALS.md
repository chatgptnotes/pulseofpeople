# 🔑 Dummy Test Credentials (No Supabase Setup Needed)

## Quick Copy-Paste Credentials

### Role Hierarchy: superadmin → admin → manager → analyst → user

---

## 1. SUPERADMIN
```
Email:    super@test.com
Password: super123
```

---

## 2. ADMIN
```
Email:    admin@test.com
Password: admin123
```

---

## 3. MANAGER
```
Email:    manager@test.com
Password: manager123
```

---

## 4. ANALYST
```
Email:    analyst@test.com
Password: analyst123
```

---

## 5. USER
```
Email:    user@test.com
Password: user123
```

---

## 📋 All Credentials Table

| Role | Email | Password | Dashboard | Charts |
|------|-------|----------|-----------|--------|
| **Superadmin** | super@test.com | super123 | SuperAdminDashboard | Platform stats |
| **Admin** | admin@test.com | admin123 | AdminDashboard | Org overview |
| **Manager** | manager@test.com | manager123 | ManagerDistrictDashboard | ✅ LineChart |
| **Analyst** | analyst@test.com | analyst123 | AnalystConstituencyDashboard | ✅ BarChart |
| **User** | user@test.com | user123 | UserBoothDashboard | ✅ PieChart + LineChart |

---

## ⚡ Quick Test

1. **Start app:**
   ```bash
   npm run dev
   ```

2. **Login with any credential above**

3. **Navigate to your dashboard to see charts**

---

## 🎯 Expected Results After Login

- **manager@test.com** → See ManagerDistrictDashboard with LineChart
- **analyst@test.com** → See AnalystConstituencyDashboard with BarChart
- **user@test.com** → See UserBoothDashboard with PieChart

---

## 📝 Notes

- These are dummy credentials for frontend testing only
- No database/Supabase setup required
- Works with mock authentication
- Role badge in profile should display correct role

---

**Status:** ✅ Ready to Use
**Setup Required:** None
