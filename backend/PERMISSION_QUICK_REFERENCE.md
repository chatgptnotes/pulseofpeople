# Permission Management API - Quick Reference

## Quick Start

### 1. Get Your Access Token
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

Save the `access` token from the response.

---

## Common Operations

### List All Permissions
```bash
curl http://127.0.0.1:8000/api/permissions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get User's Permissions
```bash
curl http://127.0.0.1:8000/api/users/USER_ID/permissions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Grant Permission
```bash
curl -X POST http://127.0.0.1:8000/api/users/USER_ID/permissions/grant/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "permission": "create_users",
    "reason": "Promoted to team lead"
  }'
```

### Revoke Permission
```bash
curl -X POST http://127.0.0.1:8000/api/users/USER_ID/permissions/revoke/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "permission": "export_data",
    "reason": "Security policy"
  }'
```

### Reset to Role Defaults
```bash
curl -X POST http://127.0.0.1:8000/api/users/USER_ID/permissions/sync-role/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "confirm": true
  }'
```

---

## Common Permission Names

### User Management
- `create_users` - Create new users
- `edit_users` - Edit user details
- `delete_users` - Delete users
- `view_users` - View user list
- `manage_roles` - Manage user roles and permissions

### Data Access
- `view_all_data` - View all organizational data
- `export_data` - Export data to files
- `import_data` - Import data from files
- `delete_data` - Delete data records

### Analytics
- `view_analytics` - View analytics dashboard
- `view_reports` - View reports
- `create_reports` - Create custom reports
- `export_reports` - Export reports

### Settings
- `manage_organization` - Manage organization settings
- `manage_integrations` - Manage third-party integrations
- `view_audit_logs` - View audit logs

### System (Superadmin Only)
- `manage_system_settings` - Manage system-wide settings
- `manage_permissions` - Manage permission definitions

---

## Response Examples

### Success Response (Grant)
```json
{
  "success": true,
  "user_id": 123,
  "permission": "create_users",
  "granted_by": "admin@example.com",
  "granted_at": "2025-11-08T20:30:00Z",
  "message": "Permission 'create_users' granted successfully"
}
```

### User Permissions List
```json
{
  "user_id": 123,
  "role": "analyst",
  "role_permissions": ["view_analytics", "view_reports"],
  "custom_grants": ["create_users"],
  "custom_revocations": ["export_data"],
  "effective_permissions": ["view_analytics", "view_reports", "create_users"]
}
```

### Error Response
```json
{
  "error": {
    "permission": ["Permission 'invalid_perm' does not exist"]
  }
}
```

---

## HTTP Status Codes

- `200` - Success
- `201` - Created (permission granted)
- `400` - Bad request (validation error)
- `401` - Unauthorized (need to login)
- `403` - Forbidden (insufficient permissions)
- `404` - Not found (user/permission doesn't exist)
- `500` - Server error

---

## Common Errors

### "Permission not found"
**Cause:** Permission name is incorrect or doesn't exist

**Solution:** Check available permissions:
```bash
curl http://127.0.0.1:8000/api/permissions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### "Cannot modify superadmin permissions"
**Cause:** Trying to modify a superadmin user

**Solution:** Only superadmins can modify superadmin permissions

### "Permission already granted"
**Cause:** User already has this permission

**Solution:** Check user's current permissions first:
```bash
curl http://127.0.0.1:8000/api/users/USER_ID/permissions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### "You don't have permission"
**Cause:** Your role doesn't have `manage_roles` permission

**Solution:** Contact a superadmin or admin

---

## Best Practices

1. **Always provide a reason** when granting/revoking permissions
2. **Check existing permissions** before making changes
3. **Use sync-role** after changing user roles
4. **Review permission history** to track changes
5. **Test in development** before production changes
6. **Document permission policies** for your organization

---

## Python Example

```python
import requests

BASE_URL = "http://127.0.0.1:8000/api"
TOKEN = "your_access_token_here"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Grant permission
response = requests.post(
    f"{BASE_URL}/users/123/permissions/grant/",
    json={
        "permission": "create_users",
        "reason": "Promoted to team lead"
    },
    headers=headers
)

if response.status_code == 201:
    print("Permission granted:", response.json())
else:
    print("Error:", response.json())
```

---

## JavaScript Example

```javascript
const BASE_URL = "http://127.0.0.1:8000/api";
const TOKEN = "your_access_token_here";

async function grantPermission(userId, permission, reason) {
  const response = await fetch(
    `${BASE_URL}/users/${userId}/permissions/grant/`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ permission, reason })
    }
  );

  if (response.ok) {
    const data = await response.json();
    console.log("Permission granted:", data);
  } else {
    const error = await response.json();
    console.error("Error:", error);
  }
}

// Usage
grantPermission(123, "create_users", "Promoted to team lead");
```

---

## TypeScript Example

```typescript
interface GrantPermissionRequest {
  permission: string;
  reason?: string;
}

interface GrantPermissionResponse {
  success: boolean;
  user_id: number;
  permission: string;
  granted_by: string;
  granted_at: string;
  message: string;
}

async function grantPermission(
  userId: number,
  data: GrantPermissionRequest
): Promise<GrantPermissionResponse> {
  const response = await fetch(
    `${BASE_URL}/users/${userId}/permissions/grant/`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${TOKEN}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data)
    }
  );

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }

  return await response.json();
}
```

---

## Troubleshooting

### 1. "Unauthorized" Error
- Check if your token is valid
- Token may have expired (get a new one)
- Make sure you're including the "Bearer " prefix

### 2. "Forbidden" Error
- You don't have `manage_roles` permission
- Contact your administrator

### 3. "Not Found" Error
- User ID doesn't exist
- Permission name is incorrect
- Check the URL path

### 4. Server Not Responding
- Make sure Django server is running:
  ```bash
  cd backend
  python manage.py runserver
  ```

---

## Need Help?

1. **Check Documentation**: See `PERMISSION_API_DOCS.md` for complete API reference
2. **View Logs**: Check Django console for error details
3. **Test in Browser**: Use Django REST Framework browsable API at http://127.0.0.1:8000/api/
4. **Contact Support**: Refer to your organization's support channel

---

**Last Updated:** 2025-11-08
**Version:** 1.0
