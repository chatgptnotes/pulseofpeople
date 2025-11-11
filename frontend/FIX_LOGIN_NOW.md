# 🚨 URGENT: Fix Login in 2 Minutes

## ✅ Good News: Supabase Connection Works!

The test confirms:
- ✅ Supabase is reachable (200 OK)
- ✅ Auth API is healthy
- ❌ **Issue:** `admin@tvk.com` - Invalid login credentials

---

## 🔧 Solution: Fix the User in Supabase Dashboard

### **Option A: Confirm Existing User Email (Fastest - 1 minute)**

1. **Open Supabase Auth Users:**
   ```
   https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users
   ```

2. **Find user:** Look for `admin@tvk.com` in the list

3. **Confirm email:**
   - Click the **3 dots (...)** next to the user
   - Select **"Confirm Email"**
   - You should see a ✅ green checkmark

4. **Try login again:**
   - Go to: http://localhost:5174
   - Email: `admin@tvk.com`
   - Password: `Admin@123456`

---

### **Option B: Create New User (If user doesn't exist - 2 minutes)**

1. **Open Supabase Auth Users:**
   ```
   https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users
   ```

2. **Click "Add User" → "Create new user"**

3. **Fill in details:**
   ```
   Email: admin@tvk.com
   Password: Admin@123456
   ```

4. **IMPORTANT:** ✅ Check the box **"Auto Confirm User"**

5. **Click "Create User"**

6. **Try login:**
   - Go to: http://localhost:5174
   - Email: `admin@tvk.com`
   - Password: `Admin@123456`

---

## 🎯 Quick Links

| Action | Link |
|--------|------|
| **Supabase Auth Users** | https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users |
| **Your Login Page** | http://localhost:5174 |
| **Supabase Dashboard** | https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq |

---

## 🔍 Why "Failed to Fetch" in Browser?

The browser shows "Failed to fetch" because the auth request returns a 400 error (invalid credentials), which the frontend interprets as a network failure. Once you confirm/create the user, this will be fixed.

---

## 📸 Visual Guide

**Step 1:** Open Auth Users page
![](https://supabase.com/dashboard/project/iwtgbseaoztjbnvworyq/auth/users)

**Step 2:** Find admin@tvk.com and click "..."

**Step 3:** Click "Confirm Email" OR "Create new user"

**Step 4:** Login at http://localhost:5174

---

## ✅ After Login Works

Once logged in, you'll have access to:
- 👤 **Superadmin Dashboard**
- 📊 **Analytics & Reports**
- 🗺️ **Interactive Maps**
- ⚙️ **System Settings**
- 👥 **User Management**

---

**Your frontend is ready:** http://localhost:5174
**Just need to fix the user in Supabase!** ⬆️
