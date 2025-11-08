# Audit Logging Quick Reference

## Installation

```bash
cd backend
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python test_audit_logging.py  # Run tests
```

## Quick Usage

### Import
```python
from api.utils.audit import log_action, ACTION_USER_CREATED, capture_model_state, get_field_changes
from api.decorators.audit import audit_log, audit_log_method
```

### Log an Action
```python
log_action(
    user=request.user,
    action=ACTION_USER_CREATED,
    resource_type='User',
    resource_id=str(user.id),
    changes={'username': user.username, 'role': 'analyst'},
    request=request
)
```

### Decorator (Function-based View)
```python
@audit_log(action=ACTION_USER_UPDATED, resource_type='User', capture_changes=True)
def update_user(request, pk):
    # Your logic
    pass
```

### Decorator (ViewSet Method)
```python
class UserViewSet(viewsets.ModelViewSet):
    @audit_log_method(action=ACTION_USER_CREATED, resource_type='User')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
```

### Capture Changes
```python
before = capture_model_state(profile)
profile.role = 'admin'
profile.save()
after = capture_model_state(profile)
changes = get_field_changes(before, after)
```

## API Endpoints (Superadmin Only)

```bash
# List logs
GET /api/superadmin/audit-logs/
GET /api/superadmin/audit-logs/?action=user_created&user_id=123

# Get single log
GET /api/superadmin/audit-logs/{id}/

# Export CSV
GET /api/superadmin/audit-logs/export/

# Statistics
GET /api/superadmin/audit-logs/stats/

# Recent logs
GET /api/superadmin/audit-logs/recent/

# User activity
GET /api/superadmin/audit-logs/user-activity/?user_id=123

# Resource history
GET /api/superadmin/audit-logs/resource-history/?resource_type=User&resource_id=123
```

## Action Constants

```python
# User actions
ACTION_USER_CREATED = 'user_created'
ACTION_USER_UPDATED = 'user_updated'
ACTION_USER_DELETED = 'user_deleted'
ACTION_ROLE_CHANGED = 'role_changed'

# Auth actions
ACTION_LOGIN_SUCCESS = 'login_success'
ACTION_LOGIN_FAILED = 'login_failed'
ACTION_LOGOUT = 'logout'
ACTION_PASSWORD_CHANGED = 'password_changed'

# Permission actions
ACTION_PERMISSION_GRANTED = 'permission_granted'
ACTION_PERMISSION_REVOKED = 'permission_revoked'

# Booth actions
ACTION_BOOTH_CREATED = 'booth_created'
ACTION_BOOTH_UPLOADED = 'booth_uploaded'
ACTION_BOOTH_DELETED = 'booth_deleted'

# Report actions
ACTION_REPORT_SUBMITTED = 'report_submitted'
ACTION_REPORT_REVIEWED = 'report_reviewed'

# Bulk actions
ACTION_BULK_UPLOAD_STARTED = 'bulk_upload_started'
ACTION_BULK_UPLOAD_COMPLETED = 'bulk_upload_completed'

# Organization actions
ACTION_ORGANIZATION_CREATED = 'organization_created'
ACTION_ORGANIZATION_UPDATED = 'organization_updated'
ACTION_SETTINGS_UPDATED = 'settings_updated'
```

## Common Patterns

### Login Logging
```python
# Success
log_action(user=user, action=ACTION_LOGIN_SUCCESS, resource_type='Authentication', request=request)

# Failure
log_action(user=None, action=ACTION_LOGIN_FAILED, resource_type='Authentication',
           changes={'username': username}, request=request)
```

### CRUD Logging
```python
# Create
log_action(user=request.user, action=ACTION_USER_CREATED, resource_type='User',
           resource_id=str(user.id), changes={'username': user.username}, request=request)

# Update (with changes)
before = capture_model_state(user)
user.email = 'new@email.com'
user.save()
after = capture_model_state(user)
log_action(user=request.user, action=ACTION_USER_UPDATED, resource_type='User',
           resource_id=str(user.id), changes=get_field_changes(before, after), request=request)

# Delete
log_action(user=request.user, action=ACTION_USER_DELETED, resource_type='User',
           resource_id=str(user.id), changes={'username': user.username}, request=request)
```

### Bulk Operations
```python
log_action(user=request.user, action=ACTION_BULK_UPLOAD_STARTED,
           resource_type='BulkUploadJob', resource_id=str(job.id),
           changes={'file_name': file.name, 'total_rows': 100}, request=request)
```

## Query Examples

```python
from api.models import AuditLog

# Get user's logs
logs = AuditLog.objects.filter(user=user).order_by('-timestamp')

# Get logs for specific action
logs = AuditLog.objects.filter(action='user_created')

# Get logs for resource
logs = AuditLog.objects.filter(target_model='User', target_id='123')

# Get recent logs
logs = AuditLog.objects.all()[:100]

# Search logs
logs = AuditLog.objects.filter(
    Q(user__username__icontains=search) |
    Q(action__icontains=search)
)
```

## Troubleshooting

### Logs not created?
```python
# Use sync logging for debugging
log_action(..., async_log=False)
```

### Check if action is valid
```python
from api.models import AuditLog
valid_actions = [choice[0] for choice in AuditLog.ACTION_TYPES]
print('user_created' in valid_actions)
```

### View errors
```bash
# Check Django logs
tail -f logs/django.log
```

## Files Location

```
backend/
├── api/
│   ├── utils/
│   │   └── audit.py              # Core utility
│   ├── decorators/
│   │   └── audit.py              # Decorators
│   ├── middleware/
│   │   └── audit_middleware.py  # Middleware
│   ├── views/
│   │   └── audit_logs.py        # ViewSet
│   ├── models.py                 # AuditLog model
│   ├── serializers.py            # Serializers
│   └── urls/
│       └── superadmin_urls.py    # Routes
├── test_audit_logging.py         # Tests
├── AUDIT_LOGGING_SETUP.md        # Full guide
└── AUDIT_QUICK_REFERENCE.md      # This file
```

## Enable Middleware (Optional)

In `config/settings.py`:
```python
MIDDLEWARE = [
    # ... existing middleware ...
    'api.middleware.audit_middleware.AuditLoggingMiddleware',  # Add this
]
```

## Testing

```bash
# Run test suite
python test_audit_logging.py

# Manual test
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from api.utils.audit import log_action, ACTION_LOGIN_SUCCESS
>>> user = User.objects.first()
>>> log_action(user=user, action=ACTION_LOGIN_SUCCESS, resource_type='Auth', async_log=False)
>>> from api.models import AuditLog
>>> AuditLog.objects.filter(user=user).count()
```

## Performance Tips

1. Use async logging (default): `async_log=True`
2. Use list serializer for large lists
3. Add pagination to queries
4. Use indexed fields for filtering
5. Archive old logs periodically

## Security Notes

- Passwords/tokens/secrets are auto-redacted
- Logs are immutable (no update/delete via API)
- Superadmin access only
- IP addresses are captured
- User agents are captured (truncated to 500 chars)

## Need Help?

1. Read: `AUDIT_LOGGING_SETUP.md` (full documentation)
2. Read: `AUDIT_IMPLEMENTATION_SUMMARY.md` (what was built)
3. Run: `python test_audit_logging.py` (test suite)
4. Check: Inline code comments
