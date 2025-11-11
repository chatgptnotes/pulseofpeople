# Supabase User Synchronization Guide

## Overview

This document describes the user synchronization mechanism between Supabase authentication and Django database.

## Architecture

The sync mechanism ensures that every Supabase authenticated user has a corresponding Django User and UserProfile record.

### Components

1. **Utils Module** (`api/utils.py`)
   - Core synchronization logic
   - Transaction-safe user creation/updates
   - Email change handling
   - User deletion handling

2. **Authentication Module** (`api/authentication.py`)
   - JWT token verification
   - Automatic user sync on authentication
   - Hybrid authentication (Supabase + Django JWT)

3. **Signals Module** (`api/signals.py`)
   - Automatic UserProfile creation
   - Audit logging
   - Future: Role sync back to Supabase

4. **Webhooks Module** (`api/webhooks.py`)
   - Webhook endpoints for Supabase events
   - Signature verification
   - Event handlers (create, update, delete)

5. **Management Command** (`management/commands/sync_supabase_users.py`)
   - Manual sync operations
   - Batch profile creation
   - Dry-run mode

## How It Works

### 1. Authentication Flow

```
User Request → JWT Token → Verify Token → Extract Payload → Sync User → Return User
```

**Step-by-step:**
1. User sends request with `Authorization: Bearer <supabase_jwt>`
2. `SupabaseJWTAuthentication` extracts and verifies the token
3. Token payload is passed to `get_user_from_supabase_payload()`
4. `sync_supabase_user()` creates/updates Django User and UserProfile
5. User object is returned for the request

### 2. User Synchronization

**Email as Unique Identifier:**
- Email is used as the primary identifier (not Supabase UUID)
- Prevents duplicate users across systems
- Handles email changes gracefully

**Transaction Safety:**
- All sync operations wrapped in `@transaction.atomic`
- Rollback on any error to prevent partial updates
- No orphaned User records without UserProfile

**Data Flow:**
```python
Supabase JWT Payload:
{
  "sub": "uuid-123",               # Supabase user ID
  "email": "user@example.com",
  "user_metadata": {
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "bio": "...",
    "avatar_url": "https://..."
  },
  "app_metadata": {
    "role": "admin",
    "organization_id": "123"
  }
}

Django User:
- username (from user_metadata.username or email)
- email (from email)
- first_name (from user_metadata.first_name)
- last_name (from user_metadata.last_name)

Django UserProfile:
- role (from app_metadata.role or user_metadata.role)
- phone (from user_metadata.phone)
- bio (from user_metadata.bio)
- avatar_url (from user_metadata.avatar_url)
- organization (from app_metadata.organization_id)
```

### 3. Signal Handlers

**Automatic Profile Creation:**
```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Creates UserProfile with default role='user' if missing
```

**Audit Logging:**
```python
@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    # Logs all user creation events to AuditLog
```

### 4. Webhook Integration

**Supported Events:**
- `user.created` - New user registered in Supabase
- `user.updated` - User metadata updated
- `user.deleted` - User deleted from Supabase
- `user.email_changed` - User email changed

**Setup:**
1. Configure webhook URL in Supabase: `https://your-domain.com/api/webhooks/supabase/user/`
2. Set `SUPABASE_WEBHOOK_SECRET` in Django settings
3. Webhooks will automatically sync users in real-time

## Usage

### Manual Sync Command

**Sync all users (ensure profiles exist):**
```bash
python manage.py sync_supabase_users --all
```

**Sync specific user:**
```bash
python manage.py sync_supabase_users --email user@example.com
```

**Dry run (preview changes):**
```bash
python manage.py sync_supabase_users --all --dry-run
```

### Programmatic Usage

**Sync user from JWT payload:**
```python
from api.utils import get_user_from_supabase_payload

payload = {
    "sub": "uuid-123",
    "email": "user@example.com",
    "user_metadata": {"first_name": "John"},
    "app_metadata": {"role": "admin"}
}

user = get_user_from_supabase_payload(payload)
```

**Sync user with custom data:**
```python
from api.utils import sync_supabase_user

user = sync_supabase_user(
    supabase_user_id="uuid-123",
    email="user@example.com",
    user_metadata={"first_name": "John", "phone": "+1234567890"},
    app_metadata={"role": "manager", "organization_id": "456"}
)
```

**Handle email change:**
```python
from api.utils import handle_user_email_change

user = handle_user_email_change(
    old_email="old@example.com",
    new_email="new@example.com"
)
```

**Handle user deletion:**
```python
from api.utils import handle_user_deletion

success = handle_user_deletion(email="user@example.com")
```

## Configuration

### Required Settings

Add to `backend/config/settings.py`:

```python
# Supabase Configuration
SUPABASE_URL = env('SUPABASE_URL', default='')
SUPABASE_KEY = env('SUPABASE_ANON_KEY', default='')
SUPABASE_JWT_SECRET = env('SUPABASE_JWT_SECRET', default='')
SUPABASE_WEBHOOK_SECRET = env('SUPABASE_WEBHOOK_SECRET', default='')

# Authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.authentication.HybridAuthentication',  # Supabase + Django JWT
        # OR for Supabase only:
        # 'api.authentication.SupabaseJWTAuthentication',
    ],
}
```

### Environment Variables

Create `.env` file:
```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_WEBHOOK_SECRET=your-webhook-secret
```

**Getting JWT Secret:**
1. Go to Supabase Dashboard → Settings → API
2. Copy "JWT Secret" (not the anon key)
3. This is used to verify JWT tokens

## Edge Cases Handled

### 1. Duplicate Usernames
If username already exists, appends a counter:
```python
username = "john_doe"  # Already exists
# Creates: john_doe1, john_doe2, etc.
```

### 2. Missing UserProfile
Automatically creates profile with default role='user':
```python
# Signal handler ensures every User has a UserProfile
@receiver(post_save, sender=User)
def create_user_profile(...):
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance, role='user')
```

### 3. Email Changes
Updates email while maintaining referential integrity:
```python
# Validates new email is unique before updating
handle_user_email_change(old_email, new_email)
```

### 4. User Deletion
Soft-deletes by marking inactive (preserves audit trails):
```python
user.is_active = False
user.save()
```

### 5. Invalid Role
Falls back to default 'user' role if invalid:
```python
valid_roles = ['superadmin', 'admin', 'manager', 'analyst', 'user', 'viewer', 'volunteer']
if role not in valid_roles:
    role = 'user'
```

### 6. Missing Organization
Logs warning and continues without org assignment:
```python
try:
    organization = Organization.objects.get(pk=organization_id)
except Organization.DoesNotExist:
    logger.warning(f"Organization {organization_id} not found")
    # Continues without org
```

## Logging

All sync operations are logged with appropriate levels:

**INFO:** Normal operations
```
INFO: Supabase user sync complete: user@example.com (user_created=True)
```

**WARNING:** Non-critical issues
```
WARNING: Invalid role 'invalid', defaulting to 'user'
```

**ERROR:** Failures
```
ERROR: User sync failed: Email is required
```

## Testing

### Test User Sync
```python
from django.test import TestCase
from api.utils import sync_supabase_user

class SupabaseSyncTestCase(TestCase):
    def test_create_user(self):
        user = sync_supabase_user(
            supabase_user_id="test-uuid",
            email="test@example.com",
            user_metadata={"first_name": "Test"},
            app_metadata={"role": "user"}
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.profile.role, "user")
```

### Test Authentication
```python
from rest_framework.test import APITestCase
from api.authentication import SupabaseJWTAuthentication

class SupabaseAuthTestCase(APITestCase):
    def test_valid_token(self):
        # Test with valid Supabase JWT
        pass
```

## Troubleshooting

### Issue: Users created without profiles
**Solution:** Run sync command
```bash
python manage.py sync_supabase_users --all
```

### Issue: Duplicate users
**Cause:** Email mismatch between systems
**Solution:** Consolidate users manually, ensure email is canonical

### Issue: Token verification fails
**Cause:** Wrong JWT secret
**Solution:** Verify `SUPABASE_JWT_SECRET` matches Supabase dashboard

### Issue: Webhook not working
**Cause:** Invalid signature or missing secret
**Solution:** Check `SUPABASE_WEBHOOK_SECRET` configuration

## Best Practices

1. **Always use email as identifier** - Don't rely on Supabase UUID in Django
2. **Run sync command after bulk imports** - Ensure all users have profiles
3. **Monitor audit logs** - Track all user operations
4. **Use dry-run first** - Test sync operations before applying
5. **Handle errors gracefully** - Log but don't fail the entire request
6. **Keep metadata in sync** - Update both Supabase and Django when needed

## Migration Checklist

- [ ] Add environment variables to `.env`
- [ ] Update `settings.py` with Supabase config
- [ ] Run migrations (if any new fields added)
- [ ] Run `sync_supabase_users --all` to create missing profiles
- [ ] Test authentication with Supabase JWT
- [ ] Configure webhook endpoint in Supabase dashboard
- [ ] Monitor logs for sync operations
- [ ] Update frontend to use Supabase auth

## Future Enhancements

1. **Bi-directional sync** - Sync Django role changes back to Supabase
2. **Batch operations** - Bulk user import from Supabase
3. **Real-time sync** - Use Supabase realtime for instant updates
4. **Conflict resolution** - Handle concurrent updates
5. **Supabase UUID storage** - Store Supabase UUID in Django for reference
