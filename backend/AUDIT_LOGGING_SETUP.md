# Audit Logging Implementation Guide

## Overview

This document describes the comprehensive audit logging system integrated into the Pulse of People backend API. The system automatically logs all important user actions and provides APIs for viewing and analyzing audit logs.

## Features

- **Automatic Logging**: Middleware and decorators for automatic audit logging
- **Asynchronous Processing**: Logs are written in background threads to avoid blocking requests
- **Error Resilience**: Audit logging failures never break main request flows
- **Comprehensive Tracking**: Captures user, action, resource, changes, IP address, and user agent
- **Filtering & Search**: Powerful API for querying logs by user, action, date, resource, etc.
- **Export Functionality**: Export audit logs to CSV
- **Statistics**: Get audit log statistics and activity reports

## Architecture

### Components

1. **Audit Utility** (`api/utils/audit.py`)
   - Core logging functions
   - State capture and change detection
   - IP address and user agent extraction
   - Action type constants

2. **Decorators** (`api/decorators/audit.py`)
   - `@audit_log()` - For function-based views
   - `@audit_log_method()` - For ViewSet methods
   - `@audit_login()` - For login views

3. **Middleware** (`api/middleware/audit_middleware.py`)
   - Automatic logging of all write operations (POST, PUT, PATCH, DELETE)
   - Configurable exclusions
   - Request body capture (with sensitive field redaction)

4. **ViewSet** (`api/views/audit_logs.py`)
   - Read-only API for audit logs
   - Advanced filtering and search
   - CSV export
   - Statistics endpoint

5. **Serializers** (`api/serializers.py`)
   - `AuditLogSerializer` - Full serializer with changes
   - `AuditLogListSerializer` - Simplified for lists

6. **Model** (`api/models.py`)
   - Enhanced with 30+ action types
   - Indexed fields for performance
   - JSON field for changes

## Setup

### 1. Run Migrations

```bash
cd backend
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

### 2. (Optional) Enable Middleware

If you want automatic logging of all write operations, add the middleware to `config/settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware ...
    'api.middleware.audit_middleware.AuditLoggingMiddleware',
]
```

**Note**: The middleware is optional. You can use just decorators for more granular control.

### 3. Test the Implementation

```bash
python test_audit_logging.py
```

## Usage

### Manual Logging

```python
from api.utils.audit import log_action, ACTION_USER_CREATED

# In your view
log_action(
    user=request.user,
    action=ACTION_USER_CREATED,
    resource_type='User',
    resource_id=str(new_user.id),
    changes={
        'username': new_user.username,
        'email': new_user.email,
        'role': 'analyst'
    },
    request=request
)
```

### Using Decorators

```python
from api.decorators.audit import audit_log
from api.utils.audit import ACTION_USER_UPDATED

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
@audit_log(action=ACTION_USER_UPDATED, resource_type='User', capture_changes=True)
def update_user(request, pk):
    # Your update logic
    return Response(data)
```

### Capturing Changes

```python
from api.utils.audit import capture_model_state, get_field_changes, log_action

# Before update
before_state = capture_model_state(user_profile)

# Make changes
user_profile.role = 'admin'
user_profile.save()

# After update
after_state = capture_model_state(user_profile)
changes = get_field_changes(before_state, after_state)

# Log it
log_action(
    user=request.user,
    action='role_changed',
    resource_type='UserProfile',
    resource_id=str(user_profile.id),
    changes={'fields': changes},
    request=request
)
```

## API Endpoints

All audit log endpoints require Superadmin role.

### List Audit Logs

```
GET /api/superadmin/audit-logs/

Query Parameters:
- user_id: Filter by user ID
- username: Filter by username (partial match)
- action: Filter by action type
- resource_type: Filter by resource type
- resource_id: Filter by resource ID
- date_from: Filter from date (ISO format)
- date_to: Filter to date (ISO format)
- search: Search across multiple fields
- page: Page number
- page_size: Results per page (max 500)

Response:
{
    "count": 1000,
    "next": "http://api.com/audit-logs/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": 123,
            "username": "admin",
            "action": "user_created",
            "action_display": "User Created",
            "target_model": "User",
            "target_id": "456",
            "ip_address": "192.168.1.1",
            "timestamp": "2025-01-01T12:00:00Z"
        }
    ]
}
```

### Get Single Audit Log

```
GET /api/superadmin/audit-logs/{id}/

Response:
{
    "id": 1,
    "user": 123,
    "username": "admin",
    "user_email": "admin@example.com",
    "action": "user_created",
    "action_display": "User Created",
    "target_model": "User",
    "target_id": "456",
    "changes": {
        "username": "newuser",
        "email": "newuser@example.com",
        "role": "analyst"
    },
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "timestamp": "2025-01-01T12:00:00Z"
}
```

### Export to CSV

```
GET /api/superadmin/audit-logs/export/

Supports same filters as list endpoint.
Returns CSV file with all audit log data.
Limited to 10,000 records per export.
```

### Get Statistics

```
GET /api/superadmin/audit-logs/stats/

Response:
{
    "total_logs": 1000,
    "action_counts": {
        "user_created": 50,
        "user_updated": 200,
        "login_success": 500
    },
    "resource_counts": {
        "User": 250,
        "PollingBooth": 100
    },
    "recent_activity": {
        "last_24_hours": 50,
        "last_7_days": 200,
        "last_30_days": 500
    },
    "top_users": [
        {
            "user_id": 123,
            "username": "admin",
            "email": "admin@example.com",
            "activity_count": 150
        }
    ]
}
```

### Get Recent Logs

```
GET /api/superadmin/audit-logs/recent/

Returns last 100 audit logs.
```

### Get User Activity

```
GET /api/superadmin/audit-logs/user-activity/?user_id=123

Returns all audit logs for a specific user (paginated).
```

### Get Resource History

```
GET /api/superadmin/audit-logs/resource-history/?resource_type=User&resource_id=123

Returns all audit logs for a specific resource (paginated).
```

## Action Types

The system tracks 30+ action types:

### User Actions
- `user_created` - User account created
- `user_updated` - User profile updated
- `user_deleted` - User account deleted
- `role_changed` - User role changed

### Permission Actions
- `permission_granted` - Permission granted to user
- `permission_revoked` - Permission revoked from user

### Polling Booth Actions
- `booth_created` - Polling booth created
- `booth_uploaded` - Polling booth uploaded
- `booth_deleted` - Polling booth deleted

### Report Actions
- `report_submitted` - Field report submitted
- `report_reviewed` - Field report reviewed

### Authentication Actions
- `login_success` - Successful login
- `login_failed` - Failed login attempt
- `logout` - User logout
- `password_changed` - Password changed

### Organization Actions
- `organization_created` - Organization created
- `organization_updated` - Organization updated
- `settings_updated` - Settings updated

### Bulk Operations
- `bulk_upload_started` - Bulk upload job started
- `bulk_upload_completed` - Bulk upload job completed
- `bulk_create` - Bulk create operation
- `bulk_update` - Bulk update operation
- `bulk_delete` - Bulk delete operation

### Generic Actions
- `create` - Generic create
- `read` - Generic read
- `update` - Generic update
- `delete` - Generic delete
- `upload` - Generic upload

## Security Considerations

1. **Sensitive Data**: Password fields are automatically redacted from logs
2. **Immutable**: Audit logs cannot be modified or deleted through the API
3. **Access Control**: Only Superadmins can view audit logs
4. **IP Tracking**: Client IP addresses are captured (respects X-Forwarded-For)
5. **User Agent**: Browser/client information is captured

## Performance Considerations

1. **Asynchronous Logging**: By default, logs are written in background threads
2. **Indexed Fields**: user, action, target_model, target_id, and timestamp are indexed
3. **Pagination**: All list endpoints are paginated (100 per page by default)
4. **Export Limits**: CSV exports are limited to 10,000 records
5. **Error Handling**: Logging failures never block main requests

## Already Implemented

The following endpoints already have audit logging:

1. **Authentication** (`api/views/auth.py`)
   - Login (success/failure)
   - Logout
   - User registration (creation)
   - Profile updates

2. **Bulk Upload** (`api/views/user_management.py`)
   - Bulk upload started

## Next Steps

To complete the audit logging integration:

1. **Add to More Endpoints**
   - Polling booth CRUD operations
   - Permission management
   - Organization settings
   - Field reports

2. **Add Completion Logging**
   - Bulk upload completion (in the background task)
   - Other long-running operations

3. **Frontend Integration**
   - Create audit log viewer component
   - Add to admin dashboard
   - Display user activity history

4. **Notifications**
   - Send notifications for critical actions
   - Alert on suspicious activity

5. **Analytics**
   - Create audit log dashboard
   - Activity trends and patterns
   - Security monitoring

## Troubleshooting

### Logs Not Being Created

1. Check that migrations were run
2. Verify the action type is valid (exists in AuditLog.ACTION_TYPES)
3. Check Django logs for audit logging errors
4. Ensure async_log=False for debugging

### Performance Issues

1. Ensure database indexes are created (run migrations)
2. Use list serializer instead of full serializer for large result sets
3. Add pagination to custom queries
4. Consider archiving old logs

### Missing User Information

1. Ensure user is authenticated before logging
2. Check that request object is passed to log_action
3. For anonymous actions, user can be None

## Testing

Run the test suite:

```bash
python test_audit_logging.py
```

Manual testing:

```bash
# Create a test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('testuser', 'test@example.com', 'password')

# Login and check audit logs
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'

# View audit logs (as superadmin)
curl -X GET http://localhost:8000/api/superadmin/audit-logs/ \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN"
```

## Support

For questions or issues with audit logging:
1. Check this documentation
2. Review the code in `api/utils/audit.py`
3. Run the test suite
4. Check Django error logs
