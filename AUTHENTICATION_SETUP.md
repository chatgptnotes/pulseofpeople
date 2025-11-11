# Authentication Integration Setup Guide

## Overview

The Pulse of People platform now uses **Supabase Authentication** on the frontend with **Django REST Framework** backend integration. This guide will help you complete the authentication setup.

---

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   React     │  Login  │   Supabase   │  Verify │   Django    │
│  Frontend   ├────────>│     Auth     ├────────>│   Backend   │
│             │<────────┤              │<────────┤             │
└─────────────┘  Token  └──────────────┘   User  └─────────────┘
```

### How It Works

1. **User logs in** via React frontend (AuthContext.tsx)
2. **Supabase authenticates** and returns JWT token
3. **Token stored** in Supabase session (not localStorage)
4. **API calls** extract token from Supabase session
5. **Django validates** Supabase JWT using HybridAuthentication
6. **Django creates/syncs** user profile automatically

---

## ✅ What's Already Done

### Frontend Changes
- ✅ `AuthContext.tsx` - Uses Supabase Auth exclusively
- ✅ `djangoApi.ts` - Extracts tokens from Supabase session (not localStorage)
- ✅ `lib/supabase.ts` - Supabase client configured

### Backend Changes
- ✅ `api/authentication.py` - HybridAuthentication validates Supabase JWT
- ✅ `config/settings.py` - REST Framework configured for hybrid auth
- ✅ Auto user creation - Django creates users from Supabase tokens

---

## 🔧 Required Configuration

### Step 1: Get Your Supabase JWT Secret

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `iwtgbseaoztjbnvworyq`
3. Navigate to: **Settings → API**
4. Copy the **JWT Secret** (under "JWT Settings")

   ```
   Example:
   your-super-secret-jwt-secret-32-characters-or-more
   ```

### Step 2: Update Backend Environment

Edit `/backend/.env` and replace the placeholder:

```env
# Find this line:
SUPABASE_JWT_SECRET=your-jwt-secret-here-get-from-supabase-dashboard

# Replace with actual secret from Step 1:
SUPABASE_JWT_SECRET=your-actual-jwt-secret-from-supabase
```

### Step 3: Verify Configuration

Check that all required variables are set:

**Backend (.env)**
```env
SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co  ✅
SUPABASE_ANON_KEY=eyJhbGci...                          ✅
SUPABASE_JWT_SECRET=your-actual-jwt-secret              ⚠️ UPDATE THIS
```

**Frontend (.env)**
```env
VITE_SUPABASE_URL=https://iwtgbseaoztjbnvworyq.supabase.co  ✅
VITE_SUPABASE_ANON_KEY=eyJhbGci...                          ✅
VITE_DJANGO_API_URL=http://localhost:8000/api                ✅
```

---

## 🚀 Testing the Integration

### Start Development Servers

**Terminal 1 - Backend:**
```bash
cd backend
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Test Authentication Flow

1. **Navigate to**: http://localhost:5173
2. **Click Login** or **Sign Up**
3. **Use Supabase credentials**:
   - Email: `test@example.com`
   - Password: Your Supabase test user password

4. **Check Console Logs**:
   - Frontend: `[AuthContext] ✅ Supabase auth successful`
   - Backend: Django should validate token and create user

5. **Test Protected API**:
   - Navigate to Dashboard
   - Check Network tab for API calls to `/api/*`
   - Verify `Authorization: Bearer <token>` header is present
   - Confirm 200 responses (not 401 Unauthorized)

---

## 🔍 Debugging

### Common Issues

#### 1. "Authentication failed: Invalid token"

**Cause**: SUPABASE_JWT_SECRET not configured or incorrect

**Fix**:
```bash
# Verify backend .env has correct JWT secret
grep SUPABASE_JWT_SECRET backend/.env

# Should match the secret in Supabase Dashboard
```

#### 2. "401 Unauthorized" on API calls

**Cause**: Token not being sent or invalid

**Fix**:
```javascript
// Check browser console for:
[djangoApi] Error getting session: ...

// Or check Network tab:
// Authorization header should be: Bearer eyJhbGci...
```

#### 3. "No active session found"

**Cause**: User not logged in via Supabase

**Fix**:
```javascript
// Check AuthContext logs:
[AuthContext] ❌ No active session found

// User needs to log in via Supabase Auth
```

### Enable Debug Logging

**Backend:**
```python
# In settings.py, set:
DEBUG = True

# Check Django console for authentication logs
```

**Frontend:**
```javascript
// Check browser console for:
[AuthContext] 🔐 Attempting login
[djangoApi] Getting auth token
```

---

## 📊 Verification Checklist

After completing setup, verify:

- [ ] Backend .env has SUPABASE_JWT_SECRET configured
- [ ] Frontend builds without TypeScript errors
- [ ] User can log in via Supabase Auth
- [ ] Token appears in Network requests (`Authorization` header)
- [ ] Django API returns 200 (not 401) for authenticated requests
- [ ] Django creates user profile automatically on first login
- [ ] User can access protected pages (Dashboard, Analytics)

---

## 🔐 How Token Validation Works

### Frontend (djangoApi.ts)

```typescript
// Extracts token from Supabase session
const getAuthToken = async (): Promise<string | null> => {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token || null;
};

// Adds token to all authenticated API calls
headers['Authorization'] = `Bearer ${token}`;
```

### Backend (authentication.py)

```python
# HybridAuthentication tries Supabase JWT first
class HybridAuthentication:
    def authenticate(self, request):
        # 1. Try Supabase JWT validation
        supabase_auth = SupabaseJWTAuthentication()
        result = supabase_auth.authenticate(request)

        # 2. Fallback to Django JWT (migration period)
        if not result:
            django_jwt_auth = JWTAuthentication()
            return django_jwt_auth.authenticate(request)
```

---

## 🎯 Next Steps

Once authentication is working:

1. **Remove Django JWT** (optional):
   - If fully migrated to Supabase, remove `djangorestframework_simplejwt`
   - Update settings.py to use only SupabaseJWTAuthentication

2. **Production Configuration**:
   - Set `DEBUG=False` in backend
   - Use environment-specific .env files
   - Configure HTTPS for production

3. **Security Enhancements**:
   - Enable Row-Level Security (RLS) in Supabase
   - Add rate limiting for auth endpoints
   - Implement refresh token rotation

---

## 📞 Support

If you encounter issues:

1. Check browser console for frontend errors
2. Check Django console for backend errors
3. Verify environment variables are loaded correctly
4. Test with Supabase Dashboard → Authentication → Users

---

## 📝 Summary

**What Changed:**
- Frontend now extracts tokens from Supabase session (not localStorage)
- Backend validates Supabase JWT tokens automatically
- Django creates/syncs users from Supabase auth

**What You Need to Do:**
1. Get JWT Secret from Supabase Dashboard
2. Update `backend/.env` with SUPABASE_JWT_SECRET
3. Test login flow at http://localhost:5173

**Expected Result:**
✅ Users log in via Supabase
✅ Frontend sends Supabase JWT to Django
✅ Django validates token and allows access
✅ Django auto-creates user profiles

---

**Last Updated**: 2025-11-09
**Status**: ✅ Integration Complete - Requires JWT Secret Configuration
