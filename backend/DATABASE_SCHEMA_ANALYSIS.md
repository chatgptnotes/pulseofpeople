# Database Schema Analysis - Pulse of People

## Executive Summary

**Current Status:** ⚠️ **HYBRID ARCHITECTURE WITH POTENTIAL ISSUES**

Your database has TWO separate user tables:
1. **Supabase `auth.users`** - 303 users (authentication)
2. **Django `auth_user`** - 792 users (application logic)

This creates complexity and potential sync issues.

---

## 📊 Current Database Structure

### User-Related Tables

```
┌─────────────────────────┐
│   auth.users (Supabase) │  ← Authentication (login/logout)
│   303 users             │
│   UUID primary keys     │
└─────────────────────────┘
           │
           │ NO DIRECT LINK!
           │
           ↓
┌─────────────────────────┐
│   auth_user (Django)    │  ← Application users
│   792 users             │
│   Integer primary keys  │
└───────────┬─────────────┘
            │ FK: user_id
            ↓
┌─────────────────────────┐
│   api_userprofile       │  ← Extended user data
│   792 profiles          │
│   role, org, district   │
└─────────────────────────┘
```

### Foreign Key Relationships

```sql
api_userprofile.user_id          → auth_user.id (Django)
api_userprofile.organization_id   → api_organization.id
api_userprofile.assigned_district_id → api_district.id
api_userprofile.assigned_state_id → api_state.id
```

---

## ⚠️ Critical Issues Identified

### Issue #1: Two Separate User Tables

**Problem:**
- Supabase auth.users uses **UUID** (e.g., `600ec5a2-baab-44a0-9ac6-2ce67a22a8e4`)
- Django auth_user uses **Integer** (e.g., `18`)
- **NO foreign key relationship** between them!

**Impact:**
- When user logs in via Supabase, frontend gets UUID
- Django backend expects Integer ID
- **ID mismatch** causes authorization failures

**Example:**
```
User: analyst@tvk.com
├─ Supabase auth.users ID: 600ec5a2-baab-44a0-9ac6-2ce67a22a8e4
└─ Django auth_user ID: 18

Frontend sends: 600ec5a2-baab-44a0-9ac6-2ce67a22a8e4
Backend expects: 18
Result: ❌ User not found!
```

### Issue #2: Data Sync Mismatch

**Current Counts:**
- Supabase auth.users: **303 users**
- Django auth_user: **792 users**
- Difference: **489 users only in Django**

**This means:**
- 489 users can use Django backend BUT cannot log in (no Supabase auth)
- OR there are duplicate/orphaned users

### Issue #3: No Linking Mechanism

**api_userprofile references Django auth_user, not Supabase auth.users:**

```python
# Current model (models.py)
class UserProfile(models.Model):
    user = models.OneToOneField(User, ...)  # Django User
    # Problem: No field to store Supabase UUID!
```

**This breaks the authentication flow:**
1. User logs in with Supabase → Gets UUID token
2. Frontend calls Django API with UUID
3. Django tries to find user by UUID → **Fails!**

---

## ✅ Correct Architecture (Recommendation)

### Option A: Store Supabase UUID in Django (Recommended)

**Add a field to link Supabase and Django:**

```python
# models.py
class UserProfile(models.Model):
    user = models.OneToOneField(User, ...)  # Django user (for Django admin)
    supabase_uid = models.UUIDField(unique=True, null=True)  # ← ADD THIS
    role = models.CharField(...)
    organization = models.ForeignKey(...)
```

**Migration needed:**
```sql
ALTER TABLE api_userprofile
ADD COLUMN supabase_uid UUID UNIQUE;

CREATE INDEX idx_userprofile_supabase_uid
ON api_userprofile(supabase_uid);
```

**Benefits:**
- ✅ Both systems work independently
- ✅ Django admin still functions with auth_user
- ✅ API can lookup by Supabase UUID
- ✅ Easy to sync in both directions

**Authentication Flow:**
```
1. User logs in → Supabase returns JWT with UUID
2. Frontend sends UUID in Authorization header
3. Django backend:
   - Validates JWT (already working)
   - Looks up UserProfile by supabase_uid
   - Gets associated auth_user for permissions
4. ✅ User authenticated and authorized!
```

---

### Option B: Use Only Supabase auth.users (Complex)

**Remove Django auth_user entirely:**

```python
# models.py
class UserProfile(models.Model):
    # user = models.OneToOneField(User, ...)  ← REMOVE
    supabase_uid = models.UUIDField(primary_key=True)  # Use Supabase ID as PK
    email = models.EmailField(unique=True)
    role = models.CharField(...)
```

**Benefits:**
- ✅ Single source of truth
- ✅ No sync issues

**Drawbacks:**
- ❌ Django admin breaks (needs auth_user)
- ❌ All existing code needs rewriting
- ❌ Lose Django's built-in permission system

---

### Option C: Keep Current + Add Sync (Not Recommended)

**Sync Supabase → Django after every auth operation:**

**Drawbacks:**
- ❌ Complex sync logic
- ❌ Race conditions possible
- ❌ Still have two sources of truth
- ❌ Performance overhead

---

## 🎯 Recommended Solution

**Use Option A: Add `supabase_uid` to UserProfile**

### Step-by-Step Implementation

#### 1. Create Migration

```python
# backend/api/migrations/0012_add_supabase_uid.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0011_twofactorbackupcode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='supabase_uid',
            field=models.UUIDField(null=True, unique=True),
        ),
        migrations.AddIndex(
            model_name='userprofile',
            name='idx_supabase_uid',
            fields=['supabase_uid'],
        ),
    ]
```

#### 2. Update Model

```python
# api/models.py

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    supabase_uid = models.UUIDField(unique=True, null=True, blank=True,
                                     help_text="Supabase Auth user ID")
    role = models.CharField(...)
    # ... rest of fields
```

#### 3. Update Authentication Middleware

```python
# api/authentication.py

class HybridAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # ... existing JWT validation ...

        supabase_uid = jwt_payload.get('sub')  # UUID from Supabase

        try:
            # Lookup by Supabase UUID first
            profile = UserProfile.objects.get(supabase_uid=supabase_uid)
            user = profile.user
        except UserProfile.DoesNotExist:
            # Fallback: lookup by email and set supabase_uid
            email = jwt_payload.get('email')
            user = User.objects.get(email=email)
            profile = user.profile
            profile.supabase_uid = supabase_uid
            profile.save()

        return (user, None)
```

#### 4. Update User Creation Script

```python
# management/commands/setup_supabase_users.py

def create_supabase_user(self, email, password, user_metadata):
    # Create in Supabase
    response = self.supabase.auth.admin.create_user(...)
    supabase_uid = response.user.id  # UUID

    # Create/update in Django
    user, created = User.objects.get_or_create(email=email, ...)

    # Create/update profile with Supabase UID
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'supabase_uid': supabase_uid,  # ← CRITICAL
            'role': user_metadata['role'],
            ...
        }
    )

    # If profile exists but missing supabase_uid, add it
    if not created and not profile.supabase_uid:
        profile.supabase_uid = supabase_uid
        profile.save()
```

#### 5. Backfill Existing Users

```python
# One-time script to sync existing users

from api.models import UserProfile
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

for profile in UserProfile.objects.filter(supabase_uid__isnull=True):
    try:
        # Find in Supabase by email
        result = supabase.auth.admin.list_users()
        supabase_user = next(
            (u for u in result if u.email == profile.user.email),
            None
        )

        if supabase_user:
            profile.supabase_uid = supabase_user.id
            profile.save()
            print(f'✅ Synced {profile.user.email}')
        else:
            print(f'⚠️  No Supabase user for {profile.user.email}')
    except Exception as e:
        print(f'❌ Error: {e}')
```

---

## 📋 Action Items

### Immediate Tasks

1. **Create migration** to add `supabase_uid` field
2. **Run migration** on database
3. **Backfill existing users** with their Supabase UUIDs
4. **Update authentication middleware** to use `supabase_uid`
5. **Update user creation script** to always set `supabase_uid`
6. **Test login flow** end-to-end

### Testing Checklist

- [ ] User can log in via Supabase Auth
- [ ] Django backend recognizes user by UUID
- [ ] UserProfile data loads correctly
- [ ] Role-based permissions work
- [ ] RLS policies filter data correctly
- [ ] Django admin still works (uses auth_user)

---

## 🔍 Verification Queries

### Check Sync Status

```sql
-- Users in Supabase but not in Django
SELECT au.email
FROM auth.users au
LEFT JOIN auth_user du ON au.email = du.email
WHERE du.id IS NULL;

-- Users in Django but not in Supabase
SELECT du.email
FROM auth_user du
LEFT JOIN auth.users au ON du.email = au.email
WHERE au.id IS NULL;

-- Profiles missing supabase_uid
SELECT u.email
FROM api_userprofile up
JOIN auth_user u ON up.user_id = u.id
WHERE up.supabase_uid IS NULL;
```

---

## 🎓 Summary

**Current State:**
- ❌ Two disconnected user tables (Supabase UUID vs Django Integer)
- ❌ No linking mechanism between them
- ❌ Potential authentication/authorization failures

**Recommended Fix:**
- ✅ Add `supabase_uid` UUID field to `api_userprofile`
- ✅ Use it as the primary lookup mechanism
- ✅ Keep Django `auth_user` for admin/backwards compatibility
- ✅ Sync Supabase UUID during user creation

**Expected Result:**
- ✅ Seamless authentication with Supabase
- ✅ Django backend can find users by Supabase UUID
- ✅ Both systems work in harmony
- ✅ No data loss or migration headaches

---

**Next Step:** Proceed with Option A implementation?
