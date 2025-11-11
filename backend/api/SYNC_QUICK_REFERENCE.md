# Supabase Sync Quick Reference

## Common Tasks

### 1. Ensure All Users Have Profiles
```bash
python manage.py sync_supabase_users --all
```

### 2. Sync Specific User
```bash
python manage.py sync_supabase_users --email user@example.com
```

### 3. Preview Changes (Dry Run)
```bash
python manage.py sync_supabase_users --all --dry-run
```

## Import Statements

```python
from api.utils import (
    sync_supabase_user,
    get_user_from_supabase_payload,
    handle_user_email_change,
    handle_user_deletion,
    ensure_user_profile_exists
)
```

## Code Examples

### Sync User from Supabase Data
```python
user = sync_supabase_user(
    supabase_user_id="uuid-123",
    email="user@example.com",
    user_metadata={
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890"
    },
    app_metadata={
        "role": "admin",
        "organization_id": "456"
    }
)
```

### Sync from JWT Payload
```python
payload = jwt.decode(token, secret, algorithms=['HS256'])
user = get_user_from_supabase_payload(payload)
```

### Handle Email Change
```python
user = handle_user_email_change(
    old_email="old@example.com",
    new_email="new@example.com"
)
```

### Soft Delete User
```python
success = handle_user_deletion(email="user@example.com")
```

### Ensure Profile Exists
```python
profile = ensure_user_profile_exists(user)
```

## Webhook Events

### Payload Format
```json
{
  "type": "user.created",
  "user": {
    "id": "uuid-123",
    "email": "user@example.com",
    "user_metadata": {},
    "app_metadata": {}
  }
}
```

### Supported Events
- `user.created` - New user registered
- `user.updated` - User data updated
- `user.deleted` - User deleted
- `user.email_changed` - Email changed

### Webhook URL
```
POST https://your-domain.com/api/webhooks/supabase/user/
```

## Environment Variables

```bash
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGc...
SUPABASE_JWT_SECRET=your-jwt-secret
SUPABASE_WEBHOOK_SECRET=your-webhook-secret
```

## Troubleshooting

### Users Without Profiles
```bash
python manage.py sync_supabase_users --all
```

### Check Logs
```bash
# Django logs show all sync operations
tail -f logs/django.log | grep "Supabase user sync"
```

### Verify JWT Secret
```python
from django.conf import settings
print(settings.SUPABASE_JWT_SECRET[:10])  # First 10 chars
```

### Test Webhook
```bash
curl -X POST https://your-domain.com/api/webhooks/supabase/user/ \
  -H "Content-Type: application/json" \
  -H "X-Supabase-Signature: <signature>" \
  -d '{
    "type": "user.created",
    "user": {
      "id": "test-uuid",
      "email": "test@example.com"
    }
  }'
```

## Role Hierarchy

From highest to lowest:
1. `superadmin` (level 7)
2. `admin` (level 6)
3. `manager` (level 5)
4. `analyst` (level 4)
5. `user` (level 3)
6. `viewer` (level 2)
7. `volunteer` (level 1)

## Common Errors

### "Email is required"
- Check JWT payload has `email` field

### "Invalid token payload"
- Verify JWT has both `sub` and `email`

### "Invalid signature"
- Check `SUPABASE_WEBHOOK_SECRET` matches

### "User profile missing"
- Run: `python manage.py sync_supabase_users --all`

## Testing

```bash
# Run all sync tests
python manage.py test api.tests_supabase_sync

# Run specific test
python manage.py test api.tests_supabase_sync.SupabaseUserSyncTestCase.test_create_new_user
```

## Logging Levels

- **INFO:** Normal sync operations
- **WARNING:** Non-critical issues (invalid role, missing org)
- **ERROR:** Failures (missing email, sync errors)

## Best Practices

1. Always use email as identifier
2. Run sync command after migrations
3. Monitor logs for errors
4. Test with dry-run first
5. Keep JWT secret secure
6. Verify webhooks with signatures
