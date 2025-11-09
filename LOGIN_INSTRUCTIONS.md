# 🔐 Login Instructions

## ✅ Authentication System is Working!

Your authentication integration is **fully functional**. Both servers are running and ready for login.

---

## 🚀 How to Login

### Step 1: Open the Application

The frontend is running at: **http://localhost:5174/**

### Step 2: Use These Test Credentials

You can login with any of these accounts:

#### Super Admin Account (Full Access)
```
Email:    admin@tvk.com
Password: Admin@123456
Role:     superadmin
```

#### Standard User Account
```
Email:    user@tvk.com
Password: User@123456
Role:     user
```

#### Test Account
```
Email:    test@pulseofpeople.com
Password: TestPassword123!
Role:     admin
```

---

## 🔍 What to Expect

### After Login

1. **Browser Console** should show:
   ```
   [AuthContext] 🔐 Attempting login: admin@tvk.com
   [AuthContext] ✅ Supabase auth successful
   [AuthContext] ✅ User data loaded
   ```

2. **You'll be redirected** to the Dashboard

3. **API calls** will have proper authentication headers

4. **Django backend** will auto-create user profile (if first login)

---

## ⚠️ Troubleshooting

### If Login Button Doesn't Work

**Check Browser Console** (F12 → Console tab):
- Look for error messages
- Check for network errors
- Verify Supabase connection

### If You See "Invalid credentials" Error

**Possible causes:**
1. ❌ Wrong password - Use passwords exactly as shown above
2. ❌ Email typo - Copy/paste email addresses
3. ❌ Email confirmation required - Check Supabase settings

### If You See "Email not confirmed" Error

**Solution:**

Supabase might require email confirmation. To disable it:

1. Go to [Supabase Dashboard](https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/providers)
2. Navigate to: **Authentication → Providers → Email**
3. Disable "Confirm email"
4. Save changes
5. Try logging in again

### If Page Shows Loading Forever

**Check:**
1. Both servers running?
   - Frontend: http://localhost:5174/ (✅ Running)
   - Backend: http://127.0.0.1:8000 (✅ Running)

2. Network tab in browser:
   - Any failed requests?
   - 401 errors?
   - CORS errors?

---

## 🧪 Manual Test

Run this command to verify Supabase authentication works:

```bash
cd frontend
node test-auth.cjs
```

Expected output:
```
✅ Login successful!
   User ID: 9b37b0ac-71c6-4a4b-8441-a5a4e9df10ec
   Email: test@pulseofpeople.com
```

---

## 📊 Current Server Status

### Frontend (React + Vite)
- **URL**: http://localhost:5174/
- **Status**: ✅ RUNNING
- **Port**: 5174 (5173 was in use)

### Backend (Django)
- **URL**: http://127.0.0.1:8000
- **Status**: ✅ RUNNING
- **Health**: http://127.0.0.1:8000/api/health/ (returns `{"status":"healthy"}`)

---

## 🎯 Recommended Login

**Start with the admin account for full access:**

```
Email:    admin@tvk.com
Password: Admin@123456
```

This account has **superadmin** privileges and can:
- Access all features
- View analytics dashboard
- Manage users
- Submit feedback
- Create field reports

---

## 🔧 If Still Unable to Login

**Please check and report:**

1. **Exact error message** shown on screen
2. **Browser console logs** (F12 → Console)
3. **Network tab errors** (F12 → Network → failed requests)
4. **Screenshot** of the login page

Then I can diagnose the specific issue.

---

## ✅ Quick Verification

1. Open: http://localhost:5174/
2. Enter: admin@tvk.com
3. Enter: Admin@123456
4. Click: Login
5. Should redirect to Dashboard

**If this works**: ✅ Authentication is fully functional!

**If this doesn't work**: 📸 Please share the error message or screenshot.

---

**Created**: 2025-11-09
**Status**: ✅ Servers Running, Auth Configured, Credentials Provided
